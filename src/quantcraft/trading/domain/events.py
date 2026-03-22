from __future__ import annotations

from dataclasses import dataclass

from quantcraft.trading.domain.intents import OrderSide

BookLevel = tuple[float, float]


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
