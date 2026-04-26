from __future__ import annotations

import inspect
from abc import ABC

import pytest

from quantcraft.backtest import BacktestEngine
from quantcraft.backtest.strategy_runtime import _StrategyDriver
from quantcraft.data import BarSeries, TimeBar
from quantcraft.research import Strategy as PublicStrategy
from quantcraft.research.strategy import Strategy
from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import BarEvent
from quantcraft.trading.order_requests import PendingOrderRequest


class BuyOnFirstBarStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.seen_bars: list[int] = []

    def on_bar(self, bar: BarEvent) -> None:
        self.seen_bars.append(bar.timestamp)
        if len(self.seen_bars) == 1:
            self.buy(quantity=1.0, tag="entry")


class ExplicitSymbolBuyOnFirstBarStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.buy(symbol="BTC/USDT", quantity=1.0, tag="entry")


class MismatchedExplicitSymbolBuyOnFirstBarStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.buy(symbol="ETH/USDT", quantity=1.0, tag="entry")


class PercentBuyOnFirstBarStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.buy(qty_percent=80.0, tag="percent-entry")


class StopMarketAboveCloseBuyStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.buy(quantity=1.0, order_type="stop_market", stop_price=120.0, tag="stop-entry")


class StopMarketBelowCloseBuyStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.buy(quantity=1.0, order_type="stop_market", stop_price=90.0, tag="stop-entry")


class ImplicitSymbolBuyOnFirstBarStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.seen_bars: list[int] = []

    def on_bar(self, bar: BarEvent) -> None:
        self.seen_bars.append(bar.timestamp)
        if len(self.seen_bars) == 1:
            self.buy(quantity=1.0, tag="entry")


class ImplicitSymbolSellOnFirstBarStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.sell(quantity=2.0, order_type="limit", limit_price=bar.high, tag="take-profit")


class ImplicitSymbolPercentSellOnFirstBarStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.sell(qty_percent=30.0, tag="scale-out")


class ExplicitSymbolSellOnFirstBarStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.sell(
            symbol="BTC/USDT",
            quantity=2.0,
            order_type="limit",
            limit_price=bar.high,
            tag="take-profit",
        )


class MismatchedExplicitSymbolSellOnFirstBarStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.sell(
            symbol="ETH/USDT",
            quantity=2.0,
            order_type="limit",
            limit_price=bar.high,
            tag="take-profit",
        )


class LimitSellOnFirstBarStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.sell(
            quantity=2.0,
            order_type="limit",
            limit_price=bar.high,
            tag="take-profit",
        )


class RaisesAfterBuyStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.buy(quantity=1.0, tag="entry")
        raise RuntimeError("boom")


class OrdersFromInitStrategy(Strategy):
    def init(self) -> None:
        self.buy(quantity=1.0)

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
    buy_signature = inspect.signature(Strategy.buy)
    sell_signature = inspect.signature(Strategy.sell)

    assert tuple(signature.parameters) == ("self", "bar")
    assert not hasattr(Strategy, "activate_pending_order_intents")
    assert tuple(inspect.signature(Strategy.init).parameters) == ("self",)
    assert not hasattr(Strategy, "prepare")
    assert not hasattr(Strategy, "handle_bar")
    assert tuple(buy_signature.parameters) == (
        "self",
        "symbol",
        "quantity",
        "qty_percent",
        "order_type",
        "limit_price",
        "stop_price",
        "tag",
    )
    assert tuple(sell_signature.parameters) == (
        "self",
        "symbol",
        "quantity",
        "qty_percent",
        "order_type",
        "limit_price",
        "stop_price",
        "tag",
    )
    assert buy_signature.parameters["quantity"].default is None
    assert buy_signature.parameters["qty_percent"].default is None
    assert sell_signature.parameters["quantity"].default is None
    assert sell_signature.parameters["qty_percent"].default is None


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

    with pytest.raises(ValueError, match="only be used during on_bar"):
        strategy.buy(symbol="BTC/USDT", qty_percent=50.0)

    with pytest.raises(ValueError, match="only be used during on_bar"):
        strategy.sell(symbol="BTC/USDT", qty_percent=50.0)


