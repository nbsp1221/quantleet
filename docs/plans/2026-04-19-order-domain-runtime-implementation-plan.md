# Order-Domain Runtime Implementation Plan

> This is an implementation-planning artifact, not the active workflow
> authority for the current docs-only slice. A later active plan must adopt or
> narrow this plan before code changes begin.

**Goal:** Introduce the first runtime `Order` seam inside `quantcraft.trading`
without breaking current market/limit behavior or collapsing the shared-kernel
boundary into backtest-specific logic.

**Architecture:** Keep `OrderIntent` as the strategy-facing request shape.
Add a minimal runtime `Order` aggregate in `trading`, keep market-data
interpretation in `matching`, keep fill application in the current trading
state path, and migrate backtest runtime orchestration away from using raw
`OrderIntent` as fake runtime order truth. Keep the core loop ordered and
deterministic rather than introducing a free-form async event mesh.

**Tech Stack:** Python 3.13, `uv`, `pytest`, Poe tasks, current
`quantcraft.trading`, `quantcraft.backtest`, and `quantcraft.research`
packages

---

- Date: `2026-04-19`
- Task: `Plan the first runtime Order implementation slice`
- Status: `draft`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Harness Expectations

This plan follows the repository-local harness protocol:

- humans steer and approve scope
- agents execute within repository-local docs and checks
- `AGENTS.md` and the active plan remain the workflow authority
- research notes are advisory only
- draft design docs guide boundaries but do not override current product specs
- implementation should preserve repository legibility rather than hiding
  rationale in chat-only context

## Handoff Contract

Scope:
- Introduce the first runtime `Order` model and migrate the backtest runtime to
  manage orders rather than raw order intents.
- Keep the current shipped strategy API and current market/limit semantics
  compatible.
- Leave trigger-aware stop-order behavior for a later slice while keeping the
  runtime seam from collapsing back into `OrderIntent`.

Owner:
- One writer operating primarily in:
  - `src/quantcraft/trading/domain/*`
  - `src/quantcraft/backtest/*`
  - affected tests and docs

Acceptance criteria:
- `OrderIntent` remains the strategy output.
- A new runtime `Order` object exists in `trading`.
- Backtest runtime no longer treats raw `OrderIntent` as the closest thing to a
  managed order.
- Matching remains in `trading` and backtest stays responsible for historical
  path approximation.
- Existing market/limit behavior remains intact under current runtime tests.
- The first slice does not ship stop-market or stop-limit support.

Evidence required:
- Focused unit tests for runtime order transitions and invariants.
- Updated runtime integration tests proving current market/limit behavior is
  preserved after the internal refactor.
- Fresh `uv run poe verify-runtime`
- Fresh `uv run poe repo-check`

Next-step note:
- Implement the smallest order seam first. Do not mix in portfolio, allocator,
  risk engine, or paper/live runtime work.

## Current-State Analysis

The current repository has three relevant constraints:

1. `OrderIntent` is the only first-class order-shaped object today.
2. Active and pending order state currently live in strategy/runtime
   orchestration rather than in a trading-owned runtime object.
3. `trading` is already the approved owner of core trading semantics, while
   `backtest` should stay a historical-runtime adapter rather than absorbing
   order meaning.

Concrete local evidence:

- [`../../src/quantcraft/trading/domain/intents.py`](../../src/quantcraft/trading/domain/intents.py)
- [`../../src/quantcraft/trading/domain/matching.py`](../../src/quantcraft/trading/domain/matching.py)
- [`../../src/quantcraft/backtest/strategy_runtime.py`](../../src/quantcraft/backtest/strategy_runtime.py)
- [`../../src/quantcraft/backtest/runtime.py`](../../src/quantcraft/backtest/runtime.py)
- [`../../docs/design-docs/order-domain-runtime-design.md`](../../docs/design-docs/order-domain-runtime-design.md)

## Planned Implementation Slices

### Task 1: Freeze The New Boundary In Tests

**Files:**
- Create: `tests/unit/trading/test_orders.py`
- Modify: `tests/unit/trading/test_matching_and_state.py`
- Modify: `tests/integration/research/test_backtest_execution_semantics.py`
- Modify: any minimal test helpers required by the backtest runtime

**Intent:**
- Lock the contract that `OrderIntent` remains a request object and runtime
  `Order` becomes a distinct managed object.
- Freeze the minimum behaviors the new `Order` must own:
  - creation from accepted intent
  - working/open state
  - fill application legality
  - terminal completion on full fill

