from __future__ import annotations

import math

import pytest

from quantcraft.research import qc
from quantcraft.research.series import OHLCVDataView, SeriesView


def test_series_view_uses_zero_as_current_confirmed_value() -> None:
    series = SeriesView((100.0, 105.0, 110.0))

    assert series[0] == 110.0
    assert series[1] == 105.0
    assert series[2] == 100.0


def test_series_view_rejects_negative_indexing() -> None:
    series = SeriesView((100.0, 105.0))

    with pytest.raises(ValueError, match="negative"):
        _ = series[-1]


def test_series_view_surfaces_missing_history_as_nan() -> None:
    series = SeriesView((100.0,))

    assert qc.is_na(series[1])
    assert qc.is_na(series[3])


def test_series_view_reports_latest_and_is_empty() -> None:
    empty = SeriesView(())
    series = SeriesView((100.0, 105.0))

    assert empty.is_empty is True
    assert qc.is_na(empty.latest)
    assert series.is_empty is False
    assert series.latest == 105.0


def test_len_series_view_is_current_visible_length() -> None:
    series = SeriesView((100.0, 105.0, 110.0))

    assert len(series) == 3


def test_series_view_does_not_expose_raw_backing_history_field() -> None:
    series = SeriesView((100.0, 105.0))

    assert not hasattr(series, "_values")


def test_ohlcv_data_view_exposes_only_series_views() -> None:
    data = OHLCVDataView(
        open=SeriesView((10.0,)),
        high=SeriesView((15.0,)),
        low=SeriesView((8.0,)),
        close=SeriesView((12.0,)),
        volume=SeriesView((100.0,)),
    )

    assert isinstance(data.open, SeriesView)
    assert isinstance(data.high, SeriesView)
    assert isinstance(data.low, SeriesView)
    assert isinstance(data.close, SeriesView)
    assert isinstance(data.volume, SeriesView)


def test_is_na_accepts_nan_and_rejects_regular_numbers() -> None:
    assert qc.is_na(math.nan) is True
    assert qc.is_na(1.0) is False
