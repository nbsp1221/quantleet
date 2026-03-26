from __future__ import annotations

from datetime import UTC, datetime

import pytest

from quantcraft.data import DataFrameDataSource, OHLCVBar


class FakeDataFrame:
    def __init__(self, records: list[dict[str, object]]) -> None:
        self._records = records

    def to_dict(self, orient: str) -> list[dict[str, object]]:
        if orient != "records":
            raise ValueError(f"unexpected orient: {orient}")
        return self._records


def test_dataframe_source_requires_minimal_schema() -> None:
    source = DataFrameDataSource(
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
    source = DataFrameDataSource(
        frame=FakeDataFrame(
            [
                {
                    "timestamp": datetime(2026, 1, 1, 0, 0),
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


def test_dataframe_source_normalizes_missing_volume_to_zero() -> None:
    source = DataFrameDataSource(
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

    assert bars == (
        OHLCVBar(
            timestamp=int(datetime(2026, 1, 1, 0, 0, tzinfo=UTC).timestamp() * 1000),
            open=1.0,
            high=2.0,
            low=0.5,
            close=1.5,
            volume=0.0,
        ),
    )


def test_dataframe_source_rejects_metadata_columns_from_input() -> None:
    source = DataFrameDataSource(
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


def test_dataframe_source_rejects_empty_constructor_metadata() -> None:
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
        DataFrameDataSource(
            frame=frame,
            symbol="",
            timeframe="1h",
        )

    with pytest.raises(ValueError, match="timeframe must be non-empty"):
        DataFrameDataSource(
            frame=frame,
            symbol="BTC/USDT:USDT",
            timeframe="",
        )
