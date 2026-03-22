# Binance Minimal Hardening Plan

**Goal:** Clean up the minimal Binance OHLCV feature so the tiny scope stays explicit and structurally sound.

**Scope:**
- Keep the feature tiny.
- Fix only the structural issues called out in review.
- Do not add pagination, caching, retries, or multi-exchange abstraction.

**Problems to fix:**
- Remove lazy local `ccxt` import and `Any` return typing.
- Remove the hidden USD-M symbol rewrite from the shared fetch path.
- Decouple tests from `ccxt.binance` and `ccxt.binanceusdm` constructor names.
- Make the notebook prove simple expected behavior instead of acting like a vague smoke demo.

**Intended shape after cleanup:**
- `ccxt` imported at module scope.
- Small exchange protocol for the fetch seam.
- `_make_exchange()` returns the protocol, not `Any`.
- Public symbol contract is explicit:
  - Spot: `BTC/USDT`
  - USD-M: caller must pass canonical CCXT symbol such as `BTC/USDT:USDT`
- Tests monkeypatch `_make_exchange()` instead of `ccxt` constructors.
- Notebook uses canonical symbols and contains lightweight assertions for non-empty, ordered rows.
