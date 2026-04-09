from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, TypeVar


class SeriesLike(Protocol):
    def __getitem__(self, index: int) -> float: ...

    def __len__(self) -> int: ...

    @property
    def latest(self) -> float: ...

    @property
    def is_empty(self) -> bool: ...


class IndicatorState(Protocol):
    @property
    def outputs(self) -> tuple[Sequence[float], ...]: ...


_IndicatorStateT = TypeVar("_IndicatorStateT", bound=IndicatorState)


class IndicatorKernel(Protocol[_IndicatorStateT]):
    def build(self, sources: tuple[tuple[float, ...], ...]) -> _IndicatorStateT: ...

    def append(self, state: _IndicatorStateT, values: tuple[float, ...]) -> None: ...


__all__ = ["IndicatorKernel", "IndicatorState", "SeriesLike"]
