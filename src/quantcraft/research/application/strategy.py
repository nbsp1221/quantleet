from __future__ import annotations

from quantcraft.trading.domain.events import BarEvent
from quantcraft.trading.domain.intents import OrderIntent, OrderType


class Strategy:
    def __init__(self) -> None:
        self._active_order_intents: tuple[OrderIntent, ...] = ()
        self._pending_order_intents: list[OrderIntent] = []
        self._handling_bar = False

    def on_bar(self, bar: BarEvent) -> None:
        return None

    def handle_bar(self, bar: BarEvent) -> None:
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

    def active_order_intents(self) -> tuple[OrderIntent, ...]:
        return self._active_order_intents

    def pending_order_intents(self) -> tuple[OrderIntent, ...]:
        return tuple(self._pending_order_intents)

    def _roll_order_intents_to_next_bar(self) -> tuple[OrderIntent, ...]:
        self._active_order_intents = self._active_order_intents + tuple(self._pending_order_intents)
        self._pending_order_intents.clear()
        return self._active_order_intents

    def _replace_active_order_intents(self, intents: tuple[OrderIntent, ...]) -> None:
        self._active_order_intents = intents

    def _assert_order_intake_allowed(self) -> None:
        if not self._handling_bar:
            raise ValueError("Order intake methods may only be used during on_bar")
