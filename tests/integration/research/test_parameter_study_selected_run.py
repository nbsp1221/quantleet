from __future__ import annotations

import matplotlib.pyplot as plt

from quantcraft.backtest import BacktestResult
from quantcraft.research import ParameterStudy
from tests.integration.research.test_parameter_study_grid_search import (
    ParameterizedRoundTripStrategy,
    crossing_bars,
    engine,
)


def test_selected_successful_row_retains_engine_result_report_and_plot_path() -> None:
    result = ParameterStudy(
        engine=engine(),
        bars=crossing_bars(),
        strategy_factory=lambda parameters: ParameterizedRoundTripStrategy(
            fast=int(parameters["fast"]),
            slow=int(parameters["slow"]),
        ),
    ).grid_search(
        parameters={"fast": [5], "slow": [10]},
        objective=("returns.total_return", "max"),
    )

    best = result.best()

    assert isinstance(best.backtest, BacktestResult)
    assert best.backtest.report.run.run_label == "grid-search-0"

    figure = best.backtest.plot()
    try:
        assert figure is not None
    finally:
        plt.close(figure)


def test_rejected_and_failed_rows_do_not_expose_fake_backtests() -> None:
    result = ParameterStudy(
        engine=engine(),
        bars=crossing_bars(),
        strategy_factory=lambda parameters: ParameterizedRoundTripStrategy(
            fast=int(parameters["fast"]),
            slow=int(parameters["slow"]),
        ),
    ).grid_search(
        parameters={"fast": [20], "slow": [10]},
        constraint=lambda parameters: False,
    )

    assert result.rejected()[0].backtest is None
