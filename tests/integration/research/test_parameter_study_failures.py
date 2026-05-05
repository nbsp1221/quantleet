from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from quantleet.data import BarSeries
from quantleet.research import ParameterStudy, Strategy
from quantleet.trading.domain.events import BarEvent
from tests.integration.research.test_parameter_study_grid_search import crossing_bars, engine
from tests.unit.research.support_parameter_study import NoTradeStrategy


class RaisingInitStrategy(NoTradeStrategy):
    def init(self) -> None:
        raise RuntimeError("init exploded")


class RaisingOnBarStrategy(NoTradeStrategy):
    def on_bar(self, bar: BarEvent) -> None:
        raise RuntimeError("on_bar exploded")


def test_mixed_failures_continue_by_default() -> None:
    def factory(parameters: Mapping[str, object]) -> Strategy:
        if parameters["case"] == "factory":
            raise ValueError("factory exploded")
        if parameters["case"] == "init":
            return RaisingInitStrategy(parameters)
        return NoTradeStrategy(parameters)

    result = ParameterStudy(
        engine=engine(),
        bars=crossing_bars(),
        strategy_factory=factory,
    ).grid_search(parameters={"case": ["ok", "factory", "init", "later"]})

    assert result.successful_count == 2
    assert result.failed_count == 2
    assert [(row.run_index, row.failure_stage, row.error_type) for row in result.failed()] == [
        (1, "strategy_factory", "ValueError"),
        (2, "backtest", "RuntimeError"),
    ]


def test_fail_fast_reraises_original_exception_with_stage_and_parameters() -> None:
    def factory(parameters: Mapping[str, object]) -> Strategy:
        if parameters["case"] == "factory":
            raise ValueError("factory exploded")
        return NoTradeStrategy(parameters)

    with pytest.raises(ValueError, match="factory exploded") as exc_info:
        ParameterStudy(
            engine=engine(),
            bars=crossing_bars(),
            strategy_factory=factory,
        ).grid_search(parameters={"case": ["ok", "factory", "later"]}, fail_fast=True)

    assert any(note == "stage=strategy_factory" for note in exc_info.value.__notes__)
    assert any("'case': 'factory'" in note for note in exc_info.value.__notes__)


def test_backtest_on_bar_failures_are_backtest_failed_rows() -> None:
    result = ParameterStudy(
        engine=engine(),
        bars=crossing_bars(),
        strategy_factory=lambda parameters: RaisingOnBarStrategy(parameters),
    ).grid_search(parameters={"x": [1]})

    assert result.failed_count == 1
    failed = result.failed()[0]
    assert failed.failure_stage == "backtest"
    assert failed.error_type == "RuntimeError"
    assert failed.error_message == "on_bar exploded"
    assert failed.backtest is None


def test_backtest_fail_fast_reraises_original_exception_with_context() -> None:
    with pytest.raises(RuntimeError, match="on_bar exploded") as exc_info:
        ParameterStudy(
            engine=engine(),
            bars=crossing_bars(),
            strategy_factory=lambda parameters: RaisingOnBarStrategy(parameters),
        ).grid_search(parameters={"x": [1]}, fail_fast=True)

    assert any(note == "stage=backtest" for note in exc_info.value.__notes__)
    assert any("'x': 1" in note for note in exc_info.value.__notes__)


def test_non_bool_constraint_fail_fast_raises_type_error_with_context() -> None:
    with pytest.raises(TypeError, match="constraint must return bool") as exc_info:
        ParameterStudy(
            engine=engine(),
            bars=crossing_bars(),
            strategy_factory=lambda parameters: NoTradeStrategy(parameters),
        ).grid_search(
            parameters={"x": [1]},
            constraint=lambda parameters: "yes",  # type: ignore[return-value]
            fail_fast=True,
        )

    assert any(note == "stage=constraint" for note in exc_info.value.__notes__)


class RaisingRisk:
    @property
    def max_drawdown(self) -> float:
        raise RuntimeError("known metric extractor exploded")


def metric_extraction_failure_result() -> object:
    return SimpleNamespace(
        report=SimpleNamespace(
            returns=SimpleNamespace(final_equity=1_000.0, total_return=0.0),
            risk=RaisingRisk(),
            trades=SimpleNamespace(
                closed_trade_count=0,
                win_rate=None,
                profit_factor=None,
            ),
            costs=SimpleNamespace(total_fees=0.0),
            exposure=SimpleNamespace(exposure_ratio=0.0),
            execution=SimpleNamespace(order_rejection_count=0),
            run=SimpleNamespace(
                run_label="grid-search-0",
                strategy_class_name="NoTradeStrategy",
                strategy_display_name=None,
                symbol="TEST",
                timeframe="1m",
                initial_cash=1_000.0,
            ),
        )
    )


@dataclass
class MetricExtractionFailingEngine:
    def run(
        self,
        *,
        strategy: object,
        bars: BarSeries,
        label: str | None = None,
    ) -> object:
        del strategy, bars, label
        return metric_extraction_failure_result()


def test_metric_extraction_failures_are_failed_rows_and_fail_fast_raises() -> None:
    result = ParameterStudy(
        engine=MetricExtractionFailingEngine(),
        bars=crossing_bars(),
        strategy_factory=lambda parameters: NoTradeStrategy(parameters),
    ).grid_search(parameters={"x": [1]})

    assert result.failed_count == 1
    assert result.failed()[0].failure_stage == "metric_extraction"

    with pytest.raises(RuntimeError, match="known metric extractor exploded") as exc_info:
        ParameterStudy(
            engine=MetricExtractionFailingEngine(),
            bars=crossing_bars(),
            strategy_factory=lambda parameters: NoTradeStrategy(parameters),
        ).grid_search(parameters={"x": [1]}, fail_fast=True)

    assert any(note == "stage=metric_extraction" for note in exc_info.value.__notes__)
