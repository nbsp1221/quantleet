from __future__ import annotations

import math

from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BookLevel, FillEvent, TickEvent
from quantleet.trading.domain.intents import _is_stop_order_type
from quantleet.trading.domain.orders import Order


def is_order_triggered(order: Order, tick: TickEvent) -> bool:
    if order.symbol != tick.symbol:
        raise ValueError("symbol mismatch between order and tick")
    if not _is_stop_order_type(order.order_type):
        return False
    if order.is_triggered:
        return False
    if order.trigger_type != "last":
        raise ValueError("unsupported trigger_type for first-slice stop matching")
    return order.is_triggered_by_price(price=tick.last)


def match_order(
    order: Order,
    tick: TickEvent,
    costs: CostConfig,
) -> FillEvent | None:
    if order.symbol != tick.symbol:
        raise ValueError("symbol mismatch between order and tick")
    if order.remaining_quantity <= 0.0:
        raise ValueError("match_order requires a positive remaining quantity")
    if not order.is_executable:
        return None

    levels = tick.asks if order.side == "buy" else tick.bids
    matched = _match_notional(
        levels=levels,
        quantity=order.remaining_quantity,
        limit_price=order.limit_price,
        side=order.side,
    )
    if matched is None:
        return None

    base_price = matched / order.remaining_quantity
    if order.executable_order_type == "market":
        slippage = costs.tick_size * costs.slippage_ticks
        fill_price = base_price + slippage if order.side == "buy" else base_price - slippage
    else:
        fill_price = base_price

    fee = round(fill_price * order.remaining_quantity * costs.fee_rate, 12)
    return FillEvent(
        symbol=order.symbol,
        side=order.side,
        quantity=order.remaining_quantity,
        price=round(fill_price, 12),
        timestamp=tick.timestamp,
        fee=fee,
    )


def _match_notional(
    *,
    levels: tuple[BookLevel, ...],
    quantity: float,
    limit_price: float | None,
    side: str,
) -> float | None:
    remaining = quantity
    notional = 0.0

    for price, available in levels:
        if limit_price is not None and not _price_is_within_limit(
            side=side,
            price=price,
            limit_price=limit_price,
        ):
            break

        taken = remaining if math.isinf(available) else min(remaining, available)
        if taken <= 0.0:
            continue

        notional += price * taken
        remaining -= taken
        if remaining <= 0.0:
            return notional

    return None


def _price_is_within_limit(*, side: str, price: float, limit_price: float) -> bool:
    if side == "buy":
        return price <= limit_price
    return price >= limit_price


__all__ = ["is_order_triggered", "match_order"]
