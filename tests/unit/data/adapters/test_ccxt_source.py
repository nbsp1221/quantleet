from __future__ import annotations

import pytest

import quantcraft.data.adapters.exchange_backend as exchange_backend
from quantcraft.data import CCXTDataSource, OHLCVBar


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


def test_ccxt_source_loads_binance_usdm_bars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeExchangeClient([[1_700_000_000_000, 1.0, 2.0, 0.5, 1.5, 10.0]])

    monkeypatch.setattr(exchange_backend, "_make_ccxt_exchange", lambda **_: fake_client)

    source = CCXTDataSource(
        exchange="binance",
        market="usdm",
        symbol="BTC/USDT:USDT",
        timeframe="1h",
        start=1_700_000_000_000,
        end=1_700_000_300_000,
    )

    bars = source.load()

    assert bars == (
        OHLCVBar(
            timestamp=1_700_000_000_000,
            open=1.0,
            high=2.0,
            low=0.5,
            close=1.5,
            volume=10.0,
        ),
    )
    assert fake_client.calls == [
        {
            "symbol": "BTC/USDT:USDT",
            "timeframe": "1h",
            "since": 1_700_000_000_000,
            "limit": None,
            "params": {"end": 1_700_000_300_000},
        }
    ]


def test_ccxt_source_does_not_hard_block_other_supported_exchanges(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_exchange() -> FakeExchangeClient:
        return FakeExchangeClient([[1_700_000_000_000, 1.0, 2.0, 0.5, 1.5, 10.0]])

    monkeypatch.setattr(exchange_backend.ccxt, "bitget", fake_exchange)

    source = CCXTDataSource(
        exchange="bitget",
        market="spot",
        symbol="BTC/USDT",
        timeframe="1h",
    )

    bars = source.load()

    assert bars[0].close == 1.5
