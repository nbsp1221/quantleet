from __future__ import annotations

import importlib

import pytest

import quantleet.integrations.venues.ccxt.market_data as exchange_backend
from tests.support_ccxt import FakeExchangeClient


def _ccxt_source_type() -> type:
    data_module = importlib.import_module("quantleet.data")
    return data_module.CCXTDataSource


def _time_bar_type() -> type:
    data_module = importlib.import_module("quantleet.data")
    return data_module.TimeBar


def _bar_series_type() -> type:
    data_module = importlib.import_module("quantleet.data")
    return data_module.BarSeries


def test_ccxt_source_loads_binance_usdm_bars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeExchangeClient(
        pages=[
            [[1_700_000_000_000, 1.0, 2.0, 0.5, 1.5, 10.0]],
            [],
        ]
    )

    monkeypatch.setattr(exchange_backend, "_make_ccxt_exchange", lambda **_: fake_client)

    source = _ccxt_source_type()(
        exchange="binance",
        market="usdm",
        symbol="BTC/USDT:USDT",
        timeframe="1h",
        start=1_700_000_000_000,
        end=1_700_000_300_000,
    )

    bars = source.load()

    bar_series_type = _bar_series_type()
    time_bar_type = _time_bar_type()

    assert isinstance(bars, bar_series_type)
    assert bars.symbol == "BTC/USDT:USDT"
    assert bars.timeframe == "1h"
    assert bars.bar_type == "time"
    assert bars.rows == (
        time_bar_type(
            timestamp=1_700_000_000_000,
            open=1.0,
            high=2.0,
            low=0.5,
            close=1.5,
            volume=10.0,
        ),
    )
    assert len(fake_client.calls) == 2
    assert fake_client.calls[0]["symbol"] == "BTC/USDT:USDT"
    assert fake_client.calls[0]["timeframe"] == "1h"
    assert fake_client.calls[0]["since"] == 1_700_000_000_000
    assert fake_client.calls[0]["params"] == {"end": 1_700_000_300_000}


def test_ccxt_source_does_not_hard_block_other_supported_exchanges(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_exchange() -> FakeExchangeClient:
        return FakeExchangeClient([[1_700_000_000_000, 1.0, 2.0, 0.5, 1.5, 10.0]])

    monkeypatch.setattr(exchange_backend.ccxt, "bitget", fake_exchange)

    source = _ccxt_source_type()(
        exchange="bitget",
        market="spot",
        symbol="BTC/USDT",
        timeframe="1h",
    )

    bars = source.load()

    assert bars.rows[0].close == 1.5


def test_ccxt_source_paginates_until_backend_exhausted_and_deduplicates_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(exchange_backend, "_DEFAULT_PAGINATION_LIMIT", 2)
    fake_client = FakeExchangeClient(
        pages=[
            [
                [1_700_000_000_000, 1.0, 2.0, 0.5, 1.5, 10.0],
                [1_700_000_300_000, 2.0, 3.0, 1.5, 2.5, 20.0],
            ],
            [
                [1_700_000_300_000, 2.0, 3.0, 1.5, 2.5, 20.0],
                [1_700_000_600_000, 3.0, 4.0, 2.5, 3.5, 30.0],
            ],
            [],
        ]
    )

    monkeypatch.setattr(exchange_backend, "_make_ccxt_exchange", lambda **_: fake_client)

    source = _ccxt_source_type()(
        exchange="binance",
        market="spot",
        symbol="BTC/USDT",
        timeframe="5m",
        start=1_700_000_000_000,
    )

    bars = source.load()

    assert tuple(bar.timestamp for bar in bars.rows) == (
        1_700_000_000_000,
        1_700_000_300_000,
        1_700_000_600_000,
    )
    assert len(fake_client.calls) == 3


def test_ccxt_source_treats_limit_as_total_returned_row_cap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(exchange_backend, "_DEFAULT_PAGINATION_LIMIT", 2)
    fake_client = FakeExchangeClient(
        pages=[
            [
                [1_700_000_000_000, 1.0, 2.0, 0.5, 1.5, 10.0],
                [1_700_000_300_000, 2.0, 3.0, 1.5, 2.5, 20.0],
            ],
            [
                [1_700_000_600_000, 3.0, 4.0, 2.5, 3.5, 30.0],
                [1_700_000_900_000, 4.0, 5.0, 3.5, 4.5, 40.0],
            ],
            [],
        ]
    )

    monkeypatch.setattr(exchange_backend, "_make_ccxt_exchange", lambda **_: fake_client)

    source = _ccxt_source_type()(
        exchange="binance",
        market="spot",
        symbol="BTC/USDT",
        timeframe="5m",
        start=1_700_000_000_000,
        limit=3,
    )

    bars = source.load()

    assert tuple(bar.timestamp for bar in bars.rows) == (
        1_700_000_000_000,
        1_700_000_300_000,
        1_700_000_600_000,
    )
    assert len(bars.rows) == 3


def test_ccxt_source_accepts_provider_native_bounded_timeframes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeExchangeClient(
        pages=[
            [
                [1_700_000_000_000, 1.0, 2.0, 0.5, 1.5, 10.0],
            ],
            [],
        ]
    )

    monkeypatch.setattr(exchange_backend, "_make_ccxt_exchange", lambda **_: fake_client)

    source = _ccxt_source_type()(
        exchange="binance",
        market="spot",
        symbol="BTC/USDT",
        timeframe="1M",
        start=1_700_000_000_000,
    )

    bars = source.load()

    assert tuple(bar.timestamp for bar in bars.rows) == (1_700_000_000_000,)


def test_ccxt_source_returns_all_rows_even_when_final_page_is_short(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(exchange_backend, "_DEFAULT_PAGINATION_LIMIT", 2)
    fake_client = FakeExchangeClient(
        pages=[
            [
                [1_700_000_000_000, 1.0, 2.0, 0.5, 1.5, 10.0],
                [1_700_000_300_000, 2.0, 3.0, 1.5, 2.5, 20.0],
            ],
            [
                [1_700_000_600_000, 3.0, 4.0, 2.5, 3.5, 30.0],
            ],
        ]
    )

    monkeypatch.setattr(exchange_backend, "_make_ccxt_exchange", lambda **_: fake_client)

    source = _ccxt_source_type()(
        exchange="binance",
        market="spot",
        symbol="BTC/USDT",
        timeframe="5m",
        start=1_700_000_000_000,
    )

    bars = source.load()

    assert tuple(bar.timestamp for bar in bars.rows) == (
        1_700_000_000_000,
        1_700_000_300_000,
        1_700_000_600_000,
    )
    assert len(fake_client.calls) == 3


def test_ccxt_source_excludes_rows_at_or_beyond_end(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeExchangeClient(
        pages=[
            [
                [1_700_000_000_000, 1.0, 2.0, 0.5, 1.5, 10.0],
                [1_700_000_300_000, 2.0, 3.0, 1.5, 2.5, 20.0],
            ],
            [
                [1_700_000_600_000, 3.0, 4.0, 2.5, 3.5, 30.0],
            ],
        ]
    )

    monkeypatch.setattr(exchange_backend, "_make_ccxt_exchange", lambda **_: fake_client)

    source = _ccxt_source_type()(
        exchange="binance",
        market="spot",
        symbol="BTC/USDT",
        timeframe="5m",
        start=1_700_000_000_000,
        end=1_700_000_600_000,
    )

    bars = source.load()

    assert tuple(bar.timestamp for bar in bars.rows) == (
        1_700_000_000_000,
        1_700_000_300_000,
    )
