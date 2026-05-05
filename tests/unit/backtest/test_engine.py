from __future__ import annotations

import math

import pytest

from quantleet.backtest import BacktestEngine
from quantleet.data import BarSeries, TimeBar
from quantleet.research import Strategy
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent


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


class NoTradeStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        return None


def test_backtest_engine_rejects_empty_label() -> None:
    engine = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    with pytest.raises(ValueError, match="label"):
        engine.run(
            bars=BarSeries(
                symbol="BTC/USDT",
                timeframe="1m",
                bar_type="time",
                rows=(
                    TimeBar(
                        timestamp=60_000,
                        open=100.0,
                        high=100.0,
                        low=100.0,
                        close=100.0,
                        volume=1.0,
                    ),
                ),
            ),
            strategy=NoTradeStrategy(),
            label="",
        )


def test_backtest_engine_rejects_empty_bar_series_before_reporting() -> None:
    engine = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    with pytest.raises(ValueError, match="at least one TimeBar"):
        engine.run(
            bars=BarSeries(symbol="BTC/USDT", timeframe="1m", bar_type="time", rows=()),
            strategy=NoTradeStrategy(),
        )
