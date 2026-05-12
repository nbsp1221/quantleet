from __future__ import annotations

import matplotlib
from matplotlib.figure import Figure

matplotlib.use("Agg")

from quantleet.backtest import BacktestEngine, CostConfig
from quantleet.data import BarSeries, DataFrameDataSource, TimeBar
from quantleet.research import ParameterStudy, qc, ta
from quantleet.strategy import Strategy, StrategyConfig, StrategyConfigValidationError


def test_public_sma_crossover_quickstart_example_runs() -> None:
    class SmaCrossStrategy(Strategy):
        def init(self) -> None:
            self.fast = ta.sma(self.data.close, length=2)
            self.slow = ta.sma(self.data.close, length=3)

        def on_bar(self, bar) -> None:
            if qc.is_na(self.fast[0]) or qc.is_na(self.slow[0]):
                return
            if qc.crossover(self.fast, self.slow):
                self.buy(quantity=1.0, tag="sma-entry")
            elif self.position.is_open and qc.crossunder(self.fast, self.slow):
                self.sell(quantity=1.0, tag="sma-exit")

    source = DataFrameDataSource(
        frame=[
            _record(1, 10.0),
            _record(2, 9.0),
            _record(3, 8.0),
            _record(4, 11.0),
            _record(5, 12.0),
            _record(6, 10.0),
            _record(7, 8.0),
        ],
        symbol="BTC/USDT",
        timeframe="1m",
    )

    result = _engine().run(source=source, strategy=SmaCrossStrategy, label="sma-cross")

    assert result.report.run.run_label == "sma-cross"
    assert "Return" in str(result.report)
    assert isinstance(result.plot(), Figure)


def test_public_orders_and_sizing_example_runs() -> None:
    class OrdersAndSizingStrategy(Strategy):
        def init(self) -> None:
            self._limit_submitted = False
            self._stop_market_submitted = False
            self._stop_limit_submitted = False

        def on_bar(self, bar) -> None:
            visible = len(self.data.close)
            if visible == 1:
                self.buy(quantity=1.0, tag="fixed-market")
                self.buy(qty_percent=10.0, order_type="limit", limit_price=99.0, tag="limit")
                self._limit_submitted = True
            elif visible == 2 and self.position.is_open and not self._stop_market_submitted:
                self.sell(
                    qty_percent=50.0,
                    order_type="stop_market",
                    stop_price=95.0,
                    tag="stop-market",
                )
                self._stop_market_submitted = True
            elif visible == 3 and self.position.is_open and not self._stop_limit_submitted:
                self.sell(
                    qty_percent=100.0,
                    order_type="stop_limit",
                    stop_price=94.0,
                    limit_price=94.0,
                    tag="stop-limit",
                )
                self._stop_limit_submitted = True

    result = _engine().run(
        bars=_bars((100.0, 101.0, 96.0, 94.0, 93.0)),
        strategy=OrdersAndSizingStrategy,
        label="orders-and-sizing",
    )

    assert result.report.run.run_label == "orders-and-sizing"
    assert result.summary.total_fills >= 1
    assert result.final_state.position_quantity >= 0.0
    assert result.report.fills


def test_public_parameter_exploration_example_runs() -> None:
    class SmaConfig(StrategyConfig):
        fast: int = 2
        slow: int = 3

        def validate(self) -> None:
            if self.fast >= self.slow:
                raise StrategyConfigValidationError("fast must be less than slow")

    class ParameterizedSmaStrategy(Strategy[SmaConfig]):
        def init(self) -> None:
            self.fast = ta.sma(self.data.close, length=self.config.fast)
            self.slow = ta.sma(self.data.close, length=self.config.slow)

        def on_bar(self, bar) -> None:
            if qc.is_na(self.fast[0]) or qc.is_na(self.slow[0]):
                return
            if qc.crossover(self.fast, self.slow):
                self.buy(quantity=1.0, tag="entry")
            elif self.position.is_open and qc.crossunder(self.fast, self.slow):
                self.sell(quantity=1.0, tag="exit")

    result = ParameterStudy(
        engine=_engine(),
        bars=_bars((10.0, 9.0, 8.0, 11.0, 12.0, 10.0, 8.0)),
        strategy=ParameterizedSmaStrategy,
    ).grid_search(
        parameters={"fast": [2, 3], "slow": [3, 4]},
        constraint=lambda parameters: parameters["fast"] < parameters["slow"],
        objective=("returns.total_return", "max"),
    )

    assert result.candidate_count == 4
    assert result.rejected_count == 1
    assert result.successful_count == 3
    best = result.best()
    assert best.backtest is not None
    assert best.backtest.report.run.strategy_config == dict(best.strategy_config)
    assert len(result.to_records()) == 4


def _engine() -> BacktestEngine:
    return BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )


def _bars(closes: tuple[float, ...]) -> BarSeries:
    return BarSeries(
        symbol="BTC/USDT",
        timeframe="1m",
        bar_type="time",
        rows=tuple(
            TimeBar(
                timestamp=(index + 1) * 60_000,
                open=close,
                high=close + 2.0,
                low=close - 2.0,
                close=close,
                volume=1.0,
            )
            for index, close in enumerate(closes)
        ),
    )


def _record(timestamp: int, close: float) -> dict[str, object]:
    return {
        "timestamp": f"1970-01-01T00:{timestamp:02d}:00+00:00",
        "open": close,
        "high": close + 2.0,
        "low": close - 2.0,
        "close": close,
        "volume": 1.0,
    }
