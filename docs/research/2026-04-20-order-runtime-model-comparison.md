# Order Runtime Model Comparison

## Status

- Date: `2026-04-20`
- Status: `current`
- Authority: `advisory`
- Canonical: `no`
- Purpose:
  summarize support and rebuttal evidence for runtime `Order` responsibility,
  state-transition ownership, and event-collaboration policy

## Why This Document Exists

The earlier slice already fixed the `OrderIntent != runtime Order` seam.

What remained open was narrower:

- how much responsibility should runtime `Order` own
- should state transitions belong directly to `Order`, or to an external
  service
- how far should event-driven decoupling go

This document is a research note that gathers support and rebuttal evidence for
those questions. It is not a governing document.

## Current `quantleet` Truth

The current codebase already contains a small runtime `Order`.

- `OrderIntent` is the request object emitted by strategy code
- the `Order` type and its invariants live in `trading`
- working-order registry and activation timing are currently owned by the
  backtest runtime
- `Order.apply_fill()` protects order-local invariants directly
- `matching` calculates market facts and returns `FillEvent | None`
- the backtest runtime evaluates working orders in an ordered loop

Local evidence:

- [`../../src/quantleet/trading/domain/orders.py`](../../src/quantleet/trading/domain/orders.py)
- [`../../src/quantleet/trading/domain/matching.py`](../../src/quantleet/trading/domain/matching.py)
- [`../../src/quantleet/backtest/runtime.py`](../../src/quantleet/backtest/runtime.py)
- [`../../src/quantleet/backtest/strategy_runtime.py`](../../src/quantleet/backtest/strategy_runtime.py)

The question is therefore no longer:

> Should runtime `Order` exist at all?

It is now:

> How rich should the already-existing runtime `Order` become?

## Comparison Targets And Observation Points

This comparison focused on four questions:

1. which fields and states repeatedly appear across libraries
2. who owns order state transitions
3. how far events are used as the control plane
4. what `quantleet` should copy now versus defer

Comparison targets:

- NautilusTrader
- QuantConnect LEAN
- backtrader
- freqtrade
- vectorbt as a partial counterexample

## Order Data That Repeats Across Libraries

The libraries compared here repeatedly expose roughly the same minimum order
information:

- order identity
- symbol / instrument
- side
- order type
- requested quantity
- filled / remaining quantity
- price fields
  - `limit_price`
  - `stop_price`
  - average fill price
- status
- timestamps

This is evidence against treating runtime `Order` as a permanently thin record
containing only `symbol + quantity`.

Sources:

- Nautilus orders docs:
  https://nautilustrader.io/docs/latest/concepts/orders/
- QuantConnect LEAN order tickets:
  https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-management/order-tickets
- backtrader order docs:
  https://www.backtrader.com/docu/order/
- freqtrade trade object docs:
  https://docs.freqtrade.io/en/stable/trade-object/

## Lifecycle Model Comparison

### NautilusTrader

Nautilus has the strongest lifecycle model in the comparison set.

Representative statuses include:

- `INITIALIZED`
- `SUBMITTED`
- `ACCEPTED`
- `TRIGGERED`
- `PARTIALLY_FILLED`
- `FILLED`
- `CANCELED`
- `EXPIRED`
- `REJECTED`

It also includes pending update/cancel distinctions and emulation-oriented
states.

Benefits:

- runtime truth is extremely explicit
- stop/stop-limit, venue ACK, and local emulation all fit naturally

Drawbacks:

- it is too heavy for `quantleet`'s current scope
- without venue-style semantics, symbolic status names can outrun real meaning

### QuantConnect LEAN

LEAN separates request and runtime concerns well:

- `SubmitOrderRequest`
- `UpdateOrderRequest`
- `CancelOrderRequest`
- `Order`
- `OrderTicket`
- `OrderEvent`

Benefits:

- mutation workflows are explicit
- it scales well to live brokerage update/cancel flows

Drawbacks:

- `quantleet` does not yet have request/ack/update/cancel workflows
- copying this structure now would be premature

### backtrader

backtrader keeps the user UX light, but its runtime `Order` is still
substantial.

Representative statuses include:

- `Created`
- `Submitted`
- `Accepted`
- `Partial`
- `Completed`
- `Canceled`
- `Expired`
- `Margin`
- `Rejected`

It also has separate trigger flags.

Benefits:

- light strategy authoring and runtime orders coexist

Drawbacks:

- the broker loop pushes a lot of the semantics
- trigger and transition ownership are broker-centric, which makes it a weaker
  kernel model for `quantleet`

