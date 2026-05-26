from __future__ import annotations

import math
from dataclasses import fields

import pytest

from quantleet.trading.domain.events import FillEvent
from quantleet.trading.domain.intents import OrderIntent
from quantleet.trading.domain.orders import Order


def test_order_from_intent_preserves_runtime_fields() -> None:
    order = Order.from_intent(
        order_id=7,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="stop_market",
            trigger_price=101.0,
            trigger_condition="crosses_above",
            trigger_type="last",
            tag="entry",
        ),
    )

    assert order.id == 7
    assert order.symbol == "BTC/USDT"
    assert order.side == "buy"
    assert order.quantity == 2.0
    assert order.order_type == "stop_market"
    assert order.trigger_price == 101.0
    assert order.trigger_condition == "crosses_above"
    assert order.trigger_type == "last"
    assert order.triggered_at is None
    assert order.tag == "entry"
    assert order.filled_quantity == 0.0
    assert order.remaining_quantity == 2.0
    assert order.is_open is True
    assert order.is_triggered is False
    assert order.is_executable is False
    assert order.executable_order_type == "market"


def test_stop_limit_order_from_intent_is_dormant_until_triggered() -> None:
    order = Order.from_intent(
        order_id=8,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_limit",
            trigger_price=105.0,
            trigger_condition="crosses_above",
            trigger_type="last",
            limit_price=106.0,
            tag="breakout",
        ),
    )

    assert order.id == 8
    assert order.order_type == "stop_limit"
    assert order.trigger_price == 105.0
    assert order.trigger_condition == "crosses_above"
    assert order.trigger_type == "last"
    assert order.limit_price == 106.0
    assert order.tag == "breakout"
    assert order.is_open is True
    assert order.is_triggered is False
    assert order.is_executable is False
    assert order.executable_order_type == "limit"


def test_runtime_order_field_surface_is_trigger_aware() -> None:
    assert tuple(field.name for field in fields(Order)) == (
        "id",
        "symbol",
        "side",
        "quantity",
        "order_type",
        "trigger_price",
        "trigger_condition",
        "trigger_type",
        "triggered_at",
        "limit_price",
        "tag",
        "filled_quantity",
    )


def test_stop_market_price_trigger_predicate_uses_runtime_trigger_condition() -> None:
    crosses_above = Order.from_intent(
        order_id=1,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=101.0,
            trigger_condition="crosses_above",
            trigger_type="last",
        ),
    )
    crosses_below = Order.from_intent(
        order_id=2,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=99.0,
            trigger_condition="crosses_below",
            trigger_type="last",
        ),
    )

    assert crosses_above.is_triggered_by_price(price=101.0) is True
    assert crosses_above.is_triggered_by_price(price=100.0) is False
    assert crosses_below.is_triggered_by_price(price=99.0) is True
    assert crosses_below.is_triggered_by_price(price=100.0) is False


def test_stop_limit_price_trigger_predicate_uses_runtime_trigger_condition() -> None:
    crosses_above = Order.from_intent(
        order_id=1,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_limit",
            trigger_price=101.0,
            trigger_condition="crosses_above",
            trigger_type="last",
            limit_price=102.0,
        ),
    )
    crosses_below = Order.from_intent(
        order_id=2,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=1.0,
            order_type="stop_limit",
            trigger_price=99.0,
            trigger_condition="crosses_below",
            trigger_type="last",
            limit_price=98.0,
        ),
    )

    assert crosses_above.is_triggered_by_price(price=101.0) is True
    assert crosses_above.is_triggered_by_price(price=100.0) is False
    assert crosses_below.is_triggered_by_price(price=99.0) is True
    assert crosses_below.is_triggered_by_price(price=100.0) is False


def test_non_stop_orders_reject_trigger_price_evaluation() -> None:
    order = Order.from_intent(
        order_id=1,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
        ),
    )

    with pytest.raises(
        ValueError,
        match="only stop-family orders support trigger-price evaluation",
    ):
        order.is_triggered_by_price(price=100.0)


def test_order_rejects_non_positive_quantity_at_creation() -> None:
    with pytest.raises(ValueError, match="positive finite quantity"):
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=0.0,
                order_type="market",
            ),
        )


