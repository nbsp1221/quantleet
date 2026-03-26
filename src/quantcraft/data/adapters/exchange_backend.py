from __future__ import annotations

import contextlib
import os
from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, cast


@contextlib.contextmanager
def _suppress_import_stderr() -> Iterator[None]:
    original_stderr = os.dup(2)
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull_fd, 2)
        yield
    finally:
        os.dup2(original_stderr, 2)
        os.close(original_stderr)
        os.close(devnull_fd)


with _suppress_import_stderr():
    import ccxt

__all__ = [
    "CCXTBackend",
    "Exchange",
    "MarketType",
    "TimeBar",
    "_make_ccxt_exchange",
    "_validate_symbol_contract",
    "ccxt",
]


class MarketType(StrEnum):
    SPOT = "spot"
    USDM = "usdm"


@dataclass(frozen=True, slots=True, kw_only=True)
class TimeBar:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class Exchange:
    """Public exchange facade.

    The public API stays stable even if the underlying implementation changes
    from the common CCXT path to a future direct backend for specific exchanges.
    """

    def __init__(self, *, name: str, market_type: MarketType) -> None:
        self.name = name
        self.market_type = market_type
        self._backend = CCXTBackend(name=name, market_type=market_type)

    def fetch_ohlcv(
        self,
        *,
        symbol: str,
        timeframe: str,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> list[TimeBar]:
        _validate_symbol_contract(self.market_type, symbol)
        rows = self._backend.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            start=start,
            end=end,
            limit=limit,
        )
        return [
            TimeBar(
                timestamp=int(row[0]),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
            )
            for row in rows
        ]


class CCXTBackend:
    """Default implementation for exchanges that work through CCXT."""

    def __init__(self, *, name: str, market_type: MarketType) -> None:
        self.name = name
        self.market_type = market_type
        self._exchange = _make_ccxt_exchange(name=name, market_type=market_type)

    def fetch_ohlcv(
        self,
        *,
        symbol: str,
        timeframe: str,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> list[list[float]]:
        params: dict[str, object] = {"end": end} if end is not None else {}
        return cast(
            list[list[float]],
            self._exchange.fetch_ohlcv(
                symbol,
                timeframe,
                since=start,
                limit=limit,
                params=params,
            ),
        )


def _make_ccxt_exchange(*, name: str, market_type: MarketType) -> Any:
    exchange_class = getattr(ccxt, name, None)
    if exchange_class is None:
        raise ValueError(f"unsupported exchange: {name}")

    if market_type is MarketType.SPOT:
        return exchange_class()

    usdm_class = getattr(ccxt, f"{name}usdm", None)
    if usdm_class is not None:
        return usdm_class()

    return exchange_class(
        {
            "options": {
                "defaultType": "swap",
            }
        }
    )


def _validate_symbol_contract(market_type: MarketType, symbol: str) -> None:
    if market_type is MarketType.USDM and ":" not in symbol:
        raise ValueError(
            "USD-M market requires a canonical CCXT USD-M symbol, for example 'BTC/USDT:USDT'",
        )
