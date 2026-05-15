from __future__ import annotations

import json
import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass

import pytest

from quantleet.backtest import BacktestEngine
from quantleet.data import BarSeries
from quantleet.research import ParameterStudy, ta
from quantleet.strategy import Strategy, StrategyConfig
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent
from tests.support_backtest import load_canonical_bars

type ParameterGrid = dict[str, list[int]]
type Constraint = Callable[[Mapping[str, object]], bool]


@dataclass(frozen=True, slots=True)
class ExpectedBestRun:
    strategy_config: dict[str, int]
    total_return: float
    final_equity: float
    max_drawdown: float
    closed_trades: int
    win_rate: float
    profit_factor: float


@dataclass(frozen=True, slots=True)
class ScenarioContract:
    name: str
    parameters: ParameterGrid
    constraint: Constraint
    strategy: type[Strategy]
    candidate_count: int
    expected: ExpectedBestRun


class ExperimentSmaCrossConfig(StrategyConfig):
    fast: int = 8
    slow: int = 64


class ExperimentSmaCross(Strategy[ExperimentSmaCrossConfig]):
    @property
    def display_name(self) -> str:
        return "Experiment SMA Cross"

    def init(self) -> None:
        self.fast = ta.sma(self.data.close, length=self.config.fast)
        self.slow = ta.sma(self.data.close, length=self.config.slow)

    def on_bar(self, bar: BarEvent) -> None:
        fast = self.fast[0]
        slow = self.slow[0]
        indicators_ready = math.isfinite(fast) and math.isfinite(slow)
        if indicators_ready and fast > slow and not self.position.is_open:
            self.buy(qty_percent=100.0, tag="entry")
        elif indicators_ready and fast < slow and self.position.is_open:
            self.sell(qty_percent=100.0, tag="exit")


class ExperimentRsiMeanReversionConfig(StrategyConfig):
    length: int = 14
    lower: int = 30
    upper: int = 70


class ExperimentRsiMeanReversion(Strategy[ExperimentRsiMeanReversionConfig]):
    @property
    def display_name(self) -> str:
        return "Experiment RSI Mean Reversion"

    def init(self) -> None:
        self.rsi = ta.rsi(self.data.close, length=self.config.length)

    def on_bar(self, bar: BarEvent) -> None:
        value = self.rsi[0]
        if math.isfinite(value) and value < self.config.lower and not self.position.is_open:
            self.buy(qty_percent=100.0, tag="entry")
        elif math.isfinite(value) and value > self.config.upper and self.position.is_open:
            self.sell(qty_percent=100.0, tag="exit")


class ExperimentDonchianBreakoutConfig(StrategyConfig):
    entry: int = 20
    exit: int = 10


class ExperimentDonchianBreakout(Strategy[ExperimentDonchianBreakoutConfig]):
    @property
    def display_name(self) -> str:
        return "Experiment Donchian Breakout"

    def on_bar(self, bar: BarEvent) -> None:
        if len(self.data.close) <= self.config.entry:
            return

        previous_highs = [self.data.high[index] for index in range(1, self.config.entry + 1)]
        previous_lows = [self.data.low[index] for index in range(1, self.config.exit + 1)]
        if not self.position.is_open and self.data.close[0] > max(previous_highs):
            self.buy(qty_percent=100.0, tag="entry")
        elif self.position.is_open and self.data.close[0] < min(previous_lows):
            self.sell(qty_percent=100.0, tag="exit")


# Expected values are the Quantcraft outputs validated by the 2026-05-02
# external comparison experiment plan.
SCENARIOS = (
    ScenarioContract(
        name="sma_cross",
        parameters={"fast": [8, 16, 32], "slow": [64, 128]},
        constraint=lambda parameters: int(parameters["fast"]) < int(parameters["slow"]),
        strategy=ExperimentSmaCross,
        candidate_count=6,
        expected=ExpectedBestRun(
            strategy_config={"fast": 32, "slow": 64},
            total_return=-0.00462704205,
            final_equity=995_372.957949989,
            max_drawdown=0.224884233499,
            closed_trades=79,
            win_rate=0.392405063291,
            profit_factor=1.006075199849,
        ),
    ),
    ScenarioContract(
        name="rsi_mean_reversion",
        parameters={"length": [7, 14, 21], "lower": [25, 30], "upper": [60, 70]},
        constraint=lambda parameters: float(parameters["lower"]) < float(parameters["upper"]),
        strategy=ExperimentRsiMeanReversion,
        candidate_count=12,
        expected=ExpectedBestRun(
            strategy_config={"length": 21, "lower": 30, "upper": 70},
            total_return=0.207109810855,
            final_equity=1_207_109.8108548732,
            max_drawdown=0.254289297864,
            closed_trades=17,
            win_rate=0.705882352941,
            profit_factor=1.667999826183,
        ),
    ),
    ScenarioContract(
        name="donchian_breakout",
        parameters={"entry": [20, 40, 80], "exit": [10, 20]},
        constraint=lambda parameters: int(parameters["exit"]) <= int(parameters["entry"]),
        strategy=ExperimentDonchianBreakout,
        candidate_count=6,
        expected=ExpectedBestRun(
            strategy_config={"entry": 80, "exit": 20},
            total_return=-0.00604958936,
            final_equity=993_950.4106398957,
            max_drawdown=0.189317502621,
            closed_trades=45,
            win_rate=0.4,
            profit_factor=0.986418390017,
        ),
    ),
)


@pytest.fixture(scope="module")
def canonical_bars() -> BarSeries:
    return load_canonical_bars()


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda scenario: scenario.name)
def test_parameter_study_pins_validated_canonical_btc_grid_outputs(
    scenario: ScenarioContract,
    canonical_bars: BarSeries,
) -> None:
    result = ParameterStudy(
        engine=_experiment_engine(),
        bars=canonical_bars,
        strategy=scenario.strategy,
    ).grid_search(
        parameters=scenario.parameters,
        constraint=scenario.constraint,
        objective=("returns.total_return", "max"),
    )

    assert result.candidate_count == scenario.candidate_count
    assert result.successful_count == scenario.candidate_count
    assert result.rejected_count == 0
    assert result.failed_count == 0
    records = result.to_records()
    assert len(records) == scenario.candidate_count
    json.dumps(records, allow_nan=False)

    expected = scenario.expected
    best = result.best()
    assert best.status == "success"
    assert dict(best.strategy_config) == expected.strategy_config
    assert dict(best.candidate_parameters) == expected.strategy_config
    assert best.metrics["returns.total_return"] == pytest.approx(expected.total_return)

    assert best.backtest is not None
    report = best.backtest.report
    assert report.run.strategy_config == dict(best.strategy_config)
    assert not hasattr(report.run, "strategy_parameters")
    assert report.returns.total_return == pytest.approx(expected.total_return)
    assert report.returns.final_equity == pytest.approx(expected.final_equity)
    assert report.risk.max_drawdown == pytest.approx(expected.max_drawdown)
    assert report.trades.closed_trade_count == expected.closed_trades
    assert report.trades.win_rate == pytest.approx(expected.win_rate)
    assert report.trades.profit_factor == pytest.approx(expected.profit_factor)


def _experiment_engine() -> BacktestEngine:
    return BacktestEngine(
        initial_cash=1_000_000.0,
        costs=CostConfig(tick_size=0.1, slippage_ticks=0.0, fee_rate=0.0),
    )
