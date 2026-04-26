from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

OrderSide = Literal["buy", "sell"]
OrderType = Literal["market", "limit", "stop_market"]
TriggerCondition = Literal["crosses_above", "crosses_below"]
TriggerType = Literal["last"]


@dataclass(frozen=True, slots=True)
class OrderIntent:
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    trigger_price: float | None = None
    trigger_condition: TriggerCondition | None = None
    trigger_type: TriggerType | None = None
    limit_price: float | None = None
    tag: str | None = None

    def __post_init__(self) -> None:
        if self.order_type == "limit" and self.limit_price is None:
            raise ValueError("limit orders require a limit_price")
        if self.order_type == "stop_market":
            if self.trigger_price is None:
                raise ValueError("stop_market orders require a trigger_price")
            if self.trigger_condition is None:
                raise ValueError("stop_market orders require a trigger_condition")
            if self.trigger_type is None:
                raise ValueError("stop_market orders require a trigger_type")
            if self.limit_price is not None:
                raise ValueError("stop_market orders cannot specify a limit_price")
        else:
            if self.trigger_price is not None:
                raise ValueError("trigger_price is only valid for stop_market orders")
            if self.trigger_condition is not None:
                raise ValueError("trigger_condition is only valid for stop_market orders")
            if self.trigger_type is not None:
                raise ValueError("trigger_type is only valid for stop_market orders")
