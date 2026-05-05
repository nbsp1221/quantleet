from __future__ import annotations

import math
from typing import Protocol


class _SeriesLike(Protocol):
    def __getitem__(self, index: int) -> float: ...

    def __len__(self) -> int: ...


def is_na(value: float) -> bool:
    return math.isnan(value)


def crossover(left: _SeriesLike | float, right: _SeriesLike | float) -> bool:
    current_left, previous_left = _current_and_previous(left)
    current_right, previous_right = _current_and_previous(right)
    if any(is_na(value) for value in (current_left, previous_left, current_right, previous_right)):
        return False
    return current_left > current_right and previous_left <= previous_right


def crossunder(left: _SeriesLike | float, right: _SeriesLike | float) -> bool:
    current_left, previous_left = _current_and_previous(left)
    current_right, previous_right = _current_and_previous(right)
    if any(is_na(value) for value in (current_left, previous_left, current_right, previous_right)):
        return False
    return current_left < current_right and previous_left >= previous_right


def _current_and_previous(value: _SeriesLike | float) -> tuple[float, float]:
    if hasattr(value, "__getitem__") and hasattr(value, "__len__"):
        series = value
        return float(series[0]), float(series[1])
    scalar = float(value)
    return scalar, scalar


__all__ = ["crossover", "crossunder", "is_na"]