def test_order_rejects_invalid_runtime_state_and_malformed_limit_orders() -> None:
    with pytest.raises(ValueError, match="non-negative finite quantity"):
        Order(
            id=1,
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
            filled_quantity=-1.0,
        )

    with pytest.raises(ValueError, match="cannot exceed quantity"):
        Order(
            id=1,
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
            filled_quantity=2.0,
        )

    with pytest.raises(ValueError, match="require a limit_price"):
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                order_type="limit",
            ),
        )

    with pytest.raises(ValueError, match="require a trigger_price"):
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                order_type="stop_market",
                trigger_condition="crosses_above",
                trigger_type="last",
            ),
        )

    with pytest.raises(ValueError, match="require a trigger_condition"):
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                order_type="stop_market",
                trigger_price=101.0,
                trigger_type="last",
            ),
        )

    with pytest.raises(ValueError, match="require a trigger_type"):
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                order_type="stop_market",
                trigger_price=101.0,
                trigger_condition="crosses_above",
            ),
        )

    with pytest.raises(ValueError, match="cannot specify a limit_price"):
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                order_type="stop_market",
                trigger_price=101.0,
                trigger_condition="crosses_above",
                trigger_type="last",
                limit_price=99.0,
            ),
        )

    with pytest.raises(ValueError, match="trigger_price is only valid"):
        Order(
            id=1,
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
            trigger_price=101.0,
        )

    with pytest.raises(ValueError, match="trigger_condition is only valid"):
        Order(
            id=1,
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
            trigger_condition="crosses_above",
        )

    with pytest.raises(ValueError, match="trigger_type is only valid"):
        Order(
            id=1,
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
            trigger_type="last",
        )

    with pytest.raises(ValueError, match="triggered_at is only valid"):
        Order(
            id=1,
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
            triggered_at=60,
        )

    with pytest.raises(ValueError, match="stop_limit orders require a limit_price"):
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                order_type="stop_limit",
                trigger_price=101.0,
                trigger_condition="crosses_above",
                trigger_type="last",
            ),
        )

    with pytest.raises(ValueError, match="stop_limit orders require a limit_price"):
        Order(
            id=1,
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_limit",
            trigger_price=101.0,
            trigger_condition="crosses_above",
            trigger_type="last",
        )

    with pytest.raises(ValueError, match="stop_limit orders require a trigger_price"):
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                order_type="stop_limit",
                trigger_condition="crosses_above",
                trigger_type="last",
                limit_price=102.0,
            ),
        )

    with pytest.raises(ValueError, match="stop_limit orders require a trigger_condition"):
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                order_type="stop_limit",
                trigger_price=101.0,
                trigger_type="last",
                limit_price=102.0,
            ),
        )

    with pytest.raises(ValueError, match="stop_limit orders require a trigger_type"):
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                order_type="stop_limit",
                trigger_price=101.0,
                trigger_condition="crosses_above",
                limit_price=102.0,
            ),
        )


def test_order_intent_rejects_trigger_fields_on_non_stop_orders() -> None:
    with pytest.raises(ValueError, match="trigger_price is only valid"):
        OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
            trigger_price=101.0,
        )

    with pytest.raises(ValueError, match="trigger_condition is only valid"):
        OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
            trigger_condition="crosses_above",
        )

    with pytest.raises(ValueError, match="trigger_type is only valid"):
        OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
            trigger_type="last",
        )


def test_order_direct_construction_rejects_malformed_stop_market_shape() -> None:
    with pytest.raises(ValueError, match="require a limit_price"):
        Order(
            id=1,
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="limit",
        )

    with pytest.raises(ValueError, match="require a trigger_price"):
        Order(
            id=1,
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            trigger_condition="crosses_above",
            trigger_type="last",
        )

    with pytest.raises(ValueError, match="require a trigger_condition"):
        Order(
            id=1,
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=101.0,
            trigger_type="last",
        )

    with pytest.raises(ValueError, match="require a trigger_type"):
        Order(
            id=1,
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=101.0,
            trigger_condition="crosses_above",
        )

    with pytest.raises(ValueError, match="cannot specify a limit_price"):
        Order(
            id=1,
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=101.0,
            trigger_condition="crosses_above",
            trigger_type="last",
            limit_price=100.0,
        )


@pytest.mark.parametrize("quantity", [0.0, -1.0, math.inf, math.nan])
def test_order_intent_rejects_non_positive_or_non_finite_quantity(quantity: float) -> None:
    with pytest.raises(ValueError, match="positive finite quantity"):
        OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=quantity,
            order_type="market",
        )


@pytest.mark.parametrize("quantity", [0.0, -1.0, math.inf, math.nan])
def test_order_rejects_non_positive_or_non_finite_quantity(quantity: float) -> None:
    with pytest.raises(ValueError, match="positive finite quantity"):
        Order(
            id=1,
            symbol="BTC/USDT",
            side="buy",
            quantity=quantity,
            order_type="market",
        )


def test_stop_market_order_from_intent_preserves_trigger_fields() -> None:
    order = Order.from_intent(
        order_id=7,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=120.0,
            trigger_condition="crosses_above",
            trigger_type="last",
            tag="entry",
        ),
    )

    assert order.trigger_price == 120.0
    assert order.trigger_condition == "crosses_above"
    assert order.trigger_type == "last"
    assert order.triggered_at is None
    assert order.is_triggered is False
    assert order.is_executable is False
    assert order.executable_order_type == "market"


def test_triggering_stop_limit_preserves_identity_and_becomes_limit_executable() -> None:
    order = Order.from_intent(
        order_id=7,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_limit",
            trigger_price=120.0,
            trigger_condition="crosses_above",
            trigger_type="last",
            limit_price=121.0,
            tag="entry",
        ),
    )

    triggered = order.trigger(timestamp=120)

    assert triggered.id == order.id
    assert triggered.order_type == "stop_limit"
    assert triggered.trigger_price == 120.0
    assert triggered.trigger_condition == "crosses_above"
    assert triggered.trigger_type == "last"
    assert triggered.triggered_at == 120
    assert triggered.limit_price == 121.0
    assert triggered.tag == "entry"
    assert triggered.filled_quantity == 0.0
    assert triggered.is_executable is True
    assert triggered.executable_order_type == "limit"


