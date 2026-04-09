from __future__ import annotations

import inspect

import numpy as np
import pytest

from quantcraft.research.indicators.pure.atr import atr


def test_atr_matches_talib_signature_and_returns_ndarray() -> None:
    assert tuple(inspect.signature(atr).parameters) == ("high", "low", "close", "length")

    result = atr(
        np.asarray((2.0, 3.0, 4.0, 5.0), dtype=float),
        np.asarray((0.5, 1.0, 2.0, 3.0), dtype=float),
        np.asarray((1.0, 2.0, 3.0, 4.0), dtype=float),
        length=3,
    )

    assert isinstance(result, np.ndarray)
    assert result == pytest.approx((float("nan"), float("nan"), float("nan"), 2.0), nan_ok=True)


def test_atr_matches_talib_fixture_values() -> None:
    result = atr(
        np.asarray((6.0, 5.0, 7.0, 4.0, 8.0, 3.0, 9.0), dtype=float),
        np.asarray((3.5, 2.5, 4.5, 1.5, 5.5, 0.5, 6.5), dtype=float),
        np.asarray((5.0, 4.0, 6.0, 3.0, 7.0, 2.0, 8.0), dtype=float),
        length=3,
    )

    assert result == pytest.approx(
        (
            float("nan"),
            float("nan"),
            float("nan"),
            3.3333333333333335,
            3.8888888888888893,
            4.7592592592592595,
            5.506172839506173,
        ),
        nan_ok=True,
    )


def test_atr_returns_nan_when_history_is_shorter_than_length() -> None:
    result = atr(
        np.asarray((2.0, 3.0), dtype=float),
        np.asarray((0.5, 1.0), dtype=float),
        np.asarray((1.0, 2.0), dtype=float),
        length=3,
    )

    assert result == pytest.approx((float("nan"), float("nan")), nan_ok=True)


def test_atr_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="length must be positive"):
        atr(
            np.asarray((2.0, 3.0), dtype=float),
            np.asarray((0.5, 1.0), dtype=float),
            np.asarray((1.0, 2.0), dtype=float),
            length=0,
        )
