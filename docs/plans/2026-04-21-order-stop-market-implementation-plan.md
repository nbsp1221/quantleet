# Order Stop-Market Implementation Plan

> This is an implementation-planning artifact, not the active workflow
> authority for the current docs-only planning slice. A later active plan must
> adopt or narrow this plan before code changes begin.
>
> Execution gate:
> do not implement directly from this file. First create a fresh active Tier A
> plan with the required approval record, evaluator contract, governing-doc
> list, and final verification set.

**Goal:** Add the first trigger-aware runtime `Order` behavior and shipped
`stop_market` backtest support without widening the kernel into full OMS or
percentage-sizing work.

**Architecture:** Keep `OrderIntent` as the strategy-facing request object and
runtime `Order` as the kernel truth. Add a minimal dormant-versus-executable
contract to `Order`, keep trigger detection in `matching`, keep canonical path
construction in `backtest`, and keep fill-driven accounting unchanged. Ship
`stop_market` end-to-end only after the exact trigger contract is frozen in
tests; defer `stop_limit` and all sizing work.

**Tech Stack:** Python 3.13, `uv`, Poe tasks, `pytest`, `quantcraft.trading`,
`quantcraft.backtest`, and `quantcraft.research`

---

- Date: `2026-04-21`
- Task: `Plan the next Order implementation slice`
- Status: `draft`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Why This Slice

Current `quantcraft` already has a real runtime `Order`, but it only knows
market/limit fills:

- [`src/quantcraft/trading/domain/orders.py`](../../src/quantcraft/trading/domain/orders.py)
- [`src/quantcraft/trading/domain/matching.py`](../../src/quantcraft/trading/domain/matching.py)
- [`src/quantcraft/backtest/runtime.py`](../../src/quantcraft/backtest/runtime.py)

Existing draft research/design work is advisory only, but it consistently
pointed to three constraints that still fit current repo truth:

1. runtime `Order` should become trigger-aware before it grows into a larger OMS
2. runtime `Order` must stay quantity-based
3. percentage sizing must stay out of this slice

Those advisory conclusions live in:

- [`../design-docs/order-runtime-model-design.md`](../design-docs/order-runtime-model-design.md)
- [`../design-docs/order-lifecycle-and-sizing-design.md`](../design-docs/order-lifecycle-and-sizing-design.md)

The best next code slice is therefore **not**:

- full stop-family support
- stop-limit support
- percentage sizing
- public UX cleanup such as symbol inference

The best next slice is:

> freeze the exact minimal stop-market contract in tests, implement
> `stop_market` end-to-end in the backtest kernel, run full verification, and
> sync governing/product docs last

That is small enough to stay legible and large enough to unlock real strategy
work.

## Why Not Broader Alternatives

### Why not “trigger groundwork only”

That phrase is too vague. The repo would still have to guess:

- how a dormant order is represented
- how trigger facts are stored
- whether trigger detection changes the matcher contract
- what gap and intrabar trigger semantics are

This plan avoids that ambiguity by making the first step a contract-freezing
test slice, then shipping one concrete user-visible behavior: `stop_market`,
and only then syncing governing/product docs to the shipped result.

### Why not `stop_market` and `stop_limit` together

`stop_limit` still needs unresolved semantics:

- gap-through handling
- post-trigger tail evaluation
- when the newly-triggered limit is allowed to match in the same bar

Those are explicitly still open in the draft docs. Mixing them into the first
trigger-aware slice would reopen too many decisions at once.

### Why not percentage sizing now

Percentage sizing is a separate seam:

- it needs account-state and resolver semantics
- the draft direction explicitly says it must not overload `quantity`
- it does not unblock the stop-trigger kernel contract

## Slice Boundaries

### In Scope

- exact minimal trigger contract for runtime `Order`
- `stop_market` support in `OrderIntent`, runtime `Order`, matching, and
  backtest runtime
- backtest semantics for:
  - gap trigger at `open`
  - intrabar trigger on the canonical path
  - no lookahead / no retroactive same-bar activation
- additive strategy-facing support for `stop_market`
- documentation sync after the new shipped behavior exists
- tests required for the new shipped behavior

### Out Of Scope

- `stop_limit`
- trailing stop
- cancel / replace / reject / expire workflows
- full OMS status taxonomy
- portfolio or ledger work
- percentage sizing
- symbol-inference UX cleanup
- paper or live runtime work

## Pre-Implementation Guardrails

Before code changes begin, the active implementation plan must include:

- a fresh Tier A implementation approval record
- explicit note that this slice changes public strategy behavior additively
- explicit note that `stop_limit` and sizing remain deferred

The later code slice must not be treated as approved just because this plan
exists.

## Planned Implementation Slices

### Task 1: Freeze The Existing Governing Backtest Boundary Before Code

**Files:**
- No durable repo edits in this task.

**Intent:**
- Start the future code slice from the current governing
  `backtest-execution-semantics.md` boundary without editing it before
  `stop_market` behavior actually ships.

