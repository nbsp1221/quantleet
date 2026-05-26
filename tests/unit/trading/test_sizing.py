from __future__ import annotations

import pytest

from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.intents import OrderIntent
from quantleet.trading.domain.orders import Order
from quantleet.trading.domain.state import TradingState
from quantleet.trading.order_requests import PendingOrderRequest
from quantleet.trading.sizing import (
    SizingConstraints,
    SizingReservations,
    resolve_pending_order_request,
)


def _fill_stub(*, symbol: str, side: str, quantity: float, price: float, timestamp: int = 60):
    return type(
        "FillStub",
        (),
        {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "timestamp": timestamp,
            "fee": 0.0,
        },
    )()


def test_buy_qty_percent_preserves_requested_position_budget_when_affordable() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=80.0, equity=80.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.01),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 4.0
    assert result.position_budget == 40.0
    assert result.cash_consumption == 40.4
    assert result.sell_quantity_reservation == 0.0


def test_buy_qty_percent_clamps_only_when_requested_budget_plus_fees_is_unaffordable() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=100.0,
            order_type="market",
        ),
        state=TradingState(cash=80.0, equity=80.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.01),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == pytest.approx(80.0 / 10.1)
    assert result.position_budget == pytest.approx(80.0 / 1.01)
    assert result.cash_consumption == pytest.approx(80.0)
    assert result.sell_quantity_reservation == 0.0


def test_buy_qty_percent_clamps_with_full_fee_rate_without_rejecting_affordable_order() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=100.0,
            order_type="market",
        ),
        state=TradingState(cash=80.0, equity=80.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=1.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 4.0
    assert result.position_budget == 40.0
    assert result.cash_consumption == 80.0


def test_buy_qty_percent_uses_remaining_buy_reservations_when_computing_basis() -> None:
    active_buy = Order.from_intent(
        order_id=1,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="limit",
            limit_price=10.0,
        ),
    ).apply_fill(fill=_fill_stub(symbol="BTC/USDT", side="buy", quantity=1.0, price=10.0))

    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(active_buy,),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 4.5
    assert result.position_budget == 45.0
    assert result.cash_consumption == 45.0
    assert result.sell_quantity_reservation == 0.0


def test_sell_qty_percent_uses_net_closable_quantity_after_active_exit_reservations() -> None:
    active_exit = Order.from_intent(
        order_id=2,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=4.0,
            order_type="limit",
            limit_price=12.0,
        ),
    ).apply_fill(fill=_fill_stub(symbol="BTC/USDT", side="sell", quantity=1.0, price=12.0))

    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            qty_percent=30.0,
            order_type="market",
        ),
        state=TradingState(
            cash=0.0, equity=100.0, position_quantity=10.0, average_entry_price=10.0
        ),
        active_orders=(active_exit,),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 2.1
    assert result.position_budget == 0.0
    assert result.cash_consumption == 0.0
    assert result.sell_quantity_reservation == 2.1


def test_subminimum_or_flat_percent_requests_resolve_to_explicit_noop() -> None:
    constraints = SizingConstraints(quantity_increment=1.0, min_quantity=1.0)

    tiny_buy = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=10.0,
            order_type="market",
        ),
        state=TradingState(cash=5.0, equity=5.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=constraints,
    )
    flat_sell = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            qty_percent=100.0,
            order_type="market",
        ),
        state=TradingState(cash=5.0, equity=5.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=constraints,
    )

    assert tiny_buy.quantity is None
    assert tiny_buy.reason == "below_minimum_size"
    assert flat_sell.quantity is None
    assert flat_sell.reason == "no_closable_position"


def test_buy_percent_serial_reservation_uses_resolved_order_budget_after_rounding() -> None:
    first = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(quantity_increment=3.0),
    )

    second = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(quantity_increment=3.0),
        reservations=SizingReservations().reserve(first),
    )

    assert first.quantity == 3.0
    assert first.position_budget == 30.0
    assert first.cash_consumption == 30.0
    assert second.quantity == 3.0
    assert second.position_budget == 30.0
    assert second.cash_consumption == 30.0


def test_dormant_stop_market_buys_reduce_ordinary_buy_percent_budget() -> None:
    dormant_stop = Order.from_intent(
        order_id=3,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="stop_market",
            trigger_price=15.0,
            trigger_condition="crosses_above",
            trigger_type="last",
        ),
    )

    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(dormant_stop,),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 3.5
    assert result.position_budget == 35.0
    assert result.cash_consumption == 35.0


