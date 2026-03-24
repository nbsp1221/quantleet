from __future__ import annotations

from abc import ABC, abstractmethod

from quantcraft.research.domain import OHLCVDataView, SeriesView
from quantcraft.trading.domain.events import BarEvent
from quantcraft.trading.domain.intents import OrderIntent, OrderType


class Strategy(ABC):
    def __init__(self) -> None:
        self._active_order_intents: tuple[OrderIntent, ...] = ()
        self._pending_order_intents: list[OrderIntent] = []
        self._handling_bar = False
        self._initialized = False
        self.data = OHLCVDataView(
            open=SeriesView(()),
            high=SeriesView(()),
            low=SeriesView(()),
            close=SeriesView(()),
            volume=SeriesView(()),
        )

    def init(self) -> None:
        return None

    @abstractmethod
    def on_bar(self, bar: BarEvent) -> None:
        raise NotImplementedError

    def _handle_bar(self, bar: BarEvent) -> None:
        if not bar.is_closed:
            raise ValueError("Strategy.handle_bar requires a closed bar")
        self._handling_bar = True
        try:
            self.on_bar(bar)
        except Exception:
            self._pending_order_intents.clear()
            raise
        finally:
            self._handling_bar = False

    def buy(
        self,
        *,
        symbol: str,
        quantity: float,
        order_type: OrderType = "market",
        limit_price: float | None = None,
        tag: str | None = None,
    ) -> None:
        self._assert_order_intake_allowed()
        self._pending_order_intents.append(
            OrderIntent(
                symbol=symbol,
                side="buy",
                quantity=quantity,
                order_type=order_type,
                limit_price=limit_price,
                tag=tag,
            )
        )

    def sell(
        self,
        *,
        symbol: str,
        quantity: float,
        order_type: OrderType = "market",
        limit_price: float | None = None,
        tag: str | None = None,
    ) -> None:
        self._assert_order_intake_allowed()
        self._pending_order_intents.append(
            OrderIntent(
                symbol=symbol,
                side="sell",
                quantity=quantity,
                order_type=order_type,
                limit_price=limit_price,
                tag=tag,
            )
        )

    def _assert_order_intake_allowed(self) -> None:
        if not self._handling_bar:
            raise ValueError("Order intake methods may only be used during on_bar")
