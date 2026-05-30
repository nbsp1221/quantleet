from __future__ import annotations

import json

from quantleet.research import WalkForwardStudy
from tests.integration.research.support_parameter_studies import (
    WfaRoundTripStrategy,
    engine,
    walk_forward_bars,
)


def test_real_wfa_records_are_portable_and_joinable() -> None:
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

    fold_records = result.to_records()
    candidate_records = result.to_candidate_records()

    assert len(fold_records) == result.fold_count
    assert {record["fold_index"] for record in fold_records} == {0, 1}
    assert {record["fold_index"] for record in candidate_records} == {0, 1}
    assert "selected_config" in fold_records[0]
    assert "candidate_parameters" in candidate_records[0]
    json.dumps(fold_records, allow_nan=False)
    json.dumps(candidate_records, allow_nan=False)
