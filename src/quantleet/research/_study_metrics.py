from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Literal

from quantleet.backtest import BacktestResult

type JSONScalar = str | int | float | bool | None
type Objective = tuple[str, Literal["max", "min"]]
type MetricState = Literal[
    "defined",
    "undefined",
    "positive_infinity",
    "negative_infinity",
]
type MetricValue = int | float | None
type Constraint = Callable[[Mapping[str, JSONScalar]], bool]


def _final_equity(result: BacktestResult) -> float:
    return result.report.returns.final_equity


def _total_return(result: BacktestResult) -> float:
    return result.report.returns.total_return


def _max_drawdown(result: BacktestResult) -> float:
    return result.report.risk.max_drawdown


def _sharpe_ratio(result: BacktestResult) -> float | None:
    return result.report.risk.sharpe_ratio


def _closed_trade_count(result: BacktestResult) -> int:
    return result.report.trades.closed_trade_count


def _win_rate(result: BacktestResult) -> float | None:
    return result.report.trades.win_rate


def _profit_factor(result: BacktestResult) -> float | None:
    return result.report.trades.profit_factor


def _total_fees(result: BacktestResult) -> float:
    return result.report.costs.total_fees


def _exposure_ratio(result: BacktestResult) -> float:
    return result.report.exposure.exposure_ratio


def _order_rejection_count(result: BacktestResult) -> int:
    return result.report.execution.order_rejection_count


METRIC_EXTRACTORS: dict[str, Callable[[BacktestResult], MetricValue]] = {
    "equity.final": _final_equity,
    "returns.total_return": _total_return,
    "risk.max_drawdown": _max_drawdown,
    "risk.sharpe_ratio": _sharpe_ratio,
    "trades.closed_count": _closed_trade_count,
    "trades.win_rate": _win_rate,
    "trades.profit_factor": _profit_factor,
    "costs.total_fees": _total_fees,
    "exposure.ratio": _exposure_ratio,
    "execution.order_rejection_count": _order_rejection_count,
}

METRIC_KEYS = tuple(METRIC_EXTRACTORS)
UNDEFINED_METRIC_STATES: Mapping[str, MetricState] = MappingProxyType(
    dict.fromkeys(METRIC_KEYS, "undefined")
)


def validate_objective(value: object) -> Objective:
    if value is None:
        raise ValueError("objective is required for selection")
    if not isinstance(value, tuple) or len(value) != 2:
        raise TypeError("objective must be a (metric_path, direction) tuple")
    metric_path, direction = value
    if not isinstance(metric_path, str) or not isinstance(direction, str):
        raise TypeError("objective must be a (metric_path, direction) tuple")
    if metric_path not in METRIC_EXTRACTORS:
        raise ValueError(f"unknown objective metric path {metric_path!r}")
    if direction not in {"max", "min"}:
        raise ValueError("objective direction must be 'max' or 'min'")
    return metric_path, direction  # type: ignore[return-value]


def extract_metrics(result: BacktestResult) -> dict[str, MetricValue]:
    metrics: dict[str, MetricValue] = {}
    for metric_path, extractor in METRIC_EXTRACTORS.items():
        metrics[metric_path] = extractor(result)
    return metrics


def normalize_metrics(
    metrics: Mapping[str, MetricValue],
) -> tuple[dict[str, MetricValue], dict[str, MetricState]]:
    normalized_metrics: dict[str, MetricValue] = {}
    metric_states: dict[str, MetricState] = {}
    for key in METRIC_KEYS:
        value = metrics.get(key)
        normalized_value, state = normalize_metric(value)
        normalized_metrics[key] = normalized_value
        metric_states[key] = state
    return normalized_metrics, metric_states


def normalize_metric(value: object) -> tuple[MetricValue, MetricState]:
    if value is None:
        return None, "undefined"
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"metric value must be numeric or None, got {type(value).__name__}")
    if isinstance(value, float):
        if math.isnan(value):
            return None, "undefined"
        if value == math.inf:
            return math.inf, "positive_infinity"
        if value == -math.inf:
            return -math.inf, "negative_infinity"
    return value, "defined"


__all__ = [
    "Constraint",
    "JSONScalar",
    "METRIC_EXTRACTORS",
    "METRIC_KEYS",
    "MetricState",
    "MetricValue",
    "Objective",
    "UNDEFINED_METRIC_STATES",
    "extract_metrics",
    "normalize_metric",
    "normalize_metrics",
    "validate_objective",
]
