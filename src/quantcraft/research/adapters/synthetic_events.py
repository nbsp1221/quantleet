from __future__ import annotations

import math

from quantcraft.data import OHLCVBar
from quantcraft.trading.domain.events import BarEvent, TickEvent

_UNBOUNDED_LEVEL_SIZE = math.inf


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
