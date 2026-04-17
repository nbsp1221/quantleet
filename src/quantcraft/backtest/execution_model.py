from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

from quantcraft.data import BarSeries, TimeBar
from quantcraft.trading.domain.events import BarEvent, TickEvent
from quantcraft.trading.domain.intents import OrderIntent

_UNBOUNDED_LEVEL_SIZE = math.inf


SyntheticEvent = TickEvent | BarEvent


class BacktestExecutionModel(Protocol):
    @property
    def name(self) -> str: ...

    def tick_events_for_bar(
        self,
        *,
        symbol: str,
        previous_close: float | None,
        bar: TimeBar,
        active_intents: tuple[OrderIntent, ...] = (),
    ) -> tuple[TickEvent, ...]: ...

    def events_from_bars(self, *, bars: BarSeries) -> tuple[SyntheticEvent, ...]: ...


@dataclass(frozen=True, slots=True)
class ConservativeOHLCVExecutionModel:
    @property
    def name(self) -> str:
        return "conservative_ohlcv"

    def infer_intrabar_prices(self, bar: TimeBar) -> tuple[float, float, float, float]:
        if bar.close >= bar.open:
            return (bar.open, bar.low, bar.high, bar.close)

        return (bar.open, bar.high, bar.low, bar.close)

    def tick_events_for_bar(
        self,
        *,
        symbol: str,
        previous_close: float | None,
        bar: TimeBar,
        active_intents: tuple[OrderIntent, ...] = (),
    ) -> tuple[TickEvent, ...]:
        prices: list[float] = [bar.open]
        del previous_close

        path = self.infer_intrabar_prices(bar)
        for start, end in zip(path, path[1:]):
            prices.extend(
                self._crossing_prices_for_segment(
                    symbol=symbol,
                    start=start,
                    end=end,
                    active_intents=active_intents,
                )
            )
            if end != prices[-1]:
                prices.append(end)

        return tuple(
            self._tick_event(symbol=symbol, timestamp=bar.timestamp, price=price)
            for price in prices
        )

    def events_from_bars(self, *, bars: BarSeries) -> tuple[SyntheticEvent, ...]:
        rows = bars.rows
        if any(current.timestamp >= nxt.timestamp for current, nxt in zip(rows, rows[1:])):
            raise ValueError("out-of-order time bars")

        events: list[SyntheticEvent] = []
        previous_close: float | None = None

        for row in rows:
            events.extend(
                self.tick_events_for_bar(
                    symbol=bars.symbol,
                    previous_close=previous_close,
                    bar=row,
                )
            )
            events.append(
                self._bar_event(
                    symbol=bars.symbol,
                    timeframe=bars.timeframe,
                    bar_type=bars.bar_type,
                    bar=row,
                )
            )
            previous_close = row.close

        return tuple(events)

    def _crossing_prices_for_segment(
        self,
        *,
        symbol: str,
        start: float,
        end: float,
        active_intents: tuple[OrderIntent, ...],
    ) -> tuple[float, ...]:
        if start == end:
            return ()

        crossed_prices: list[float] = []
        low = min(start, end)
        high = max(start, end)

        for intent in active_intents:
            if (
                intent.symbol != symbol
                or intent.order_type != "limit"
                or intent.limit_price is None
            ):
                continue
            if self._is_marketable_at_price(intent=intent, price=start):
                continue
            if not low <= intent.limit_price <= high:
                continue
            crossed_prices.append(intent.limit_price)

        ordered_prices = sorted(set(crossed_prices), reverse=start > end)
        return tuple(price for price in ordered_prices if price != start)

    @staticmethod
    def _is_marketable_at_price(*, intent: OrderIntent, price: float) -> bool:
        if intent.limit_price is None:
            return False
        if intent.side == "buy":
            return price <= intent.limit_price
        return price >= intent.limit_price

    @staticmethod
    def _tick_event(*, symbol: str, timestamp: int, price: float) -> TickEvent:
        return TickEvent(
            timestamp=timestamp,
            symbol=symbol,
            bids=((price, _UNBOUNDED_LEVEL_SIZE),),
            asks=((price, _UNBOUNDED_LEVEL_SIZE),),
            last=price,
        )

    @staticmethod
    def _bar_event(*, symbol: str, timeframe: str, bar_type: str, bar: TimeBar) -> BarEvent:
        return BarEvent(
            bar_type=bar_type,
            bar_spec=timeframe,
            symbol=symbol,
            timestamp=bar.timestamp,
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=bar.volume,
            is_closed=True,
        )


__all__ = [
    "BacktestExecutionModel",
    "ConservativeOHLCVExecutionModel",
    "SyntheticEvent",
]
