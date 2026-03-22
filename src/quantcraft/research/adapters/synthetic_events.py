from __future__ import annotations

import math
from dataclasses import dataclass

from quantcraft.trading.domain.events import BarEvent, TickEvent

_UNBOUNDED_LEVEL_SIZE = math.inf


@dataclass(frozen=True, slots=True)
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


SyntheticEvent = TickEvent | BarEvent


def infer_intrabar_prices(bar: OHLCVBar) -> tuple[float, float, float, float]:
    if bar.close >= bar.open:
        return (bar.open, bar.low, bar.high, bar.close)

    return (bar.open, bar.high, bar.low, bar.close)


def convert_ohlcv_to_backtest_events(
    *,
    symbol: str,
    bar_type: str,
    bar_spec: object,
    rows: tuple[OHLCVBar, ...],
) -> tuple[SyntheticEvent, ...]:
    if any(current.timestamp >= nxt.timestamp for current, nxt in zip(rows, rows[1:])):
        raise ValueError("out-of-order OHLCV rows")

    events: list[SyntheticEvent] = []

    for row in rows:
        for price in infer_intrabar_prices(row):
            events.append(
                TickEvent(
                    timestamp=row.timestamp,
                    symbol=symbol,
                    bids=((price, _UNBOUNDED_LEVEL_SIZE),),
                    asks=((price, _UNBOUNDED_LEVEL_SIZE),),
                    last=price,
                )
            )

        events.append(
            BarEvent(
                bar_type=bar_type,
                bar_spec=bar_spec,
                symbol=symbol,
                timestamp=row.timestamp,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close,
                volume=row.volume,
                is_closed=True,
            )
        )

    return tuple(events)
