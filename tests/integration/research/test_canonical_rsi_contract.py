from __future__ import annotations

import pytest

from quantcraft.backtest import BacktestSummary, ExposureSummary
from tests.support_backtest import (
    assert_canonical_report,
    canonical_report_expectation,
    canonical_rsi_trade_log_digest,
    canonical_rsi_trade_log_samples,
    load_canonical_rsi_bars,
    run_canonical_rsi_backtest,
)


def test_canonical_rsi_backtest_matches_public_result_contract() -> None:
    result = run_canonical_rsi_backtest(load_canonical_rsi_bars())

    assert result.summary == BacktestSummary(
        total_trades=34,
        total_fills=68,
        total_fees=pytest.approx(2712.97336),
        final_balance=pytest.approx(1_007_629.8266399998),
        final_equity=pytest.approx(1_007_629.8266399998),
        total_return=pytest.approx(0.00762982664),
        max_drawdown=pytest.approx(0.040586338429),
        realized_pnl=pytest.approx(10_342.799999999595),
        unrealized_pnl=0.0,
        win_rate=pytest.approx(0.647058823529),
        average_win=pytest.approx(2500.771605454533),
        average_loss=pytest.approx(3948.929056666677),
        profit_factor=pytest.approx(1.161010460695),
        exposure=ExposureSummary(
            bars_in_position=4504,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.5141552511415525),
        ),
    )

    first_fills, last_fills = canonical_rsi_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1736265600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 97915.5,
            "fee": 39.1662,
        },
        {
            "timestamp": 1736848800000,
            "side": "sell",
            "quantity": 1.0,
            "price": 97129.79999999999,
            "fee": 38.85192,
        },
        {
            "timestamp": 1737334800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 99769.6,
            "fee": 39.90784,
        },
        {
            "timestamp": 1738184400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 104155.29999999999,
            "fee": 41.66212,
        },
        {
            "timestamp": 1738357200000,
            "side": "buy",
            "quantity": 1.0,
            "price": 101647.6,
            "fee": 40.65904,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1765490400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 92823.5,
            "fee": 37.1294,
        },
        {
            "timestamp": 1765713600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 89308.40000000001,
            "fee": 35.72336,
        },
        {
            "timestamp": 1765983600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 89633.9,
            "fee": 35.85356,
        },
        {
            "timestamp": 1766502000000,
            "side": "buy",
            "quantity": 1.0,
            "price": 86837.3,
            "fee": 34.73492,
        },
        {
            "timestamp": 1766970000000,
            "side": "sell",
            "quantity": 1.0,
            "price": 88262.09999999999,
            "fee": 35.30484,
        },
    )
    assert canonical_rsi_trade_log_digest(result.trade_log) == (
        "b95fcc3832f1ac9850fc8ab4e9fabd01bc2465f118597d9ea8f7ed2a8e3ae9c1"
    )
    assert_canonical_report("rsi_30_70", result.report, canonical_report_expectation("rsi_30_70"))
