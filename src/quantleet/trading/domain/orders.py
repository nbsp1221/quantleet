from __future__ import annotations

import math
from dataclasses import dataclass

from quantleet.trading.domain.events import FillEvent
from quantleet.trading.domain.intents import (
    OrderIntent,
    OrderSide,
    OrderType,
    TriggerCondition,
    TriggerType,
    _is_stop_order_type,
)


@dataclass(frozen=True, slots=True)
class Order:
    id: int
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    trigger_price: float | None = None
    trigger_condition: TriggerCondition | None = None
    trigger_type: TriggerType | None = None
    triggered_at: int | None = None
    limit_price: float | None = None
    tag: str | None = None
    filled_quantity: float = 0.0

    def __post_init__(self) -> None:
        if not math.isfinite(self.quantity) or self.quantity <= 0.0:
            raise ValueError("Order requires a positive finite quantity")
        if not math.isfinite(self.filled_quantity) or self.filled_quantity < 0.0:
            raise ValueError("Order filled_quantity must be a non-negative finite quantity")
        if self.filled_quantity > self.quantity:
            raise ValueError("Order filled_quantity cannot exceed quantity")
        if self.order_type == "limit" and self.limit_price is None:
            raise ValueError("limit orders require a limit_price")
        if _is_stop_order_type(self.order_type):
            if self.trigger_price is None:
                raise ValueError(f"{self.order_type} orders require a trigger_price")
            if self.trigger_condition is None:
                raise ValueError(f"{self.order_type} orders require a trigger_condition")
            if self.trigger_type is None:
                raise ValueError(f"{self.order_type} orders require a trigger_type")
            if self.order_type == "stop_market" and self.limit_price is not None:
                raise ValueError("stop_market orders cannot specify a limit_price")
            if self.order_type == "stop_limit" and self.limit_price is None:
                raise ValueError("stop_limit orders require a limit_price")
        else:
            if self.trigger_price is not None:
                raise ValueError("trigger_price is only valid for stop-family orders")
            if self.trigger_condition is not None:
                raise ValueError("trigger_condition is only valid for stop-family orders")
            if self.trigger_type is not None:
                raise ValueError("trigger_type is only valid for stop-family orders")
            if self.triggered_at is not None:
                raise ValueError("triggered_at is only valid for stop-family orders")

    @classmethod
    def from_intent(cls, *, order_id: int, intent: OrderIntent) -> Order:
        return cls(
            id=order_id,
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            order_type=intent.order_type,
            trigger_price=intent.trigger_price,
            trigger_condition=intent.trigger_condition,
            trigger_type=intent.trigger_type,
            limit_price=intent.limit_price,
            tag=intent.tag,
        )

    @property
    def remaining_quantity(self) -> float:
        return round(self.quantity - self.filled_quantity, 12)

    @property
    def is_open(self) -> bool:
        return self.remaining_quantity > 0.0

    @property
    def is_triggered(self) -> bool:
        return self.triggered_at is not None

    @property
    def is_executable(self) -> bool:
        if not _is_stop_order_type(self.order_type):
            return True
        return self.is_triggered

    @property
    def executable_order_type(self) -> OrderType:
        if self.order_type == "stop_market":
            return "market"
        if self.order_type == "stop_limit":
            return "limit"
        return self.order_type

    def is_triggered_by_price(self, *, price: float) -> bool:
        if not _is_stop_order_type(self.order_type):
            raise ValueError("only stop-family orders support trigger-price evaluation")

        trigger_price = self.trigger_price
        trigger_condition = self.trigger_condition
        if trigger_price is None or trigger_condition is None:
            raise ValueError("stop-family trigger facts must be present")

        if trigger_condition == "crosses_above":
            return price >= trigger_price
        return price <= trigger_price

    def trigger(self, *, timestamp: int) -> Order:
        if not _is_stop_order_type(self.order_type):
            raise ValueError("only stop-family orders can be triggered")
        if self.is_triggered:
            raise ValueError("stop-family order has already been triggered")
        return Order(
            id=self.id,
            symbol=self.symbol,
            side=self.side,
            quantity=self.quantity,
            order_type=self.order_type,
            trigger_price=self.trigger_price,
            trigger_condition=self.trigger_condition,
            trigger_type=self.trigger_type,
            triggered_at=timestamp,
            limit_price=self.limit_price,
            tag=self.tag,
            filled_quantity=self.filled_quantity,
        )

    def apply_fill(self, fill: FillEvent) -> Order:
        if not self.is_open:
            raise ValueError("cannot apply a fill to a terminal order")
        if not self.is_executable:
            raise ValueError("cannot apply a fill to a dormant stop order")
        if fill.symbol != self.symbol:
            raise ValueError("fill symbol does not match the order symbol")
        if fill.side != self.side:
            raise ValueError("fill side does not match the order side")
        if fill.quantity <= 0.0:
            raise ValueError("fill quantity must be positive")
        if fill.quantity > self.remaining_quantity:
            raise ValueError("fill quantity exceeds the remaining order quantity")

        next_filled = round(self.filled_quantity + fill.quantity, 12)
        return Order(
            id=self.id,
            symbol=self.symbol,
            side=self.side,
            quantity=self.quantity,
            order_type=self.order_type,
            trigger_price=self.trigger_price,
            trigger_condition=self.trigger_condition,
            trigger_type=self.trigger_type,
            triggered_at=self.triggered_at,
            limit_price=self.limit_price,
            tag=self.tag,
            filled_quantity=next_filled,
        )


__all__ = ["Order"]
