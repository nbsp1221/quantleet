from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from quantcraft.backtest.execution_model import ConservativeOHLCVExecutionModel
from quantcraft.data import BarSeries, TimeBar
from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import BarEvent, TickEvent
from quantcraft.trading.domain.intents import OrderIntent
from quantcraft.trading.domain.matching import match_order
from quantcraft.trading.domain.orders import Order

_ZERO_COSTS = CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0)


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


def test_execution_model_exposes_expected_name() -> None:
    assert ConservativeOHLCVExecutionModel().name == "conservative_ohlcv"


def test_bullish_bar_uses_open_low_high_close_path() -> None:
    bar = TimeBar(
        timestamp=60,
        open=100.0,
        high=105.0,
        low=95.0,
        close=104.0,
        volume=10.0,
    )

    assert ConservativeOHLCVExecutionModel().infer_intrabar_prices(bar) == (
        100.0,
        95.0,
        105.0,
        104.0,
    )


def test_bearish_bar_uses_open_high_low_close_path() -> None:
    bar = TimeBar(
        timestamp=120,
        open=110.0,
        high=112.0,
        low=108.0,
        close=109.0,
        volume=12.0,
    )

    assert ConservativeOHLCVExecutionModel().infer_intrabar_prices(bar) == (
        110.0,
        112.0,
        108.0,
        109.0,
    )


def test_doji_bar_explicitly_uses_open_low_high_close_path() -> None:
    bar = TimeBar(
        timestamp=180,
        open=100.0,
        high=103.0,
        low=97.0,
        close=100.0,
        volume=8.0,
    )

    assert ConservativeOHLCVExecutionModel().infer_intrabar_prices(bar) == (
        100.0,
        97.0,
        103.0,
        100.0,
    )


def test_gap_segment_skips_intermediate_prices() -> None:
    events = ConservativeOHLCVExecutionModel().events_from_bars(
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
                TimeBar(
                    timestamp=120,
                    open=110.0,
                    high=112.0,
                    low=108.0,
                    close=109.0,
                    volume=12.0,
                ),
            )
        )
    )

    tick_prices = [event.last for event in events if isinstance(event, TickEvent)]

    assert tick_prices == [100.0, 95.0, 105.0, 104.0, 110.0, 112.0, 108.0, 109.0]


def test_malformed_time_bar_is_rejected_before_event_conversion() -> None:
    with pytest.raises(ValueError, match="invalid time bar"):
        TimeBar(
            timestamp=60,
            open=100.0,
            high=99.0,
            low=95.0,
            close=98.0,
            volume=10.0,
        )


