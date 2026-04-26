# Order Sizing Spec

## Status

- Status: `implemented`
- Class: `product-spec`
- Scope:
  current implemented explicit percentage-based order sizing slice in the
  current single-symbol backtest and research workflow

Related documents:

- [backtest-mvp.md](backtest-mvp.md)
- [research-ergonomics.md](research-ergonomics.md)
- [../design-docs/backtest-execution-semantics.md](../design-docs/backtest-execution-semantics.md)
- [../design-docs/order-lifecycle-and-sizing-design.md](../design-docs/order-lifecycle-and-sizing-design.md)

Status note:

- the current shipped strategy surface supports both `quantity` and
  `qty_percent`, plus `stop_price` for `stop_market`
- runtime `OrderIntent` resolves sizing into concrete quantity and may also
  carry trigger facts for shipped `stop_market`
- runtime `Order` remains quantity-based and may also carry trigger facts for
  shipped `stop_market`
- this document is now part of the current product authority for shipped
  behavior alongside [backtest-mvp.md](backtest-mvp.md) and
  [research-ergonomics.md](research-ergonomics.md)
- current backtest path construction and conservative executable-price rules
  remain governed by
  [../design-docs/backtest-execution-semantics.md](../design-docs/backtest-execution-semantics.md)
- current architecture boundaries remain governed by
  [../../ARCHITECTURE.md](../../ARCHITECTURE.md)

## Goal

Provide a small, explicit order-sizing UX that lets strategy authors express:

- entry or increase by percentage
- partial exit by percentage
- fixed quantity when they want direct control

without overloading `quantity`, and without introducing portfolio-target
rebalancing semantics into the current backtest MVP.

## Why This Slice Exists

The original quantity-only strategy surface was adequate for deterministic MVP
coverage, but it was weaker than common real strategy authoring workflows,
where users often think in:

- "deploy 80% of available capital"
- "take off 30% of the current position"

This shipped slice improves that UX without forcing `quantcraft` into a full
portfolio-construction layer.

## Current Repository Truth

Current shipped truth:

- `Strategy.buy()` and `Strategy.sell()` accept either `quantity` or
  `qty_percent`, plus `order_type`, `limit_price`, `stop_price`, and `tag`
- pending strategy requests are modeled outside `trading.domain`
- `OrderIntent` resolves sizing into quantity and may also carry shipped
  stop-trigger facts
- runtime `Order` remains quantity-based and may also carry shipped
  stop-trigger facts
- current shipped scope remains:
  - single symbol
  - long-only
  - `market`, `limit`, and `stop_market`
  - `qty_percent + stop_market` remains out of scope
  - no margin or leverage modeling
  - no portfolio-target APIs

Repository evidence:

- [strategy.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/research/strategy.py:64)
- [intents.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/trading/domain/intents.py:11)
- [orders.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/trading/domain/orders.py:10)
- [backtest-mvp.md](/home/retn0/repositories/nbsp1221/quantcraft/docs/product-specs/backtest-mvp.md:106)

## Public UX Direction

The first approved percentage-sizing direction for this slice is:

```python
self.buy(quantity=1.0)
self.buy(qty_percent=80)

self.sell(quantity=0.5)
self.sell(qty_percent=30)
```

Rules:

- `quantity` and `qty_percent` are mutually exclusive
- callers must provide exactly one sizing mode
- `qty_percent` is expressed as a human percent, not a decimal fraction:
  - `30` means `30%`
  - `80` means `80%`

This slice does **not** adopt a strategy-level default sizing declaration such
as a top-level global `default_qty_type`.

Sizing remains explicit at the order-intent call site.

## Core Semantic Rule

`qty_percent` has one product meaning:

> a strategy-layer budget instruction expressing the percentage of currently
> executable sizing resources for the requested order direction

This means:

- `qty_percent` is part of the strategy-facing sizing UX
- `qty_percent` is not a venue-native order field
- `qty_percent` is not part of the runtime `Order` object

In the current single-symbol, long-only slice that means:

- for `buy(...)`, `qty_percent` is a percentage of reserved-adjusted quote cash
  used as requested position budget, with fee-aware affordability clamping
- for `sell(...)`, `qty_percent` is a percentage of net closable position
  quantity

This intentionally avoids the following meanings in this slice:

- portfolio value percentage
- equity target percentage
- buying-power target percentage
- rebalance target percentage

## Resolution Boundary

The architectural rule remains:

- strategy code expresses intent
- runtime `Order` stays concrete and quantity-based

Therefore:

- `qty_percent` must not flow through the runtime `Order` model as a raw
  percentage field
