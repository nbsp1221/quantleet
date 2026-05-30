from __future__ import annotations


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
