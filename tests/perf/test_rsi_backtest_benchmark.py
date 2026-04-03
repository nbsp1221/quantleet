from __future__ import annotations

import csv
from pathlib import Path
from time import perf_counter

import pytest

from quantcraft.data import BarSeries, DataFrameDataSource
from quantcraft.research import BacktestEngine, Strategy, qc, ta
from quantcraft.trading.domain.costs import CostConfig

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "backtest"
    / "binance_usdm_btcusdtusdt_1h_2025.csv"
)
EXPECTED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")
EXPECTED_ROWS = 8_760
FIRST_RUN_THRESHOLD_SECONDS = 1.0
STEADY_STATE_THRESHOLD_SECONDS = 1.0
STEADY_STATE_ROUNDS = 5


class Rsi3070Strategy(Strategy):
    def init(self) -> None:
        self.rsi = ta.rsi(self.data.close, length=14)

    def on_bar(self, bar) -> None:
        if qc.is_na(self.rsi[0]):
            return
        if (not self.position.is_open) and self.rsi[0] < 30:
            self.buy(symbol=bar.symbol, quantity=1.0)
        elif self.position.is_open and self.rsi[0] > 70:
            self.sell(symbol=bar.symbol, quantity=1.0)


def _load_canonical_bars() -> BarSeries:
    with FIXTURE_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert tuple(reader.fieldnames or ()) == EXPECTED_COLUMNS
        rows = list(reader)

    assert len(rows) == EXPECTED_ROWS
    assert rows[0]["timestamp"] == "2025-01-01T00:00:00+00:00"
    assert rows[-1]["timestamp"] == "2025-12-31T23:00:00+00:00"
    assert rows == sorted(rows, key=lambda row: str(row["timestamp"]))

    return DataFrameDataSource(
        frame=rows,
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    ).load()


def _run_canonical_backtest(bars: BarSeries):
    engine = BacktestEngine(
        initial_cash=1_000_000.0,
        costs=CostConfig(tick_size=0.1, slippage_ticks=1.0, fee_rate=0.0004),
    )
    return engine.run(bars=bars, strategy=Rsi3070Strategy())


def _assert_canonical_result_shape(result) -> None:
    assert result.summary.total_trades == 118
    assert result.summary.total_fills == 236
    assert result.summary.final_equity == pytest.approx(1_038_523.5766)


@pytest.mark.slow
def test_rsi_backtest_first_run_is_within_threshold() -> None:
    bars = _load_canonical_bars()

    first_run_started_at = perf_counter()
    first_result = _run_canonical_backtest(bars)
    first_run_seconds = perf_counter() - first_run_started_at

    _assert_canonical_result_shape(first_result)

    assert first_run_seconds < FIRST_RUN_THRESHOLD_SECONDS, (
        "canonical RSI first-run runtime exceeded the perf gate: "
        f"{first_run_seconds:.6f}s >= {FIRST_RUN_THRESHOLD_SECONDS:.1f}s"
    )


@pytest.mark.slow
def test_rsi_backtest_steady_state_median_is_within_threshold(benchmark) -> None:
    bars = _load_canonical_bars()

    steady_result = benchmark.pedantic(
        _run_canonical_backtest,
        args=(bars,),
        rounds=STEADY_STATE_ROUNDS,
        iterations=1,
        warmup_rounds=0,
    )

    _assert_canonical_result_shape(steady_result)
    steady_state_median = benchmark.stats.stats.median

    assert steady_state_median < STEADY_STATE_THRESHOLD_SECONDS, (
        "canonical RSI steady-state median runtime exceeded the perf gate: "
        f"{steady_state_median:.6f}s >= {STEADY_STATE_THRESHOLD_SECONDS:.1f}s"
    )
