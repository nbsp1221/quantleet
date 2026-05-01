from __future__ import annotations

import inspect

import pytest

from quantcraft.backtest import BacktestResult, BacktestSummary, ExposureSummary
from quantcraft.trading.domain.state import TradingState


def _summary() -> BacktestSummary:
    return BacktestSummary(
        total_trades=0,
        total_fills=0,
        total_fees=0.0,
        final_balance=1_000.0,
        final_equity=1_000.0,
        total_return=0.0,
        max_drawdown=0.0,
        realized_pnl=0.0,
        unrealized_pnl=0.0,
        win_rate=0.0,
        average_win=0.0,
        average_loss=0.0,
        profit_factor=0.0,
        exposure=ExposureSummary(
            bars_in_position=0,
            total_bars=0,
            exposure_ratio=0.0,
        ),
    )


def _manual_result(**overrides: object) -> BacktestResult:
    values = {
        "trade_log": (),
        "equity_curve": (),
        "final_state": TradingState(cash=1_000.0, equity=1_000.0),
        "summary": _summary(),
    }
    values.update(overrides)
    return BacktestResult(**values)


def test_backtest_result_preserves_legacy_positional_construction() -> None:
    result = BacktestResult(
        (),
        (),
        TradingState(cash=1_000.0, equity=1_000.0),
        _summary(),
        "custom_model",
    )

    assert result.execution_model_name == "custom_model"
    assert result.drawdown_curve == ()


def test_drawdown_curve_participates_in_result_equality() -> None:
    left = _manual_result(equity_curve=(100.0, 90.0), drawdown_curve=(0.0, 0.1))
    right = _manual_result(equity_curve=(100.0, 90.0), drawdown_curve=(0.0, 0.2))

    assert left != right


def test_plot_public_signature_does_not_accept_data_inputs() -> None:
    signature = inspect.signature(BacktestResult.plot)

    assert "bars" not in signature.parameters
    assert "source" not in signature.parameters
    assert "dataframe" not in signature.parameters
    assert "report" not in signature.parameters


def test_plot_rejects_workaround_style_arguments() -> None:
    result = _manual_result()

    with pytest.raises(TypeError):
        result.plot(bars=object())  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        result.plot(source=object())  # type: ignore[call-arg]


def test_plot_requires_engine_run_snapshot() -> None:
    result = _manual_result()

    with pytest.raises(ValueError, match="run snapshot"):
        result.plot()