**Example checks to add:**
- creating a runtime `Order` from a `market` or `limit` intent preserves symbol,
  side, quantity, and family semantics
- `Order.apply_fill(...)` updates remaining quantity and rejects illegal fills
- a terminal order cannot be filled again
- the backtest runtime still produces the same market/limit integration results
  after the internal refactor

### Task 2: Add `trading.domain.orders`

**Files:**
- Create: `src/quantcraft/trading/domain/orders.py`
- Modify: `src/quantcraft/trading/domain/__init__.py`

**Intent:**
- Introduce the minimal runtime `Order` model.

**Recommended initial contents:**
- `Order`
- only the narrowest supporting state/type helpers required by the first slice
- constructor/helper for creating runtime orders from accepted intents

**Recommended responsibilities:**
- identity
- order-local quantities
- price fields relevant to the family
- invariant-preserving transitions for open/fill/completion behavior in the
  current market/limit slice

**Explicitly not in this first file:**
- broker tickets
- cancel/replace workflows
- venue-style acknowledgement state taxonomies
- bracket/OCO structures
- shipped stop-order execution logic

### Task 3: Keep Matching As Market-Fact Calculation

**Files:**
- Modify: `src/quantcraft/trading/domain/matching.py`
- Possibly modify: `tests/unit/trading/test_matching_and_state.py`

**Intent:**
- Preserve the current boundary where `matching` interprets executable market
  facts rather than becoming a stateful god object.

**Recommended direction:**
- matching should inspect runtime `Order` values instead of raw intents
- matching should calculate:
  - whether an order is executable
  - whether a fill occurs and at what price/quantity
- matching should not directly mutate unrelated trading/account state

For this first slice, keep the matcher contract narrow:

- continue returning `FillEvent | None`
- do not introduce trigger signals or a new transition object yet

If a later stop-order slice needs a richer matcher result, that should be
planned separately instead of being smuggled into the first runtime `Order`
refactor.

### Task 4: Move Runtime Order Ownership Out Of Strategy State

**Files:**
- Modify: `src/quantcraft/backtest/execution_model.py`
- Modify: `src/quantcraft/backtest/strategy_runtime.py`
- Modify: `src/quantcraft/backtest/runtime.py`
- Possibly modify: `src/quantcraft/backtest/order_activation.py`

**Intent:**
- Replace the current use of active/pending `OrderIntent` tuples as the nearest
  thing to runtime order state.

**Recommended outcome:**
- strategy continues to emit `OrderIntent`
- runtime accepts or defers the intent according to current activation rules
- once accepted into working state, the runtime manages a real `Order`
- any backtest execution-model hooks that currently reason about active intents
  should be updated to consume the runtime order representation or a deliberate
  order projection instead
- backtest orchestration continues to own bar/tick timing and activation rules,
  but not the meaning of an order itself

### Task 5: Preserve Fill-Driven Accounting

**Files:**
- Modify: `src/quantcraft/trading/domain/state.py`
- Modify: current result-surface tests only if internal refactor requires it

**Intent:**
- Keep the accounting handoff on `FillEvent`.

This slice should not introduce a new portfolio model.
The minimum target is:

- `Order` handles order-local transitions
- `FillEvent` remains the state-update handoff
- `TradingState` continues to update from fill facts

That preserves the current runtime while keeping the door open for later
`Position` and `Portfolio` promotion.

### Task 6: Documentation And Routing Sync

**Files:**
- Modify: `docs/design-docs/order-domain-runtime-design.md`
- Modify: any user-facing docs touched by implementation behavior changes
- Modify: this implementation plan if the code slice narrows or reorders tasks

**Intent:**
- Keep repository docs as the system of record while the first runtime `Order`
  seam is introduced.

## Verification Plan

During implementation:

- targeted unit tests for `Order`
- targeted integration tests for preserved market/limit behavior

Before closing the code slice:

- `uv run poe verify-runtime`
- `uv run poe repo-check`

If the implementation touches public runtime-sensitive semantics more broadly
than planned, widen verification to `uv run poe verify`.

## Out Of Scope

- public `Strategy` API changes
- shipped stop-market or stop-limit support
- cancel / replace / update flows
- `Portfolio`, `Ledger`, allocator, or risk engine design
- paper or live runtime implementation
- venue-specific adapters or broker-ticket abstractions

## One-Line Summary

The first implementation slice should introduce a real runtime `Order` inside
`trading`, keep matching and accounting boundaries intact, and migrate backtest
runtime ownership away from raw `OrderIntent` state without trying to build a
full OMS.
