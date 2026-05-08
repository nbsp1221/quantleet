from __future__ import annotations

import pytest

from quantleet.backtest.strategy_runtime import _StrategyDriver
from quantleet.strategy import (
    Strategy,
    StrategyConfig,
    StrategyConfigMutationError,
    StrategyConfigValidationError,
)
from quantleet.trading.domain.events import BarEvent


class ThresholdConfig(StrategyConfig):
    threshold: float = 10.0


class ConfiguredStrategy(Strategy[ThresholdConfig]):
    def __init__(self, config: ThresholdConfig | None = None) -> None:
        super().__init__(config)
        self.seen_in_init: float | None = None
        self.seen_in_on_bar: float | None = None

    def init(self) -> None:
        self.seen_in_init = self.config.threshold

    def on_bar(self, bar: BarEvent) -> None:
        self.seen_in_on_bar = self.config.threshold


def _closed_bar(close: float = 12.0) -> BarEvent:
    return BarEvent(
        bar_type="time",
        bar_spec="1m",
        symbol="BTC/USDT",
        timestamp=1,
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1.0,
        is_closed=True,
    )


def test_strategy_config_is_available_without_user_init_for_ordinary_strategy() -> None:
    class NoInitStrategy(Strategy[ThresholdConfig]):
        def init(self) -> None:
            self.initial_threshold = self.config.threshold

        def on_bar(self, bar: BarEvent) -> None:
            self.buy(quantity=1.0)

    strategy = NoInitStrategy()
    runtime = _StrategyDriver(strategy)

    runtime.initialize()
    runtime.handle_bar(_closed_bar())

    assert strategy.initial_threshold == 10.0
    assert strategy.config.to_mapping() == {"threshold": 10.0}
    assert len(runtime.order_state().pending) == 1


def test_strategy_accepts_explicit_config_instance() -> None:
    strategy = ConfiguredStrategy(ThresholdConfig(threshold=25.0))
    runtime = _StrategyDriver(strategy)

    runtime.initialize()
    runtime.handle_bar(_closed_bar())

    assert strategy.seen_in_init == 25.0
    assert strategy.seen_in_on_bar == 25.0


def test_config_less_strategy_has_empty_config_and_runtime_state() -> None:
    class EmptyStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(quantity=1.0)

    strategy = EmptyStrategy()
    runtime = _StrategyDriver(strategy)

    runtime.initialize()
    runtime.handle_bar(_closed_bar())

    assert strategy.config.to_mapping() == {}
    assert len(runtime.order_state().pending) == 1


def test_strategy_config_reassignment_is_rejected() -> None:
    strategy = ConfiguredStrategy()

    with pytest.raises(StrategyConfigMutationError):
        strategy.config = ThresholdConfig(threshold=1.0)


def test_strategy_config_deletion_is_rejected() -> None:
    strategy = ConfiguredStrategy()

    with pytest.raises(StrategyConfigMutationError):
        del strategy.config

    assert strategy.config.to_mapping() == {"threshold": 10.0}


def test_strategy_rejects_config_subclass_that_widens_declared_schema() -> None:
    class ExtendedThresholdConfig(ThresholdConfig):
        extra: int = 1

    with pytest.raises(StrategyConfigValidationError, match="expected config ThresholdConfig"):
        ConfiguredStrategy(ExtendedThresholdConfig(threshold=5.0, extra=2))


def test_config_mutation_during_lifecycle_fails_before_order_intake() -> None:
    class MutatingStrategy(Strategy[ThresholdConfig]):
        def on_bar(self, bar: BarEvent) -> None:
            self.config.threshold = 1.0
            self.buy(quantity=1.0)

    strategy = MutatingStrategy()
    runtime = _StrategyDriver(strategy)
    runtime.initialize()

    with pytest.raises(StrategyConfigMutationError):
        runtime.handle_bar(_closed_bar())

    assert runtime.order_state().pending == ()
