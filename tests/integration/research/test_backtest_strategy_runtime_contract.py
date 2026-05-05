from __future__ import annotations

from quantleet.data import TimeBar
from quantleet.trading.domain.costs import CostConfig
from tests.integration.research.support_backtest_runner import (
    PositionViewProbeStrategy,
    ReusedStrategyInstanceProbe,
    fixture_bar_series,
    make_bar_series,
    run_engine_backtest,
)


def test_backtest_runner_exposes_position_view_during_on_bar() -> None:
    rows = tuple(
        TimeBar(
            timestamp=timestamp,
            open=price,
            high=price + 1.0,
            low=price - 1.0,
            close=price + 0.5,
            volume=10.0,
        )
        for timestamp, price in (
            (60, 100.0),
            (120, 110.0),
            (180, 120.0),
            (240, 130.0),
            (300, 140.0),
        )
    )
    strategy = PositionViewProbeStrategy()

    run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=strategy,
        initial_cash=10_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert strategy.position_snapshots == [
        (False, 0.0, 0.0),
        (True, 2.0, 110.0),
        (True, 3.0, 113.333333333333),
        (True, 2.0, 113.333333333333),
        (False, 0.0, 0.0),
    ]


def test_backtest_engine_reuses_strategy_instance_without_cross_run_state_leakage() -> None:
    strategy = ReusedStrategyInstanceProbe()
    bars = fixture_bar_series()

    first_result = run_engine_backtest(
        bars=bars,
        strategy=strategy,
    )
    second_result = run_engine_backtest(
        bars=bars,
        strategy=strategy,
    )

    assert second_result.trade_log == first_result.trade_log
    assert second_result.summary.total_fills == first_result.summary.total_fills
    assert second_result.summary.total_trades == first_result.summary.total_trades
