from __future__ import annotations

import math

import pytest

from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import FillEvent, TickEvent
from quantcraft.trading.domain.intents import OrderIntent
from quantcraft.trading.domain.matching import match_order
from quantcraft.trading.domain.orders import Order
from quantcraft.trading.domain.state import TradingState, apply_fill


def test_market_buy_applies_adverse_slippage_to_best_ask() -> None:
    fill = match_order(
        Order.from_intent(order_id=1, intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="market",
        )),
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((99.0, math.inf),),
            asks=((101.0, math.inf),),
            last=100.0,
        ),
        CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001),
    )

    assert fill == FillEvent(
        symbol="BTC/USDT",
        side="buy",
        quantity=2.0,
        price=102.0,
        timestamp=60,
        fee=0.204,
    )


def test_limit_buy_fills_across_multiple_levels_without_beating_limit() -> None:
    fill = match_order(
        Order.from_intent(order_id=1, intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="limit",
            limit_price=102.0,
        )),
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((99.0, math.inf),),
            asks=((101.0, 1.0), (102.0, 2.0), (103.0, 5.0)),
            last=100.0,
        ),
        CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001),
    )

    assert fill == FillEvent(
        symbol="BTC/USDT",
        side="buy",
        quantity=2.0,
        price=101.5,
        timestamp=60,
        fee=0.203,
    )


def test_limit_order_returns_none_when_book_cannot_fill_within_limit() -> None:
    fill = match_order(
        Order.from_intent(order_id=1, intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="limit",
            limit_price=101.0,
        )),
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((99.0, math.inf),),
            asks=((101.0, 1.0), (102.0, 2.0)),
            last=100.0,
        ),
        CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001),
    )

    assert fill is None


def test_market_sell_applies_adverse_slippage_to_best_bid() -> None:
    fill = match_order(
        Order.from_intent(order_id=1, intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=2.0,
            order_type="market",
        )),
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((99.0, math.inf),),
            asks=((101.0, math.inf),),
            last=100.0,
        ),
        CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001),
    )

    assert fill == FillEvent(
        symbol="BTC/USDT",
        side="sell",
        quantity=2.0,
        price=98.0,
        timestamp=60,
        fee=0.196,
    )


def test_limit_sell_fills_across_multiple_levels_without_beating_limit() -> None:
    fill = match_order(
        Order.from_intent(order_id=1, intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=2.0,
            order_type="limit",
            limit_price=98.0,
        )),
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((99.0, 1.0), (98.0, 2.0), (97.0, 5.0)),
            asks=((101.0, math.inf),),
            last=100.0,
        ),
        CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001),
    )

    assert fill == FillEvent(
        symbol="BTC/USDT",
        side="sell",
        quantity=2.0,
        price=98.5,
        timestamp=60,
        fee=0.197,
    )


def test_matching_skips_zero_liquidity_levels() -> None:
    fill = match_order(
        Order.from_intent(order_id=1, intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="limit",
            limit_price=102.0,
        )),
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((99.0, math.inf),),
            asks=((101.0, 0.0), (102.0, 1.0)),
            last=100.0,
        ),
        CostConfig(tick_size=0.5, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert fill == FillEvent(
        symbol="BTC/USDT",
        side="buy",
        quantity=1.0,
        price=102.0,
        timestamp=60,
        fee=0.0,
    )


def test_matching_rejects_symbol_mismatch_between_intent_and_tick() -> None:
    with pytest.raises(ValueError, match="symbol mismatch"):
        match_order(
            Order.from_intent(order_id=1, intent=OrderIntent(
                symbol="ETH/USDT",
                side="buy",
                quantity=1.0,
                order_type="market",
            )),
            TickEvent(
                timestamp=60,
                symbol="BTC/USDT",
                bids=((99.0, math.inf),),
                asks=((101.0, math.inf),),
                last=100.0,
            ),
            CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001),
        )


def test_matching_rejects_non_positive_quantities() -> None:
    with pytest.raises(ValueError, match="positive quantity"):
        match_order(
            Order.from_intent(order_id=1, intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=0.0,
                order_type="market",
            )),
            TickEvent(
                timestamp=60,
                symbol="BTC/USDT",
                bids=((99.0, math.inf),),
                asks=((101.0, math.inf),),
                last=100.0,
            ),
            CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001),
        )


def test_matching_rejects_orders_without_remaining_quantity() -> None:
    order = Order.from_intent(
        order_id=1,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
        ),
    ).apply_fill(
        FillEvent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            price=100.0,
            timestamp=60,
            fee=0.0,
        )
    )

    with pytest.raises(ValueError, match="positive remaining quantity"):
        match_order(
            order,
            TickEvent(
                timestamp=120,
                symbol="BTC/USDT",
                bids=((99.0, math.inf),),
                asks=((101.0, math.inf),),
                last=100.0,
            ),
            CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001),
        )


def test_apply_fill_updates_long_only_state_deterministically() -> None:
    opened = apply_fill(
        TradingState(cash=1_000.0),
        FillEvent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            price=100.0,
            timestamp=60,
            fee=1.0,
        ),
        mark_price=100.0,
    )

    assert opened == TradingState(
        cash=799.0,
        position_quantity=2.0,
        average_entry_price=100.0,
        realized_pnl=0.0,
        unrealized_pnl=0.0,
        equity=999.0,
    )

    closed = apply_fill(
        opened,
        FillEvent(
            symbol="BTC/USDT",
            side="sell",
            quantity=1.0,
            price=110.0,
            timestamp=120,
            fee=0.11,
        ),
        mark_price=110.0,
    )

    assert closed == TradingState(
        cash=908.89,
        position_quantity=1.0,
        average_entry_price=100.0,
        realized_pnl=10.0,
        unrealized_pnl=10.0,
        equity=1_018.89,
    )


def test_apply_fill_rejects_non_positive_quantities() -> None:
    with pytest.raises(ValueError, match="positive quantity"):
        apply_fill(
            TradingState(cash=1_000.0),
            FillEvent(
                symbol="BTC/USDT",
                side="buy",
                quantity=0.0,
                price=100.0,
                timestamp=60,
                fee=0.0,
            ),
            mark_price=100.0,
        )


def test_apply_fill_rejects_short_sells() -> None:
    with pytest.raises(ValueError, match="current long position"):
        apply_fill(
            TradingState(cash=1_000.0),
            FillEvent(
                symbol="BTC/USDT",
                side="sell",
                quantity=1.0,
                price=110.0,
                timestamp=120,
                fee=0.11,
            ),
            mark_price=110.0,
        )


def test_apply_fill_rejects_levered_buys() -> None:
    with pytest.raises(ValueError, match="insufficient cash"):
        apply_fill(
            TradingState(cash=50.0),
            FillEvent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                price=100.0,
                timestamp=60,
                fee=0.1,
            ),
            mark_price=100.0,
        )
