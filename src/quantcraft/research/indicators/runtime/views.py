from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Protocol


class RuntimeValues(Protocol):
    def values(self, output_index: int) -> Sequence[float]: ...


class IndicatorSeriesView:
    __slots__ = ("_runtime", "_output_index")

    def __init__(self, runtime: RuntimeValues, output_index: int) -> None:
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


__all__ = ["IndicatorSeriesView"]
