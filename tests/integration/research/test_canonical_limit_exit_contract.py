from __future__ import annotations

import pytest

from quantcraft.backtest import BacktestSummary, ExposureSummary
from tests.support_backtest import (
    canonical_limit_exit_trade_log_digest,
    canonical_limit_exit_trade_log_samples,
    load_canonical_limit_exit_bars,
    run_canonical_limit_exit_backtest,
)


def test_canonical_limit_exit_backtest_matches_public_result_contract() -> None:
    result = run_canonical_limit_exit_backtest(load_canonical_limit_exit_bars())

    assert result.summary == BacktestSummary(
        total_trades=13,
        total_fills=27,
        total_fees=pytest.approx(1191.233712),
        final_balance=pytest.approx(908974.8462879998),
        final_equity=pytest.approx(996583.0462879997),
        total_return=pytest.approx(-0.003416953712),
        max_drawdown=pytest.approx(0.035056108234),
        realized_pnl=pytest.approx(28316.180000000022),
        unrealized_pnl=pytest.approx(-30541.90000000001),
        win_rate=pytest.approx(1.0),
        average_win=pytest.approx(2090.169717538463),
        average_loss=0.0,
        profit_factor=float("inf"),
        exposure=ExposureSummary(
            bars_in_position=7013,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.8005707762557077),
        ),
    )

    first_fills, last_fills = canonical_limit_exit_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1736265600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 97915.5,
            "fee": 39.1662,
        },
        {
            "timestamp": 1736967600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 99873.81,
            "fee": 39.949524,
        },
        {
            "timestamp": 1737334800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 99769.6,
            "fee": 39.90784,
        },
        {
            "timestamp": 1737338400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 101764.99200000001,
            "fee": 40.7059968,
        },
        {
            "timestamp": 1737936000000,
            "side": "buy",
            "quantity": 1.0,
            "price": 102560.1,
            "fee": 41.02404,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1755176400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 118822.3,
            "fee": 47.52892,
        },
        {
            "timestamp": 1759503600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 121198.746,
            "fee": 48.4794984,
        },
        {
            "timestamp": 1759856400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 121621.70000000001,
            "fee": 48.64868,
        },
        {
            "timestamp": 1759942800000,
            "side": "sell",
            "quantity": 1.0,
            "price": 124054.13400000002,
            "fee": 49.6216536,
        },
        {
            "timestamp": 1760115600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 118150.1,
            "fee": 47.26004,
        },
    )
    assert canonical_limit_exit_trade_log_digest(result.trade_log) == (
        "a8a7bbf6716b5743bb7aa6a9345107c2f7aa570cf78fee5cdbf5b45c1cd0ff93"
    )