- `qty_percent` must not be treated as a venue-order field
- percent sizing must resolve into concrete quantity in the strategy/runtime
  control path before runtime `Order` creation

The intended boundary is:

`Strategy.buy/sell -> sizing resolver in research/backtest or execution runtime -> quantity-based trading path`

This preserves the current `OrderIntent != runtime Order` seam and keeps the
runtime trading kernel quantity-based.

This slice does **not** require `quantcraft.trading` domain models to carry raw
percentage fields.

To avoid environment drift, one canonical shared sizing policy should define:

- resource-basis semantics
- reservation accounting
- affordability and rounding rules
- order-type price anchors

Backtest and execution runtimes should provide environment-specific inputs such
as current resources, active orders, and instrument constraints, but they
should not invent separate percent-resolution semantics.

## Buy-Side Semantics

For `buy(qty_percent=...)`, the resolver interprets the requested
percentage against the reserved-adjusted quote-cash basis available for new buy
position budget.

Conceptually:

1. determine the quote cash available for new buy sizing
2. subtract any buy-side cash already reserved for active unresolved buy orders
3. apply the requested percentage to that remaining quote-cash basis to obtain
   the requested position budget
4. check whether that requested position budget remains affordable once the
   current runtime model's fee and execution-cost assumptions are added
5. keep the requested position budget unchanged when it is affordable
6. otherwise clamp the position budget down to the maximum affordable budget
   under the current runtime model
7. convert the final affordable position budget into concrete base-asset
   quantity using the current execution-model context
8. round the result down to the supported quantity precision and tradable size
   boundary for the current environment
9. reject the request if the resulting quantity is not tradable
10. create a quantity-based runtime `Order`

Current intended scope:

- the user expresses buy-side sizing in quote-cash position-budget terms
- the engine resolves that budget into asset quantity
- the buy-side resource base is reservation-aware rather than gross-cash-only
- the quantity is bounded by the current backtest execution semantics and cost
  assumptions
- fees and other conservative execution costs constrain affordability after the
  requested position budget is computed rather than redefining the meaning of
  the requested percentage

For this slice, the buy-side quote-cash basis means:

- quote cash not already reserved for unresolved buy-side intent
- quote cash that may be requested as new position budget before fees are
  charged

For this slice, fee-aware affordability means:

- fees are modeled as additional cash consumption on top of the requested
  position budget
- if the requested position budget plus modeled costs is affordable, the engine
  should preserve that requested budget exactly
- if the requested position budget plus modeled costs is not affordable, the
  engine should reduce only as much position budget as needed to remain
  affordable
- this is a general affordability clamp for any percent, not a special rule
  only for `qty_percent=100`

This slice does **not** interpret buy-side `qty_percent` as:

- "hold 80% of total portfolio in this asset"
- "buy 80% of current equity regardless of existing holdings"
- "use 80% of leveraged buying power"

## Price Anchor Rule

Buy-side percent sizing must use an explicit conservative price anchor when
translating the final affordable position budget into base quantity.

For this slice:

- `market` buys should use the runtime's current executable buy-side reference
  price, plus the slice's fee and slippage assumptions when computing
  affordability
- `limit` buys should use the submitted `limit_price` as the affordability
  anchor for quantity resolution

The `limit` rule is intentionally conservative:

- the venue should not fill a limit buy above its submitted limit
- using `limit_price` prevents the resolver from creating a quantity that is
  only affordable at a more optimistic valuation price

This slice does not require the buy-side resolver to maximize quantity against
the most optimistic currently visible price.

## Sell-Side Semantics

For `sell(qty_percent=...)`, the resolver should interpret the requested
percentage against net closable position quantity only.

Conceptually:

1. read the current open long quantity
2. subtract any sell-side quantity already reserved by active unresolved exit
   orders
3. treat the remainder as net closable quantity
4. apply the requested percentage to that net closable quantity
5. round the result down to the supported quantity precision and tradable size
   boundary for the current environment
6. submit no new order if the resulting quantity is not tradable
7. create a quantity-based runtime `Order` when the resolved exit quantity is
   tradable

Current intended scope:

- the user expresses sell-side sizing as a fraction of what is still closable
- the sell-side resource base is reservation-aware rather than gross-position-only
- percent exits stay within the current long-only exit semantics of the MVP

For this slice, "net closable quantity" means:

- current open long quantity
- minus quantity already reserved by active unresolved exit-side orders

Examples:

- `sell(qty_percent=30)` means "attempt to exit 30% of the currently net
  closable long"
- `sell(qty_percent=100)` means "attempt to exit the full currently net
  closable long"

In the current long-only slice, sell-side percent sizing remains exit-only.
It does not become a short-entry shorthand.