**Required gate:**
- the fresh active implementation plan must cite
  `docs/design-docs/backtest-execution-semantics.md` as governing
- the future implementer must treat canonical path, conservative executable
  prices, and matching-boundary rules as hard constraints while writing the
  failing tests in Task 2
- no governing-doc promotion happens until the shipped behavior exists and the
  full verification set passes

### Task 2: Freeze The Exact Stop-Market Contract In Tests

**Files:**
- Modify: `tests/unit/trading/test_orders.py`
- Modify: `tests/unit/trading/test_matching_and_state.py`
- Modify: `tests/unit/backtest/test_execution_model.py`
- Modify: `tests/integration/research/test_backtest_execution_semantics.py`
- Modify: `tests/unit/trading/test_contracts.py`
- Modify: `tests/unit/research/test_strategy_surface.py`

**Intent:**
- Turn the current “trigger-aware direction” into one concrete contract before
  production code changes.

**Contract to freeze, split by boundary:**

Kernel-local contract:
- `stop_market` orders are dormant before trigger
- dormant stop orders cannot fill
- buy `stop_market` triggers when price reaches or exceeds `stop_price`
- sell `stop_market` triggers when price reaches or falls below `stop_price`
- `stop_market` requires `stop_price`
- non-stop orders forbid `stop_price`
- `stop_market` forbids `limit_price`

Backtest/runtime contract:
- gap-through `stop_market` triggers at `open`, because `open` is the first
  executable point after the gap
- any active `stop_market` already crossed at `open` also triggers at `open`,
  because `open` is the first executable price of the new bar regardless of
  whether the crossing came from a true gap
- intrabar `stop_market` triggers at an order-aware decisive stop-crossing tick
  emitted at the stop price as an outcome-equivalent compression of the
  canonical path
- a triggered `stop_market` executes through the ordinary market-fill path on
  that same decisive tick/open, including normal market slippage
- orders created from `on_bar` still activate on the next bar only
- no retroactive fill or trigger inside the bar that created the order
- `sell(..., order_type="stop_market")` remains exit-only and is a no-op while
  flat
- newly triggered stops do not overtake previously active orders on the same
  tick; existing active-order priority remains intact via a two-phase per-tick
  rule: already-executable active orders run first, then newly-triggered stops
  join the same tick after them
- within the newly-triggered phase, stop-market orders preserve existing
  working-order / order-id order

**Why tests come first:**
- This is the narrowest way to resolve the remaining ambiguity without
  smuggling semantic guesses into code.

### Task 3: Extend The Public Request Shape Additively For `stop_market`

**Files:**
- Modify: `src/quantcraft/trading/domain/intents.py`
- Modify: `src/quantcraft/research/strategy.py`
- Modify: `tests/unit/trading/test_contracts.py`
- Modify: `tests/unit/research/test_strategy_surface.py`

**Intent:**
- Add only the minimum request shape needed to express `stop_market`.

**Recommended change:**
- extend `OrderType` to include `\"stop_market\"`
- add `stop_price: float | None`
- keep `quantity` semantics unchanged
- do not add `stop_limit`, percentage sizing, or a second API path

**Rules:**
- this must be additive
- existing `market`/`limit` behavior must not change
- existing quantity-based strategy calls must remain valid
- exit-only long/flat semantics must remain intact for `sell(...)`

### Task 4: Promote Runtime `Order` To A Minimal Trigger-Aware Aggregate

**Files:**
- Modify: `src/quantcraft/trading/domain/orders.py`
- Modify: `tests/unit/trading/test_orders.py`

**Intent:**
- Make runtime `Order` capable of representing dormant and triggered
  stop-market orders without inventing a large status enum.

**Recommended fields and behavior:**
- add `stop_price: float | None`
- add `triggered_at: int | None`
- optionally add `triggered_price: float | None` if needed by the frozen test
  contract
- add a derived notion of executability
- add `trigger(...)`
- keep `apply_fill(...)`
- reject fill application before trigger on dormant stop orders

**Explicitly avoid:**
- `SUBMITTED`, `ACCEPTED`, `PENDING_CANCEL`, or similar OMS statuses
- portfolio or account semantics
- flat/oversell/cash legality; those stay in runtime and `TradingState`

### Task 5: Keep Matching Pure By Splitting Trigger Detection From Fill Matching

**Files:**
- Modify: `src/quantcraft/trading/domain/matching.py`
- Modify: `tests/unit/trading/test_matching_and_state.py`

**Intent:**
- Keep `matching` as market-fact calculation, not a stateful order manager.

**Recommended direction:**
- keep `match_order(...) -> FillEvent | None` for executable orders
- add a narrow trigger-detection helper for stop-market orders
- make the triggered `stop_market` execute through the existing market-order
  fill path rather than through a new bespoke matcher path
- consume the stop-crossing decisive tick from `execution_model` rather than
  inventing a second stop-only execution channel in `runtime`
- let the runtime loop own event ordering explicitly:
  1. execute already-executable active orders
  2. evaluate dormant-stop trigger facts
  3. apply `Order.trigger(...)`
  4. run the same-tick market-fill pass for the just-triggered stop-market
     orders

