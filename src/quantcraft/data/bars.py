from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class TimeBar:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        prices = (self.open, self.high, self.low, self.close)
        if not isinstance(self.timestamp, int) or isinstance(self.timestamp, bool):
            raise ValueError("invalid time bar")
        if not all(math.isfinite(price) for price in prices):
            raise ValueError("invalid time bar")
        if not math.isfinite(self.volume) or self.volume < 0.0:
            raise ValueError("invalid time bar")
        if self.high < max(self.open, self.low, self.close):
            raise ValueError("invalid time bar")
        if self.low > min(self.open, self.high, self.close):
            raise ValueError("invalid time bar")


@dataclass(frozen=True, slots=True, kw_only=True)
class BarSeries:
    symbol: str
    timeframe: str
    bar_type: str
    rows: tuple[TimeBar, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol:
            raise ValueError("invalid bar series metadata")
        if not isinstance(self.timeframe, str) or not self.timeframe:
            raise ValueError("invalid bar series metadata")
        if self.bar_type != "time":
            raise ValueError("bar_type must be 'time'")
        if not isinstance(self.rows, tuple) or not all(
            isinstance(row, TimeBar) for row in self.rows
        ):
            raise ValueError("rows must be a tuple of TimeBar")
