from __future__ import annotations

import contextlib
import os
from collections.abc import Iterator
from enum import StrEnum
from typing import Any, cast

from quantcraft.data.bars import TimeBar


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

_DEFAULT_PAGINATION_LIMIT = 1_000

__all__ = [
    "CCXTBackend",
    "Exchange",
    "MarketType",
    "TimeBar",
    "_DEFAULT_PAGINATION_LIMIT",
    "_fetch_ohlcv_range",
    "_make_ccxt_exchange",
    "_validate_symbol_contract",
    "ccxt",
]


class MarketType(StrEnum):
    SPOT = "spot"
    USDM = "usdm"


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


def _fetch_ohlcv_range(
    *,
    name: str,
    market_type: MarketType,
    symbol: str,
    timeframe: str,
    start: int | None = None,
    end: int | None = None,
    limit: int | None = None,
) -> list[TimeBar]:
    _validate_symbol_contract(market_type, symbol)
    if start is None:
        return Exchange(name=name, market_type=market_type).fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            start=start,
            end=end,
            limit=limit,
        )

    backend = CCXTBackend(name=name, market_type=market_type)
    cursor = start
    remaining = limit
    rows: list[TimeBar] = []

    while True:
        request_limit = (
            min(remaining, _DEFAULT_PAGINATION_LIMIT)
            if remaining is not None
            else _DEFAULT_PAGINATION_LIMIT
        )
        page = backend.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            start=cursor,
            end=end,
            limit=request_limit,
        )
        if not page:
            break

        page_last_timestamp = int(page[-1][0])
        if page_last_timestamp < cursor:
            raise ValueError("provider returned a non-advancing OHLCV page")

        added = 0
        for raw_row in page:
            timestamp = int(raw_row[0])
            if timestamp < cursor:
                continue
            if end is not None and timestamp >= end:
                continue
            if rows and timestamp <= rows[-1].timestamp:
                continue

            rows.append(
                TimeBar(
                    timestamp=timestamp,
                    open=float(raw_row[1]),
                    high=float(raw_row[2]),
                    low=float(raw_row[3]),
                    close=float(raw_row[4]),
                    volume=float(raw_row[5]),
                )
            )
            added += 1

            if remaining is not None:
                remaining -= 1
                if remaining == 0:
                    return rows

        next_cursor = page_last_timestamp + 1
        if next_cursor <= cursor:
            raise ValueError("provider returned a non-advancing OHLCV page")
        if end is not None and next_cursor >= end:
            break
        if added == 0:
            break

        cursor = next_cursor

    return rows


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
