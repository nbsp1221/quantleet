from __future__ import annotations

import importlib
from datetime import UTC, datetime
from pathlib import Path

import pytest


def _write_csv(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _csv_source_type() -> type:
    data_module = importlib.import_module("quantleet.data")
    return getattr(data_module, "CSVDataSource")


def _time_bar_type() -> type:
    data_module = importlib.import_module("quantleet.data")
    return getattr(data_module, "TimeBar")


def _bar_series_type() -> type:
    data_module = importlib.import_module("quantleet.data")
    return getattr(data_module, "BarSeries")


def test_csv_source_requires_minimal_schema(tmp_path: Path) -> None:
    csv_path = tmp_path / "bars.csv"
    _write_csv(
        csv_path,
        "timestamp,open,high,low\n2026-01-01T00:00:00+00:00,1,2,0.5\n",
    )

    source = _csv_source_type()(
        path=csv_path,
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    )

    with pytest.raises(ValueError, match="missing required columns"):
        source.load()


def test_csv_source_rejects_naive_timestamps(tmp_path: Path) -> None:
    csv_path = tmp_path / "bars.csv"
    _write_csv(
        csv_path,
        "timestamp,open,high,low,close\n2026-01-01T00:00:00,1,2,0.5,1.5\n",
    )

    source = _csv_source_type()(
        path=csv_path,
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    )

    with pytest.raises(ValueError, match="timezone-aware"):
        source.load()


def test_csv_source_materializes_bar_series_with_time_bar_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "bars.csv"
    _write_csv(
        csv_path,
        "timestamp,open,high,low,close\n2026-01-01T00:00:00+09:00,1,2,0.5,1.5\n",
    )

    source = _csv_source_type()(
        path=csv_path,
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
            timestamp=int(datetime(2025, 12, 31, 15, 0, tzinfo=UTC).timestamp() * 1000),
            open=1.0,
            high=2.0,
            low=0.5,
            close=1.5,
            volume=0.0,
        ),
    )


def test_csv_source_rejects_symbol_column_from_input(tmp_path: Path) -> None:
    csv_path = tmp_path / "bars.csv"
    _write_csv(
        csv_path,
        "timestamp,open,high,low,close,symbol\n"
        "2026-01-01T00:00:00+00:00,1,2,0.5,1.5,BTC/USDT:USDT\n",
    )

    source = _csv_source_type()(
        path=csv_path,
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    )

    with pytest.raises(ValueError, match="symbol/timeframe columns are not allowed"):
        source.load()


def test_csv_source_rejects_empty_constructor_metadata(tmp_path: Path) -> None:
    csv_path = tmp_path / "bars.csv"
    _write_csv(
        csv_path,
        "timestamp,open,high,low,close\n2026-01-01T00:00:00+00:00,1,2,0.5,1.5\n",
    )

    csv_source_type = _csv_source_type()

    with pytest.raises(ValueError, match="symbol must be non-empty"):
        csv_source_type(
            path=csv_path,
            symbol="",
            timeframe="1h",
        )

    with pytest.raises(ValueError, match="timeframe must be non-empty"):
        csv_source_type(
            path=csv_path,
            symbol="BTC/USDT:USDT",
            timeframe="",
        )
