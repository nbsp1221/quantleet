from __future__ import annotations

from dataclasses import dataclass

from quantcraft.data.adapters.exchange_backend import Exchange, MarketType
from quantcraft.data.domain import HistoricalDataSource, OHLCVBar


@dataclass(frozen=True, slots=True, kw_only=True)
class CCXTDataSource(HistoricalDataSource):
    exchange: str
    market: str
    symbol: str
    timeframe: str
    start: int | None = None
    end: int | None = None
    limit: int | None = None

    def load(self) -> tuple[OHLCVBar, ...]:
        rows = Exchange(
            name=self.exchange,
            market_type=MarketType(self.market),
        ).fetch_ohlcv(
            symbol=self.symbol,
            timeframe=self.timeframe,
            start=self.start,
            end=self.end,
            limit=self.limit,
        )
        return tuple(
            OHLCVBar(
                timestamp=row.timestamp,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close,
                volume=row.volume,
            )
            for row in rows
        )