def test_dormant_stop_limit_rejects_fill_until_triggered() -> None:
    order = Order.from_intent(
        order_id=7,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_limit",
            trigger_price=120.0,
            trigger_condition="crosses_above",
            trigger_type="last",
            limit_price=121.0,
        ),
    )
    fill = FillEvent(
        symbol="BTC/USDT",
        side="buy",
        quantity=1.0,
        price=100.0,
        timestamp=60,
        fee=0.0,
    )

    with pytest.raises(ValueError, match="dormant stop order"):
        order.apply_fill(fill)

    assert order.trigger(timestamp=120).apply_fill(fill).filled_quantity == 1.0


def test_trigger_marks_stop_market_executable_once() -> None:
    order = Order.from_intent(
        order_id=9,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=95.0,
            trigger_condition="crosses_below",
            trigger_type="last",
        ),
    )

    triggered = order.trigger(timestamp=120)

    assert triggered.triggered_at == 120
    assert triggered.is_triggered is True
    assert triggered.is_executable is True

    with pytest.raises(ValueError, match="already been triggered"):
        triggered.trigger(timestamp=180)


def test_non_stop_orders_do_not_require_triggering_to_be_executable() -> None:
    order = Order.from_intent(
        order_id=16,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=1.0,
            order_type="limit",
            limit_price=110.0,
        ),
    )

    assert order.is_triggered is False
    assert order.is_executable is True
    assert order.executable_order_type == "limit"

    with pytest.raises(ValueError, match="only stop-family orders can be triggered"):
        order.trigger(timestamp=60)


def test_dormant_stop_market_rejects_fill_application_until_triggered() -> None:
    order = Order.from_intent(
        order_id=10,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=110.0,
            trigger_condition="crosses_above",
            trigger_type="last",
        ),
    )

    with pytest.raises(ValueError, match="dormant stop order"):
        order.apply_fill(
            FillEvent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                price=112.0,
                timestamp=60,
                fee=0.0,
            )
        )


def test_apply_fill_updates_remaining_quantity_and_marks_terminal_on_full_fill() -> None:
    order = Order.from_intent(
        order_id=3,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=2.0,
            order_type="limit",
            limit_price=110.0,
        ),
    )

    partially_filled = order.apply_fill(
        FillEvent(
            symbol="BTC/USDT",
            side="sell",
            quantity=1.0,
            price=110.0,
            timestamp=60,
            fee=0.0,
        )
    )
    assert partially_filled.remaining_quantity == 1.0
    assert partially_filled.is_open is True

    fully_filled = partially_filled.apply_fill(
        FillEvent(
            symbol="BTC/USDT",
            side="sell",
            quantity=1.0,
            price=110.0,
            timestamp=120,
            fee=0.0,
        )
    )
    assert fully_filled.remaining_quantity == 0.0
    assert fully_filled.is_open is False


def test_order_rejects_illegal_fill_application() -> None:
    order = Order.from_intent(
        order_id=4,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
        ),
    )

    with pytest.raises(ValueError, match="symbol"):
        order.apply_fill(
            FillEvent(
                symbol="ETH/USDT",
                side="buy",
                quantity=1.0,
                price=100.0,
                timestamp=60,
                fee=0.0,
            )
        )

    with pytest.raises(ValueError, match="exceeds the remaining"):
        order.apply_fill(
            FillEvent(
                symbol="BTC/USDT",
                side="buy",
                quantity=2.0,
                price=100.0,
                timestamp=60,
                fee=0.0,
            )
        )

    with pytest.raises(ValueError, match="order side"):
        order.apply_fill(
            FillEvent(
                symbol="BTC/USDT",
                side="sell",
                quantity=1.0,
                price=100.0,
                timestamp=60,
                fee=0.0,
            )
        )

    with pytest.raises(ValueError, match="must be positive"):
        order.apply_fill(
            FillEvent(
                symbol="BTC/USDT",
                side="buy",
                quantity=0.0,
                price=100.0,
                timestamp=60,
                fee=0.0,
            )
        )

    dormant_stop = Order.from_intent(
        order_id=8,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=120.0,
            trigger_condition="crosses_above",
            trigger_type="last",
        ),
    )

    with pytest.raises(ValueError, match="dormant stop order"):
        dormant_stop.apply_fill(
            FillEvent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                price=120.0,
                timestamp=120,
                fee=0.0,
            )
        )

    filled = order.apply_fill(
        FillEvent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            price=100.0,
            timestamp=60,
            fee=0.0,
        )
    )

    with pytest.raises(ValueError, match="terminal order"):
        filled.apply_fill(
            FillEvent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                price=100.0,
                timestamp=120,
                fee=0.0,
            )
        )
