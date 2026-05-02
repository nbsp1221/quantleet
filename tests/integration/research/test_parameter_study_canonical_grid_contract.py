from __future__ import annotations

import json
import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass

import pytest

from quantcraft.backtest import BacktestEngine
from quantcraft.data import BarSeries
from quantcraft.research import ParameterStudy, Strategy, ta
from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import BarEvent
from tests.support_backtest import load_canonical_bars

type ParameterGrid = dict[str, list[int]]
type StrategyFactory = Callable[[Mapping[str, object]], Strategy]
type Constraint = Callable[[Mapping[str, object]], bool]


@dataclass(frozen=True, slots=True)
class ExpectedBestRun:
    parameters: dict[str, int]
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
    factory: StrategyFactory
    candidate_count: int
    expected: ExpectedBestRun


class ExperimentSmaCross(Strategy):
    def __init__(self, *, fast: int, slow: int) -> None:
        super().__init__()
        self.fast_length = fast
        self.slow_length = slow

    @property
    def display_name(self) -> str:
        return "Experiment SMA Cross"

    def parameters(self) -> dict[str, object]:
        return {"fast": self.fast_length, "slow": self.slow_length}

    def init(self) -> None:
        self.fast = ta.sma(self.data.close, length=self.fast_length)
        self.slow = ta.sma(self.data.close, length=self.slow_length)

    def on_bar(self, bar: BarEvent) -> None:
        fast = self.fast[0]
        slow = self.slow[0]
        indicators_ready = math.isfinite(fast) and math.isfinite(slow)
        if indicators_ready and fast > slow and not self.position.is_open:
            self.buy(qty_percent=100.0, tag="entry")
        elif indicators_ready and fast < slow and self.position.is_open:
            self.sell(qty_percent=100.0, tag="exit")


class ExperimentRsiMeanReversion(Strategy):
    def __init__(self, *, length: int, lower: int, upper: int) -> None:
        super().__init__()
        self.length = length
        self.lower = lower
        self.upper = upper

    @property
    def display_name(self) -> str:
        return "Experiment RSI Mean Reversion"

    def parameters(self) -> dict[str, object]:
        return {"length": self.length, "lower": self.lower, "upper": self.upper}

    def init(self) -> None:
        self.rsi = ta.rsi(self.data.close, length=self.length)

    def on_bar(self, bar: BarEvent) -> None:
        value = self.rsi[0]
        if math.isfinite(value) and value < self.lower and not self.position.is_open:
            self.buy(qty_percent=100.0, tag="entry")
        elif math.isfinite(value) and value > self.upper and self.position.is_open:
            self.sell(qty_percent=100.0, tag="exit")


class ExperimentDonchianBreakout(Strategy):
    def __init__(self, *, entry: int, exit: int) -> None:
        super().__init__()
        self.entry = entry
        self.exit = exit

    @property
    def display_name(self) -> str:
        return "Experiment Donchian Breakout"

    def parameters(self) -> dict[str, object]:
        return {"entry": self.entry, "exit": self.exit}

    def on_bar(self, bar: BarEvent) -> None:
        if len(self.data.close) <= self.entry:
            return

        previous_highs = [self.data.high[index] for index in range(1, self.entry + 1)]
        previous_lows = [self.data.low[index] for index in range(1, self.exit + 1)]
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
        factory=lambda parameters: ExperimentSmaCross(
            fast=int(parameters["fast"]),
            slow=int(parameters["slow"]),
        ),
        candidate_count=6,
        expected=ExpectedBestRun(
            parameters={"fast": 32, "slow": 64},
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
        factory=lambda parameters: ExperimentRsiMeanReversion(
            length=int(parameters["length"]),
            lower=int(parameters["lower"]),
            upper=int(parameters["upper"]),
        ),
        candidate_count=12,
        expected=ExpectedBestRun(
            parameters={"length": 21, "lower": 30, "upper": 70},
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
        factory=lambda parameters: ExperimentDonchianBreakout(
            entry=int(parameters["entry"]),
            exit=int(parameters["exit"]),
        ),
        candidate_count=6,
        expected=ExpectedBestRun(
            parameters={"entry": 80, "exit": 20},
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
        strategy_factory=scenario.factory,
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
    assert dict(best.parameters) == expected.parameters
    assert best.metrics["returns.total_return"] == pytest.approx(expected.total_return)

    assert best.backtest is not None
    report = best.backtest.report
    assert report.run.strategy_parameters == dict(best.parameters)
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
