from __future__ import annotations

import pytest

from quantcraft.backtest import BacktestSummary, ExposureSummary
from tests.support_backtest import (
    canonical_stop_market_inside_bar_trade_log_digest,
    canonical_stop_market_inside_bar_trade_log_samples,
    load_canonical_stop_market_inside_bar_bars,
    run_canonical_stop_market_inside_bar_backtest,
)


def test_canonical_stop_market_inside_bar_backtest_matches_public_result_contract() -> None:
    result = run_canonical_stop_market_inside_bar_backtest(
        load_canonical_stop_market_inside_bar_bars()
    )

    assert result.summary == BacktestSummary(
        total_trades=37,
        total_fills=74,
        total_fees=pytest.approx(3180.777748),
        final_balance=pytest.approx(999067.6522520002),
        final_equity=pytest.approx(999067.6522520002),
        total_return=pytest.approx(-0.000932347748),
        max_drawdown=pytest.approx(0.005891044362),
        realized_pnl=pytest.approx(2248.429999999737),
        unrealized_pnl=0.0,
        win_rate=pytest.approx(0.378378378378),
        average_win=pytest.approx(568.137775999991),
        average_loss=pytest.approx(386.359852695658),
        profit_factor=pytest.approx(0.895080044353),
        exposure=ExposureSummary(
            bars_in_position=76,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.008675799086757991),
        ),
    )

    first_fills, last_fills = canonical_stop_market_inside_bar_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1735776000000,
            "side": "buy",
            "quantity": 1.0,
            "price": 95161.31,
            "fee": 38.064524,
        },
        {
            "timestamp": 1735826400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 96425.9,
            "fee": 38.57036,
        },
        {
            "timestamp": 1735833600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 97440.11,
            "fee": 38.976044,
        },
        {
            "timestamp": 1735855200000,
            "side": "sell",
            "quantity": 1.0,
            "price": 97179.9,
            "fee": 38.87196,
        },
        {
            "timestamp": 1735869600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 97180.21,
            "fee": 38.872084,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1755126000000,
            "side": "sell",
            "quantity": 1.0,
            "price": 122965.2,
            "fee": 49.18608,
        },
        {
            "timestamp": 1759636800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 124545.71,
            "fee": 49.818284,
        },
        {
            "timestamp": 1759640400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 125167.29999999999,
            "fee": 50.06692,
        },
        {
            "timestamp": 1759773600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 125877.41,
            "fee": 50.350964,
        },
        {
            "timestamp": 1759777200000,
            "side": "sell",
            "quantity": 1.0,
            "price": 125986.0,
            "fee": 50.3944,
        },
    )
    assert canonical_stop_market_inside_bar_trade_log_digest(result.trade_log) == (
        "a5060fbaed4342d83addf9f5c15f50f41abea16207bf8bacacdaa104989f140d"
    )
