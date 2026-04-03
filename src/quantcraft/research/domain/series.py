from __future__ import annotations

from dataclasses import dataclass
from math import nan


class _SeriesBuffer:
    __slots__ = ("values",)

    def __init__(self, values: tuple[float, ...] = ()) -> None:
        self.values = list(values)

    def append(self, value: float) -> None:
        self.values.append(value)


class SeriesView:
    __slots__ = ("__buffer",)

    def __init__(self, values: tuple[float, ...] | _SeriesBuffer) -> None:
        if isinstance(values, _SeriesBuffer):
            self.__buffer = values
            return
        self.__buffer = _SeriesBuffer(values)

    def __getitem__(self, index: int) -> float:
        if index < 0:
            raise ValueError("SeriesView does not allow negative indices")
        if index >= len(self.__buffer.values):
            return nan
        return self.__buffer.values[-(index + 1)]

    def __len__(self) -> int:
        return len(self.__buffer.values)

    @property
    def latest(self) -> float:
        return self[0]

    @property
    def is_empty(self) -> bool:
        return len(self.__buffer.values) == 0

    def _append(self, value: float) -> None:
        self.__buffer.append(value)


@dataclass(frozen=True, slots=True)
class OHLCVDataView:
    open: SeriesView
    high: SeriesView
    low: SeriesView
    close: SeriesView
    volume: SeriesView
