from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from quantcraft.backtest import BacktestEngine
from quantcraft.data import BarSeries, DataFrameDataSource
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


def _normalize_fill(fill: FillEvent) -> dict[str, float | int | str]:
    return {
        "timestamp": fill.timestamp,
        "side": fill.side,
        "quantity": round(fill.quantity, 12),
        "price": round(fill.price, 12),
        "fee": round(fill.fee, 12),
    }
