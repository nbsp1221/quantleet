# Order Reservation Policy

## Status

- Status: `implemented`
- Class: `product-spec`
- Scope:
  planned MVP policy for percent-sized orders, resource reservation, and
  dormant stop-family orders in the current single-symbol long-only
  research/backtest workflow

Related documents:

- [backtest-mvp.md](backtest-mvp.md)
- [research-ergonomics.md](research-ergonomics.md)
- [order-sizing.md](order-sizing.md)
- [stop-limit.md](stop-limit.md)
- [../plans/2026-04-29-order-reservation-test-scenarios.md](../plans/2026-04-29-order-reservation-test-scenarios.md)
- [../design-docs/order-lifecycle-and-sizing-design.md](../design-docs/order-lifecycle-and-sizing-design.md)
- [../design-docs/backtest-execution-semantics.md](../design-docs/backtest-execution-semantics.md)
- [../../ARCHITECTURE.md](../../ARCHITECTURE.md)

This document defines the product contract for the conservative reservation
policy slice now implemented in the current research/backtest workflow.

## Goal

Make strategy-authored order sizing predictable by ensuring that every accepted
order has a concrete quantity and a reserved resource claim before it enters
the runtime order book.

For the MVP, this means:

- `qty_percent` remains a strategy-facing convenience, not a runtime order
  field
- percent-sized orders resolve into fixed quantity before runtime `Order`
  creation
- accepted orders reserve the required cash or position immediately
- dormant stop-family orders covered by this policy reserve resources just like
  ordinary market or limit orders

## Why This Slice Exists

The current sizing surface lets strategies express orders in either fixed units
or percentages. That is useful, but stop-family orders expose a product gap:

- a stop order is dormant before trigger
- a percent order still needs a concrete quantity before the shared trading
  kernel can process it
- different real venues reserve conditional-order resources at different times
- the MVP needs one simple rule that users and agents can reason about

The conservative MVP rule is:

> accepted orders reserve the resources they may need, even if they are not yet
> executable.

This avoids an optimistic backtest where the same cash or position can support
many mutually competing dormant orders. It also preserves the existing
architecture direction: strategy UX may talk in percentages, but the trading
kernel should continue to process concrete quantity-based orders.

## Product Decision

The MVP default reservation policy is `reserve_on_accept`.

In this document, "accepted order" means a strategy request has passed runtime
activation, sizing, and resource checks and has become a concrete order intent.
It does not mean every submitted strategy request must become an order.

`reserve_on_accept` means:

1. strategy code submits an order request
2. the runtime resolves any `qty_percent` sizing into concrete quantity
3. the runtime accepts or rejects the request
4. accepted orders reserve the required resource immediately
5. dormant stop-family orders keep that reservation while waiting for trigger
6. filled orders consume the reservation
7. partial fills shrink the reservation to the remaining unresolved order
   quantity
8. canceled, expired, or otherwise removed orders release the reservation when
   those lifecycle states exist in a future slice

The first planned application of this policy covers:

- `market`
- `limit`
- `stop_market`
- `stop_limit`

For sizing and reservation purposes, stop-family orders inherit the price
anchor of the order they become after trigger:

- `stop_market` follows `market`
- `stop_limit` follows `limit`

The stop price decides when a stop-family order becomes executable. It does not
create a separate sizing mode.

The executable timing still differs by order type. A dormant stop-family order
is not executable before trigger. Reservation is a resource-safety fact, not an
execution fact.

The reservation owner is the runtime or account-control layer, not
`quantcraft.trading.domain.Order`. A reservation may be keyed by order id, but
runtime `Order` should remain quantity and lifecycle oriented rather than
absorbing cash, margin, portfolio, or risk-accounting fields.

## Core Semantic Rules

### 1. Runtime orders stay quantity-based

`qty_percent` must not become a field on runtime `Order`.

The intended boundary remains:

```text
Strategy.buy/sell(...)
  -> PendingOrderRequest(quantity | qty_percent) outside trading.domain
  -> sizing resolution
  -> OrderIntent(quantity)
  -> Order(quantity)
```

The runtime trading kernel should not need to know whether the user originally
typed `quantity=1.0` or `qty_percent=80`.

### 2. Percent sizing resolves before order creation

Percent sizing is resolved when the runtime activates the strategy request into
a concrete order intent.

For the current bar-based backtest workflow, that means the resource basis is
the runtime state available at request activation, not a later trigger-time
portfolio snapshot.

This keeps percent sizing aligned with real exchange APIs, where order
submission generally uses concrete venue primitives such as base quantity,
quote/notional amount, price, and trigger price rather than a dynamic
"available balance percent" field.

`quantcraft` chooses concrete base quantity as the runtime kernel primitive in
this MVP. Future venue adapters may translate between venue-native base-size or
quote-size APIs at the integration boundary, but that translation must not
change runtime `Order` into a percent-based object.

