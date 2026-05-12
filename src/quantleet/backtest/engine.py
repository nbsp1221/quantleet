from __future__ import annotations

import math
from dataclasses import dataclass
from typing import cast

from quantleet.backtest.results import BacktestResult
from quantleet.backtest.runtime import _run_backtest
from quantleet.backtest.strategy_runtime import StrategyLike
from quantleet.data import BarSeries
from quantleet.data.sources import HistoricalDataSource
from quantleet.strategy import Strategy, StrategyConfig
from quantleet.trading.domain.costs import CostConfig


class _BacktestStrategyConstructionError(Exception):
    """Raised when a direct backtest cannot construct its strategy instance."""

    def __init__(self, strategy_name: str, original: BaseException) -> None:
        super().__init__(f"failed to construct strategy {strategy_name}: {original}")
        self.original = original


@dataclass(frozen=True, slots=True)
class BacktestEngine:
    initial_cash: float
    costs: CostConfig

    def __post_init__(self) -> None:
        if not math.isfinite(self.initial_cash) or self.initial_cash <= 0.0:
            raise ValueError("initial_cash must be a positive finite float")

    def run(
        self,
        *,
        strategy: type[Strategy[StrategyConfig]],
        config: StrategyConfig | None = None,
        bars: BarSeries | None = None,
        source: HistoricalDataSource | None = None,
        label: str | None = None,
    ) -> BacktestResult:
        if label is not None and (not isinstance(label, str) or not label):
            raise ValueError("label must be a non-empty string or None")
        if (bars is None) == (source is None):
            raise ValueError("provide exactly one of bars or source")
        strategy_instance = _materialize_strategy(strategy=strategy, config=config)
        strategy_config = cast(StrategyConfig, getattr(strategy_instance, "config")).to_mapping()
        runtime_strategy = cast(StrategyLike, strategy_instance)
        if bars is not None:
            raw_bars = bars
        else:
            assert source is not None
            raw_bars = source.load()
        run_bars = _validated_bars(raw_bars)

        return _run_backtest(
            bars=run_bars,
            strategy=runtime_strategy,
            strategy_config=strategy_config,
            initial_cash=self.initial_cash,
            costs=self.costs,
            label=label,
        )


def _materialize_strategy(
    *,
    strategy: object,
    config: object,
) -> Strategy[StrategyConfig]:
    if not isinstance(strategy, type) or not issubclass(strategy, Strategy):
        raise TypeError("strategy must be a Strategy class; pass strategy=StrategyClass")
    if config is not None and not isinstance(config, StrategyConfig):
        raise TypeError("config must be a StrategyConfig instance or None")
    expected_config_type = strategy.config_type
    if config is not None and type(config) is not expected_config_type:
        raise TypeError(
            f"{strategy.__name__} expected config {expected_config_type.__name__}; "
            f"got {type(config).__name__}"
        )
    try:
        return strategy(config)
    except Exception as error:
        raise _BacktestStrategyConstructionError(strategy.__name__, error) from error


def _validated_bars(bars: object) -> BarSeries:
    if not isinstance(bars, BarSeries):
        raise ValueError("bars must be a BarSeries instance")
    if not bars.rows:
        raise ValueError("bars must contain at least one TimeBar")
    return bars


__all__ = ["BacktestEngine"]
