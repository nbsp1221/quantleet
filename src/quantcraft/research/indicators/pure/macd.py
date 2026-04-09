from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Generic, TypeVar

import numpy as np
import talib

_DEFAULT_FAST: Final[int] = 12
_DEFAULT_SLOW: Final[int] = 26
_DEFAULT_SIGNAL: Final[int] = 9
_SeriesT = TypeVar("_SeriesT")


@dataclass(frozen=True, slots=True)
class PureMACDResult(Generic[_SeriesT]):
    macd: _SeriesT
    signal: _SeriesT
    histogram: _SeriesT


def macd(
    values: np.ndarray,
    fast: int = _DEFAULT_FAST,
    slow: int = _DEFAULT_SLOW,
    signal: int = _DEFAULT_SIGNAL,
) -> PureMACDResult[np.ndarray]:
    _validate_period(fast, name="fast")
    _validate_period(slow, name="slow")
    _validate_period(signal, name="signal")
    macd_values, signal_values, histogram_values = talib.MACD(
        np.asarray(values, dtype=float),
        fastperiod=fast,
        slowperiod=slow,
        signalperiod=signal,
    )
    return PureMACDResult(
        macd=macd_values,
        signal=signal_values,
        histogram=histogram_values,
    )


def _validate_period(length: int, *, name: str) -> None:
    if length <= 0:
        raise ValueError(f"{name} must be positive")
