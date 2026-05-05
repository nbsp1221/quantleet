# Order Lifecycle And Sizing Comparison

## Status

- Date: `2026-04-20`
- Status: `current`
- Authority: `advisory`
- Canonical: `no`
- Purpose:
  gather support and rebuttal evidence for the next two hard seams in
  `quantleet.trading`:
  runtime `Order` lifecycle/FSM and sizing-intent design

## Why This Document Exists

The repository already fixed the first seam:

- `OrderIntent != runtime Order`

The next questions are narrower and more practical:

- what lifecycle model should runtime `Order` follow next, especially once
  `stop-market` and `stop-limit` arrive
- what sizing-intent model should support:
  - explicit unit quantity
  - entry by percentage of available cash
  - exit by percentage of current position

This note collects support and rebuttal evidence for those questions. It is not
the design decision itself, and it should not be read as a guarantee that the
next public contract must expose these features immediately.

## Method

This note used:

- current `quantleet` code and docs
- official public docs for comparator libraries
- local source review of comparator libraries already present on the machine

To keep the repository durable, citations below prefer public docs and
repository-local files over machine-local `/tmp/...` paths.

## Current `quantleet` Truth

Today, `quantleet` still has a very small order model:

- `OrderIntent` carries only:
  - `symbol`
  - `side`
  - `quantity`
  - `order_type`
  - `limit_price?`
  - `tag?`
- `OrderType` currently allows only `market` and `limit`
- runtime `Order` exists but only tracks immutable submission terms plus
  `filled_quantity`
- matching is still a narrow function from executable order + tick to
  `FillEvent | None`
- current product scope is still single-symbol, long-only, market/limit-only
  backtest MVP

Local evidence:

- [`../../src/quantleet/trading/domain/intents.py`](../../src/quantleet/trading/domain/intents.py)
- [`../../src/quantleet/trading/domain/orders.py`](../../src/quantleet/trading/domain/orders.py)
- [`../../src/quantleet/trading/domain/matching.py`](../../src/quantleet/trading/domain/matching.py)
- [`../product-specs/backtest-mvp.md`](../product-specs/backtest-mvp.md)
- [`../product-specs/research-ergonomics.md`](../product-specs/research-ergonomics.md)
- [`../design-docs/order-runtime-model-design.md`](../design-docs/order-runtime-model-design.md)

That means the real comparison question is not “what does a complete OMS look
like,” but:

> what is the smallest correct next model that will not need to be thrown away
> when stop-family orders and percentage sizing arrive?

## Lifecycle Evidence

### Common Pattern 1: Mature engines separate request from managed order

NautilusTrader, LEAN, and backtrader all keep the strategy-facing request or
authoring surface lighter than the runtime order machinery.

This supports the existing `quantleet` seam and strengthens the case for
putting lifecycle depth onto runtime `Order`, not back onto `OrderIntent`.

Sources:

- Nautilus orders:
  https://nautilustrader.io/docs/latest/concepts/orders/
- QuantConnect order tickets:
  https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-management/order-tickets
- backtrader orders:
  https://www.backtrader.com/docu/order/

### Common Pattern 2: Stop-family orders need something beyond “open vs filled”

All of the richer comparators distinguish dormant stop orders from immediately
working orders in some way.

- Nautilus has explicit stop-family types and a rich lifecycle including
  `TRIGGERED`
- LEAN keeps stop-specific facts on order types and models trigger behavior in
  fill/order logic rather than only in a generic order request
- backtrader uses both statuses and a separate triggered flag/behavior in the
  broker layer

This is strong evidence that:

> a runtime order model that only knows “filled quantity” is not enough once
> `stop-market` and `stop-limit` arrive

But the same evidence also suggests that `triggered` does not need to become a
huge first-class lifecycle ladder by itself. It can be modeled as a fact
orthogonal to the main status axis.

Sources:

- Nautilus orders:
  https://nautilustrader.io/docs/latest/concepts/orders/
- QuantConnect stop market orders:
  https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-types/stop-market-orders
- QuantConnect stop limit orders:
  https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-types/stop-limit-orders
- backtrader orders:
  https://www.backtrader.com/docu/order/

### Common Pattern 3: Full venue-style taxonomies exist for live complexity, not for free

Nautilus and LEAN both support more lifecycle states than `quantleet` should
copy immediately:

- `submitted`
- `accepted`
- `pending_cancel`
- `pending_update`
- brokerage/exchange reconciliation semantics

Those states make sense because those engines already carry:

- live brokerage integration
- order updates and cancellations
- venue reconciliation
- richer partial-fill and event streams

This is evidence against immediately freezing a large status enum inside
`quantleet`.

Sources:

- Nautilus orders:
  https://nautilustrader.io/docs/latest/concepts/orders/
- QuantConnect order tickets:
  https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-management/order-tickets
- QuantConnect order events:
  https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-events

### Synthesis For Lifecycle

The evidence converges on:

- runtime `Order` should gain more lifecycle depth than it has now
- but `quantleet` should not jump to a full venue-style OMS taxonomy
- stop triggering should be represented explicitly
- the smallest correct answer is a kernel-local lifecycle plus stop-trigger
  facts

