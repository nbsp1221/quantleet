# Exchange Object OHLCV Implementation Plan

## Scope

Implement the approved exchange-object design without expanding product scope.

Do not add:

- cache
- retry
- pagination helpers
- non-Binance exchanges
- order or account methods

## Steps

1. Introduce shared public models

- add `MarketType`
- add `TimeBar`
- place them where the public facade can use them cleanly

2. Add the `Exchange` facade

- accept `name` and `market_type`
- reject unsupported combinations clearly
- keep only Binance support for this batch

3. Add internal provider seam

- introduce a small private provider shape for `fetch_ohlcv(...)`
- implement initial `CCXTExchangeProvider`
- keep provider private to avoid exposing unnecessary abstraction

4. Migrate Binance logic

- move current Binance `ccxt` fetch logic behind the provider
- preserve current symbol contract:
  - spot: `BTC/USDT`
  - usdm: `BTC/USDT:USDT`
- preserve `end -> params["end"]` forwarding

5. Replace old public API

- remove `fetch_binance_ohlcv`
- remove `BinanceMarket`
- remove `OHLCVBar`
- export `Exchange`, `MarketType`, `TimeBar`

6. Update tests

- replace function-based tests with facade-based tests
- keep tests local and behavior-focused
- verify delegation, symbol contract, and `TimeBar` normalization

7. Update notebook

- rewrite the Binance validation notebook to use `Exchange`
- keep assertions for non-empty results and ascending timestamps

8. Verification

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`
- execute the notebook validation flow

## Risks

### Over-design risk

Keep provider internal and minimal. Do not turn this into a multi-exchange framework in this batch.

### Public churn risk

This batch intentionally changes the public API shape. That is acceptable because the current project is still pre-commit and pre-release.

### Scope creep risk

Do not add future methods such as order entry or balance fetch now. The facade shape is chosen to support those later, not to implement them today.
