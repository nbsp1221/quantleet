from __future__ import annotations

import math

import pytest

from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import FillEvent, TickEvent
from quantleet.trading.domain.intents import OrderIntent
from quantleet.trading.domain.matching import is_order_triggered, match_order
from quantleet.trading.domain.orders import Order
from quantleet.trading.domain.state import TradingState, apply_fill


def test_market_buy_applies_adverse_slippage_to_best_ask() -> None:
    fill = match_order(
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=2.0,
                order_type="market",
            ),
        ),
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
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=2.0,
                order_type="limit",
                limit_price=102.0,
            ),
        ),
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
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=2.0,
                order_type="limit",
                limit_price=101.0,
            ),
        ),
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


def test_dormant_stop_market_returns_no_fill_until_triggered() -> None:
    fill = match_order(
        Order.from_intent(
            order_id=11,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                order_type="stop_market",
                trigger_price=110.0,
                trigger_condition="crosses_above",
                trigger_type="last",
            ),
        ),
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((99.0, math.inf),),
            asks=((101.0, math.inf),),
            last=100.0,
        ),
        CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001),
    )

    assert fill is None


def test_dormant_stop_limit_returns_no_fill_until_triggered() -> None:
    fill = match_order(
        Order.from_intent(
            order_id=11,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                order_type="stop_limit",
                trigger_price=110.0,
                trigger_condition="crosses_above",
                trigger_type="last",
                limit_price=110.0,
            ),
        ),
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((99.0, math.inf),),
            asks=((100.0, math.inf),),
            last=100.0,
        ),
        CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001),
    )

    assert fill is None


def test_crosses_above_triggers_on_equality_and_gap_through() -> None:
    order = Order.from_intent(
        order_id=12,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=110.0,
            trigger_condition="crosses_above",
            trigger_type="last",
        ),
    )

    assert is_order_triggered(
        order,
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((110.0, math.inf),),
            asks=((110.0, math.inf),),
            last=110.0,
        ),
    )
    assert is_order_triggered(
        order,
        TickEvent(
            timestamp=120,
            symbol="BTC/USDT",
            bids=((120.0, math.inf),),
            asks=((120.0, math.inf),),
            last=120.0,
        ),
    )


def test_crosses_below_triggers_on_equality_and_gap_through() -> None:
    order = Order.from_intent(
        order_id=13,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=95.0,
            trigger_condition="crosses_below",
            trigger_type="last",
        ),
    )

    assert is_order_triggered(
        order,
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((95.0, math.inf),),
            asks=((95.0, math.inf),),
            last=95.0,
        ),
    )


def test_stop_limit_trigger_detection_uses_stop_family_predicate() -> None:
    order = Order.from_intent(
        order_id=13,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_limit",
            trigger_price=110.0,
            trigger_condition="crosses_above",
            trigger_type="last",
            limit_price=111.0,
        ),
    )
    tick = TickEvent(
        timestamp=60,
        symbol="BTC/USDT",
        bids=((110.0, math.inf),),
        asks=((110.0, math.inf),),
        last=110.0,
    )

    assert is_order_triggered(order, tick) is True
    assert is_order_triggered(order.trigger(timestamp=60), tick) is False


def test_is_order_triggered_returns_false_for_non_stop_and_already_triggered_orders() -> None:
    ordinary = Order.from_intent(
        order_id=16,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
        ),
    )
    stop = Order.from_intent(
        order_id=17,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=110.0,
            trigger_condition="crosses_above",
            trigger_type="last",
        ),
    ).trigger(timestamp=60)
    tick = TickEvent(
        timestamp=120,
        symbol="BTC/USDT",
        bids=((120.0, math.inf),),
        asks=((120.0, math.inf),),
        last=120.0,
    )

    assert is_order_triggered(ordinary, tick) is False
    assert is_order_triggered(stop, tick) is False


