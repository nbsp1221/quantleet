# Order Sizing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.
>
> This is an implementation-planning artifact, not the active workflow
> authority for the current docs-only slice. A later active Tier A plan must
> adopt or narrow this plan before code changes begin.
>
> Execution gate:
> do not implement directly from this file. First create a fresh active Tier A
> implementation plan with the required approval record, evaluator contract,
> governing-doc list, and final verification set.

**Goal:** Add the first shipped `qty_percent` strategy-sizing path without
breaking the current quantity-based order kernel or widening the MVP into
portfolio-target behavior.

**Architecture:** Keep raw percentage sizing out of `trading.domain` runtime
objects. Let `research` own strategy-facing ergonomics, let one neutral shared
pending-request contract plus one canonical shared sizing policy live outside
`trading.domain`, and resolve percent requests into concrete quantity using
runtime-supplied state and price anchors. Keep `OrderIntent` plus runtime
`Order` quantity-based. Backtest runtime should remain the owner of activation
timing and executable-price context.

**Tech Stack:** Python 3.13, `uv`, Poe tasks, `pytest`, `quantleet.research`,
`quantleet.backtest`, `quantleet.trading`, structure-doc checks

---

- Date: `2026-04-22`
- Task: `Plan the first explicit qty_percent implementation slice`
- Status: `draft`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Why This Slice

The approved product direction is already frozen in
[`../product-specs/order-sizing.md`](../product-specs/order-sizing.md):

- `buy(qty_percent=...)` means percent of reserved-adjusted quote cash as
  requested position budget, with fee-aware affordability clamping
- `sell(qty_percent=...)` means percent of net closable position quantity
- runtime `Order` must stay quantity-based
- `target_percent`, rebalance, leverage, and default top-level strategy sizing
  remain deferred

Current repo truth is still narrower:

- [`../../src/quantleet/research/strategy.py`](../../src/quantleet/research/strategy.py)
  only accepts `quantity`
- [`../../src/quantleet/trading/domain/intents.py`](../../src/quantleet/trading/domain/intents.py)
  is quantity-only
- [`../../src/quantleet/trading/domain/orders.py`](../../src/quantleet/trading/domain/orders.py)
  is quantity-only
- [`../../src/quantleet/backtest/strategy_runtime.py`](../../src/quantleet/backtest/strategy_runtime.py)
  currently activates pending `OrderIntent` objects directly into runtime
  `Order`

So the implementation work is not "add one extra argument." The real change is:

> introduce a strategy-facing sizing-request seam, add one shared percent
> sizing policy, and resolve percent requests into concrete quantity at runtime
> activation without polluting the trading kernel.

## Why Not Broader Alternatives

### Why not overload `quantity`

The governing spec and sizing design already reject that path:

- [`../product-specs/order-sizing.md`](../product-specs/order-sizing.md)
- [`../design-docs/order-lifecycle-and-sizing-design.md`](../design-docs/order-lifecycle-and-sizing-design.md)

Do not copy the `backtesting.py` pattern where one numeric field means either
units or fraction depending on magnitude. That would make validation,
debugging, and future stop-family/runtime work harder.

### Why not add raw percent fields to `OrderIntent` or runtime `Order`

That would blur the boundary the spec intentionally protects. `qty_percent` is
a strategy-layer budget instruction, not the downstream runtime-order truth.
Keeping `OrderIntent` and `Order` quantity-based preserves the shared-kernel
direction and avoids leaking portfolio-like semantics into `trading.domain`.

### Why not ship target-percent in the same slice

`target_percent` would reopen:

- portfolio value basis
- sell-before-buy ordering
- open-order-aware target reconciliation
- multi-symbol allocation

That is a separate control-layer problem and should stay deferred.

## Slice Boundaries

### In Scope

- additive strategy-facing `qty_percent` support on `buy(...)` and `sell(...)`
- one neutral shared pending request shape that can represent either
  `quantity` or `qty_percent`
- one canonical shared sizing policy that resolves percent requests into
  quantity using supplied runtime state, reservations, affordability checks,
  and price anchors
