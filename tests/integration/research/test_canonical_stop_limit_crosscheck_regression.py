from __future__ import annotations

import pytest

from quantleet.backtest import BacktestSummary, ExposureSummary
from tests.support_backtest import (
    canonical_stop_limit_buy_trade_log_digest,
    canonical_stop_limit_donchian_trade_log_digest,
    canonical_stop_limit_donchian_trade_log_samples,
    canonical_stop_limit_inside_bar_trade_log_digest,
    canonical_stop_limit_inside_bar_trade_log_samples,
    canonical_stop_limit_opening_range_trade_log_digest,
    canonical_stop_limit_opening_range_trade_log_samples,
    load_canonical_stop_limit_donchian_bars,
    load_canonical_stop_limit_inside_bar_bars,
    load_canonical_stop_limit_opening_range_bars,
    run_canonical_stop_limit_donchian_backtest,
    run_canonical_stop_limit_inside_bar_backtest,
    run_canonical_stop_limit_opening_range_backtest,
)


def test_canonical_stop_limit_opening_range_pins_entry_evidence_and_full_regression() -> None:
    result = run_canonical_stop_limit_opening_range_backtest(
        load_canonical_stop_limit_opening_range_bars()
    )

    assert canonical_stop_limit_buy_trade_log_digest(result.trade_log) == (
        "c363b95498cfe981d8c289db72b0ab3755f995af56bfa94e8adaecebc2d1a925"
    )

    # Cross-engine evidence covers stop-limit entry fills; full output is Quantleet's
    # canonical regression snapshot, including its market-exit and cost policies.
    assert result.summary == BacktestSummary(
        total_trades=31,
        total_fills=62,
        total_fees=pytest.approx(2682.94784),
        final_balance=pytest.approx(992447.2521599995),
        final_equity=pytest.approx(992447.2521599995),
        total_return=pytest.approx(-0.00755274784),
        max_drawdown=pytest.approx(0.017636316859),
        realized_pnl=pytest.approx(-4869.800000000292),
        unrealized_pnl=0.0,
        win_rate=pytest.approx(0.41935483871),
        average_win=pytest.approx(1635.497058461529),
        average_loss=pytest.approx(1600.789422222232),
        profit_factor=pytest.approx(0.737881137645),
        exposure=ExposureSummary(
            bars_in_position=775,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.0884703196347032),
        ),
    )

    first_fills, last_fills = canonical_stop_limit_opening_range_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1735743600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 94449.3,
            "fee": 37.77972,
        },
        {
            "timestamp": 1735833600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 96428.4,
            "fee": 38.57136,
        },
        {
            "timestamp": 1735916400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 97325.8,
            "fee": 38.93032,
        },
        {
            "timestamp": 1736006400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 97623.4,
            "fee": 39.04936,
        },
        {
            "timestamp": 1736017200000,
            "side": "buy",
            "quantity": 1.0,
            "price": 98272.70000000001,
            "fee": 39.30908,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1755093600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 121777.2,
            "fee": 48.71088,
        },
        {
            "timestamp": 1759636800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 124545.70000000001,
            "fee": 49.81828,
        },
        {
            "timestamp": 1759726800000,
            "side": "sell",
            "quantity": 1.0,
            "price": 123538.09999999999,
            "fee": 49.41524,
        },
        {
            "timestamp": 1759748400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 124336.40000000001,
            "fee": 49.73456,
        },
        {
            "timestamp": 1759838400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 124397.0,
            "fee": 49.7588,
        },
    )
    assert canonical_stop_limit_opening_range_trade_log_digest(result.trade_log) == (
        "245f98ed2d822c1d26299a3c04050f73ea35a741da2c24d433952852bad8f046"
    )


