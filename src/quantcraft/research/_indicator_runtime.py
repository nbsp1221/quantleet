from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar


class _SeriesLike(Protocol):
    def __getitem__(self, index: int) -> float: ...

    def __len__(self) -> int: ...

    @property
    def latest(self) -> float: ...

    @property
    def is_empty(self) -> bool: ...


class _IndicatorState(Protocol):
    @property
    def outputs(self) -> tuple[Sequence[float], ...]: ...


_KernelState = TypeVar("_KernelState", bound=_IndicatorState)


class _IndicatorKernel(Protocol[_KernelState]):
    def build(self, sources: tuple[tuple[float, ...], ...]) -> _KernelState: ...

    def append(self, state: _KernelState, values: tuple[float, ...]) -> None: ...


class _IndicatorSeriesView:
    __slots__ = ("_runtime", "_output_index")

    def __init__(self, runtime: _IndicatorRuntime[Any], output_index: int) -> None:
        self._runtime = runtime
        self._output_index = output_index

    def __getitem__(self, index: int) -> float:
        if index < 0:
            raise ValueError("computed series does not allow negative indices")
        values = self._runtime.values(self._output_index)
        if index >= len(values):
            return math.nan
        return values[-(index + 1)]

    def __len__(self) -> int:
        return len(self._runtime.values(self._output_index))

    @property
    def latest(self) -> float:
        return self[0]

    @property
    def is_empty(self) -> bool:
        return len(self) == 0


@dataclass(frozen=True, slots=True)
class _RebuildPlan:
    lengths: tuple[int, ...]
    sources: tuple[tuple[float, ...], ...]


@dataclass(frozen=True, slots=True)
class _AppendPlan:
    lengths: tuple[int, ...]
    rows: tuple[tuple[float, ...], ...]


class _SourceSynchronizer:
    __slots__ = ("_sources", "_lengths")

    def __init__(self, sources: tuple[_SeriesLike, ...]) -> None:
        self._sources = sources
        self._lengths: tuple[int, ...] | None = None

    def plan(self) -> _RebuildPlan | _AppendPlan | None:
        current_lengths = tuple(len(source) for source in self._sources)
        if self._lengths is None:
            return _RebuildPlan(
                lengths=current_lengths,
                sources=tuple(self._materialize_source(source) for source in self._sources),
            )
        if current_lengths == self._lengths:
            return None
        append_delta = self._append_delta(current_lengths)
        if append_delta is None:
            return _RebuildPlan(
                lengths=current_lengths,
                sources=tuple(self._materialize_source(source) for source in self._sources),
            )
        appended = tuple(
            self._materialize_appended_values(source, append_delta) for source in self._sources
        )
        return _AppendPlan(lengths=current_lengths, rows=tuple(zip(*appended)))

    def commit(self, lengths: tuple[int, ...]) -> None:
        self._lengths = lengths

    def _append_delta(self, current_lengths: tuple[int, ...]) -> int | None:
        if self._lengths is None:
            return None
        deltas = tuple(
            current - previous for previous, current in zip(self._lengths, current_lengths)
        )
        if any(delta < 0 for delta in deltas):
            return None
        delta_set = set(deltas)
        if delta_set == {0}:
            return 0
        if len(delta_set) != 1:
            return None
        return deltas[0]

    @staticmethod
    def _materialize_source(series: _SeriesLike) -> tuple[float, ...]:
        return tuple(series[index] for index in range(len(series) - 1, -1, -1))

    @staticmethod
    def _materialize_appended_values(series: _SeriesLike, delta: int) -> tuple[float, ...]:
        if delta <= 0:
            return ()
        return tuple(series[index] for index in range(delta - 1, -1, -1))


class _IndicatorRuntime(Generic[_KernelState]):
    __slots__ = ("_kernel", "_state", "_synchronizer")

    def __init__(
        self,
        *,
        sources: tuple[_SeriesLike, ...],
        kernel: _IndicatorKernel[_KernelState],
    ) -> None:
        self._kernel = kernel
        self._state: _KernelState | None = None
        self._synchronizer = _SourceSynchronizer(sources)

    def view(self, output_index: int = 0) -> _IndicatorSeriesView:
        return _IndicatorSeriesView(self, output_index)

    def values(self, output_index: int) -> Sequence[float]:
        self._sync()
        if self._state is None:
            return ()
        return self._state.outputs[output_index]

    def _sync(self) -> None:
        plan = self._synchronizer.plan()
        if plan is None:
            return
        if isinstance(plan, _RebuildPlan):
            self._state = self._kernel.build(plan.sources)
            self._synchronizer.commit(plan.lengths)
            return
        if self._state is None:
            raise RuntimeError("append plan requires an initialized indicator state")
        for values in plan.rows:
            self._kernel.append(self._state, values)
        self._synchronizer.commit(plan.lengths)