def test_dormant_stop_limit_buys_reduce_ordinary_buy_percent_budget() -> None:
    dormant_stop = Order.from_intent(
        order_id=3,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="stop_limit",
            trigger_price=15.0,
            trigger_condition="crosses_above",
            trigger_type="last",
            limit_price=16.0,
        ),
    )

    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(dormant_stop,),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 3.4
    assert result.position_budget == 34.0
    assert result.cash_consumption == 34.0


def test_triggered_stop_limit_buys_reserve_cash_like_ordinary_limits() -> None:
    triggered_stop = Order.from_intent(
        order_id=3,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="stop_limit",
            trigger_price=15.0,
            trigger_condition="crosses_above",
            trigger_type="last",
            limit_price=10.0,
        ),
    ).trigger(timestamp=60)

    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(triggered_stop,),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 4.0
    assert result.position_budget == 40.0
    assert result.cash_consumption == 40.0


def test_quantity_based_stop_limit_buy_rejects_when_unaffordable_before_trigger() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="stop_limit",
            stop_price=15.0,
            trigger_condition="crosses_above",
            limit_price=16.0,
        ),
        state=TradingState(cash=1.0, equity=1.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(min_cost=100.0),
    )

    assert result.reason == "insufficient_cash"
    assert result.quantity is None
    assert result.cash_consumption == 0.0


def test_buy_qty_percent_stop_market_uses_stop_price_plus_slippage() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="stop_market",
            stop_price=25.0,
            trigger_condition="crosses_above",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == pytest.approx(50.0 / 26.0)
    assert result.position_budget == pytest.approx(50.0)
    assert result.cash_consumption == pytest.approx(50.0)


def test_buy_qty_percent_stop_limit_uses_limit_price_not_stop_price() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="stop_limit",
            stop_price=25.0,
            trigger_condition="crosses_above",
            limit_price=20.0,
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 2.5
    assert result.position_budget == 50.0
    assert result.cash_consumption == 50.0


def test_explicit_quantity_market_buy_records_budget_and_fee_cash_consumption() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            quantity=3.2,
            order_type="market",
        ),
        state=TradingState(cash=50.0, equity=50.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=0.5, slippage_ticks=2.0, fee_rate=0.1),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 3.2
    assert result.position_budget == 35.2
    assert result.cash_consumption == 38.72
    assert result.sell_quantity_reservation == 0.0


@pytest.mark.parametrize(
    ("order_request", "expected_budget"),
    [
        (
            PendingOrderRequest(
                symbol="BTC/USDT",
                side="buy",
                quantity=2.0,
                order_type="limit",
                limit_price=16.0,
            ),
            32.0,
        ),
        (
            PendingOrderRequest(
                symbol="BTC/USDT",
                side="buy",
                quantity=2.0,
                order_type="stop_limit",
                stop_price=25.0,
                trigger_condition="crosses_above",
                limit_price=16.0,
            ),
            32.0,
        ),
        (
            PendingOrderRequest(
                symbol="BTC/USDT",
                side="buy",
                quantity=2.0,
                order_type="stop_market",
                stop_price=25.0,
                trigger_condition="crosses_above",
            ),
            52.0,
        ),
    ],
)
def test_explicit_quantity_buy_uses_order_type_anchor_without_resizing(
    order_request: PendingOrderRequest,
    expected_budget: float,
) -> None:
    result = resolve_pending_order_request(
        request=order_request,
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 2.0
    assert result.position_budget == expected_budget
    assert result.cash_consumption == expected_budget


def test_explicit_quantity_buy_rejects_below_minimum_cost_after_affordability() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="limit",
            limit_price=10.0,
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(min_cost=30.0),
    )

    assert result.quantity is None
    assert result.reason == "below_minimum_cost"
    assert result.position_budget == 0.0
    assert result.cash_consumption == 0.0


def test_explicit_quantity_buy_respects_active_and_manual_cash_reservations() -> None:
    active_buy = Order.from_intent(
        order_id=11,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="limit",
            limit_price=10.0,
        ),
    )

    accepted = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            quantity=5.0,
            order_type="limit",
            limit_price=10.0,
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(active_buy,),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
        reservations=SizingReservations(buy_cash=30.0),
    )
    rejected = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            quantity=6.0,
            order_type="limit",
            limit_price=10.0,
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(active_buy,),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
        reservations=SizingReservations(buy_cash=30.0),
    )

    assert accepted.reason is None
    assert accepted.quantity == 5.0
    assert accepted.position_budget == 50.0
    assert accepted.cash_consumption == 50.0
    assert rejected.quantity is None
    assert rejected.reason == "insufficient_cash"


