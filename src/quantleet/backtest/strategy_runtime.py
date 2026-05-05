from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, cast

from quantleet.data import BarSeries, TimeBar
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent, OrderRejectedEvent, OrderRejectionReason
from quantleet.trading.domain.intents import OrderIntent, _is_stop_order_type
from quantleet.trading.domain.orders import Order
from quantleet.trading.domain.state import TradingState
from quantleet.trading.order_requests import PendingOrderRequest
from quantleet.trading.sizing import (
    SizingConstraints,
    SizingReservations,
    resolve_pending_order_request,
)


@dataclass(frozen=True, slots=True)
class _StrategyOrderState:
    active: tuple[Order, ...]
    pending: tuple[PendingOrderRequest, ...]
    order_events: tuple[OrderRejectedEvent, ...] = ()


class _PositionLike(Protocol):
    def _refresh(self, state: TradingState) -> None: ...


class StrategyLike(Protocol):
    _pending_order_requests: list[PendingOrderRequest]
    data: Any
    position: _PositionLike

    def _reset_runtime_state(self) -> None: ...

    def init(self) -> None: ...

    @property
    def display_name(self) -> str | None: ...

    def parameters(self) -> dict[str, object]: ...

    def _handle_bar(self, bar: BarEvent) -> None: ...


