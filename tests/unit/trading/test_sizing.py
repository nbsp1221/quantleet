from __future__ import annotations

import pytest

from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.intents import OrderIntent
from quantcraft.trading.domain.orders import Order
from quantcraft.trading.domain.state import TradingState
from quantcraft.trading.order_requests import PendingOrderRequest
from quantcraft.trading.sizing import (
    SizingConstraints,
    SizingReservations,
    resolve_pending_order_request,
)


def test_buy_qty_percent_preserves_requested_position_budget_when_affordable() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=80.0, equity=80.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.01),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 4.0


def test_buy_qty_percent_clamps_only_when_requested_budget_plus_fees_is_unaffordable() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=100.0,
            order_type="market",
        ),
        state=TradingState(cash=80.0, equity=80.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.01),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == pytest.approx(80.0 / 10.1)


def test_buy_qty_percent_uses_remaining_buy_reservations_when_computing_basis() -> None:
    active_buy = Order.from_intent(
        order_id=1,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="limit",
            limit_price=10.0,
        ),
    ).apply_fill(
        fill=type(
            "FillStub",
            (),
            {
                "symbol": "BTC/USDT",
                "side": "buy",
                "quantity": 1.0,
                "price": 10.0,
                "timestamp": 60,
                "fee": 0.0,
            },
        )()
    )

    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(active_buy,),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 4.5


def test_sell_qty_percent_uses_net_closable_quantity_after_active_exit_reservations() -> None:
    active_exit = Order.from_intent(
        order_id=2,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=4.0,
            order_type="limit",
            limit_price=12.0,
        ),
    ).apply_fill(
        fill=type(
            "FillStub",
            (),
            {
                "symbol": "BTC/USDT",
                "side": "sell",
                "quantity": 1.0,
                "price": 12.0,
                "timestamp": 60,
                "fee": 0.0,
            },
        )()
    )

    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            qty_percent=30.0,
            order_type="market",
        ),
        state=TradingState(
            cash=0.0, equity=100.0, position_quantity=10.0, average_entry_price=10.0
        ),
        active_orders=(active_exit,),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 2.1


def test_subminimum_or_flat_percent_requests_resolve_to_explicit_noop() -> None:
    constraints = SizingConstraints(quantity_increment=1.0, min_quantity=1.0)

    tiny_buy = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=10.0,
            order_type="market",
        ),
        state=TradingState(cash=5.0, equity=5.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=constraints,
    )
    flat_sell = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            qty_percent=100.0,
            order_type="market",
        ),
        state=TradingState(cash=5.0, equity=5.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=constraints,
    )

    assert tiny_buy.quantity is None
    assert tiny_buy.reason == "below_minimum_size"
    assert flat_sell.quantity is None
    assert flat_sell.reason == "no_closable_position"


def test_buy_percent_serial_reservation_uses_resolved_order_budget_after_rounding() -> None:
    first = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(quantity_increment=3.0),
    )

    second = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(quantity_increment=3.0),
        reservations=SizingReservations().reserve(first),
    )

    assert first.quantity == 3.0
    assert first.cash_consumption == 30.0
    assert second.quantity == 3.0


def test_dormant_stop_market_buys_do_not_reduce_ordinary_buy_percent_budget() -> None:
    dormant_stop = Order.from_intent(
        order_id=3,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="stop_market",
            trigger_price=15.0,
            trigger_condition="crosses_above",
            trigger_type="last",
        ),
    )

    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(dormant_stop,),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 5.0
