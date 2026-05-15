from __future__ import annotations

import json

from quantleet.research import WalkForwardStudy
from tests.unit.research.support_parameter_study import NoTradeStrategy, make_bars, make_engine


def test_fold_records_are_flat_with_nested_selected_config_and_metric_states() -> None:
    result = WalkForwardStudy(
        engine=make_engine(),
        bars=make_bars(closes=tuple(float(100 + index) for index in range(8))),
        strategy=NoTradeStrategy,
    ).run(
        parameters={"x": [1]},
        objective=("returns.total_return", "max"),
        train_size=4,
        test_size=2,
    )

    record = result.to_records()[0]

    assert record["fold_index"] == 0
    assert record["status"] == "success"
    assert record["selected_config"] == {
        "x": 1,
        "fast": 5,
        "slow": 20,
        "name": "alpha",
        "count": 3,
        "ratio": 0.5,
        "enabled": True,
        "maybe": None,
        "status": "reserved-looking",
    }
    assert "x" not in record
    assert "train.returns.total_return" in record
    assert record["train.returns.total_return_state"] == "defined"
    assert "test.returns.total_return" in record
    assert record["test.returns.total_return_state"] == "defined"
    json.dumps(result.to_records(), allow_nan=False)


def test_candidate_records_reuse_grid_search_records_with_fold_metadata() -> None:
    result = WalkForwardStudy(
        engine=make_engine(),
        bars=make_bars(closes=tuple(float(100 + index) for index in range(8))),
        strategy=NoTradeStrategy,
    ).run(
        parameters={"x": [1, 2]},
        objective=("returns.total_return", "max"),
        train_size=4,
        test_size=2,
    )

    candidate_records = result.to_candidate_records()

    assert {record["fold_index"] for record in candidate_records} == {0, 1}
    assert {"run_index", "candidate_parameters", "strategy_config"}.issubset(candidate_records[0])
    json.dumps(candidate_records, allow_nan=False)
