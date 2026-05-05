# Runtime Order Model Design

## Status

- Date: `2026-04-20`
- Status: `draft`
- Role: `design / decision record`
- Authority: `non-governing`
- Scope:
  narrow design guidance for what the runtime `Order` object in
  `quantleet.trading` should own
- Read after:
  [`order-domain-runtime-design.md`](order-domain-runtime-design.md)

## Purpose

This document does **not** reopen the `OrderIntent != runtime Order` seam.

That boundary was fixed in the earlier draft and the first seam now exists in
code.

This document answers a narrower question:

> What kind of domain object should runtime `Order` be?

Concretely, this document fixes:

- what `Order` should own directly
- what must remain outside `Order`
- how far event-driven decoupling should go
- what lifecycle model is narrow enough for the current stage

## Current Code Truth

`quantleet` already has a minimal runtime `Order`.

- `OrderIntent` is created by strategy code
- the backtest runtime activates pending intents into working `Order` values
- `matching` takes an `Order` and computes fill possibility plus fill facts
- `Order.apply_fill()` protects order-local invariants directly
- `TradingState` consumes `FillEvent` and performs accounting

The current core loop therefore already has this boundary:

`OrderIntent -> runtime Order -> FillEvent -> TradingState`

Local evidence:

- [`../../src/quantleet/trading/domain/orders.py`](../../src/quantleet/trading/domain/orders.py)
- [`../../src/quantleet/trading/domain/matching.py`](../../src/quantleet/trading/domain/matching.py)
- [`../../src/quantleet/backtest/runtime.py`](../../src/quantleet/backtest/runtime.py)
- [`../../src/quantleet/trading/domain/state.py`](../../src/quantleet/trading/domain/state.py)

## Decision

### 1. `Order` should be a small rich aggregate

`Order` is not a passive DTO. It is a small aggregate that protects its own
consistency.

It is **not** a full OMS aggregate.

At this stage, `Order` should have:

- its own identity
- immutable submission terms
- filled and remaining quantity
- only legal order-local transitions

It should **not** yet absorb:

- venue ACK taxonomy
- cancel/replace workflow stacks
- request/ticket/event hierarchies
- portfolio or risk semantics

### 2. `Order` should own transition legality directly

This is the central decision in this document.

- the default recommendation is that `Order` exposes APIs that apply legal
  state transitions
- external components calculate what happened and pass that fact in
- `Order` validates whether the transition is legal and produces its next state

`apply_fill()` is already the beginning of that pattern.

If future behavior is added, it should follow the same rule:

- `trigger(...)`
- `cancel(...)`
- `reject(...)`
- `expire(...)`

The important point is not “make a huge mutable API immediately.”

The important point is:

> transition legality must stay inside the aggregate boundary

The current code can still use a small immutable-like transition pattern.

### 3. `matching` should calculate market facts only

`matching` is not the `Order` state machine.

Responsibilities that belong to `matching`:

- determine whether the order is executable on the current tick/book
- calculate fill facts such as price, quantity, and fee
- for future stop-family orders, determine whether trigger conditions are met

Responsibilities that do **not** belong to `matching`:

- mutating position or cash
- owning bar-aware activation rules
- mutating `Order` internals directly

In short:

`matching` is a **market-fact calculator**.

### 4. Runtime orchestration should stay outside `Order`

The following responsibilities belong to the runtime loop, not to `Order`:

- intent acceptance and activation timing
- next-bar activation
- same-bar tail evaluation
- event ordering
- working-order registry management

Those are runtime semantics, not order-local invariants.

So the split is:

- `Order` protects transition legality
- runtime orchestration decides when transitions are attempted and in what
  order

### 5. Accounting should remain downstream of `FillEvent`

`Order` is not an accounting aggregate.

Keep the following outside `Order`:

- cash increases and decreases
- average entry price
- realized and unrealized PnL
- trade grouping
- future position and portfolio state

`Order` owns execution-local truth.
Accounting truth stays downstream of fills.

The current `FillEvent -> TradingState` boundary remains valid.

### 6. Keep the hot path synchronous and deterministic

Do not turn the core loop into a general message bus where every component
publishes events and every other component “eventually” figures out the right
state.

Recommended model:

1. the runtime loop receives a tick or event
2. `matching` calculates market facts
3. `Order` applies a transition synchronously
4. the runtime obtains facts such as `FillEvent`
5. downstream state reacts to those facts

In short:

- aggregate-internal transitions: synchronous
- cross-aggregate reactions: optional events

### 7. Avoid an internal event mesh, but treat inbound execution events as first-class inputs

This document does **not** recommend “never use events.”

It recommends:

- use events where they are helpful
- do not make an internal message bus the primary control plane for order
  acceptance, matching, and fill application

Good event examples:

- `OrderFilled`
- `OrderCancelled`
- `OrderTriggered`
- `OrderRejected`

Bad default:

- “broadcast the event and let every component fix its own state whenever it
  notices”

That pattern conflicts with the deterministic backtest semantics `quantleet`
currently wants.

At the same time, paper/live paths will eventually treat these as authoritative
inputs:

- venue accept / reject
- venue cancel confirmation
- partial / full fill report
- stop trigger notification

So the correct interpretation is:

> keep internal orchestration explicit, but accept external execution events as
> first-class kernel inputs

Those are not the same thing.

## Recommended Minimal Lifecycle For Now

Do not freeze a large status enum yet.

For the current stage, the minimal truths that matter are:

- whether the order is still working/open
- filled quantity
- remaining quantity
- whether the order is terminal

That makes the current model centered on:

- `filled_quantity`
- `remaining_quantity`
- `is_open`

appropriate for now.

But the long-lived shared-kernel direction should explicitly reserve pressure
for the following concepts.

### Stop-family pressure

- `stop_price`
- dormant versus triggered distinction
- `triggered_at` or an equivalent trigger fact

### Paper/live pressure

- submit outcome
- terminal reasons such as accept / reject / cancel / expire
- handling authoritative inbound execution updates

What should **not** be introduced yet:

- `submitted`
- `accepted`
- `pending_update`
- `pending_cancel`

as a venue-style taxonomy for the current slice.

In short:

- reserve the concepts
- defer the taxonomy

## Alternatives Considered

### Alternative A: keep `Order` as a thin record

Benefits:

- the current implementation stays simple
- orchestration remains concentrated in one place and is easy to read

Rejected because:

- stop-family or cancel flows would scatter illegal-transition protection
- it would waste the benefits of the `OrderIntent != Order` seam

### Alternative B: expand to a full OMS now

Benefits:

- it looks more future-proof for paper/live expansion

Rejected because:

- it runs far ahead of current product pressure
- it encourages symbolic mutation workflows that the current spec does not
  need
- it would likely create status names before the real semantics exist

## Boundary Implications

This design implies the following boundaries:

1. `Order` protects order-local legality
2. `matching` remains a calculation object
3. runtime orchestration keeps ownership of ordering and activation
4. inbound execution events become kernel inputs in future paper/live paths
5. accounting promotion remains a separate future slice

## Open Questions

This document does **not** yet close:

- when to introduce an explicit status enum
- when partial fill should become a user-visible lifecycle concept
- whether stop-market / stop-limit should model `triggered` as a field or a
  status
- where submit/ack semantics should live in paper/live

Those belong to a later design slice.

See also:

- [`order-lifecycle-and-sizing-design.md`](order-lifecycle-and-sizing-design.md)

## One-Line Summary

The best current fit for `quantleet` is a runtime `Order` that is **small but
behavioral**: rich enough to enforce order-local invariants, but not so large
that it absorbs matching, runtime orchestration, or accounting.
