from __future__ import annotations

import math

from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import BookLevel, FillEvent, TickEvent
from quantcraft.trading.domain.orders import Order


def match_order(
    order: Order,
    tick: TickEvent,
    costs: CostConfig,
) -> FillEvent | None:
    if order.symbol != tick.symbol:
        raise ValueError("symbol mismatch between order and tick")
    if order.remaining_quantity <= 0.0:
        raise ValueError("match_order requires a positive remaining quantity")

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
    if order.order_type == "market":
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
__all__ = ["match_order"]
