from __future__ import annotations

import pytest

from quantcraft.data import TimeBar
from quantcraft.trading.domain.state import TradingState
from tests.integration.research.support_backtest_runner import (
    BuyAndHoldStrategy,
    DeterministicEntryExitStrategy,
    GapCrossedBuyLimitStrategy,
    IntrabarTouchedBuyLimitStrategy,
    MarketableBuyLimitStrategy,
    NeverFilledLimitStrategy,
    OlderLimitThenNewerMarketExitStrategy,
    RepeatedExitSignalsStrategy,
    SellWhileFlatStrategy,
    fixture_bar_series,
    make_bar_series,
    run_engine_backtest,
)


def test_backtest_runner_uses_tick_path_not_bar_only_fills() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=DeterministicEntryExitStrategy(),
    )

    assert tuple(fill.timestamp for fill in result.trade_log) == (120, 180)
    assert tuple(fill.price for fill in result.trade_log) == (111.0, 114.0)


def test_backtest_runner_activates_bar_orders_on_the_next_bar() -> None:
    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=BuyAndHoldStrategy(),
    )

    assert tuple(fill.timestamp for fill in result.trade_log) == (120,)
    assert result.trade_log[0].price == 111.0
    assert result.final_state.position_quantity == 1.0
    assert result.summary.trade_count == 0
    assert result.summary.total_fills == 1
    assert result.summary.ending_equity == 1002.889
    assert result.summary.unrealized_pnl == 3.0
    assert result.equity_curve == (1000.0, 997.889, 1002.889)


def test_unfilled_limit_order_carries_without_creating_trade_log_entries() -> None:
    strategy = NeverFilledLimitStrategy()

    result = run_engine_backtest(
        bars=fixture_bar_series(),
        strategy=strategy,
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
    assert strategy._placed is True


def test_backtest_runner_fills_gap_crossed_buy_limit_at_open() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=105.0, low=95.0, close=104.0, volume=10.0),
        TimeBar(timestamp=120, open=95.0, high=101.0, low=90.0, close=99.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=GapCrossedBuyLimitStrategy(),
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
        strategy=IntrabarTouchedBuyLimitStrategy(),
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
        strategy=MarketableBuyLimitStrategy(),
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 121.0, 120),
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
        strategy=OlderLimitThenNewerMarketExitStrategy(),
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 111.0, 120),
        ("sell", 115.0, 240),
        ("sell", 114.0, 240),
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
        strategy=SellWhileFlatStrategy(),
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
        strategy=RepeatedExitSignalsStrategy(),
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
            strategy=BuyAndHoldStrategy(),
        )
