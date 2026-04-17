from __future__ import annotations

import pytest

import quantcraft.integrations.venues.ccxt.market_data as exchange_backend
from quantcraft.backtest import BacktestEngine, BacktestResult
from quantcraft.data import CCXTDataSource, DataFrameDataSource
from quantcraft.trading.domain.costs import CostConfig
from tests.integration.research.support_backtest_runner import (
    DeterministicEntryExitStrategy,
    FakeExchangeClient,
    InMemoryBarSeriesSource,
    InMemoryDuckTypedSource,
    fixture_bar_series,
    fixture_dataframe_records,
    run_engine_backtest,
    run_engine_backtest_from_source,
)


def test_backtest_engine_runs_materialized_bar_series() -> None:
    result = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001),
    ).run(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy(),
    )

    assert isinstance(result, BacktestResult)
    assert result.summary.total_trades == 1


def test_backtest_engine_runs_source_that_loads_bar_series() -> None:
    result = run_engine_backtest_from_source(
        source=InMemoryBarSeriesSource(),
        strategy=DeterministicEntryExitStrategy(),
    )

    assert isinstance(result, BacktestResult)
    assert result.summary.total_trades == 1


def test_backtest_engine_runs_dataframe_source_quickstart_path() -> None:
    source = DataFrameDataSource(
        frame=fixture_dataframe_records(),
        symbol="BTC/USDT",
        timeframe="1m",
    )

    result = run_engine_backtest_from_source(
        source=source,
        strategy=DeterministicEntryExitStrategy(),
    )

    assert isinstance(result, BacktestResult)
    assert result.summary.total_trades == 1
    assert result.summary.total_fills == 2


def test_backtest_engine_rejects_missing_and_duplicate_inputs() -> None:
    engine = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001),
    )

    with pytest.raises(ValueError, match="provide exactly one of bars or source"):
        engine.run(strategy=DeterministicEntryExitStrategy())

    with pytest.raises(ValueError, match="provide exactly one of bars or source"):
        engine.run(
            bars=fixture_bar_series(),
            source=InMemoryBarSeriesSource(),
            strategy=DeterministicEntryExitStrategy(),
        )


def test_backtest_engine_rejects_non_bar_series_bars_input() -> None:
    engine = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001),
    )

    with pytest.raises(ValueError, match="bars must be a BarSeries instance"):
        engine.run(
            bars=("not", "a", "bar-series"),  # type: ignore[arg-type]
            strategy=DeterministicEntryExitStrategy(),
        )


def test_backtest_engine_rejects_source_results_that_are_not_bar_series() -> None:
    engine = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001),
    )

    with pytest.raises(ValueError, match="bars must be a BarSeries instance"):
        engine.run(
            source=InMemoryDuckTypedSource(),
            strategy=DeterministicEntryExitStrategy(),
        )


def test_backtest_runner_accepts_paginated_ccxt_source_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(exchange_backend, "_DEFAULT_PAGINATION_LIMIT", 2)
    fake_client = FakeExchangeClient(
        pages=[
            [
                [60_000, 100.0, 105.0, 95.0, 104.0, 10.0],
                [120_000, 110.0, 112.0, 108.0, 109.0, 12.0],
            ],
            [
                [120_000, 110.0, 112.0, 108.0, 109.0, 12.0],
                [180_000, 109.0, 114.0, 107.0, 113.0, 14.0],
            ],
            [],
        ]
    )
    monkeypatch.setattr(exchange_backend, "_make_ccxt_exchange", lambda **_: fake_client)

    bars = CCXTDataSource(
        exchange="binance",
        market="spot",
        symbol="BTC/USDT",
        timeframe="1m",
        start=60_000,
    ).load()

    result = run_engine_backtest(
        bars=bars,
        strategy=DeterministicEntryExitStrategy(),
    )

    assert tuple(row.timestamp for row in bars.rows) == (60_000, 120_000, 180_000)
    assert len(result.trade_log) == 2
    assert result.summary.total_trades == 1
    assert result.summary.final_equity > 0.0


def test_backtest_engine_runs_exchange_backed_source_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(exchange_backend, "_DEFAULT_PAGINATION_LIMIT", 2)
    fake_client = FakeExchangeClient(
        pages=[
            [
                [60_000, 100.0, 105.0, 95.0, 104.0, 10.0],
                [120_000, 110.0, 112.0, 108.0, 109.0, 12.0],
            ],
            [
                [120_000, 110.0, 112.0, 108.0, 109.0, 12.0],
                [180_000, 109.0, 114.0, 107.0, 113.0, 14.0],
            ],
            [],
        ]
    )
    monkeypatch.setattr(exchange_backend, "_make_ccxt_exchange", lambda **_: fake_client)

    source = CCXTDataSource(
        exchange="binance",
        market="spot",
        symbol="BTC/USDT",
        timeframe="1m",
        start=60_000,
    )

    result = run_engine_backtest_from_source(
        source=source,
        strategy=DeterministicEntryExitStrategy(),
    )

    assert isinstance(result, BacktestResult)
    assert len(result.trade_log) == 2
    assert result.summary.total_trades == 1
    assert result.summary.final_equity > 0.0
