from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from quantleet.data import BarSeries
from quantleet.research import ParameterStudy
from quantleet.strategy import Strategy, StrategyConfig
from quantleet.trading.domain.events import BarEvent
from tests.integration.research.test_parameter_study_grid_search import crossing_bars, engine
from tests.unit.research.support_parameter_study import NoTradeStrategy


class FailureConfig(StrategyConfig):
    case: str = "ok"


class MixedFailureStrategy(Strategy[FailureConfig]):
    def __init__(self, config: FailureConfig | None = None) -> None:
        if config is not None and config.case == "construction":
            raise ValueError("construction exploded")
        super().__init__(config)

    def init(self) -> None:
        if self.config.case == "init":
            raise RuntimeError("init exploded")

    def on_bar(self, bar: BarEvent) -> None:
        return None


class RaisingInitStrategy(NoTradeStrategy):
    def init(self) -> None:
        raise RuntimeError("init exploded")


class RaisingOnBarStrategy(NoTradeStrategy):
    def on_bar(self, bar: BarEvent) -> None:
        raise RuntimeError("on_bar exploded")


def test_mixed_failures_continue_by_default() -> None:
    result = ParameterStudy(
        engine=engine(),
        bars=crossing_bars(),
        strategy=MixedFailureStrategy,
    ).grid_search(parameters={"case": ["ok", "construction", "init", "later"]})

    assert result.successful_count == 2
    assert result.failed_count == 2
    assert [(row.run_index, row.failure_stage, row.error_type) for row in result.failed()] == [
        (1, "strategy_construction", "ValueError"),
        (2, "backtest", "RuntimeError"),
    ]


def test_fail_fast_reraises_original_exception_with_stage_and_config_context() -> None:
    with pytest.raises(ValueError, match="construction exploded") as exc_info:
        ParameterStudy(
            engine=engine(),
            bars=crossing_bars(),
            strategy=MixedFailureStrategy,
        ).grid_search(parameters={"case": ["ok", "construction", "later"]}, fail_fast=True)

    assert any(note == "stage=strategy_construction" for note in exc_info.value.__notes__)
    assert any(
        "candidate_parameters={'case': 'construction'}" in note for note in exc_info.value.__notes__
    )
    assert any(
        "strategy_config={'case': 'construction'}" in note for note in exc_info.value.__notes__
    )


def test_backtest_on_bar_failures_are_backtest_failed_rows() -> None:
    result = ParameterStudy(
        engine=engine(),
        bars=crossing_bars(),
        strategy=RaisingOnBarStrategy,
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
            strategy=RaisingOnBarStrategy,
        ).grid_search(parameters={"x": [1]}, fail_fast=True)

    assert any(note == "stage=backtest" for note in exc_info.value.__notes__)
    assert any("'x': 1" in note for note in exc_info.value.__notes__)


def test_non_bool_constraint_fail_fast_raises_type_error_with_context() -> None:
    with pytest.raises(TypeError, match="constraint must return bool") as exc_info:
        ParameterStudy(
            engine=engine(),
            bars=crossing_bars(),
            strategy=NoTradeStrategy,
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
        config: object | None = None,
        bars: BarSeries,
        label: str | None = None,
    ) -> object:
        del strategy, config, bars, label
        return metric_extraction_failure_result()


def test_metric_extraction_failures_are_failed_rows_and_fail_fast_raises() -> None:
    result = ParameterStudy(
        engine=MetricExtractionFailingEngine(),
        bars=crossing_bars(),
        strategy=NoTradeStrategy,
    ).grid_search(parameters={"x": [1]})

    assert result.failed_count == 1
    assert result.failed()[0].failure_stage == "metric_extraction"

    with pytest.raises(RuntimeError, match="known metric extractor exploded") as exc_info:
        ParameterStudy(
            engine=MetricExtractionFailingEngine(),
            bars=crossing_bars(),
            strategy=NoTradeStrategy,
        ).grid_search(parameters={"x": [1]}, fail_fast=True)

    assert any(note == "stage=metric_extraction" for note in exc_info.value.__notes__)
