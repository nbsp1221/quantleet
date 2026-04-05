from __future__ import annotations

import pytest

from quantcraft.research.application.backtest import BacktestSummary, ExposureSummary
from tests.support_backtest import (
    canonical_rsi_trade_log_digest,
    canonical_rsi_trade_log_samples,
    load_canonical_rsi_bars,
    run_canonical_rsi_backtest,
)


def test_canonical_rsi_backtest_matches_public_result_contract() -> None:
    result = run_canonical_rsi_backtest(load_canonical_rsi_bars())

    assert result.summary == BacktestSummary(
        total_trades=118,
        total_fills=236,
        total_fees=pytest.approx(9538.82336),
        final_balance=pytest.approx(1_038_523.57664),
        final_equity=pytest.approx(1_038_523.57664),
        total_return=pytest.approx(0.03852357664),
        max_drawdown=pytest.approx(0.021601945864),
        realized_pnl=pytest.approx(48_062.39999999861),
        unrealized_pnl=0.0,
        win_rate=pytest.approx(0.737288135593),
        average_win=pytest.approx(1468.807173333322),
        average_loss=pytest.approx(2879.440240000012),
        profit_factor=pytest.approx(1.43157555534),
        exposure=ExposureSummary(
            bars_in_position=4153,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.4740867579908676),
        ),
    )

    first_fills, last_fills = canonical_rsi_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1735894800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 96090.70000000001,
            "fee": 38.43628,
        },
        {
            "timestamp": 1735930800000,
            "side": "sell",
            "quantity": 1.0,
            "price": 98483.59999999999,
            "fee": 39.39344,
        },
        {
            "timestamp": 1735984800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 97644.40000000001,
            "fee": 39.05776,
        },
        {
            "timestamp": 1736128800000,
            "side": "sell",
            "quantity": 1.0,
            "price": 98735.59999999999,
            "fee": 39.49424,
        },
        {
            "timestamp": 1736254800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 100712.5,
            "fee": 40.285,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1766613600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 87653.79999999999,
            "fee": 35.06152,
        },
        {
            "timestamp": 1766768400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 86821.8,
            "fee": 34.72872,
        },
        {
            "timestamp": 1766973600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 88419.2,
            "fee": 35.36768,
        },
        {
            "timestamp": 1767031200000,
            "side": "buy",
            "quantity": 1.0,
            "price": 87814.20000000001,
            "fee": 35.12568,
        },
        {
            "timestamp": 1767092400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 87914.2,
            "fee": 35.16568,
        },
    )
    assert canonical_rsi_trade_log_digest(result.trade_log) == (
        "c36fdb0fbc3b0c75367cff88f856644203f4d6ac0c2ee169572317187e56e269"
    )
