from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import UTC, datetime
from functools import cache
from math import isinf, isnan
from pathlib import Path
from typing import Any, ClassVar

import pytest

from quantleet.backtest import BacktestEngine, BacktestReport
from quantleet.data import BarSeries, DataFrameDataSource, TimeBar
from quantleet.research import Strategy, qc, ta
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import FillEvent

CANONICAL_BACKTEST_FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "backtest"
    / "binance_usdm_btcusdtusdt_1h_2025.csv"
)
CANONICAL_REPORT_SNAPSHOT_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "backtest" / "canonical_report_snapshots.json"
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
CANONICAL_REPORT_TOP_LEVEL_FIELDS = {
    "run",
    "execution",
    "returns",
    "risk",
    "trades",
    "costs",
    "exposure",
    "equity",
    "fills",
    "closed_trades",
    "order_rejections",
}


@dataclass(frozen=True)
class CanonicalReportSequenceExpectation:
    count: int
    first: tuple[dict[str, object], ...]
    last: tuple[dict[str, object], ...]
    digest: str


@dataclass(frozen=True)
class CanonicalReportExpectation:
    run: dict[str, object]
    execution: dict[str, object]
    returns: dict[str, object]
    risk: dict[str, object]
    trades: dict[str, object]
    costs: dict[str, object]
    exposure: dict[str, object]
    equity: CanonicalReportSequenceExpectation
    fills: CanonicalReportSequenceExpectation
    closed_trades: CanonicalReportSequenceExpectation
    order_rejection_count: int


def canonical_report_expectation(name: str) -> CanonicalReportExpectation:
    return _load_canonical_report_expectations()[name]


@cache
def _load_canonical_report_expectations() -> dict[str, CanonicalReportExpectation]:
    payload = json.loads(CANONICAL_REPORT_SNAPSHOT_PATH.read_text(encoding="utf-8"))
    return {
        name: CanonicalReportExpectation(
            run=_normalize_loaded_snapshot_value(data["run"]),
            execution=_normalize_loaded_snapshot_value(data["execution"]),
            returns=_normalize_loaded_snapshot_value(data["returns"]),
            risk=_normalize_loaded_snapshot_value(data["risk"]),
            trades=_normalize_loaded_snapshot_value(data["trades"]),
            costs=_normalize_loaded_snapshot_value(data["costs"]),
            exposure=_normalize_loaded_snapshot_value(data["exposure"]),
            equity=_sequence_expectation(data["equity"]),
            fills=_sequence_expectation(data["fills"]),
            closed_trades=_sequence_expectation(data["closed_trades"]),
            order_rejection_count=data["order_rejection_count"],
        )
        for name, data in payload.items()
    }


def _sequence_expectation(data: dict[str, object]) -> CanonicalReportSequenceExpectation:
    return CanonicalReportSequenceExpectation(
        count=int(data["count"]),
        first=_normalize_loaded_snapshot_value(data["first"]),
        last=_normalize_loaded_snapshot_value(data["last"]),
        digest=str(data["digest"]),
    )


def _normalize_loaded_snapshot_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _normalize_loaded_snapshot_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return tuple(_normalize_loaded_snapshot_value(item) for item in value)
    return value


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
    signal_rows: ClassVar[dict[int, dict[str, float]]] = {}

    def init(self) -> None:
        self._entry_pending = False

    def on_bar(self, bar) -> None:
        row = self.signal_rows.get(bar.timestamp, {})
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


class _CanonicalStopLimitSignalStrategy(Strategy):
    signal_name: str
    rows: ClassVar[tuple[TimeBar, ...]] = ()
    signals: ClassVar[dict[int, tuple[float, float]]] = {}

    def init(self) -> None:
        self._entry_pending = False
        self._entry_bar_index: int | None = None

    def on_bar(self, bar) -> None:
        bar_index = len(self.data.close) - 1
        if self.position.is_open:
            self._entry_pending = False
            if self._entry_bar_index is None:
                self._entry_bar_index = bar_index
            if bar_index - self._entry_bar_index >= 24:
                self.sell(quantity=1.0, tag="time-exit")
            return

        self._entry_bar_index = None
        if self._entry_pending:
            return

        signal = self.signals.get(self.rows[bar_index].timestamp)
        if signal is None:
            return
        stop_price, limit_price = signal
        self.buy(
            quantity=1.0,
            order_type="stop_limit",
            stop_price=stop_price,
            limit_price=limit_price,
            tag="entry",
        )
        self._entry_pending = True


