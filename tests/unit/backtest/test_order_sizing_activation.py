from __future__ import annotations

from quantcraft.backtest.strategy_runtime import _StrategyDriver
from quantcraft.data import BarSeries, TimeBar
from quantcraft.research.strategy import Strategy
from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import BarEvent
from quantcraft.trading.domain.intents import OrderIntent
from quantcraft.trading.domain.orders import Order
from quantcraft.trading.domain.state import TradingState


class PercentBuyStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.buy(qty_percent=50.0, tag="half-entry")


class DoublePercentBuyStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.buy(qty_percent=50.0, tag="first")
        self.buy(qty_percent=50.0, tag="second")


class PercentSellStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.sell(qty_percent=50.0, tag="half-exit")


class LimitPercentBuyStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.buy(qty_percent=50.0, order_type="limit", limit_price=20.0, tag="limit-entry")


def _runtime(strategy: Strategy) -> _StrategyDriver:
    return _StrategyDriver(strategy)


def _bars() -> BarSeries:
    return BarSeries(
        symbol="BTC/USDT",
        timeframe="1m",
        bar_type="time",
        rows=(
            TimeBar(timestamp=60, open=100.0, high=105.0, low=95.0, close=104.0, volume=10.0),
            TimeBar(timestamp=120, open=10.0, high=12.0, low=9.0, close=11.0, volume=12.0),
        ),
    )


def _bar_event(timestamp: int, *, symbol: str = "BTC/USDT") -> BarEvent:
    return BarEvent(
        bar_type="time",
        bar_spec="1m",
        symbol=symbol,
        timestamp=timestamp,
        open=100.0 if timestamp == 60 else 10.0,
        high=105.0 if timestamp == 60 else 12.0,
        low=95.0 if timestamp == 60 else 9.0,
        close=104.0 if timestamp == 60 else 11.0,
        volume=10.0 if timestamp == 60 else 12.0,
        is_closed=True,
    )


def test_percent_requests_resolve_only_at_next_bar_activation() -> None:
    runtime = _runtime(PercentBuyStrategy())
    runtime.initialize(bars=_bars())
    runtime.handle_bar(_bar_event(60), state=TradingState(cash=100.0, equity=100.0))

    assert runtime.order_state().active == ()

    runtime.activate_pending_order_requests(
        bar=_bars().rows[1],
        state=TradingState(cash=100.0, equity=100.0),
        costs=CostConfig(tick_size=0.1, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert runtime.order_state().active[0].quantity == 5.0


def test_same_cycle_percent_buys_resolve_serially_against_updated_reservations() -> None:
    runtime = _runtime(DoublePercentBuyStrategy())
    runtime.initialize(bars=_bars())
    runtime.handle_bar(_bar_event(60), state=TradingState(cash=100.0, equity=100.0))

    runtime.activate_pending_order_requests(
        bar=_bars().rows[1],
        state=TradingState(cash=100.0, equity=100.0),
        costs=CostConfig(tick_size=0.1, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple(order.quantity for order in runtime.order_state().active) == (5.0, 2.5)


def test_same_cycle_percent_exits_resolve_against_net_closable_after_prior_exit_reservation() -> (
    None
):
    runtime = _runtime(PercentSellStrategy())
    runtime.initialize(bars=_bars())
    runtime.handle_bar(
        _bar_event(60),
        state=TradingState(
            cash=100.0, position_quantity=10.0, average_entry_price=8.0, equity=200.0
        ),
    )
    runtime.replace_active_orders(
        (
            Order.from_intent(
                order_id=1,
                intent=OrderIntent(
                    symbol="BTC/USDT",
                    side="sell",
                    quantity=4.0,
                    order_type="market",
                ),
            ),
        )
    )

    runtime.activate_pending_order_requests(
        bar=_bars().rows[1],
        state=TradingState(
            cash=100.0, position_quantity=10.0, average_entry_price=8.0, equity=200.0
        ),
        costs=CostConfig(tick_size=0.1, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple(order.quantity for order in runtime.order_state().active) == (4.0, 3.0)


def test_limit_buy_percent_uses_submitted_limit_price_not_optimistic_mark() -> None:
    runtime = _runtime(LimitPercentBuyStrategy())
    runtime.initialize(bars=_bars())
    runtime.handle_bar(_bar_event(60), state=TradingState(cash=100.0, equity=100.0))

    runtime.activate_pending_order_requests(
        bar=_bars().rows[1],
        state=TradingState(cash=100.0, equity=100.0),
        costs=CostConfig(tick_size=0.1, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert runtime.order_state().active[0].quantity == 2.5


def test_flat_sell_qty_percent_resolves_to_no_new_order() -> None:
    runtime = _runtime(PercentSellStrategy())
    runtime.initialize(bars=_bars())
    runtime.handle_bar(_bar_event(60), state=TradingState(cash=100.0, equity=100.0))

    runtime.activate_pending_order_requests(
        bar=_bars().rows[1],
        state=TradingState(cash=100.0, equity=100.0),
        costs=CostConfig(tick_size=0.1, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert runtime.order_state().active == ()


def test_dormant_stop_market_buy_does_not_reduce_ordinary_percent_buy_budget() -> None:
    runtime = _runtime(PercentBuyStrategy())
    runtime.initialize(bars=_bars())
    runtime.handle_bar(_bar_event(60), state=TradingState(cash=100.0, equity=100.0))
    runtime.replace_active_orders(
        (
            Order.from_intent(
                order_id=1,
                intent=OrderIntent(
                    symbol="BTC/USDT",
                    side="buy",
                    quantity=1.0,
                    order_type="stop_market",
                    trigger_price=20.0,
                    trigger_condition="crosses_above",
                    trigger_type="last",
                ),
            ),
        )
    )

    runtime.activate_pending_order_requests(
        bar=_bars().rows[1],
        state=TradingState(cash=100.0, equity=100.0),
        costs=CostConfig(tick_size=0.1, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert tuple(order.quantity for order in runtime.order_state().active) == (1.0, 5.0)
