from __future__ import annotations

from typing import Generator

import matplotlib
import pytest

matplotlib.use("Agg")

from matplotlib import pyplot as plt

from quantleet.backtest import BacktestEngine
from quantleet.data import BarSeries, TimeBar
from quantleet.research import Strategy
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent

PLOT_BAR_COUNT = 10_000


@pytest.fixture(autouse=True)
def close_figures() -> Generator[None]:
    yield
    plt.close("all")


class NoTradeStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        return None


@pytest.mark.slow
def test_backtest_result_plot_handles_ten_thousand_bars_within_threshold() -> None:
    result = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    ).run(
        bars=_bars(PLOT_BAR_COUNT),
        strategy=NoTradeStrategy(),
    )

    fig = result.plot()

    assert len(fig.axes[0].lines[0].get_ydata()) == PLOT_BAR_COUNT
    assert len(fig.axes[1].lines[0].get_ydata()) == PLOT_BAR_COUNT
    assert len(fig.axes[2].lines[0].get_ydata()) == PLOT_BAR_COUNT


def _bars(count: int) -> BarSeries:
    return BarSeries(
        symbol="BTC/USDT",
        timeframe="1m",
        bar_type="time",
        rows=tuple(
            TimeBar(
                timestamp=(index + 1) * 60_000,
                open=100.0 + (index % 10),
                high=100.0 + (index % 10),
                low=100.0 + (index % 10),
                close=100.0 + (index % 10),
                volume=1.0,
            )
            for index in range(count)
        ),
    )
