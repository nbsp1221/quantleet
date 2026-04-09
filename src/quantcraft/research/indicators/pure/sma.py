from __future__ import annotations

from typing import Final

import numpy as np
import talib

_DEFAULT_LENGTH: Final[int] = 20


def sma(values: np.ndarray, length: int = _DEFAULT_LENGTH) -> np.ndarray:
    _validate_length(length)
    return talib.SMA(_to_array(values), timeperiod=length)


def _to_array(values: np.ndarray) -> np.ndarray:
    return np.asarray(values, dtype=float)


def _validate_length(length: int) -> None:
    if length <= 0:
        raise ValueError("length must be positive")
