from __future__ import annotations

import csv
import hashlib
import json
from datetime import UTC, datetime
from math import isnan
from pathlib import Path

from quantcraft.backtest import BacktestEngine
from quantcraft.data import BarSeries, DataFrameDataSource, TimeBar
from quantcraft.research import Strategy, qc, ta
from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import FillEvent

CANONICAL_BACKTEST_FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "backtest"
    / "binance_usdm_btcusdtusdt_1h_2025.csv"
)
CANONICAL_BACKTEST_EXPECTED_COLUMNS = (
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
)
CANONICAL_BACKTEST_EXPECTED_ROWS = 8_760


class CanonicalRsi3070Strategy(Strategy):
    def init(self) -> None:
        self.rsi = ta.rsi(self.data.close, length=14)

    def on_bar(self, bar) -> None:
        if qc.is_na(self.rsi[0]):
            return
        if (not self.position.is_open) and self.rsi[0] < 30:
            self.buy(quantity=1.0)
        elif self.position.is_open and self.rsi[0] > 70:
            self.sell(quantity=1.0)


class CanonicalEmaCrossStrategy(Strategy):
    def init(self) -> None:
        self.fast = ta.ema(self.data.close, length=10)
        self.slow = ta.ema(self.data.close, length=20)

    def on_bar(self, bar) -> None:
        if qc.crossover(self.fast, self.slow):
            self.buy(quantity=1.0)
        elif qc.crossunder(self.fast, self.slow):
            self.sell(quantity=1.0)


class CanonicalMacdCrossStrategy(Strategy):
    def init(self) -> None:
        self.macd = ta.macd(self.data.close, fast=12, slow=26, signal=9)

    def on_bar(self, bar) -> None:
        if qc.crossover(self.macd.macd, self.macd.signal):
            self.buy(quantity=1.0)
        elif qc.crossunder(self.macd.macd, self.macd.signal):
            self.sell(quantity=1.0)


class CanonicalLimitEntryStrategy(Strategy):
    def init(self) -> None:
        self.ema = ta.ema(self.data.close, length=20)
        self._entry_pending = False

    def on_bar(self, bar) -> None:
        if qc.is_na(self.ema[0]) or qc.is_na(self.ema[1]):
            return
        if self.position.is_open:
            self._entry_pending = False
            if self.data.close[0] < self.ema[0]:
                self.sell(quantity=1.0)
            return
        if self._entry_pending:
            return
        if self.ema[0] > self.ema[1] and self.data.close[0] > self.ema[0] * 1.01:
            self.buy(
                quantity=1.0,
                order_type="limit",
                limit_price=float(self.ema[0]),
            )
            self._entry_pending = True


class CanonicalLimitExitStrategy(Strategy):
    def init(self) -> None:
        self.rsi = ta.rsi(self.data.close, length=14)
        self._exit_pending = False

    def on_bar(self, bar) -> None:
        if qc.is_na(self.rsi[0]):
            return
        if self.position.is_open:
            if not self._exit_pending:
                self.sell(
                    quantity=1.0,
                    order_type="limit",
                    limit_price=float(self.position.average_entry_price * 1.02),
                )
                self._exit_pending = True
            return
        self._exit_pending = False
        if self.rsi[0] < 30:
            self.buy(quantity=1.0)


class CanonicalLimitMixedStrategy(Strategy):
    def init(self) -> None:
        self.bands = ta.bb(self.data.close, length=20, stddev=2)
        self._entry_pending = False
        self._exit_pending = False

    def on_bar(self, bar) -> None:
        if qc.is_na(self.bands.lower[0]) or qc.is_na(self.bands.middle[0]):
            return
        if self.position.is_open:
            self._entry_pending = False
            if not self._exit_pending:
                self.sell(
                    quantity=1.0,
                    order_type="limit",
                    limit_price=float(self.bands.middle[0]),
                )
                self._exit_pending = True
            return
        self._exit_pending = False
        if self._entry_pending:
            return
        if self.data.close[0] < self.bands.lower[0]:
            self.buy(
                quantity=1.0,
                order_type="limit",
                limit_price=float(self.bands.lower[0]),
            )
            self._entry_pending = True


