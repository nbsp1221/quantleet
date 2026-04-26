from __future__ import annotations

import pytest

from quantcraft.backtest import BacktestSummary, ExposureSummary
from tests.support_backtest import (
    canonical_stop_market_donchian_trade_log_digest,
    canonical_stop_market_donchian_trade_log_samples,
    load_canonical_stop_market_donchian_bars,
    run_canonical_stop_market_donchian_backtest,
)


def test_canonical_stop_market_donchian_backtest_matches_public_result_contract() -> None:
    result = run_canonical_stop_market_donchian_backtest(
        load_canonical_stop_market_donchian_bars()
    )

    assert result.summary == BacktestSummary(
        total_trades=11,
        total_fills=22,
        total_fees=pytest.approx(957.600444),
        final_balance=pytest.approx(1003219.6895559998),
        final_equity=pytest.approx(1003219.6895559998),
        total_return=pytest.approx(0.003219689556),
        max_drawdown=pytest.approx(0.008937033638),
        realized_pnl=pytest.approx(4177.28999999995),
        unrealized_pnl=0.0,
        win_rate=pytest.approx(0.545454545455),
        average_win=pytest.approx(1882.151602666662),
        average_loss=pytest.approx(1614.644012000005),
        profit_factor=pytest.approx(1.398811073162),
        exposure=ExposureSummary(
            bars_in_position=298,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.034018264840182645),
        ),
    )

    first_fills, last_fills = canonical_stop_market_donchian_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1735776000000,
            "side": "buy",
            "quantity": 1.0,
            "price": 95161.31,
            "fee": 38.064524,
        },
        {
            "timestamp": 1735887600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 96504.59999999999,
            "fee": 38.60184,
        },
        {
            "timestamp": 1735920000000,
            "side": "buy",
            "quantity": 1.0,
            "price": 97822.51,
            "fee": 39.129004,
        },
        {
            "timestamp": 1735984800000,
            "side": "sell",
            "quantity": 1.0,
            "price": 97644.2,
            "fee": 39.05768,
        },
        {
            "timestamp": 1736128800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 98949.11,
            "fee": 39.579644,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1752508800000,
            "side": "sell",
            "quantity": 1.0,
            "price": 119863.0,
            "fee": 47.9452,
        },
        {
            "timestamp": 1755122400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 123300.11,
            "fee": 49.320044,
        },
        {
            "timestamp": 1755154800000,
            "side": "sell",
            "quantity": 1.0,
            "price": 121792.2,
            "fee": 48.71688,
        },
        {
            "timestamp": 1759636800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 124545.71,
            "fee": 49.818284,
        },
        {
            "timestamp": 1759806000000,
            "side": "sell",
            "quantity": 1.0,
            "price": 124205.5,
            "fee": 49.6822,
        },
    )
    assert canonical_stop_market_donchian_trade_log_digest(result.trade_log) == (
        "55d9b2baff8133169b3a301f4d8612b66eb02f405fa42ca0ff7b3272ac45d600"
    )
