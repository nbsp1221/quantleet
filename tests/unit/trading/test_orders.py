from __future__ import annotations

import pytest

from quantcraft.trading.domain.events import FillEvent
from quantcraft.trading.domain.intents import OrderIntent
from quantcraft.trading.domain.orders import Order


def test_order_from_intent_preserves_runtime_fields() -> None:
    order = Order.from_intent(
        order_id=7,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="limit",
            limit_price=101.0,
            tag="entry",
        ),
    )

    assert order.id == 7
    assert order.symbol == "BTC/USDT"
    assert order.side == "buy"
    assert order.quantity == 2.0
    assert order.order_type == "limit"
    assert order.limit_price == 101.0
    assert order.tag == "entry"
    assert order.filled_quantity == 0.0
    assert order.remaining_quantity == 2.0
    assert order.is_open is True


def test_order_rejects_non_positive_quantity_at_creation() -> None:
    with pytest.raises(ValueError, match="positive quantity"):
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
    with pytest.raises(ValueError, match="cannot be negative"):
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
