from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from quantcraft.data import CSVDataSource, OHLCVBar


def _write_csv(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_csv_source_requires_minimal_schema(tmp_path: Path) -> None:
    csv_path = tmp_path / "bars.csv"
    _write_csv(
        csv_path,
        "timestamp,open,high,low\n"
        "2026-01-01T00:00:00+00:00,1,2,0.5\n",
    )

    source = CSVDataSource(
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
        "timestamp,open,high,low,close\n"
        "2026-01-01T00:00:00,1,2,0.5,1.5\n",
    )

    source = CSVDataSource(
        path=csv_path,
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    )

    with pytest.raises(ValueError, match="timezone-aware"):
        source.load()


def test_csv_source_normalizes_missing_volume_to_zero(tmp_path: Path) -> None:
    csv_path = tmp_path / "bars.csv"
    _write_csv(
        csv_path,
        "timestamp,open,high,low,close\n"
        "2026-01-01T00:00:00+09:00,1,2,0.5,1.5\n",
    )

    source = CSVDataSource(
        path=csv_path,
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    )

    bars = source.load()

    assert bars == (
        OHLCVBar(
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

    source = CSVDataSource(
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
        "timestamp,open,high,low,close\n"
        "2026-01-01T00:00:00+00:00,1,2,0.5,1.5\n",
    )

    with pytest.raises(ValueError, match="symbol must be non-empty"):
        CSVDataSource(
            path=csv_path,
            symbol="",
            timeframe="1h",
        )

    with pytest.raises(ValueError, match="timeframe must be non-empty"):
        CSVDataSource(
            path=csv_path,
            symbol="BTC/USDT:USDT",
            timeframe="",
        )