def test_is_order_triggered_rejects_symbol_mismatch_and_invalid_trigger_shape() -> None:
    order = Order.from_intent(
        order_id=18,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=110.0,
            trigger_condition="crosses_above",
            trigger_type="last",
        ),
    )

    with pytest.raises(ValueError, match="symbol mismatch"):
        is_order_triggered(
            order,
            TickEvent(
                timestamp=60,
                symbol="ETH/USDT",
                bids=((110.0, math.inf),),
                asks=((110.0, math.inf),),
                last=110.0,
            ),
        )

    object.__setattr__(order, "trigger_type", "mark")
    with pytest.raises(ValueError, match="unsupported trigger_type"):
        is_order_triggered(
            order,
            TickEvent(
                timestamp=120,
                symbol="BTC/USDT",
                bids=((120.0, math.inf),),
                asks=((120.0, math.inf),),
                last=120.0,
            ),
        )

    object.__setattr__(order, "trigger_type", "last")
    object.__setattr__(order, "trigger_condition", None)
    with pytest.raises(ValueError, match="trigger facts must be present"):
        is_order_triggered(
            order,
            TickEvent(
                timestamp=180,
                symbol="BTC/USDT",
                bids=((120.0, math.inf),),
                asks=((120.0, math.inf),),
                last=120.0,
            ),
        )


def test_triggered_stop_market_reuses_market_fill_semantics() -> None:
    tick = TickEvent(
        timestamp=60,
        symbol="BTC/USDT",
        bids=((99.0, math.inf),),
        asks=((101.0, math.inf),),
        last=110.0,
    )
    costs = CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001)
    ordinary_market = Order.from_intent(
        order_id=14,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="market",
        ),
    )
    stop_market = Order.from_intent(
        order_id=15,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="stop_market",
            trigger_price=110.0,
            trigger_condition="crosses_above",
            trigger_type="last",
        ),
    ).trigger(timestamp=60)

    assert match_order(stop_market, tick, costs) == match_order(ordinary_market, tick, costs)


def test_triggered_stop_limit_buy_reuses_limit_fill_semantics() -> None:
    tick = TickEvent(
        timestamp=60,
        symbol="BTC/USDT",
        bids=((99.0, math.inf),),
        asks=((105.0, math.inf),),
        last=105.0,
    )
    costs = CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001)
    ordinary_limit = Order.from_intent(
        order_id=14,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="limit",
            limit_price=106.0,
        ),
    )
    stop_limit = Order.from_intent(
        order_id=15,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="stop_limit",
            trigger_price=105.0,
            trigger_condition="crosses_above",
            trigger_type="last",
            limit_price=106.0,
        ),
    ).trigger(timestamp=60)

    assert match_order(stop_limit, tick, costs) == match_order(ordinary_limit, tick, costs)


def test_triggered_stop_limit_buy_remains_unfilled_when_worse_than_limit() -> None:
    fill = match_order(
        Order.from_intent(
            order_id=15,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=2.0,
                order_type="stop_limit",
                trigger_price=105.0,
                trigger_condition="crosses_above",
                trigger_type="last",
                limit_price=106.0,
            ),
        ).trigger(timestamp=60),
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((109.0, math.inf),),
            asks=((110.0, math.inf),),
            last=110.0,
        ),
        CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001),
    )

    assert fill is None


def test_market_sell_applies_adverse_slippage_to_best_bid() -> None:
    fill = match_order(
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="sell",
                quantity=2.0,
                order_type="market",
            ),
        ),
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
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="sell",
                quantity=2.0,
                order_type="limit",
                limit_price=98.0,
            ),
        ),
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


def test_triggered_stop_limit_sell_reuses_limit_fill_semantics() -> None:
    tick = TickEvent(
        timestamp=60,
        symbol="BTC/USDT",
        bids=((95.0, math.inf),),
        asks=((97.0, math.inf),),
        last=95.0,
    )
    costs = CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001)
    ordinary_limit = Order.from_intent(
        order_id=14,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=2.0,
            order_type="limit",
            limit_price=94.0,
        ),
    )
    stop_limit = Order.from_intent(
        order_id=15,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=2.0,
            order_type="stop_limit",
            trigger_price=95.0,
            trigger_condition="crosses_below",
            trigger_type="last",
            limit_price=94.0,
        ),
    ).trigger(timestamp=60)

    assert match_order(stop_limit, tick, costs) == match_order(ordinary_limit, tick, costs)


