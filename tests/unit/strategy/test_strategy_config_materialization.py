from __future__ import annotations

import math

import pytest

from quantleet.strategy import (
    StrategyConfig,
    StrategyConfigMutationError,
    StrategyConfigValidationError,
)


class RsiConfig(StrategyConfig):
    period: int = 14
    oversold: float = 30.0
    enabled: bool = True
    label: str = "rsi"
    maybe_period: int | None = None


def test_partial_overrides_preserve_non_searched_defaults() -> None:
    config = RsiConfig(period=7, oversold=20.0)

    assert config.period == 7
    assert config.oversold == 20.0
    assert config.to_mapping() == {
        "period": 7,
        "oversold": 20.0,
        "enabled": True,
        "label": "rsi",
        "maybe_period": None,
    }


def test_unknown_and_private_overrides_raise_validation_error() -> None:
    with pytest.raises(StrategyConfigValidationError, match="unknown"):
        RsiConfig(unknown=1)

    with pytest.raises(StrategyConfigValidationError, match="_private"):
        RsiConfig(_private=1)


@pytest.mark.parametrize("value", [1, 7])
def test_int_fields_accept_int_but_not_bool_or_float(value: int) -> None:
    assert RsiConfig(period=value).period == value

    with pytest.raises(StrategyConfigValidationError):
        RsiConfig(period=True)

    with pytest.raises(StrategyConfigValidationError):
        RsiConfig(period=1.5)


def test_float_fields_accept_finite_int_and_float_but_not_bool_or_non_finite() -> None:
    assert RsiConfig(oversold=20).oversold == 20
    assert RsiConfig(oversold=20.5).oversold == 20.5

    with pytest.raises(StrategyConfigValidationError):
        RsiConfig(oversold=True)

    for value in (math.nan, math.inf, -math.inf):
        with pytest.raises(StrategyConfigValidationError):
            RsiConfig(oversold=value)


def test_bool_and_str_fields_are_strict() -> None:
    assert RsiConfig(enabled=False).enabled is False
    assert RsiConfig(label="mean-reversion").label == "mean-reversion"

    with pytest.raises(StrategyConfigValidationError):
        RsiConfig(enabled=1)

    with pytest.raises(StrategyConfigValidationError):
        RsiConfig(label=1)


def test_optional_primitives_accept_none_and_matching_values() -> None:
    assert RsiConfig(maybe_period=None).maybe_period is None
    assert RsiConfig(maybe_period=21).maybe_period == 21

    with pytest.raises(StrategyConfigValidationError):
        RsiConfig(maybe_period=True)


def test_to_mapping_returns_detached_plain_dict() -> None:
    config = RsiConfig(period=7)
    snapshot = config.to_mapping()

    snapshot["period"] = 99

    assert isinstance(snapshot, dict)
    assert config.period == 7
    assert config.to_mapping()["period"] == 7


def test_materialized_config_is_immutable() -> None:
    config = RsiConfig()

    with pytest.raises(StrategyConfigMutationError):
        config.period = 21

    with pytest.raises(StrategyConfigMutationError):
        config.new_value = 1

    with pytest.raises(StrategyConfigMutationError):
        del config.period

    with pytest.raises(StrategyConfigMutationError):
        del config._values


def test_internal_values_mapping_cannot_mutate_snapshot() -> None:
    config = RsiConfig(period=7)

    with pytest.raises(TypeError):
        config._values["period"] = 99

    assert config.period == 7
    assert config.to_mapping()["period"] == 7
