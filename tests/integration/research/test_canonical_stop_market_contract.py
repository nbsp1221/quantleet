from __future__ import annotations

import pytest

from quantcraft.backtest import BacktestSummary, ExposureSummary
from quantcraft.data import TimeBar
from quantcraft.trading.domain.costs import CostConfig
from tests.integration.research.support_backtest_runner import (
    StopMarketGapAboveBuyStrategy,
    StopMarketGapBelowSellStrategy,
    make_bar_series,
    run_engine_backtest,
)


def test_canonical_stop_market_gap_above_entry_matches_public_result_contract() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=120.0, high=122.0, low=118.0, close=121.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=StopMarketGapAboveBuyStrategy(),
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert result.summary == BacktestSummary(
        total_trades=0,
        total_fills=1,
        total_fees=0.0,
        final_balance=880.0,
        final_equity=1001.0,
        total_return=0.001,
        max_drawdown=0.0,
        realized_pnl=0.0,
        unrealized_pnl=1.0,
        win_rate=0.0,
        average_win=0.0,
        average_loss=0.0,
        profit_factor=0.0,
        exposure=ExposureSummary(
            bars_in_position=1,
            total_bars=2,
            exposure_ratio=0.5,
        ),
    )
    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 120.0, 120),
    )


def test_canonical_stop_market_gap_below_exit_matches_public_result_contract() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=105.0, high=108.0, low=103.0, close=106.0, volume=12.0),
        TimeBar(timestamp=180, open=90.0, high=92.0, low=88.0, close=91.0, volume=14.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=StopMarketGapBelowSellStrategy(),
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert result.summary == BacktestSummary(
        total_trades=1,
        total_fills=2,
        total_fees=0.0,
        final_balance=985.0,
        final_equity=985.0,
        total_return=pytest.approx(-0.015),
        max_drawdown=pytest.approx(0.015984015984),
        realized_pnl=-15.0,
        unrealized_pnl=0.0,
        win_rate=0.0,
        average_win=0.0,
        average_loss=15.0,
        profit_factor=0.0,
        exposure=ExposureSummary(
            bars_in_position=1,
            total_bars=3,
            exposure_ratio=pytest.approx(1 / 3),
        ),
    )
    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 105.0, 120),
        ("sell", 90.0, 180),
    )
