from __future__ import annotations

import pytest

from quantleet.strategy import (
    Strategy,
    StrategyConfig,
    StrategyConfigDeclarationError,
)
from quantleet.trading.domain.events import BarEvent


def test_public_annotated_defaults_become_ordered_config_fields() -> None:
    class RsiConfig(StrategyConfig):
        period: int = 14
        oversold: float = 30.0
        enabled: bool = True
        label: str = "rsi"
        _cache_key: str = "ignored"
        unannotated = "ignored"

    config = RsiConfig()

    assert config.to_mapping() == {
        "period": 14,
        "oversold": 30.0,
        "enabled": True,
        "label": "rsi",
    }
    assert "_cache_key" not in config.to_mapping()
    assert "unannotated" not in config.to_mapping()


def test_private_annotations_are_ignored_before_type_resolution() -> None:
    class PrivateAnnotationConfig(StrategyConfig):
        period: int = 14
        _cache: "NotImported" = None  # noqa: F821

    assert PrivateAnnotationConfig().to_mapping() == {"period": 14}


def test_inherited_fields_are_base_first_and_subclass_redeclarations_win() -> None:
    class BaseConfig(StrategyConfig):
        lookback: int = 20
        threshold: float = 1.5

    class ChildConfig(BaseConfig):
        threshold: float = 2.0
        enabled: bool = False

    assert ChildConfig().to_mapping() == {
        "lookback": 20,
        "threshold": 2.0,
        "enabled": False,
    }


def test_missing_default_raises_declaration_error() -> None:
    with pytest.raises(StrategyConfigDeclarationError, match="default"):

        class MissingDefaultConfig(StrategyConfig):
            lookback: int


@pytest.mark.parametrize(
    "annotation, default",
    [
        (list[int], [1, 2]),
        (dict[str, int], {"x": 1}),
        (tuple[int, ...], (1,)),
        (object, object()),
    ],
)
def test_unsupported_annotations_raise_declaration_error(
    annotation: object,
    default: object,
) -> None:
    with pytest.raises(StrategyConfigDeclarationError):
        type(
            "InvalidConfig",
            (StrategyConfig,),
            {
                "__annotations__": {"value": annotation},
                "value": default,
            },
        )


def test_non_optional_none_default_raises_declaration_error() -> None:
    with pytest.raises(StrategyConfigDeclarationError, match="None"):

        class NoneDefaultConfig(StrategyConfig):
            maybe: int = None  # type: ignore[assignment]


def test_optional_none_default_is_accepted() -> None:
    class OptionalConfig(StrategyConfig):
        maybe: int | None = None

    assert OptionalConfig().to_mapping() == {"maybe": None}


def test_strategy_generic_config_declaration_materializes_default_config() -> None:
    class RsiConfig(StrategyConfig):
        period: int = 14

    class RsiStrategy(Strategy[RsiConfig]):
        def on_bar(self, bar: BarEvent) -> None:
            pass

    strategy = RsiStrategy()

    assert isinstance(strategy.config, RsiConfig)
    assert strategy.config.to_mapping() == {"period": 14}


def test_config_type_fallback_is_accepted() -> None:
    class RiskConfig(StrategyConfig):
        risk_per_trade: float = 0.01

    class RiskStrategy(Strategy):
        config_type = RiskConfig

        def on_bar(self, bar: BarEvent) -> None:
            pass

    assert RiskStrategy().config.to_mapping() == {"risk_per_trade": 0.01}


def test_same_type_generic_and_fallback_declaration_is_accepted() -> None:
    class RsiConfig(StrategyConfig):
        period: int = 14

    class RsiStrategy(Strategy[RsiConfig]):
        config_type = RsiConfig

        def on_bar(self, bar: BarEvent) -> None:
            pass

    assert RsiStrategy().config.to_mapping() == {"period": 14}


def test_conflicting_generic_and_fallback_declaration_raises() -> None:
    class RsiConfig(StrategyConfig):
        period: int = 14

    class OtherConfig(StrategyConfig):
        lookback: int = 10

    with pytest.raises(StrategyConfigDeclarationError, match="conflict"):

        class ConflictingStrategy(Strategy[RsiConfig]):
            config_type = OtherConfig

            def on_bar(self, bar: BarEvent) -> None:
                pass


def test_invalid_config_type_fallback_raises() -> None:
    with pytest.raises(StrategyConfigDeclarationError):

        class InvalidFallbackStrategy(Strategy):
            config_type = object

            def on_bar(self, bar: BarEvent) -> None:
                pass


def test_config_less_strategy_gets_empty_config() -> None:
    class EmptyStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            pass

    assert type(EmptyStrategy().config) is StrategyConfig
    assert EmptyStrategy().config.to_mapping() == {}
