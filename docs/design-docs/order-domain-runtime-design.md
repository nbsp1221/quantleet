# Order Domain Runtime Design

## Status

- Date: `2026-04-19`
- Status: `draft`
- Role: `design / decision record`
- Authority: `non-governing`
- Scope:
  Narrow design note for the first `trading`-kernel seam:
  `OrderIntent` versus runtime-managed `Order`
- Purpose:
  Fix the recommended Order-domain boundary before later work on stop orders,
  paper trading, or live trading pulls the repository into ad hoc runtime
  semantics.

## Maintenance Note

This draft originally captured the boundary decision before the first runtime
`Order` seam landed in code. The core seam recommendation still stands, but
parts of the historical “current repository truth” below have been superseded
by the implemented April 19 runtime-Order slice.

Use this note for the seam decision itself.

Use [`order-runtime-model-design.md`](order-runtime-model-design.md) for
the narrower follow-on question of what the runtime `Order` aggregate should
own now that a minimal `Order` object exists in code.

## Why This Slice Exists

The immediate UX complaint in the session was small:

- current `Strategy.buy()` / `sell()` feel awkward for the single-symbol MVP

When this investigation originally started, the real architectural pressure
point was below the strategy surface:

- `OrderIntent` was still the only first-class order-shaped object
- active and pending order state lived on `Strategy` and in backtest
  orchestration
- there was no dedicated runtime `Order` model yet
- `OrderEvent` remained a documented but deferred future direction
- `stop-market` and `stop-limit` were already likely future pressure on the
  seam

This note therefore answers a narrower question than “design the whole trading
kernel”:

> What is the smallest durable Order-domain design that should be fixed now so
> future stop orders and runtime work do not require an architectural rewrite?

## Current Repository Truth

Verified current truth as of `2026-04-20`:

- `OrderIntent` is the current strategy output contract with:
  - `symbol`
  - `side`
  - `quantity`
  - `order_type`
  - `limit_price?`
  - `tag?`
- `OrderType` currently allows only `market` and `limit`
- there is now a minimal runtime `Order` object in `trading`
- `OrderEvent` is currently deferred rather than implemented in the public
  slice
- strategy still emits `OrderIntent`, but backtest runtime now activates
  pending intents into runtime `Order` values owned by the working-order path
- pending order state still originates in `Strategy`, while active runtime
  order ownership now lives in `_StrategyDriver` / backtest orchestration, not
  in `TradingState`
- `TradingState` only tracks spot-like long-only cash, position, PnL, and
  equity state
- matching is now a single-step function from
  `Order + TickEvent + CostConfig` to `FillEvent | None`
- current backtest semantics are deterministic and conservative, but stop
  orders, modify/cancel flows, and user-visible partial fills remain deferred

Repository evidence:

- [intents.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/trading/domain/intents.py:1)
- [orders.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/trading/domain/orders.py:1)
- [strategy.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/research/strategy.py:41)
- [strategy_runtime.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/backtest/strategy_runtime.py:11)
- [state.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/trading/domain/state.py:1)
- [matching.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/trading/domain/matching.py:1)
- [backtest-mvp.md](/home/retn0/repositories/nbsp1221/quantleet/docs/product-specs/backtest-mvp.md:74)
- [backtest-execution-semantics.md](/home/retn0/repositories/nbsp1221/quantleet/docs/design-docs/backtest-execution-semantics.md:31)

## Decision Question

Three candidate directions were considered.

### Option A: Keep Expanding `OrderIntent`

Treat `OrderIntent` as both strategy intent and the runtime order object.
Extend it with `stop_price`, trigger flags, lifecycle fields, and later venue
status or cancel/update semantics.

### Option B: Split `OrderIntent` And Runtime `Order`

Keep `OrderIntent` as the strategy-facing request shape.
Introduce a separate runtime-managed `Order` owned by `trading`.
Design only the minimum lifecycle needed for immediately executable orders and
stop-triggered orders, with current stop-family discussion treated only as
future pressure on the seam rather than as a shipped contract.

Defer broader OMS concerns.

### Option C: Design A Full OMS Now

Introduce a large model now:

- request / intent / ticket / order / order event / cancel request / update
  request