class CanonicalStopLimitOpeningRangeBreakoutStrategy(_CanonicalStopLimitSignalStrategy):
    signal_name = "opening_range"


class CanonicalStopLimitDonchianBreakoutStrategy(_CanonicalStopLimitSignalStrategy):
    signal_name = "donchian"


class CanonicalStopLimitInsideBarBreakoutStrategy(_CanonicalStopLimitSignalStrategy):
    signal_name = "inside_bar"


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


def load_canonical_stop_limit_opening_range_bars() -> BarSeries:
    return load_canonical_bars()


def load_canonical_stop_limit_donchian_bars() -> BarSeries:
    return load_canonical_bars()


def load_canonical_stop_limit_inside_bar_bars() -> BarSeries:
    return load_canonical_bars()


def _canonical_backtest_engine() -> BacktestEngine:
    return BacktestEngine(
        initial_cash=1_000_000.0,
        costs=CostConfig(tick_size=0.1, slippage_ticks=1.0, fee_rate=0.0004),
    )


def _run_canonical_backtest(bars: BarSeries, strategy: type[Strategy]):
    return _canonical_backtest_engine().run(bars=bars, strategy=strategy)


def run_canonical_rsi_backtest(bars: BarSeries):
    return _run_canonical_backtest(bars, CanonicalRsi3070Strategy)


def run_canonical_ema_backtest(bars: BarSeries):
    return _run_canonical_backtest(bars, CanonicalEmaCrossStrategy)


def run_canonical_macd_backtest(bars: BarSeries):
    return _run_canonical_backtest(bars, CanonicalMacdCrossStrategy)


def run_canonical_limit_entry_backtest(bars: BarSeries):
    return _run_canonical_backtest(bars, CanonicalLimitEntryStrategy)


def run_canonical_limit_exit_backtest(bars: BarSeries):
    return _run_canonical_backtest(bars, CanonicalLimitExitStrategy)


def run_canonical_limit_mixed_backtest(bars: BarSeries):
    return _run_canonical_backtest(bars, CanonicalLimitMixedStrategy)


def run_canonical_stop_market_opening_range_backtest(bars: BarSeries):
    return _run_canonical_backtest(
        bars,
        _canonical_stop_market_strategy(CanonicalStopMarketOpeningRangeBreakoutStrategy, bars),
    )


def run_canonical_stop_market_donchian_backtest(bars: BarSeries):
    return _run_canonical_backtest(
        bars,
        _canonical_stop_market_strategy(CanonicalStopMarketDonchianBreakoutStrategy, bars),
    )


def run_canonical_stop_market_inside_bar_backtest(bars: BarSeries):
    return _run_canonical_backtest(
        bars,
        _canonical_stop_market_strategy(CanonicalStopMarketInsideBarBreakoutStrategy, bars),
    )


def run_canonical_stop_limit_opening_range_backtest(bars: BarSeries):
    return _run_canonical_backtest(
        bars,
        _canonical_stop_limit_strategy(CanonicalStopLimitOpeningRangeBreakoutStrategy, bars),
    )


def run_canonical_stop_limit_donchian_backtest(bars: BarSeries):
    return _run_canonical_backtest(
        bars,
        _canonical_stop_limit_strategy(CanonicalStopLimitDonchianBreakoutStrategy, bars),
    )


def run_canonical_stop_limit_inside_bar_backtest(bars: BarSeries):
    return _run_canonical_backtest(
        bars,
        _canonical_stop_limit_strategy(CanonicalStopLimitInsideBarBreakoutStrategy, bars),
    )


def _canonical_stop_market_strategy(
    strategy: type[_CanonicalStopMarketSignalStrategy],
    bars: BarSeries,
) -> type[_CanonicalStopMarketSignalStrategy]:
    signals = _canonical_stop_market_signals(bars)

    class RunStrategy(strategy):
        signal_rows = signals

    RunStrategy.__name__ = strategy.__name__
    RunStrategy.__qualname__ = strategy.__qualname__
    return RunStrategy


def _canonical_stop_limit_strategy(
    strategy: type[_CanonicalStopLimitSignalStrategy],
    bars: BarSeries,
) -> type[_CanonicalStopLimitSignalStrategy]:
    run_rows = bars.rows
    run_signals = _canonical_stop_limit_signals(strategy.signal_name, run_rows)

    class RunStrategy(strategy):
        rows = run_rows
        signals = run_signals

    RunStrategy.__name__ = strategy.__name__
    RunStrategy.__qualname__ = strategy.__qualname__
    return RunStrategy


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