#### Prior-art baseline

A read-only source comparison against local financial-library clones supports
this boundary.

- `backtrader` computes percent sizing through a strategy sizer before broker
  submission; orders carry `size`, `price`, `pricelimit`, and `exectype`.
- `nautilus_trader` order factories for market, limit, stop-market, and
  stop-limit all require `Quantity`; stop variants add trigger and/or limit
  prices.
- `LEAN` exposes portfolio percentage helpers such as `SetHoldings` and
  `CalculateOrderQuantity`, while stop order APIs take concrete `quantity`.
- `backtesting.py` lets one `size` argument cover market, limit, stop-market,
  and stop-limit semantics. This is ergonomically close to the desired user
  surface, though it resolves fractional size at execution time and is less
  conservative than this MVP's `reserve_on_accept` policy.
- `lumibot`, `vectorbt`, and `freqtrade` likewise keep percent, target, or stake
  calculations outside venue-style order primitives or convert them before
  execution.

The product implication is that `qty_percent` should be accepted uniformly for
`market`, `limit`, `stop_market`, and `stop_limit`, but only as strategy/request
syntax. The runtime order and reservation ledger should operate on concrete
quantity plus order-type prices.

### 3. Stop orders inherit their child order sizing semantics

Stop-family orders are not separate sizing primitives.

In this MVP policy:

- `stop_market` is a market order with an added trigger condition
- `stop_limit` is a limit order with an added trigger condition

Therefore:

- `market` and `stop_market` use market-style percent sizing
- `limit` and `stop_limit` use limit-style percent sizing

For buy-side `stop_market`, the submitted `stop_price` is the trigger reference
and the sizing anchor. Modeled slippage and fees still apply to affordability.

For buy-side `stop_limit`, `limit_price` is the sizing anchor. The stop price
does not affect quantity resolution.

### 4. Accepted buy orders reserve cash

For buy-side orders, the reservation represents the cash required to support
the accepted order under the current execution-cost assumptions.

The price anchor should be conservative and order-type specific:

- `market`: current executable buy reference plus modeled slippage
- `limit`: submitted `limit_price`
- `stop_market`: submitted `stop_price` plus modeled slippage
- `stop_limit`: submitted `limit_price`

If an explicit `quantity` buy request would exceed available cash under the
modeled reservation requirement, the request should not be accepted as a
smaller order. It should emit an explicit rejection event with a stable reason.

If a `qty_percent` buy request would exceed available cash after fees or other
modeled costs, the sizing resolver may reduce the position budget only as
defined by [order-sizing.md](order-sizing.md). This clamp is part of percent
sizing, not a general license to resize explicit fixed-quantity orders.

### 5. Accepted sell orders reserve position quantity

For sell-side orders in the current long-only workflow, the reservation
represents closable long position quantity.

Sell-side percent sizing uses the net unreserved long position as its basis.
Multiple active exit orders should not be able to reserve more than the current
long position.

Flat sell orders remain governed by the current long-only no-short policy.

### 6. Dormant stop orders are reserved but not executable

A stop-family order can be both:

- resource-reserved
- not executable

Before trigger:

- it cannot fill
- its cash or position claim still reduces available resources for later
  requests

After trigger:

- `stop_market` becomes executable as a market order
- `stop_limit` becomes executable as a limit order
- the reservation ledger remains associated with the same order id until the
  order is filled, partially filled, canceled, expired, or otherwise removed

## Success Conditions

The policy is successful when a user can reason about available resources with
one rule:

> if the engine accepted an order, the resources needed for that order are no
> longer available to later competing orders.

Concrete success criteria:

- `qty_percent` never leaks into runtime `Order`
- percent-sized market, limit, stop-market, and stop-limit requests resolve to
  fixed quantity before runtime order creation
- dormant stop-family buy orders covered by this policy reduce later buy-side
  available cash
- dormant stop-family sell orders covered by this policy reduce later sell-side
  available position
- multiple active or pending orders cannot reserve the same cash or position
  twice
- partial fills reduce remaining reservation to the unresolved remainder
- stop trigger timing does not recalculate percent sizing
- trigger-time execution can still fail for normal execution reasons, but not
  because the engine allowed later orders to spend the same reserved resource
- tests and examples explain that this is a conservative MVP policy, not a
  full venue-specific conditional-order model

## User-Facing Examples

### Percent stop-limit entry

```python
self.buy(
    qty_percent=80,
    order_type="stop_limit",
    stop_price=105.0,
    limit_price=106.0,
)
```

Intended meaning:

- use 80% of currently unreserved buy-side quote-cash basis at activation,
  subject to fee-aware affordability
- compute a concrete quantity using `limit_price=106.0`
- create a dormant stop-limit order with that fixed quantity
- reserve the modeled cash requirement immediately
- do not recalculate quantity when the stop later triggers

