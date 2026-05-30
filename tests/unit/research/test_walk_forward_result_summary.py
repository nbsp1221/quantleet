from __future__ import annotations

from quantleet.research import WalkForwardStudy
from tests.integration.research.support_parameter_studies import (
    WfaRoundTripStrategy,
    walk_forward_bars,
)
from tests.integration.research.test_walk_forward_failures import OneSelectedTestFailureEngine
from tests.unit.research.support_parameter_study import NoTradeStrategy, make_bars, make_engine


def test_oos_summary_uses_independent_successful_test_folds_only() -> None:
    result = WalkForwardStudy(
        engine=make_engine(),
        bars=make_bars(closes=tuple(float(100 + index) for index in range(10))),
        strategy=NoTradeStrategy,
    ).run(
        parameters={"x": [1]},
        objective=("returns.total_return", "max"),
        train_size=4,
        test_size=2,
    )

    assert result.oos_summary.fold_count == 3
    assert result.oos_summary.successful_fold_count == 3
    assert result.oos_summary.failed_fold_count == 0
    assert result.oos_summary.failure_rate == 0.0
    assert result.oos_summary.objective_mean == 0.0
    assert result.oos_summary.objective_median == 0.0
    assert result.oos_summary.objective_min == 0.0
    assert result.oos_summary.objective_max == 0.0
    assert result.oos_summary.positive_fold_ratio == 0.0
    assert result.oos_summary.metric_summaries["returns.total_return"] == {
        "count": 3,
        "mean": 0.0,
        "median": 0.0,
        "min": 0.0,
        "max": 0.0,
    }
    assert result.oos_summary.metric_state_counts["trades.win_rate"] == {"undefined": 3}
    assert not hasattr(result.oos_summary, "equity_curve")
    assert not hasattr(result.oos_summary, "final_equity")
    assert not hasattr(result.oos_summary, "aggregate_total_return")


def test_oos_summary_excludes_failed_folds_from_numeric_aggregates() -> None:
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

    assert result.oos_summary.fold_count == 2
    assert result.oos_summary.successful_fold_count == 1
    assert result.oos_summary.failed_fold_count == 1
    assert result.oos_summary.objective_metric_state_counts == {"defined": 1}
    assert result.oos_summary.metric_summaries["returns.total_return"]["count"] == 1
    assert result.oos_summary.objective_mean == result.folds[1].test_metrics["returns.total_return"]