def test_order_intake_requires_exactly_one_sizing_mode() -> None:
    class MixedSizingStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(quantity=1.0, qty_percent=50.0)

    class MissingSizingStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.sell()

    runtime = _runtime(MixedSizingStrategy())

    with pytest.raises(ValueError, match="exactly one sizing mode"):
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
                is_closed=True,
            )
        )

    runtime = _runtime(MissingSizingStrategy())
    with pytest.raises(ValueError, match="exactly one sizing mode"):
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
                is_closed=True,
            )
        )


@pytest.mark.parametrize("invalid_percent", (0.0, -5.0, 120.0))
def test_qty_percent_validation_rejects_out_of_range_values(invalid_percent: float) -> None:
    class InvalidPercentStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(qty_percent=invalid_percent)

    runtime = _runtime(InvalidPercentStrategy())

    with pytest.raises(ValueError, match="qty_percent"):
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
                is_closed=True,
            )
        )


def test_qty_percent_validation_rejects_non_numeric_values() -> None:
    class InvalidPercentTypeStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(qty_percent="bad")  # type: ignore[arg-type]

    runtime = _runtime(InvalidPercentTypeStrategy())

    with pytest.raises(ValueError, match="qty_percent"):
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
                is_closed=True,
            )
        )


def test_implicit_buy_uses_active_bar_symbol() -> None:
    strategy = ImplicitSymbolBuyOnFirstBarStrategy()
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
        PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
            tag="entry",
        ),
    )


def test_explicit_symbol_buy_matching_active_series_is_preserved() -> None:
    strategy = ExplicitSymbolBuyOnFirstBarStrategy()
    runtime = _runtime(strategy)

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
            is_closed=True,
        )
    )

    assert runtime.order_state().pending == (
        PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="market",
            tag="entry",
        ),
    )


def test_explicit_symbol_buy_mismatch_is_rejected_in_single_symbol_workflow() -> None:
    strategy = MismatchedExplicitSymbolBuyOnFirstBarStrategy()
    runtime = _runtime(strategy)

    with pytest.raises(ValueError, match="active series symbol"):
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
                is_closed=True,
            )
        )


def test_implicit_sell_uses_active_bar_symbol() -> None:
    strategy = ImplicitSymbolSellOnFirstBarStrategy()
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
        PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            quantity=2.0,
            order_type="limit",
            limit_price=105.0,
            tag="take-profit",
        ),
    )


def test_explicit_symbol_sell_matching_active_series_is_preserved() -> None:
    strategy = ExplicitSymbolSellOnFirstBarStrategy()
    runtime = _runtime(strategy)

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
            is_closed=True,
        )
    )

    assert runtime.order_state().pending == (
        PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            quantity=2.0,
            order_type="limit",
            limit_price=105.0,
            tag="take-profit",
        ),
    )


def test_explicit_symbol_sell_mismatch_is_rejected_in_single_symbol_workflow() -> None:
    strategy = MismatchedExplicitSymbolSellOnFirstBarStrategy()
    runtime = _runtime(strategy)

    with pytest.raises(ValueError, match="active series symbol"):
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
                is_closed=True,
            )
        )


def test_implicit_symbol_ordering_outside_active_bar_context_keeps_on_bar_guard() -> None:
    strategy = ImplicitSymbolBuyOnFirstBarStrategy()

    with pytest.raises(ValueError, match="only be used during on_bar"):
        strategy.buy(quantity=1.0)

    with pytest.raises(ValueError, match="only be used during on_bar"):
        strategy.sell(quantity=1.0)

    with pytest.raises(ValueError, match="only be used during on_bar"):
        strategy.buy(qty_percent=50.0)

    with pytest.raises(ValueError, match="only be used during on_bar"):
        strategy.sell(qty_percent=50.0)


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


def test_backtest_engine_calls_init_for_each_run_on_reused_strategy_instance() -> None:
    strategy = RecordsInitCallsStrategy()
    engine = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=0.1, slippage_ticks=1.0, fee_rate=0.001),
    )
    bars = _make_bar_series(
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
    )

    engine.run(
        bars=bars,
        strategy=strategy,
    )
    engine.run(
        bars=bars,
        strategy=strategy,
    )

    assert strategy.init_calls == 2


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
        PendingOrderRequest(
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
        PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            quantity=2.0,
            order_type="limit",
            limit_price=105.0,
            tag="take-profit",
        ),
    )
    assert runtime.order_state().active == ()


