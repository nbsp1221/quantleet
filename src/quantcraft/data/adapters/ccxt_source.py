from __future__ import annotations

from dataclasses import dataclass

from quantcraft.data.bars import BarSeries, TimeBar
from quantcraft.data.sources import HistoricalDataSource
from quantcraft.integrations.venues.ccxt.market_data import MarketType, _fetch_ohlcv_range


@dataclass(frozen=True, slots=True, kw_only=True)
class CCXTDataSource(HistoricalDataSource):
    exchange: str
    market: str
    symbol: str
    timeframe: str
    start: int | None = None
    end: int | None = None
    limit: int | None = None

    def load(self) -> BarSeries:
        rows = _fetch_ohlcv_range(
            name=self.exchange,
            market_type=MarketType(self.market),
            symbol=self.symbol,
            timeframe=self.timeframe,
            start=self.start,
            end=self.end,
            limit=self.limit,
        )
        return BarSeries(
            symbol=self.symbol,
            timeframe=self.timeframe,
            bar_type="time",
            rows=tuple(
                TimeBar(
                    timestamp=row.timestamp,
                    open=row.open,
                    high=row.high,
                    low=row.low,
                    close=row.close,
                    volume=row.volume,
                )
                for row in rows
            ),
        )
