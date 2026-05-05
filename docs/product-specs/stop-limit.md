# Stop-Limit Order Spec

## Status

- Status: `implemented`
- Class: `product-spec`
- Scope:
  current `stop_limit` order slice for the single-symbol
  long-only research/backtest workflow

Related documents:

- [backtest-mvp.md](backtest-mvp.md)
- [research-ergonomics.md](research-ergonomics.md)
- [order-sizing.md](order-sizing.md)
- [order-reservation.md](order-reservation.md)
- [../plans/2026-04-27-stop-limit-test-scenarios.md](../plans/2026-04-27-stop-limit-test-scenarios.md)
- [../design-docs/backtest-execution-semantics.md](../design-docs/backtest-execution-semantics.md)
- [../design-docs/order-lifecycle-and-sizing-design.md](../design-docs/order-lifecycle-and-sizing-design.md)
- [../../ARCHITECTURE.md](../../ARCHITECTURE.md)

This document defines the product contract for shipped `stop_limit` orders in
the current research/backtest workflow.

Conservative resource-reservation behavior for percent-sized stop-limit orders
is governed by [order-reservation.md](order-reservation.md). That policy is now
part of the shipped stop-family sizing contract.

The linked test scenario plan is a pre-implementation planning input, not a
second product authority. Once executable tests exist, those tests become the
scenario-level source of truth.

## Goal

Let strategy authors express a stop-triggered order that becomes a working
limit order only after its stop condition is reached.

In the current slice, `stop_limit` extends the existing
`Strategy.buy()` / `Strategy.sell()` research workflow and the public
`BacktestEngine` path without changing the shared matching boundary.

## Why This Slice Exists

The shipped `stop_market` slice lets strategies express breakout or protective
trigger behavior, but execution after trigger is still market-like. That is not
enough when the user wants price protection after the trigger.

`stop_limit` fills that gap:

- the stop price defines when the order becomes active
- the limit price defines the worst acceptable execution price after activation
- the order may remain unfilled after trigger if the market moves through the
  limit too quickly

This is consistent with real trading venues. Coinbase describes a stop-limit
order as automatically placing a limit order when the stop price is reached.
Binance.US describes it as placing a limit buy/sell order once the market price
reaches the designated stop price. Interactive Brokers describes the same
two-part model: stop price activates the order, then limit price constrains
execution. Kraken documents stop-loss-limit behavior where a triggered stop
opens a limit order and also calls out selectable trigger signals.

External references:

