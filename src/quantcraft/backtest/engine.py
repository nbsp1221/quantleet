from __future__ import annotations

import math
from dataclasses import dataclass

from quantcraft.backtest.results import BacktestResult
from quantcraft.backtest.runtime import _run_backtest
from quantcraft.backtest.strategy_runtime import StrategyLike
from quantcraft.data import BarSeries
from quantcraft.data.sources import HistoricalDataSource
from quantcraft.trading.domain.costs import CostConfig


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
        strategy: StrategyLike,
        bars: BarSeries | None = None,
        source: HistoricalDataSource | None = None,
    ) -> BacktestResult:
        if (bars is None) == (source is None):
            raise ValueError("provide exactly one of bars or source")

        if bars is not None:
            return _run_backtest(
                bars=_validated_bars(bars),
                strategy=strategy,
                initial_cash=self.initial_cash,
                costs=self.costs,
            )

        if source is None:
            raise ValueError("source must be provided")

        return _run_backtest(
            bars=_validated_bars(source.load()),
            strategy=strategy,
            initial_cash=self.initial_cash,
            costs=self.costs,
        )


def _validated_bars(bars: object) -> BarSeries:
    if not isinstance(bars, BarSeries):
        raise ValueError("bars must be a BarSeries instance")
    return bars


__all__ = ["BacktestEngine"]
