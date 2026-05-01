from __future__ import annotations

import pytest

from quantcraft.backtest import (
    BacktestReport,
    BacktestResult,
    BacktestSummary,
    ExposureSummary,
)
from quantcraft.trading.domain.events import FillEvent
from quantcraft.trading.domain.state import TradingState
from tests.integration.research.support_backtest_runner import (
    BuyAndHoldStrategy,
    DeterministicEntryExitStrategy,
    OlderLimitThenNewerMarketExitStrategy,
    fixture_bar_series,
    run_engine_backtest,
)


def test_backtest_runner_produces_deterministic_trade_log_and_summary() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy(),
    )

    assert result == BacktestResult(
        trade_log=(
            FillEvent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                price=111.0,
                timestamp=120,
                fee=0.111,
            ),
            FillEvent(
                symbol="BTC/USDT",
                side="sell",
                quantity=1.0,
                price=114.0,
                timestamp=180,
                fee=0.114,
            ),
        ),
        equity_curve=(1000.0, 997.889, 1002.775),
        final_state=TradingState(
            cash=1002.775,
            position_quantity=0.0,
            average_entry_price=0.0,
            realized_pnl=3.0,
            unrealized_pnl=0.0,
            equity=1002.775,
        ),
        summary=BacktestSummary(
            total_trades=1,
            total_fills=2,
            total_fees=0.225,
            final_balance=1002.775,
            final_equity=1002.775,
            total_return=0.002775,
            max_drawdown=0.002111,
            realized_pnl=3.0,
            unrealized_pnl=0.0,
            win_rate=1.0,
            average_win=2.775,
            average_loss=0.0,
            profit_factor=float("inf"),
            exposure=ExposureSummary(
                bars_in_position=1,
                total_bars=3,
                exposure_ratio=1 / 3,
            ),
        ),
    )
    assert result.trade_log
    assert result.final_state.position_quantity == 0.0
    assert result.summary.trade_count == 1
    assert result.summary.ending_equity == 1002.775


def test_backtest_runner_exposes_expanded_research_result_surface() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy(),
    )

    assert result.execution_model_name == "conservative_ohlcv"
    assert result.order_events == ()
    assert result.equity_curve == (1000.0, 997.889, 1002.775)
    assert result.summary.final_balance == 1002.775
    assert result.summary.final_equity == 1002.775
    assert result.summary.total_return == 0.002775
    assert result.summary.max_drawdown == 0.002111
    assert result.summary.total_trades == 1
    assert result.summary.total_fills == 2
    assert result.summary.win_rate == 1.0
    assert result.summary.average_win == 2.775
    assert result.summary.average_loss == 0.0
    assert result.summary.profit_factor == float("inf")
    assert result.summary.exposure.bars_in_position == 1
    assert result.summary.exposure.total_bars == 3
    assert result.summary.exposure.exposure_ratio == 1 / 3
    assert isinstance(result.report, BacktestReport)
    assert result.report.run.symbol == "BTC/USDT"
    assert result.report.run.timeframe == "1m"
    assert result.report.run.bar_count == 3
    assert result.report.execution.order_activation_timing == "next_bar"
    assert result.report.execution.fill_price_basis == "conservative_ohlcv"
    assert result.report.execution.open_position_finalization == "mark_to_market"


def test_backtest_result_preserves_legacy_positional_execution_model_name() -> None:
    result = BacktestResult(
        (),
        (),
        TradingState(cash=1000.0),
        BacktestSummary(
            total_trades=0,
            total_fills=0,
            total_fees=0.0,
            final_balance=1000.0,
            final_equity=1000.0,
            total_return=0.0,
            max_drawdown=0.0,
            realized_pnl=0.0,
            unrealized_pnl=0.0,
            win_rate=0.0,
            average_win=0.0,
            average_loss=0.0,
            profit_factor=0.0,
            exposure=ExposureSummary(
                bars_in_position=0,
                total_bars=0,
                exposure_ratio=0.0,
            ),
        ),
        "custom_model",
    )

    assert result.execution_model_name == "custom_model"
    assert result.order_events == ()
    with pytest.raises(ValueError, match="engine-produced"):
        _ = result.report


def test_backtest_runner_trade_statistics_are_net_of_fees() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy(),
    )

    assert result.summary.realized_pnl == 3.0
    assert result.summary.total_fees == 0.225
    assert result.summary.total_trades == 1
    assert result.summary.total_fills == 2
    assert result.summary.win_rate == 1.0
    assert result.summary.average_win == 2.775
    assert result.summary.average_loss == 0.0
    assert result.summary.profit_factor == float("inf")


def test_backtest_runner_net_trade_stats_handle_partial_closes() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=OlderLimitThenNewerMarketExitStrategy(),
    )

    assert len(result.trade_log) == 2
    assert result.summary.total_trades == 1
    assert result.summary.total_fills == 2
    assert result.summary.total_fees == 0.337
    assert result.summary.realized_pnl == 4.0
    assert result.summary.unrealized_pnl == 3.0
    assert result.summary.average_win == 3.774
    assert result.summary.average_loss == 0.0
    assert result.summary.profit_factor == float("inf")


def test_backtest_runner_marks_open_positions_to_latest_market_state() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=BuyAndHoldStrategy(),
    )

    assert result.final_state == TradingState(
        cash=888.889,
        position_quantity=1.0,
        average_entry_price=111.0,
        realized_pnl=0.0,
        unrealized_pnl=3.0,
        equity=1002.889,
    )
    assert result.summary == BacktestSummary(
        total_trades=0,
        total_fills=1,
        total_fees=0.111,
        final_balance=888.889,
        final_equity=1002.889,
        total_return=0.002889,
        max_drawdown=0.002111,
        realized_pnl=0.0,
        unrealized_pnl=3.0,
        win_rate=0.0,
        average_win=0.0,
        average_loss=0.0,
        profit_factor=0.0,
        exposure=ExposureSummary(
            bars_in_position=2,
            total_bars=3,
            exposure_ratio=2 / 3,
        ),
    )
