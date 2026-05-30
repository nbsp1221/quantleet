from __future__ import annotations

from quantleet.research import ParameterStudy
from tests.integration.research.support_parameter_studies import (
    ParameterizedRoundTripStrategy,
    crossing_bars,
    engine,
)


def test_canonical_small_grid_search_uses_real_backtest_engine() -> None:
    study = ParameterStudy(
        engine=engine(),
        bars=crossing_bars(),
        strategy=ParameterizedRoundTripStrategy,
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
    assert dict(best.strategy_config) == {"fast": 5, "slow": 10, "enabled": False}
    assert dict(best.candidate_parameters) == {"fast": 5, "slow": 10}
    assert dict(best.candidate_parameters) != dict(best.strategy_config)
    assert best.backtest.report.run.strategy_config == dict(best.strategy_config)
    assert not hasattr(best.backtest.report.run, "strategy_parameters")

    records = result.to_records()
    assert len(records) == 4
    assert records[0]["returns.total_return_state"] == "defined"
    assert records[2]["status"] == "rejected"


def test_strategy_class_constructs_once_per_admissible_candidate_with_fresh_instances() -> None:
    ParameterizedRoundTripStrategy.instances = []
    ParameterizedRoundTripStrategy.constructed_configs = []

    result = ParameterStudy(
        engine=engine(),
        bars=crossing_bars(),
        strategy=ParameterizedRoundTripStrategy,
    ).grid_search(
        parameters={"fast": [5, 20], "slow": [10, 30]},
        constraint=lambda parameters: parameters["fast"] < parameters["slow"],
    )

    assert result.successful_count == 3
    assert result.rejected_count == 1
    assert ParameterizedRoundTripStrategy.constructed_configs == [
        {"fast": 5, "slow": 10, "enabled": False},
        {"fast": 5, "slow": 30, "enabled": False},
        {"fast": 20, "slow": 30, "enabled": False},
    ]
    assert len(ParameterizedRoundTripStrategy.instances) == 3
    assert len({id(instance) for instance in ParameterizedRoundTripStrategy.instances}) == 3
