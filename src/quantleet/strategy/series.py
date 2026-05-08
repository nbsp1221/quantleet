from __future__ import annotations

from dataclasses import dataclass
from math import nan


class _SeriesBuffer:
    __slots__ = ("values", "visible_length")

    def __init__(
        self,
        values: tuple[float, ...] = (),
        *,
        visible_length: int | None = None,
    ) -> None:
        self.values = list(values)
        if visible_length is None:
            self.visible_length = len(self.values)
            return
        if visible_length < 0 or visible_length > len(self.values):
            raise ValueError("visible_length must be between 0 and the backing length")
        self.visible_length = visible_length

    def append(self, value: float) -> None:
        self.values.append(value)
        self.visible_length += 1

    def set_visible_length(self, visible_length: int) -> None:
        if visible_length < 0 or visible_length > len(self.values):
            raise ValueError("visible_length must be between 0 and the backing length")
        self.visible_length = visible_length

    def advance(self, step: int = 1) -> None:
        self.set_visible_length(self.visible_length + step)


class SeriesView:
    __slots__ = ("__buffer",)

    def __init__(
        self,
        values: tuple[float, ...] | _SeriesBuffer,
        *,
        visible_length: int | None = None,
    ) -> None:
        if isinstance(values, _SeriesBuffer):
            self.__buffer = values
            if visible_length is not None:
                self.__buffer.set_visible_length(visible_length)
            return
        self.__buffer = _SeriesBuffer(values, visible_length=visible_length)

    def __getitem__(self, index: int) -> float:
        if index < 0:
            raise ValueError("SeriesView does not allow negative indices")
        if index >= self.__buffer.visible_length:
            return nan
        return self.__buffer.values[self.__buffer.visible_length - (index + 1)]

    def __len__(self) -> int:
        return self.__buffer.visible_length

    @property
    def latest(self) -> float:
        return self[0]

    @property
    def is_empty(self) -> bool:
        return self.__buffer.visible_length == 0

    def _append(self, value: float) -> None:
        self.__buffer.append(value)

    def _set_visible_length(self, visible_length: int) -> None:
        self.__buffer.set_visible_length(visible_length)

    def _advance(self, step: int = 1) -> None:
        self.__buffer.advance(step)

    def _all_values(self) -> tuple[float, ...]:
        return tuple(self.__buffer.values)


@dataclass(frozen=True, slots=True)
class OHLCVDataView:
    open: SeriesView
    high: SeriesView
    low: SeriesView
    close: SeriesView
    volume: SeriesView


__all__ = ["OHLCVDataView", "SeriesView"]
