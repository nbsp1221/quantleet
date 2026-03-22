from __future__ import annotations

import math

from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import BookLevel, FillEvent, TickEvent
from quantcraft.trading.domain.intents import OrderIntent


def match_order_intent(
    intent: OrderIntent,
    tick: TickEvent,
    costs: CostConfig,
) -> FillEvent | None:
    if intent.symbol != tick.symbol:
        raise ValueError("symbol mismatch between intent and tick")
    if intent.quantity <= 0.0:
        raise ValueError("match_order_intent requires a positive quantity")

    levels = tick.asks if intent.side == "buy" else tick.bids
    matched = _match_notional(
        levels=levels,
        quantity=intent.quantity,
        limit_price=intent.limit_price,
        side=intent.side,
    )
    if matched is None:
        return None

    base_price = matched / intent.quantity
    if intent.order_type == "market":
        slippage = costs.tick_size * costs.slippage_ticks
        fill_price = base_price + slippage if intent.side == "buy" else base_price - slippage
    else:
        fill_price = base_price

    fee = round(fill_price * intent.quantity * costs.fee_rate, 12)
    return FillEvent(
        symbol=intent.symbol,
        side=intent.side,
        quantity=intent.quantity,
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
