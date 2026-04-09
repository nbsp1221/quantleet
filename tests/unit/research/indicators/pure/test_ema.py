from __future__ import annotations

import inspect

import numpy as np
import pytest

from quantcraft.research.indicators.pure.ema import ema


def test_ema_matches_talib_signature_and_returns_ndarray() -> None:
    assert tuple(inspect.signature(ema).parameters) == ("values", "length")

    result = ema(np.asarray((1.0, 2.0, 3.0), dtype=float), length=3)

    assert isinstance(result, np.ndarray)
    assert result == pytest.approx((float("nan"), float("nan"), 2.0), nan_ok=True)


def test_ema_uses_talib_seed_and_fixture_values() -> None:
    result = ema(np.asarray((5.0, 4.0, 6.0, 3.0, 7.0, 2.0, 8.0), dtype=float), length=3)

    assert result == pytest.approx(
        (float("nan"), float("nan"), 5.0, 4.0, 5.5, 3.75, 5.875),
        nan_ok=True,
    )


def test_ema_keeps_flat_input_flat_after_warmup() -> None:
    result = ema(np.asarray((5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0), dtype=float), length=3)

    assert result == pytest.approx(
        (float("nan"), float("nan"), 5.0, 5.0, 5.0, 5.0, 5.0),
        nan_ok=True,
    )


def test_ema_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="length must be positive"):
        ema(np.asarray((1.0, 2.0, 3.0), dtype=float), length=0)