def test_explicit_quantity_sell_respects_active_and_manual_position_reservations() -> None:
    active_exit = Order.from_intent(
        order_id=12,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=4.0,
            order_type="limit",
            limit_price=12.0,
        ),
    ).apply_fill(fill=_fill_stub(symbol="BTC/USDT", side="sell", quantity=1.0, price=12.0))

    accepted = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            quantity=5.0,
            order_type="market",
        ),
        state=TradingState(cash=0.0, equity=100.0, position_quantity=10.0),
        active_orders=(active_exit,),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
        reservations=SizingReservations(sell_quantity=2.0),
    )
    rejected = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            quantity=6.0,
            order_type="market",
        ),
        state=TradingState(cash=0.0, equity=100.0, position_quantity=10.0),
        active_orders=(active_exit,),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
        reservations=SizingReservations(sell_quantity=2.0),
    )

    assert accepted.reason is None
    assert accepted.quantity == 5.0
    assert accepted.sell_quantity_reservation == 5.0
    assert accepted.position_budget == 0.0
    assert accepted.cash_consumption == 0.0
    assert rejected.quantity is None
    assert rejected.reason == "insufficient_position"


def test_explicit_quantity_requests_round_down_before_budget_and_reservation_checks() -> None:
    buy = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            quantity=3.9,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(quantity_increment=1.0),
    )
    sell = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            quantity=3.9,
            order_type="market",
        ),
        state=TradingState(cash=0.0, equity=40.0, position_quantity=4.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(quantity_increment=1.0),
    )

    assert buy.reason is None
    assert buy.quantity == 3.0
    assert buy.position_budget == 30.0
    assert buy.cash_consumption == 30.0
    assert sell.reason is None
    assert sell.quantity == 3.0
    assert sell.sell_quantity_reservation == 3.0


def test_buy_percent_manual_reservation_reduces_requested_budget_basis() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=25.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
        reservations=SizingReservations(buy_cash=20.0),
    )

    assert result.reason is None
    assert result.quantity == 2.0
    assert result.position_budget == 20.0
    assert result.cash_consumption == 20.0


def test_buy_percent_reports_no_budget_when_cash_is_fully_reserved() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
        reservations=SizingReservations(buy_cash=100.0),
    )

    assert result.quantity is None
    assert result.reason == "no_buy_budget_available"
    assert result.cash_consumption == 0.0


def test_buy_percent_below_minimum_cost_reports_stable_noop_reason() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=20.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(min_cost=30.0),
    )

    assert result.quantity is None
    assert result.reason == "below_minimum_cost"
    assert result.position_budget == 0.0
    assert result.cash_consumption == 0.0


def test_sell_percent_manual_reservations_and_exact_full_exit_basis() -> None:
    partial = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            qty_percent=50.0,
            order_type="market",
        ),
        state=TradingState(cash=0.0, equity=100.0, position_quantity=10.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
        reservations=SizingReservations(sell_quantity=2.0),
    )
    full = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            qty_percent=100.0,
            order_type="market",
        ),
        state=TradingState(cash=0.0, equity=100.0, position_quantity=10.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
        reservations=SizingReservations(sell_quantity=2.0),
    )

    assert partial.reason is None
    assert partial.quantity == 4.0
    assert partial.sell_quantity_reservation == 4.0
    assert full.reason is None
    assert full.quantity == 8.0
    assert full.sell_quantity_reservation == 8.0


def test_sell_percent_reports_no_closable_position_when_fully_reserved() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            qty_percent=100.0,
            order_type="market",
        ),
        state=TradingState(cash=0.0, equity=100.0, position_quantity=10.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
        reservations=SizingReservations(sell_quantity=10.0),
    )

    assert result.quantity is None
    assert result.reason == "no_closable_position"
    assert result.sell_quantity_reservation == 0.0


def test_sell_percent_subminimum_after_rounding_reports_below_minimum_size() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            qty_percent=10.0,
            order_type="market",
        ),
        state=TradingState(cash=0.0, equity=100.0, position_quantity=5.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(quantity_increment=1.0, min_quantity=1.0),
    )

    assert result.quantity is None
    assert result.reason == "below_minimum_size"


