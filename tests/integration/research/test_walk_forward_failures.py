from __future__ import annotations

from dataclasses import dataclass

from quantleet.backtest import BacktestResult, BacktestStrategyConstructionError
from quantleet.data import BarSeries
from quantleet.research import WalkForwardStudy
from quantleet.strategy import Strategy, StrategyConfig
from tests.integration.research.support_parameter_studies import (
    WfaRoundTripStrategy,
    engine,
    walk_forward_bars,
)


@dataclass
class OneSelectedTestFailureEngine:
    calls: int = 0

    def run(
        self,
        *,
        strategy: type[Strategy[StrategyConfig]],
        config: StrategyConfig | None = None,
        bars: BarSeries | None = None,
        source: object | None = None,
        label: str | None = None,
    ) -> BacktestResult:
        self.calls += 1
        if bars is not None and len(bars.rows) == 3 and self.calls == 2:
            raise RuntimeError("selected test failed")
        return engine().run(strategy=strategy, config=config, bars=bars, label=label)


@dataclass
class SelectedConstructionFailureEngine:
    calls: int = 0

    def run(
        self,
        *,
        strategy: type[Strategy[StrategyConfig]],
        config: StrategyConfig | None = None,
        bars: BarSeries | None = None,
        source: object | None = None,
        label: str | None = None,
    ) -> BacktestResult:
        self.calls += 1
        if bars is not None and len(bars.rows) == 3 and self.calls == 2:
            raise BacktestStrategyConstructionError(strategy.__name__, RuntimeError("bad test"))
        return engine().run(strategy=strategy, config=config, bars=bars, label=label)


def test_selected_test_failure_is_recorded_and_later_folds_continue() -> None:
    result = WalkForwardStudy(
        engine=OneSelectedTestFailureEngine(),
        bars=walk_forward_bars(),
        strategy=WfaRoundTripStrategy,
    ).run(
        parameters={"fast": [2], "slow": [3]},
        objective=("returns.total_return", "max"),
        train_size=6,
        test_size=3,
    )

    assert [fold.status for fold in result.folds] == ["failed", "success"]
    assert result.folds[0].failure_stage == "test_backtest"
    assert result.folds[0].selected_test_result is None
    assert result.folds[1].selected_test_result is not None
    assert result.oos_summary.successful_fold_count == 1


def test_selected_test_construction_failure_uses_public_failure_stage() -> None:
    result = WalkForwardStudy(
        engine=SelectedConstructionFailureEngine(),
        bars=walk_forward_bars(),
        strategy=WfaRoundTripStrategy,
    ).run(
        parameters={"fast": [2], "slow": [3]},
        objective=("returns.total_return", "max"),
        train_size=6,
        test_size=3,
    )

    assert result.folds[0].failure_stage == "test_strategy_construction"
    assert result.to_records()[0]["failure_stage"] == "test_strategy_construction"
    assert result.to_records()[0]["test_status"] == "failed"


def test_rejected_train_candidate_does_not_fail_fold_when_another_row_is_eligible() -> None:
    result = WalkForwardStudy(
        engine=engine(),
        bars=walk_forward_bars(),
        strategy=WfaRoundTripStrategy,
    ).run(
        parameters={"fast": [2, 5], "slow": [3]},
        objective=("returns.total_return", "max"),
        train_size=6,
        test_size=3,
    )

    assert result.successful_fold_count == 2
    assert all(fold.train_result is not None for fold in result.folds)
    assert all(
        fold.train_result is not None and fold.train_result.rejected_count == 1
        for fold in result.folds
    )
    assert all(fold.selected_test_result is not None for fold in result.folds)


def test_no_eligible_training_row_does_not_fabricate_test_result() -> None:
    result = WalkForwardStudy(
        engine=engine(),
        bars=walk_forward_bars(),
        strategy=WfaRoundTripStrategy,
    ).run(
        parameters={"fast": [2], "slow": [3]},
        objective=("returns.total_return", "max"),
        constraint=lambda config: False,
        train_size=6,
        test_size=3,
    )

    assert all(fold.status == "failed" for fold in result.folds)
    assert all(fold.failure_stage == "selection" for fold in result.folds)
    assert all(fold.selected_test_result is None for fold in result.folds)
    assert result.oos_summary.successful_fold_count == 0


def test_failed_fold_records_include_failure_metadata() -> None:
    result = WalkForwardStudy(
        engine=OneSelectedTestFailureEngine(),
        bars=walk_forward_bars(),
        strategy=WfaRoundTripStrategy,
    ).run(
        parameters={"fast": [2], "slow": [3]},
        objective=("returns.total_return", "max"),
        train_size=6,
        test_size=3,
    )

    failed_record = result.to_records()[0]

    assert failed_record["status"] == "failed"
    assert failed_record["test_status"] == "failed"
    assert failed_record["failure_stage"] == "test_backtest"
    assert failed_record["error_type"] == "RuntimeError"
    assert failed_record["error_message"] == "selected test failed"
