# Minimal Binance OHLCV Design

**Goal:** Add the smallest useful Binance OHLCV fetch function for spot and USD-M futures.

**Decision:** Use one public function, `fetch_binance_ohlcv(...)`, backed by a tiny enum for market selection and a tiny dataclass for normalized OHLCV rows.

**Scope:**
- Support Binance spot and Binance USD-M futures only.
- Support one-shot fetches only.
- No caching.
- No pagination loop.
- No retry layer.

**API shape:**
- `BinanceMarket(StrEnum)` with `SPOT` and `USDM`
- `OHLCVBar` dataclass with timestamp/open/high/low/close/volume
- `fetch_binance_ohlcv(...) -> list[OHLCVBar]`

**Implementation notes:**
- Use `ccxt.binance()` for spot.
- Use `ccxt.binanceusdm()` for USD-M futures.
- Pass `since=start` and `limit=limit`.
- If `end` is provided, pass it through `params={"end": end}`.
- Normalize the raw CCXT rows into `OHLCVBar`.
