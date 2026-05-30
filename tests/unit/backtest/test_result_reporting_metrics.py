from __future__ import annotations

import math

import pytest

from quantleet.backtest.reporting import (
    ClosedTrade,
    _geometric_average,
    _periodic_returns,
    _trade_metrics,
    periods_per_year_for_timeframe,
)
from quantleet.backtest.runtime import _trade_statistics
from quantleet.data import BarSeries, TimeBar
from quantleet.research import Strategy
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent
from tests.integration.research.support_backtest_runner import run_engine_backtest


class NoTradeStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        return None


class BuyFirstBarStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        if len(self.data.close) == 1:
            self.buy(quantity=1.0)


def _bars(
    closes: tuple[float, ...],
    *,
    timeframe: str = "1d",
    step_ms: int = 86_400_000,
) -> BarSeries:
    return BarSeries(
        symbol="BTC/USDT",
        timeframe=timeframe,
        bar_type="time",
        rows=tuple(
            TimeBar(
                timestamp=(index + 1) * step_ms,
                open=close,
                high=close,
                low=close,
                close=close,
                volume=1.0,
            )
            for index, close in enumerate(closes)
        ),
    )


def test_periods_per_year_uses_fixed_timeframe_before_timestamp_gaps() -> None:
    periods = periods_per_year_for_timeframe(
        timeframe="1h",
        timestamps=(0, 2 * 60 * 60 * 1000, 4 * 60 * 60 * 1000),
    )

    assert periods == pytest.approx(365.2425 * 24)


def test_periods_per_year_falls_back_to_timestamp_delta_for_month_like_tokens() -> None:
    periods = periods_per_year_for_timeframe(
        timeframe="1M",
        timestamps=(
            0,
            10 * 24 * 60 * 60 * 1000,
            40 * 24 * 60 * 60 * 1000,
            50 * 24 * 60 * 60 * 1000,
        ),
    )

    assert periods == pytest.approx(365.2425 / 10)


def test_decimal_timeframes_are_not_fixed_duration_beta_tokens() -> None:
    periods = periods_per_year_for_timeframe(
        timeframe="1.5h",
        timestamps=(0, 90 * 60 * 1000),
    )

    assert periods == pytest.approx((365.2425 * 24 * 60) / 90)


def test_report_return_and_risk_metrics_are_hand_computable() -> None:
    result = run_engine_backtest(
        bars=_bars((100.0, 110.0, 121.0)),
        strategy=NoTradeStrategy,
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    report = result.report

    assert report.returns.final_equity == 1_000.0
    assert report.returns.final_cash == 1_000.0
    assert report.returns.total_return == 0.0
    assert report.returns.buy_and_hold_return == 0.21
    assert report.returns.active_return == -0.21
    assert report.returns.equity_peak == 1_000.0
    assert report.risk.max_drawdown == 0.0
    assert report.risk.volatility == 0.0
    assert report.risk.sharpe_ratio is None
    assert report.trades.win_rate is None
    assert report.trades.profit_factor is None


def test_report_risk_metrics_include_first_return_and_are_annualized() -> None:
    result = run_engine_backtest(
        bars=_bars((100.0, 110.0, 121.0, 110.0), timeframe="1d"),
        strategy=BuyFirstBarStrategy,
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    report = result.report

    assert report.equity[0].equity == 1_000.0
    assert report.equity[1].equity == 1_000.0
    assert report.equity[2].equity == 1_011.0
    assert report.equity[3].equity == 1_000.0
    assert report.risk.volatility == pytest.approx(0.17071507644)
    assert report.risk.sharpe_ratio == pytest.approx(0.0640152802)


def test_total_loss_annualized_return_is_complete_loss() -> None:
    result = run_engine_backtest(
        bars=_bars((100.0, 100.0, 0.0), timeframe="1d"),
        strategy=BuyFirstBarStrategy,
        initial_cash=100.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert result.report.returns.final_equity == 0.0
    assert result.report.returns.annualized_return == -1.0


def test_report_uses_none_not_nan_for_undefined_metrics() -> None:
    result = run_engine_backtest(
        bars=_bars((100.0, 100.0)),
        strategy=NoTradeStrategy,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    report = result.report
    values = (
        report.risk.volatility,
        report.risk.sharpe_ratio,
        report.trades.win_rate,
        report.trades.average_win,
        report.trades.average_loss,
        report.trades.profit_factor,
    )

    assert report.risk.volatility == 0.0
    assert all(value is None for value in values[1:])
    assert not any(isinstance(value, float) and math.isnan(value) for value in values)


def test_runtime_trade_statistics_classifies_zero_pnl_as_neither_win_nor_loss() -> None:
    average_win, average_loss, win_rate, profit_factor = _trade_statistics((0.0, 10.0, -4.0, 2.0))

    assert average_win == 6.0
    assert average_loss == 4.0
    assert win_rate == 0.5
    assert profit_factor == 3.0


def test_runtime_trade_statistics_reports_loss_only_and_win_only_edges() -> None:
    assert _trade_statistics((-2.0, -6.0)) == (0.0, 4.0, 0.0, 0.0)
    assert _trade_statistics((2.0, 6.0)) == (4.0, 0.0, 1.0, float("inf"))


def test_report_trade_metrics_preserve_fractional_profit_factor() -> None:
    closed_trades = [
        ClosedTrade(
            entry_timestamp=60,
            exit_timestamp=120,
            entry_bar_index=0,
            exit_bar_index=1,
            duration_bars=2,
            quantity=1.0,
            entry_price=100.0,
            exit_price=107.0,
            gross_pnl=7.0,
            net_pnl=6.5,
            allocated_entry_fee=0.25,
            exit_fee=0.25,
            total_fees=0.5,
            net_return=0.065,
            entry_tag=None,
            entry_tags=(),
            exit_tag=None,
        ),
        ClosedTrade(
            entry_timestamp=180,
            exit_timestamp=240,
            entry_bar_index=2,
            exit_bar_index=3,
            duration_bars=2,
            quantity=1.0,
            entry_price=100.0,
            exit_price=96.0,
            gross_pnl=-4.0,
            net_pnl=-4.2,
            allocated_entry_fee=0.1,
            exit_fee=0.1,
            total_fees=0.2,
            net_return=-0.042,
            entry_tag=None,
            entry_tags=(),
            exit_tag=None,
        ),
    ]

    metrics = _trade_metrics(closed_trades, (0.065, -0.042), fill_count=4)

    assert metrics.closed_trade_count == 2
    assert metrics.win_rate == 0.5
    assert metrics.average_win == 6.5
    assert metrics.average_loss == 4.2
    assert metrics.profit_factor == pytest.approx(1.547619047619)


def test_periodic_returns_requires_positive_initial_cash() -> None:
    assert _periodic_returns(initial_cash=0.0, equity_values=(0.0, 1.0)) == ()


def test_geometric_average_compounds_return_factors() -> None:
    assert _geometric_average((0.10, -0.10, 0.05)) == pytest.approx(0.012997012504)
    assert _geometric_average(()) is None
