from __future__ import annotations


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