### Percent stop-limit exit

```python
self.sell(
    qty_percent=50,
    order_type="stop_limit",
    stop_price=95.0,
    limit_price=94.0,
)
```

Intended meaning:

- use 50% of currently unreserved closable long quantity at activation
- create a dormant stop-limit sell order with that fixed quantity
- reserve that position quantity immediately
- do not let later exit orders reserve the same quantity

### Percent stop-market entry

```python
self.buy(
    qty_percent=50,
    order_type="stop_market",
    stop_price=105.0,
)
```

Intended meaning:

- use 50% of currently unreserved buy-side quote-cash basis at activation,
  subject to fee-aware affordability
- compute a concrete quantity using `stop_price=105.0` plus modeled slippage
- create a dormant stop-market order with that fixed quantity
- reserve the modeled cash requirement immediately
- do not recalculate quantity when the stop later triggers

### Percent stop-market exit

```python
self.sell(
    qty_percent=50,
    order_type="stop_market",
    stop_price=95.0,
)
```

Intended meaning:

- use 50% of currently unreserved closable long quantity at activation
- create a dormant stop-market sell order with that fixed quantity
- reserve that position quantity immediately
- execute as a market sell only after the stop triggers

## Why Not Trigger-Time Percent Sizing

Trigger-time percent sizing is a different product concept.

It would mean:

```text
when trigger condition becomes true:
  inspect portfolio again
  compute quantity from current available resources
  submit a new order
```

That can be useful later, but it is closer to strategy-level conditional order
generation than to a normal exchange-style stop order with fixed size.

The MVP does not use trigger-time percent sizing because it:

- makes dormant order size unknowable before trigger
- makes backtest results more sensitive to unrelated later orders
- complicates resource accounting
- diverges from the current `OrderIntent -> Order(quantity)` boundary
- encourages users to treat stop orders as hidden strategy callbacks

Future execution or venue adapters may support venue-specific conditional
checks, but that must be an explicit account or risk policy rather than an
adapter-local escape hatch. A future `check_on_trigger` mode must still define
how the account avoids unintended overcommitment, how failures are reported,
and how it differs from the deterministic research default.

## Relationship To Real Venues

Real venues differ on when conditional orders reserve funds or margin.

Some venue and account models reserve resources when an order is accepted.
Others accept a conditional order without immediate reservation and check
available balance or margin when the trigger fires.

`quantcraft` deliberately chooses the more conservative MVP model:

- fixed quantity is decided before runtime order creation
- required resources are reserved when the order is accepted
- later venue-specific `check_on_trigger` behavior is deferred and must be
  modeled as an explicit account-control policy

This choice favors deterministic research behavior and simpler user reasoning
over exact replication of every venue's conditional-order margin policy.

## Implementation Policy Decisions

The human product-intent questions for this slice are closed:

1. Stop-market gap overspend:
   when a buy `stop_market` triggers, the engine attempts execution at the
   modeled executable price from the OHLC path, including gap and slippage
   effects. The fixed order quantity is not recalculated from percent sizing.
   If the account can afford the actual execution cost with the order's
   reservation plus currently unreserved cash, the order may fill. If not, the
   order is rejected with an observable rejection event, no fill is created, no
   cash-shortage partial fill is created, no negative cash is allowed, and the
   reservation is released.
2. Failure reporting surface:
   invalid order shape or invalid strategy request input raises a validation
   error at the earliest boundary. Examples include non-positive quantity,
   `qty_percent <= 0`, `qty_percent > 100`, missing required prices, or fields
   that contradict the order type. Valid orders that fail because of account or
   market state are not silently ignored. They must produce an observable
   rejection event with a stable reason, such as insufficient cash,
   insufficient position, minimum quantity, minimum notional, or execution
   affordability failure.
3. Account-control ownership:
   reservation accounting, available-balance checks, rejection decisions, and
   reservation release belong to the runtime/account-control layer. The
   `Order` domain object owns order invariants only. This keeps the MVP
   backtest implementation aligned with later paper/live execution boundaries.

## Non-Goals

This slice does not include:

- venue-specific conditional-order margin modes
- `check_on_trigger` as a selectable runtime policy
- full account, margin, leverage, or buying-power modeling
- short selling
- reduce-only, post-only, time-in-force, OCO, OTO, bracket, or trailing orders
- cancel, replace, or amend flows
- dynamic trigger-time percent sizing
- portfolio target sizing such as target weight, target value, or rebalance
  targets
- moving `qty_percent` into runtime `Order`

## Open Questions For Later Slices

- how reservations should be represented once cancel/replace/expire events are
  first-class lifecycle transitions
- whether future paper/live account-control layers should expose a venue policy
  such as `reserve_on_accept` versus `check_on_trigger`
- how margin, leverage, and short-side reservations should work outside the
  current long-only MVP
