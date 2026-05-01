from __future__ import annotations

from abc import ABC, abstractmethod

from quantcraft.research.series import OHLCVDataView, SeriesView
from quantcraft.trading.domain.events import BarEvent
from quantcraft.trading.domain.intents import (
    OrderSide,
    OrderType,
    TriggerCondition,
    _is_stop_order_type,
)
from quantcraft.trading.domain.state import TradingState
from quantcraft.trading.order_requests import PendingOrderRequest


class PositionView:
    __slots__ = ("_is_open", "_quantity", "_average_entry_price")

    def __init__(self) -> None:
        self._is_open = False
        self._quantity = 0.0
        self._average_entry_price = 0.0

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def quantity(self) -> float:
        return self._quantity

    @property
    def average_entry_price(self) -> float:
        return self._average_entry_price

    def _refresh(self, state: TradingState) -> None:
        self._quantity = state.position_quantity
        self._average_entry_price = state.average_entry_price
        self._is_open = state.position_quantity > 0.0


class Strategy(ABC):
    def __init__(self) -> None:
        self._reset_runtime_state()

    def _reset_runtime_state(self) -> None:
        self._pending_order_requests: list[PendingOrderRequest] = []
        self._handling_bar = False
        self._active_bar_symbol: str | None = None
        self._active_bar_close: float | None = None
        self.data = OHLCVDataView(
            open=SeriesView(()),
            high=SeriesView(()),
            low=SeriesView(()),
            close=SeriesView(()),
            volume=SeriesView(()),
        )
        self.position = PositionView()

    def init(self) -> None:
        pass

    @property
    def display_name(self) -> str | None:
        return None

    def parameters(self) -> dict[str, object]:
        return {}

    @abstractmethod
    def on_bar(self, bar: BarEvent) -> None:
        raise NotImplementedError

    def _handle_bar(self, bar: BarEvent) -> None:
        if not bar.is_closed:
            raise ValueError("Strategy.handle_bar requires a closed bar")
        self._handling_bar = True
        self._active_bar_symbol = bar.symbol
        self._active_bar_close = bar.close
        try:
            self.on_bar(bar)
        except Exception:
            self._pending_order_requests.clear()
            raise
        finally:
            self._handling_bar = False
            self._active_bar_symbol = None
            self._active_bar_close = None

    def buy(
        self,
        *,
        symbol: str | None = None,
        quantity: float | None = None,
        qty_percent: float | None = None,
        order_type: OrderType = "market",
        limit_price: float | None = None,
        stop_price: float | None = None,
        tag: str | None = None,
    ) -> None:
        self._submit_order_request(
            side="buy",
            symbol=symbol,
            quantity=quantity,
            qty_percent=qty_percent,
            order_type=order_type,
            limit_price=limit_price,
            stop_price=stop_price,
            tag=tag,
        )

    def sell(
        self,
        *,
        symbol: str | None = None,
        quantity: float | None = None,
        qty_percent: float | None = None,
        order_type: OrderType = "market",
        limit_price: float | None = None,
        stop_price: float | None = None,
        tag: str | None = None,
    ) -> None:
        self._submit_order_request(
            side="sell",
            symbol=symbol,
            quantity=quantity,
            qty_percent=qty_percent,
            order_type=order_type,
            limit_price=limit_price,
            stop_price=stop_price,
            tag=tag,
        )

    def _assert_order_intake_allowed(self) -> None:
        if not self._handling_bar:
            raise ValueError("Order intake methods may only be used during on_bar")

    def _submit_order_request(
        self,
        *,
        side: OrderSide,
        symbol: str | None,
        quantity: float | None,
        qty_percent: float | None,
        order_type: OrderType,
        limit_price: float | None,
        stop_price: float | None,
        tag: str | None,
    ) -> None:
        self._assert_order_intake_allowed()
        self._pending_order_requests.append(
            PendingOrderRequest(
                symbol=self._resolve_order_symbol(symbol),
                side=side,
                quantity=quantity,
                qty_percent=qty_percent,
                order_type=order_type,
                limit_price=limit_price,
                stop_price=stop_price,
                trigger_condition=self._infer_trigger_condition(
                    order_type=order_type,
                    stop_price=stop_price,
                ),
                tag=tag,
            )
        )

    def _resolve_order_symbol(self, symbol: str | None) -> str:
        active_bar_symbol = self._active_bar_symbol
        if symbol is not None:
            if active_bar_symbol is not None and symbol != active_bar_symbol:
                raise ValueError(
                    "explicit symbol must match the active series symbol "
                    "in the current single-symbol on_bar workflow"
                )
            return symbol
        if active_bar_symbol is None:
            raise RuntimeError("active bar symbol is missing during on_bar order intake")
        return active_bar_symbol

    def _infer_trigger_condition(
        self,
        *,
        order_type: OrderType,
        stop_price: float | None,
    ) -> TriggerCondition | None:
        if not _is_stop_order_type(order_type):
            if stop_price is not None:
                raise ValueError("stop_price is only valid for stop-family orders")
            return None

        if stop_price is None:
            raise ValueError(f"{order_type} orders require a stop_price")

        active_bar_close = self._active_bar_close
        if active_bar_close is None:
            raise RuntimeError("active bar close is missing during on_bar order intake")
        if stop_price == active_bar_close:
            raise ValueError("stop_price equal to the active bar close is ambiguous")
        if stop_price > active_bar_close:
            return "crosses_above"
        return "crosses_below"

__all__ = ["Strategy"]
