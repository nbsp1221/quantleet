from __future__ import annotations

import pytest

from quantcraft.backtest import BacktestSummary, ExposureSummary
from tests.support_backtest import (
    canonical_stop_market_opening_range_trade_log_digest,
    canonical_stop_market_opening_range_trade_log_samples,
    load_canonical_stop_market_opening_range_bars,
    run_canonical_stop_market_opening_range_backtest,
)


def test_canonical_stop_market_opening_range_backtest_matches_public_result_contract() -> None:
    result = run_canonical_stop_market_opening_range_backtest(
        load_canonical_stop_market_opening_range_bars()
    )

    assert result.summary == BacktestSummary(
        total_trades=36,
        total_fills=72,
        total_fees=pytest.approx(3108.974584),
        final_balance=pytest.approx(990447.9654159998),
        final_equity=pytest.approx(990447.9654159998),
        total_return=pytest.approx(-0.009552034584),
        max_drawdown=pytest.approx(0.015488816994),
        realized_pnl=pytest.approx(-6443.060000000228),
        unrealized_pnl=0.0,
        win_rate=pytest.approx(0.333333333333),
        average_win=pytest.approx(1204.708845999993),
        average_loss=pytest.approx(1000.355864000006),
        profit_factor=pytest.approx(0.602140143),
        exposure=ExposureSummary(
            bars_in_position=241,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.027511415525114154),
        ),
    )

    first_fills, last_fills = canonical_stop_market_opening_range_trade_log_samples(
        result.trade_log
    )
    assert first_fills == (
        {
            "timestamp": 1735743600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 94449.31,
            "fee": 37.779724,
        },
        {
            "timestamp": 1735772400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 94770.4,
            "fee": 37.90816,
        },
        {
            "timestamp": 1735804800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 96031.51,
            "fee": 38.412604,
        },
        {
            "timestamp": 1735858800000,
            "side": "sell",
            "quantity": 1.0,
            "price": 96863.7,
            "fee": 38.74548,
        },
        {
            "timestamp": 1735916400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 97325.81,
            "fee": 38.930324,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1759658400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 122997.9,
            "fee": 49.19916,
        },
        {
            "timestamp": 1759773600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 125877.41,
            "fee": 50.350964,
        },
        {
            "timestamp": 1759791600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 124999.79999999999,
            "fee": 49.99992,
        },
        {
            "timestamp": 1759838400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 125047.11,
            "fee": 50.018844,
        },
        {
            "timestamp": 1759845600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 123825.29999999999,
            "fee": 49.53012,
        },
    )
    assert canonical_stop_market_opening_range_trade_log_digest(result.trade_log) == (
        "40a67df9179c88467ca13f63dc0aec8834542116d9c73591e79a1652f7a10be3"
    )
