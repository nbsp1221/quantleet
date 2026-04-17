from __future__ import annotations

import pytest

from quantcraft.backtest import BacktestSummary, ExposureSummary
from tests.support_backtest import (
    canonical_limit_entry_trade_log_digest,
    canonical_limit_entry_trade_log_samples,
    load_canonical_limit_entry_bars,
    run_canonical_limit_entry_backtest,
)


def test_canonical_limit_entry_backtest_matches_public_result_contract() -> None:
    result = run_canonical_limit_entry_backtest(load_canonical_limit_entry_bars())

    assert result.summary == BacktestSummary(
        total_trades=29,
        total_fills=58,
        total_fees=pytest.approx(2018.622999964434),
        final_balance=pytest.approx(1000295.8770889534),
        final_equity=pytest.approx(1000295.8770889534),
        total_return=pytest.approx(0.000295877089),
        max_drawdown=pytest.approx(0.002148614649),
        realized_pnl=pytest.approx(2314.50008891821),
        unrealized_pnl=0.0,
        win_rate=pytest.approx(0.448275862069),
        average_win=pytest.approx(455.448461425902),
        average_loss=pytest.approx(351.559556848934),
        profit_factor=pytest.approx(1.052600811724),
        exposure=ExposureSummary(
            bars_in_position=45,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.005136986301369863),
        ),
    )

    first_fills, last_fills = canonical_limit_entry_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1736334000000,
            "side": "buy",
            "quantity": 1.0,
            "price": 94575.3353760541,
            "fee": 37.830134150422,
        },
        {
            "timestamp": 1736337600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 95093.7,
            "fee": 38.03748,
        },
        {
            "timestamp": 1736514000000,
            "side": "buy",
            "quantity": 1.0,
            "price": 93471.29184450864,
            "fee": 37.388516737803,
        },
        {
            "timestamp": 1736517600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 93522.0,
            "fee": 37.4088,
        },
        {
            "timestamp": 1736564400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 94113.08560330409,
            "fee": 37.645234241322,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1744045200000,
            "side": "sell",
            "quantity": 1.0,
            "price": 77394.7,
            "fee": 30.95788,
        },
        {
            "timestamp": 1744052400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 78106.8499729574,
            "fee": 31.242739989183,
        },
        {
            "timestamp": 1744056000000,
            "side": "sell",
            "quantity": 1.0,
            "price": 78093.59999999999,
            "fee": 31.23744,
        },
        {
            "timestamp": 1744124400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 78302.20893005375,
            "fee": 31.320883572022,
        },
        {
            "timestamp": 1744128000000,
            "side": "sell",
            "quantity": 1.0,
            "price": 78459.79999999999,
            "fee": 31.38392,
        },
    )
    assert canonical_limit_entry_trade_log_digest(result.trade_log) == (
        "e539a7a5b5b11d21db02c486556a075dcc7ae940376b52437a48d1b29ce4550c"
    )
