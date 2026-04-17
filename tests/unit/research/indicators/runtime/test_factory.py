from __future__ import annotations

from dataclasses import dataclass

from quantcraft.research.indicators.runtime.factory import (
    bind_indicator,
    bind_indicator_from_pure,
    bind_multi_output_indicator,
    bind_multi_output_indicator_from_pure,
)
from quantcraft.research.series import SeriesView


class MutableSeries:
    def __init__(self, values: tuple[float, ...]) -> None:
        self._values = values

    def __getitem__(self, index: int) -> float:
        if index < 0:
            raise ValueError("negative indices are not supported")
        if index >= len(self._values):
            from math import nan

            return nan
        return self._values[-(index + 1)]

    def __len__(self) -> int:
        return len(self._values)

    @property
    def latest(self) -> float:
        return self[0]

    @property
    def is_empty(self) -> bool:
        return not self._values

    def append(self, value: float) -> None:
        self._values = self._values + (value,)


@dataclass
class EchoState:
    outputs: tuple[list[float], ...]


class EchoKernel:
    def build(self, sources: tuple[tuple[float, ...], ...]) -> EchoState:
        values = list(sources[0])
        return EchoState(outputs=(values, [value * 10.0 for value in values]))

    def append(self, state: EchoState, values: tuple[float, ...]) -> None:
        state.outputs[0].append(values[0])
        state.outputs[1].append(values[0] * 10.0)


def test_factory_binds_single_output_indicator_view() -> None:
    series = MutableSeries((1.0, 2.0, 3.0))

    view = bind_indicator(sources=(series,), kernel=EchoKernel())

    assert view[0] == 3.0
    series.append(4.0)
    assert view[0] == 4.0


def test_factory_binds_named_multi_output_indicator_views() -> None:
    series = MutableSeries((1.0, 2.0, 3.0))

    result = bind_multi_output_indicator(
        sources=(series,),
        kernel=EchoKernel(),
        result_type=PairResult,
        field_indices={"primary": 0, "secondary": 1},
    )

    assert isinstance(result, PairResult)
    assert result.primary[0] == 3.0
    assert result.secondary[0] == 30.0


def test_factory_binds_single_output_indicator_from_pure_function() -> None:
    series = MutableSeries((1.0, 2.0, 3.0))

    view = bind_indicator_from_pure(
        sources=(series,),
        compute=lambda values: tuple(value * 2.0 for value in values),
    )

    assert view[0] == 6.0
    series.append(4.0)
    assert view[0] == 8.0


def test_factory_binds_multi_output_indicator_from_pure_function() -> None:
    series = MutableSeries((1.0, 2.0, 3.0))

    result = bind_multi_output_indicator_from_pure(
        sources=(series,),
        compute=lambda values: PurePair(
            primary=tuple(values),
            secondary=tuple(value * 10.0 for value in values),
        ),
        result_type=PairResult,
        field_names=("primary", "secondary"),
    )

    assert isinstance(result, PairResult)
    assert result.primary[0] == 3.0
    assert result.secondary[0] == 30.0


def test_factory_precomputed_binding_uses_visible_prefix_of_full_history() -> None:
    series = SeriesView((1.0, 2.0, 3.0, 4.0), visible_length=3)

    view = bind_indicator_from_pure(
        sources=(series,),
        compute=lambda values: tuple(value * 2.0 for value in values),
    )

    assert view[0] == 6.0

    series._advance()

    assert view[0] == 8.0


@dataclass(frozen=True, slots=True)
class PairResult:
    primary: object
    secondary: object


@dataclass(frozen=True, slots=True)
class PurePair:
    primary: tuple[float, ...]
    secondary: tuple[float, ...]
