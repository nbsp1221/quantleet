from __future__ import annotations

import math
from dataclasses import dataclass

from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.orders import Order
from quantcraft.trading.domain.state import TradingState
from quantcraft.trading.order_requests import PendingOrderRequest


@dataclass(frozen=True, slots=True)
class SizingConstraints:
    min_quantity: float = 0.0
    quantity_increment: float = 1e-12
    min_cost: float = 0.0

    def __post_init__(self) -> None:
        if self.min_quantity < 0.0:
            raise ValueError("min_quantity cannot be negative")
        if self.quantity_increment <= 0.0:
            raise ValueError("quantity_increment must be positive")
        if self.min_cost < 0.0:
            raise ValueError("min_cost cannot be negative")


@dataclass(frozen=True, slots=True)
class SizingReservations:
    buy_cash: float = 0.0
    sell_quantity: float = 0.0

    def reserve(self, result: ResolvedOrderSizing) -> SizingReservations:
        return SizingReservations(
            buy_cash=round(self.buy_cash + result.cash_consumption, 12),
            sell_quantity=round(self.sell_quantity + result.sell_quantity_reservation, 12),
        )


@dataclass(frozen=True, slots=True)
class ResolvedOrderSizing:
    quantity: float | None
    reason: str | None = None
    position_budget: float = 0.0
    cash_consumption: float = 0.0
    sell_quantity_reservation: float = 0.0

    @property
    def is_noop(self) -> bool:
        return self.quantity is None


def resolve_pending_order_request(
    *,
    request: PendingOrderRequest,
    state: TradingState,
    active_orders: tuple[Order, ...],
    market_buy_price: float,
    costs: CostConfig,
    constraints: SizingConstraints | None = None,
    reservations: SizingReservations | None = None,
) -> ResolvedOrderSizing:
    sizing_constraints = constraints or SizingConstraints()
    running_reservations = reservations or SizingReservations()

    if request.quantity is not None:
        return _resolve_quantity_request(
            request=request,
            market_buy_price=market_buy_price,
            costs=costs,
            constraints=sizing_constraints,
        )

    assert request.qty_percent is not None
    if request.side == "buy":
        return _resolve_buy_percent_request(
            request=request,
            state=state,
            active_orders=active_orders,
            market_buy_price=market_buy_price,
            costs=costs,
            constraints=sizing_constraints,
            reservations=running_reservations,
        )
    return _resolve_sell_percent_request(
        request=request,
        state=state,
        active_orders=active_orders,
        constraints=sizing_constraints,
        reservations=running_reservations,
    )


def _resolve_quantity_request(
    *,
    request: PendingOrderRequest,
    market_buy_price: float,
    costs: CostConfig,
    constraints: SizingConstraints,
) -> ResolvedOrderSizing:
    assert request.quantity is not None
    quantity = _round_down_to_increment(request.quantity, increment=constraints.quantity_increment)
    if quantity <= 0.0 or quantity < constraints.min_quantity:
        return ResolvedOrderSizing(quantity=None, reason="below_minimum_size")

    if request.side == "sell":
        return ResolvedOrderSizing(quantity=quantity, sell_quantity_reservation=quantity)
    if request.order_type == "stop_market":
        return ResolvedOrderSizing(quantity=quantity)

    anchor_price = _buy_anchor_price(
        request=request,
        market_buy_price=market_buy_price,
        costs=costs,
    )
    position_budget = round(quantity * anchor_price, 12)
    if position_budget < constraints.min_cost:
        return ResolvedOrderSizing(quantity=None, reason="below_minimum_cost")

    return ResolvedOrderSizing(
        quantity=quantity,
        position_budget=position_budget,
        cash_consumption=_cash_consumption_for_budget(
            position_budget=position_budget,
            fee_rate=costs.fee_rate,
        ),
    )


