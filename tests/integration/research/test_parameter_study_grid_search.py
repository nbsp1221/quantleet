from __future__ import annotations

from collections.abc import Mapping

from quantleet.backtest import BacktestEngine
from quantleet.data import BarSeries, TimeBar
from quantleet.research import ParameterStudy, Strategy
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent


def crossing_bars() -> BarSeries:
    closes = (100.0, 101.0, 99.0, 104.0, 106.0, 103.0)
    return BarSeries(
        symbol="TEST",
        timeframe="1m",
        bar_type="time",
        rows=tuple(
            TimeBar(
                timestamp=(index + 1) * 60,
                open=close,
                high=close + 1.0,
                low=close - 1.0,
                close=close,
                volume=1.0,
            )
            for index, close in enumerate(closes)
        ),
    )


def engine() -> BacktestEngine:
    return BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )


class ParameterizedRoundTripStrategy(Strategy):
    def __init__(self, *, fast: int, slow: int, instance_ids: list[int] | None = None) -> None:
        super().__init__()
        self._fast = fast
        self._slow = slow
        self._instance_ids = instance_ids
        if instance_ids is not None:
            instance_ids.append(id(self))

    @property
    def display_name(self) -> str:
        return "Parameterized Round Trip"

    def parameters(self) -> dict[str, object]:
        return {"fast": self._fast, "slow": self._slow}

    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar: BarEvent) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self._seen_bars >= 2 and self.position.is_open:
            self.sell(quantity=1.0, tag="exit")


def test_canonical_small_grid_search_uses_real_backtest_engine() -> None:
    study = ParameterStudy(
        engine=engine(),
        bars=crossing_bars(),
        strategy_factory=lambda parameters: ParameterizedRoundTripStrategy(
            fast=int(parameters["fast"]),
            slow=int(parameters["slow"]),
        ),
    )

    result = study.grid_search(
        parameters={"fast": [5, 10], "slow": [10, 20]},
        constraint=lambda parameters: parameters["fast"] < parameters["slow"],
        objective=("returns.total_return", "max"),
    )

    assert result.candidate_count == 4
    assert result.rejected_count == 1
    assert result.successful_count == 3
    assert result.failed_count == 0
    assert [row.run_index for row in result.rows] == [0, 1, 2, 3]

    best = result.best()
    assert best.status == "success"
    assert best.backtest is not None
    assert best.backtest.report.run.run_label == f"grid-search-{best.run_index}"
    assert best.backtest.report.run.strategy_display_name == "Parameterized Round Trip"
    assert best.backtest.report.run.strategy_parameters == dict(best.parameters)

    records = result.to_records()
    assert len(records) == 4
    assert records[0]["returns.total_return_state"] == "defined"
    assert records[2]["status"] == "rejected"


def test_strategy_factory_runs_once_per_admissible_candidate_with_fresh_instances() -> None:
    factory_inputs: list[dict[str, object]] = []
    instance_ids: list[int] = []

    def factory(parameters: Mapping[str, object]) -> Strategy:
        factory_inputs.append(dict(parameters))
        return ParameterizedRoundTripStrategy(
            fast=int(parameters["fast"]),
            slow=int(parameters["slow"]),
            instance_ids=instance_ids,
        )

    result = ParameterStudy(
        engine=engine(),
        bars=crossing_bars(),
        strategy_factory=factory,
    ).grid_search(
        parameters={"fast": [5, 20], "slow": [10, 30]},
        constraint=lambda parameters: parameters["fast"] < parameters["slow"],
    )

    assert result.successful_count == 3
    assert result.rejected_count == 1
    assert factory_inputs == [
        {"fast": 5, "slow": 10},
        {"fast": 5, "slow": 30},
        {"fast": 20, "slow": 30},
    ]
    assert len(instance_ids) == len(set(instance_ids)) == 3