class _StrategyDriver:
    _DEFAULT_FLAT_STATE = TradingState(cash=0.0, equity=0.0)

    def __init__(self, strategy: StrategyLike) -> None:
        self._strategy = strategy
        self._active_orders: tuple[Order, ...] = ()
        self._next_order_id = 1
        self._preloaded_rows: tuple[TimeBar, ...] | None = None
        self._visible_bars = 0
        self._order_events: list[OrderRejectedEvent] = []

    def initialize(self, *, bars: BarSeries | None = None) -> None:
        self._strategy._reset_runtime_state()
        self._active_orders = ()
        self._next_order_id = 1
        self._preloaded_rows = None
        self._visible_bars = 0
        self._order_events = []
        if bars is not None:
            self._preload_bars(bars)
        self._strategy.init()

    def sync_position(self, state: TradingState) -> None:
        self._strategy.position._refresh(state)

    def handle_bar(self, bar: BarEvent, *, state: TradingState | None = None) -> None:
        self._append_bar(bar)
        self.sync_position(self._DEFAULT_FLAT_STATE if state is None else state)
        self._strategy._handle_bar(bar)

    def activate_pending_order_intents(
        self,
        *,
        next_bar: TimeBar,
        state: TradingState,
        costs: CostConfig,
    ) -> _StrategyOrderState:
        next_active_orders = list(self._active_orders)
        reservations = SizingReservations()
        for request in self._strategy._pending_order_requests:
            sizing = resolve_pending_order_request(
                request=request,
                state=state,
                active_orders=self._active_orders,
                market_buy_price=next_bar.open,
                costs=costs,
                constraints=SizingConstraints(),
                reservations=reservations,
            )
            if sizing.is_noop:
                self._record_rejection(
                    request=request,
                    timestamp=next_bar.timestamp,
                    reason=sizing.reason,
                    quantity=sizing.quantity,
                )
                continue
            quantity = sizing.quantity
            if quantity is None:
                continue
            if (
                _is_stop_order_type(request.order_type)
                and request.side == "sell"
                and state.position_quantity <= 0.0
            ):
                self._record_rejection(
                    request=request,
                    timestamp=next_bar.timestamp,
                    reason="insufficient_position",
                    quantity=quantity,
                )
                continue
            intent = request.to_order_intent(quantity=quantity)
            next_active_orders.append(self._create_order(intent))
            reservations = reservations.reserve(sizing)
        self._active_orders = tuple(next_active_orders)
        self._strategy._pending_order_requests.clear()
        return self.order_state()

    def activate_pending_order_requests(
        self,
        *,
        bar: TimeBar,
        state: TradingState,
        costs: CostConfig,
    ) -> _StrategyOrderState:
        return self.activate_pending_order_intents(
            next_bar=bar,
            state=state,
            costs=costs,
        )

    def order_state(self) -> _StrategyOrderState:
        return _StrategyOrderState(
            active=self._active_orders,
            pending=tuple(self._strategy._pending_order_requests),
            order_events=tuple(self._order_events),
        )

    def replace_active_orders(self, orders: tuple[Order, ...]) -> None:
        self._active_orders = orders

    def drain_order_events(self) -> tuple[OrderRejectedEvent, ...]:
        events = tuple(self._order_events)
        self._order_events.clear()
        return events

    def _append_bar(self, bar: BarEvent) -> None:
        if self._preloaded_rows is not None:
            self._advance_preloaded_bar(bar)
            return
        self._strategy.data.open._append(bar.open)
        self._strategy.data.high._append(bar.high)
        self._strategy.data.low._append(bar.low)
        self._strategy.data.close._append(bar.close)
        self._strategy.data.volume._append(bar.volume)

    def _preload_bars(self, bars: BarSeries) -> None:
        self._preloaded_rows = bars.rows
        data_view_factory = cast(Any, type(self._strategy.data))
        series_factory = cast(Any, type(self._strategy.data.open))
        self._strategy.data = data_view_factory(
            open=self._preloaded_series(series_factory, tuple(row.open for row in bars.rows)),
            high=self._preloaded_series(series_factory, tuple(row.high for row in bars.rows)),
            low=self._preloaded_series(series_factory, tuple(row.low for row in bars.rows)),
            close=self._preloaded_series(series_factory, tuple(row.close for row in bars.rows)),
            volume=self._preloaded_series(series_factory, tuple(row.volume for row in bars.rows)),
        )

    def _advance_preloaded_bar(self, bar: BarEvent) -> None:
        if self._preloaded_rows is None:
            raise RuntimeError("preloaded bar advancement requires preloaded rows")
        if self._visible_bars >= len(self._preloaded_rows):
            raise ValueError("received more bars than were preloaded")
        expected = self._preloaded_rows[self._visible_bars]
        if (
            bar.timestamp != expected.timestamp
            or bar.open != expected.open
            or bar.high != expected.high
            or bar.low != expected.low
            or bar.close != expected.close
            or bar.volume != expected.volume
        ):
            raise ValueError("bar event does not match the preloaded backtest history")
        self._visible_bars += 1
        self._strategy.data.open._set_visible_length(self._visible_bars)
        self._strategy.data.high._set_visible_length(self._visible_bars)
        self._strategy.data.low._set_visible_length(self._visible_bars)
        self._strategy.data.close._set_visible_length(self._visible_bars)
        self._strategy.data.volume._set_visible_length(self._visible_bars)

    @staticmethod
    def _preloaded_series(series_factory: Any, values: tuple[float, ...]) -> object:
        return series_factory(values, visible_length=0)

    def _create_order(self, intent: OrderIntent) -> Order:
        order = Order.from_intent(order_id=self._next_order_id, intent=intent)
        self._next_order_id += 1
        return order

    def _record_rejection(
        self,
        *,
        request: PendingOrderRequest,
        timestamp: int,
        reason: str | None,
        quantity: float | None,
    ) -> None:
        self._order_events.append(
            OrderRejectedEvent(
                symbol=request.symbol,
                side=request.side,
                order_type=request.order_type,
                reason=_rejection_reason(reason),
                timestamp=timestamp,
                quantity=request.quantity if request.quantity is not None else quantity,
                tag=request.tag,
            )
        )


def _rejection_reason(reason: str | None) -> OrderRejectionReason:
    if reason is None:
        return "buy_budget_unaffordable"
    allowed_reasons: tuple[OrderRejectionReason, ...] = (
        "insufficient_cash",
        "insufficient_position",
        "below_minimum_size",
        "below_minimum_cost",
        "no_buy_budget_available",
        "no_closable_position",
        "buy_budget_unaffordable",
        "execution_affordability",
    )
    if reason not in allowed_reasons:
        raise ValueError(f"unsupported order rejection reason: {reason}")
    return cast(OrderRejectionReason, reason)


__all__ = ["StrategyLike", "_StrategyDriver", "_StrategyOrderState"]