**Why:**
- this preserves the existing matcher contract for market/limit orders
- it avoids forcing one function to return both trigger and fill events in the
  first slice

### Task 6: Teach The Backtest Runtime And Execution Model The New Trigger Path

**Files:**
- Modify: `src/quantcraft/backtest/execution_model.py`
- Modify: `src/quantcraft/backtest/runtime.py`
- Modify: `src/quantcraft/backtest/strategy_runtime.py`

**Intent:**
- Make the backtest path produce correct stop-market trigger/fill behavior
  while preserving the governing backtest boundary.

**Required outcome:**
- `execution_model` remains the owner of canonical path traversal
- `trading` remains the owner of trigger/fill fact evaluation
- `runtime` orders the sequence deterministically
- `execution_model` must stay on the canonical gap + intrabar path and expose
  order-aware decisive stop-crossing ticks at the stop price only as an
  outcome-equivalent compression of that path, parallel to the current
  resting-limit crossing ticks
- runtime must validate `Order.trigger(...)` / `Order.apply_fill(...)` before
  letting any `FillEvent` reach accounting
- runtime must preserve the current active-order priority when a stop triggers
  on the same tick as other already-active orders by using a two-phase per-tick
  pass: execute already-executable orders first, then append just-triggered
  stop-market orders to the same tick's market-fill pass

**Key semantics to preserve:**
- gap segment stays separate from intrabar movement
- `open` remains the first executable price of the bar for already-crossed
  stop-market orders, with no pre-open synthetic stop tick
- no intermediate executable prices inside a gap
- no same-bar retroactive activation from `on_bar`

### Task 7: Keep Accounting Fill-Driven

**Files:**
- Modify only if necessary:
  - `src/quantcraft/trading/domain/state.py`
  - result-surface tests

**Intent:**
- Preserve `FillEvent -> TradingState` as the accounting handoff.

**Rule:**
- trigger facts must not become a second accounting path
- only fills change cash, position quantity, and PnL
- order-local legality must be checked before `TradingState` sees the fill
- flat/oversell/cash rejection stays in runtime and `TradingState`, not in
  `Order`

### Task 8: Documentation And Contract Sync

**Files:**
- Modify: `docs/product-specs/backtest-mvp.md`
- Modify: `docs/product-specs/research-ergonomics.md`
- Modify: `docs/design-docs/backtest-execution-semantics.md`
- Optionally modify:
  - `docs/design-docs/order-runtime-model-design.md`
  - `docs/design-docs/order-lifecycle-and-sizing-design.md`

**Intent:**
- Keep the docs aligned with what the code actually ships.

**Important constraint:**
- the code slice does not close until the product specs match the shipped
  `stop_market` behavior and current public strategy contract
- `docs/design-docs/backtest-execution-semantics.md` only updates once the
  shipped `stop_market` behavior and full verification evidence exist
- only sync docs to the shipped `stop_market` behavior in this slice
- if draft order docs are updated, they should only align pointers or note what
  remains deferred after the shipped stop-market slice
- do not sneak in `stop_limit` or sizing guidance as if implemented

## Verification Plan

### Focused Test Lane

Run first:

```bash
uv run pytest -q \
  tests/unit/trading/test_orders.py \
  tests/unit/trading/test_matching_and_state.py \
  tests/unit/trading/test_contracts.py \
  tests/unit/research/test_strategy_surface.py \
  tests/unit/backtest/test_execution_model.py \
  tests/integration/research/test_backtest_execution_semantics.py
```

### Required Full Verification

Before closing the code slice:

```bash
uv run poe verify
uv run poe verify-runtime
uv run poe perf-check
uv run poe coverage
uv run poe repo-check
```

## Risk Register

### Main Risks

1. **Over-modeling lifecycle**
   - Mitigation:
     keep trigger facts small and avoid a full status enum.

2. **Leaking backtest timing into `trading`**
   - Mitigation:
     keep gap/tail/activation ordering in `backtest` runtime and execution
     model.

3. **Changing strategy behavior too broadly**
   - Mitigation:
     additive `stop_market` only; no symbol UX or sizing changes in this
     slice.

4. **Smuggling `stop_limit` into the first trigger slice**
   - Mitigation:
     explicit defer below plus contract tests.

## Explicit Defers

- `stop_limit`
- trailing stop
- percentage sizing
- `quantity` overloads
- public portfolio-target APIs
- cancel / replace / reject / expire flows
- paper/live execution events

## Follow-Up Slice After This One

If this slice lands cleanly, the next plan should choose between:

1. `stop_limit` semantics
2. separate sizing resolver groundwork
3. public strategy UX cleanup such as symbol inference

Do **not** decide those in the same code change.

## One-Line Summary

The next code slice should stop being vague about “groundwork” and instead ship
one concrete behavior: a trigger-aware runtime `Order` plus end-to-end
`stop_market` backtest support, while explicitly deferring `stop_limit` and all
sizing work.
