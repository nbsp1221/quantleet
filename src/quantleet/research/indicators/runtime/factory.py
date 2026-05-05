from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Callable, TypeVar, cast

import numpy as np

from quantleet.research.indicators.runtime.base import IndicatorKernel, IndicatorState, SeriesLike
from quantleet.research.indicators.runtime.runtime import IndicatorRuntime
from quantleet.research.indicators.runtime.views import IndicatorSeriesView
from quantleet.research.series import SeriesView

_KernelState = TypeVar("_KernelState", bound=IndicatorState)
_ResultT = TypeVar("_ResultT")
_PureResultT = TypeVar("_PureResultT")


@dataclass(slots=True)
class _PureFunctionState:
    outputs: tuple[list[float], ...]
    sources: tuple[list[float], ...]


class _PureFunctionKernel:
    __slots__ = ("_compute_outputs",)

    def __init__(
        self,
        compute_outputs: Callable[[tuple[tuple[float, ...], ...]], tuple[Any, ...]],
    ) -> None:
        self._compute_outputs = compute_outputs

    def build(self, sources: tuple[tuple[float, ...], ...]) -> _PureFunctionState:
        outputs = self._compute_outputs(sources)
        return _PureFunctionState(
            outputs=tuple(list(output) for output in outputs),
            sources=tuple(list(source) for source in sources),
        )

    def append(self, state: _PureFunctionState, values: tuple[float, ...]) -> None:
        for source, value in zip(state.sources, values):
            source.append(value)
        runtime_sources = tuple(tuple(source) for source in state.sources)
        outputs = self._compute_outputs(runtime_sources)
        latest_outputs = tuple(fresh_output[-1] for fresh_output in outputs)
        for cached_output, latest_output in zip(state.outputs, latest_outputs):
            cached_output.append(latest_output)


class _PrecomputedRuntime:
    """Optimization-only cache for static full-history SeriesView inputs."""

    __slots__ = ("_outputs", "_sources")

    def __init__(
        self,
        *,
        sources: tuple[SeriesView, ...],
        compute_outputs: Callable[[tuple[np.ndarray, ...]], tuple[Any, ...]],
    ) -> None:
        self._sources = sources
        self._outputs = compute_outputs(_full_source_values(sources))

    def view(self, output_index: int = 0) -> IndicatorSeriesView:
        return IndicatorSeriesView(self, output_index)

    def values(self, output_index: int) -> Sequence[float]:
        visible_length = min(len(source) for source in self._sources)
        return cast(Sequence[float], self._outputs[output_index][:visible_length])


def bind_indicator(
    *,
    sources: tuple[SeriesLike, ...],
    kernel: IndicatorKernel[_KernelState],
) -> IndicatorSeriesView:
    return IndicatorRuntime(sources=sources, kernel=kernel).view()


def bind_indicator_from_pure(
    *,
    sources: tuple[SeriesLike, ...],
    compute: Callable[..., Any],
) -> IndicatorSeriesView:
    precomputed = _bind_precomputed_indicator_if_possible(sources=sources, compute=compute)
    if precomputed is not None:
        return precomputed
    return bind_indicator(
        sources=sources,
        kernel=_PureFunctionKernel(
            compute_outputs=lambda runtime_sources: (compute(*runtime_sources),),
        ),
    )


def bind_multi_output_indicator(
    *,
    sources: tuple[SeriesLike, ...],
    kernel: IndicatorKernel[_KernelState],
    result_type: type[_ResultT],
    field_indices: dict[str, int],
) -> _ResultT:
    runtime = IndicatorRuntime(sources=sources, kernel=kernel)
    if not is_dataclass(result_type):
        raise TypeError("result_type must be a dataclass")
    kwargs = {
        field.name: runtime.view(field_indices[field.name])
        for field in fields(cast(Any, result_type))
    }
    return result_type(**kwargs)


def bind_multi_output_indicator_from_pure(
    *,
    sources: tuple[SeriesLike, ...],
    compute: Callable[..., _PureResultT],
    result_type: type[_ResultT],
    field_names: tuple[str, ...],
) -> _ResultT:
    precomputed = _bind_precomputed_multi_output_if_possible(
        sources=sources,
        compute=compute,
        result_type=result_type,
        field_names=field_names,
    )
    if precomputed is not None:
        return precomputed
    return bind_multi_output_indicator(
        sources=sources,
        kernel=_PureFunctionKernel(
            compute_outputs=lambda runtime_sources: tuple(
                getattr(compute(*runtime_sources), field_name) for field_name in field_names
            ),
        ),
        result_type=result_type,
        field_indices={field_name: index for index, field_name in enumerate(field_names)},
    )


def _bind_precomputed_indicator_if_possible(
    *,
    sources: tuple[SeriesLike, ...],
    compute: Callable[..., Any],
) -> IndicatorSeriesView | None:
    if not _all_series_views(sources):
        return None
    runtime = _PrecomputedRuntime(
        sources=cast(tuple[SeriesView, ...], sources),
        compute_outputs=lambda runtime_sources: (compute(*runtime_sources),),
    )
    return runtime.view()


def _bind_precomputed_multi_output_if_possible(
    *,
    sources: tuple[SeriesLike, ...],
    compute: Callable[..., _PureResultT],
    result_type: type[_ResultT],
    field_names: tuple[str, ...],
) -> _ResultT | None:
    if not _all_series_views(sources):
        return None
    runtime = _PrecomputedRuntime(
        sources=cast(tuple[SeriesView, ...], sources),
        compute_outputs=lambda runtime_sources: tuple(
            getattr(compute(*runtime_sources), field_name) for field_name in field_names
        ),
    )
    if not is_dataclass(result_type):
        raise TypeError("result_type must be a dataclass")
    kwargs = {
        field.name: runtime.view(index)
        for index, field in enumerate(fields(cast(Any, result_type)))
    }
    return result_type(**kwargs)


def _all_series_views(sources: tuple[SeriesLike, ...]) -> bool:
    return all(isinstance(source, SeriesView) for source in sources) and all(
        len(cast(SeriesView, source)._all_values()) > 0 for source in sources
    )


def _full_source_values(sources: tuple[SeriesLike, ...]) -> tuple[np.ndarray, ...]:
    return tuple(
        np.asarray(cast(SeriesView, source)._all_values(), dtype=float) for source in sources
    )


__all__ = [
    "bind_indicator",
    "bind_indicator_from_pure",
    "bind_multi_output_indicator",
    "bind_multi_output_indicator_from_pure",
]
