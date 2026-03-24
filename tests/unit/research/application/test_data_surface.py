from __future__ import annotations

from quantcraft.research.application._runtime import _StrategyDriver
from quantcraft.research.application.strategy import Strategy
from quantcraft.trading.domain.events import BarEvent


class RecordsDataSurfaceStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.latest_close: float | None = None
        self.previous_close: float | None = None
        self.current_volume: float | None = None
        self.bound_close = None

    def init(self) -> None:
        self.bound_close = self.data.close

    def on_bar(self, bar: BarEvent) -> None:
        self.latest_close = self.data.close[0]
        self.previous_close = self.data.close[1]
        self.current_volume = self.data.volume.latest


def test_strategy_data_surface_is_causal_and_updates_with_closed_bars() -> None:
    strategy = RecordsDataSurfaceStrategy()
    runtime = _StrategyDriver(strategy)
    runtime.initialize()

    first_bar = BarEvent(
        bar_type="time",
        bar_spec="1m",
        symbol="BTC/USDT",
        timestamp=60,
        open=100.0,
        high=105.0,
        low=95.0,
        close=104.0,
        volume=10.0,
        is_closed=True,
    )
    second_bar = BarEvent(
        bar_type="time",
        bar_spec="1m",
        symbol="BTC/USDT",
        timestamp=120,
        open=104.0,
        high=108.0,
        low=101.0,
        close=107.0,
        volume=12.0,
        is_closed=True,
    )

    runtime.handle_bar(first_bar)
    assert strategy.latest_close == 104.0
    assert strategy.previous_close != strategy.previous_close
    assert strategy.current_volume == 10.0
    assert strategy.bound_close is strategy.data.close
    assert strategy.bound_close[0] == 104.0

    runtime.handle_bar(second_bar)
    assert strategy.latest_close == 107.0
    assert strategy.previous_close == 104.0
    assert strategy.current_volume == 12.0
    assert strategy.bound_close is strategy.data.close
    assert strategy.bound_close[0] == 107.0
    assert strategy.bound_close[1] == 104.0


def test_strategy_init_sees_empty_data_surface() -> None:
    seen = {}

    class InitReadsDataStrategy(Strategy):
        def init(self) -> None:
            seen["is_empty"] = self.data.close.is_empty
            seen["latest"] = self.data.close.latest

        def on_bar(self, bar: BarEvent) -> None:
            return None

    runtime = _StrategyDriver(InitReadsDataStrategy())
    runtime.initialize()

    assert seen["is_empty"] is True
    assert seen["latest"] != seen["latest"]
