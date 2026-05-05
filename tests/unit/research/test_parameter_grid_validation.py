from __future__ import annotations

import math
from collections.abc import Mapping
from enum import IntEnum
from typing import Any

import pytest

from quantleet.research import ParameterStudy
from tests.unit.research.support_parameter_study import (
    CountingEngine,
    NoTradeStrategy,
    make_bars,
)


class ParameterEnum(IntEnum):
    FAST = 5


def make_study(*, engine: CountingEngine | None = None) -> ParameterStudy:
    return ParameterStudy(
        engine=engine or CountingEngine(),
        bars=make_bars(),
        strategy_factory=lambda parameters: NoTradeStrategy(dict(parameters)),
    )


def test_parameter_grid_enumerates_mapping_order_then_value_order() -> None:
    result = make_study().grid_search(
        parameters={"fast": [5, 10], "slow": [20, 50]},
        objective=("returns.total_return", "max"),
    )

    assert [row.run_index for row in result.rows] == [0, 1, 2, 3]
    assert [dict(row.parameters) for row in result.rows] == [
        {"fast": 5, "slow": 20},
        {"fast": 5, "slow": 50},
        {"fast": 10, "slow": 20},
        {"fast": 10, "slow": 50},
    ]
    assert result.candidate_count == 4
    assert result.successful_count == 4


@pytest.mark.parametrize(
    ("parameters", "error_type", "match"),
    [
        ({}, ValueError, "parameters"),
        ({1: [5]}, TypeError, "parameter name"),
        ({"": [5]}, ValueError, "parameter name"),
        ({"fast": []}, ValueError, "fast"),
        ({"fast": {5, 10}}, TypeError, "ordered"),
        ({"fast": [5, 5]}, ValueError, "duplicate"),
        ({"fast": [object()]}, TypeError, "fast"),
        ({"fast": [lambda: 5]}, TypeError, "fast"),
        ({"fast": [[5]]}, TypeError, "fast"),
        ({"fast": [ParameterEnum.FAST]}, TypeError, "fast"),
        ({"fast": [math.nan]}, ValueError, "finite"),
        ({"fast": [math.inf]}, ValueError, "finite"),
    ],
)
def test_invalid_parameter_grids_fail_before_running(
    parameters: Any,
    error_type: type[Exception],
    match: str,
) -> None:
    engine = CountingEngine()

    with pytest.raises(error_type, match=match):
        make_study(engine=engine).grid_search(parameters=parameters)

    assert engine.calls == []


def test_supported_json_scalar_parameter_values_are_preserved_in_records() -> None:
    result = make_study().grid_search(
        parameters={
            "name": ["alpha"],
            "count": [3],
            "ratio": [0.5],
            "enabled": [True],
            "maybe": [None],
            "status": ["reserved-looking"],
        },
    )

    record = result.to_records()[0]

    assert record["parameters"] == {
        "name": "alpha",
        "count": 3,
        "ratio": 0.5,
        "enabled": True,
        "maybe": None,
        "status": "reserved-looking",
    }
    assert record["status"] == "success"


def test_raw_candidate_limit_is_checked_before_constraints_or_runs() -> None:
    engine = CountingEngine()

    with pytest.raises(ValueError, match="1001.*1000"):
        make_study(engine=engine).grid_search(
            parameters={"x": list(range(1001))},
            constraint=lambda parameters: False,
        )

    assert engine.calls == []


def test_raw_candidate_limit_accepts_explicit_override_and_none() -> None:
    result = make_study().grid_search(
        parameters={"x": list(range(1001))},
        constraint=lambda parameters: False,
        max_candidates=None,
    )

    assert result.candidate_count == 1001
    assert result.rejected_count == 1001

    result = make_study().grid_search(
        parameters={"x": list(range(1001))},
        constraint=lambda parameters: False,
        max_candidates=1001,
    )

    assert result.candidate_count == 1001
    assert result.rejected_count == 1001


@pytest.mark.parametrize("max_candidates", [True, False, 1.5, "1000"])
def test_invalid_max_candidates_types_fail(max_candidates: object) -> None:
    with pytest.raises(TypeError, match="max_candidates"):
        make_study().grid_search(parameters={"x": [1]}, max_candidates=max_candidates)  # type: ignore[arg-type]


@pytest.mark.parametrize("max_candidates", [0, -1])
def test_invalid_max_candidates_values_fail(max_candidates: int) -> None:
    with pytest.raises(ValueError, match="max_candidates"):
        make_study().grid_search(parameters={"x": [1]}, max_candidates=max_candidates)


def test_constraint_rejections_are_rows_not_failures() -> None:
    engine = CountingEngine()

    result = make_study(engine=engine).grid_search(
        parameters={"fast": [5, 20], "slow": [10]},
        constraint=lambda parameters: parameters["fast"] < parameters["slow"],
    )

    assert result.candidate_count == 2
    assert result.successful_count == 1
    assert result.rejected_count == 1
    assert result.failed_count == 0
    assert [dict(row.parameters) for row in result.rejected()] == [{"fast": 20, "slow": 10}]
    assert [call["strategy"].parameters() for call in engine.calls] == [{"fast": 5, "slow": 10}]


def test_constraint_exceptions_continue_by_default_and_fail_fast_raises() -> None:
    def constraint(parameters: Mapping[str, object]) -> bool:
        if parameters["x"] == 2:
            raise RuntimeError("bad constraint")
        return True

    result = make_study().grid_search(parameters={"x": [1, 2, 3]}, constraint=constraint)

    assert result.successful_count == 2
    assert result.failed_count == 1
    failed = result.failed()[0]
    assert failed.failure_stage == "constraint"
    assert failed.error_type == "RuntimeError"
    assert failed.error_message == "bad constraint"
    assert dict(failed.parameters) == {"x": 2}

    with pytest.raises(RuntimeError, match="bad constraint") as exc_info:
        make_study().grid_search(
            parameters={"x": [1, 2, 3]},
            constraint=constraint,
            fail_fast=True,
        )

    assert any("stage=constraint" in note for note in exc_info.value.__notes__)


@pytest.mark.parametrize("constraint_result", [1, 0, None, "yes"])
def test_constraint_must_return_bool(constraint_result: object) -> None:
    result = make_study().grid_search(
        parameters={"x": [1]},
        constraint=lambda parameters: constraint_result,  # type: ignore[return-value]
    )

    assert result.failed_count == 1
    assert result.failed()[0].failure_stage == "constraint"
    assert result.failed()[0].error_type == "TypeError"


def test_callbacks_cannot_mutate_stored_or_later_parameter_identity() -> None:
    seen: list[dict[str, object]] = []

    def constraint(parameters: Mapping[str, object]) -> bool:
        seen.append(dict(parameters))
        with pytest.raises(TypeError):
            parameters["x"] = 99  # type: ignore[index]
        return True

    result = make_study().grid_search(parameters={"x": [1, 2]}, constraint=constraint)

    assert seen == [{"x": 1}, {"x": 2}]
    assert [dict(row.parameters) for row in result.rows] == [{"x": 1}, {"x": 2}]
