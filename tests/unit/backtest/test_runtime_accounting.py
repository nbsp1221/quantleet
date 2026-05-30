from __future__ import annotations

import pytest

from quantleet.backtest.analytics import drawdown_for_equity, max_drawdown_from_curve
from quantleet.backtest.runtime import (
    _allocated_entry_fee,
    _apply_runtime_fill,
    _mark_state_to_market,
    _net_closed_trade_pnl,
    _runtime_fill_rejection,
    _update_buy_reservation_after_fill,
)
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import FillEvent
from quantleet.trading.domain.intents import OrderIntent
from quantleet.trading.domain.orders import Order
from quantleet.trading.domain.state import TradingState


def _order(
    *,
    order_id: int = 1,
    side: str = "buy",
    quantity: float = 2.0,
    limit_price: float = 30.0,
) -> Order:
    return Order.from_intent(
        order_id=order_id,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side=side,
            quantity=quantity,
            order_type="limit",
            limit_price=limit_price,
        ),
    )


def _fill(*, side: str = "buy", quantity: float = 1.0, price: float = 30.0) -> FillEvent:
    return FillEvent(
        symbol="BTC/USDT",
        side=side,
        quantity=quantity,
        price=price,
        timestamp=120,
        fee=0.1234567890123,
    )


def test_update_buy_reservation_decrements_partial_fill_with_public_precision() -> None:
    fill = _fill()
    partially_filled = _order().apply_fill(fill=fill)
    reservations = {partially_filled.id: 100.0}

    _update_buy_reservation_after_fill(
        reservations=reservations,
        order=partially_filled,
        fill=fill,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert reservations == {1: 69.876543210988}


def test_update_buy_reservation_removes_completed_buy_and_ignores_sells() -> None:
    buy_fill = _fill(quantity=2.0)
    completed_buy = _order().apply_fill(fill=buy_fill)
    reservations = {completed_buy.id: 100.0, 99: 42.0}

    _update_buy_reservation_after_fill(
        reservations=reservations,
        order=completed_buy,
        fill=buy_fill,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert reservations == {99: 42.0}

    sell_fill = _fill(side="sell")
    _update_buy_reservation_after_fill(
        reservations=reservations,
        order=_order(order_id=2, side="sell"),
        fill=sell_fill,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    )

    assert reservations == {99: 42.0}


def test_runtime_fill_rejection_uses_reservation_plus_unreserved_cash_boundary() -> None:
    order = _order(order_id=5, quantity=1.0, limit_price=10.0)
    state = TradingState(cash=15.0, equity=15.0)

    accepted = _runtime_fill_rejection(
        state=state,
        order=order,
        fill=FillEvent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            price=10.0,
            timestamp=120,
            fee=0.0,
        ),
        buy_reservations={99: 5.0},
        timestamp=120,
    )
    rejected = _runtime_fill_rejection(
        state=state,
        order=order,
        fill=FillEvent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            price=10.0,
            timestamp=120,
            fee=0.000000000002,
        ),
        buy_reservations={5: 10.0, 99: 5.0},
        timestamp=120,
    )

    assert accepted is None
    assert rejected is not None
    assert rejected.reason == "execution_affordability"
    assert rejected.quantity == 1.0
    assert rejected.order_id == 5


def test_runtime_fill_rejection_preserves_public_cash_precision_boundary() -> None:
    rejection = _runtime_fill_rejection(
        state=TradingState(cash=10.0000000000001, equity=10.0000000000001),
        order=_order(order_id=6, quantity=1.0, limit_price=10.0),
        fill=FillEvent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            price=10.0,
            timestamp=120,
            fee=0.0000000000006,
        ),
        buy_reservations={6: 10.0000000000001},
        timestamp=120,
    )

    assert rejection is not None
    assert rejection.reason == "execution_affordability"


def test_mark_state_to_market_preserves_flat_state_and_rounds_equity() -> None:
    state = TradingState(
        cash=100.1234567890123,
        position_quantity=-0.5,
        average_entry_price=12.5,
        realized_pnl=3.0,
        unrealized_pnl=99.0,
        equity=0.0,
    )

    marked = _mark_state_to_market(state, mark_price=20.0)

    assert marked == TradingState(
        cash=100.1234567890123,
        position_quantity=-0.5,
        average_entry_price=12.5,
        realized_pnl=3.0,
        unrealized_pnl=0.0,
        equity=100.123456789012,
    )


def test_entry_fee_allocation_requires_open_position_and_rounds_allocated_fee() -> None:
    fill = _fill(side="sell", quantity=0.333333333333, price=130.0)

    with pytest.raises(ValueError, match="cannot allocate entry fees without an open position"):
        _allocated_entry_fee(
            open_entry_fee_pool=1.0,
            fill=fill,
            state=TradingState(cash=100.0, position_quantity=0.0),
        )

    assert (
        _allocated_entry_fee(
            open_entry_fee_pool=1.0,
            fill=fill,
            state=TradingState(cash=100.0, position_quantity=3.0),
        )
        == 0.111111111111
    )


def test_net_closed_trade_pnl_subtracts_allocated_entry_and_exit_fees() -> None:
    assert (
        _net_closed_trade_pnl(
            state=TradingState(cash=0.0, position_quantity=1.0, average_entry_price=100.0),
            fill=FillEvent(
                symbol="BTC/USDT",
                side="sell",
                quantity=0.333333333333,
                price=130.0,
                timestamp=120,
                fee=0.222222222222,
            ),
            allocated_entry_fee=0.111111111111,
        )
        == 9.666666666657
    )


def test_apply_runtime_fill_allocates_partial_exit_fee_pool_and_closed_net_pnl() -> None:
    order = _order(order_id=7, side="sell", quantity=0.333333333333, limit_price=130.0)
    fill = FillEvent(
        symbol="BTC/USDT",
        side="sell",
        quantity=0.333333333333,
        price=130.0,
        timestamp=120,
        fee=0.222222222222,
    )
    closing_trade_pnls: list[float] = []
    trade_log: list[FillEvent] = []

    state, open_entry_fee_pool, filled_order = _apply_runtime_fill(
        state=TradingState(cash=100.0, position_quantity=3.0, average_entry_price=100.0),
        order=order,
        fill=fill,
        mark_price=130.0,
        open_entry_fee_pool=1.0,
        closing_trade_pnls=closing_trade_pnls,
        trade_log=trade_log,
    )

    assert state.position_quantity == 2.666666666667
    assert state.realized_pnl == pytest.approx(9.99999999999)
    assert open_entry_fee_pool == 0.888888888889
    assert closing_trade_pnls == [9.666666666657]
    assert trade_log == [fill]
    assert filled_order.filled_quantity == 0.333333333333


def test_drawdown_helpers_preserve_zero_and_low_positive_equity_boundaries() -> None:
    assert max_drawdown_from_curve(()) == 0.0
    assert drawdown_for_equity(running_peak=0.5, equity=0.25) == 0.5