def test_out_of_order_time_bars_are_rejected_before_gap_modeling() -> None:
    with pytest.raises(ValueError, match="out-of-order time bars"):
        ConservativeOHLCVExecutionModel().events_from_bars(
            bars=_make_bar_series(
                (
                    TimeBar(
                        timestamp=120,
                        open=110.0,
                        high=112.0,
                        low=108.0,
                        close=109.0,
                        volume=12.0,
                    ),
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
        )


def test_synthetic_ticks_use_unbounded_book_depth_representation() -> None:
    events = ConservativeOHLCVExecutionModel().events_from_bars(
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
        )
    )

    ticks = tuple(event for event in events if isinstance(event, TickEvent))

    assert ticks
    assert all(math.isinf(tick.bids[0][1]) for tick in ticks)
    assert all(math.isinf(tick.asks[0][1]) for tick in ticks)
    assert all(tick.last_size is None for tick in ticks)


def test_rising_segment_sell_limit_fills_at_limit_price() -> None:
    bar = TimeBar(
        timestamp=120,
        open=100.0,
        high=120.0,
        low=95.0,
        close=118.0,
        volume=10.0,
    )
    order = Order.from_intent(
        order_id=1,
        intent=OrderIntent(
        symbol="BTC/USDT",
        side="sell",
        quantity=1.0,
        order_type="limit",
        limit_price=110.0,
        ),
    )

    ticks = tuple(
        ConservativeOHLCVExecutionModel().tick_events_for_bar(
            symbol="BTC/USDT",
            previous_close=100.0,
            bar=bar,
            active_orders=(order,),
        )
    )

    fill = next(
        match_order(order, tick, _ZERO_COSTS)
        for tick in ticks
        if match_order(order, tick, _ZERO_COSTS) is not None
    )

    assert fill.price == 110.0
    assert fill.timestamp == 120


def test_gap_crossed_buy_limit_fills_at_open() -> None:
    bar = TimeBar(
        timestamp=120,
        open=95.0,
        high=101.0,
        low=90.0,
        close=99.0,
        volume=10.0,
    )
    order = Order.from_intent(
        order_id=1,
        intent=OrderIntent(
        symbol="BTC/USDT",
        side="buy",
        quantity=1.0,
        order_type="limit",
        limit_price=100.0,
        ),
    )

    ticks = tuple(
        ConservativeOHLCVExecutionModel().tick_events_for_bar(
            symbol="BTC/USDT",
            previous_close=104.0,
            bar=bar,
            active_orders=(order,),
        )
    )

    fill = next(
        match_order(order, tick, _ZERO_COSTS)
        for tick in ticks
        if match_order(order, tick, _ZERO_COSTS) is not None
    )

    assert fill.price == 95.0
    assert fill.timestamp == 120


def test_marketable_buy_limit_fills_at_first_executable_open() -> None:
    bar = TimeBar(
        timestamp=120,
        open=121.0,
        high=125.0,
        low=119.0,
        close=124.0,
        volume=10.0,
    )
    order = Order.from_intent(
        order_id=1,
        intent=OrderIntent(
        symbol="BTC/USDT",
        side="buy",
        quantity=1.0,
        order_type="limit",
        limit_price=130.0,
        ),
    )

    ticks = tuple(
        ConservativeOHLCVExecutionModel().tick_events_for_bar(
            symbol="BTC/USDT",
            previous_close=120.0,
            bar=bar,
            active_orders=(order,),
        )
    )

    fill = next(
        match_order(order, tick, _ZERO_COSTS)
        for tick in ticks
        if match_order(order, tick, _ZERO_COSTS) is not None
    )

    assert fill.price == 121.0
    assert fill.timestamp == 120


def test_conversion_from_checked_in_fixture_is_deterministic() -> None:
    fixture_path = Path(__file__).with_name("fixtures") / "ohlcv_fixture.json"
    payload = json.loads(fixture_path.read_text())
    rows = tuple(TimeBar(**row) for row in payload)
    bars = _make_bar_series(rows)
    model = ConservativeOHLCVExecutionModel()

    first = model.events_from_bars(bars=bars)
    second = model.events_from_bars(bars=bars)

    assert first == second
    assert first == (
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((100.0, math.inf),),
            asks=((100.0, math.inf),),
            last=100.0,
        ),
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((95.0, math.inf),),
            asks=((95.0, math.inf),),
            last=95.0,
        ),
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((105.0, math.inf),),
            asks=((105.0, math.inf),),
            last=105.0,
        ),
        TickEvent(
            timestamp=60,
            symbol="BTC/USDT",
            bids=((104.0, math.inf),),
            asks=((104.0, math.inf),),
            last=104.0,
        ),
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
        ),
        TickEvent(
            timestamp=120,
            symbol="BTC/USDT",
            bids=((110.0, math.inf),),
            asks=((110.0, math.inf),),
            last=110.0,
        ),
        TickEvent(
            timestamp=120,
            symbol="BTC/USDT",
            bids=((112.0, math.inf),),
            asks=((112.0, math.inf),),
            last=112.0,
        ),
        TickEvent(
            timestamp=120,
            symbol="BTC/USDT",
            bids=((108.0, math.inf),),
            asks=((108.0, math.inf),),
            last=108.0,
        ),
        TickEvent(
            timestamp=120,
            symbol="BTC/USDT",
            bids=((109.0, math.inf),),
            asks=((109.0, math.inf),),
            last=109.0,
        ),
        BarEvent(
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
        ),
    )
