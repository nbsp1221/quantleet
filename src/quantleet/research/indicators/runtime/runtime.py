from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar

from quantleet.research.indicators.runtime.base import IndicatorKernel, IndicatorState, SeriesLike
from quantleet.research.indicators.runtime.views import IndicatorSeriesView

_KernelState = TypeVar("_KernelState", bound=IndicatorState)


@dataclass(frozen=True, slots=True)
class RebuildPlan:
    lengths: tuple[int, ...]
    sources: tuple[tuple[float, ...], ...]


@dataclass(frozen=True, slots=True)
class AppendPlan:
    lengths: tuple[int, ...]
    rows: tuple[tuple[float, ...], ...]


class SourceSynchronizer:
    __slots__ = ("_sources", "_lengths")

    def __init__(self, sources: tuple[SeriesLike, ...]) -> None:
        self._sources = sources
        self._lengths: tuple[int, ...] | None = None

    def plan(self) -> RebuildPlan | AppendPlan | None:
        current_lengths = tuple(len(source) for source in self._sources)
        if self._lengths is None:
            return RebuildPlan(
                lengths=current_lengths,
                sources=tuple(self._materialize_source(source) for source in self._sources),
            )
        if current_lengths == self._lengths:
            return None
        append_delta = self._append_delta(current_lengths)
        if append_delta is None:
            return RebuildPlan(
                lengths=current_lengths,
                sources=tuple(self._materialize_source(source) for source in self._sources),
            )
        appended = tuple(
            self._materialize_appended_values(source, append_delta) for source in self._sources
        )
        return AppendPlan(lengths=current_lengths, rows=tuple(zip(*appended)))

    def commit(self, lengths: tuple[int, ...]) -> None:
        self._lengths = lengths

    def reset(self) -> None:
        self._lengths = None

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
    def _materialize_source(series: SeriesLike) -> tuple[float, ...]:
        return tuple(series[index] for index in range(len(series) - 1, -1, -1))

    @staticmethod
    def _materialize_appended_values(series: SeriesLike, delta: int) -> tuple[float, ...]:
        if delta <= 0:
            return ()
        return tuple(series[index] for index in range(delta - 1, -1, -1))


class IndicatorRuntime(Generic[_KernelState]):
    __slots__ = ("_kernel", "_state", "_synchronizer")

    def __init__(
        self,
        *,
        sources: tuple[SeriesLike, ...],
        kernel: IndicatorKernel[_KernelState],
    ) -> None:
        self._kernel = kernel
        self._state: _KernelState | None = None
        self._synchronizer = SourceSynchronizer(sources)

    def view(self, output_index: int = 0) -> IndicatorSeriesView:
        return IndicatorSeriesView(self, output_index)

    @property
    def initialized(self) -> bool:
        return self._state is not None

    def reset(self) -> None:
        self._state = None
        self._synchronizer.reset()

    def values(self, output_index: int) -> Sequence[float]:
        self._sync()
        if self._state is None:
            return ()
        return self._state.outputs[output_index]

    def _sync(self) -> None:
        plan = self._synchronizer.plan()
        if plan is None:
            return
        if isinstance(plan, RebuildPlan):
            self._state = self._kernel.build(plan.sources)
            self._synchronizer.commit(plan.lengths)
            return
        if self._state is None:
            raise RuntimeError("append plan requires an initialized indicator state")
        for values in plan.rows:
            self._kernel.append(self._state, values)
        self._synchronizer.commit(plan.lengths)


__all__ = ["AppendPlan", "IndicatorRuntime", "RebuildPlan", "SourceSynchronizer"]
