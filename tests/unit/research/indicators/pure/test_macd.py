from __future__ import annotations

import inspect

import numpy as np
import pytest

from quantcraft.research.indicators.pure.macd import PureMACDResult, macd


def test_macd_matches_talib_signature_and_result_shape() -> None:
    assert tuple(inspect.signature(macd).parameters) == ("values", "fast", "slow", "signal")

    result = macd(np.asarray((1.0, 2.0, 3.0, 4.0), dtype=float), fast=2, slow=3, signal=2)

    assert isinstance(result, PureMACDResult)
    assert isinstance(result.macd, np.ndarray)
    assert isinstance(result.signal, np.ndarray)
    assert isinstance(result.histogram, np.ndarray)
    assert result.macd == pytest.approx(
        (float("nan"), float("nan"), float("nan"), 0.5),
        nan_ok=True,
    )
    assert result.signal == pytest.approx(
        (float("nan"), float("nan"), float("nan"), 0.5),
        nan_ok=True,
    )
    assert result.histogram == pytest.approx(
        (float("nan"), float("nan"), float("nan"), 0.0),
        nan_ok=True,
    )


def test_macd_matches_talib_fixture_values() -> None:
    result = macd(
        np.asarray((5.0, 4.0, 6.0, 3.0, 7.0, 2.0, 8.0), dtype=float),
        fast=2,
        slow=3,
        signal=2,
    )

    assert result.macd == pytest.approx(
        (
            float("nan"),
            float("nan"),
            float("nan"),
            -0.33333333333333304,
            0.3888888888888893,
            -0.4537037037037033,
            0.5570987654320989,
        ),
        nan_ok=True,
    )
    assert result.signal == pytest.approx(
        (
            float("nan"),
            float("nan"),
            float("nan"),
            -0.16666666666666652,
            0.203703703703704,
            -0.23456790123456744,
            0.29320987654321,
        ),
        nan_ok=True,
    )
    assert result.histogram == pytest.approx(
        (
            float("nan"),
            float("nan"),
            float("nan"),
            -0.16666666666666652,
            0.18518518518518529,
            -0.21913580246913583,
            0.2638888888888889,
        ),
        nan_ok=True,
    )


def test_macd_returns_all_nan_when_fast_period_exceeds_slow_period() -> None:
    result = macd(np.asarray((1.0, 2.0, 3.0, 4.0, 5.0), dtype=float), fast=5, slow=3, signal=2)

    assert result.macd == pytest.approx(
        (float("nan"), float("nan"), float("nan"), float("nan"), float("nan")),
        nan_ok=True,
    )
    assert result.signal == pytest.approx(
        (float("nan"), float("nan"), float("nan"), float("nan"), float("nan")),
        nan_ok=True,
    )
    assert result.histogram == pytest.approx(
        (float("nan"), float("nan"), float("nan"), float("nan"), float("nan")),
        nan_ok=True,
    )


def test_macd_rejects_non_positive_periods() -> None:
    with pytest.raises(ValueError, match="fast must be positive"):
        macd(np.asarray((1.0, 2.0, 3.0), dtype=float), fast=0, slow=3, signal=2)

    with pytest.raises(ValueError, match="slow must be positive"):
        macd(np.asarray((1.0, 2.0, 3.0), dtype=float), fast=2, slow=0, signal=2)

    with pytest.raises(ValueError, match="signal must be positive"):
        macd(np.asarray((1.0, 2.0, 3.0), dtype=float), fast=2, slow=3, signal=0)
