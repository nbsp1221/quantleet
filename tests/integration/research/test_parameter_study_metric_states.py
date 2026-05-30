from __future__ import annotations

from quantleet.research import ParameterStudy
from tests.integration.research.support_parameter_studies import crossing_bars, engine
from tests.unit.research.support_parameter_study import NoTradeStrategy


def test_no_trade_metrics_are_undefined_not_zero() -> None:
    result = ParameterStudy(
        engine=engine(),
        bars=crossing_bars(),
        strategy=NoTradeStrategy,
    ).grid_search(
        parameters={"x": [1]},
        objective=("returns.total_return", "max"),
    )

    row = result.successful()[0]
    assert row.status == "success"
    assert row.metric_states["trades.win_rate"] == "undefined"
    assert row.metric_states["trades.profit_factor"] == "undefined"
    assert row.metrics["trades.win_rate"] is None
    assert row.metrics["trades.profit_factor"] is None

    record = result.to_records()[0]
    assert record["trades.win_rate"] is None
    assert record["trades.win_rate_state"] == "undefined"
    assert record["trades.profit_factor"] is None
    assert record["trades.profit_factor_state"] == "undefined"
