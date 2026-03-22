from __future__ import annotations

import inspect

import pytest

from quantcraft.research.application.strategy import Strategy
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


def test_strategy_surface_is_self_based_and_on_bar_is_the_first_hook() -> None:
    signature = inspect.signature(Strategy.on_bar)

    assert tuple(signature.parameters) == ("self", "bar")
    assert not hasattr(Strategy, "activate_pending_order_intents")


def test_on_bar_requires_a_closed_bar() -> None:
    strategy = BuyOnFirstBarStrategy()

    with pytest.raises(ValueError, match="closed bar"):
        strategy.handle_bar(
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


def test_order_intents_from_on_bar_become_effective_on_the_next_bar() -> None:
    strategy = BuyOnFirstBarStrategy()

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
    strategy.handle_bar(first_bar)

    assert strategy.active_order_intents() == ()
    assert strategy.pending_order_intents() == (
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
    strategy.handle_bar(first_bar)
    assert strategy.pending_order_intents() == (
        OrderIntent(
            symbol="BTC/USDT",
            side="sell",
            quantity=2.0,
            order_type="limit",
            limit_price=105.0,
            tag="take-profit",
        ),
    )
    assert strategy.active_order_intents() == ()


def test_failed_on_bar_does_not_leak_staged_intents_to_the_next_bar() -> None:
    strategy = RaisesAfterBuyStrategy()
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
        strategy.handle_bar(first_bar)

    assert strategy.pending_order_intents() == ()
    assert strategy.active_order_intents() == ()

    with pytest.raises(RuntimeError, match="boom"):
        strategy.handle_bar(second_bar)

    assert strategy.pending_order_intents() == ()
    assert strategy.active_order_intents() == ()
