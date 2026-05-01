from __future__ import annotations

from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import FillEvent
from tests.integration.research.support_backtest_runner import (
    DeterministicEntryExitStrategy,
    OlderLimitThenNewerMarketExitStrategy,
    fixture_bar_series,
    fixture_rows,
    make_bar_series,
    run_engine_backtest,
)


def test_reporting_fill_rows_preserve_order_provenance_without_mutating_fill_event() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy(),
    )

    assert result.trade_log == (
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
    )
    assert not hasattr(result.trade_log[0], "tag")
    assert result.report.fills[0].order_id == 1
    assert result.report.fills[0].order_type == "market"
    assert result.report.fills[0].tag == "entry"
    assert result.report.fills[1].order_id == 2
    assert result.report.fills[1].order_type == "limit"
    assert result.report.fills[1].tag == "exit"


def test_closed_trade_rows_include_weighted_average_fee_and_tag_details() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy(),
    )

    assert len(result.report.closed_trades) == 1
    trade = result.report.closed_trades[0]

    assert trade.entry_timestamp == 120
    assert trade.exit_timestamp == 180
    assert trade.entry_bar_index == 1
    assert trade.exit_bar_index == 2
    assert trade.duration_bars == 2
    assert trade.quantity == 1.0
    assert trade.entry_price == 111.0
    assert trade.exit_price == 114.0
    assert trade.gross_pnl == 3.0
    assert trade.allocated_entry_fee == 0.111
    assert trade.exit_fee == 0.114
    assert trade.total_fees == 0.225
    assert trade.net_pnl == 2.775
    assert trade.entry_tag == "entry"
    assert trade.entry_tags == ("entry",)
    assert trade.exit_tag == "exit"
    assert result.report.trades.best_trade == trade.net_return
    assert result.report.trades.worst_trade == trade.net_return
    assert result.report.costs.fees_as_initial_cash == 0.000225


def test_partial_closes_allocate_entry_fees_and_leave_open_inventory() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=OlderLimitThenNewerMarketExitStrategy(),
    )

    trades = result.report.closed_trades

    assert len(trades) == 1
    assert trades[0].quantity == 1.0
    assert trades[0].gross_pnl == 4.0
    assert trades[0].allocated_entry_fee == 0.111
    assert trades[0].exit_fee == 0.115
    assert trades[0].net_pnl == 3.774
    assert result.report.returns.unrealized_pnl == 3.0
    assert result.report.exposure.ending_state == "open"
    assert result.report.exposure.final_position_quantity == 1.0
    assert result.report.exposure.final_average_entry_price == 111.0


def test_fee_drag_uses_closed_trade_gross_absolute_pnl_denominator() -> None:
    result = run_engine_backtest(
        bars=make_bar_series(fixture_rows()[:3]),
        strategy=DeterministicEntryExitStrategy(),
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.001),
    )

    trade = result.report.closed_trades[0]

    assert trade.gross_pnl == 3.0
    assert result.report.costs.closed_trade_fees == 0.225
    assert result.report.costs.fees_to_gross_pnl_ratio == 0.075