def test_triggered_stop_limit_sell_remains_unfilled_when_worse_than_limit() -> None:
    fill = match_order(
        Order.from_intent(
            order_id=15,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="sell",
                quantity=2.0,
                order_type="stop_limit",
                trigger_price=95.0,
                trigger_condition="crosses_below",
                trigger_type="last",
                limit_price=94.0,
            ),
        ).trigger(timestamp=60),
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((90.0, math.inf),),
            asks=((91.0, math.inf),),
            last=90.0,
        ),
        CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.001),
    )

    assert fill is None


def test_matching_skips_zero_liquidity_levels() -> None:
    fill = match_order(
        Order.from_intent(
            order_id=1,
            intent=OrderIntent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                order_type="limit",
                limit_price=102.0,
            ),
        ),
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
            Order.from_intent(
                order_id=1,
                intent=OrderIntent(
                    symbol="ETH/USDT",
                    side="buy",
                    quantity=1.0,
                    order_type="market",
                ),
            ),
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
    with pytest.raises(ValueError, match="positive finite quantity"):
        match_order(
            Order.from_intent(
                order_id=1,
                intent=OrderIntent(
                    symbol="BTC/USDT",
                    side="buy",
                    quantity=0.0,
                    order_type="market",
                ),
            ),
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


def test_apply_fill_updates_weighted_average_and_mark_to_market_state() -> None:
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
        mark_price=115.0,
    )
    increased = apply_fill(
        opened,
        FillEvent(
            symbol="BTC/USDT",
            side="buy",
            quantity=3.0,
            price=120.0,
            timestamp=120,
            fee=1.8,
        ),
        mark_price=130.0,
    )

    assert opened == TradingState(
        cash=799.0,
        position_quantity=2.0,
        average_entry_price=100.0,
        realized_pnl=0.0,
        unrealized_pnl=30.0,
        equity=1_029.0,
    )
    assert increased == TradingState(
        cash=437.2,
        position_quantity=5.0,
        average_entry_price=112.0,
        realized_pnl=0.0,
        unrealized_pnl=90.0,
        equity=1_087.2,
    )


def test_apply_fill_allows_buy_that_exactly_spends_available_cash() -> None:
    state = apply_fill(
        TradingState(cash=101.0),
        FillEvent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            price=100.0,
            timestamp=60,
            fee=1.0,
        ),
        mark_price=100.0,
    )

    assert state == TradingState(
        cash=0.0,
        position_quantity=1.0,
        average_entry_price=100.0,
        realized_pnl=0.0,
        unrealized_pnl=0.0,
        equity=100.0,
    )


def test_apply_fill_accumulates_realized_pnl_and_resets_on_full_close() -> None:
    state = TradingState(
        cash=437.2,
        position_quantity=5.0,
        average_entry_price=112.0,
        realized_pnl=0.0,
        unrealized_pnl=90.0,
        equity=1_087.2,
    )

    profitable_partial = apply_fill(
        state,
        FillEvent(
            symbol="BTC/USDT",
            side="sell",
            quantity=2.0,
            price=130.0,
            timestamp=180,
            fee=0.26,
        ),
        mark_price=125.0,
    )
    losing_partial = apply_fill(
        profitable_partial,
        FillEvent(
            symbol="BTC/USDT",
            side="sell",
            quantity=1.0,
            price=90.0,
            timestamp=240,
            fee=0.09,
        ),
        mark_price=95.0,
    )
    closed = apply_fill(
        losing_partial,
        FillEvent(
            symbol="BTC/USDT",
            side="sell",
            quantity=2.0,
            price=110.0,
            timestamp=300,
            fee=0.22,
        ),
        mark_price=200.0,
    )

    assert profitable_partial == TradingState(
        cash=696.94,
        position_quantity=3.0,
        average_entry_price=112.0,
        realized_pnl=36.0,
        unrealized_pnl=39.0,
        equity=1_071.94,
    )
    assert losing_partial == TradingState(
        cash=786.85,
        position_quantity=2.0,
        average_entry_price=112.0,
        realized_pnl=14.0,
        unrealized_pnl=-34.0,
        equity=976.85,
    )
    assert closed == TradingState(
        cash=1_006.63,
        position_quantity=0.0,
        average_entry_price=0.0,
        realized_pnl=10.0,
        unrealized_pnl=0.0,
        equity=1_006.63,
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
