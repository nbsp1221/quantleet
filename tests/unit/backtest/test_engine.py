from __future__ import annotations

import math

import pytest

from quantcraft.backtest import BacktestEngine
from quantcraft.trading.domain.costs import CostConfig


def test_backtest_engine_rejects_non_positive_initial_cash() -> None:
    with pytest.raises(ValueError, match="initial_cash must be a positive finite float"):
        BacktestEngine(
            initial_cash=0.0,
            costs=CostConfig(tick_size=0.5, slippage_ticks=1.0, fee_rate=0.001),
        )

    with pytest.raises(ValueError, match="initial_cash must be a positive finite float"):
        BacktestEngine(
            initial_cash=-1.0,
            costs=CostConfig(tick_size=0.5, slippage_ticks=1.0, fee_rate=0.001),
        )


@pytest.mark.parametrize("invalid_value", [math.nan, math.inf, -math.inf])
def test_backtest_engine_rejects_non_finite_initial_cash(invalid_value: float) -> None:
    with pytest.raises(ValueError, match="initial_cash must be a positive finite float"):
        BacktestEngine(
            initial_cash=invalid_value,
            costs=CostConfig(tick_size=0.5, slippage_ticks=1.0, fee_rate=0.001),
        )


def test_backtest_engine_accepts_positive_finite_initial_cash() -> None:
    engine = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=0.5, slippage_ticks=1.0, fee_rate=0.001),
    )

    assert engine.initial_cash == 1_000.0
