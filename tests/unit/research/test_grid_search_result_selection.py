from __future__ import annotations

import math

import pytest

from quantcraft.research import GridSearchResult, GridSearchRow


def row(
    run_index: int,
    *,
    status: str = "success",
    metric: float | int | None = None,
    state: str = "defined",
) -> GridSearchRow:
    return GridSearchRow(
        run_index=run_index,
        status=status,
        parameters={"x": run_index},
        backtest=None,
        metrics={"returns.total_return": metric},
        metric_states={"returns.total_return": state},
        failure_stage=None,
        error_type=None,
        error_message=None,
    )


def test_best_and_top_rank_by_explicit_max_and_min_objectives() -> None:
    result = GridSearchResult(
        rows=(row(0, metric=0.10), row(1, metric=0.30), row(2, metric=0.20)),
        objective=("returns.total_return", "max"),
    )

    assert result.best().run_index == 1
    assert [selected.run_index for selected in result.top(2)] == [1, 2]
    assert [
        selected.run_index
        for selected in result.top(2, objective=("returns.total_return", "min"))
    ] == [0, 2]


def test_selection_requires_objective_and_valid_n() -> None:
    result = GridSearchResult(rows=(row(0, metric=0.10),), objective=None)

    with pytest.raises(ValueError, match="objective"):
        result.best()
    with pytest.raises(ValueError, match="objective"):
        result.top(1)
    with pytest.raises(ValueError, match="n"):
        result.top(0, objective=("returns.total_return", "max"))


@pytest.mark.parametrize("objective", [[], ()])
def test_explicit_invalid_falsy_objective_does_not_fall_back_to_default(
    objective: object,
) -> None:
    result = GridSearchResult(
        rows=(row(0, metric=0.10),),
        objective=("returns.total_return", "max"),
    )

    with pytest.raises(TypeError, match="objective"):
        result.top(1, objective=objective)  # type: ignore[arg-type]


def test_failed_rejected_undefined_and_nan_rows_are_ineligible() -> None:
    result = GridSearchResult(
        rows=(
            row(0, metric=0.10),
            row(1, status="failed", metric=99.0),
            row(2, status="rejected", metric=99.0),
            row(3, metric=None, state="undefined"),
            row(4, metric=math.nan, state="undefined"),
        ),
        objective=("returns.total_return", "max"),
    )

    assert result.eligible_count == 1
    assert result.best().run_index == 0


def test_infinity_is_eligible_and_ties_preserve_run_index() -> None:
    result = GridSearchResult(
        rows=(
            row(0, metric=0.10),
            row(1, metric=math.inf, state="positive_infinity"),
            row(2, metric=math.inf, state="positive_infinity"),
        ),
        objective=("returns.total_return", "max"),
    )

    assert result.best().run_index == 1
    assert [selected.run_index for selected in result.top(3)] == [1, 2, 0]


def test_negative_infinity_is_eligible_for_min_objectives() -> None:
    result = GridSearchResult(
        rows=(
            row(0, metric=-0.10),
            row(1, metric=-math.inf, state="negative_infinity"),
        ),
        objective=("returns.total_return", "min"),
    )

    assert result.best().run_index == 1


def test_no_eligible_rows_best_raises_top_returns_empty_tuple() -> None:
    result = GridSearchResult(
        rows=(row(0, status="rejected", metric=None, state="undefined"),),
        objective=("returns.total_return", "max"),
    )

    with pytest.raises(ValueError, match="eligible"):
        result.best()
    assert result.top(5) == ()