## Sizing Evidence

### Comparator A: `backtesting.py` overloads one `size` value

`backtesting.py` treats a single `size` parameter in two different ways:

- `0 < size < 1` means a fraction of available liquidity
- `size >= 1` means absolute units

It also uses `Position.close(portion=...)` / `Trade.close(portion=...)` for
position-relative exits.

This proves the ergonomic demand is real, but it also shows the main risk:

> overloading one float to mean both “units” and “percent” is compact but
> semantically ambiguous

Source:

- https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html

### Comparator B: `backtrader` separates cash sizing from target sizing

backtrader offers:

- explicit size-based order APIs
- separate cash-based sizers such as `PercentSizer`
- separate target-order APIs such as `order_target_percent`

This is strong evidence for keeping these concerns distinct:

- percent of available cash
- percent of portfolio value
- explicit units

They are not one thing wearing different syntax.

Sources:

- https://www.backtrader.com/docu/order/
- https://www.backtrader.com/docu/sizers-reference/
- https://www.backtrader.com/docu/order_target/order_target/

### Comparator C: LEAN and Zipline push portfolio percentages into target layers

LEAN’s `SetHoldings` and `PortfolioTarget`, and Zipline’s
`order_target_percent`, are portfolio-level constructs.

They come with important baggage:

- they depend on portfolio value / buying power semantics
- they translate weights into quantities
- they must care about open orders and ordering of reductions versus increases

Zipline explicitly warns that target APIs do not account for open orders, which
can overshoot target exposure if used naively.

This is strong evidence that:

> portfolio-target sizing is a different layer from order-intent sizing

and should not be folded into the next `quantleet` order slice.

Sources:

- QuantConnect position sizing:
  https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/position-sizing
- Zipline API:
  https://zipline.ml4trading.io/api-reference.html

### Comparator D: Freqtrade is stake-centric, not order-intent-centric

Freqtrade uses wallet-aware stake sizing with:

- fixed `stake_amount`
- dynamic `stake_amount = "unlimited"`
- strategy callback overrides such as `custom_stake_amount`

This is useful evidence for compounding and available-balance-aware entries,
but it also shows the downside of stake-centric design:

- it is harder to map cleanly back to reusable order-intent semantics
- partial exits become strategy/bot-specific math instead of a small general
  contract

Sources:

- Freqtrade configuration:
  https://www.freqtrade.io/en/stable/configuration/
- Freqtrade strategy callbacks:
  https://docs.freqtrade.io/en/latest/strategy-callbacks/
- Freqtrade backtesting:
  https://www.freqtrade.io/en/stable/backtesting/

### Synthesis For Sizing

The evidence converges on three points.

1. Comparator libraries repeatedly need percentage-based sizing semantics.
2. Overloading one raw float is too ambiguous for a long-lived shared kernel.
3. Portfolio-target sizing should remain deferred until portfolio/equity and
   open-order reservation semantics become first-class.

That leaves a narrow preferred direction:

- runtime `Order` stays quantity-based
- if percentage-based sizing is later introduced, it should resolve to concrete
  quantity outside runtime `Order`
- the first useful percentage bases are likely:
  - entry as fraction of available cash / buying power
  - exit as fraction of current position quantity

## Strongest Rebuttal Evidence

The strongest objections found were:

1. A rich lifecycle enum now would be fake precision because current shipped
   `quantleet` does not yet have:
   - stop-family orders
   - cancel/replace
   - paper/live execution events
   - user-visible partial-fill behavior
2. A single “beautiful” sizing abstraction now would be overreach because
   current strategy state still does not expose:
   - cash
   - equity
   - portfolio value
   - open-order reservations
3. Target-percent APIs can look attractive too early and smuggle portfolio
   control into the order layer.

Those objections are valid, and they narrow the design space sharply.

## Narrowest Still-Correct Recommendation

### Lifecycle

Do **not** adopt a large venue-style status taxonomy yet.

Prefer only the narrower principle that the next lifecycle model must:

- distinguish dormant stop orders from executable orders
- represent stop-trigger facts explicitly
- remain kernel-local rather than venue-shaped

### Sizing

Do **not** overload the existing `quantity: float` field to mean both units and
percentages.

Prefer a future separate sizing layer, but keep the recommendation narrow:

- explicit units remain the current truth
- available-cash fraction is the best candidate basis for entry/increase
- current-position fraction is the best candidate basis for reduce/exit

Defer:

- portfolio-target percent
- portfolio value / equity-based target sizing
- open-order-aware rebalancing

## What This Research Does Not Decide

This note does **not** settle:

- the exact runtime `Order` lifecycle field layout
- whether the lifecycle should use one enum or one enum plus terminal facts
- the exact names of sizing-intent variants
- the public strategy API syntax for percentage sizing

Those belong in the design doc.

## One-Line Summary

The evidence supports two narrow next steps:

- a small kernel-local `Order` lifecycle with explicit stop-trigger facts
- a separate typed sizing-intent layer that resolves to concrete quantity

and it rejects both extremes:

- a full live-style OMS taxonomy now
- a magic overloaded `quantity` float that tries to mean everything