- backtest runtime activation support for:
  - reservation-aware buy sizing
  - reservation-aware sell sizing
  - same-cycle serial resolution
  - market-versus-limit buy anchors
- additive doc and quickstart updates after code behavior is shipped
- tests required to freeze the new semantics

### Out Of Scope

- `target_percent`
- `target_value`
- rebalance optimizers
- leverage or buying-power semantics
- quote-notional as a public user-facing contract
- stop-family orders
- shorting
- multi-symbol allocation
- live or paper runtime implementation

## Pre-Implementation Guardrails

Before code changes begin, the future active implementation plan must include:

- a fresh Tier A implementation approval record
- explicit note that the slice changes public strategy behavior additively
- explicit note that `OrderIntent` and runtime `Order` remain quantity-based
- explicit note that target and leverage semantics remain deferred

The later code slice must not be treated as approved just because this plan
exists.

## Recommended Internal Shape

The smallest coherent internal shape is:

1. `Strategy.buy/sell()` accept either `quantity` or `qty_percent`
2. `research` stores pending strategy requests in a neutral shared request type
   that both `research` and `backtest` may depend on without creating a
   `backtest -> research` dependency
3. backtest activation passes each pending request through a shared sizing
   policy using:
   - current `TradingState`
   - currently active runtime orders
   - order-type-specific buy price anchor
   - instrument constraints and current cost model
4. the resolver produces a concrete quantity or a deliberate no-op
5. only then does the runtime create quantity-only `OrderIntent` and `Order`

The key ownership rule is:

- `research` owns authoring ergonomics and intake validation
- the cross-runtime pending request contract must live in a neutral support
  layer rather than inside `research`
- `trading` owns quantity-only runtime order and fill semantics
- `backtest` owns activation timing plus executable-price context

## Planned Implementation Slices

### Task 1: Freeze The New Public UX And Kernel Boundary In Tests

**Files:**
- Modify: `tests/unit/research/test_strategy_surface.py`
- Modify: `tests/unit/trading/test_contracts.py`
- Modify: `tests/unit/trading/test_orders.py`
- Create: `tests/unit/trading/test_sizing.py`
- Create: `tests/integration/research/test_order_sizing_contract.py`

**Intent:**
- Lock the additive public API and the non-negotiable architectural seam before
  production edits.

**Contract to freeze:**
- `buy(...)` and `sell(...)` accept exactly one sizing mode:
  `quantity` or `qty_percent`
- `buy(...)` and `sell(...)` expose an explicit additive call signature for
  `qty_percent` without weakening the current `quantity` path
- `tests/unit/research/test_strategy_surface.py` should lock those public order
  method signatures explicitly rather than relying only on behavioral cases
- `qty_percent` is validated as numeric and `0 < qty_percent <= 100`
- invalid or mixed sizing requests fail explicitly
- `OrderIntent` remains quantity-only and does not gain raw percent fields
- runtime `Order` remains quantity-only
- runtime `Order` field surface is locked explicitly enough that adding a raw
  `qty_percent` field would fail the contract tests
- implicit-symbol `qty_percent` orders still inherit the active bar symbol in
  the current single-symbol `on_bar()` path
- flat `sell(qty_percent=...)` remains an exit-only no-op under current
  long-only behavior

**Why tests first:**
- This slice changes public strategy ergonomics and Tier A runtime semantics.
  Freezing the boundary in tests first prevents accidental widening during the
  implementation.

### Task 2: Introduce A Neutral Shared Pending Request Shape

**Files:**
- Create: `src/quantleet/trading/order_requests.py`
- Modify: `src/quantleet/research/strategy.py`
- Modify: `src/quantleet/backtest/strategy_runtime.py`
- Modify: `tests/unit/research/test_strategy_surface.py`

**Intent:**
- Stop treating raw `OrderIntent` as the only pending order-shaped object.

**Recommended change:**
- add a neutral shared dataclass such as `PendingOrderRequest` that holds:
  - `symbol`
  - `side`
  - `order_type`
  - exactly one of `quantity` or `qty_percent`
  - `limit_price`
  - `tag`