def test_limit_orders_require_limit_price_at_intake() -> None:
    class MissingLimitPriceQuantityStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(quantity=1.0, order_type="limit")

    class MissingLimitPricePercentStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(qty_percent=50.0, order_type="limit")

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

    for strategy in (MissingLimitPriceQuantityStrategy(), MissingLimitPricePercentStrategy()):
        with pytest.raises(ValueError, match="limit orders require a limit_price"):
            _runtime(strategy).handle_bar(first_bar)


def test_stop_market_above_close_is_normalized_with_crosses_above() -> None:
    runtime = _runtime(StopMarketAboveCloseBuyStrategy())

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
            is_closed=True,
        )
    )

    assert runtime.order_state().pending == (
        PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            stop_price=120.0,
            trigger_condition="crosses_above",
            tag="stop-entry",
        ),
    )


def test_stop_market_below_close_is_normalized_with_crosses_below() -> None:
    runtime = _runtime(StopMarketBelowCloseBuyStrategy())

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
            is_closed=True,
        )
    )

    assert runtime.order_state().pending == (
        PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            stop_price=90.0,
            trigger_condition="crosses_below",
            tag="stop-entry",
        ),
    )


def test_stop_market_rejects_missing_stop_price() -> None:
    class MissingStopPriceStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(quantity=1.0, order_type="stop_market")

    with pytest.raises(ValueError, match="stop_market orders require a stop_price"):
        _runtime(MissingStopPriceStrategy()).handle_bar(
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
                is_closed=True,
            )
        )


def test_stop_market_rejects_qty_percent_in_the_first_slice() -> None:
    class StopPercentStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(qty_percent=50.0, order_type="stop_market", stop_price=120.0)

    with pytest.raises(ValueError, match="qty_percent is not supported for stop_market"):
        _runtime(StopPercentStrategy()).handle_bar(
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
                is_closed=True,
            )
        )


def test_stop_market_rejects_stop_price_equal_to_active_close() -> None:
    class EqualStopPriceStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(quantity=1.0, order_type="stop_market", stop_price=104.0)

    with pytest.raises(ValueError, match="stop_price equal to the active bar close"):
        _runtime(EqualStopPriceStrategy()).handle_bar(
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
                is_closed=True,
            )
        )


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


def test_qty_percent_orders_preserve_symbol_and_percent_before_runtime_resolution() -> None:
    runtime = _runtime(PercentBuyOnFirstBarStrategy())
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
            is_closed=True,
        )
    )

    assert runtime.order_state().pending == (
        PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=80.0,
            order_type="market",
            tag="percent-entry",
        ),
    )


def test_percent_orders_inherit_implicit_symbol_during_on_bar() -> None:
    buy_runtime = _runtime(PercentBuyOnFirstBarStrategy())
    buy_runtime.handle_bar(
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
            is_closed=True,
        )
    )
    assert buy_runtime.order_state().pending == (
        PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=80.0,
            order_type="market",
            tag="percent-entry",
        ),
    )

    sell_runtime = _runtime(ImplicitSymbolPercentSellOnFirstBarStrategy())
    sell_runtime.handle_bar(
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
            is_closed=True,
        )
    )
    assert sell_runtime.order_state().pending == (
        PendingOrderRequest(
            symbol="BTC/USDT",
            side="sell",
            qty_percent=30.0,
            order_type="market",
            tag="scale-out",
        ),
    )


def test_sell_is_the_current_long_exit_surface() -> None:
    class SellWhileFlatInLongOnlyScopeStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.sell(quantity=1.0, tag="flat-exit")

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


def test_percent_sell_is_the_current_long_exit_surface() -> None:
    class PercentSellWhileFlatInLongOnlyScopeStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.sell(qty_percent=100.0, tag="flat-exit")

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
        strategy=PercentSellWhileFlatInLongOnlyScopeStrategy(),
    )

    assert result.trade_log == ()
    assert result.final_state.position_quantity == 0.0
    assert result.final_state.cash == 1_000.0
