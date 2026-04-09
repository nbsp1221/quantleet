from __future__ import annotations

import inspect

import numpy as np
import pytest

from quantcraft.research.indicators.pure.sma import sma


def test_sma_matches_talib_signature_and_returns_ndarray() -> None:
    assert tuple(inspect.signature(sma).parameters) == ("values", "length")

    result = sma(np.asarray((1.0, 2.0, 3.0), dtype=float), length=3)

    assert isinstance(result, np.ndarray)
    assert result == pytest.approx((float("nan"), float("nan"), 2.0), nan_ok=True)


def test_sma_uses_talib_warmup_and_expected_fixture_values() -> None:
    result = sma(np.asarray((1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0), dtype=float), length=3)

    assert result == pytest.approx(
        (float("nan"), float("nan"), 2.0, 3.0, 4.0, 5.0, 6.0),
        nan_ok=True,
    )


def test_sma_returns_nan_when_history_is_shorter_than_length() -> None:
    result = sma(np.asarray((1.0, 2.0), dtype=float), length=3)

    assert result == pytest.approx((float("nan"), float("nan")), nan_ok=True)


def test_sma_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="length must be positive"):
        sma(np.asarray((1.0, 2.0, 3.0), dtype=float), length=0)
