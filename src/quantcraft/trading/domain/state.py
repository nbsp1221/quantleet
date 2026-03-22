from __future__ import annotations

from dataclasses import dataclass

from quantcraft.trading.domain.events import FillEvent


@dataclass(frozen=True, slots=True)
class TradingState:
    cash: float
    position_quantity: float = 0.0
    average_entry_price: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    equity: float = 0.0


def apply_fill(
    state: TradingState,
    fill: FillEvent,
    *,
    mark_price: float,
) -> TradingState:
    if fill.quantity <= 0.0:
        raise ValueError("apply_fill requires a positive quantity")

    if fill.side == "buy":
        total_cost = fill.price * fill.quantity + fill.fee
        if total_cost > state.cash:
            raise ValueError("insufficient cash for spot-like long-only buy")

        next_quantity = state.position_quantity + fill.quantity
        average_entry_price = (
            (state.average_entry_price * state.position_quantity) + (fill.price * fill.quantity)
        ) / next_quantity
        cash = state.cash - total_cost
        realized_pnl = state.realized_pnl
    else:
        if fill.quantity > state.position_quantity:
            raise ValueError("cannot sell more than the current long position")

        next_quantity = state.position_quantity - fill.quantity
        average_entry_price = state.average_entry_price if next_quantity > 0.0 else 0.0
        cash = state.cash + (fill.price * fill.quantity) - fill.fee
        realized_pnl = state.realized_pnl + (
            (fill.price - state.average_entry_price) * fill.quantity
        )

    unrealized_pnl = (
        (mark_price - average_entry_price) * next_quantity if next_quantity > 0.0 else 0.0
    )
    equity = cash + (next_quantity * mark_price)

    return TradingState(
        cash=round(cash, 12),
        position_quantity=round(next_quantity, 12),
        average_entry_price=round(average_entry_price, 12),
        realized_pnl=round(realized_pnl, 12),
        unrealized_pnl=round(unrealized_pnl, 12),
        equity=round(equity, 12),
    )
