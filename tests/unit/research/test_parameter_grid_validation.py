from __future__ import annotations

import math
from collections.abc import Mapping
from enum import IntEnum
from typing import Any

import pytest

from quantleet.research import ParameterStudy
from quantleet.strategy import Strategy, StrategyConfig, StrategyConfigValidationError
from quantleet.trading.domain.events import BarEvent
from tests.unit.research.support_parameter_study import (
    CountingEngine,
    NoTradeStrategy,
    make_bars,
)


class ParameterEnum(IntEnum):
    FAST = 5


class SmaConfig(StrategyConfig):
    fast: int = 10
    slow: int = 20

    def validate(self) -> None:
        if self.fast >= self.slow:
            raise StrategyConfigValidationError("fast must be less than slow")


class SmaStrategy(Strategy[SmaConfig]):
    def on_bar(self, bar: BarEvent) -> None:
        return None


def make_study(*, engine: CountingEngine | None = None) -> ParameterStudy:
    return ParameterStudy(
        engine=engine or CountingEngine(),
        bars=make_bars(),
        strategy=NoTradeStrategy,
    )


def test_parameter_grid_enumerates_mapping_order_then_value_order() -> None:
    result = make_study().grid_search(
        parameters={"fast": [5, 10], "slow": [20, 50]},
        objective=("returns.total_return", "max"),
    )

    assert [row.run_index for row in result.rows] == [0, 1, 2, 3]
    assert [dict(row.candidate_parameters) for row in result.rows] == [
        {"fast": 5, "slow": 20},
        {"fast": 5, "slow": 50},
        {"fast": 10, "slow": 20},
        {"fast": 10, "slow": 50},
    ]
    assert [dict(row.strategy_config) for row in result.rows] == [
        {
            "x": 1,
            "fast": 5,
            "slow": 20,
            "name": "alpha",
            "count": 3,
            "ratio": 0.5,
            "enabled": True,
            "maybe": None,
            "status": "reserved-looking",
        },
        {
            "x": 1,
            "fast": 5,
            "slow": 50,
            "name": "alpha",
            "count": 3,
            "ratio": 0.5,
            "enabled": True,
            "maybe": None,
            "status": "reserved-looking",
        },
        {
            "x": 1,
            "fast": 10,
            "slow": 20,
            "name": "alpha",
            "count": 3,
            "ratio": 0.5,
            "enabled": True,
            "maybe": None,
            "status": "reserved-looking",
        },
        {
            "x": 1,
            "fast": 10,
            "slow": 50,
            "name": "alpha",
            "count": 3,
            "ratio": 0.5,
            "enabled": True,
            "maybe": None,
            "status": "reserved-looking",
        },
    ]
    assert result.candidate_count == 4
    assert result.successful_count == 4


@pytest.mark.parametrize(
    ("parameters", "error_type", "match"),
    [
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


def test_empty_parameter_grid_runs_default_config_once() -> None:
    result = make_study().grid_search(parameters={})

    assert result.candidate_count == 1
    assert result.successful_count == 1
    assert result.rows[0].candidate_parameters == {}
    assert dict(result.rows[0].strategy_config)["x"] == 1


def test_unknown_parameter_key_fails_before_running() -> None:
    engine = CountingEngine()

    with pytest.raises(StrategyConfigValidationError, match="unknown"):
        make_study(engine=engine).grid_search(parameters={"missing": [1]})

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

    assert record["candidate_parameters"] == {
        "name": "alpha",
        "count": 3,
        "ratio": 0.5,
        "enabled": True,
        "maybe": None,
        "status": "reserved-looking",
    }
    assert record["strategy_config"] == {
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
    assert "parameters" not in record
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
    assert [dict(row.candidate_parameters) for row in result.rejected()] == [
        {"fast": 20, "slow": 10}
    ]
    assert result.rejected()[0].rejection_stage == "constraint"
    assert [call["config"].to_mapping() for call in engine.calls] == [
        {
            "x": 1,
            "fast": 5,
            "slow": 10,
            "name": "alpha",
            "count": 3,
            "ratio": 0.5,
            "enabled": True,
            "maybe": None,
            "status": "reserved-looking",
        }
    ]


def test_strategy_config_validation_rejections_are_rows_without_running() -> None:
    engine = CountingEngine()

    result = ParameterStudy(
        engine=engine,
        bars=make_bars(),
        strategy=SmaStrategy,
    ).grid_search(parameters={"fast": [5, 25]})

    assert result.candidate_count == 2
    assert result.successful_count == 1
    assert result.rejected_count == 1
    assert len(engine.calls) == 1
    rejected = result.rejected()[0]
    assert rejected.rejection_stage == "strategy_config"
    assert rejected.error_type == "StrategyConfigValidationError"
    assert rejected.error_message == "fast must be less than slow"
    assert dict(rejected.candidate_parameters) == {"fast": 25}
    assert dict(rejected.strategy_config) == {"fast": 25, "slow": 20}


def test_strategy_config_validation_happens_before_constraint() -> None:
    seen_configs: list[dict[str, object]] = []

    result = ParameterStudy(
        engine=CountingEngine(),
        bars=make_bars(),
        strategy=SmaStrategy,
    ).grid_search(
        parameters={"fast": [25]},
        constraint=lambda config: seen_configs.append(dict(config)) is None,
    )

    assert seen_configs == []
    assert result.rejected_count == 1
    assert result.rejected()[0].rejection_stage == "strategy_config"


def test_strategy_config_type_validation_rejections_are_rows_without_running() -> None:
    engine = CountingEngine()

    result = ParameterStudy(
        engine=engine,
        bars=make_bars(),
        strategy=SmaStrategy,
    ).grid_search(parameters={"fast": ["bad"]})

    assert engine.calls == []
    assert result.candidate_count == 1
    assert result.rejected_count == 1
    rejected = result.rejected()[0]
    assert rejected.rejection_stage == "strategy_config"
    assert rejected.error_type == "StrategyConfigValidationError"
    assert rejected.error_message == "fast expects int"
    assert dict(rejected.candidate_parameters) == {"fast": "bad"}
    assert dict(rejected.strategy_config) == {"fast": "bad", "slow": 20}


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
    assert dict(failed.candidate_parameters) == {"x": 2}

    with pytest.raises(RuntimeError, match="bad constraint") as exc_info:
        make_study().grid_search(
            parameters={"x": [1, 2, 3]},
            constraint=constraint,
            fail_fast=True,
        )

    assert any("stage=constraint" in note for note in exc_info.value.__notes__)
    assert any("candidate_parameters={'x': 2}" in note for note in exc_info.value.__notes__)
    assert any("'slow': 20" in note for note in exc_info.value.__notes__)


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

    assert seen == [
        {
            "x": 1,
            "fast": 5,
            "slow": 20,
            "name": "alpha",
            "count": 3,
            "ratio": 0.5,
            "enabled": True,
            "maybe": None,
            "status": "reserved-looking",
        },
        {
            "x": 2,
            "fast": 5,
            "slow": 20,
            "name": "alpha",
            "count": 3,
            "ratio": 0.5,
            "enabled": True,
            "maybe": None,
            "status": "reserved-looking",
        },
    ]
    assert [dict(row.candidate_parameters) for row in result.rows] == [{"x": 1}, {"x": 2}]
