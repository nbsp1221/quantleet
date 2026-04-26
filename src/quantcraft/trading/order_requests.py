from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real

from quantcraft.trading.domain.intents import (
    OrderIntent,
    OrderSide,
    OrderType,
    TriggerCondition,
)


@dataclass(frozen=True, slots=True)
class PendingOrderRequest:
    symbol: str
    side: OrderSide
    quantity: float | None = None
    qty_percent: float | None = None
    order_type: OrderType = "market"
    stop_price: float | None = None
    trigger_condition: TriggerCondition | None = None
    limit_price: float | None = None
    tag: str | None = None

    def __post_init__(self) -> None:
        has_quantity = self.quantity is not None
        has_qty_percent = self.qty_percent is not None
        if has_quantity == has_qty_percent:
            raise ValueError("PendingOrderRequest requires exactly one sizing mode")
        if self.quantity is not None:
            if not _is_finite_number(self.quantity) or self.quantity <= 0.0:
                raise ValueError("quantity must be a positive finite float")
        if self.qty_percent is not None:
            if not _is_finite_number(self.qty_percent):
                raise ValueError("qty_percent must be numeric")
            if not (0.0 < self.qty_percent <= 100.0):
                raise ValueError("qty_percent must satisfy 0 < qty_percent <= 100")
        if self.order_type == "limit" and self.limit_price is None:
            raise ValueError("limit orders require a limit_price")
        if self.order_type == "stop_market" and self.stop_price is None:
            raise ValueError("stop_market orders require a stop_price")
        if self.order_type == "stop_market" and self.trigger_condition is None:
            raise ValueError("stop_market orders require a trigger_condition")
        if self.order_type == "stop_market" and self.limit_price is not None:
            raise ValueError("stop_market orders cannot specify a limit_price")
        if self.limit_price is not None and (
            not _is_finite_number(self.limit_price) or self.limit_price <= 0.0
        ):
            raise ValueError("limit_price must be a positive finite float")
        if self.stop_price is not None and (
            not _is_finite_number(self.stop_price) or self.stop_price <= 0.0
        ):
            raise ValueError("stop_price must be a positive finite float")
        if self.order_type != "stop_market" and self.stop_price is not None:
            raise ValueError("stop_price is only valid for stop_market orders")
        if self.order_type != "stop_market" and self.trigger_condition is not None:
            raise ValueError("trigger_condition is only valid for stop_market orders")

    def to_order_intent(self, *, quantity: float) -> OrderIntent:
        return OrderIntent(
            symbol=self.symbol,
            side=self.side,
            quantity=quantity,
            order_type=self.order_type,
            trigger_price=self.stop_price,
            trigger_condition=self.trigger_condition,
            trigger_type="last" if self.order_type == "stop_market" else None,
            limit_price=self.limit_price,
            tag=self.tag,
        )


def _is_finite_number(value: object) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(float(value))


__all__ = ["PendingOrderRequest"]
