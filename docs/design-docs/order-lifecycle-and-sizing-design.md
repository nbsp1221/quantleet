# Order Lifecycle And Sizing Design

## Status

- Date: `2026-04-20`
- Status: `draft`
- Role: `design / decision record`
- Authority: `non-governing`
- Scope:
  narrow follow-on design for:
  - runtime `Order` lifecycle / FSM depth
  - sizing intent design needed for the next order-model expansion
- Read after:
  - [`order-domain-runtime-design.md`](order-domain-runtime-design.md)
  - [`order-runtime-model-design.md`](order-runtime-model-design.md)

## Purpose

This document does **not** reopen the existing seam:

- `OrderIntent != runtime Order`

It answers the next two questions after that seam:

1. what lifecycle model should runtime `Order` use once stop-family orders are
   introduced
2. what sizing-intent direction should be preferred once percentage-based
   sizing is intentionally introduced

## Current Code Truth

Current runtime `Order` is still minimal:

- immutable submission terms
- `filled_quantity`
- derived `remaining_quantity`
- derived `is_open`
- `apply_fill()` as the only transition method

Current intent is still quantity-only:

- `symbol`
- `side`
- `quantity`
- `order_type`
- `limit_price?`
- `tag?`

Current shipped product scope includes:

- single symbol
- long-only
- `market`, `limit`, `stop_market`, and `stop_limit`
- no cancel/replace
- no public partial-fill workflow

Local evidence:

- [`../../src/quantcraft/trading/domain/orders.py`](../../src/quantcraft/trading/domain/orders.py)
- [`../../src/quantcraft/trading/domain/intents.py`](../../src/quantcraft/trading/domain/intents.py)
- [`../product-specs/backtest-mvp.md`](../product-specs/backtest-mvp.md)
- [`../product-specs/research-ergonomics.md`](../product-specs/research-ergonomics.md)

## Decision

## 1. Keep runtime `Order` quantity-based

Runtime `Order` should stay quantity-based.

It should **not** become a portfolio-target object.

That means:

- concrete executable units remain the runtime truth
- any percent-based sizing must resolve to quantity before or at order creation
- runtime `Order` does not directly own:
  - target portfolio weight
  - target portfolio value
  - portfolio rebalance semantics

## 2. Keep lifecycle guidance narrow: no full status taxonomy yet

The next lifecycle model should be richer than the current
`filled_quantity + is_open` shape, but this slice does **not** freeze a full
kernel enum or a venue-style status ladder.

What this slice does fix is smaller:

- `quantcraft` should **not** adopt a large live-style taxonomy next
- future stop-family support should require explicit trigger facts
- whatever lifecycle shape comes next must stay kernel-local rather than
  venue-shaped

## 3. Model stop triggering as a fact, not the main lifecycle axis

The key design choice is this:

> stop triggering is a fact recorded on the order, not the primary lifecycle
> ladder

Why:

- a stop-market order often triggers and fills immediately
- a stop-limit order triggers and then continues life as an ordinary working
  limit order
- treating `TRIGGERED` as the main lifecycle status tends to overfit live OMS
  models too early

So the preferred direction is:

- pre-trigger stop-family orders must be distinguishable from executable orders
- trigger time and optional trigger price should be representable as facts
- stop-market and stop-limit should share the same trigger concept, even if
  their post-trigger behavior differs

This document intentionally does **not** freeze the exact lifecycle matrix
needed to express that.

## 4. `Order` owns legal transitions, not runtime ordering

This document keeps the same boundary already fixed in the previous runtime
Order draft.

`Order` should continue to own legal transition application.

At the current level of design certainty, that clearly includes:

- legal `apply_fill(...)`

And it strongly suggests that future runtime-order behavior will eventually
need order-local methods for things like:

- `trigger(...)`
- `cancel(...)`
- `reject(...)`
- `expire(...)`

But this slice does **not** freeze the exact next method set as a contract.

Runtime orchestration should still own:

- when activation happens
- next-bar versus same-bar timing
- working-order registry
- event ordering

Matching should still own:

- market-fact calculation
- trigger satisfaction checks
- fill price / quantity / fee calculation

## 5. Do not overload `quantity` to mean percentages

The current `quantity: float` field should **not** become an overloaded
“sometimes units, sometimes percent” channel.

Do not copy the `backtesting.py` pattern where:

- `0 < size < 1` means fraction
- `size >= 1` means units

That is compact, but too ambiguous for a shared kernel that will later need
stop-family, paper, and live behavior.

## 6. Prefer a separate sizing layer, but do not freeze the next public contract yet

The evidence supports one clear rule:

> if `quantcraft` adds percentage-based sizing, it should not overload the
> existing `quantity` float to do it

The best current direction is:

- runtime `Order` stays quantity-based
- any future percentage semantics resolve to quantity outside runtime `Order`
- the first candidate percentage bases are:
  - entry/increase relative to available cash or buying power
  - reduce/exit relative to current position quantity

This slice does **not** freeze:

- the exact names of future sizing-intent variants
- the exact strategy-facing syntax
- the exact resolver behavior

It only fixes the direction:

- separate sizing semantics from raw quantity
- defer portfolio-target sizing to a later control layer

## 7. What to defer

Defer all of the following:

- full OMS venue-style status ladders:
  - `SUBMITTED`
  - `ACCEPTED`
  - `PENDING_CANCEL`
  - `PENDING_UPDATE`
- request / ticket / amend / replace stacks
- portfolio-target APIs such as:
  - `target_percent`
  - `target_value`
  - `SetHoldings`-style behavior
- quote/notional sizing as a general public contract
- bracket, OCO, trailing stop, post-only, reduce-only, TIF
- exact lifecycle enum values
- exact terminal-reason representation
- exact sizing-intent names and resolver rules

## 8. Open questions intentionally left for the next slice

This document still does **not** settle:

- the exact lifecycle representation
- the exact stop-trigger field layout
- the exact public strategy syntax for percentage sizing
- the exact sizing-resolver policy
- the exact backtest semantics for stop-limit gap-through cases
- whether public partial-fill behavior should become visible in the current
  backtest path

## One-Line Summary

The preferred next direction is:

- keep lifecycle guidance small and stop-trigger-aware
- keep runtime `Order` quantity-based
- and, if percentage sizing is added later, introduce it through a separate
  sizing layer rather than by overloading `quantity`