def _resolve_buy_percent_request(
    *,
    request: PendingOrderRequest,
    state: TradingState,
    active_orders: tuple[Order, ...],
    market_buy_price: float,
    costs: CostConfig,
    constraints: SizingConstraints,
    reservations: SizingReservations,
) -> ResolvedOrderSizing:
    qty_percent = request.qty_percent
    if qty_percent is None:
        raise ValueError("buy percent sizing requires qty_percent")
    available_cash = max(
        state.cash
        - _active_buy_cash_reservation(
            active_orders=active_orders,
            market_buy_price=market_buy_price,
            costs=costs,
        )
        - reservations.buy_cash,
        0.0,
    )
    requested_position_budget = round(available_cash * (qty_percent / 100.0), 12)
    if requested_position_budget <= 0.0:
        return ResolvedOrderSizing(quantity=None, reason="no_buy_budget_available")

    affordable_position_budget = _maximum_affordable_position_budget(
        available_cash=available_cash,
        fee_rate=costs.fee_rate,
    )
    final_budget = min(requested_position_budget, affordable_position_budget)
    if final_budget <= 0.0:
        return ResolvedOrderSizing(quantity=None, reason="buy_budget_unaffordable")

    anchor_price = _buy_anchor_price(
        request=request,
        market_buy_price=market_buy_price,
        costs=costs,
    )
    quantity = _round_down_to_increment(
        final_budget / anchor_price, increment=constraints.quantity_increment
    )
    if quantity <= 0.0 or quantity < constraints.min_quantity:
        return ResolvedOrderSizing(quantity=None, reason="below_minimum_size")

    position_budget = round(quantity * anchor_price, 12)
    if position_budget < constraints.min_cost:
        return ResolvedOrderSizing(quantity=None, reason="below_minimum_cost")

    cash_consumption = _cash_consumption_for_budget(
        position_budget=position_budget,
        fee_rate=costs.fee_rate,
    )
    if cash_consumption - available_cash > 1e-12:
        return ResolvedOrderSizing(quantity=None, reason="buy_budget_unaffordable")

    return ResolvedOrderSizing(
        quantity=quantity,
        position_budget=position_budget,
        cash_consumption=cash_consumption,
    )


def _resolve_sell_percent_request(
    *,
    request: PendingOrderRequest,
    state: TradingState,
    active_orders: tuple[Order, ...],
    constraints: SizingConstraints,
    reservations: SizingReservations,
) -> ResolvedOrderSizing:
    qty_percent = request.qty_percent
    if qty_percent is None:
        raise ValueError("sell percent sizing requires qty_percent")
    net_closable = max(
        state.position_quantity - _active_sell_quantity(active_orders) - reservations.sell_quantity,
        0.0,
    )
    if net_closable <= 0.0:
        return ResolvedOrderSizing(quantity=None, reason="no_closable_position")

    quantity = _round_down_to_increment(
        net_closable * (qty_percent / 100.0),
        increment=constraints.quantity_increment,
    )
    if quantity <= 0.0 or quantity < constraints.min_quantity:
        return ResolvedOrderSizing(quantity=None, reason="below_minimum_size")

    return ResolvedOrderSizing(
        quantity=quantity,
        sell_quantity_reservation=quantity,
    )


def _active_buy_cash_reservation(
    *,
    active_orders: tuple[Order, ...],
    market_buy_price: float,
    costs: CostConfig,
) -> float:
    total = 0.0
    for order in active_orders:
        if not order.is_open or order.side != "buy":
            continue
        if order.order_type == "stop_market" and not order.is_triggered:
            continue
        anchor = _order_buy_anchor_price(
            order=order,
            market_buy_price=market_buy_price,
            costs=costs,
        )
        position_budget = round(order.remaining_quantity * anchor, 12)
        total += _cash_consumption_for_budget(
            position_budget=position_budget,
            fee_rate=costs.fee_rate,
        )
    return round(total, 12)


def _active_sell_quantity(active_orders: tuple[Order, ...]) -> float:
    total = 0.0
    for order in active_orders:
        if order.is_open and order.side == "sell":
            total += order.remaining_quantity
    return round(total, 12)


def _maximum_affordable_position_budget(*, available_cash: float, fee_rate: float) -> float:
    if fee_rate == 0.0:
        return round(available_cash, 12)
    return round(available_cash / (1.0 + fee_rate), 12)


def _buy_anchor_price(
    *,
    request: PendingOrderRequest,
    market_buy_price: float,
    costs: CostConfig,
) -> float:
    if request.order_type == "stop_market":
        raise ValueError("stop_market is unsupported in ordinary buy anchor pricing")
    if request.order_type == "limit":
        if request.limit_price is None:
            raise ValueError("limit buy requests require a limit_price")
        return request.limit_price
    slippage = costs.tick_size * costs.slippage_ticks
    return round(market_buy_price + slippage, 12)


def _order_buy_anchor_price(
    *,
    order: Order,
    market_buy_price: float,
    costs: CostConfig,
) -> float:
    if order.order_type == "stop_market":
        raise ValueError("stop_market is unsupported in ordinary buy anchor pricing")
    if order.order_type == "limit":
        if order.limit_price is None:
            raise ValueError("limit buy orders require a limit_price")
        return order.limit_price
    slippage = costs.tick_size * costs.slippage_ticks
    return round(market_buy_price + slippage, 12)


def _cash_consumption_for_budget(*, position_budget: float, fee_rate: float) -> float:
    return round(position_budget + (position_budget * fee_rate), 12)


def _round_down_to_increment(value: float, *, increment: float) -> float:
    if value <= 0.0:
        return 0.0
    steps = math.floor((value / increment) + 1e-12)
    return round(steps * increment, 12)


__all__ = [
    "ResolvedOrderSizing",
    "SizingConstraints",
    "SizingReservations",
    "resolve_pending_order_request",
]
