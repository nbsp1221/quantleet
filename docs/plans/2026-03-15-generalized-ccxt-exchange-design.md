# Generalized CCXT Exchange Design

## Goal

Keep the approved public API:

```python
exchange = Exchange(name="binance", market_type="spot")
exchange.fetch_ohlcv(...)
```

But remove the Binance-only limitation so that CCXT-supported overseas exchanges can be used without source changes.

Examples:

```python
Exchange(name="bybit", market_type="spot")
Exchange(name="bitget", market_type="spot")
Exchange(name="mexc", market_type="spot")
```

## Public API

The public API stays unchanged:

- `Exchange`
- `MarketType`
- `TimeBar`

Only the internal implementation changes.

## Architecture

### Exchange

`Exchange` remains the public facade.

Responsibilities:

- store `name` and `market_type`
- validate the public symbol contract
- delegate data fetching to the internal backend
- normalize returned rows into `TimeBar`

### CCXTBackend

`CCXTBackend` is the default implementation for CCXT-supported exchanges.

Responsibilities:

- construct the correct CCXT exchange instance from `name` and `market_type`
- translate public arguments:
  - `start` -> `since`
  - `end` -> `params["end"]`
- return raw CCXT OHLCV rows

This backend exists so the public facade does not need to know CCXT constructor details.

## Why this is simpler than the current code

The current code contains internal protocol shims whose intent is not obvious.

This design removes:

- `_ExchangeProvider`
- `_CCXTOHLCVExchange`

and keeps:

- one public facade
- one concrete default backend

That makes the code easier to read while still leaving a clean place for future direct backends.

## Exchange Resolution

Resolution rules:

- `spot`:
  - use `getattr(ccxt, name)` and instantiate it
- `usdm`:
  - first try `getattr(ccxt, f"{name}usdm")`
  - if that does not exist, fall back to `getattr(ccxt, name)` with CCXT options that request swap/perpetual market type

This keeps the common path generic and avoids hardcoding Binance only.

## Symbol Contract

The library does not rewrite symbols automatically.

Current contract:

- spot symbols follow normal CCXT symbols
  - example: `BTC/USDT`
- usdm symbols must already be canonical CCXT USD-M symbols
  - example: `BTC/USDT:USDT`

The intent is to keep the API explicit and avoid hidden exchange-specific normalization logic in this batch.

## Testing

Tests should prove:

- Binance spot still works
- Binance USD-M still works
- Bybit/Bitget/MEXC spot can be constructed through the same public API
- generic exchange resolution works without Binance-specific code
- unsupported exchange names still fail clearly

Live smoke validation should also fetch a small number of OHLCV rows from:

- Binance spot
- Binance usdm
- Bybit spot
- Bitget spot
- MEXC spot

## Non-goals

This batch does not add:

- direct backends
- retries
- cache
- order/balance methods
- symbol normalization

The goal is only to remove Binance-only hardcoding while keeping the architecture small and understandable.
