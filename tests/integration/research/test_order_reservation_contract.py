from __future__ import annotations

import pytest

from quantleet.data import TimeBar
from quantleet.research import Strategy
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import OrderRejectedEvent
from tests.integration.research.support_backtest_runner import make_bar_series, run_engine_backtest


class PercentStopMarketGapEntryStrategy(Strategy):
    def on_bar(self, bar) -> None:
        if len(self.data.close) == 1:
            self.buy(
                qty_percent=100.0,
                order_type="stop_market",
                stop_price=105.0,
                tag="gap-entry",
            )


class DormantStopThenMarketEntryStrategy(Strategy):
    def on_bar(self, bar) -> None:
        if len(self.data.close) == 1:
            self.buy(
                qty_percent=50.0,
                order_type="stop_limit",
                stop_price=130.0,
                limit_price=120.0,
                tag="dormant-stop",
            )
            self.buy(qty_percent=50.0, tag="market-entry")


class StopMarketAndCompetingLimitStrategy(Strategy):
    def on_bar(self, bar) -> None:
        if len(self.data.close) == 1:
            self.buy(
                qty_percent=50.0,
                order_type="stop_market",
                stop_price=105.0,
                tag="stop-entry",
            )
            self.buy(
                qty_percent=100.0,
                order_type="limit",
                limit_price=100.0,
                tag="limit-entry",
            )


def test_stop_market_gap_overspend_rejects_without_negative_cash_or_fill() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=150.0, high=150.0, low=150.0, close=150.0, volume=10.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=PercentStopMarketGapEntryStrategy(),
        initial_cash=100.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert result.trade_log == ()
    assert result.final_state.cash == 100.0
    assert result.final_state.position_quantity == 0.0
    assert result.order_events == (
        OrderRejectedEvent(
            symbol="BTC/USDT",
            side="buy",
            order_type="stop_market",
            reason="execution_affordability",
            timestamp=120,
            quantity=0.95238095238,
            order_id=1,
            tag="gap-entry",
        ),
    )


def test_stop_market_gap_overspend_cannot_consume_other_order_reservation() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=150.0, high=150.0, low=150.0, close=150.0, volume=10.0),
        TimeBar(timestamp=180, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=StopMarketAndCompetingLimitStrategy(),
        initial_cash=200.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple((fill.side, fill.price) for fill in result.trade_log) == (("buy", 100.0),)
    assert result.trade_log[0].quantity == pytest.approx(1.0)
    assert result.order_events == (
        OrderRejectedEvent(
            symbol="BTC/USDT",
            side="buy",
            order_type="stop_market",
            reason="execution_affordability",
            timestamp=120,
            quantity=0.95238095238,
            order_id=1,
            tag="stop-entry",
        ),
    )


def test_dormant_stop_limit_reservation_reduces_later_same_cycle_percent_buy() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=100.0, high=101.0, low=99.0, close=100.0, volume=10.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=DormantStopThenMarketEntryStrategy(),
        initial_cash=100.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple((fill.side, fill.quantity, fill.price) for fill in result.trade_log) == (
        ("buy", 0.25, 100.0),
    )
    assert result.order_events == ()
