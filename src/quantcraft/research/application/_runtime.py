from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from quantcraft.trading.domain.events import BarEvent
from quantcraft.trading.domain.intents import OrderIntent

if TYPE_CHECKING:
    from quantcraft.research.application.strategy import Strategy


@dataclass(frozen=True, slots=True)
class _StrategyOrderState:
    active: tuple[OrderIntent, ...]
    pending: tuple[OrderIntent, ...]


class _StrategyDriver:
    def __init__(self, strategy: Strategy) -> None:
        self._strategy = strategy

    def initialize(self) -> None:
        if self._strategy._initialized:
            return None
        self._strategy.init()
        self._strategy._initialized = True
        return None

    def handle_bar(self, bar: BarEvent) -> None:
        self._append_bar(bar)
        self._strategy._handle_bar(bar)

    def activate_pending_order_intents(self) -> _StrategyOrderState:
        self._strategy._active_order_intents = (
            self._strategy._active_order_intents + tuple(self._strategy._pending_order_intents)
        )
        self._strategy._pending_order_intents.clear()
        return self.order_state()

    def order_state(self) -> _StrategyOrderState:
        return _StrategyOrderState(
            active=self._strategy._active_order_intents,
            pending=tuple(self._strategy._pending_order_intents),
        )

    def replace_active_order_intents(self, intents: tuple[OrderIntent, ...]) -> None:
        self._strategy._active_order_intents = intents

    def _append_bar(self, bar: BarEvent) -> None:
        self._strategy.data.open._append(bar.open)
        self._strategy.data.high._append(bar.high)
        self._strategy.data.low._append(bar.low)
        self._strategy.data.close._append(bar.close)
        self._strategy.data.volume._append(bar.volume)