- rich venue-like status taxonomy
- contingent orders, TIF, post-only, reduce-only, bracket/OCO foundations

## Initial Hypothesis

The working hypothesis was:

> Option B is the best fit for `quantleet` now.

That means:

- `OrderIntent` and runtime `Order` should be separated
- but the initial Order-domain spec should stop well short of a full OMS model

## Evidence Supporting The Hypothesis

### 1. The Repo Architecture Points Toward A Separate Runtime Order

The repository’s approved architecture already distinguishes:

- `research` as strategy authoring
- `backtest` as historical runtime orchestration
- `trading` as the shared trading kernel

The current implementation does **not** fully realize that split for order
state today. Order-like runtime state still lives partly in `research` and
`backtest`.

But the approved architecture still supports the recommendation that managed
runtime order state should eventually belong to `trading`, not remain spread
across strategy/runtime orchestration.

Sources:

- [ARCHITECTURE.md](/home/retn0/repositories/nbsp1221/quantleet/ARCHITECTURE.md:79)
- [quantleet-architecture.md](/home/retn0/repositories/nbsp1221/quantleet/docs/design-docs/quantleet-architecture.md:113)
- [quantleet-architecture.md](/home/retn0/repositories/nbsp1221/quantleet/docs/design-docs/quantleet-architecture.md:132)
- [quantleet-architecture.md](/home/retn0/repositories/nbsp1221/quantleet/docs/design-docs/quantleet-architecture.md:145)
- [strategy_runtime.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/backtest/strategy_runtime.py:59)

### 2. The Current MVP Cannot Naturally Absorb Stop Orders

Today’s flow is effectively:

`OrderIntent -> executable tick match -> FillEvent`

That is enough for current `market` and `limit`.
It is not enough for dormant conditional orders which need:

- a trigger condition
- a transition from not-yet-executable to executable
- explicit causality around gap trigger or same-bar tail evaluation

This is the first strong sign that runtime `Order` needs to exist apart from
intent.

Sources:

- [matching.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/trading/domain/matching.py:10)
- [strategy_runtime.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/backtest/strategy_runtime.py:59)
- [backtest-mvp.md](/home/retn0/repositories/nbsp1221/quantleet/docs/product-specs/backtest-mvp.md:162)

### 3. Mature Engines Repeatedly Separate Request/Intent From Managed Order

NautilusTrader:

- rich order lifecycle
- stop and stop-limit are first-class order types
- risk and execution operate on managed orders, not bare strategy intent

LEAN:

- `OrderRequest`, `OrderTicket`, and runtime `Order` are distinct
- stop-market and stop-limit depend on runtime state and order events

backtrader:

- `buy()` / `sell()` stay simple
- runtime order object still carries lifecycle and stop-family semantics

These are different frameworks with different UX goals, but they converge on
the same core point:

> strategy authoring may be light, but the runtime order concept still needs
> its own identity and lifecycle.

Sources:

- Nautilus docs: https://nautilustrader.io/docs/latest/concepts/orders/
- LEAN docs: https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-management/order-tickets
- backtrader docs: https://www.backtrader.com/docu/order/

## Evidence Against The Hypothesis

### 1. YAGNI And Evolutionary Design Warn Against Modeling The Whole Future

The strongest rebuttal is not “keep `OrderIntent` forever.”
It is:

> do not let fear of future rewrite justify speculative design now.

Martin Fowler’s writing on YAGNI and evolutionary design is directly relevant:

- presumptive features increase cost of carry
- future abstractions are often wrong before real constraints arrive

That warning applies strongly to:

- venue-heavy status taxonomies
- update / cancel / replace workflows
- contingent order trees
- TIF / post-only / reduce-only
- full broker-ticket abstractions

Sources:

- https://martinfowler.com/bliki/Yagni.html
- https://martinfowler.com/articles/designDead.html

### 2. DDD Does Not Require Rich Aggregates Everywhere

DDD guidance only supports rich domain modeling when there are real invariants
and behavioral complexity to protect.
If the current repository still has a very small backtest-only order path, a
maximal `Order` aggregate would be premature.

Sources:

- https://learn.microsoft.com/en-us/archive/msdn-magazine/2013/august/data-points-coding-for-domain-driven-design-tips-for-data-focused-devs
- https://www.dddcommunity.org/wp-content/uploads/files/pdf_articles/Vernon_2011_3.pdf