def assert_canonical_report(
    scenario: str,
    report: BacktestReport,
    expectation: CanonicalReportExpectation,
) -> None:
    actual_fields = {field.name for field in fields(report)}
    assert actual_fields == CANONICAL_REPORT_TOP_LEVEL_FIELDS, (
        f"{scenario}.BacktestReport top-level contract changed: "
        f"missing_actual_fields={sorted(CANONICAL_REPORT_TOP_LEVEL_FIELDS - actual_fields)}, "
        f"unexpected_actual_fields={sorted(actual_fields - CANONICAL_REPORT_TOP_LEVEL_FIELDS)}"
    )
    _assert_report_group(f"{scenario}.run", report.run, expectation.run)
    _assert_report_group(f"{scenario}.execution", report.execution, expectation.execution)
    _assert_report_group(f"{scenario}.returns", report.returns, expectation.returns)
    _assert_report_group(f"{scenario}.risk", report.risk, expectation.risk)
    _assert_report_group(f"{scenario}.trades", report.trades, expectation.trades)
    _assert_report_group(f"{scenario}.costs", report.costs, expectation.costs)
    _assert_report_group(f"{scenario}.exposure", report.exposure, expectation.exposure)
    _assert_report_sequence(
        name=f"{scenario}.equity",
        rows=report.equity,
        expectation=expectation.equity,
    )
    _assert_report_sequence(
        name=f"{scenario}.fills",
        rows=report.fills,
        expectation=expectation.fills,
    )
    _assert_report_sequence(
        name=f"{scenario}.closed_trades",
        rows=report.closed_trades,
        expectation=expectation.closed_trades,
    )
    assert len(report.order_rejections) == expectation.order_rejection_count, (
        f"{scenario}.order_rejections row count changed: "
        f"expected={expectation.order_rejection_count}, actual={len(report.order_rejections)}"
    )


def _assert_report_group(name: str, actual: object, expected: dict[str, object]) -> None:
    actual_values = _normalize_report_row(actual)
    if not is_dataclass(actual):
        raise AssertionError(f"{name} must be a report dataclass")
    actual_fields = {field.name for field in fields(actual)}
    expected_fields = set(expected)
    assert actual_fields == expected_fields, (
        f"{name} field contract changed: "
        f"missing_actual_fields={sorted(expected_fields - actual_fields)}, "
        f"unexpected_actual_fields={sorted(actual_fields - expected_fields)}"
    )
    for key, expected_value in expected.items():
        _assert_report_value(f"{name}.{key}", actual_values[key], expected_value)


def _assert_report_sequence(
    *,
    name: str,
    rows: tuple[object, ...],
    expectation: CanonicalReportSequenceExpectation,
) -> None:
    first = tuple(_normalize_report_row(row) for row in rows[:3])
    last = tuple(_normalize_report_row(row) for row in rows[-3:])
    digest = _report_rows_digest(rows)
    assert len(rows) == expectation.count, (
        f"{name} row count changed: expected={expectation.count}, actual={len(rows)}"
    )
    assert first == expectation.first, f"{name} first rows changed"
    assert last == expectation.last, f"{name} last rows changed"
    assert digest == expectation.digest, (
        f"{name} digest changed: expected={expectation.digest}, actual={digest}, "
        f"first_rows_match={first == expectation.first}, last_rows_match={last == expectation.last}"
    )


def _assert_report_value(path: str, actual: object, expected: object) -> None:
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"{path} expected a mapping"
        assert set(actual) == set(expected), f"{path} mapping keys changed"
        for key, value in expected.items():
            _assert_report_value(f"{path}.{key}", actual[key], value)
        return
    if isinstance(expected, tuple):
        assert isinstance(actual, tuple), f"{path} expected a tuple"
        assert len(actual) == len(expected), f"{path} tuple length changed"
        for index, value in enumerate(expected):
            _assert_report_value(f"{path}[{index}]", actual[index], value)
        return
    if isinstance(expected, float):
        assert isinstance(actual, float | int), f"{path} expected a numeric value"
        if isinf(expected):
            assert isinf(float(actual)) and (actual > 0.0) == (expected > 0.0), path
            return
        assert actual == pytest.approx(expected), path
        return
    assert actual == expected, path


