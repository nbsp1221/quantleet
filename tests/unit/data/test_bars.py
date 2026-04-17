from __future__ import annotations

from dataclasses import FrozenInstanceError, is_dataclass
from typing import get_type_hints

import pytest

from quantcraft.data.bars import BarSeries, TimeBar
from quantcraft.data.sources import HistoricalDataSource


def _time_bar_kwargs() -> dict[str, float | int]:
    return {
        "timestamp": 1_700_000_000_000,
        "open": 1.0,
        "high": 2.0,
        "low": 0.5,
        "close": 1.5,
        "volume": 10.0,
    }


def _time_bar_instance() -> TimeBar:
    return TimeBar(**_time_bar_kwargs())


def test_public_data_surface_and_root_owner_share_bar_contract_types() -> None:
    from quantcraft.data import BarSeries as PublicBarSeries
    from quantcraft.data import TimeBar as PublicTimeBar

    assert PublicTimeBar is TimeBar
    assert PublicBarSeries is BarSeries


def test_time_bar_is_a_frozen_dataclass_with_ohlcv_fields() -> None:
    bar = _time_bar_instance()

    assert is_dataclass(bar)
    assert bar.close == 1.5
    assert bar.volume == 10.0

    with pytest.raises(FrozenInstanceError):
        bar.close = 2.0  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field_overrides", "match"),
    [
        ({"timestamp": True}, "invalid time bar"),
        ({"open": float("inf")}, "invalid time bar"),
        ({"volume": -1.0}, "invalid time bar"),
        ({"high": 0.25}, "invalid time bar"),
        ({"low": 3.0}, "invalid time bar"),
    ],
)
def test_time_bar_rejects_invalid_rows(
    field_overrides: dict[str, float | int | bool],
    match: str,
) -> None:
    kwargs: dict[str, float | int] = _time_bar_kwargs()
    kwargs.update(field_overrides)

    with pytest.raises(ValueError, match=match):
        TimeBar(**kwargs)


def test_bar_series_is_a_frozen_dataclass_for_time_bars() -> None:
    bars = (_time_bar_instance(),)

    series = BarSeries(
        symbol="BTC/USDT",
        timeframe="1m",
        bar_type="time",
        rows=bars,
    )

    assert is_dataclass(series)
    assert series.symbol == "BTC/USDT"
    assert series.timeframe == "1m"
    assert series.bar_type == "time"
    assert series.rows == bars

    with pytest.raises(FrozenInstanceError):
        series.symbol = "ETH/USDT"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field_overrides", "match"),
    [
        ({"symbol": ""}, "invalid bar series metadata"),
        ({"timeframe": ""}, "invalid bar series metadata"),
        ({"bar_type": "tick"}, "bar_type must be 'time'"),
    ],
)
def test_bar_series_rejects_invalid_metadata(
    field_overrides: dict[str, object],
    match: str,
) -> None:
    kwargs: dict[str, object] = {
        "symbol": "BTC/USDT",
        "timeframe": "1m",
        "bar_type": "time",
        "rows": (_time_bar_instance(),),
    }
    kwargs.update(field_overrides)

    with pytest.raises(ValueError, match=match):
        BarSeries(**kwargs)


def test_bar_series_requires_a_tuple_of_time_bars() -> None:
    time_bar = _time_bar_instance()

    with pytest.raises(ValueError, match="rows must be a tuple of TimeBar"):
        BarSeries(
            symbol="BTC/USDT",
            timeframe="1m",
            bar_type="time",
            rows=[time_bar],
        )

    with pytest.raises(ValueError, match="rows must be a tuple of TimeBar"):
        BarSeries(
            symbol="BTC/USDT",
            timeframe="1m",
            bar_type="time",
            rows=(time_bar, object()),
        )


def test_historical_data_source_contract_loads_bar_series() -> None:
    annotations = get_type_hints(HistoricalDataSource.load)
    assert annotations["return"] == BarSeries