@pytest.mark.parametrize(
    ("active_order", "expected_available_cash"),
    [
        (
            Order.from_intent(
                order_id=21,
                intent=OrderIntent(
                    symbol="BTC/USDT",
                    side="buy",
                    quantity=2.0,
                    order_type="market",
                ),
            ),
            75.8,
        ),
        (
            Order.from_intent(
                order_id=22,
                intent=OrderIntent(
                    symbol="BTC/USDT",
                    side="buy",
                    quantity=2.0,
                    order_type="limit",
                    limit_price=16.0,
                ),
            ),
            64.8,
        ),
        (
            Order.from_intent(
                order_id=23,
                intent=OrderIntent(
                    symbol="BTC/USDT",
                    side="buy",
                    quantity=2.0,
                    order_type="stop_market",
                    trigger_price=25.0,
                    trigger_condition="crosses_above",
                    trigger_type="last",
                ),
            ),
            42.8,
        ),
        (
            Order.from_intent(
                order_id=24,
                intent=OrderIntent(
                    symbol="BTC/USDT",
                    side="buy",
                    quantity=2.0,
                    order_type="stop_limit",
                    trigger_price=25.0,
                    trigger_condition="crosses_above",
                    trigger_type="last",
                    limit_price=16.0,
                ),
            ),
            64.8,
        ),
        (
            Order.from_intent(
                order_id=25,
                intent=OrderIntent(
                    symbol="BTC/USDT",
                    side="buy",
                    quantity=2.0,
                    order_type="stop_limit",
                    trigger_price=25.0,
                    trigger_condition="crosses_above",
                    trigger_type="last",
                    limit_price=16.0,
                ),
            ).trigger(timestamp=120),
            64.8,
        ),
    ],
)
def test_active_buy_reservation_matrix_uses_order_type_price_anchor(
    active_order: Order,
    expected_available_cash: float,
) -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=100.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(active_order,),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.1),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.position_budget == pytest.approx(expected_available_cash / 1.1)
    assert result.cash_consumption == pytest.approx(expected_available_cash)


def test_partially_filled_and_closed_buy_orders_reserve_only_open_remaining_quantity() -> None:
    partially_filled = Order.from_intent(
        order_id=31,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=3.0,
            order_type="limit",
            limit_price=10.0,
        ),
    ).apply_fill(fill=_fill_stub(symbol="BTC/USDT", side="buy", quantity=2.0, price=10.0))
    fully_filled = Order.from_intent(
        order_id=32,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=2.0,
            order_type="limit",
            limit_price=10.0,
        ),
    ).apply_fill(fill=_fill_stub(symbol="BTC/USDT", side="buy", quantity=2.0, price=10.0))
    active_sell = Order.from_intent(
        order_id=33,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=5.0,
            order_type="limit",
            limit_price=12.0,
        ),
    )

    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=100.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(partially_filled, fully_filled, active_sell),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.position_budget == 90.0
    assert result.cash_consumption == 90.0


def test_active_sell_reservation_matrix_counts_only_open_sell_orders() -> None:
    open_sell = Order.from_intent(
        order_id=41,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=3.0,
            order_type="limit",
            limit_price=12.0,
        ),
    )
    partially_filled_sell = Order.from_intent(
        order_id=42,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=4.0,
            order_type="limit",
            limit_price=12.0,
        ),
    ).apply_fill(fill=_fill_stub(symbol="BTC/USDT", side="sell", quantity=1.0, price=12.0))
    fully_filled_sell = Order.from_intent(
        order_id=43,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=2.0,
            order_type="limit",
            limit_price=12.0,
        ),
    ).apply_fill(fill=_fill_stub(symbol="BTC/USDT", side="sell", quantity=2.0, price=12.0))
    active_buy = Order.from_intent(
        order_id=44,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=5.0,
            order_type="limit",
            limit_price=10.0,
        ),
    )

    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            qty_percent=100.0,
            order_type="market",
        ),
        state=TradingState(cash=0.0, equity=120.0, position_quantity=12.0),
        active_orders=(open_sell, partially_filled_sell, fully_filled_sell, active_buy),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.reason is None
    assert result.quantity == 6.0
    assert result.sell_quantity_reservation == 6.0


def test_explicit_quantity_buy_exceeding_unreserved_cash_rejects_without_resize() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            quantity=20.0,
            order_type="market",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.quantity is None
    assert result.reason == "insufficient_cash"


def test_explicit_quantity_sell_exceeding_unreserved_position_rejects_without_shorting() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            quantity=6.0,
            order_type="market",
        ),
        state=TradingState(cash=0.0, equity=50.0, position_quantity=5.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
        constraints=SizingConstraints(),
    )

    assert result.quantity is None
    assert result.reason == "insufficient_position"
