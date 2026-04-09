from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from quantcraft.data import BarSeries, TimeBar
from quantcraft.research.domain import SeriesView
from quantcraft.trading.domain.events import BarEvent
from quantcraft.trading.domain.intents import OrderIntent
from quantcraft.trading.domain.state import TradingState

if TYPE_CHECKING:
    from quantcraft.research.application.strategy import Strategy


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


@dataclass(frozen=True, slots=True)
class _StrategyOrderState:
    active: tuple[OrderIntent, ...]
    pending: tuple[OrderIntent, ...]


class _StrategyDriver:
    _DEFAULT_FLAT_STATE = TradingState(cash=0.0, equity=0.0)

    def __init__(self, strategy: Strategy) -> None:
        self._strategy = strategy
        self._preloaded_rows: tuple[TimeBar, ...] | None = None
        self._visible_bars = 0

    def initialize(self, *, bars: BarSeries | None = None) -> None:
        self._strategy._reset_runtime_state()
        self._preloaded_rows = None
        self._visible_bars = 0
        if bars is not None:
            self._preload_bars(bars)
        self._strategy.init()

    def sync_position(self, state: TradingState) -> None:
        self._strategy.position._refresh(state)

    def handle_bar(self, bar: BarEvent, *, state: TradingState | None = None) -> None:
        self._append_bar(bar)
        self.sync_position(self._DEFAULT_FLAT_STATE if state is None else state)
        self._strategy._handle_bar(bar)

    def activate_pending_order_intents(self) -> _StrategyOrderState:
        self._strategy._active_order_intents = self._strategy._active_order_intents + tuple(
            self._strategy._pending_order_intents
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
        from quantcraft.research.domain import OHLCVDataView

        self._strategy.data = OHLCVDataView(
            open=self._preloaded_series(tuple(row.open for row in bars.rows)),
            high=self._preloaded_series(tuple(row.high for row in bars.rows)),
            low=self._preloaded_series(tuple(row.low for row in bars.rows)),
            close=self._preloaded_series(tuple(row.close for row in bars.rows)),
            volume=self._preloaded_series(tuple(row.volume for row in bars.rows)),
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
    def _preloaded_series(values: tuple[float, ...]) -> SeriesView:
        return SeriesView(values, visible_length=0)
