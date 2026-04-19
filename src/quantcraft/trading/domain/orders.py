from __future__ import annotations

from dataclasses import dataclass

from quantcraft.trading.domain.events import FillEvent
from quantcraft.trading.domain.intents import OrderIntent, OrderSide, OrderType


@dataclass(frozen=True, slots=True)
class Order:
    id: int
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    limit_price: float | None = None
    tag: str | None = None
    filled_quantity: float = 0.0

    def __post_init__(self) -> None:
        if self.quantity <= 0.0:
            raise ValueError("Order requires a positive quantity")
        if self.filled_quantity < 0.0:
            raise ValueError("Order filled_quantity cannot be negative")
        if self.filled_quantity > self.quantity:
            raise ValueError("Order filled_quantity cannot exceed quantity")
        if self.order_type == "limit" and self.limit_price is None:
            raise ValueError("limit orders require a limit_price")

    @classmethod
    def from_intent(cls, *, order_id: int, intent: OrderIntent) -> Order:
        return cls(
            id=order_id,
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            order_type=intent.order_type,
            limit_price=intent.limit_price,
            tag=intent.tag,
        )

    @property
    def remaining_quantity(self) -> float:
        return round(self.quantity - self.filled_quantity, 12)

    @property
    def is_open(self) -> bool:
        return self.remaining_quantity > 0.0

    def apply_fill(self, fill: FillEvent) -> Order:
        if not self.is_open:
            raise ValueError("cannot apply a fill to a terminal order")
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
            limit_price=self.limit_price,
            tag=self.tag,
            filled_quantity=next_filled,
        )


__all__ = ["Order"]
