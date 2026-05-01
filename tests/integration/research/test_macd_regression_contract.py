from __future__ import annotations

import pytest

from quantcraft.backtest import BacktestSummary, ExposureSummary
from tests.support_backtest import (
    assert_canonical_report,
    canonical_macd_trade_log_digest,
    canonical_macd_trade_log_samples,
    canonical_report_expectation,
    load_canonical_macd_bars,
    run_canonical_macd_backtest,
)


def test_canonical_macd_backtest_matches_public_regression_contract() -> None:
    result = run_canonical_macd_backtest(load_canonical_macd_bars())

    assert result.summary == BacktestSummary(
        total_trades=333,
        total_fills=666,
        total_fees=pytest.approx(27110.48432),
        final_balance=pytest.approx(971733.3156799956),
        final_equity=pytest.approx(971733.3156799956),
        total_return=pytest.approx(-0.02826668432),
        max_drawdown=pytest.approx(0.043460392272),
        realized_pnl=pytest.approx(-1156.200000003876),
        unrealized_pnl=0.0,
        win_rate=pytest.approx(0.345345345345),
        average_win=pytest.approx(1502.259381565206),
        average_loss=pytest.approx(922.139968807351),
        profit_factor=pytest.approx(0.859388277347),
        exposure=ExposureSummary(
            bars_in_position=4326,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.49383561643835616),
        ),
    )
    first_fills, last_fills = canonical_macd_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1735923600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 97822.5,
            "fee": 39.129,
        },
        {
            "timestamp": 1735963200000,
            "side": "sell",
            "quantity": 1.0,
            "price": 98149.2,
            "fee": 39.25968,
        },
        {
            "timestamp": 1736024400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 98577.5,
            "fee": 39.431,
        },
        {
            "timestamp": 1736042400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 98086.5,
            "fee": 39.2346,
        },
        {
            "timestamp": 1736110800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 98244.90000000001,
            "fee": 39.29796,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1767006000000,
            "side": "sell",
            "quantity": 1.0,
            "price": 87747.09999999999,
            "fee": 35.09884,
        },
        {
            "timestamp": 1767078000000,
            "side": "buy",
            "quantity": 1.0,
            "price": 87404.40000000001,
            "fee": 34.96176,
        },
        {
            "timestamp": 1767157200000,
            "side": "sell",
            "quantity": 1.0,
            "price": 88287.09999999999,
            "fee": 35.31484,
        },
        {
            "timestamp": 1767178800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 88804.70000000001,
            "fee": 35.52188,
        },
        {
            "timestamp": 1767193200000,
            "side": "sell",
            "quantity": 1.0,
            "price": 88443.29999999999,
            "fee": 35.37732,
        },
    )
    assert canonical_macd_trade_log_digest(result.trade_log) == (
        "bc91de2ef8edfb0992d557ac5339c6f17111d892e43ee94c7079064257b89b12"
    )
    assert_canonical_report("macd_cross", result.report, canonical_report_expectation("macd_cross"))