## Reservation Lifecycle

Reservation accounting in this slice must track unresolved remainder, not
original requested size.

That means:

- buy-side cash reservation should track only the unresolved remaining spend
  implied by active buy-side orders
- sell-side quantity reservation should track only the unresolved remaining exit
  quantity implied by active sell-side orders
- reservations should shrink on partial fills as unresolved remainder shrinks
- reservations should be released when the active order is canceled, rejected,
  expired, or otherwise reaches a terminal no-longer-working state

This slice should not double-count already filled size as still reserved.

## Percent Range And Validation

The intended validation contract for `qty_percent` is:

- it must be numeric
- it must be strictly greater than `0`
- it must be less than or equal to `100`

Invalid examples:

- `qty_percent=0`
- `qty_percent=-5`
- `qty_percent=120`

This slice should fail invalid sizing requests explicitly rather than silently
clipping them.

## Same-Cycle Resolution Order

Within a single strategy callback or other single intent-emission cycle, new
percent-sized orders should resolve serially in the order they are emitted.

That means:

- each accepted percent-sized order updates reservation state before the next
  percent-sized order in the same cycle resolves
- later orders in the same cycle see the already reduced free cash or net
  closable quantity left by earlier accepted orders
- this slice does not define a same-cycle batch rebalance optimizer or
  sell-first reorderer

The intent-emission order therefore remains part of the deterministic sizing
contract for this first slice.

## Affordability And Conservative Resolution

This slice should remain consistent with the repository's conservative backtest
execution model.

Implications:

- percent-based buy sizing must resolve against reserved-adjusted resources, not
  gross cash
- buy-side resolution must preserve the requested position budget when that
  budget remains affordable after fees are applied
- buy-side resolution must clamp the requested position budget only when the
  requested budget plus fees would over-allocate cash
- buy-side resolution must round down and reject sub-minimum quantities rather
  than silently assuming venue acceptance
- buy-side resolution must enforce the current environment's supported
  quantity increment, minimum quantity, and minimum notional or cost rules
- exit-side percent sizing must resolve against net closable quantity, not
  gross position quantity
- exit-side percent sizing must not create overlapping exit quantity beyond the
  currently net closable long

The exact arithmetic remains an implementation concern for the later code
slice, but the product contract is clear:

- `qty_percent` should not over-allocate capital
- `qty_percent` should not oversell the current position after active exit
  reservations are considered

## Execution-Layer Note

This product slice intentionally mirrors common strategy-authoring UX while
remaining separate from venue API semantics.

That means:

- users author `qty_percent` in strategy code
- the runtime converts that into concrete quantity before order creation
- downstream exchange adapters continue to operate on the concrete venue
  primitives they already support

This slice should not be read as a claim that exchanges natively accept a
universal `qty_percent` order parameter.

## Order-Type Scope For This Slice

The first percentage-sizing slice applies only to the current shipped order
types:

- `market`
- `limit`

It does **not** automatically widen support to:

- stop-market
- stop-limit
- trailing or bracket-style orders

Future order-type expansion should inherit this sizing primitive only after the
runtime order and stop-family slices are defined.

Current shipped stop-family rule:

- `stop_market` requests support `quantity`
- `qty_percent + stop_market` remains explicitly out of scope and is rejected
  during strategy request normalization

## Strategy Examples

Illustrative examples:

```python
class DipBuyer(Strategy):
    def on_bar(self, bar):
        if not self.position.is_open:
            self.buy(qty_percent=80)
        elif some_take_profit_signal():
            self.sell(qty_percent=30)
```

```python
class MixedSizing(Strategy):
    def on_bar(self, bar):
        if first_entry_condition():
            self.buy(qty_percent=50)
        elif scale_in_condition():
            self.buy(quantity=0.25)
        elif reduce_condition():
            self.sell(qty_percent=25)
```

## Explicitly Deferred

This slice intentionally does **not** define:

- `target_percent`
- `target_value`
- portfolio rebalancing
- multi-symbol percent allocation
- buying-power or leverage-aware sizing
- quote-notional sizing as a separate public contract
- strategy-level default sizing declarations
- open-order-aware target reconciliation
- same-cycle sell-first reorder or rebalance optimization

Those are distinct features and should not be smuggled into the first
percentage-sizing slice.

## Acceptance Direction

This shipped product slice remains coherent only if all of the following hold:

1. users can still place explicit quantity-based orders
2. users can express percent-based buy sizing without overloading `quantity`
3. users can express partial exit percentages directly
4. runtime `Order` remains quantity-based
5. the new primitive does not silently become a portfolio-target API
6. the resulting semantics remain consistent with current conservative backtest
   rules
