from __future__ import annotations

import math

import pytest

from quantcraft.trading.domain.costs import CostConfig


def test_cost_config_rejects_non_positive_tick_size() -> None:
    with pytest.raises(ValueError, match="tick_size must be a positive finite float"):
        CostConfig(tick_size=0.0, slippage_ticks=1.0, fee_rate=0.001)

    with pytest.raises(ValueError, match="tick_size must be a positive finite float"):
        CostConfig(tick_size=-0.5, slippage_ticks=1.0, fee_rate=0.001)


def test_cost_config_rejects_negative_slippage_ticks() -> None:
    with pytest.raises(ValueError, match="slippage_ticks must be a non-negative finite float"):
        CostConfig(tick_size=0.5, slippage_ticks=-1.0, fee_rate=0.001)


def test_cost_config_rejects_negative_fee_rate() -> None:
    with pytest.raises(ValueError, match="fee_rate must be a non-negative finite float"):
        CostConfig(tick_size=0.5, slippage_ticks=1.0, fee_rate=-0.001)


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("tick_size", math.nan, "tick_size must be a positive finite float"),
        ("tick_size", math.inf, "tick_size must be a positive finite float"),
        ("slippage_ticks", math.nan, "slippage_ticks must be a non-negative finite float"),
        ("slippage_ticks", math.inf, "slippage_ticks must be a non-negative finite float"),
        ("fee_rate", math.nan, "fee_rate must be a non-negative finite float"),
        ("fee_rate", math.inf, "fee_rate must be a non-negative finite float"),
    ],
)
def test_cost_config_rejects_non_finite_values(
    field_name: str,
    value: float,
    message: str,
) -> None:
    kwargs = {
        "tick_size": 0.5,
        "slippage_ticks": 1.0,
        "fee_rate": 0.001,
    }
    kwargs[field_name] = value

    with pytest.raises(ValueError, match=message):
        CostConfig(**kwargs)


def test_cost_config_accepts_positive_tick_size_and_zero_costs() -> None:
    costs = CostConfig(tick_size=0.5, slippage_ticks=0.0, fee_rate=0.0)

    assert costs.tick_size == 0.5
    assert costs.slippage_ticks == 0.0
    assert costs.fee_rate == 0.0
