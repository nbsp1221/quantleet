from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class OHLCVBar:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        prices = (self.open, self.high, self.low, self.close)
        if not isinstance(self.timestamp, int) or isinstance(self.timestamp, bool):
            raise ValueError("invalid OHLCV row")
        if not all(math.isfinite(price) for price in prices):
            raise ValueError("invalid OHLCV row")
        if not math.isfinite(self.volume) or self.volume < 0.0:
            raise ValueError("invalid OHLCV row")
        if self.high < max(self.open, self.low, self.close):
            raise ValueError("invalid OHLCV row")
        if self.low > min(self.open, self.high, self.close):
            raise ValueError("invalid OHLCV row")
