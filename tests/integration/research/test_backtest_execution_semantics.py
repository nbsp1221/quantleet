from __future__ import annotations

import pytest

from quantleet.data import TimeBar
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.state import TradingState
from tests.integration.research.support_backtest_runner import (
    BuyAndHoldStrategy,
    BuyThenImplicitSellStrategy,
    DeterministicEntryExitStrategy,
    GapCrossedBuyLimitStrategy,
    IntrabarTouchedBuyLimitStrategy,
    MarketableBuyLimitStrategy,
    MultipleStopMarketEntriesStrategy,
    NeverFilledLimitStrategy,
    OlderLimitThenNewerMarketExitStrategy,
    OlderLimitThenTriggeredStopExitStrategy,
    RepeatedExitSignalsStrategy,
    SellWhileFlatStrategy,
    StopMarketGapAboveBuyStrategy,
    StopMarketGapAboveSellStrategy,
    StopMarketGapBelowBuyStrategy,
    StopMarketGapBelowSellStrategy,
    StopMarketIntrabarAboveBuyStrategy,
    StopMarketIntrabarAboveSellStrategy,
    StopMarketIntrabarBelowBuyStrategy,
    StopMarketIntrabarBelowSellStrategy,
    StopMarketSellWhileFlatStrategy,
    fixture_bar_series,
    make_bar_series,
    run_engine_backtest,
)


def test_backtest_runner_uses_tick_path_not_bar_only_fills() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy,
    )

    assert tuple(fill.timestamp for fill in result.trade_log) == (120, 180)
    assert tuple(fill.price for fill in result.trade_log) == (111.0, 114.0)


def test_backtest_runner_activates_bar_orders_on_the_next_bar() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=BuyAndHoldStrategy,
    )

    assert tuple(fill.timestamp for fill in result.trade_log) == (120,)
    assert result.trade_log[0].price == 111.0
    assert result.final_state.position_quantity == 1.0
    assert result.summary.trade_count == 0
    assert result.summary.total_fills == 1
    assert result.summary.ending_equity == 1002.889
    assert result.summary.unrealized_pnl == 3.0
    assert result.equity_curve == (1000.0, 997.889, 1002.889)


def test_backtest_runner_supports_symbol_free_entry_within_single_symbol_on_bar() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=BuyAndHoldStrategy,
    )

    assert tuple(fill.timestamp for fill in result.trade_log) == (120,)
    assert tuple(fill.symbol for fill in result.trade_log) == ("BTC/USDT",)
    assert result.trade_log[0].price == 111.0
    assert result.final_state.position_quantity == 1.0


def test_backtest_runner_supports_symbol_free_exit_within_single_symbol_on_bar() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=BuyThenImplicitSellStrategy,
    )

    assert tuple((fill.side, fill.symbol, fill.timestamp) for fill in result.trade_log) == (
        ("buy", "BTC/USDT", 120),
        ("sell", "BTC/USDT", 180),
    )
    assert result.final_state.position_quantity == 0.0
    assert result.summary.total_trades == 1


def test_unfilled_limit_order_carries_without_creating_trade_log_entries() -> None:
    NeverFilledLimitStrategy.placed_history = []

    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=NeverFilledLimitStrategy,
    )

    assert result.trade_log == ()
    assert result.final_state == TradingState(
        cash=1_000.0,
        position_quantity=0.0,
        average_entry_price=0.0,
        realized_pnl=0.0,
        unrealized_pnl=0.0,
        equity=1_000.0,
    )
    assert NeverFilledLimitStrategy.placed_history[-1] is True


def test_backtest_runner_fills_gap_crossed_buy_limit_at_open() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=105.0, low=95.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=95.0, high=101.0, low=90.0, close=99.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=GapCrossedBuyLimitStrategy,
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 95.0, 120),
    )


def test_backtest_runner_fills_intrabar_touched_buy_limit_at_limit_price() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=101.0, volume=10.0),
        TimeBar(timestamp=120, open=110.0, high=112.0, low=108.0, close=109.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=IntrabarTouchedBuyLimitStrategy,
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 109.0, 120),
    )


def test_backtest_runner_fills_marketable_buy_limit_at_open() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=101.0, volume=10.0),
        TimeBar(timestamp=120, open=121.0, high=125.0, low=119.0, close=124.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=MarketableBuyLimitStrategy,
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 121.0, 120),
    )


def test_backtest_runner_fills_gap_above_buy_stop_market_at_first_executable_point() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=120.0, high=122.0, low=118.0, close=121.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=StopMarketGapAboveBuyStrategy,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 120.0, 120),
    )


def test_backtest_runner_fills_gap_below_buy_stop_market_at_first_executable_point() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=85.0, high=88.0, low=80.0, close=84.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=StopMarketGapBelowBuyStrategy,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 85.0, 120),
    )


def test_backtest_runner_fills_intrabar_above_buy_stop_market_on_same_point() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=100.0, high=120.0, low=95.0, close=118.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=StopMarketIntrabarAboveBuyStrategy,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 110.0, 120),
    )


def test_backtest_runner_fills_intrabar_below_buy_stop_market_on_same_point() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=100.0, high=102.0, low=80.0, close=85.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=StopMarketIntrabarBelowBuyStrategy,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 90.0, 120),
    )


