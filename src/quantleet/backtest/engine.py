from __future__ import annotations

import math
from dataclasses import dataclass

from quantleet.backtest.results import BacktestResult
from quantleet.backtest.runtime import _run_backtest
from quantleet.backtest.strategy_runtime import StrategyLike
from quantleet.data import BarSeries
from quantleet.data.sources import HistoricalDataSource
from quantleet.trading.domain.costs import CostConfig


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
        label: str | None = None,
    ) -> BacktestResult:
        if label is not None and (not isinstance(label, str) or not label):
            raise ValueError("label must be a non-empty string or None")
        if (bars is None) == (source is None):
            raise ValueError("provide exactly one of bars or source")

        if bars is not None:
            return _run_backtest(
                bars=_validated_bars(bars),
                strategy=strategy,
                initial_cash=self.initial_cash,
                costs=self.costs,
                label=label,
            )

        if source is None:
            raise ValueError("source must be provided")

        return _run_backtest(
            bars=_validated_bars(source.load()),
            strategy=strategy,
            initial_cash=self.initial_cash,
            costs=self.costs,
            label=label,
        )


def _validated_bars(bars: object) -> BarSeries:
    if not isinstance(bars, BarSeries):
        raise ValueError("bars must be a BarSeries instance")
    if not bars.rows:
        raise ValueError("bars must contain at least one TimeBar")
    return bars


__all__ = ["BacktestEngine"]
