from __future__ import annotations

import pytest

from quantcraft.backtest import BacktestSummary, ExposureSummary
from tests.support_backtest import (
    canonical_limit_mixed_trade_log_digest,
    canonical_limit_mixed_trade_log_samples,
    load_canonical_limit_mixed_bars,
    run_canonical_limit_mixed_backtest,
)


def test_canonical_limit_mixed_backtest_matches_public_result_contract() -> None:
    result = run_canonical_limit_mixed_backtest(load_canonical_limit_mixed_bars())

    assert result.summary == BacktestSummary(
        total_trades=27,
        total_fills=55,
        total_fees=pytest.approx(2449.423402),
        final_balance=pytest.approx(906876.681597995),
        final_equity=pytest.approx(994484.881597995),
        total_return=pytest.approx(-0.005515118402),
        max_drawdown=pytest.approx(0.040545478092),
        realized_pnl=pytest.approx(32010.204999994836),
        unrealized_pnl=pytest.approx(-35075.90000000001),
        win_rate=pytest.approx(1.0),
        average_win=pytest.approx(1096.66130511092),
        average_loss=0.0,
        profit_factor=float("inf"),
        exposure=ExposureSummary(
            bars_in_position=7572,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.8643835616438356),
        ),
    )

    first_fills, last_fills = canonical_limit_mixed_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1735891200000,
            "side": "buy",
            "quantity": 1.0,
            "price": 96275.1,
            "fee": 38.51004,
        },
        {
            "timestamp": 1735905600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 96847.67,
            "fee": 38.739068,
        },
        {
            "timestamp": 1736247600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 101366.8,
            "fee": 40.54672,
        },
        {
            "timestamp": 1737075600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 101738.47499999999,
            "fee": 40.69539,
        },
        {
            "timestamp": 1737324000000,
            "side": "buy",
            "quantity": 1.0,
            "price": 103687.4,
            "fee": 41.47496,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1755176400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 118822.2,
            "fee": 47.52888,
        },
        {
            "timestamp": 1759503600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 122078.2199999996,
            "fee": 48.831288,
        },
        {
            "timestamp": 1759824000000,
            "side": "buy",
            "quantity": 1.0,
            "price": 123627.1,
            "fee": 49.45084,
        },
        {
            "timestamp": 1759838400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 124716.47999999944,
            "fee": 49.886592,
        },
        {
            "timestamp": 1759849200000,
            "side": "buy",
            "quantity": 1.0,
            "price": 122684.1,
            "fee": 49.07364,
        },
    )
    assert canonical_limit_mixed_trade_log_digest(result.trade_log) == (
        "b2f43fa6c9f65da5f5deae2ce1dab6d46b2c82d98991c6a18cf21f5fc7903fef"
    )
