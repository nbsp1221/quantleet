# Order-Domain Architecture Comparison

## Status

- Date: `2026-04-19`
- Status: `current`
- Authority: `advisory`
- Canonical: `no`
- Purpose:
  Preserve the support and rebuttal evidence behind the current Order-domain
  direction so later spec or implementation work does not have to reconstruct
  the argument from chat history.

## Why This Note Exists

The session started from a small user-facing complaint about strategy-order UX,
but the investigation exposed a deeper runtime question:

> Should `quantcraft` keep stretching `OrderIntent`, or should it introduce a
> real runtime `Order` model?

This note is the evidence artifact for that question.
It is not a governing design doc or an execution plan.

## Current `quantcraft` Starting Point

Current repository truth, before later Order-domain work:

- `Strategy` emits `OrderIntent`
- the current public order surface supports only `market` and `limit`
- there is no runtime `Order` object today
- active and pending order state currently live partly on `Strategy` and are
  orchestrated by the backtest runtime
- matching today is effectively:
  `OrderIntent + TickEvent + CostConfig -> FillEvent | None`
- `TradingState` tracks one spot-like long-only state, not a real
  portfolio/account model

Relevant local evidence:

- [`../src/quantcraft/trading/domain/intents.py`](../../src/quantcraft/trading/domain/intents.py)
- [`../src/quantcraft/trading/domain/matching.py`](../../src/quantcraft/trading/domain/matching.py)
- [`../src/quantcraft/trading/domain/state.py`](../../src/quantcraft/trading/domain/state.py)
- [`../src/quantcraft/backtest/strategy_runtime.py`](../../src/quantcraft/backtest/strategy_runtime.py)
- [`../src/quantcraft/research/strategy.py`](../../src/quantcraft/research/strategy.py)
- [`../docs/product-specs/backtest-mvp.md`](../product-specs/backtest-mvp.md)

## Candidate Directions Considered

### Option A: Keep Expanding `OrderIntent`

Treat `OrderIntent` as both strategy request and runtime order truth.
Add fields for trigger state, stop pricing, and later runtime metadata.

### Option B: Split `OrderIntent` And Runtime `Order`

Keep `OrderIntent` as strategy-facing intent and introduce a real runtime
`Order` aggregate owned by `trading`.

### Option C: Jump Straight To A Full OMS

Design a large request/ticket/order/event/status stack now, including venue-like
state taxonomies and contingent-order machinery.

## Evidence Supporting A Runtime `Order`

### 1. Stop-Family Orders Create A Real Runtime Boundary

`market` and `limit` can be modeled today as “intent meets executable tick.”
`stop-market` and `stop-limit` cannot.

They require at least:

- a dormant working order
- a trigger condition
- a transition from not-yet-executable to executable
- causality around trigger, fill, and completion

That pressure does not naturally belong inside `OrderIntent`.

### 2. Mature Trading Engines Repeatedly Split Request From Managed Order

**NautilusTrader**

- rich order lifecycle
- stop and stop-limit are first-class runtime orders
- risk and execution operate on managed orders

**QuantConnect LEAN**

- explicit request, ticket, and runtime-order layers
- stop-order behavior depends on runtime state and order events

**backtrader**

- user-facing `buy()` / `sell()` stay simple
- runtime still has concrete order objects and lifecycle states

Cross-library implication:

> strategy-facing ergonomics can be light, but runtime order truth still needs
> its own identity and lifecycle.

Sources:

- https://nautilustrader.io/docs/latest/concepts/orders/
- https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-management/order-tickets
- https://www.backtrader.com/docu/order/

## Evidence Against Overdesign

### 1. YAGNI Still Applies

Martin Fowler’s YAGNI and evolutionary-design arguments remain valid here.
Fear of future rewrite is not itself proof that the repository should freeze a
full OMS now.

That warning applies strongly to:

- venue-heavy status taxonomies
- cancel / modify / replace workflows
- TIF, post-only, reduce-only
- bracket / OCO trees
- broker-specific acknowledgement schemas

Sources:

- https://martinfowler.com/bliki/Yagni.html
- https://martinfowler.com/articles/designDead.html

### 2. Some Useful Systems Stay Smaller Longer

- `backtesting.py` gets real value without a rich mutable order engine
- `vectorbt` proves that broad research value does not require a runtime order
  aggregate at all

Implication:

> the evidence supports a runtime `Order`, but not a maximal OMS.

Sources:

- https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html
- https://vectorbt.dev/api/portfolio/base/

## Final Synthesis

The evidence rejects both extremes.

Rejected:

- **Option A**: keep stretching `OrderIntent`
- **Option C**: design a full OMS now

Recommended:

- **Option B**: introduce a runtime `Order`, but keep the first seam minimal

That recommendation leads to these working conclusions:

- `OrderIntent` should remain strategy-facing intent
- `Order` should become runtime-managed truth
- `Order` should own its own invariant-preserving state transitions
- matching logic should stay separate from the `Order` aggregate and compute
  market facts such as executability, trigger satisfaction, and fill outcomes
- `FillEvent` should remain the accounting handoff to later
  `Position` / `Portfolio` work
- the kernel should stay ordered and deterministic, not devolve into an
  unconstrained async event mesh

## What This Research Does Not Decide

This note does **not** settle:

- the final runtime `Order` field set
- the exact state enum or partial-fill schema
- portfolio, ledger, allocator, or risk-engine design
- paper/live runtime design
- public strategy API changes

Those belong in design docs or later implementation plans.

## Recommended Document Roles

For future Order-domain work, the clean split is:

- `docs/research/...`
  - evidence and cross-library comparison
- `docs/design-docs/order-domain-runtime-design.md`
  - durable draft boundary and architecture direction
- `docs/plans/...`
  - concrete implementation planning for the next code slice

## One-Line Summary

The best-supported local optimum for `quantcraft` is not “just use
`OrderIntent` longer” and not “build a full OMS now.”
It is a minimal runtime `Order` layer with clear boundaries, supported by
separate research and implementation artifacts.
