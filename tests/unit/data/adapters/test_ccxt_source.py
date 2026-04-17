from __future__ import annotations

import importlib

import pytest

import quantcraft.integrations.venues.ccxt.market_data as exchange_backend


class FakeExchangeClient:
    def __init__(
        self,
        rows: list[list[float]] | None = None,
        *,
        pages: list[list[list[float]]] | None = None,
        options: dict | None = None,
    ) -> None:
        if rows is not None and pages is not None:
            raise ValueError("rows and pages are mutually exclusive")
        self.rows = rows or []
        self.pages = pages[:] if pages is not None else None
        self.options = options or {}
        self.calls: list[dict[str, object]] = []

    def parse_timeframe(self, timeframe: str) -> int:
        mapping = {
            "1s": 1,
            "1m": 60,
            "3m": 180,
            "5m": 300,
            "1h": 3600,
            "1d": 86400,
            "1w": 604800,
            "1M": 2592000,
        }
        return mapping[timeframe]

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since: int | None = None,
        limit: int | None = None,
        params: dict[str, object] | None = None,
    ) -> list[list[float]]:
        self.calls.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "since": since,
                "limit": limit,
                "params": params,
            }
        )
        if self.pages is not None:
            if self.pages:
                return self.pages.pop(0)
            return []
        return self.rows


def _ccxt_source_type() -> type:
    data_module = importlib.import_module("quantcraft.data")
    return getattr(data_module, "CCXTDataSource")


def _time_bar_type() -> type:
    data_module = importlib.import_module("quantcraft.data")
    return getattr(data_module, "TimeBar")


def _bar_series_type() -> type:
    data_module = importlib.import_module("quantcraft.data")
    return getattr(data_module, "BarSeries")


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


def test_ccxt_source_accepts_provider_native_monthly_timeframe_for_bounded_queries(
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
