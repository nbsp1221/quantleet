from __future__ import annotations

import math
from dataclasses import dataclass

import pytest

from quantcraft.research.indicators.runtime.views import IndicatorSeriesView


@dataclass
class RuntimeStub:
    outputs: tuple[tuple[float, ...], ...]

    def values(self, output_index: int) -> tuple[float, ...]:
        return self.outputs[output_index]


def test_view_exposes_latest_history_and_length() -> None:
    runtime = RuntimeStub(outputs=((1.0, 2.0, 3.0),))
    view = IndicatorSeriesView(runtime, output_index=0)

    assert view[0] == 3.0
    assert view[1] == 2.0
    assert view[2] == 1.0
    assert len(view) == 3
    assert view.latest == 3.0
    assert view.is_empty is False


def test_view_returns_nan_for_missing_history() -> None:
    runtime = RuntimeStub(outputs=((1.0, 2.0),))
    view = IndicatorSeriesView(runtime, output_index=0)

    assert math.isnan(view[2])


def test_view_rejects_negative_indices() -> None:
    runtime = RuntimeStub(outputs=((1.0,),))
    view = IndicatorSeriesView(runtime, output_index=0)

    with pytest.raises(ValueError, match="negative indices"):
        _ = view[-1]


def test_view_reports_empty_state() -> None:
    runtime = RuntimeStub(outputs=((),))
    view = IndicatorSeriesView(runtime, output_index=0)

    assert len(view) == 0
    assert view.is_empty is True
    assert math.isnan(view.latest)
