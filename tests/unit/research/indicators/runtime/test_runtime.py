from __future__ import annotations

from dataclasses import dataclass

from quantleet.research.indicators.runtime.runtime import IndicatorRuntime


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

    def replace(self, values: tuple[float, ...]) -> None:
        self._values = values


@dataclass
class RecordingState:
    outputs: tuple[list[float], ...]


class RecordingKernel:
    def __init__(self) -> None:
        self.build_inputs: list[tuple[tuple[float, ...], ...]] = []
        self.append_inputs: list[tuple[float, ...]] = []

    def build(self, sources: tuple[tuple[float, ...], ...]) -> RecordingState:
        self.build_inputs.append(sources)
        values = list(sources[0])
        return RecordingState(outputs=(values,))

    def append(self, state: RecordingState, values: tuple[float, ...]) -> None:
        self.append_inputs.append(values)
        state.outputs[0].append(values[0])


class DualOutputKernel:
    def __init__(self) -> None:
        self.build_calls = 0

    def build(self, sources: tuple[tuple[float, ...], ...]) -> RecordingState:
        self.build_calls += 1
        values = list(sources[0])
        doubled = [value * 2.0 for value in values]
        return RecordingState(outputs=(values, doubled))

    def append(self, state: RecordingState, values: tuple[float, ...]) -> None:
        state.outputs[0].append(values[0])
        state.outputs[1].append(values[0] * 2.0)


class MultiSourceKernel:
    def __init__(self) -> None:
        self.build_inputs: list[tuple[tuple[float, ...], ...]] = []
        self.append_inputs: list[tuple[float, ...]] = []

    def build(self, sources: tuple[tuple[float, ...], ...]) -> RecordingState:
        self.build_inputs.append(sources)
        values = [left + right for left, right in zip(*sources)]
        return RecordingState(outputs=(values,))

    def append(self, state: RecordingState, values: tuple[float, ...]) -> None:
        self.append_inputs.append(values)
        left, right = values
        state.outputs[0].append(left + right)


def test_runtime_uses_append_path_for_monotonic_growth() -> None:
    series = MutableSeries((1.0, 2.0, 3.0))
    kernel = RecordingKernel()
    runtime = IndicatorRuntime(sources=(series,), kernel=kernel)
    view = runtime.view()

    assert view[0] == 3.0
    assert kernel.build_inputs == [((1.0, 2.0, 3.0),)]

    series.append(4.0)

    assert view[0] == 4.0
    assert kernel.build_inputs == [((1.0, 2.0, 3.0),)]
    assert kernel.append_inputs == [(4.0,)]


def test_runtime_rebuilds_when_source_shape_is_not_append_only() -> None:
    series = MutableSeries((1.0, 2.0, 3.0))
    kernel = RecordingKernel()
    runtime = IndicatorRuntime(sources=(series,), kernel=kernel)
    view = runtime.view()

    assert view[0] == 3.0

    series.replace((10.0, 20.0))

    assert view[0] == 20.0
    assert kernel.build_inputs == [
        ((1.0, 2.0, 3.0),),
        ((10.0, 20.0),),
    ]
    assert kernel.append_inputs == []


def test_runtime_shares_cache_across_multiple_output_views() -> None:
    series = MutableSeries((1.0, 2.0, 3.0))
    kernel = DualOutputKernel()
    runtime = IndicatorRuntime(sources=(series,), kernel=kernel)
    primary = runtime.view(0)
    secondary = runtime.view(1)

    assert primary[0] == 3.0
    assert secondary[0] == 6.0
    assert kernel.build_calls == 1


def test_runtime_uses_append_path_for_multi_source_growth() -> None:
    left = MutableSeries((1.0, 2.0, 3.0))
    right = MutableSeries((10.0, 20.0, 30.0))
    kernel = MultiSourceKernel()
    runtime = IndicatorRuntime(sources=(left, right), kernel=kernel)
    view = runtime.view()

    assert view[0] == 33.0

    left.append(4.0)
    right.append(40.0)

    assert view[0] == 44.0
    assert kernel.build_inputs == [((1.0, 2.0, 3.0), (10.0, 20.0, 30.0))]
    assert kernel.append_inputs == [(4.0, 40.0)]


def test_runtime_rebuilds_when_multi_source_growth_is_misaligned() -> None:
    left = MutableSeries((1.0, 2.0, 3.0))
    right = MutableSeries((10.0, 20.0, 30.0))
    kernel = MultiSourceKernel()
    runtime = IndicatorRuntime(sources=(left, right), kernel=kernel)
    view = runtime.view()

    assert view[0] == 33.0

    left.append(4.0)

    assert view[0] == 33.0
    assert kernel.build_inputs == [
        ((1.0, 2.0, 3.0), (10.0, 20.0, 30.0)),
        ((1.0, 2.0, 3.0, 4.0), (10.0, 20.0, 30.0)),
    ]
    assert kernel.append_inputs == []


def test_runtime_reports_initialization_state_and_can_reset() -> None:
    series = MutableSeries((1.0, 2.0, 3.0))
    kernel = RecordingKernel()
    runtime = IndicatorRuntime(sources=(series,), kernel=kernel)
    view = runtime.view()

    assert runtime.initialized is False

    assert view[0] == 3.0
    assert runtime.initialized is True

    series.append(4.0)
    runtime.reset()

    assert runtime.initialized is False
    assert view[0] == 4.0
    assert runtime.initialized is True
    assert kernel.build_inputs == [
        ((1.0, 2.0, 3.0),),
        ((1.0, 2.0, 3.0, 4.0),),
    ]
