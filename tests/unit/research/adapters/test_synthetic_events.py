from __future__ import annotations

import inspect
import json
import math
from pathlib import Path

import pytest

from quantcraft.data import OHLCVBar
from quantcraft.research.adapters.synthetic_events import (
    convert_ohlcv_to_backtest_events,
    infer_intrabar_prices,
)
from quantcraft.trading.domain.events import BarEvent, TickEvent


def test_bullish_bar_uses_open_low_high_close_path() -> None:
    bar = OHLCVBar(
        timestamp=60,
        open=100.0,
        high=105.0,
        low=95.0,
        close=104.0,
        volume=10.0,
    )

    assert infer_intrabar_prices(bar) == (100.0, 95.0, 105.0, 104.0)


def test_bearish_bar_uses_open_high_low_close_path() -> None:
    bar = OHLCVBar(
        timestamp=120,
        open=110.0,
        high=112.0,
        low=108.0,
        close=109.0,
        volume=12.0,
    )

    assert infer_intrabar_prices(bar) == (110.0, 112.0, 108.0, 109.0)


def test_doji_bar_explicitly_uses_open_low_high_close_path() -> None:
    bar = OHLCVBar(
        timestamp=180,
        open=100.0,
        high=103.0,
        low=97.0,
        close=100.0,
        volume=8.0,
    )

    assert infer_intrabar_prices(bar) == (100.0, 97.0, 103.0, 100.0)


def test_gap_segment_skips_intermediate_prices() -> None:
    events = convert_ohlcv_to_backtest_events(
        symbol="BTC/USDT",
        bar_type="time",
        bar_spec="1m",
        rows=(
            OHLCVBar(
                timestamp=60,
                open=100.0,
                high=105.0,
                low=95.0,
                close=104.0,
                volume=10.0,
            ),
            OHLCVBar(
                timestamp=120,
                open=110.0,
                high=112.0,
                low=108.0,
                close=109.0,
                volume=12.0,
            ),
        ),
    )

    tick_prices = [event.last for event in events if isinstance(event, TickEvent)]

    assert tick_prices == [100.0, 95.0, 105.0, 104.0, 110.0, 112.0, 108.0, 109.0]


def test_conversion_api_does_not_accept_order_context() -> None:
    signature = inspect.signature(convert_ohlcv_to_backtest_events)

    assert tuple(signature.parameters) == ("symbol", "bar_type", "bar_spec", "rows")


def test_malformed_ohlcv_row_is_rejected_before_event_conversion() -> None:
    with pytest.raises(ValueError, match="invalid OHLCV row"):
        OHLCVBar(
            timestamp=60,
            open=100.0,
            high=99.0,
            low=95.0,
            close=98.0,
            volume=10.0,
        )


def test_out_of_order_ohlcv_rows_are_rejected_before_gap_modeling() -> None:
    with pytest.raises(ValueError, match="out-of-order OHLCV rows"):
        convert_ohlcv_to_backtest_events(
            symbol="BTC/USDT",
            bar_type="time",
            bar_spec="1m",
            rows=(
                OHLCVBar(
                    timestamp=120,
                    open=110.0,
                    high=112.0,
                    low=108.0,
                    close=109.0,
                    volume=12.0,
                ),
                OHLCVBar(
                    timestamp=60,
                    open=100.0,
                    high=105.0,
                    low=95.0,
                    close=104.0,
                    volume=10.0,
                ),
            ),
        )


def test_synthetic_ticks_use_unbounded_book_depth_representation() -> None:
    events = convert_ohlcv_to_backtest_events(
        symbol="BTC/USDT",
        bar_type="time",
        bar_spec="1m",
        rows=(
            OHLCVBar(
                timestamp=60,
                open=100.0,
                high=105.0,
                low=95.0,
                close=104.0,
                volume=10.0,
            ),
        ),
    )

    ticks = tuple(event for event in events if isinstance(event, TickEvent))

    assert ticks
    assert all(math.isinf(tick.bids[0][1]) for tick in ticks)
    assert all(math.isinf(tick.asks[0][1]) for tick in ticks)
    assert all(tick.last_size is None for tick in ticks)


def test_conversion_from_checked_in_fixture_is_deterministic() -> None:
    fixture_path = Path(__file__).with_name("fixtures") / "ohlcv_fixture.json"
    payload = json.loads(fixture_path.read_text())
    rows = tuple(OHLCVBar(**row) for row in payload)

    first = convert_ohlcv_to_backtest_events(
        symbol="BTC/USDT",
        bar_type="time",
        bar_spec="1m",
        rows=rows,
    )
    second = convert_ohlcv_to_backtest_events(
        symbol="BTC/USDT",
        bar_type="time",
        bar_spec="1m",
        rows=rows,
    )

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
