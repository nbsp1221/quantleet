# Generalized CCXT Exchange Implementation Plan

## Scope

Generalize the current Exchange facade from Binance-only to CCXT-backed overseas exchanges without changing the public API shape.

## Steps

1. Simplify internal structure

- remove protocol-only internal shims
- replace them with a single concrete `CCXTBackend`

2. Generalize exchange construction

- spot: `getattr(ccxt, name)()`
- usdm:
  - prefer `<name>usdm` class when available
  - otherwise use the base exchange class with CCXT options requesting swap/perpetual markets

3. Keep symbol handling explicit

- keep the current USD-M canonical symbol check
- do not add hidden rewriting

4. Update tests

- rewrite tests around the generic backend resolution
- add coverage for:
  - Binance spot
  - Binance usdm
  - Bybit spot
  - Bitget spot
  - MEXC spot
  - unsupported exchange names
  - usdm fallback path when no `<name>usdm` class exists

5. Run local gates

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`

6. Run live smoke validation

- Binance spot
- Binance usdm
- Bybit spot
- Bitget spot
- MEXC spot

7. QA review

- ask a separate QA subagent for a strict review
- fix blocking findings until approval
