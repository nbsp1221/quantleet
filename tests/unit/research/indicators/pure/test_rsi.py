from __future__ import annotations

import inspect

import numpy as np
import pytest

from quantcraft.research.indicators.pure.rsi import rsi


def test_rsi_matches_talib_signature_and_returns_ndarray() -> None:
    assert tuple(inspect.signature(rsi).parameters) == ("values", "length")

    result = rsi(np.asarray((1.0, 2.0, 3.0, 4.0), dtype=float), length=3)

    assert isinstance(result, np.ndarray)
    assert result == pytest.approx((float("nan"), float("nan"), float("nan"), 100.0), nan_ok=True)


def test_rsi_matches_talib_fixture_values() -> None:
    result = rsi(np.asarray((5.0, 4.0, 6.0, 3.0, 7.0, 2.0, 8.0), dtype=float), length=3)

    assert result == pytest.approx(
        (
            float("nan"),
            float("nan"),
            float("nan"),
            33.33333333333333,
            66.66666666666666,
            34.40860215053764,
            64.9425287356322,
        ),
        nan_ok=True,
    )


def test_rsi_returns_zero_for_flat_input_after_warmup() -> None:
    result = rsi(np.asarray((5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0), dtype=float), length=3)

    assert result == pytest.approx(
        (float("nan"), float("nan"), float("nan"), 0.0, 0.0, 0.0, 0.0),
        nan_ok=True,
    )


def test_rsi_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="length must be positive"):
        rsi(np.asarray((1.0, 2.0, 3.0), dtype=float), length=0)
