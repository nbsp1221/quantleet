# Backtest Execution Semantics

## Status

- Status: `approved`
- Scope: canonical backtest-only price-path construction, matching-boundary rules, and performance-safe path traversal
- Role: governing design document for backtest execution semantics

Related documents:

- [quantcraft-architecture.md](quantcraft-architecture.md)
- [../product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md)

## Why This Document Exists

`quantcraft` must keep one trading kernel across backtest, paper, and live
environments without letting OHLC-only backtests drift into optimistic
fill behavior.

The repository therefore needs an explicit answer to three questions:

1. who owns path generation
2. who owns fill matching
3. how backtest performance is protected without making path generation
   order-dependent

This document fixes those boundaries.

## Architectural Boundary

The boundary is strict:

- `trading` matches executable events and applies fills
- `trading` does not inspect bars to invent special fill cases
- `backtest` adapters convert bars into a canonical synthetic path
- paper and live runtimes should be able to reuse the same matching core with
  real venue events

In short:

- matching owns fills
- backtest adapters own approximation

## Canonical Price Path

Backtest price movement is modeled in two parts.

### 1. Gap Segment

The movement from `prev_close` to `next_open` is a distinct gap segment.

Rules:

- no fills occur at intermediate gap prices
- `open` is the first executable price of the new bar
- if a resting order is crossed by the gap, `open` is the first price the
  matching engine may see
- if a dormant stop trigger is crossed by the gap, `open` is also the first
  executable price and trigger point the matching engine may see

### 2. Intrabar Segment

Within a bar, the path is continuous along a fixed canonical route:

- bullish bar: `open -> low -> high -> close`
- bearish bar: `open -> high -> low -> close`

This rule is order-independent and deterministic.

The important implication is that the bar does not mean "four isolated ticks."
It means "a continuous path constrained by those four prices."

## Conservative Limit Contract

For OHLC-only backtesting, bar extremes do not justify optimistic price
improvement on resting limits.

The conservative contract is:

- a marketable limit fills immediately at the first executable price no worse
  than the limit
- a resting limit touched during continuous intrabar movement fills at the
  limit price itself
- a resting limit crossed by a gap fills at `open`, because `open` is the first
  executable price after the gap

Examples:

- buy limit `130`, best executable ask `121`
  - immediate fill at `121`
- sell limit `110`, bar path moves continuously from `100` up through `120`
  - conservative fill at `110`, not `120`
- buy limit `100`, next bar opens at `95`
  - fill at `95`, because the gap made `95` the first executable price

## Performance Contract

Backtest execution must not require materializing every tick-sized price step in
every bar.

The repository therefore distinguishes between:

- the canonical path definition
- the way that path is traversed

Allowed optimization:

- represent the canonical path as segments
- lazily materialize executable events only when evaluation is needed
- use active orders to skip ahead along the already-defined canonical path
  without changing that path

Forbidden optimization:

- generating a different path because of the current orders
- injecting special executable prices solely to make a fill happen
- using bar extremes as executable prices when the conservative touched-limit
  outcome is the limit price

This distinction matters:

- order-dependent path fabrication changes semantics
- order-aware traversal acceleration only changes runtime cost

## Outcome-Equivalent Traversal

Any future fast path must be outcome-equivalent to a full canonical traversal at
tick-size granularity.

That means:

- the same orders fill or remain unfilled
- fill timestamps remain the same at the chosen event resolution
- fill prices remain the same under the conservative contract

If an optimization changes any of those outcomes, it is a semantic change, not
just a performance improvement.

## Synthetic Execution Events

The backtest adapter may emit a reduced set of decisive executable events rather
than a full tick grid, but those events must preserve the same conservative
result as the canonical path.

Typical decisive events include:

- `open`
- canonical path turning points
- the first executable crossing of a resting limit
- the first executable crossing of a dormant stop trigger
- the first executable point after a gap

The decisive-event stream is a compression of the canonical path, not a new
price path.

## Implementation Consequence

The current repository should treat this document as the authority for follow-up
implementation work in the backtest execution path.

In particular, any implementation work should preserve all of the following:

- one shared matching kernel
- no bar-aware special cases in `trading`
- deterministic, order-independent canonical path construction
- conservative resting-limit handling
- same-point stop trigger/fill behavior when a decisive executable point both
  triggers a stop and serves as the first marketable point
- performance optimizations that do not alter outcomes
