# Active Plan

- Date: `2026-04-23`
- Task: `Freeze the stop/trigger Order domain spec before implementation planning`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Produce a docs-first stop/trigger Order spec that fixes the durable kernel
    direction before a new implementation plan is written.
  - Use current repository truth plus comparator-library evidence to decide:
    - whether `Order` stays backtest-local or becomes the long-lived shared
      runtime model
    - whether trigger-aware orders use inheritance-heavy modeling or
      concrete-order types with shared trigger facts
    - whether trigger commonality should live in a `TriggerSpec`-style value
      object or direct order fields
    - which first-class concepts the next implementation plan must preserve
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/design-docs/order-domain-runtime-design.md`
  - `docs/design-docs/order-runtime-model-design.md`
  - `docs/design-docs/order-lifecycle-and-sizing-design.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the repo workflow, Tier A safety boundary, current backtest and
    research scope, capability ownership, and the existing `OrderIntent` versus
    runtime `Order` seam this spec must extend rather than overwrite.
- Supporting references:
  - `docs/plans/2026-04-21-order-stop-market-implementation-plan.md`
  - `docs/plans/2026-04-21-order-stop-market-execution-plan.md`
  - local comparator sources under:
    - `/tmp/nautilus_trader`
    - `/tmp/lean`
    - `/tmp/backtrader`
    - `/tmp/quant-sizing-survey/backtesting.py`
    - `/tmp/quant-sizing-survey/lumibot`
    - `/tmp/quant-sizing-survey/vectorbt`
    - `/tmp/freqtrade`
- Why these references matter:
  - They are not repo authority, but they provide primary-source examples for
    stop-family order modeling, trigger handling, same-bar semantics, and order
    lifecycle depth.
- In-repo scope:
  - Create one active plan artifact that doubles as the approved design/spec
    note for the next Order-domain planning slice.
  - Keep the result docs-only. No Python implementation or product-spec edits.
- Out-of-repo scope:
  - No code changes outside this repository.
  - No live-service calls.
  - No web browsing was required for this slice because local comparator source
    trees already provided sufficient primary-source evidence.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A design-slice approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread direction to research comparator libraries, fix the stop
      concept as a durable kernel concern rather than a backtest-only shortcut,
      and write the spec before implementation planning
    - Granted scope:
      docs-only Tier A design/spec work for the `trading` context, including
      read-only inspection of local comparator repositories under `/tmp`
    - Expiration:
      end of this `2026-04-23` spec-design slice
    - Audit reference:
      this active plan
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The repository contains one docs-first stop/trigger Order spec that is
    explicit about:
    - runtime `Order` being a shared-kernel model rather than a backtest-only
      artifact
    - concrete order taxonomy for `market`, `limit`, `stop_market`,
      `stop_limit`
    - why `BaseTriggerOrder` is deferred
    - why `TriggerSpec` is deferred
    - which lifecycle and trigger facts must exist before implementation
  - The spec distinguishes durable design from first shipped implementation
    scope.
  - `uv run poe repo-check` passes after the new doc is added.
- Out of scope:
  - Implementing `stop_market`
  - Finalizing the concrete implementation plan
  - Promoting this spec into governing product authority
  - Designing trailing stops, OCO/brackets, or full OMS workflows

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after the new spec is evidence-backed, aligned with
    current repo truth, clear about rejected alternatives, and verified through
    the repo-local check surface.
- Acceptance artifact location:
  - `docs/plans/2026-04-23-stop-trigger-order-spec-design.md`
- How the generator and evaluator agreed on done before execution:
  - This slice is done when a future implementation-planning session can start
    from this document without reopening the core debates about:
    - shared-kernel versus backtest-local `Order`
    - explicit stop-family order types versus flat optional-stop fields
    - inheritance versus composition for trigger commonality
