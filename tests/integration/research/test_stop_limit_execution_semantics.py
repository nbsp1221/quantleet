from __future__ import annotations

from quantleet.data import BarSeries, TimeBar
from quantleet.research import Strategy
from quantleet.trading.domain.costs import CostConfig
from tests.integration.research.support_backtest_runner import (
    BuyStopLimitStrategy,
    SellStopLimitStrategy,
    make_bar_series,
    run_engine_backtest,
    run_engine_backtest_from_source,
)

_ZERO_COSTS = CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0)


class PriorityExitStrategy(Strategy):
    def init(self) -> None:
        self._seen_bars = 0

    def on_bar(self, bar) -> None:
        self._seen_bars += 1
        if self._seen_bars == 1:
            self.buy(quantity=2.0, tag="entry")
        elif self._seen_bars == 2 and self.position.is_open:
            self.sell(quantity=1.25, order_type="limit", limit_price=115.0, tag="older-limit")
            self.sell(
                quantity=0.75,
                order_type="stop_limit",
                stop_price=115.0,
                limit_price=115.0,
                tag="newer-stop-limit",
            )


class FlatSellStopLimitStrategy(Strategy):
    def on_bar(self, bar) -> None:
        self.sell(
            quantity=1.0,
            order_type="stop_limit",
            stop_price=95.0,
            limit_price=94.0,
            tag="flat-stop-limit",
        )


class InMemorySource:
    def __init__(self, bars: BarSeries) -> None:
        self._bars = bars

    def load(self) -> BarSeries:
        return self._bars


def test_buy_stop_limit_gap_through_beyond_limit_triggers_without_trade_log_fill() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=110.0, high=112.0, low=108.0, close=111.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=BuyStopLimitStrategy(stop_price=105.0, limit_price=106.0),
        costs=_ZERO_COSTS,
    )

    assert result.trade_log == ()
    assert result.final_state.position_quantity == 0.0


def test_buy_stop_limit_same_point_trigger_and_fill_uses_trigger_tick() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=100.0, high=106.0, low=99.0, close=104.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=BuyStopLimitStrategy(stop_price=105.0, limit_price=106.0),
        costs=_ZERO_COSTS,
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 105.0, 120),
    )
    assert result.final_state.position_quantity == 1.0


def test_buy_stop_limit_does_not_reuse_pre_trigger_low() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=100.0, high=106.0, low=94.0, close=104.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=BuyStopLimitStrategy(stop_price=105.0, limit_price=95.0),
        costs=_ZERO_COSTS,
    )

    assert result.trade_log == ()
    assert result.final_state.position_quantity == 0.0


def test_buy_stop_limit_post_trigger_tail_fills_at_limit_crossing() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=80.0, high=106.0, low=70.0, close=90.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=BuyStopLimitStrategy(stop_price=105.0, limit_price=95.0),
        costs=_ZERO_COSTS,
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 95.0, 120),
    )


def test_buy_stop_limit_triggered_unfilled_order_can_fill_on_later_bar() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=110.0, high=112.0, low=108.0, close=111.0, volume=12.0),
        TimeBar(timestamp=180, open=111.0, high=112.0, low=106.0, close=107.0, volume=14.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=BuyStopLimitStrategy(stop_price=105.0, limit_price=106.0),
        costs=_ZERO_COSTS,
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 106.0, 180),
    )


def test_sell_stop_limit_gap_through_beyond_limit_triggers_without_trade_log_fill() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=100.0, high=101.0, low=99.0, close=100.0, volume=12.0),
        TimeBar(timestamp=180, open=90.0, high=92.0, low=88.0, close=91.0, volume=14.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=SellStopLimitStrategy(stop_price=95.0, limit_price=94.0),
        costs=_ZERO_COSTS,
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 100.0, 120),
    )
    assert result.final_state.position_quantity == 1.0


def test_sell_stop_limit_same_point_trigger_and_fill_uses_trigger_tick() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=100.0, high=101.0, low=99.0, close=100.0, volume=12.0),
        TimeBar(timestamp=180, open=100.0, high=101.0, low=94.0, close=96.0, volume=14.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=SellStopLimitStrategy(stop_price=95.0, limit_price=94.0),
        costs=_ZERO_COSTS,
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 100.0, 120),
        ("sell", 95.0, 180),
    )
    assert result.final_state.position_quantity == 0.0


def test_sell_stop_limit_does_not_reuse_pre_trigger_high() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=100.0, high=101.0, low=99.0, close=100.0, volume=12.0),
        TimeBar(timestamp=180, open=100.0, high=106.0, low=94.0, close=96.0, volume=14.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=SellStopLimitStrategy(stop_price=95.0, limit_price=105.0),
        costs=_ZERO_COSTS,
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 100.0, 120),
    )
    assert result.final_state.position_quantity == 1.0


def test_sell_stop_limit_post_trigger_tail_fills_at_limit_crossing() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=100.0, high=101.0, low=99.0, close=100.0, volume=12.0),
        TimeBar(timestamp=180, open=120.0, high=130.0, low=94.0, close=110.0, volume=14.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=SellStopLimitStrategy(stop_price=95.0, limit_price=105.0),
        costs=_ZERO_COSTS,
    )

    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 100.0, 120),
        ("sell", 105.0, 180),
    )


def test_existing_executable_order_fills_before_newly_triggered_stop_limit_at_same_tick() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=100.0, high=101.0, low=99.0, close=100.0, volume=12.0),
        TimeBar(timestamp=180, open=115.0, high=116.0, low=114.0, close=115.0, volume=14.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=PriorityExitStrategy(),
        costs=_ZERO_COSTS,
    )

    assert tuple(
        (fill.side, fill.quantity, fill.price, fill.timestamp) for fill in result.trade_log
    ) == (
        ("buy", 2.0, 100.0, 120),
        ("sell", 1.25, 115.0, 180),
        ("sell", 0.75, 115.0, 180),
    )


def test_flat_sell_stop_limit_does_not_become_short_entry() -> None:
    rows = (
        TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
        TimeBar(timestamp=120, open=95.0, high=96.0, low=93.0, close=94.0, volume=12.0),
    )

    result = run_engine_backtest(
        bars=make_bar_series(rows),
        strategy=FlatSellStopLimitStrategy(),
        costs=_ZERO_COSTS,
    )

    assert result.trade_log == ()
    assert result.final_state.position_quantity == 0.0


def test_source_based_run_path_matches_bars_based_stop_limit_semantics() -> None:
    bars = make_bar_series(
        (
            TimeBar(timestamp=60, open=100.0, high=100.0, low=100.0, close=100.0, volume=10.0),
            TimeBar(timestamp=120, open=100.0, high=106.0, low=99.0, close=104.0, volume=12.0),
        )
    )

    bars_result = run_engine_backtest(
        bars=bars,
        strategy=BuyStopLimitStrategy(stop_price=105.0, limit_price=106.0),
        costs=_ZERO_COSTS,
    )
    source_result = run_engine_backtest_from_source(
        source=InMemorySource(bars),
        strategy=BuyStopLimitStrategy(stop_price=105.0, limit_price=106.0),
        costs=_ZERO_COSTS,
    )

    assert source_result.trade_log == bars_result.trade_log
    assert source_result.final_state == bars_result.final_state