- place that type outside `trading.domain` so runtime-order models stay small,
  but keep it in a package that both `research` and `backtest` may import
  without violating the current architecture direction
- update `Strategy._pending_order_intents` to a request collection backed by
  that neutral shared contract rather than by `OrderIntent`
- keep `Strategy` validation at intake time narrow:
  - callback-only guard remains
  - limit orders still require `limit_price`
  - sizing mode validation remains explicit

**Explicitly avoid:**
- exporting the request type as public trading-kernel API
- placing the request type inside `research`, which would force
  `backtest -> research` coupling during activation
- adding `qty_percent` to `OrderIntent`
- hiding invalid mixed sizing behind silent precedence rules

### Task 3: Add One Canonical Shared Percent-Sizing Policy

**Files:**
- Create: `src/quantleet/trading/sizing.py`
- Modify: `tests/unit/trading/test_sizing.py`

**Intent:**
- Centralize percent-resolution semantics in one pure helper layer without
  putting raw percent fields into runtime orders.

**Recommended direction:**
- keep this policy outside `trading.domain` so runtime-order models stay small
- keep it internal in this slice rather than exporting it from the public
  `quantleet.trading` facade
- design the policy to consume neutral inputs supplied by the runtime, such as:
  - side
  - requested percent
  - order type
  - current state
  - active runtime orders
  - price anchor
  - fee model inputs
  - quantity increment / minimum quantity / minimum notional constraints
- have the policy return a resolved quantity or an explicit no-op result with a
  reason

**Required behaviors to freeze in unit tests:**
- buy percent first computes a requested position budget from reserved-adjusted
  quote cash
- active unresolved buy orders reduce that quote-cash basis via remaining
  reserved spend
- if requested budget plus modeled fees is affordable, the resolver preserves
  the requested position budget exactly
- if requested budget plus modeled fees is not affordable, the resolver clamps
  down to the maximum affordable position budget without a `100%` special case
- sell percent uses net closable quantity
- active unresolved sell orders reduce net closable quantity via remaining exit
  reservation
- reservation math tracks unresolved remainder, not original submitted size
- sub-minimum or unaffordable results resolve to a deliberate no-op rather than
  an over-allocated quantity

### Task 4: Teach Backtest Activation To Resolve Percent Requests Serially

**Files:**
- Modify: `src/quantleet/backtest/runtime.py`
- Modify: `src/quantleet/backtest/strategy_runtime.py`
- Modify: `src/quantleet/backtest/order_activation.py`
- Possibly create: `src/quantleet/backtest/order_sizing.py`
- Modify: `tests/unit/backtest/test_order_activation_policy.py`
- Create: `tests/unit/backtest/test_order_sizing_activation.py`

**Intent:**
- Move percent resolution to the runtime activation moment where state,
  active-order reservations, and current-bar price anchors are known.

**Recommended direction:**
- do not let `Strategy._handle_bar()` resolve `qty_percent`
- let backtest runtime activate each pending request at the start of the next
  bar using the current activation context
- resolve pending requests serially in emission order
- after each accepted request, update the reservation view before resolving the
  next request in the same cycle

**Backtest-specific rules to freeze:**
- `market` buy percent uses the current bar's first executable buy-side
  reference price under the conservative execution model to determine
  affordability and concrete quantity
- `limit` buy percent uses submitted `limit_price` as affordability anchor
- sell percent uses current position minus unresolved exit reservations
- no retroactive same-bar activation is introduced

### Task 5: Preserve Quantity-Only Order Creation And Matching

**Files:**
- Modify: `src/quantleet/trading/domain/intents.py` only if helper APIs or
  constructor ergonomics need minimal additive support; otherwise keep it
  unchanged
- Modify: `src/quantleet/trading/domain/orders.py` only if creation helpers
  need to better support resolved intent creation; otherwise keep it unchanged
- Modify: `tests/unit/trading/test_orders.py` only if helper coverage needs a
  small additive test

**Intent:**
- Keep percent semantics outside the runtime order kernel even after the new
  strategy UX ships.

