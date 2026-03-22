# Exchange Object OHLCV Design

## Goal

Replace the current Binance-specific function-first shape with a small exchange-object API that can grow without multiplying top-level functions.

Immediate scope is intentionally narrow:

- One public object: `Exchange`
- One public method: `fetch_ohlcv(...)`
- One supported exchange: `binance`
- Two supported market types: `spot`, `usdm`
- One returned model: `TimeBar`

Out of scope for this batch:

- cache
- retry
- pagination
- websocket
- order entry
- balance/account methods
- exchanges other than Binance

## Public API

```python
exchange = Exchange(name="binance", market_type="spot")
bars = exchange.fetch_ohlcv(
    symbol="BTC/USDT",
    timeframe="1h",
    start=...,
    end=...,
    limit=...,
)
```

Returned value:

```python
list[TimeBar]
```

## Naming

### Exchange

`Exchange` is the public facade object. This follows the same mental model as `ccxt`: users work with an exchange object and call flat methods on it.

### MarketType

`market_type` is fixed at object construction time because spot and futures have different underlying implementations and symbol contracts.

Initial values:

- `spot`
- `usdm`

### TimeBar

`TimeBar` replaces `OHLCVBar`.

Reasoning:

- more intuitive than a raw acronym-heavy model name
- matches how users think about candle/bar data
- leaves room for later models such as `DollarBar` or `VolumeBar`

Fields:

- `timestamp`
- `open`
- `high`
- `low`
- `close`
- `volume`

## Internal Structure

The public `Exchange` object owns a private provider.

High-level shape:

- `Exchange`
- provider protocol or concrete private seam for `fetch_ohlcv(...)`
- initial implementation: `CCXTExchangeProvider`

The user only sees `Exchange`. Provider selection happens internally.

For this batch:

- `Exchange(name="binance", market_type="spot")` -> `CCXTExchangeProvider`
- `Exchange(name="binance", market_type="usdm")` -> `CCXTExchangeProvider`

Later, if a market or exchange cannot be served well through `ccxt`, the public API stays the same and only the provider changes.

## Responsibility Boundaries

### Exchange facade

Responsible for:

- validating supported `name` / `market_type`
- choosing the provider
- exposing a stable public method surface

Not responsible for:

- caching
- retry policy
- pagination orchestration beyond what the provider already does

### Provider

Responsible for:

- low-level API calls
- translating public parameters to `ccxt`
- normalizing returned rows into `TimeBar`

## Symbol Contract

For this batch the symbol contract stays explicit:

- Binance spot uses normal CCXT spot symbols such as `BTC/USDT`
- Binance USD-M uses canonical CCXT USD-M symbols such as `BTC/USDT:USDT`

No hidden symbol rewriting should happen in the facade.

## Testing

Tests for this batch should stay small and local:

- facade constructs the right provider for Binance spot
- facade constructs the right provider for Binance USD-M
- `fetch_ohlcv(...)` delegates correctly
- USD-M symbol contract is enforced
- returned rows are normalized into `TimeBar`

Notebook validation should also be updated to use the new `Exchange` object.

## Success Criteria

This design is complete when:

- there is no public `fetch_binance_ohlcv(...)`
- the public entrypoint is `Exchange(...).fetch_ohlcv(...)`
- returned bars are modeled as `TimeBar`
- existing Binance spot / USD-M notebook validation still works through the new API
- pytest, ruff, mypy, and build are green