- Checks the evaluator will use:
  - Compare the new spec against current implementation truth in:
    - `src/quantcraft/trading/domain/intents.py`
    - `src/quantcraft/trading/domain/orders.py`
    - `src/quantcraft/trading/domain/matching.py`
    - `src/quantcraft/backtest/execution_model.py`
    - `src/quantcraft/backtest/strategy_runtime.py`
  - Compare the design decision against comparator evidence from Nautilus,
    LEAN, backtrader, backtesting.py, lumibot, vectorbt, and freqtrade.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - treating protective-stop versus entry-stop as separate domain concepts
  - freezing `TriggerSpec` or `BaseTriggerOrder` without evidence that the
    abstraction already pays for itself
  - drifting into backtest-only semantics for the long-lived `Order` model
  - writing a stop-market-only spec that cannot naturally accommodate
    `stop_limit`

## Generator Work Log

- Planned slice order:
  1. Read the active plan template and recent Order-domain plan artifacts.
  2. Read current repo truth for `OrderIntent`, runtime `Order`, matching, and
     backtest path construction.
  3. Read comparator implementations from local `/tmp` repositories.
  4. Freeze the durable design choices in this spec.
  5. Run `uv run poe repo-check`.
- Notes:
  - Existing `2026-04-21` stop-market handoff artifacts remain useful as a
    narrower implementation reference, but they are no longer the best durable
    authority for the overall stop/trigger order model after this spec.
  - This document intentionally fixes the kernel shape first; the next
    implementation plan may still choose to ship only `stop_market` in its
    first code slice.
- Blockers or scope changes:
  - None.

## Stop/Trigger Order Spec

### 1. Role Of This Document

This document is a docs-first design/spec artifact for the next Order-domain
planning step.

It is **not** governing product authority and it is **not** an implementation
plan.

Its job is narrower:

- freeze the durable stop/trigger order model
- remove the biggest architectural ambiguity before code planning
- let the later implementation plan narrow the first shipped slice without
  changing the kernel direction

### 2. Current Repository Truth

Current implemented truth as of `2026-04-23`:

- `OrderIntent` is quantity-based and only supports `market` and `limit`
  order types.
- runtime `Order` exists and is also currently quantity-based with
  `market`/`limit` only.
- matching is driven by executable `TickEvent` values and does not own any
  dormant trigger state.
- backtest path construction already tries to preserve a shared-kernel shape:
  synthetic executable ticks are produced first, then the matcher consumes
  orders against them.

Repo evidence:

- [src/quantcraft/trading/domain/intents.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/trading/domain/intents.py)
- [src/quantcraft/trading/domain/orders.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/trading/domain/orders.py)
- [src/quantcraft/trading/domain/matching.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/trading/domain/matching.py)
- [src/quantcraft/backtest/execution_model.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/backtest/execution_model.py)
- [src/quantcraft/backtest/strategy_runtime.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/backtest/strategy_runtime.py)

### 3. Problem Definition

Current `quantcraft` can express only immediately executable `market` and
working `limit` orders.

That is enough for:

- simple crossover strategies
- simple mean-reversion entries and exits
- basic limit-entry and limit-exit strategies

That is **not** enough for an important class of real strategy behavior:

- breakout entries above or below a trigger level
- protective exits that must activate only after a loss threshold is crossed
- stop-followed workflows where activation and execution are different moments
- future paper/live parity for trigger-aware order handling

Without stop-family orders, the current engine can still simulate some
strategies indirectly, but only by distorting intent into:

- ad hoc bar-close logic
- synthetic market/limit substitutions
- strategy-local state machines that should really belong to the order model

That is the main product problem this spec addresses.

### 4. Why This Matters Now

This is the right next seam because:

- stop-family orders are a much bigger unlock for realistic strategy coverage
  than adding more indicators or small UX polish
- the repository already has a shared matching kernel and synthetic executable
  tick path, so trigger-aware orders fit the current architecture
- delaying the stop-order model increases the chance that backtest-specific
  workarounds harden into the wrong long-lived design

The next code slice still does **not** need to ship the full stop family at
once, but the kernel direction must be fixed now.

### 5. Feature Goal

The feature goal for this design family is:

- let a user express stop-triggered order intent directly from a strategy
- let the runtime model hold dormant trigger-aware orders without pretending
  they are already executable
- preserve causal execution semantics on the shared backtest path
- keep the model suitable for later paper/live promotion