### freqtrade

freqtrade’s `Order` is closer to an exchange/trade persistence object than to
a reusable trading-kernel aggregate.

Benefits:

- practical for real bot operations and exchange snapshot tracking

Drawbacks:

- farther from the shared-kernel direction `quantleet` wants
- the system is more trade-centric than runtime-order-centric

## Who Owns State Transitions?

### Strongest `Order`-centric model: Nautilus

Nautilus is closest to an `Order` aggregate that owns legal state transitions
itself.

Even when external components compute facts or deliver events:

- legality checks
- open/closed decisions
- lifecycle progression

still end up owned by the `Order` side.

This is the strongest argument in favor of a richer runtime `Order` in
`quantleet`.

### More external-authority-heavy models: LEAN and backtrader

LEAN and backtrader still have runtime order objects, but transition authority
leans more heavily toward transaction handlers or broker loops.

Benefits:

- these models line up well with live brokerage mutation flows

Drawbacks:

- order-local invariants more easily leak outside the object

At the current `quantleet` stage, a **small rich aggregate + thin
orchestration** is the more convincing fit.

## Evidence About Event-Driven Decoupling

### Support

Event collaboration has clear strengths:

- senders do not need to know downstream consumers
- later reactions such as risk, portfolio, or alerting can be attached
  loosely
- adding consumers is easy

Especially after execution, facts like these are natural event payloads:

- `FillEvent`
- future `OrderTriggered`
- future `OrderCancelled`

Source:

- Martin Fowler, Event Collaboration:
  https://martinfowler.com/eaaDev/EventCollaboration.html

### Rebuttal

Fowler also emphasizes real downsides:

- control flow becomes implicit
- it gets harder to see who listens to what
- stale replicated state becomes more likely
- cascaded debugging gets harder

That is especially dangerous in trading runtime code:

- if ordering changes, fill/cash/position semantics change
- deterministic backtest contracts can break
- hidden subscribers can change behavior unexpectedly

So the evidence does **not** support “make everything event-driven.”

## DDD Aggregate Interpretation

Under Vaughn Vernon’s aggregate guidance, the key question is simple:

- an aggregate should protect true invariants
- an aggregate should stay small
- it should own only the immediate consistency it genuinely needs

From that lens, the following belong inside runtime `Order`:

- identity
- immutable submission terms
- filled / remaining quantity
- open / terminal judgment
- illegal fill / trigger / cancel / reject protection

The following belong outside the aggregate:

- fill price discovery
- order-book traversal
- slippage and fee math
- backtest activation timing
- next-bar lookahead protection
- cash / position / PnL accounting

So yes, `Order` should be rich — but not large.

Source:

- Vaughn Vernon aggregate essay:
  https://www.dddcommunity.org/wp-content/uploads/files/pdf_articles/Vernon_2011_1.pdf

## Strongest Contrarian View

The strongest contrarian view from this comparison was:

> `quantleet` already has the seam it needs. Designing more lifecycle/status
> machinery now risks overdesign relative to actual product pressure.

That objection is legitimate.

Current product scope is still:

- single-symbol
- long-only
- `market` / `limit`
- no cancel/replace
- no shipped stop-family
- no user-visible partial-fill workflow

That means there is weak evidence for immediately adopting:

- a huge status enum
- an `OrderEvent` mesh
- a LEAN-style request/ticket stack
- a Nautilus-style full OMS taxonomy

## Synthesis

This comparison weakens both extremes:

- keeping `Order` as a permanently thin record
- freezing a full OMS now

The strongest evidence points to the middle:

- `Order` should clearly own order-local invariants
- but it should not absorb matching, orchestration, and accounting
- expanding an internal event mesh into the main control plane is risky now

The comparator set does not converge on a single “perfect implementation
pattern.”

- Nautilus strongly supports `Order`-centric lifecycle ownership
- LEAN and backtrader give more authority to transaction/broker orchestration

So the most useful conclusion is narrower:

> `quantleet` can and should lean toward a small rich aggregate, but only in
> combination with explicit runtime orchestration and without taking on OMS
> weight prematurely

## What This Research Does Not Decide

This document does **not** settle:

- the exact status enum
- the exact representation of stop triggering
- whether submit/accept/reject should be stored as fields versus enum values
- how wide a mutable `Order` method surface should become

Those decisions belong in the design doc.

## One-Line Summary

The evidence supports making `Order` richer, but not making it heavy: do not
keep it as a thin record forever, and do not rush into full OMS or internal
event-mesh complexity.
