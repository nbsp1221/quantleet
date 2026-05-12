from __future__ import annotations

import json
import math

from quantleet.research import GridSearchResult, GridSearchRow
from quantleet.strategy import StrategyConfigValidationError
from tests.unit.research.support_parameter_study import (
    NoTradeConfig,
    NoTradeStrategy,
    make_bars,
    make_engine,
)

EXPECTED_NON_METRIC_KEYS = {
    "run_index",
    "status",
    "candidate_parameters",
    "strategy_config",
    "run.label",
    "strategy.class_name",
    "strategy.display_name",
    "run.symbol",
    "run.timeframe",
    "run.initial_cash",
    "execution.model_name",
    "rejection_stage",
    "failure_stage",
    "error_type",
    "error_message",
}

EXPECTED_METRIC_KEYS = {
    "equity.final",
    "returns.total_return",
    "risk.max_drawdown",
    "risk.sharpe_ratio",
    "trades.closed_count",
    "trades.win_rate",
    "trades.profit_factor",
    "costs.total_fees",
    "exposure.ratio",
    "execution.order_rejection_count",
}


def test_to_records_uses_stable_shape_for_success_rejected_and_failed_rows() -> None:
    success_result = make_engine().run(
        bars=make_bars(),
        strategy=NoTradeStrategy,
        config=NoTradeConfig(x=1),
        label="grid-search-0",
    )
    result = GridSearchResult(
        rows=(
            GridSearchRow.success(
                run_index=0,
                candidate_parameters={"x": 1},
                strategy_config={"x": 1, "enabled": True},
                backtest=success_result,
                metrics={
                    "equity.final": success_result.report.returns.final_equity,
                    "returns.total_return": success_result.report.returns.total_return,
                    "risk.max_drawdown": success_result.report.risk.max_drawdown,
                    "risk.sharpe_ratio": success_result.report.risk.sharpe_ratio,
                    "trades.closed_count": success_result.report.trades.closed_trade_count,
                    "trades.win_rate": success_result.report.trades.win_rate,
                    "trades.profit_factor": math.inf,
                    "costs.total_fees": success_result.report.costs.total_fees,
                    "exposure.ratio": success_result.report.exposure.exposure_ratio,
                    "execution.order_rejection_count": (
                        success_result.report.execution.order_rejection_count
                    ),
                },
            ),
            GridSearchRow.rejected(
                run_index=1,
                candidate_parameters={"x": 2},
                strategy_config={"x": 2, "enabled": True},
                rejection_stage="strategy_config",
                error=StrategyConfigValidationError("bad config"),
            ),
            GridSearchRow.failed(
                run_index=2,
                candidate_parameters={"x": 3},
                strategy_config={"x": 3, "enabled": True},
                failure_stage="strategy_construction",
                error=ValueError("bad strategy"),
            ),
        ),
        objective=("returns.total_return", "max"),
    )

    records = result.to_records()
    key_sets = [set(record) for record in records]

    assert key_sets[0] == key_sets[1] == key_sets[2]
    assert EXPECTED_NON_METRIC_KEYS.issubset(key_sets[0])
    assert EXPECTED_METRIC_KEYS.issubset(key_sets[0])
    assert {f"{key}_state" for key in EXPECTED_METRIC_KEYS}.issubset(key_sets[0])

    success = records[0]
    assert success["status"] == "success"
    assert success["candidate_parameters"] == {"x": 1}
    assert success["strategy_config"] == {"x": 1, "enabled": True}
    assert "parameters" not in success
    assert success["run.label"] == "grid-search-0"
    assert success["strategy.class_name"] == "NoTradeStrategy"
    assert success["run.symbol"] == "TEST"
    assert success["trades.profit_factor"] is None
    assert success["trades.profit_factor_state"] == "positive_infinity"

    rejected = records[1]
    assert rejected["status"] == "rejected"
    assert rejected["rejection_stage"] == "strategy_config"
    assert rejected["failure_stage"] is None
    assert rejected["error_type"] == "StrategyConfigValidationError"
    assert rejected["error_message"] == "bad config"
    assert rejected["returns.total_return"] is None
    assert rejected["returns.total_return_state"] == "undefined"

    failed = records[2]
    assert failed["status"] == "failed"
    assert failed["rejection_stage"] is None
    assert failed["failure_stage"] == "strategy_construction"
    assert failed["error_type"] == "ValueError"
    assert failed["error_message"] == "bad strategy"
    assert "traceback" not in json.dumps(failed).lower()


def test_to_records_never_emits_non_standard_json_float_tokens() -> None:
    result = GridSearchResult(
        rows=(
            GridSearchRow(
                run_index=0,
                status="success",
                candidate_parameters={"x": 1},
                strategy_config={"x": 1, "enabled": True},
                backtest=None,
                metrics={"returns.total_return": math.nan},
                metric_states={"returns.total_return": "undefined"},
                rejection_stage=None,
                failure_stage=None,
                error_type=None,
                error_message=None,
            ),
        ),
        objective=None,
    )

    payload = json.dumps(result.to_records(), allow_nan=False)

    assert "NaN" not in payload
    assert "Infinity" not in payload
