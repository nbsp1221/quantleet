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

## Why This Slice Exists

The immediate UX complaint in the session was small:

- current `Strategy.buy()` / `sell()` feel awkward for the single-symbol MVP

But the investigation showed that the real architectural pressure point is
below the strategy surface:

- today `OrderIntent` is the only first-class order-shaped object
- active and pending order state currently live on `Strategy` and are
  orchestrated by the backtest runtime
- there is no dedicated runtime `Order` model, and `OrderEvent` remains a
  documented but deferred part of the broader event direction rather than a
  current public contract
- `stop-market` and `stop-limit` are explicitly out of scope today, but they
  are likely future requirements in the long-lived framework direction
  discussed in this session

This note therefore answers a narrower question than “design the whole trading
kernel”:

> What is the smallest durable Order-domain design that should be fixed now so
> future stop orders and runtime work do not require an architectural rewrite?

## Current Repository Truth

Verified current truth:

- `OrderIntent` is the current strategy output contract with:
  - `symbol`
  - `side`
  - `quantity`
  - `order_type`
  - `limit_price?`
  - `tag?`
- `OrderType` currently allows only `market` and `limit`
- there is no current runtime `Order` object
- `OrderEvent` is currently deferred rather than implemented in the public
  slice
- there is a minimal `OrderIntent` activation lifecycle today, but it lives
  across `Strategy` and backtest runtime orchestration rather than in a
  dedicated runtime `Order`
- active and pending order state currently live on `Strategy`, with
  `_StrategyDriver` and backtest runtime orchestrating activation and
  consumption, not in `TradingState`
- `TradingState` only tracks spot-like long-only cash, position, PnL, and
  equity state
- matching is a single-step function from
  `OrderIntent + TickEvent + CostConfig` to `FillEvent | None`
- current backtest semantics are deterministic and conservative, but stop
  orders, modify/cancel flows, and user-visible partial fills remain deferred

Repository evidence:

- [intents.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/trading/domain/intents.py:1)
- [strategy.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/research/strategy.py:41)
- [strategy_runtime.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/backtest/strategy_runtime.py:11)
- [state.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/trading/domain/state.py:1)
- [matching.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/trading/domain/matching.py:1)
- [backtest-mvp.md](/home/retn0/repositories/nbsp1221/quantcraft/docs/product-specs/backtest-mvp.md:74)
- [backtest-execution-semantics.md](/home/retn0/repositories/nbsp1221/quantcraft/docs/design-docs/backtest-execution-semantics.md:31)

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

> Option B is the best fit for `quantcraft` now.

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

- [ARCHITECTURE.md](/home/retn0/repositories/nbsp1221/quantcraft/ARCHITECTURE.md:79)
- [quantcraft-architecture.md](/home/retn0/repositories/nbsp1221/quantcraft/docs/design-docs/quantcraft-architecture.md:113)
- [quantcraft-architecture.md](/home/retn0/repositories/nbsp1221/quantcraft/docs/design-docs/quantcraft-architecture.md:132)
- [quantcraft-architecture.md](/home/retn0/repositories/nbsp1221/quantcraft/docs/design-docs/quantcraft-architecture.md:145)
- [strategy_runtime.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/backtest/strategy_runtime.py:59)

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

- [matching.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/trading/domain/matching.py:10)
- [strategy_runtime.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/backtest/strategy_runtime.py:59)
- [backtest-mvp.md](/home/retn0/repositories/nbsp1221/quantcraft/docs/product-specs/backtest-mvp.md:162)

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
- [Nautilus orders doc](/tmp/nautilus_trader/docs/concepts/orders.md:1)
- [Nautilus risk engine](/tmp/nautilus_trader/nautilus_trader/risk/engine.pyx:77)
- LEAN docs: https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-management/order-tickets
- [LEAN OrderTicket](/tmp/lean/Common/Orders/OrderTicket.cs:25)
- [LEAN transaction handler](/tmp/lean/Engine/TransactionHandlers/BrokerageTransactionHandler.cs:294)
- backtrader docs: https://www.backtrader.com/docu/order/
- [backtrader order.py](/tmp/backtrader/backtrader/order.py:222)

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

## Recommended Order-Domain Design

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

`Order` should become the runtime-managed object that exists after intent
acceptance and before terminal completion.

Its minimum responsibilities should be:

- identity inside the runtime
- order family semantics sufficient to distinguish:
  - immediately executable orders
  - price-constrained resting orders
  - stop-triggered orders
- side, symbol, requested quantity
- price fields relevant to the family when applicable
- runtime-owned executability and trigger state
- runtime-owned completion facts, with exact outcome taxonomy deferred

This is the first place where richer domain modeling is warranted:

> `OrderIntent` should say what the strategy wants.
> `Order` should say what the runtime is actually managing.

### 3. Let `Order` Own Order-Local State Validity

The runtime `Order` should be an aggregate-like domain object, not a passive
record.

That means the `Order` object should own:

- legality of trigger transitions
- legality of fill application
- open versus terminal completion state
- remaining-quantity and completion facts that are intrinsic to the order

Exact runtime collaboration details belong in the implementation plan rather
than this draft design note.

### 4. Model Triggering As Runtime Order Behavior, Not Intent Mutation

Stop-triggered orders require a runtime transition.

The Order-domain spec should therefore reserve explicit support for:

- order is accepted locally
- order is not yet executable because it is waiting on a stop trigger
- order becomes triggered
- triggered order proceeds according to its post-trigger family semantics

This does **not** require a large venue-like status enum in the first slice.
It does require that trigger and executability state belong to runtime
`Order`, not to `OrderIntent`.

This remains a future boundary consideration, not a requirement that the first
runtime `Order` implementation ship trigger-aware behavior immediately.

### 5. Keep The First Lifecycle Model Minimal

The first canonical lifecycle should be defined behaviorally, not as a huge
status table.

The runtime order must support these transitions:

1. `intent accepted -> order created`
2. `order created -> order working`
3. `stop-family order working -> order triggered`
4. `order working/triggered -> order completed or remains open`

This note intentionally does **not** standardize all future intermediate states
such as:

- `pending_update`
- `pending_cancel`
- venue acknowledgement taxonomies
- local emulation versus venue-open distinctions

Those are valid future concerns, but the current evidence does not justify
freezing them now.

### 6. Preserve The Existing Matching Boundary

This Order-domain design does not move fill semantics out of the approved
backtest boundary:

- `backtest` still owns approximation and synthetic path generation
- `trading` still owns executable-event matching and fill application

The new seam is about runtime order state, not about making `trading`
bar-aware.

Source:

- [backtest-execution-semantics.md](/home/retn0/repositories/nbsp1221/quantcraft/docs/design-docs/backtest-execution-semantics.md:19)

## Explicit Stop Line

The following should be designed **now**:

- `OrderIntent != Order`
- runtime `Order` identity
- a minimal distinction between:
  - immediately executable orders
  - resting price-constrained orders
- a minimal boundary between open and terminal order state

The following should be **deferred**:

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

- [2026-04-19-order-domain-runtime-implementation-plan.md](/home/retn0/repositories/nbsp1221/quantcraft/docs/plans/2026-04-19-order-domain-runtime-implementation-plan.md:1)

## One-Line Summary

`quantcraft` should not jump straight to a full OMS, but it also should not
keep stretching `OrderIntent` into a fake runtime order.
The right next architecture move is a minimal runtime `Order` owned by
`trading`, with just enough lifecycle for immediately executable and
stop-triggered orders.