### 6. First Shipped Scope

This spec fixes the durable stop/trigger model, but it also narrows the
intended **first shipped implementation slice**.

First shipped implementation scope:

- `stop_market` end-to-end support
- additive strategy-facing API for `stop_market`
- trigger-aware runtime order behavior
- causal backtest trigger and fill semantics for `stop_market`

Not required in the first shipped slice:

- end-to-end `stop_limit` support

But the first shipped slice must **not** block natural later support for:

- `stop_limit`
- trailing stop orders
- additional trigger-order conditions or venue-specific aliases

So the implementation may ship only `stop_market`, while the durable kernel
shape must already be stop-family aware.

### 7. Non-Goals

This design/spec explicitly does **not** require the next code slice to add:

- trailing stop orders
- OCO / bracket / OTO orchestration
- cancel / replace / reject workflows beyond what already exists
- short-selling semantics
- portfolio-target or rebalance order semantics
- percentage-sizing redesign
- paper/live brokerage integration
- venue-specific trigger-source support beyond the minimal first backtest
  source

### 8. Primary Decision

`quantcraft` should model stop-family behavior as a **shared-kernel runtime
order concern**, not as a backtest-only convenience.

That means:

- the long-lived runtime `Order` model must remain suitable for backtest,
  paper, and live paths
- stop behavior must not be encoded as strategy-side special cases such as
  "protective stop" versus "entry stop"
- the durable runtime model should be able to express both `stop_market` and
  `stop_limit`, even if the first shipped implementation slice only delivers
  `stop_market`

This matches the repository's existing architectural intent: the shared
trading kernel owns order semantics, while backtest owns only historical event
construction and orchestration.

### 9. Order Taxonomy

The durable runtime order taxonomy should be explicit.

Recommended concrete runtime order types:

- `MarketOrder`
- `LimitOrder`
- `StopMarketOrder`
- `StopLimitOrder`

Explicit design rule:

- `stop_market` and `stop_limit` are **real order types**, not just
  presentation aliases for a flat `Order` with optional stop fields
- those runtime order types are parameterized by explicit `trigger_condition`
  facts, so both upward- and downward-triggering semantics can live in the same
  canonical order family without introducing separate user-facing `MIT` / `LIT`
  classes

Why:

- `stop_market` and `stop_limit` have different post-trigger execution
  behavior
- explicit order types keep user-visible semantics legible
- this aligns with Nautilus, LEAN, and backtrader, which all preserve
  stop-family order types explicitly

Comparator evidence:

- Nautilus:
  [model/enums.py](/tmp/nautilus_trader/nautilus_trader/model/enums.py:338)
- LEAN:
  [StopMarketOrder.cs](/tmp/lean/Common/Orders/StopMarketOrder.cs:23),
  [StopLimitOrder.cs](/tmp/lean/Common/Orders/StopLimitOrder.cs:23)
- backtrader:
  [order.py](/tmp/backtrader/backtrader/order.py:226)

### 10. Public Strategy Contract

The exact Python API names remain implementation-plan territory, but the
feature contract is already narrow enough to state what the strategy surface
must support.

Required additive user-facing capability:

- a strategy must be able to submit a stop-triggered buy or sell order without
  encoding trigger state manually in strategy-local booleans

Required first-slice public behavior:

- a strategy can request `stop_market`
- the request remains quantity-based
- the request includes a trigger/stop price
- the request does **not** require the strategy to specify
  `crosses_above`/`crosses_below` directly
- the request does not require the strategy to declare whether the order is a
  "protective" stop or an "entry" stop

Representative intended shape:

```python
self.buy(order_type="stop_market", stop_price=105.0, quantity=1.0)
self.sell(order_type="stop_market", stop_price=95.0, quantity=1.0)
```

Representative later-natural shape:

```python
self.buy(
    order_type="stop_limit",
    stop_price=105.0,
    limit_price=106.0,
    quantity=1.0,
)
```

This section fixes the **capability contract**, not the final method signature
or naming details.

Normalization boundary:

