from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from quantcraft.data.adapters.dataframe_source import DataFrameDataSource
from quantcraft.data.bars import BarSeries
from quantcraft.data.sources import HistoricalDataSource


@dataclass(frozen=True, slots=True, kw_only=True)
class CSVDataSource(HistoricalDataSource):
    path: Path
    symbol: str
    timeframe: str

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol must be non-empty")
        if not self.timeframe:
            raise ValueError("timeframe must be non-empty")

    def load(self) -> BarSeries:
        with self.path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

        delegate = DataFrameDataSource(
            frame=rows,
            symbol=self.symbol,
            timeframe=self.timeframe,
        )
        return delegate.load()