**Default recommendation:**
- prefer leaving `OrderIntent` and `Order` unchanged
- only touch these files if the code shape becomes noticeably worse without a
  small helper extraction

This task exists mainly as a guardrail:

- if the implementation starts drifting toward raw percent fields in
  `trading.domain`, stop and narrow the slice

### Task 6: Add End-To-End Backtest Contracts For The Shipped UX

**Files:**
- Modify: `tests/integration/research/test_order_sizing_contract.py`
- Modify: `tests/integration/research/support_backtest_runner.py`
- Possibly modify: `tests/support_backtest.py`

**Intent:**
- Prove the shipped user-visible behavior, not just the internal resolver.

**Scenarios to cover:**
- `buy(qty_percent=80)` on the first eligible bar creates an entry sized from
  reserved-adjusted available cash without overspending after fees
- `buy(qty_percent=50)` preserves the requested 50%-of-basis position budget
  when fees remain separately affordable
- `buy(qty_percent=100)` clamps to the maximum affordable position budget when
  fees or execution costs would otherwise over-allocate cash
- `sell(qty_percent=30)` reduces only a portion of the open position
- repeated percent orders in one callback resolve sequentially instead of each
  seeing gross resources
- resting exit reservations reduce the closable basis for later exits
- flat percent sells remain no-op exits under long-only semantics
- limit-buy percent sizing uses `limit_price`, not a more optimistic current
  mark

### Task 7: Sync Docs And Examples Last

**Files:**
- Modify: `docs/product-specs/research-ergonomics.md`
- Modify: `docs/product-specs/backtest-mvp.md` only if shipped scope wording
  changes are required
- Modify: `docs/product-specs/order-sizing.md` if implementation narrows a
  draft-only ambiguity into shipped wording
- Modify: `docs/product-specs/index.md`
- Modify: `tests/structure/docs/test_system_of_record_docs.py`
- Modify: `tests/structure/docs/test_research_ergonomics_quickstart.py`
- Modify: `tests/structure/repo/test_index_status_maps.py`
- Modify: `tests/structure/repo/test_repository_entrypoint_docs.py`
- Modify: relevant quickstart/notebook/example assets if they are intentionally
  upgraded to show `qty_percent`

**Intent:**
- Update system-of-record docs only after code behavior and tests are already
  green.

**Doc sync rule:**
- do not silently rewrite old quantity examples unless the public quickstart is
  intentionally updated to demonstrate the new capability
- preserve current quantity-based examples where they still serve as the
  canonical minimal path
- if the slice becomes shipped behavior, promote the routing row for
  `order-sizing.md` out of `Future-only` and add a structure test that locks
  the new index status
- if the slice becomes shipped behavior, update `docs/product-specs/order-sizing.md`
  so its status and surrounding system-of-record tests no longer describe it as
  a future-only draft

## Verification Plan

During implementation:

- focused unit tests for strategy intake validation
- focused unit tests for the new sizing policy
- focused unit tests for activation-time serial reservation behavior
- focused integration tests for end-to-end backtest percent sizing

Before closing the code slice:

- run the focused new unit and integration tests first so semantic failures are
  easy to localize while the slice is still moving
- `uv run poe verify-runtime`

If runtime-sensitive performance changes appear during activation-path work,
no extra lane is needed beyond `verify-runtime`, because that command already
includes the default verification bundle plus `perf-check`.

If the implementation deliberately changes docs, examples, or notebooks beyond
what `verify-runtime` already covers, the future active code slice may still
run:

- `uv run poe repo-check`

## Explicit Risks To Watch

- leaking raw percent semantics into `trading.domain`
- using gross cash or gross position instead of reservation-aware bases
- forgetting that reservations must track remaining unresolved size rather than
  original order size
- resolving market-buy percent sizing before the runtime has the correct next
  bar activation context
- letting docs imply `target_percent` or leverage-aware semantics were shipped

## One-Line Summary

Implement `qty_percent` by adding a neutral shared pending-request layer plus one
shared percent-sizing policy, then resolve those requests into quantity at
backtest activation time so the trading kernel stays quantity-based and the new
user-facing behavior remains deterministic.
