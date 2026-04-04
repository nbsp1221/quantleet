from __future__ import annotations

import inspect
from abc import ABC

import pytest

from quantcraft.data import BarSeries, TimeBar
from quantcraft.research import BacktestEngine
from quantcraft.research import Strategy as PublicStrategy
from quantcraft.research.application._runtime import _StrategyDriver
from quantcraft.research.application.strategy import Strategy
from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import BarEvent
from quantcraft.trading.domain.intents import OrderIntent


class BuyOnFirstBarStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.seen_bars: list[int] = []

    def on_bar(self, bar: BarEvent) -> None:
        self.seen_bars.append(bar.timestamp)
        if len(self.seen_bars) == 1:
            self.buy(symbol=bar.symbol, quantity=1.0, tag="entry")


class LimitSellOnFirstBarStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.sell(
            symbol=bar.symbol,
            quantity=2.0,
            order_type="limit",
            limit_price=bar.high,
            tag="take-profit",
        )


class RaisesAfterBuyStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.buy(symbol=bar.symbol, quantity=1.0, tag="entry")
        raise RuntimeError("boom")


class OrdersFromInitStrategy(Strategy):
    def init(self) -> None:
        self.buy(symbol="BTC/USDT", quantity=1.0)

    def on_bar(self, bar: BarEvent) -> None:
        return None


class RecordsInitCallsStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.init_calls = 0

    def init(self) -> None:
        self.init_calls += 1

    def on_bar(self, bar: BarEvent) -> None:
        return None


def _runtime(strategy: Strategy) -> _StrategyDriver:
    return _StrategyDriver(strategy)


def _make_bar_series(
    rows: tuple[TimeBar, ...],
    *,
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
) -> BarSeries:
    return BarSeries(
        symbol=symbol,
        timeframe=timeframe,
        bar_type="time",
        rows=rows,
    )


def test_strategy_surface_is_self_based_and_on_bar_is_the_first_hook() -> None:
    signature = inspect.signature(Strategy.on_bar)

    assert tuple(signature.parameters) == ("self", "bar")
    assert not hasattr(Strategy, "activate_pending_order_intents")
    assert tuple(inspect.signature(Strategy.init).parameters) == ("self",)
    assert not hasattr(Strategy, "prepare")
    assert not hasattr(Strategy, "handle_bar")


def test_public_research_strategy_surface_exports_strategy() -> None:
    assert PublicStrategy is Strategy


def test_strategy_is_an_abstract_base_class() -> None:
    assert issubclass(Strategy, ABC)
    assert inspect.isabstract(Strategy)


def test_on_bar_requires_a_closed_bar() -> None:
    strategy = BuyOnFirstBarStrategy()
    runtime = _runtime(strategy)

    with pytest.raises(ValueError, match="closed bar"):
        runtime.handle_bar(
            BarEvent(
                bar_type="time",
                bar_spec="1m",
                symbol="BTC/USDT",
                timestamp=60,
                open=100.0,
                high=105.0,
                low=95.0,
                close=104.0,
                volume=10.0,
                is_closed=False,
            )
        )

    assert strategy.seen_bars == []


def test_order_intake_methods_are_restricted_to_bar_handling_callback() -> None:
    strategy = BuyOnFirstBarStrategy()

    with pytest.raises(ValueError, match="only be used during on_bar"):
        strategy.buy(symbol="BTC/USDT", quantity=1.0)

    with pytest.raises(ValueError, match="only be used during on_bar"):
        strategy.sell(symbol="BTC/USDT", quantity=1.0)


def test_init_cannot_create_orders() -> None:
    strategy = OrdersFromInitStrategy()

    with pytest.raises(ValueError, match="only be used during on_bar"):
        strategy.init()


def test_backtest_engine_calls_init_once_before_processing() -> None:
    strategy = RecordsInitCallsStrategy()

    engine = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=0.1, slippage_ticks=1.0, fee_rate=0.001),
    )
    engine.run(
        bars=_make_bar_series(
            (
                TimeBar(
                    timestamp=60,
                    open=100.0,
                    high=105.0,
                    low=95.0,
                    close=104.0,
                    volume=10.0,
                ),
            )
        ),
        strategy=strategy,
    )

    assert strategy.init_calls == 1


def test_order_intents_from_on_bar_become_effective_on_the_next_bar() -> None:
    strategy = BuyOnFirstBarStrategy()
    runtime = _runtime(strategy)

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
    runtime.handle_bar(first_bar)

    assert runtime.order_state().active == ()
    assert runtime.order_state().pending == (
        OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
            tag="entry",
        ),
    )


def test_sell_forwards_order_type_limit_price_and_tag() -> None:
    strategy = LimitSellOnFirstBarStrategy()
    runtime = _runtime(strategy)
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
    runtime.handle_bar(first_bar)
    assert runtime.order_state().pending == (
        OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=2.0,
            order_type="limit",
            limit_price=105.0,
            tag="take-profit",
        ),
    )
    assert runtime.order_state().active == ()


def test_failed_on_bar_does_not_leak_staged_intents_to_the_next_bar() -> None:
    strategy = RaisesAfterBuyStrategy()
    runtime = _runtime(strategy)
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
        open=110.0,
        high=112.0,
        low=108.0,
        close=109.0,
        volume=12.0,
        is_closed=True,
    )

    with pytest.raises(RuntimeError, match="boom"):
        runtime.handle_bar(first_bar)

    assert runtime.order_state().pending == ()
    assert runtime.order_state().active == ()

    with pytest.raises(RuntimeError, match="boom"):
        runtime.handle_bar(second_bar)

    assert runtime.order_state().pending == ()
    assert runtime.order_state().active == ()


def test_sell_is_the_current_long_exit_surface() -> None:
    class SellWhileFlatInLongOnlyScopeStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.sell(symbol=bar.symbol, quantity=1.0, tag="flat-exit")

    result = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=0.1, slippage_ticks=0.0, fee_rate=0.0),
    ).run(
        bars=_make_bar_series(
            (
                TimeBar(
                    timestamp=60,
                    open=100.0,
                    high=101.0,
                    low=99.0,
                    close=100.5,
                    volume=10.0,
                ),
                TimeBar(
                    timestamp=120,
                    open=101.0,
                    high=102.0,
                    low=100.0,
                    close=101.5,
                    volume=10.0,
                ),
            )
        ),
        strategy=SellWhileFlatInLongOnlyScopeStrategy(),
    )

    assert result.trade_log == ()
    assert result.final_state.position_quantity == 0.0
    assert result.final_state.cash == 1_000.0
