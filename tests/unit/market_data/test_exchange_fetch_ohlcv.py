from __future__ import annotations

import pytest

import quantcraft.exchange as exchange_module


class FakeExchangeClient:
    def __init__(
        self,
        rows: list[list[float]] | None = None,
        *,
        options: dict | None = None,
    ) -> None:
        self.rows = rows or []
        self.options = options or {}
        self.calls: list[dict[str, object]] = []

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
        return self.rows


def test_exchange_fetch_ohlcv_normalizes_rows_for_binance_spot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeExchangeClient([[1_700_000_000_000, 1.0, 2.0, 0.5, 1.5, 10.0]])

    monkeypatch.setattr(exchange_module, "_make_ccxt_exchange", lambda **_: fake_client)

    exchange = exchange_module.Exchange(name="binance", market_type=exchange_module.MarketType.SPOT)
    rows = exchange.fetch_ohlcv(
        symbol="BTC/USDT",
        timeframe="1h",
        start=1_700_000_000_000,
        limit=100,
    )

    assert fake_client.calls == [
        {
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "since": 1_700_000_000_000,
            "limit": 100,
            "params": {},
        }
    ]
    assert rows == [
        exchange_module.TimeBar(
            timestamp=1_700_000_000_000,
            open=1.0,
            high=2.0,
            low=0.5,
            close=1.5,
            volume=10.0,
        )
    ]


def test_exchange_fetch_ohlcv_forwards_end_for_binance_usdm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeExchangeClient()

    monkeypatch.setattr(exchange_module, "_make_ccxt_exchange", lambda **_: fake_client)

    exchange = exchange_module.Exchange(name="binance", market_type=exchange_module.MarketType.USDM)
    rows = exchange.fetch_ohlcv(
        symbol="BTC/USDT:USDT",
        timeframe="5m",
        start=1_700_000_000_000,
        end=1_700_000_300_000,
        limit=50,
    )

    assert rows == []
    assert fake_client.calls == [
        {
            "symbol": "BTC/USDT:USDT",
            "timeframe": "5m",
            "since": 1_700_000_000_000,
            "limit": 50,
            "params": {"end": 1_700_000_300_000},
        }
    ]


def test_exchange_rejects_non_canonical_usdm_symbol() -> None:
    exchange = exchange_module.Exchange(name="binance", market_type=exchange_module.MarketType.USDM)

    with pytest.raises(ValueError, match="USD-M market requires a canonical CCXT USD-M symbol"):
        exchange.fetch_ohlcv(symbol="BTC/USDT", timeframe="1h", limit=10)


def test_make_ccxt_exchange_uses_generic_spot_exchange_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created: list[FakeExchangeClient] = []

    def fake_bybit() -> FakeExchangeClient:
        client = FakeExchangeClient()
        created.append(client)
        return client

    monkeypatch.setattr(exchange_module.ccxt, "bybit", fake_bybit)

    exchange = exchange_module.Exchange(name="bybit", market_type=exchange_module.MarketType.SPOT)

    assert exchange.name == "bybit"
    assert exchange.market_type is exchange_module.MarketType.SPOT
    assert len(created) == 1


def test_make_ccxt_exchange_uses_explicit_usdm_class_when_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created: list[FakeExchangeClient] = []

    def fake_binanceusdm() -> FakeExchangeClient:
        client = FakeExchangeClient()
        created.append(client)
        return client

    monkeypatch.setattr(exchange_module.ccxt, "binanceusdm", fake_binanceusdm)

    exchange = exchange_module.Exchange(name="binance", market_type=exchange_module.MarketType.USDM)

    assert exchange.name == "binance"
    assert exchange.market_type is exchange_module.MarketType.USDM
    assert len(created) == 1


def test_make_ccxt_exchange_falls_back_to_swap_default_type_for_usdm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created: list[FakeExchangeClient] = []

    def fake_bybit(options: dict | None = None) -> FakeExchangeClient:
        client = FakeExchangeClient(options=options)
        created.append(client)
        return client

    monkeypatch.setattr(exchange_module.ccxt, "bybit", fake_bybit)
    monkeypatch.delattr(exchange_module.ccxt, "bybitusdm", raising=False)

    exchange = exchange_module.Exchange(name="bybit", market_type=exchange_module.MarketType.USDM)

    assert exchange.name == "bybit"
    assert exchange.market_type is exchange_module.MarketType.USDM
    assert len(created) == 1
    assert created[0].options == {"options": {"defaultType": "swap"}}


@pytest.mark.parametrize("exchange_name", ["bitget", "mexc"])
def test_exchange_supports_other_ccxt_spot_exchanges_without_source_changes(
    monkeypatch: pytest.MonkeyPatch,
    exchange_name: str,
) -> None:
    def fake_exchange() -> FakeExchangeClient:
        return FakeExchangeClient()

    monkeypatch.setattr(exchange_module.ccxt, exchange_name, fake_exchange)

    exchange = exchange_module.Exchange(
        name=exchange_name,
        market_type=exchange_module.MarketType.SPOT,
    )

    assert exchange.name == exchange_name
    assert exchange.market_type is exchange_module.MarketType.SPOT


def test_exchange_rejects_unknown_exchange_name() -> None:
    with pytest.raises(ValueError, match="unsupported exchange"):
        exchange_module.Exchange(
            name="not-a-real-exchange",
            market_type=exchange_module.MarketType.SPOT,
        )
