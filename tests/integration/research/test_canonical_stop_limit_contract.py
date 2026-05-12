from __future__ import annotations

from quantleet.data import TimeBar
from quantleet.trading.domain.costs import CostConfig
from tests.integration.research.support_backtest_runner import (
    BuyStopLimitStrategy,
    SellStopLimitStrategy,
    StopLimitConfig,
    make_bar_series,
    run_engine_backtest,
)

_ZERO_COSTS = CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0)


def test_canonical_buy_stop_limit_trigger_and_fill_public_outcome() -> None:
    result = run_engine_backtest(
        bars=make_bar_series(
            (
                TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
                TimeBar(timestamp=120, open=100.0, high=106.0, low=99.0, close=104.0, volume=12.0),
            )
        ),
        strategy=BuyStopLimitStrategy,
        config=StopLimitConfig(stop_price=105.0, limit_price=106.0),
        costs=_ZERO_COSTS,
    )

    assert tuple(
        (fill.side, fill.quantity, fill.price, fill.timestamp) for fill in result.trade_log
    ) == (("buy", 1.0, 105.0, 120),)
    assert result.final_state.position_quantity == 1.0
    assert result.summary.total_fills == 1


def test_canonical_buy_stop_limit_trigger_without_fill_public_outcome() -> None:
    result = run_engine_backtest(
        bars=make_bar_series(
            (
                TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
                TimeBar(timestamp=120, open=110.0, high=112.0, low=108.0, close=111.0, volume=12.0),
            )
        ),
        strategy=BuyStopLimitStrategy,
        config=StopLimitConfig(stop_price=105.0, limit_price=106.0),
        costs=_ZERO_COSTS,
    )

    assert result.trade_log == ()
    assert result.final_state.position_quantity == 0.0
    assert result.summary.total_fills == 0


def test_canonical_sell_stop_limit_trigger_and_fill_public_outcome() -> None:
    result = run_engine_backtest(
        bars=make_bar_series(
            (
                TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
                TimeBar(timestamp=120, open=100.0, high=101.0, low=99.0, close=100.0, volume=12.0),
                TimeBar(timestamp=180, open=100.0, high=101.0, low=94.0, close=96.0, volume=14.0),
            )
        ),
        strategy=SellStopLimitStrategy,
        config=StopLimitConfig(stop_price=95.0, limit_price=94.0),
        costs=_ZERO_COSTS,
    )

    assert tuple(
        (fill.side, fill.quantity, fill.price, fill.timestamp) for fill in result.trade_log
    ) == (
        ("buy", 1.0, 100.0, 120),
        ("sell", 1.0, 95.0, 180),
    )
    assert result.final_state.position_quantity == 0.0
    assert result.summary.total_fills == 2


def test_canonical_sell_stop_limit_trigger_without_fill_public_outcome() -> None:
    result = run_engine_backtest(
        bars=make_bar_series(
            (
                TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
                TimeBar(timestamp=120, open=100.0, high=101.0, low=99.0, close=100.0, volume=12.0),
                TimeBar(timestamp=180, open=90.0, high=92.0, low=88.0, close=91.0, volume=14.0),
            )
        ),
        strategy=SellStopLimitStrategy,
        config=StopLimitConfig(stop_price=95.0, limit_price=94.0),
        costs=_ZERO_COSTS,
    )

    assert tuple(
        (fill.side, fill.quantity, fill.price, fill.timestamp) for fill in result.trade_log
    ) == (("buy", 1.0, 100.0, 120),)
    assert result.final_state.position_quantity == 1.0
    assert result.summary.total_fills == 1
