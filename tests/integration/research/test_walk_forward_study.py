from __future__ import annotations

from quantleet.research import GridSearchResult, WalkForwardStudy
from tests.integration.research.support_parameter_studies import (
    WfaRoundTripStrategy,
    engine,
    walk_forward_bars,
)


def test_canonical_rolling_wfa_workflow_composes_real_public_contracts() -> None:
    WfaRoundTripStrategy.constructed_count = 0
    WfaRoundTripStrategy.instance_numbers = []
    WfaRoundTripStrategy.constructed_configs = []

    result = WalkForwardStudy(
        engine=engine(),
        bars=walk_forward_bars(),
        strategy=WfaRoundTripStrategy,
    ).run(
        parameters={"fast": [2, 3], "slow": [3, 5]},
        objective=("returns.total_return", "max"),
        constraint=lambda config: config["fast"] < config["slow"],
        train_size=6,
        test_size=3,
    )

    assert result.fold_count == 2
    assert result.successful_fold_count == 2
    assert all(isinstance(fold.train_result, GridSearchResult) for fold in result.folds)
    assert all(fold.selected_test_result is not None for fold in result.folds)
    assert all(fold.selected_config is not None for fold in result.folds)
    assert all(
        fold.selected_test_result is not None
        and fold.selected_test_result.report.run.strategy_config == dict(fold.selected_config or {})
        for fold in result.folds
    )
    assert len(WfaRoundTripStrategy.constructed_configs) > result.execution_scale.fold_count
    assert all(fold.selected_test_result is not None for fold in result.folds)
    assert result.to_records()[0]["selected_config"] == dict(result.folds[0].selected_config or {})


def test_wfa_selection_uses_train_result_and_selected_test_config_snapshot() -> None:
    result = WalkForwardStudy(
        engine=engine(),
        bars=walk_forward_bars(),
        strategy=WfaRoundTripStrategy,
    ).run(
        parameters={"fast": [2, 3], "slow": [3, 5]},
        objective=("returns.total_return", "max"),
        train_size=6,
        test_size=3,
    )

    first_fold = result.folds[0]

    assert first_fold.selected_train_row is not None
    assert first_fold.selected_config == first_fold.selected_train_row.strategy_config
    assert first_fold.selected_test_result is not None
    assert first_fold.selected_test_result.report.run.strategy_config == dict(
        first_fold.selected_config or {}
    )