- the strategy/request surface uses `stop_price`
- request normalization converts `stop_price` into runtime `trigger_price`
- request normalization also infers runtime `trigger_condition`
- this normalization happens at the request-to-runtime boundary, before a
  concrete runtime order is created
- runtime order semantics use only `trigger_price`
- runtime order semantics persist the inferred `trigger_condition`
- no user-facing `market_if_touched` / `limit_if_touched` alias surface is
  required in the first shipped slice
- the first shipped slice infers `trigger_condition` from the submission-time
  current trigger source snapshot:
  - if `stop_price > current_trigger_price`, infer `crosses_above`
  - if `stop_price < current_trigger_price`, infer `crosses_below`
  - if `stop_price == current_trigger_price`, reject as ambiguous/in-market for
    first-slice auto-inference

### 11. Trigger Modeling

Triggering should be modeled as a **first-class runtime fact**.

Recommended trigger facts:

- `trigger_price`
- `trigger_type`
- `trigger_condition`
- `is_triggered`
- `triggered_at` or an equivalent timestamp/event-backed fact

Recommended lifecycle support:

- `OrderTriggered` as an internal/runtime event
- `TRIGGERED` as an order lifecycle state or equivalent kernel-local fact for
  orders that can remain working after trigger
- `TRIGGERED` does not need to persist as a durable visible state for
  `StopMarketOrder`; it is primarily required for trigger-aware orders that can
  remain open after trigger, such as `StopLimitOrder`
- `StopMarketOrder` may record trigger facts and fill on the same executable
  point without persisting a long-lived triggered state

Layering rule for the first slice:

- `OrderTriggered` is a runtime/backtest-internal event
- it is not automatically promoted into the public
  `quantcraft.trading.domain.events` export surface in the first shipped slice
- the first implementation may use it to coordinate trigger-aware runtime
  semantics without widening the public event contract
- for the first shipped slice, `trigger_type` is fixed to synthetic executable
  `last`
- that first-slice `trigger_type` default is kernel-local rather than a newly
  widened public strategy parameter
- `trigger_condition` is a durable runtime fact once inferred and must not
  change just because later market prices move around it

Important nuance:

- a `StopMarketOrder` may trigger and fill on the same executable market step
- a `StopLimitOrder` may trigger first and remain open afterward

So the model must support explicit triggering even when some trigger-aware
orders collapse quickly into filled state.

This follows the strongest comparator pattern seen in Nautilus:

- explicit stop-family order types
- explicit trigger facts
- explicit trigger event/state

Evidence:

- [stop_market.pyx](/tmp/nautilus_trader/nautilus_trader/model/orders/stop_market.pyx:137)
- [stop_limit.pyx](/tmp/nautilus_trader/nautilus_trader/model/orders/stop_limit.pyx:150)
- [base.pyx](/tmp/nautilus_trader/nautilus_trader/model/orders/base.pyx:79)

### 12. Inheritance Versus Composition

The recommended direction is:

- keep one shared base `Order`
- keep concrete order classes explicit
- share trigger commonality through direct fields and shared lifecycle/events
- **do not introduce `BaseTriggerOrder` yet**

Rationale:

- the abstraction is not yet proven to pay for itself
- the first stop-family set is still small
- a premature `BaseTriggerOrder` would freeze a class hierarchy before the
  repository knows whether future triggerable orders will share enough stable
  behavior
- Nautilus reaches a good result without introducing a visible intermediate
  `BaseTriggerOrder`; all concrete stop-family orders inherit directly from the
  main `Order`

This is composition-biased in the important sense:

- common trigger behavior belongs in shared facts, lifecycle handling, and
  execution policy
- not in a forced inheritance layer added before duplication appears

### 7. `TriggerSpec` Decision

The recommended first design is:

- **do not create a `TriggerSpec` value object yet**
- keep trigger facts directly on concrete trigger-aware orders

Rationale:

- today, a `TriggerSpec` would mostly be a field bundle without enough proven
  independent behavior
- introducing it now would add indirection without clarifying the domain
- Nautilus and LEAN both keep trigger data directly on concrete order models
  rather than centering a reusable trigger-spec value object

This does **not** reject composition as a principle.

It only says the first useful composition boundary is more likely to be:

