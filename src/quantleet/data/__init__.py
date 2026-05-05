from __future__ import annotations

from quantleet.data.bars import BarSeries, TimeBar
from quantleet.data.sources import HistoricalDataSource

__all__ = [
    "BarSeries",
    "CCXTDataSource",
    "CSVDataSource",
    "DataFrameDataSource",
    "HistoricalDataSource",
    "TimeBar",
]


def __getattr__(name: str) -> object:
    if name in {"BarSeries", "HistoricalDataSource", "TimeBar"}:
        return globals()[name]

    if name == "CCXTDataSource":
        from quantleet.data.adapters.ccxt_source import CCXTDataSource

        return CCXTDataSource

    if name == "CSVDataSource":
        from quantleet.data.adapters.csv_source import CSVDataSource

        return CSVDataSource

    if name == "DataFrameDataSource":
        from quantleet.data.adapters.dataframe_source import DataFrameDataSource

        return DataFrameDataSource

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