- [Coinbase Advanced Trade order types](https://help.coinbase.com/en-gb/coinbase/trading-and-funding/advanced-trade/order-types)
- [Binance.US stop-limit order overview](https://support.binance.us/en/articles/9842888-what-s-the-difference-between-market-limit-and-stop-limit-orders)
- [Binance.US stop-limit function guide](https://support.binance.us/en/articles/9842912-how-to-use-the-stop-limit-function)
- [Interactive Brokers stop-limit glossary](https://www.interactivebrokers.com/campus/glossary-terms/stop-limit-order/)
- [Kraken other order options](https://support.kraken.com/hc/articles/7987518770708-other-order-options)
- [Coinbase Exchange matching engine](https://docs.cdp.coinbase.com/exchange/concepts/matching-engine)
- [Binance.US trading rules](https://www.binance.us/trading-rules/)

## Current Repository Truth

Current repository truth:

- `OrderType` supports `market`, `limit`, `stop_market`, and `stop_limit`.
- `Strategy.buy()` and `Strategy.sell()` accept `order_type`, `quantity`,
  `qty_percent`, `limit_price`, `stop_price`, and `tag`.
- `stop_market` uses `stop_price` at strategy intake and normalizes it into
  runtime `trigger_price`, `trigger_condition`, and `trigger_type`.
- runtime `OrderIntent` and `Order` already carry trigger facts and
  `limit_price`.
- dormant `stop_market` orders are not executable.
- triggered `stop_market` orders reuse market execution semantics.
- ordinary `limit` orders reuse the shared matching kernel and are constrained
  by `limit_price`.
- current backtest execution semantics are owned by `backtest`; matching and
  state transitions stay in `trading`.
- `qty_percent` is supported for `market`, `limit`, `stop_market`, and
  `stop_limit`.

Repository evidence:

- [strategy.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/research/strategy.py)
- [intents.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/trading/domain/intents.py)
- [orders.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/trading/domain/orders.py)
- [matching.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/trading/domain/matching.py)
- [execution_model.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/backtest/execution_model.py)
- [runtime.py](/home/retn0/repositories/nbsp1221/quantleet/src/quantleet/backtest/runtime.py)

## Public UX Direction

The public strategy API is additive:

```python
self.buy(
    quantity=1.0,
    order_type="stop_limit",
    stop_price=105.0,
    limit_price=106.0,
    tag="breakout-entry",
)

self.sell(
    quantity=1.0,
    order_type="stop_limit",
    stop_price=95.0,
    limit_price=94.0,
    tag="protected-exit",
)
```

Rules:

- `order_type="stop_limit"` requires `stop_price`.
- `order_type="stop_limit"` requires `limit_price`.
- `quantity` and `qty_percent` are supported.
- users do not provide `trigger_condition` directly from the strategy surface.
- the strategy surface infers `trigger_condition` from `stop_price` relative to
  the last evaluated `last` reference price, matching the current
  `stop_market` UX.

The public naming is `stop_limit` to stay consistent with existing
snake_case order types such as `stop_market`.

## Core Semantic Rule

`stop_limit` has one product meaning:

> a stop-triggered order that becomes a working limit order only after its
> trigger condition is satisfied

In `quantleet`, `stop` is a generic price-trigger primitive. It is not a
venue-specific synonym for stop-loss, take-profit, bracket, reduce-only, or
position-close behavior. Those higher-level names describe how a trigger is
used around a position; this slice implements the lower-level trigger order
itself.

This means:

- before trigger, the order is dormant and cannot fill
- before trigger, crossing the limit price alone is irrelevant
- after trigger, the order is executable as a limit order
- after trigger, the order may fill at the limit price or better
- after trigger, the order may remain open if the current executable price is
  worse than the limit
- no pre-trigger price movement may be used retroactively to fill the order

This deliberately mirrors the existing `stop_market` shape while changing only
the post-trigger executable behavior:

- `stop_market` = stop trigger, then market execution
- `stop_limit` = stop trigger, then limit execution

## Lifecycle Semantics

The lifecycle is:

```text
Strategy.buy/sell(...)
  -> PendingOrderRequest
  -> OrderIntent
  -> dormant runtime Order(order_type="stop_limit")
  -> triggered runtime Order(order_type="stop_limit")
  -> filled, partially filled, or still-open working limit order
```

State rules:

- a dormant `stop_limit` is not executable
- triggering records the trigger timestamp
- a triggered `stop_limit` becomes executable as a limit order
- a triggered but unfilled `stop_limit` remains active
- a filled `stop_limit` follows existing `Order.apply_fill()` terminal or
  remaining-quantity behavior

The first slice does not add user-visible partial-fill scenarios, but the
runtime model should not block the matching kernel from continuing to support
finite-liquidity fills internally.

## Trigger Direction

The first slice inherits the current `stop_market` trigger-direction model.
At order intake, compare `stop_price` with the last evaluated `last` reference
price:

- if `stop_price > reference_last`, infer `crosses_above`
- if `stop_price < reference_last`, infer `crosses_below`
- if `stop_price == reference_last`, reject the request as ambiguous

Do not derive trigger direction from order side, position direction, entry/exit
purpose, or the eventual limit price. A buy, sell, long-entry, long-exit,
short-entry, or short-exit intent uses the same trigger-direction rule.

In the current bar-based backtest workflow, the active closed-bar close is the
last evaluated `last` reference price available to strategy order intake. Future
paper or live workflows should use their own last evaluated `last` tick. This
keeps the product rule tick-based rather than bar-specific.

The equality rejection is a conservative `quantleet` policy, not a claim that
all venues reject already-met trigger orders. Some venues immediately trigger
already-met stops; others reject stops that would trigger immediately or are too
close to the current market. Because this product surface does not expose
`trigger_condition`, equality lacks enough information to infer direction
without inventing hidden user intent.

Examples:

- buy breakout above the reference last:
  `buy(order_type="stop_limit", stop_price=105, limit_price=106)` infers
  `crosses_above` when `reference_last=100`
- buy pullback below the reference last:
  `buy(order_type="stop_limit", stop_price=95, limit_price=94)` infers
  `crosses_below` when `reference_last=100`
- sell breakdown below the reference last:
  `sell(order_type="stop_limit", stop_price=95, limit_price=94)` infers
  `crosses_below` when `reference_last=100`
- sell take-profit-style trigger above the reference last:
  `sell(order_type="stop_limit", stop_price=105, limit_price=104)` infers
  `crosses_above` when `reference_last=100`

Limit price does not participate in trigger-direction inference. With
`reference_last=100` and `stop_price=90`, all of these infer `crosses_below` at
intake:

- `buy(..., stop_price=90, limit_price=120)`
- `buy(..., stop_price=90, limit_price=80)`
- `sell(..., stop_price=90, limit_price=120)`
- `sell(..., stop_price=90, limit_price=80)`

Whether those orders fill is decided later, after trigger, by the executable
tick data and ordinary limit matching semantics.

## Limit Price Semantics

After trigger, `limit_price` has the same meaning as an ordinary limit order:

- buy limit: fill only at `limit_price` or lower
- sell limit: fill only at `limit_price` or higher

The first slice should not impose a hard relationship between `stop_price` and
`limit_price` beyond both being positive finite prices.

Typical venue examples use:

- buy stop-limit with `limit_price >= stop_price`
- sell stop-limit with `limit_price <= stop_price`

Those relationships are common because they make the triggered order more
likely to execute after a breakout or protective trigger. They should be
documented as examples, not enforced as a product invariant. Some venues impose
venue-specific price bands or order-entry constraints. `quantleet` should keep
those as future venue/instrument constraints rather than hard-coding them into
the first research/backtest slice.

## Trigger Reference

The first slice uses the current `stop_market` trigger reference:

- `trigger_type="last"`

This aligns with the current internal `TickEvent.last` matching path and keeps
the first stop-limit slice inside the shipped research/backtest model.

Real venues may support different trigger references. Kraken documents last
price and index price trigger signals. Derivatives venues commonly expose mark,
index, or contract-price trigger references. Those are future venue/product
constraints, not first-slice research/backtest behavior.

## Backtest Execution Semantics

Backtest path construction remains governed by
[../design-docs/backtest-execution-semantics.md](../design-docs/backtest-execution-semantics.md).

Additional `stop_limit` rules:

- strategy-created orders do not apply retroactively to the bar that created
  them
- dormant `stop_limit` orders activate on the next bar like other current
  strategy requests
- a gap through the stop triggers the order at the next bar open, because open
  is the first executable price
- intrabar trigger detection follows the canonical path:
  - bullish bar: `open -> low -> high -> close`
  - bearish bar: `open -> high -> low -> close`
- once triggered, the order may match only against the trigger point and the
  path tail after that point
- pre-trigger path segments must never be evaluated as if the order had already
  been a working limit
- if the trigger point is also limit-marketable, same-point trigger and fill is
  allowed
- if the trigger point is worse than the limit, the order remains open as a
  triggered working limit order
- if the order triggers within a path segment and remains unfilled, backtest
  traversal must be able to evaluate the remaining segment tail for newly
  relevant limit crossings

The matching kernel must remain bar-unaware. `backtest` owns synthetic path and
decisive-event construction; `trading` consumes executable events and applies
ordinary trigger, matching, fill, and state-transition rules.

## Gap-Through Examples

### Buy Stop-Limit Filled

- previous close: `100`
- submitted order: buy `stop_price=105`, `limit_price=106`
- next path crosses `105`
- first executable trigger point is `105`

Expected result:

- order triggers at `105`
- order is now a buy limit at `106`
- the trigger point is at or below the buy limit
- fill may occur at the ordinary conservative executable price

### Buy Stop-Limit Not Filled

- previous close: `100`
- submitted order: buy `stop_price=105`, `limit_price=106`
- next bar opens at `110`

Expected result:

- order triggers at the open
- order is now a buy limit at `106`
- open `110` is worse than the buy limit
- no fill occurs at the open
- order remains active as a triggered working limit

### Sell Stop-Limit Filled

- previous close: `100`
- submitted order: sell `stop_price=95`, `limit_price=94`
- next path crosses `95`
- first executable trigger point is `95`

Expected result:

- order triggers at `95`
- order is now a sell limit at `94`
- the trigger point is at or above the sell limit
- fill may occur at the ordinary conservative executable price

### Sell Stop-Limit Not Filled

- previous close: `100`
- submitted order: sell `stop_price=95`, `limit_price=94`
- next bar opens at `90`

Expected result:

- order triggers at the open
- order is now a sell limit at `94`
- open `90` is worse than the sell limit
- no fill occurs at the open
- order remains active as a triggered working limit

## Sizing Scope

Included in the current slice:

- `quantity + stop_limit`
- `qty_percent + stop_limit`

Sizing policy:

- stop-limit percent sizing uses `limit_price` as the buy-side sizing anchor
- dormant buy stop-limit orders reserve cash at acceptance
- `qty_percent` resolves to concrete quantity before runtime `Order` creation
- `qty_percent` does not flow into `Order` or venue-adapter primitives

Reservation guidance:

- [order-reservation.md](order-reservation.md) defines the conservative answer:
  `reserve_on_accept`

## Order Identity, Priority, And Results

The first implementation should preserve the same runtime order identity after
trigger:

- keep the same order id
- keep `order_type="stop_limit"`
- set `triggered_at`
- route executable behavior as `limit`

This keeps trigger state inspectable internally and avoids hiding stop-limit
lifecycle by replacing it with an ordinary limit order too early.

Ordering guidance:

- existing executable orders are processed before newly triggered stop-family
  orders at the same event point
- a triggered but unfilled stop-limit keeps stable order identity and remains in
  the active order set for later events

This is `quantleet`'s deterministic price-time-like priority policy. It aligns
with common central-limit-order-book price-time/FIFO practice: orders already
eligible for execution are evaluated before orders that only become eligible at
the current event.

Public result guidance:

- the public `trade_log` remains fill-level
- runtime/account failures may appear in `BacktestResult.order_events`
- trigger-only events do not appear in `trade_log`
- a later public order-event surface may expose trigger events explicitly, but
  that is out of scope for this slice

## Included Scope

The current implementation slice includes:

- single symbol
- single timeframe
- long + flat position scope
- `quantity` and `qty_percent` sizing
- `Strategy.buy(..., order_type="stop_limit", stop_price=..., limit_price=...)`
- `Strategy.sell(..., order_type="stop_limit", stop_price=..., limit_price=...)`
- public `BacktestEngine.run(bars=..., strategy=...)`
- public `BacktestEngine.run(source=..., strategy=...)`
- dormant trigger state
- triggered working-limit state
- conservative OHLC backtest gap and intrabar semantics
- canonical unit and integration tests

## Excluded Scope

This implemented slice does not include:

- trailing stop-limit orders
- stop-loss or take-profit attachments
- OTO, OCO, bracket, or parent-child order activation
- cancel, modify, or replace flows
- reduce-only orders
- shorting
- leverage or margin
- multi-symbol support
- multi-timeframe support
- live trading
- paper trading
- venue-specific price bands
- venue-specific trigger references beyond current `last`
- time-in-force controls
- user-visible partial-fill contracts

## Validation Rules

Strategy intake and order normalization should enforce:

- `stop_limit` requires exactly one supported sizing mode
- supported sizing modes are `quantity` and `qty_percent`
- `stop_limit` requires `stop_price`
- `stop_limit` requires `limit_price`
- `stop_price` must be a positive finite float
- `limit_price` must be a positive finite float
- `stop_price == reference_last` is rejected as ambiguous
- `stop_price` is only valid for stop-family orders
- `trigger_condition` remains runtime-normalized, not user-provided

Runtime order validation should enforce:

- `stop_limit` requires `trigger_price`
- `stop_limit` requires `trigger_condition`
- `stop_limit` requires `trigger_type`
- `stop_limit` requires `limit_price`
- non-stop order types must not carry trigger facts
- `stop_market` continues to reject `limit_price`

## Test Coverage Expectations

The implementation plan should use
[../plans/2026-04-27-stop-limit-test-scenarios.md](../plans/2026-04-27-stop-limit-test-scenarios.md)
as the pre-implementation test-design input.

At the product-spec level, coverage must prove:

- strategy intake validates supported request shapes
- trigger direction and trigger reference follow the first-slice UX
- dormant orders cannot fill
- triggered orders execute through ordinary limit semantics
- gap-through trigger-without-fill distinguishes `stop_limit` from
  `stop_market`
- same-point trigger/fill is allowed when the trigger point is limit-marketable
- post-trigger path tails can fill, but pre-trigger path movement cannot be
  reused
- trigger-only events do not appear as public fills
- current long-only flat-sell behavior is preserved

The detailed scenario catalog should not be duplicated here. Once tests exist
under `tests/`, executable tests become the scenario-level contract.

## Implementation Guidance

The implementation should preserve existing generalization rather than add a
parallel stop-limit engine.

Expected shape:

- extend `OrderType` with `stop_limit`
- reuse direct runtime trigger fields
- keep `TriggerSpec` deferred
- keep inheritance-heavy order hierarchies deferred
- map triggered `stop_market` to executable `market`
- map triggered `stop_limit` to executable `limit`
- keep `match_order()` ignorant of bars
- teach backtest path traversal to account for both dormant stop trigger
  crossings and triggered limit crossings

Do not:

- duplicate limit matching logic for `stop_limit`
- add a backtest-only fill shortcut in `trading`
- infer stop trigger direction from side, position purpose, or limit price
- evaluate the pre-trigger path after the order becomes triggered
- add attached protective orders

## Open Decisions For Implementation Planning

These decisions should be closed in the later implementation plan, not by
changing this product meaning:

- exact internal representation of triggered `stop_limit` after trigger:
  same `Order` with `triggered_at`, unless implementation discovers a concrete
  reason that this violates existing runtime invariants
- whether decisive-event traversal needs a local helper to preserve the
  post-trigger path tail without materializing unnecessary ticks
- whether the first canonical integration contract should use a synthetic
  fixture or the existing BTC USD-M 1h 2025 fixture
- whether future venue integrations need explicit trigger references beyond
  `last`, such as mark or index price

## Acceptance Criteria

This spec is ready for implementation planning when:

1. `stop_limit` is defined as a first-class order type
2. the public strategy API is additive and explicit
3. trigger semantics are shared with `stop_market`
4. post-trigger execution semantics are shared with `limit`
5. gap-through non-execution is explicit
6. same-bar semantics are causal
7. `%` sizing and attached-order workflows are deferred
8. exchange/broker source evidence supports the product behavior
9. the test matrix is detailed enough to drive TDD
