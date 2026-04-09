from __future__ import annotations

import inspect

import numpy as np
import pytest

from quantcraft.research.indicators.pure.bb import PureBollingerBandsResult, bb


def test_bb_matches_talib_signature_and_result_shape() -> None:
    assert tuple(inspect.signature(bb).parameters) == ("values", "length", "stddev")

    result = bb(np.asarray((1.0, 2.0, 3.0), dtype=float), length=3, stddev=2.0)

    assert isinstance(result, PureBollingerBandsResult)
    assert isinstance(result.upper, np.ndarray)
    assert isinstance(result.middle, np.ndarray)
    assert isinstance(result.lower, np.ndarray)
    assert result.upper == pytest.approx(
        (float("nan"), float("nan"), 3.6329931618554525),
        nan_ok=True,
    )
    assert result.middle == pytest.approx((float("nan"), float("nan"), 2.0), nan_ok=True)
    assert result.lower == pytest.approx(
        (float("nan"), float("nan"), 0.3670068381445475),
        nan_ok=True,
    )


def test_bb_matches_talib_fixture_values_and_field_mapping() -> None:
    result = bb(np.asarray((1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0), dtype=float), length=3, stddev=2.0)

    assert result.upper == pytest.approx(
        (
            float("nan"),
            float("nan"),
            3.6329931618554525,
            4.632993161855452,
            5.632993161855453,
            6.632993161855453,
            7.632993161855449,
        ),
        nan_ok=True,
    )
    assert result.middle == pytest.approx(
        (float("nan"), float("nan"), 2.0, 3.0, 4.0, 5.0, 6.0),
        nan_ok=True,
    )
    assert result.lower == pytest.approx(
        (
            float("nan"),
            float("nan"),
            0.3670068381445475,
            1.3670068381445486,
            2.3670068381445466,
            3.3670068381445466,
            4.367006838144551,
        ),
        nan_ok=True,
    )


def test_bb_returns_nan_when_history_is_shorter_than_length() -> None:
    result = bb(np.asarray((1.0, 2.0), dtype=float), length=3, stddev=2.0)

    assert result.upper == pytest.approx((float("nan"), float("nan")), nan_ok=True)
    assert result.middle == pytest.approx((float("nan"), float("nan")), nan_ok=True)
    assert result.lower == pytest.approx((float("nan"), float("nan")), nan_ok=True)


def test_bb_allows_zero_and_negative_stddev_per_talib() -> None:
    zero = bb(np.asarray((1.0, 2.0, 3.0, 4.0, 5.0), dtype=float), length=3, stddev=0.0)
    negative = bb(np.asarray((1.0, 2.0, 3.0, 4.0, 5.0), dtype=float), length=3, stddev=-2.0)

    assert zero.upper == pytest.approx((float("nan"), float("nan"), 2.0, 3.0, 4.0), nan_ok=True)
    assert zero.middle == pytest.approx((float("nan"), float("nan"), 2.0, 3.0, 4.0), nan_ok=True)
    assert zero.lower == pytest.approx((float("nan"), float("nan"), 2.0, 3.0, 4.0), nan_ok=True)
    assert negative.upper == pytest.approx(
        (
            float("nan"),
            float("nan"),
            0.3670068381445475,
            1.3670068381445486,
            2.3670068381445466,
        ),
        nan_ok=True,
    )
    assert negative.lower == pytest.approx(
        (
            float("nan"),
            float("nan"),
            3.6329931618554525,
            4.632993161855452,
            5.632993161855453,
        ),
        nan_ok=True,
    )


def test_bb_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="length must be positive"):
        bb(np.asarray((1.0, 2.0, 3.0), dtype=float), length=0, stddev=2.0)