class _CanonicalStopMarketSignalStrategy(Strategy):
    prefix: str

    def __init__(self, signal_rows: dict[int, dict[str, float]]) -> None:
        super().__init__()
        self._signal_rows = signal_rows

    def init(self) -> None:
        self._entry_pending = False

    def on_bar(self, bar) -> None:
        row = self._signal_rows.get(bar.timestamp, {})
        if self.position.is_open:
            self._entry_pending = False
            if row.get(f"{self.prefix}_exit") is not None:
                self.sell(quantity=1.0, tag="signal-exit")
            return

        if self._entry_pending:
            return

        entry_price = row.get(f"{self.prefix}_entry")
        if entry_price is None:
            return

        self.buy(
            quantity=1.0,
            order_type="stop_market",
            stop_price=entry_price,
            tag="entry",
        )
        self._entry_pending = True


class CanonicalStopMarketOpeningRangeBreakoutStrategy(_CanonicalStopMarketSignalStrategy):
    prefix = "orb"


class CanonicalStopMarketDonchianBreakoutStrategy(_CanonicalStopMarketSignalStrategy):
    prefix = "turtle"


class CanonicalStopMarketInsideBarBreakoutStrategy(_CanonicalStopMarketSignalStrategy):
    prefix = "inside"


def load_canonical_bars() -> BarSeries:
    with CANONICAL_BACKTEST_FIXTURE_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert tuple(reader.fieldnames or ()) == CANONICAL_BACKTEST_EXPECTED_COLUMNS
        rows = list(reader)

    assert len(rows) == CANONICAL_BACKTEST_EXPECTED_ROWS
    assert rows[0]["timestamp"] == "2025-01-01T00:00:00+00:00"
    assert rows[-1]["timestamp"] == "2025-12-31T23:00:00+00:00"
    assert rows == sorted(rows, key=lambda row: str(row["timestamp"]))

    return DataFrameDataSource(
        frame=rows,
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    ).load()


def load_canonical_rsi_bars() -> BarSeries:
    return load_canonical_bars()


def load_canonical_ema_bars() -> BarSeries:
    return load_canonical_bars()


def load_canonical_macd_bars() -> BarSeries:
    return load_canonical_bars()


def load_canonical_limit_entry_bars() -> BarSeries:
    return load_canonical_bars()


def load_canonical_limit_exit_bars() -> BarSeries:
    return load_canonical_bars()


def load_canonical_limit_mixed_bars() -> BarSeries:
    return load_canonical_bars()


def load_canonical_stop_market_opening_range_bars() -> BarSeries:
    return load_canonical_bars()


def load_canonical_stop_market_donchian_bars() -> BarSeries:
    return load_canonical_bars()


def load_canonical_stop_market_inside_bar_bars() -> BarSeries:
    return load_canonical_bars()


def _canonical_backtest_engine() -> BacktestEngine:
    return BacktestEngine(
        initial_cash=1_000_000.0,
        costs=CostConfig(tick_size=0.1, slippage_ticks=1.0, fee_rate=0.0004),
    )


def _run_canonical_backtest(bars: BarSeries, strategy: Strategy):
    return _canonical_backtest_engine().run(bars=bars, strategy=strategy)


def run_canonical_rsi_backtest(bars: BarSeries):
    return _run_canonical_backtest(bars, CanonicalRsi3070Strategy())


def run_canonical_ema_backtest(bars: BarSeries):
    return _run_canonical_backtest(bars, CanonicalEmaCrossStrategy())


def run_canonical_macd_backtest(bars: BarSeries):
    return _run_canonical_backtest(bars, CanonicalMacdCrossStrategy())


def run_canonical_limit_entry_backtest(bars: BarSeries):
    return _run_canonical_backtest(bars, CanonicalLimitEntryStrategy())


def run_canonical_limit_exit_backtest(bars: BarSeries):
    return _run_canonical_backtest(bars, CanonicalLimitExitStrategy())


def run_canonical_limit_mixed_backtest(bars: BarSeries):
    return _run_canonical_backtest(bars, CanonicalLimitMixedStrategy())


def run_canonical_stop_market_opening_range_backtest(bars: BarSeries):
    return _run_canonical_backtest(
        bars,
        CanonicalStopMarketOpeningRangeBreakoutStrategy(_canonical_stop_market_signals(bars)),
    )