def test_backtest_runner_fills_gap_above_sell_stop_market_at_first_executable_point() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=105.0, high=108.0, low=103.0, close=106.0, volume=12.0),
        TimeBar(timestamp=180, open=120.0, high=122.0, low=118.0, close=121.0, volume=14.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=StopMarketGapAboveSellStrategy,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 105.0, 120),
        ("sell", 120.0, 180),
    )


def test_backtest_runner_fills_gap_below_sell_stop_market_at_first_executable_point() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=105.0, high=108.0, low=103.0, close=106.0, volume=12.0),
        TimeBar(timestamp=180, open=90.0, high=92.0, low=88.0, close=91.0, volume=14.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=StopMarketGapBelowSellStrategy,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 105.0, 120),
        ("sell", 90.0, 180),
    )


def test_backtest_runner_fills_intrabar_above_sell_stop_market_on_same_point() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=105.0, high=108.0, low=103.0, close=106.0, volume=12.0),
        TimeBar(timestamp=180, open=110.0, high=120.0, low=108.0, close=118.0, volume=14.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=StopMarketIntrabarAboveSellStrategy,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 105.0, 120),
        ("sell", 115.0, 180),
    )


def test_backtest_runner_fills_intrabar_below_sell_stop_market_on_same_point() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=105.0, high=108.0, low=103.0, close=106.0, volume=12.0),
        TimeBar(timestamp=180, open=100.0, high=102.0, low=90.0, close=91.0, volume=14.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=StopMarketIntrabarBelowSellStrategy,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 105.0, 120),
        ("sell", 95.0, 180),
    )


def test_backtest_runner_preserves_older_active_intents_ahead_of_newly_activated_ones() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=105.0, low=95.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=110.0, high=112.0, low=108.0, close=109.0, volume=12.0),
        TimeBar(timestamp=180, open=109.0, high=114.0, low=107.0, close=113.0, volume=14.0),
        TimeBar(timestamp=240, open=115.0, high=116.0, low=114.0, close=115.0, volume=15.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=OlderLimitThenNewerMarketExitStrategy,
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 111.0, 120),
        ("sell", 115.0, 240),
        ("sell", 114.0, 240),
    )


def test_backtest_runner_preserves_older_active_orders_ahead_of_newly_triggered_stops() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=105.0, high=108.0, low=103.0, close=106.0, volume=12.0),
        TimeBar(timestamp=180, open=110.0, high=112.0, low=108.0, close=109.0, volume=14.0),
        TimeBar(timestamp=240, open=115.0, high=116.0, low=114.0, close=115.0, volume=15.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=OlderLimitThenTriggeredStopExitStrategy,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 105.0, 120),
        ("sell", 115.0, 240),
        ("sell", 115.0, 240),
    )


def test_backtest_runner_preserves_multiple_stop_trigger_ordering_within_same_segment() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=104.0, low=96.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=100.0, high=120.0, low=95.0, close=118.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=MultipleStopMarketEntriesStrategy,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 105.0, 120),
        ("buy", 110.0, 120),
    )


def test_backtest_runner_ignores_exit_signals_while_flat() -> None:
    rows = tuple(
        TimeBar(
            timestamp=timestamp,
            open=price,
            high=price + 2.0,
            low=price - 2.0,
            close=price + 1.0,
            volume=10.0,
        )
        for timestamp, price in (
            (60, 100.0),
            (120, 101.0),
            (180, 102.0),
        )
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=SellWhileFlatStrategy,
    )

    assert result.trade_log == ()
    assert result.summary.total_trades == 0
    assert result.summary.total_fills == 0
    assert result.final_state.position_quantity == 0.0


def test_backtest_runner_ignores_stop_market_exit_signals_while_flat() -> None:
    rows = tuple(
        TimeBar(
            timestamp=timestamp,
            open=price,
            high=price + 2.0,
            low=price - 10.0,
            close=price + 1.0,
            volume=10.0,
        )
        for timestamp, price in (
            (60, 100.0),
            (120, 101.0),
            (180, 102.0),
        )
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=StopMarketSellWhileFlatStrategy,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert result.trade_log == ()
    assert result.summary.total_trades == 0
    assert result.summary.total_fills == 0
    assert result.final_state.position_quantity == 0.0


def test_backtest_runner_handles_unguarded_exit_signals_before_and_after_entry() -> None:
    rows = tuple(
        TimeBar(
            timestamp=timestamp,
            open=price,
            high=price + 5.0,
            low=price - 5.0,
            close=price + 1.0,
            volume=10.0,
        )
        for timestamp, price in (
            (60, 100.0),
            (120, 101.0),
            (180, 102.0),
            (240, 103.0),
            (300, 104.0),
        )
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=RepeatedExitSignalsStrategy,
    )

    assert tuple((fill.side, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 180),
        ("sell", 240),
    )
    assert result.summary.total_trades == 1
    assert result.summary.total_fills == 2
    assert result.final_state.position_quantity == 0.0


def test_backtest_runner_rejects_out_of_order_bars_before_matching() -> None:
    rows = (
        TimeBar(timestamp=120, open=110.0, high=112.0, low=108.0, close=109.0, volume=12.0),
        TimeBar(timestamp=60, open=100.0, high=105.0, low=95.0, close=104.0, volume=10.0),
    )

    with pytest.raises(ValueError, match="out-of-order time bars"):
        run_engine_backtest(
            bars=make_bar_series(rows),
            strategy=BuyAndHoldStrategy,
        )
