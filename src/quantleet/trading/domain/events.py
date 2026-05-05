from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from quantleet.trading.domain.intents import OrderSide, OrderType

BookLevel = tuple[float, float]
OrderRejectionReason = Literal[
    "insufficient_cash",
    "insufficient_position",
    "below_minimum_size",
    "below_minimum_cost",
    "no_buy_budget_available",
    "no_closable_position",
    "buy_budget_unaffordable",
    "execution_affordability",
]


@dataclass(frozen=True, slots=True)
class TickEvent:
    timestamp: int
    symbol: str
    bids: tuple[BookLevel, ...]
    asks: tuple[BookLevel, ...]
    last: float
    last_size: float | None = None


@dataclass(frozen=True, slots=True)
class BarEvent:
    bar_type: str
    bar_spec: object
    symbol: str
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    is_closed: bool


@dataclass(frozen=True, slots=True)
class FillEvent:
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    timestamp: int
    fee: float


@dataclass(frozen=True, slots=True)
class OrderRejectedEvent:
    symbol: str
    side: OrderSide
    order_type: OrderType
    reason: OrderRejectionReason
    timestamp: int
    quantity: float | None = None
    order_id: int | None = None
    tag: str | None = None
