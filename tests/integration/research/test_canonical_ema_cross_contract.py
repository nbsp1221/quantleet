from __future__ import annotations

import pytest

from quantcraft.backtest import BacktestSummary, ExposureSummary
from tests.support_backtest import (
    assert_canonical_report,
    canonical_ema_trade_log_digest,
    canonical_ema_trade_log_samples,
    canonical_report_expectation,
    load_canonical_ema_bars,
    run_canonical_ema_backtest,
)


def test_canonical_ema_backtest_matches_public_result_contract() -> None:
    result = run_canonical_ema_backtest(load_canonical_ema_bars())

    assert result.summary == BacktestSummary(
        total_trades=188,
        total_fills=376,
        total_fees=pytest.approx(15277.53524),
        final_balance=pytest.approx(978253.5647599992),
        final_equity=pytest.approx(978253.5647599992),
        total_return=pytest.approx(-0.02174643524),
        max_drawdown=pytest.approx(0.03543430962),
        realized_pnl=pytest.approx(-6468.900000002081),
        unrealized_pnl=0.0,
        win_rate=pytest.approx(0.292553191489),
        average_win=pytest.approx(2082.405335272716),
        average_loss=pytest.approx(1024.652095338357),
        profit_factor=pytest.approx(0.840426782297),
        exposure=ExposureSummary(
            bars_in_position=4471,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.5103881278538813),
        ),
    )
    first_fills, last_fills = canonical_ema_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1735905600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 96710.5,
            "fee": 38.6842,
        },
        {
            "timestamp": 1736071200000,
            "side": "sell",
            "quantity": 1.0,
            "price": 97619.79999999999,
            "fee": 39.04792,
        },
        {
            "timestamp": 1736110800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 98244.90000000001,
            "fee": 39.29796,
        },
        {
            "timestamp": 1736262000000,
            "side": "sell",
            "quantity": 1.0,
            "price": 99945.2,
            "fee": 39.97808,
        },
        {
            "timestamp": 1736492400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 94207.70000000001,
            "fee": 37.68308,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1766952000000,
            "side": "sell",
            "quantity": 1.0,
            "price": 87488.59999999999,
            "fee": 34.99544,
        },
        {
            "timestamp": 1766966400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 87920.5,
            "fee": 35.1682,
        },
        {
            "timestamp": 1767013200000,
            "side": "sell",
            "quantity": 1.0,
            "price": 87343.79999999999,
            "fee": 34.93752,
        },
        {
            "timestamp": 1767092400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 87914.40000000001,
            "fee": 35.16576,
        },
        {
            "timestamp": 1767200400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 87625.79999999999,
            "fee": 35.05032,
        },
    )
    assert canonical_ema_trade_log_digest(result.trade_log) == (
        "d582b256fb7fb64c64f7584c1b2e20fb69ca794b50f50c5a00786961b90965c5"
    )
    assert_canonical_report("ema_cross", result.report, canonical_report_expectation("ema_cross"))
