from __future__ import annotations

import inspect

import pytest

from quantleet.research import GridSearchResult, GridSearchRow, ParameterStudy
from tests.unit.research.support_parameter_study import (
    CountingEngine,
    NoTradeStrategy,
    make_bars,
)


def test_public_import_surface_exposes_parameter_study_types() -> None:
    assert ParameterStudy is not None
    assert GridSearchResult is not None
    assert GridSearchRow is not None


def test_parameter_study_requires_materialized_bars_and_callable_factory() -> None:
    engine = CountingEngine()
    study = ParameterStudy(
        engine=engine,
        bars=make_bars(),
        strategy_factory=lambda parameters: NoTradeStrategy(parameters),
    )

    assert study.grid_search(parameters={"x": [1]}).successful_count == 1

    with pytest.raises(TypeError, match="BarSeries"):
        ParameterStudy(
            engine=engine,
            bars=object(),
            strategy_factory=lambda parameters: NoTradeStrategy(parameters),
        )

    with pytest.raises(TypeError, match="strategy_factory"):
        ParameterStudy(engine=engine, bars=make_bars(), strategy_factory=object())


def test_beta_public_signatures_do_not_accept_deferred_controls() -> None:
    study_signature = inspect.signature(ParameterStudy)
    search_signature = inspect.signature(ParameterStudy.grid_search)

    assert "source" not in study_signature.parameters
    assert "source" not in search_signature.parameters
    for deferred_name in ("n_jobs", "workers", "parallel", "executor"):
        assert deferred_name not in search_signature.parameters

    study = ParameterStudy(
        engine=CountingEngine(),
        bars=make_bars(),
        strategy_factory=lambda parameters: NoTradeStrategy(parameters),
    )

    with pytest.raises(TypeError):
        study.grid_search(parameters={"x": [1]}, source=object())  # type: ignore[call-arg]


@pytest.mark.parametrize(
    "objective",
    [
        ("equity.final", "max"),
        ("returns.total_return", "max"),
        ("risk.max_drawdown", "min"),
        ("trades.closed_count", "max"),
        ("trades.win_rate", "max"),
        ("risk.sharpe_ratio", "max"),
        ("trades.profit_factor", "max"),
        ("costs.total_fees", "min"),
        ("exposure.ratio", "max"),
        ("execution.order_rejection_count", "min"),
    ],
)
def test_all_beta_objective_paths_are_accepted(objective: tuple[str, str]) -> None:
    result = ParameterStudy(
        engine=CountingEngine(),
        bars=make_bars(),
        strategy_factory=lambda parameters: NoTradeStrategy(parameters),
    ).grid_search(parameters={"x": [1]}, objective=objective)

    assert result.objective == objective


@pytest.mark.parametrize(
    ("objective", "error_type", "match"),
    [
        (("returns.total_return", "largest"), ValueError, "direction"),
        (("unknown.metric", "max"), ValueError, "objective"),
        (["returns.total_return", "max"], TypeError, "objective"),
        (lambda row: 1.0, TypeError, "objective"),
        ((("returns.total_return", "max"), ("risk.max_drawdown", "min")), TypeError, "objective"),
    ],
)
def test_invalid_objectives_fail_before_any_backtest(
    objective: object,
    error_type: type[Exception],
    match: str,
) -> None:
    engine = CountingEngine()

    with pytest.raises(error_type, match=match):
        ParameterStudy(
            engine=engine,
            bars=make_bars(),
            strategy_factory=lambda parameters: NoTradeStrategy(parameters),
        ).grid_search(parameters={"x": [1]}, objective=objective)  # type: ignore[arg-type]

    assert engine.calls == []