def run_canonical_stop_market_donchian_backtest(bars: BarSeries):
    return _run_canonical_backtest(
        bars,
        CanonicalStopMarketDonchianBreakoutStrategy(_canonical_stop_market_signals(bars)),
    )


def run_canonical_stop_market_inside_bar_backtest(bars: BarSeries):
    return _run_canonical_backtest(
        bars,
        CanonicalStopMarketInsideBarBreakoutStrategy(_canonical_stop_market_signals(bars)),
    )


def canonical_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return (
        tuple(_normalize_fill(fill) for fill in trade_log[:5]),
        tuple(_normalize_fill(fill) for fill in trade_log[-5:]),
    )


def canonical_trade_log_digest(trade_log: tuple[FillEvent, ...]) -> str:
    payload = json.dumps(
        [_normalize_fill(fill) for fill in trade_log],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def canonical_rsi_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return canonical_trade_log_samples(trade_log)


def canonical_rsi_trade_log_digest(trade_log: tuple[FillEvent, ...]) -> str:
    return canonical_trade_log_digest(trade_log)


def canonical_ema_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return canonical_trade_log_samples(trade_log)


def canonical_ema_trade_log_digest(trade_log: tuple[FillEvent, ...]) -> str:
    return canonical_trade_log_digest(trade_log)


def canonical_macd_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return canonical_trade_log_samples(trade_log)


def canonical_macd_trade_log_digest(trade_log: tuple[FillEvent, ...]) -> str:
    return canonical_trade_log_digest(trade_log)


def canonical_limit_entry_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return canonical_trade_log_samples(trade_log)


def canonical_limit_entry_trade_log_digest(trade_log: tuple[FillEvent, ...]) -> str:
    return canonical_trade_log_digest(trade_log)


def canonical_limit_exit_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return canonical_trade_log_samples(trade_log)


def canonical_limit_exit_trade_log_digest(trade_log: tuple[FillEvent, ...]) -> str:
    return canonical_trade_log_digest(trade_log)


def canonical_limit_mixed_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return canonical_trade_log_samples(trade_log)


def canonical_limit_mixed_trade_log_digest(trade_log: tuple[FillEvent, ...]) -> str:
    return canonical_trade_log_digest(trade_log)


def canonical_stop_market_opening_range_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return canonical_trade_log_samples(trade_log)


def canonical_stop_market_opening_range_trade_log_digest(
    trade_log: tuple[FillEvent, ...],
) -> str:
    return canonical_trade_log_digest(trade_log)


def canonical_stop_market_donchian_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return canonical_trade_log_samples(trade_log)


def canonical_stop_market_donchian_trade_log_digest(trade_log: tuple[FillEvent, ...]) -> str:
    return canonical_trade_log_digest(trade_log)


def canonical_stop_market_inside_bar_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return canonical_trade_log_samples(trade_log)


def canonical_stop_market_inside_bar_trade_log_digest(trade_log: tuple[FillEvent, ...]) -> str:
    return canonical_trade_log_digest(trade_log)


def _normalize_fill(fill: FillEvent) -> dict[str, float | int | str]:
    return {
        "timestamp": fill.timestamp,
        "side": fill.side,
        "quantity": round(fill.quantity, 12),
        "price": round(fill.price, 12),
        "fee": round(fill.fee, 12),
    }


def _canonical_stop_market_signals(bars: BarSeries) -> dict[int, dict[str, float]]:
    rows = bars.rows
    high = [row.high for row in rows]
    low = [row.low for row in rows]
    close = [row.close for row in rows]
    ema20 = _ema(close, span=20)
    ema50 = _ema(close, span=50)
    atr14 = _rolling_mean(_true_range(rows), length=14)
    rsi14 = _rsi(close, length=14)

    signals: dict[int, dict[str, float]] = {}
    opening_ranges = _opening_ranges(rows)

    for index, row in enumerate(rows):
        timestamp = datetime.fromtimestamp(row.timestamp / 1000, tz=UTC)
        hour_index = timestamp.hour
        opening_high, opening_low = opening_ranges[timestamp.date().isoformat()]
        row_signals: dict[str, float] = {}

        opening_mid = (opening_high + opening_low) / 2
        if (
            6 <= hour_index <= 18
            and atr14[index] is not None
            and opening_high > row.close + atr14[index] * 0.05
        ):
            row_signals["orb_entry"] = opening_high + 0.01
        if hour_index >= 22 or row.close < opening_mid:
            row_signals["orb_exit"] = 1.0

        donchian_high = _window_max(high, end=index, length=20)
        donchian_low = _window_min(low, end=index, length=10)
        if (
            atr14[index] is not None
            and donchian_high is not None
            and ema20[index] is not None
            and ema50[index] is not None
            and ema20[index] > ema50[index]
            and donchian_high > row.close + atr14[index] * 0.05
        ):
            row_signals["turtle_entry"] = donchian_high + 0.01
        if donchian_low is not None and row.close < donchian_low:
            row_signals["turtle_exit"] = 1.0

        mother_high = high[index - 1] if index > 0 else None
        mother_low = low[index - 1] if index > 0 else None
        inside_bar = (
            mother_high is not None
            and mother_low is not None
            and row.high < mother_high
            and row.low > mother_low
        )
        if (
            inside_bar
            and atr14[index] is not None
            and ema20[index] is not None
            and ema50[index] is not None
            and ema20[index] > ema50[index]
            and mother_high is not None
            and mother_high > row.close + atr14[index] * 0.02
        ):
            row_signals["inside_entry"] = mother_high + 0.01
        if mother_low is not None and (row.close < mother_low or rsi14[index] > 62.0):
            row_signals["inside_exit"] = 1.0

        signals[row.timestamp] = row_signals

    return signals


def _opening_ranges(rows: tuple[TimeBar, ...]) -> dict[str, tuple[float, float]]:
    ranges: dict[str, tuple[float, float]] = {}
    for row in rows:
        timestamp = datetime.fromtimestamp(row.timestamp / 1000, tz=UTC)
        if timestamp.hour >= 6:
            continue
        key = timestamp.date().isoformat()
        if key not in ranges:
            ranges[key] = (row.high, row.low)
            continue
        previous_high, previous_low = ranges[key]
        ranges[key] = (max(previous_high, row.high), min(previous_low, row.low))
    return ranges


def _ema(values: list[float], *, span: int) -> list[float | None]:
    alpha = 2 / (span + 1)
    result: list[float | None] = []
    previous: float | None = None
    for value in values:
        previous = value if previous is None else alpha * value + (1 - alpha) * previous
        result.append(previous)
    return result


def _true_range(rows: tuple[TimeBar, ...]) -> list[float]:
    result: list[float] = []
    previous_close: float | None = None
    for row in rows:
        candidates = [row.high - row.low]
        if previous_close is not None:
            candidates.append(abs(row.high - previous_close))
            candidates.append(abs(row.low - previous_close))
        result.append(max(candidates))
        previous_close = row.close
    return result


def _rolling_mean(values: list[float], *, length: int) -> list[float | None]:
    result: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < length:
            result.append(None)
            continue
        result.append(sum(values[index + 1 - length : index + 1]) / length)
    return result


def _rsi(values: list[float], *, length: int) -> list[float]:
    gains: list[float | None] = [None]
    losses: list[float | None] = [None]
    for previous, current in zip(values, values[1:]):
        delta = current - previous
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))

    average_gain = _ewm(gains, alpha=1 / length, min_periods=length)
    average_loss = _ewm(losses, alpha=1 / length, min_periods=length)

    result: list[float] = []
    for gain, loss in zip(average_gain, average_loss, strict=True):
        if gain is None or loss is None or loss == 0.0:
            result.append(50.0)
            continue
        relative_strength = gain / loss
        result.append(100 - (100 / (1 + relative_strength)))
    return result


def _ewm(
    values: list[float | None],
    *,
    alpha: float,
    min_periods: int,
) -> list[float | None]:
    result: list[float | None] = []
    previous: float | None = None
    seen = 0
    for value in values:
        if value is not None and not isnan(value):
            seen += 1
            previous = value if previous is None else alpha * value + (1 - alpha) * previous
        if seen < min_periods or previous is None:
            result.append(None)
        else:
            result.append(previous)
    return result


def _window_max(values: list[float], *, end: int, length: int) -> float | None:
    if end < length:
        return None
    return max(values[end - length : end])


def _window_min(values: list[float], *, end: int, length: int) -> float | None:
    if end < length:
        return None
    return min(values[end - length : end])
