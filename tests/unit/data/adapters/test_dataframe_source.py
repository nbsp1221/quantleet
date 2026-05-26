from __future__ import annotations

import importlib
from datetime import UTC, datetime

import pytest


class FakeDataFrame:
    def __init__(self, records: list[dict[str, object]]) -> None:
        self._records = records

    def to_dict(self, orient: str) -> list[dict[str, object]]:
        if orient != "records":
            raise ValueError(f"unexpected orient: {orient}")
        return self._records


def _dataframe_source_type() -> type:
    data_module = importlib.import_module("quantleet.data")
    return data_module.DataFrameDataSource


def _time_bar_type() -> type:
    data_module = importlib.import_module("quantleet.data")
    return data_module.TimeBar


def _bar_series_type() -> type:
    data_module = importlib.import_module("quantleet.data")
    return data_module.BarSeries


def test_dataframe_source_requires_minimal_schema() -> None:
    source = _dataframe_source_type()(
        frame=FakeDataFrame(
            [
                {
                    "timestamp": "2026-01-01T00:00:00+00:00",
                    "open": 1.0,
                    "high": 2.0,
                    "low": 0.5,
                }
            ]
        ),
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    )

    with pytest.raises(ValueError, match="missing required columns"):
        source.load()


def test_dataframe_source_rejects_naive_timestamps() -> None:
    source = _dataframe_source_type()(
        frame=FakeDataFrame(
            [
                {
                    "timestamp": datetime(2026, 1, 1, 0, 0),  # noqa: DTZ001
                    "open": 1.0,
                    "high": 2.0,
                    "low": 0.5,
                    "close": 1.5,
                }
            ]
        ),
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    )

    with pytest.raises(ValueError, match="timezone-aware"):
        source.load()


def test_dataframe_source_rejects_unparseable_timestamp_strings() -> None:
    source = _dataframe_source_type()(
        frame=FakeDataFrame(
            [
                {
                    "timestamp": "not-a-timestamp",
                    "open": 1.0,
                    "high": 2.0,
                    "low": 0.5,
                    "close": 1.5,
                }
            ]
        ),
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    )

    with pytest.raises(ValueError, match="explicitly parseable"):
        source.load()


def test_dataframe_source_rejects_non_datetime_non_string_timestamps() -> None:
    source = _dataframe_source_type()(
        frame=FakeDataFrame(
            [
                {
                    "timestamp": 123,
                    "open": 1.0,
                    "high": 2.0,
                    "low": 0.5,
                    "close": 1.5,
                }
            ]
        ),
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    )

    with pytest.raises(ValueError, match="timezone-aware or explicitly parseable"):
        source.load()


def test_dataframe_source_materializes_bar_series_with_time_bar_rows() -> None:
    source = _dataframe_source_type()(
        frame=FakeDataFrame(
            [
                {
                    "timestamp": datetime(2026, 1, 1, 0, 0, tzinfo=UTC),
                    "open": "1.0",
                    "high": "2.0",
                    "low": "0.5",
                    "close": "1.5",
                }
            ]
        ),
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    )

    bars = source.load()
    bar_series_type = _bar_series_type()
    time_bar_type = _time_bar_type()

    assert isinstance(bars, bar_series_type)
    assert bars.symbol == "BTC/USDT:USDT"
    assert bars.timeframe == "1h"
    assert bars.bar_type == "time"
    assert bars.rows == (
        time_bar_type(
            timestamp=int(datetime(2026, 1, 1, 0, 0, tzinfo=UTC).timestamp() * 1000),
            open=1.0,
            high=2.0,
            low=0.5,
            close=1.5,
            volume=0.0,
        ),
    )


def test_dataframe_source_rejects_metadata_columns_from_input() -> None:
    source = _dataframe_source_type()(
        frame=FakeDataFrame(
            [
                {
                    "timestamp": datetime(2026, 1, 1, 0, 0, tzinfo=UTC),
                    "open": 1.0,
                    "high": 2.0,
                    "low": 0.5,
                    "close": 1.5,
                    "timeframe": "1h",
                }
            ]
        ),
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    )

    with pytest.raises(ValueError, match="symbol/timeframe columns are not allowed"):
        source.load()


def test_dataframe_source_rejects_non_numeric_price_fields() -> None:
    source = _dataframe_source_type()(
        frame=FakeDataFrame(
            [
                {
                    "timestamp": datetime(2026, 1, 1, 0, 0, tzinfo=UTC),
                    "open": "bad-number",
                    "high": 2.0,
                    "low": 0.5,
                    "close": 1.5,
                }
            ]
        ),
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    )

    with pytest.raises(ValueError, match="open must be numeric"):
        source.load()


def test_dataframe_source_rejects_empty_constructor_metadata() -> None:
    dataframe_source_type = _dataframe_source_type()
    frame = FakeDataFrame(
        [
            {
                "timestamp": datetime(2026, 1, 1, 0, 0, tzinfo=UTC),
                "open": 1.0,
                "high": 2.0,
                "low": 0.5,
                "close": 1.5,
            }
        ]
    )

    with pytest.raises(ValueError, match="symbol must be non-empty"):
        dataframe_source_type(
            frame=frame,
            symbol="",
            timeframe="1h",
        )

    with pytest.raises(ValueError, match="timeframe must be non-empty"):
        dataframe_source_type(
            frame=frame,
            symbol="BTC/USDT:USDT",
            timeframe="",
        )