- trigger-evaluation policy
- same-bar/tail execution policy
- trailing update policy

rather than a standalone trigger data object.

### 13. Validation Rules

The durable order-validation direction should be:

- `MarketOrder`
  - requires quantity
  - forbids `limit_price`
  - forbids `trigger_price`
- `LimitOrder`
  - requires quantity
  - requires `limit_price`
  - forbids `trigger_price`
- `StopMarketOrder`
  - requires quantity
  - requires `trigger_price`
  - requires `trigger_condition`
  - forbids `limit_price`
- `StopLimitOrder`
  - requires quantity
  - requires `trigger_price`
  - requires `trigger_condition`
  - requires `limit_price`

No validation rule should branch on user intent such as:

- "protective stop"
- "entry stop"

Strategy-side request normalization infers `trigger_condition` mechanically
from:

- `stop_price`
- the submission-time current trigger-source price
- the first-slice trigger-source choice

Runtime trigger direction is then derived from:

- persisted `trigger_condition`
- `trigger_price`
- observed executable market price source

Design rule:

- trigger direction must **not** be derived from `side` alone
- trigger direction must **not** be reinterpreted from position intent such as:
  - open versus close
  - reduce-only versus non-reduce-only
- a buy or sell stop request may validly normalize into either
  `crosses_above` or `crosses_below`
- venue-native names such as "stop", "take profit", "market if touched", or
  "limit if touched" are projection concerns, not the canonical kernel model

### 14. Behavioral Requirements

The next implementation plan must preserve the following behavior-level
requirements.

General:

- a stop-family order is dormant before trigger
- a dormant stop-family order must not fill
- a trigger-aware order carries a durable `trigger_condition`
- triggering and filling are distinct concepts even when they happen on the
  same executable step
- on any executable point where trigger and fill both occur, trigger facts are
  established first and the underlying fill is applied second on that same
  point
- stop-family orders are **not** independent fill-model families
- stop-family orders are modeled as:
  - a trigger layer
  - plus an underlying executable order behavior
- once triggered, the stop layer is conceptually consumed and execution
  proceeds according to the underlying order behavior
- the matcher/fill engine must reuse the existing underlying execution path
  rather than duplicating separate fill logic per stop-family variant
- trigger detection uses `trigger_condition`, not `side` alone

`stop_market`:

- when triggered, it becomes immediately executable as a market order
- in backtest, it may trigger and fill on the same decisive executable point

`stop_limit`:

- when triggered, it becomes an ordinary working limit order
- while dormant, it is invisible to working-limit path compression and matching
- it must never gain access to pre-trigger price-path history
- the trigger event upgrades it to a working limit order before the engine
  evaluates the remainder of the current synthetic path
- only the post-trigger tail may be evaluated for same-bar limit matching
- the trigger tick itself is included in that post-trigger tail
- the trigger tick is therefore the first point at which the underlying limit
  behavior may be evaluated

Implementation-shape rule:

- the engine should be able to reason about:
  - `stop_market` as `stop + market`
  - `stop_limit` as `stop + limit`
- trigger detection and underlying fill behavior should remain separate concerns
- a design that sends `limit` and `stop_limit` through entirely separate,
  duplicated fill logic is out of bounds for this spec
- the same warning applies to `market` versus `stop_market`

Ordering and causality:

- orders emitted from `on_bar()` become active on the next bar only
- stop-trigger evaluation must use the causal synthetic path, not bar-summary
  hindsight shortcuts
- already-executable working orders must not be overtaken by newly triggered
  stop orders on the same executable point unless a later spec explicitly
  changes priority rules

Long-only MVP compatibility:

- `sell(stop...)` while flat remains an exit-only no-op in the current
  long-only scope
- in the first shipped slice, a flat sell-stop request does not create a
  dormant runtime order and is discarded as a no-op during activation/runtime
  processing
- no stop behavior may silently introduce short-entry semantics

### 15. Trigger Semantics

Recommended semantic rule:

- `crosses_above` triggers when the chosen trigger price source reaches or
  exceeds the order trigger price
- `crosses_below` triggers when the chosen trigger price source reaches or
  falls below the order trigger price

