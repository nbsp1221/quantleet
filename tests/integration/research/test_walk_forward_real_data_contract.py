from __future__ import annotations

import pytest

from quantleet.backtest import BacktestEngine
from quantleet.data import BarSeries
from quantleet.research import WalkForwardStudy, qc, ta
from quantleet.strategy import Strategy, StrategyConfig
from quantleet.trading.domain.costs import CostConfig
from tests.support_backtest import load_canonical_bars

_DAY = 24
_MONTH = _DAY * 30
_BAR_OFFSET = _MONTH * 4
_BAR_COUNT = _MONTH * 6
_TRAIN_SIZE = _MONTH * 3
_TEST_SIZE = _MONTH
_STEP_SIZE = _MONTH


class SmaRsiWfaConfig(StrategyConfig):
    fast: int = 12
    slow: int = 24
    rsi_length: int = 14
    rsi_entry: int = 55
    rsi_exit: int = 45


class SmaRsiWfaStrategy(Strategy[SmaRsiWfaConfig]):
    def init(self) -> None:
        self.fast = ta.sma(self.data.close, length=self.config.fast)
        self.slow = ta.sma(self.data.close, length=self.config.slow)
        self.rsi = ta.rsi(self.data.close, length=self.config.rsi_length)

    def on_bar(self, bar: object) -> None:
        if (
            not self.position.is_open
            and qc.crossover(self.fast, self.slow)
            and not qc.is_na(self.rsi.latest)
            and self.rsi.latest >= self.config.rsi_entry
        ):
            self.buy(quantity=1.0)
            return

        if self.position.is_open and (
            qc.crossunder(self.fast, self.slow)
            or (not qc.is_na(self.rsi.latest) and self.rsi.latest <= self.config.rsi_exit)
        ):
            self.sell(quantity=1.0)


def test_wfa_real_data_focused_sma_rsi_contract_matches_golden_slice() -> None:
    result = WalkForwardStudy(
        engine=BacktestEngine(
            initial_cash=1_000_000.0,
            costs=CostConfig(tick_size=0.1, slippage_ticks=0.0, fee_rate=0.0),
        ),
        bars=_focused_real_bars(),
        strategy=SmaRsiWfaStrategy,
    ).run(
        parameters={
            "fast": [6, 12, 24],
            "slow": [12, 24, 48],
            "rsi_length": [14],
            "rsi_entry": [55],
            "rsi_exit": [40, 45],
        },
        objective=("returns.total_return", "max"),
        constraint=lambda config: (
            config["fast"] < config["slow"] and config["rsi_exit"] < config["rsi_entry"]
        ),
        train_size=_TRAIN_SIZE,
        test_size=_TEST_SIZE,
        step_size=_STEP_SIZE,
        max_candidates=None,
    )

    assert result.fold_count == 3
    assert result.successful_fold_count == 3
    assert result.failed_fold_count == 0
    assert result.execution_scale.raw_candidate_count_per_fold == 18
    assert result.execution_scale.planned_total_runs == 57

    assert [dict(fold.selected_config or {}) for fold in result.folds] == [
        {"fast": 6, "slow": 48, "rsi_length": 14, "rsi_entry": 55, "rsi_exit": 40},
        {"fast": 6, "slow": 12, "rsi_length": 14, "rsi_entry": 55, "rsi_exit": 45},
        {"fast": 6, "slow": 24, "rsi_length": 14, "rsi_entry": 55, "rsi_exit": 40},
    ]
    assert [fold.test_metrics["returns.total_return"] for fold in result.folds] == [
        pytest.approx(-0.0026449),
        pytest.approx(-0.0077626),
        pytest.approx(0.0058646),
    ]
    assert [fold.test_metrics["trades.closed_count"] for fold in result.folds] == [9, 21, 7]
    assert [
        fold.selected_test_result.report.exposure.ending_state
        for fold in result.folds
        if fold.selected_test_result is not None
    ] == ["open", "flat", "flat"]
    assert all(
        fold.train_result is not None and fold.train_result.rejected_count == 6
        for fold in result.folds
    )
    assert result.oos_summary.positive_fold_ratio == pytest.approx(1 / 3)


def _focused_real_bars() -> BarSeries:
    bars = load_canonical_bars()
    return BarSeries(
        symbol=bars.symbol,
        timeframe=bars.timeframe,
        bar_type=bars.bar_type,
        rows=bars.rows[_BAR_OFFSET : _BAR_OFFSET + _BAR_COUNT],
    )
