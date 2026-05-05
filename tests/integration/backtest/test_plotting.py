from __future__ import annotations

from datetime import UTC, datetime
from typing import Sequence

import matplotlib
import pytest

matplotlib.use("Agg")

from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from quantleet.backtest import BacktestEngine
from quantleet.data import BarSeries, DataFrameDataSource, HistoricalDataSource, TimeBar
from quantleet.research import Strategy
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent


@pytest.fixture(autouse=True)
def close_figures() -> None:
    yield
    plt.close("all")


class NoTradeStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        return None


class EntryExitStrategy(Strategy):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar: BarEvent) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self._seen_bars == 2 and self.position.is_open:
            self.sell(quantity=1.0, tag="exit")


class LongBeforeDropStrategy(Strategy):
    def init(self) -> None:
        self._entered = False

    def on_bar(self, bar: BarEvent) -> None:
        if not self._entered:
            self._entered = True
            self.buy(quantity=1.0, tag="entry")


class CountingSource(HistoricalDataSource):
    def __init__(self, bars: BarSeries) -> None:
        self.bars = bars
        self.load_count = 0

    def load(self) -> BarSeries:
        self.load_count += 1
        return self.bars


def test_engine_bars_result_plots_price_fills_equity_and_drawdown() -> None:
    result = _engine().run(
        bars=_bars((100.0, 110.0, 120.0, 115.0)),
        strategy=EntryExitStrategy(),
    )

    fig = result.plot()

    assert isinstance(fig, Figure)
    assert len(fig.axes) == 3
    assert _line_ydata(fig.axes[0]) == (100.0, 110.0, 120.0, 115.0)
    assert _line_ydata(fig.axes[1]) == result.equity_curve
    assert _line_ydata(fig.axes[2]) == tuple(-value for value in result.drawdown_curve)
    assert len(fig.axes[0].collections) == 2


def test_engine_source_result_plots_without_reloading_source() -> None:
    source = CountingSource(_bars((100.0, 102.0, 101.0)))
    result = _engine().run(source=source, strategy=NoTradeStrategy())

    fig = result.plot()

    assert source.load_count == 1
    assert _line_ydata(fig.axes[0]) == (100.0, 102.0, 101.0)


def test_plot_uses_snapshot_from_run_instead_of_current_source_state() -> None:
    source = CountingSource(_bars((100.0, 101.0, 102.0)))
    result = _engine().run(source=source, strategy=NoTradeStrategy())
    source.bars = _bars((900.0, 901.0, 902.0))

    fig = result.plot()

    assert source.load_count == 1
    assert _line_ydata(fig.axes[0]) == (100.0, 101.0, 102.0)


def test_plot_uses_snapshot_from_run_instead_of_mutated_user_records() -> None:
    records = [
        _record(timestamp=1, close=100.0),
        _record(timestamp=2, close=101.0),
        _record(timestamp=3, close=102.0),
    ]
    result = _engine().run(
        source=DataFrameDataSource(
            frame=records,
            symbol="BTC/USDT",
            timeframe="1m",
        ),
        strategy=NoTradeStrategy(),
    )
    records[1] = _record(timestamp=2, close=999.0)

    fig = result.plot()

    assert _line_ydata(fig.axes[0]) == (100.0, 101.0, 102.0)


def test_drawdown_plot_matches_engine_result_drawdown_curve() -> None:
    result = _engine().run(
        bars=_bars((100.0, 120.0, 80.0, 90.0)),
        strategy=LongBeforeDropStrategy(),
    )

    fig = result.plot()

    assert any(value > 0.0 for value in result.drawdown_curve)
    assert result.summary.max_drawdown == max(result.drawdown_curve)
    assert _line_ydata(fig.axes[2]) == tuple(-value for value in result.drawdown_curve)


def _engine() -> BacktestEngine:
    return BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )


def _bars(closes: Sequence[float]) -> BarSeries:
    return BarSeries(
        symbol="BTC/USDT",
        timeframe="1m",
        bar_type="time",
        rows=tuple(
            TimeBar(
                timestamp=(index + 1) * 60_000,
                open=close,
                high=close,
                low=close,
                close=close,
                volume=1.0,
            )
            for index, close in enumerate(closes)
        ),
    )


def _record(*, timestamp: int, close: float) -> dict[str, object]:
    return {
        "timestamp": datetime.fromtimestamp(timestamp * 60, tz=UTC),
        "open": close,
        "high": close,
        "low": close,
        "close": close,
        "volume": 1.0,
    }


def _line_ydata(axis, index: int = 0) -> tuple[float, ...]:
    return tuple(float(value) for value in axis.lines[index].get_ydata())