The domain should care only about executable crossing semantics, not the
strategy story behind the order.

The domain should also avoid folding trigger-direction semantics into order-side
names alone. The canonical runtime model must preserve trigger direction
explicitly through `trigger_condition`.

For future runtime breadth, keep `trigger_type` as a real concept even if the
first shipped backtest slice supports only one source.

Recommended long-lived shape:

- durable enum or equivalent concept such as:
  - `last`
  - `bid`
  - `ask`
  - `mid`
  - `mark`
  - `index`

Recommended first shipped scope:

- freeze a single minimal backtest trigger source first:
  - synthetic executable `TickEvent.last`
  - `crosses_above` triggers when `last >= trigger_price`
  - `crosses_below` triggers when `last <= trigger_price`
- exact equality at the first eligible executable point counts as a trigger
- defer broader trigger-source support to later paper/live slices

Canonical examples:

- buy `stop_market` above current price normalizes to `crosses_above`
- buy `stop_market` below current price normalizes to `crosses_below`
- sell `stop_market` above current price normalizes to `crosses_above`
- sell `stop_market` below current price normalizes to `crosses_below`

Venue-facing projection examples:

- some venues or APIs may call `crosses_above + market` a stop order
- some venues or APIs may call `crosses_below + market` a take-profit or
  market-if-touched order
- the kernel should preserve the canonical trigger condition and leave those
  names to adapters or UX copy

### 16. Runtime Boundary

Responsibility split:

- `Strategy` / `research`
  - expresses order requests
  - does not own trigger progression
- `backtest`
  - constructs synthetic executable path facts from bars
  - decides path ordering and same-bar execution policy
- `trading` runtime order model
  - owns order terms and legal state transitions
  - owns trigger facts
  - owns fill application legality
- matcher / execution logic
  - determines whether executable prices satisfy trigger or fill conditions

This preserves the existing repository design principle that backtest is a
historical event source, not a separate trading semantics owner.

### 17. Same-Bar And Post-Trigger Guidance

The durable spec should preserve these best-practice constraints:

- orders created from `on_bar()` never act retroactively on the bar that
  created them
- trigger detection must respect causal event ordering on the synthetic bar
  path already defined by the current execution model:
  - bullish bar path: `open -> low -> high -> close`
  - bearish bar path: `open -> high -> low -> close`
- `stop_market` may trigger and fill on the same decisive executable point
- `stop_limit` must only become a working limit order **after** trigger
- any same-bar post-trigger `stop_limit` matching must evaluate only the tail
  after the trigger point, never the pre-trigger path

This follows the same design pressure seen in:

- Nautilus and LEAN:
  triggered state is explicit, because stop-limit survives trigger
- backtesting.py:
  same-bar stop and limit ordering must be decided conservatively

Evidence:

- [backtesting.py](/tmp/quant-sizing-survey/backtesting.py/backtesting/backtesting.py:872)
- [FillModel.cs](/tmp/lean/Common/Orders/Fills/FillModel.cs:471)

### 18. Acceptance Criteria

The feature-spec level done contract for the next planning step is:

1. a user can express stop-triggered intent directly from strategy code
2. strategy-facing `stop_price` requests are normalized into durable runtime
   `trigger_price + trigger_condition` facts without asking the user to provide
   trigger direction manually
3. runtime order state can represent dormant, triggered, and filled stop-family
   behavior without backtest-specific hacks
4. the first shipped slice can add `stop_market` without redesigning the order
   model again
5. later `stop_limit` support can be added by reusing the same trigger-aware
   order model rather than replacing it
6. underlying `market` and `limit` execution behavior can be reused after
   trigger instead of cloning stop-specific fill engines
7. same-bar semantics remain causal and do not evaluate pre-trigger path for a
   triggered `stop_limit`
8. no strategy API or runtime model requires a distinction between
   "protective stop" and "entry stop"
9. no runtime rule depends on deriving trigger direction from `side` alone

### 19. Relationship To Existing Stop-Market Plan

The existing `2026-04-21` stop-market handoff plan remains useful as a first
shipping slice reference, but this spec supersedes it on one important point:

