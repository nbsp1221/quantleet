# Data Sources

The first beta works with normalized historical OHLCV data.

## In-Memory Data

```python
from quantcraft.data import DataFrameDataSource

source = DataFrameDataSource(
    frame=[
        {"timestamp": "1970-01-01T00:01:00+00:00", "open": 10.0, "high": 12.0, "low": 8.0, "close": 10.0, "volume": 1.0},
    ],
    symbol="BTC/USDT",
    timeframe="1m",
)
```

## Materialized Series

```python
from quantcraft.data import BarSeries, TimeBar

bars = BarSeries(
    symbol="BTC/USDT",
    timeframe="1m",
    bar_type="time",
    rows=(
        TimeBar(timestamp=60_000, open=10.0, high=12.0, low=8.0, close=10.0, volume=1.0),
    ),
)
```

## Built-In Sources

- `DataFrameDataSource` for dataframe-like records.
- `CSVDataSource` for local CSV-backed historical data.
- `CCXTDataSource` for exchange-backed historical OHLCV loading.

The quickstart does not require live exchange credentials.