### 3. Some Successful Libraries Stay Small Longer

Evidence from smaller systems matters too:

- `backtesting.py` keeps a relatively small order/trade model and uses
  cancel-and-replace rather than deep amendment machinery
- `vectorbt` proves broad research value without a rich mutable runtime order
  lifecycle
- backtrader itself notes that some states such as partial fills are broker or
  context dependent

That means “full OMS now” is not supported by the evidence.

Sources:

- https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html
- https://vectorbt.dev/api/portfolio/base/
- https://www.backtrader.com/docu/order/

## Comparison And Final Conclusion

The evidence does **not** support Option A.

Keeping `OrderIntent` as both intent and runtime truth would force future stop
semantics, trigger state, and runtime identity into the wrong object.
That would repeat the exact boundary confusion already visible in the current
MVP.

The evidence also does **not** support Option C.

A full OMS-style taxonomy now would overfit to live-trading concerns that the
repository has not implemented yet and that the product slice does not need
today.

Therefore the recommended answer remains Option B:

> Separate `OrderIntent` from runtime `Order`, but define only the minimum
> durable runtime seam required for immediately executable orders and resting
> price-constrained orders, while keeping future stop-family support as a
> pressure on the seam rather than a first-slice contract.

## Recommended Seam Direction

### 1. Keep `OrderIntent` As Strategy Output

`OrderIntent` remains the strategy-facing “please create this order” shape.
It is not the mutable runtime object.

Future-facing requirements for the intent layer:

- it must remain symbol-bearing
- it must express the order family the strategy wants
- it must stay clearly separate from the mutable runtime order object

This note does **not** change the current shipped `OrderIntent` schema.
It only says the future Order slice should not treat that schema as the final
runtime model.

### 2. Introduce A Runtime `Order` Owned By `trading`

The seam recommendation is simply:

- strategy output remains `OrderIntent`
- runtime-managed truth becomes `Order`
- future stop-family or richer runtime work must extend `Order`, not mutate
  `OrderIntent` into a fake runtime object

This seam says **what must be separate**, not yet **how much behavior the new
`Order` aggregate should own**.
That narrower ownership question now lives in
[`order-runtime-model-design.md`](order-runtime-model-design.md).

### 3. Preserve The Existing Matching Boundary

This Order-domain design does not move fill semantics out of the approved
backtest boundary:

- `backtest` still owns approximation and synthetic path generation
- `trading` still owns executable-event matching and fill application

The new seam is about runtime order state, not about making `trading`
bar-aware.

Source:

- [backtest-execution-semantics.md](/home/retn0/repositories/nbsp1221/quantleet/docs/design-docs/backtest-execution-semantics.md:19)

## Explicit Stop Line

The following should be designed **now**:

- `OrderIntent != Order`
- runtime `Order` identity
- a minimal distinction between:
  - immediately executable orders
  - resting price-constrained orders
- a minimal boundary between runtime-managed order truth and downstream fill
  accounting

The following should be **deferred**:

- exact runtime `Order` ownership and lifecycle depth
- trigger-aware runtime behavior for stop-family orders
- full OMS request/ticket hierarchy
- full venue status taxonomy
- modify / cancel / replace workflows
- post-only / reduce-only / TIF
- bracket / OCO / parent-child contingencies
- exact partial-fill accounting fields
- exact client-order-key or broker-id schema
- account allocator / portfolio / ledger design
- broker-specific error and acknowledgement schemas

Implementation sequencing and exact file-level ownership belong in the
implementation plan, not in this draft design note.

See:

- [2026-04-19-order-domain-runtime-implementation-plan.md](/home/retn0/repositories/nbsp1221/quantleet/docs/plans/2026-04-19-order-domain-runtime-implementation-plan.md:1)

## One-Line Summary

`quantleet` should not jump straight to a full OMS, but it also should not
keep stretching `OrderIntent` into a fake runtime order.
This seam note’s core recommendation led to the now-implemented minimal
runtime `Order` boundary, while deeper object-responsibility questions are
handled in [`order-runtime-model-design.md`](order-runtime-model-design.md).