- the **durable model** must be stop-family aware, not stop-market-only

This means the next implementation plan should be allowed to keep:

- first shipped implementation scope = `stop_market` only

while still preserving:

- explicit `stop_limit` as part of the kernel direction
- trigger-aware lifecycle facts that will not need redesign when `stop_limit`
  lands later
- explicit runtime `trigger_condition` so future venue-facing aliases do not
  require remapping trigger direction out of type names

For the first shipped slice, "explicit order types" should be read as the
**canonical runtime order taxonomy**, not as a hard requirement to introduce
Python subclass hierarchies immediately.

In other words:

- `market`, `limit`, `stop_market`, and `stop_limit` must be first-class
  runtime meanings
- the first shipped implementation may still represent those meanings with a
  single discriminated `Order` aggregate plus explicit trigger facts
- a later slice may promote that taxonomy into separate runtime classes if the
  code shape starts paying for it

### 20. Rejected Alternatives

#### Rejected: flat `Order` with optional `stop_price`

Why rejected:

- too easy to drift into ambiguous combinations
- weakens the semantic distinction between stop-market and stop-limit
- better for a small backtest utility than a shared execution kernel

Closest comparator:

- `backtesting.py`

#### Rejected: separate user-facing `MIT` / `LIT` order classes in the first
slice

Why rejected:

- modern crypto trading UX more commonly exposes generic trigger/TP-SL order
  surfaces instead of asking the trader to think in `MIT` / `LIT` terms
- the canonical kernel model is clearer when trigger direction is stored
  explicitly as `trigger_condition`
- venue-specific names can be handled later as adapter or UX projection details

#### Rejected: `BaseTriggerOrder` now

Why rejected:

- abstraction benefit is still speculative
- risks locking the codebase into an inheritance shape before duplication is
  real

Closest lesson:

- Nautilus gets most of the benefit without that extra layer

#### Rejected: `TriggerSpec` now

Why rejected:

- would mostly be a passive wrapper today
- adds indirection without yet paying back complexity

### 21. What This Spec Intentionally Leaves For The Implementation Plan

Still intentionally deferred:

- exact Python class API shape for the first shipped slice
- whether the initial implementation creates real Python subclasses
  immediately or first evolves the current dataclass model toward them in steps
- exact trigger-source enum names
- exact event object names if the first implementation keeps trigger state
  kernel-local before exposing a fuller order-event model
- exact test matrix for gap-through and same-bar tail behavior

Those decisions belong in the next implementation plan, but they must stay
inside the design box fixed above.

## Evaluator Review

- Findings:
  - Comparator evidence strongly supports a hybrid design:
    explicit stop-family order types plus explicit trigger facts.
  - Nautilus provides the best match for `quantcraft` because it keeps stop
    semantics in a shared runtime order model rather than flattening them into
    a bar-only backtest convenience.
  - The best-practice recommendation is therefore:
    - `Order` remains the shared kernel base
    - `StopMarketOrder` and `StopLimitOrder` are explicit concrete order types
    - trigger commonality is shared through direct fields and lifecycle/events,
      not a premature `BaseTriggerOrder` or `TriggerSpec`
  - No additional user decision is required to freeze the design at this stage.
- Verification evidence:
  - repository truth reads over:
    - `src/quantcraft/trading/domain/intents.py`
    - `src/quantcraft/trading/domain/events.py`
    - `src/quantcraft/backtest/execution_model.py`
    - `src/quantcraft/backtest/strategy_runtime.py`
  - comparator-source reads over:
    - `/tmp/nautilus_trader/nautilus_trader/model/orders/*`
    - `/tmp/lean/Common/Orders/*`
    - `/tmp/backtrader/backtrader/order.py`
    - `/tmp/quant-sizing-survey/backtesting.py/backtesting/backtesting.py`
    - `/tmp/quant-sizing-survey/lumibot/lumibot/entities/order.py`
    - `/tmp/quant-sizing-survey/vectorbt/vectorbt/portfolio/*`
    - `/tmp/freqtrade/freqtrade/*`
- Final disposition:
  - `complete`