def test_canonical_stop_limit_donchian_pins_entry_evidence_and_full_regression() -> None:
    result = run_canonical_stop_limit_donchian_backtest(load_canonical_stop_limit_donchian_bars())

    assert canonical_stop_limit_buy_trade_log_digest(result.trade_log) == (
        "6da6a52ca5c224cf67a5d4c22532d4d04a20909b8e0c2e5a551fc196aef57ad9"
    )

    # Cross-engine evidence covers stop-limit entry fills; full output is Quantleet's
    # canonical regression snapshot, including its market-exit and cost policies.
    assert result.summary == BacktestSummary(
        total_trades=14,
        total_fills=28,
        total_fees=pytest.approx(1222.35876),
        final_balance=pytest.approx(1000670.1412399996),
        final_equity=pytest.approx(1000670.1412399996),
        total_return=pytest.approx(0.00067014124),
        max_drawdown=pytest.approx(0.009276083229),
        realized_pnl=pytest.approx(1892.499999999852),
        unrealized_pnl=0.0,
        win_rate=pytest.approx(0.571428571429),
        average_win=pytest.approx(2053.378534999988),
        average_loss=pytest.approx(2626.147840000008),
        profit_factor=pytest.approx(1.042530052941),
        exposure=ExposureSummary(
            bars_in_position=350,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.03995433789954338),
        ),
    )

    first_fills, last_fills = canonical_stop_limit_donchian_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1735765200000,
            "side": "buy",
            "quantity": 1.0,
            "price": 94823.3,
            "fee": 37.92932,
        },
        {
            "timestamp": 1735855200000,
            "side": "sell",
            "quantity": 1.0,
            "price": 97179.9,
            "fee": 38.87196,
        },
        {
            "timestamp": 1735920000000,
            "side": "buy",
            "quantity": 1.0,
            "price": 97822.5,
            "fee": 39.129,
        },
        {
            "timestamp": 1736010000000,
            "side": "sell",
            "quantity": 1.0,
            "price": 97677.7,
            "fee": 39.07108,
        },
        {
            "timestamp": 1736020800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 98481.20000000001,
            "fee": 39.39248,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1755212400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 118230.0,
            "fee": 47.292,
        },
        {
            "timestamp": 1759629600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 123923.20000000001,
            "fee": 49.56928,
        },
        {
            "timestamp": 1759719600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 124066.7,
            "fee": 49.62668,
        },
        {
            "timestamp": 1759759200000,
            "side": "buy",
            "quantity": 1.0,
            "price": 125147.1,
            "fee": 50.05884,
        },
        {
            "timestamp": 1759849200000,
            "side": "sell",
            "quantity": 1.0,
            "price": 122684.0,
            "fee": 49.0736,
        },
    )
    assert canonical_stop_limit_donchian_trade_log_digest(result.trade_log) == (
        "85b09951f22bf0fad23fc1ddb0a384f9a64a2598bbde11347f3d7e3ad9f52a7c"
    )


def test_canonical_stop_limit_inside_bar_pins_entry_evidence_and_full_regression() -> None:
    result = run_canonical_stop_limit_inside_bar_backtest(
        load_canonical_stop_limit_inside_bar_bars()
    )

    assert canonical_stop_limit_buy_trade_log_digest(result.trade_log) == (
        "e3c64692347ae87144fd681ecc67f09e69960a4f0a4a9a44b087d87c1178bb70"
    )

    # Cross-engine evidence covers stop-limit entry fills; full output is Quantleet's
    # canonical regression snapshot, including its market-exit and cost policies.
    assert result.summary == BacktestSummary(
        total_trades=32,
        total_fills=64,
        total_fees=pytest.approx(2883.92504),
        final_balance=pytest.approx(1007345.0749599993),
        final_equity=pytest.approx(1007345.0749599993),
        total_return=pytest.approx(0.00734507496),
        max_drawdown=pytest.approx(0.01091148869),
        realized_pnl=pytest.approx(10228.99999999965),
        unrealized_pnl=0.0,
        win_rate=pytest.approx(0.5),
        average_win=pytest.approx(1766.546142499989),
        average_loss=pytest.approx(1307.478957500011),
        profit_factor=pytest.approx(1.351108660194),
        exposure=ExposureSummary(
            bars_in_position=800,
            total_bars=8760,
            exposure_ratio=pytest.approx(0.091324200913242),
        ),
    )

    first_fills, last_fills = canonical_stop_limit_inside_bar_trade_log_samples(result.trade_log)
    assert first_fills == (
        {
            "timestamp": 1735743600000,
            "side": "buy",
            "quantity": 1.0,
            "price": 94449.3,
            "fee": 37.77972,
        },
        {
            "timestamp": 1735833600000,
            "side": "sell",
            "quantity": 1.0,
            "price": 96428.4,
            "fee": 38.57136,
        },
        {
            "timestamp": 1735844400000,
            "side": "buy",
            "quantity": 1.0,
            "price": 97650.1,
            "fee": 39.06004,
        },
        {
            "timestamp": 1735934400000,
            "side": "sell",
            "quantity": 1.0,
            "price": 98545.5,
            "fee": 39.4182,
        },
        {
            "timestamp": 1735974000000,
            "side": "buy",
            "quantity": 1.0,
            "price": 98272.70000000001,
            "fee": 39.30908,
        },
    )
    assert last_fills == (
        {
            "timestamp": 1760389200000,
            "side": "sell",
            "quantity": 1.0,
            "price": 115656.79999999999,
            "fee": 46.26272,
        },
        {
            "timestamp": 1761544800000,
            "side": "buy",
            "quantity": 1.0,
            "price": 115817.5,
            "fee": 46.327,
        },
        {
            "timestamp": 1761634800000,
            "side": "sell",
            "quantity": 1.0,
            "price": 114060.0,
            "fee": 45.624,
        },
        {
            "timestamp": 1761649200000,
            "side": "buy",
            "quantity": 1.0,
            "price": 114588.1,
            "fee": 45.83524,
        },
        {
            "timestamp": 1761739200000,
            "side": "sell",
            "quantity": 1.0,
            "price": 113084.5,
            "fee": 45.2338,
        },
    )
    assert canonical_stop_limit_inside_bar_trade_log_digest(result.trade_log) == (
        "3e25460c2df8b6cfbe33e1af943b2f9de3177c1c1598b35689635b617417e3a7"
    )
