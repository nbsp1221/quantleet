from __future__ import annotations

from typing import Final

import numpy as np
import talib

_DEFAULT_LENGTH: Final[int] = 20


def cci(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    length: int = _DEFAULT_LENGTH,
) -> np.ndarray:
    _validate_length(length)
    return talib.CCI(
        np.asarray(high, dtype=float),
        np.asarray(low, dtype=float),
        np.asarray(close, dtype=float),
        timeperiod=length,
    )


def _validate_length(length: int) -> None:
    if length <= 0:
        raise ValueError("length must be positive")
