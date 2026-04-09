from __future__ import annotations

import inspect

import numpy as np
import pytest

from quantcraft.research.indicators.pure.cci import cci


def test_cci_matches_talib_signature_and_returns_ndarray() -> None:
    assert tuple(inspect.signature(cci).parameters) == ("high", "low", "close", "length")

    result = cci(
        np.asarray((2.0, 3.0, 4.0), dtype=float),
        np.asarray((0.5, 1.0, 2.0), dtype=float),
        np.asarray((1.0, 2.0, 3.0), dtype=float),
        length=3,
    )

    assert isinstance(result, np.ndarray)
    assert result == pytest.approx((float("nan"), float("nan"), 100.0), nan_ok=True)


def test_cci_matches_talib_fixture_values() -> None:
    result = cci(
        np.asarray((6.0, 5.0, 7.0, 4.0, 8.0, 3.0, 9.0), dtype=float),
        np.asarray((3.5, 2.5, 4.5, 1.5, 5.5, 0.5, 6.5), dtype=float),
        np.asarray((5.0, 4.0, 6.0, 3.0, 7.0, 2.0, 8.0), dtype=float),
        length=3,
    )

    assert result == pytest.approx(
        (
            float("nan"),
            float("nan"),
            100.00000000000003,
            -80.00000000000003,
            71.42857142857142,
            -66.66666666666667,
            63.63636363636364,
        ),
        nan_ok=True,
    )


def test_cci_returns_zero_for_flat_input_after_warmup() -> None:
    result = cci(
        np.asarray((5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0), dtype=float),
        np.asarray((5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0), dtype=float),
        np.asarray((5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0), dtype=float),
        length=3,
    )

    assert result == pytest.approx(
        (float("nan"), float("nan"), 0.0, 0.0, 0.0, 0.0, 0.0),
        nan_ok=True,
    )


def test_cci_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="length must be positive"):
        cci(
            np.asarray((2.0, 3.0), dtype=float),
            np.asarray((0.5, 1.0), dtype=float),
            np.asarray((1.0, 2.0), dtype=float),
            length=0,
        )
