from __future__ import annotations

from typing import ClassVar

import pytest

from quantleet.backtest import BacktestEngine
from quantleet.backtest.engine import _BacktestStrategyConstructionError
from quantleet.data import BarSeries, TimeBar
from quantleet.data.sources import HistoricalDataSource
from quantleet.strategy import Strategy, StrategyConfig
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent


class FastSlowConfig(StrategyConfig):
    fast: int = 5
    slow: int = 20


class OtherConfig(StrategyConfig):
    value: int = 1


class ConfiguredStrategy(Strategy[FastSlowConfig]):
    seen_configs: ClassVar[list[dict[str, object]]] = []

    def __init__(self, config: FastSlowConfig | None = None) -> None:
        super().__init__(config)
        type(self).seen_configs.append(self.config.to_mapping())

    def on_bar(self, bar: BarEvent) -> None:
        return None


class ConfigLessStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        return None


class CountingStrategy(Strategy):
    instances: ClassVar[list[CountingStrategy]] = []
    handled_counts: ClassVar[list[int]] = []

    def __init__(self, config: StrategyConfig | None = None) -> None:
        super().__init__(config)
        self._handled_count = 0
        type(self).instances.append(self)

    def on_bar(self, bar: BarEvent) -> None:
        self._handled_count += 1
        type(self).handled_counts.append(self._handled_count)


class RaisingConfig(StrategyConfig):
    def validate(self) -> None:
        raise ValueError("bad default config")


class BadDefaultConfigStrategy(Strategy[RaisingConfig]):
    def on_bar(self, bar: BarEvent) -> None:
        return None


class RaisingConstructorStrategy(Strategy[FastSlowConfig]):
    def __init__(self, config: FastSlowConfig | None = None) -> None:
        super().__init__(config)
        raise RuntimeError("constructor exploded")

    def on_bar(self, bar: BarEvent) -> None:
        return None


class NotAStrategy:
    pass


class RecordingSource(HistoricalDataSource):
    def __init__(self) -> None:
        self.load_calls = 0

    def load(self) -> BarSeries:
        self.load_calls += 1
        return _bars()


def test_run_accepts_strategy_class_and_explicit_config() -> None:
    ConfiguredStrategy.seen_configs = []
    config = FastSlowConfig(fast=3, slow=12)

    result = _engine().run(
        bars=_bars(),
        strategy=ConfiguredStrategy,
        config=config,
    )

    assert ConfiguredStrategy.seen_configs == [{"fast": 3, "slow": 12}]
    assert result.report.run.strategy_config == {"fast": 3, "slow": 12}
    assert result.report.run.strategy_class_name == "ConfiguredStrategy"
    result.report.run.strategy_config["fast"] = 99
    assert config.to_mapping() == {"fast": 3, "slow": 12}


def test_run_accepts_omitted_config_and_reports_default_snapshot() -> None:
    result = _engine().run(bars=_bars(), strategy=ConfiguredStrategy)

    assert result.report.run.strategy_config == {"fast": 5, "slow": 20}


def test_run_accepts_config_less_strategy_and_reports_empty_snapshot() -> None:
    result = _engine().run(bars=_bars(), strategy=ConfigLessStrategy)

    assert result.report.run.strategy_config == {}
    assert type(result.report.run.strategy_config) is dict


def test_wrong_config_type_fails_before_source_load() -> None:
    source = RecordingSource()

    with pytest.raises(TypeError, match="ConfiguredStrategy expected config FastSlowConfig"):
        _engine().run(
            source=source,
            strategy=ConfiguredStrategy,
            config=OtherConfig(),
        )

    assert source.load_calls == 0


def test_dict_config_fails_before_source_load() -> None:
    source = RecordingSource()

    with pytest.raises(TypeError, match="config must be a StrategyConfig instance or None"):
        _engine().run(
            source=source,
            strategy=ConfiguredStrategy,
            config={"fast": 3},  # type: ignore[arg-type]
        )

    assert source.load_calls == 0


def test_strategy_instance_fails_before_source_load() -> None:
    source = RecordingSource()

    with pytest.raises(TypeError, match="strategy must be a Strategy class"):
        _engine().run(
            source=source,
            strategy=ConfiguredStrategy(),  # type: ignore[arg-type]
        )

    assert source.load_calls == 0


def test_non_strategy_class_fails_before_source_load() -> None:
    source = RecordingSource()

    with pytest.raises(TypeError, match="strategy must be a Strategy class"):
        _engine().run(
            source=source,
            strategy=NotAStrategy,  # type: ignore[arg-type]
        )

    assert source.load_calls == 0


def test_default_config_materialization_failure_fails_before_source_load() -> None:
    source = RecordingSource()

    with pytest.raises(_BacktestStrategyConstructionError, match="bad default config"):
        _engine().run(source=source, strategy=BadDefaultConfigStrategy)

    assert source.load_calls == 0


def test_strategy_construction_failure_fails_before_source_load() -> None:
    source = RecordingSource()

    with pytest.raises(_BacktestStrategyConstructionError, match="constructor exploded"):
        _engine().run(
            source=source,
            strategy=RaisingConstructorStrategy,
            config=FastSlowConfig(),
        )

    assert source.load_calls == 0


def test_every_run_uses_fresh_strategy_instance() -> None:
    CountingStrategy.instances = []
    CountingStrategy.handled_counts = []

    _engine().run(bars=_bars(), strategy=CountingStrategy)
    _engine().run(bars=_bars(), strategy=CountingStrategy)

    assert len(CountingStrategy.instances) == 2
    assert CountingStrategy.instances[0] is not CountingStrategy.instances[1]
    assert CountingStrategy.handled_counts == [1, 2, 1, 2]


def _engine() -> BacktestEngine:
    return BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )


def _bars() -> BarSeries:
    return BarSeries(
        symbol="BTC/USDT",
        timeframe="1m",
        bar_type="time",
        rows=(
            TimeBar(
                timestamp=60_000,
                open=100.0,
                high=101.0,
                low=99.0,
                close=100.0,
                volume=1.0,
            ),
            TimeBar(
                timestamp=120_000,
                open=101.0,
                high=102.0,
                low=100.0,
                close=101.0,
                volume=1.0,
            ),
        ),
    )