def _report_rows_digest(rows: tuple[object, ...]) -> str:
    payload = json.dumps(
        [_normalize_report_row(row) for row in rows],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _normalize_report_row(row: object) -> dict[str, object]:
    if is_dataclass(row):
        value = asdict(row)
    elif isinstance(row, dict):
        value = row
    else:
        raise TypeError(f"expected dataclass or dict row, got {type(row).__name__}")
    return {str(key): _normalize_report_value(item) for key, item in value.items()}


def _normalize_report_value(value: Any) -> object:
    if is_dataclass(value):
        return _normalize_report_row(value)
    if isinstance(value, dict):
        return {str(key): _normalize_report_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return tuple(_normalize_report_value(item) for item in value)
    if isinstance(value, float):
        if isinf(value):
            return "inf" if value > 0.0 else "-inf"
        if isnan(value):
            return "nan"
        return round(value, 12)
    return value


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


def canonical_stop_limit_opening_range_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return canonical_trade_log_samples(trade_log)


def canonical_stop_limit_opening_range_trade_log_digest(
    trade_log: tuple[FillEvent, ...],
) -> str:
    return canonical_trade_log_digest(trade_log)


def canonical_stop_limit_buy_trade_log_digest(trade_log: tuple[FillEvent, ...]) -> str:
    return canonical_trade_log_digest(tuple(fill for fill in trade_log if fill.side == "buy"))


def canonical_stop_limit_donchian_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return canonical_trade_log_samples(trade_log)


def canonical_stop_limit_donchian_trade_log_digest(trade_log: tuple[FillEvent, ...]) -> str:
    return canonical_trade_log_digest(trade_log)


def canonical_stop_limit_inside_bar_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return canonical_trade_log_samples(trade_log)


def canonical_stop_limit_inside_bar_trade_log_digest(trade_log: tuple[FillEvent, ...]) -> str:
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


def _canonical_stop_limit_signals(
    signal_name: str,
    rows: tuple[TimeBar, ...],
) -> dict[int, tuple[float, float]]:
    signals: dict[int, tuple[float, float]] = {}
    opening_range_highs = _opening_range_highs(rows) if signal_name == "opening_range" else {}
    for index, row in enumerate(rows):
        if signal_name == "opening_range":
            signal = _canonical_stop_limit_opening_range_signal(
                row=row,
                opening_range_highs=opening_range_highs,
            )
        elif signal_name == "donchian":
            signal = _canonical_stop_limit_donchian_signal(rows, index)
        elif signal_name == "inside_bar":
            signal = _canonical_stop_limit_inside_bar_signal(rows, index)
        else:
            raise ValueError(f"unknown stop-limit signal name: {signal_name}")
        if signal is not None:
            signals[row.timestamp] = signal
    return signals


def _opening_range_highs(rows: tuple[TimeBar, ...]) -> dict[str, tuple[float, int]]:
    ranges: dict[str, tuple[float, int]] = {}
    for row in rows:
        timestamp = datetime.fromtimestamp(row.timestamp / 1000, tz=UTC)
        if timestamp.hour >= 6:
            continue
        key = timestamp.date().isoformat()
        if key not in ranges:
            ranges[key] = (row.high, 1)
            continue
        previous_high, previous_count = ranges[key]
        ranges[key] = (max(previous_high, row.high), previous_count + 1)
    return ranges


def _canonical_stop_limit_opening_range_signal(
    *,
    row: TimeBar,
    opening_range_highs: dict[str, tuple[float, int]],
) -> tuple[float, float] | None:
    timestamp = datetime.fromtimestamp(row.timestamp / 1000, tz=UTC)
    if timestamp.hour < 6:
        return None

    opening_range = opening_range_highs.get(timestamp.date().isoformat())
    if opening_range is None:
        return None
    opening_high, opening_count = opening_range
    if opening_count < 6:
        return None

    stop_price = opening_high + 0.1
    if row.close >= stop_price:
        return None
    return stop_price, stop_price + 50.0


def _canonical_stop_limit_donchian_signal(
    rows: tuple[TimeBar, ...],
    index: int,
) -> tuple[float, float] | None:
    if index < 20:
        return None
    stop_price = max(row.high for row in rows[index - 20 : index]) + 0.1
    if rows[index].close >= stop_price:
        return None
    return stop_price, stop_price + 50.0


def _canonical_stop_limit_inside_bar_signal(
    rows: tuple[TimeBar, ...],
    index: int,
) -> tuple[float, float] | None:
    if index < 1:
        return None
    mother = rows[index - 1]
    row = rows[index]
    if not (row.high < mother.high and row.low > mother.low):
        return None
    stop_price = mother.high + 0.1
    if row.close >= stop_price:
        return None
    return stop_price, stop_price + 50.0


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
