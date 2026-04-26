# Stop/Trigger Order Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.
>
> Execution gate:
> do not implement directly from this file. First create a fresh active Tier A
> implementation plan with the required implementation approval record,
> evaluator contract, and fresh verification evidence.

**Goal:** Ship the first end-to-end stop-trigger order slice in the shared backtest kernel by adding `stop_market` support with durable `trigger_condition` semantics, same-point trigger/fill handling, and stop-aware synthetic path generation.

**Architecture:** Keep the current `PendingOrderRequest -> OrderIntent -> Order -> FillEvent -> TradingState` seam intact, but extend it with explicit trigger facts. Normalize strategy-facing `stop_price` into durable runtime `trigger_price + trigger_condition` at request time using the current `on_bar()` close, keep stop orders dormant until the matcher sees a causal synthetic executable point, and delegate triggered `stop_market` fills back into the existing market-fill path instead of creating a second stop-specific fill engine. Defer `stop_limit` execution, trailing logic, and stop-aware `%` sizing.

**Tech Stack:** Python 3.13, frozen `dataclass` aggregates, `pytest`, `uv`, Poe tasks, `quantcraft.trading`, `quantcraft.backtest`, `quantcraft.research`

---

- Date: `2026-04-23`
- Task: `Author the concrete stop-trigger order implementation plan`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Produce one implementation plan that a future coding session can execute
    without reopening the stop-order design debate.
  - Translate the approved spec and test matrix into:
    - concrete file targets
    - TDD sequencing
    - runtime ordering decisions
    - repository-local verification gates
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
  - `docs/design-docs/order-runtime-model-design.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-23-stop-trigger-order-spec-design.md`
  - `docs/plans/2026-04-23-stop-trigger-order-test-matrix-design.md`
- Why these are governing:
  - They define the Tier A workflow rules, current shipped backtest/research
    contract, the canonical backtest path/matching boundary, and the approved
    stop-trigger semantics this implementation must preserve.
- Supporting references:
  - `docs/plans/2026-04-21-order-stop-market-implementation-plan.md`
  - `docs/plans/2026-04-21-order-stop-market-execution-plan.md`
  - `src/quantcraft/trading/domain/intents.py`
  - `src/quantcraft/trading/order_requests.py`
  - `src/quantcraft/research/strategy.py`
  - `src/quantcraft/backtest/strategy_runtime.py`
  - `src/quantcraft/trading/domain/orders.py`
  - `src/quantcraft/trading/domain/matching.py`
  - `src/quantcraft/backtest/execution_model.py`
  - `src/quantcraft/backtest/runtime.py`
  - `src/quantcraft/trading/sizing.py`
- Why these references matter:
  - They are the exact code seams the stop-trigger slice must extend.
  - The older `2026-04-21` plan artifacts are useful historical context, but
    they predate the finalized `trigger_condition` and strategy-side
    auto-inference decisions.
- In-repo scope:
  - Add one docs-only implementation plan under `docs/plans/`.
  - Record the exact implementation order, boundaries, and verification
    commands for the future Tier A code slice.
- Out-of-repo scope:
  - No Python implementation in this session.
  - No live-service work.
  - No new comparator research in this session.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A docs-only planning approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread direction to re-read the approved stop spec and test
      matrix, inspect current source seams, and write the actual implementation
      plan before any code work starts
    - Granted scope:
      docs-only Tier A planning work for the `trading` and `backtest`
      implementation slice
    - Expiration:
      end of this `2026-04-23` implementation-planning slice
    - Audit reference:
      this active plan plus the approved spec/test artifacts dated
      `2026-04-23`
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The repository contains one implementation plan that:
    - reflects the approved `trigger_condition` model
    - maps stop-trigger semantics onto current source files
    - gives an explicit TDD order
    - calls out the `qty_percent` and `stop_limit` defers clearly
    - uses only repo-local verification commands
  - `uv run poe repo-check` passes after the new plan is added.
- Out of scope:
  - Executing the code changes
  - Closing the future Tier A implementation review
  - Reopening the core stop-order design

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close this planning slice only after the new implementation plan is
    specific enough that a future code session can execute it without guessing:
    - where request normalization lives
    - where trigger facts live
    - how same-point trigger/fill ordering works
    - how stop-crossing synthetic ticks are generated
- Acceptance artifact location:
  - `docs/plans/2026-04-23-stop-trigger-order-implementation-plan.md`
- How the generator and evaluator agreed on done before execution:
  - This slice is done when the plan is concrete enough for a future engineer
    to write the first failing tests directly from it and still stay inside the
    approved spec and test matrix.
- Checks the evaluator will use:
  - verify the plan cites the approved `2026-04-23` spec/test artifacts
  - verify the plan uses current code truth instead of the older narrow
    `2026-04-21` assumptions
  - run `uv run poe repo-check`
- Auto-fail conditions:
  - deriving trigger direction from `side` alone
  - introducing a second stop-specific fill path instead of reusing market
    matching after trigger
  - hiding the request-normalization boundary
  - silently widening this slice into `stop_limit`, trailing, or stop-aware
    `%` sizing

## Generator Work Log

- Planned slice order:
  1. Re-read the approved stop spec and test matrix.
  2. Re-read the current source seams in `research`, `trading`, `backtest`,
     and current tests.
  3. Translate the approved semantics into a concrete TDD implementation plan.
  4. Run repo-local verification for the new planning artifact.
- Notes:
  - Current repo truth is still a single `Order` dataclass discriminated by
    `order_type`. This plan keeps that shape for the first code slice instead
    of adding runtime subclass hierarchies.
  - The two `2026-04-23` design artifacts are still untracked in the working
    tree as of this planning session. This plan assumes they remain the
    authoritative design inputs for the future implementation kickoff.
- Blockers or scope changes:
  - None.

## Repository Snapshot

The future implementation starts from these concrete seams.

### Current Strategy And Request Surface

- `Strategy.buy()` / `Strategy.sell()` in
  `src/quantcraft/research/strategy.py` currently accept:
  - `symbol`
  - one sizing mode
  - `order_type`
  - `limit_price`
  - `tag`
- `_StrategyDriver.handle_bar()` and `_StrategyDriver.activate_pending_order_requests()`
  in `src/quantcraft/backtest/strategy_runtime.py` own:
  - `on_bar()` lifecycle enforcement
  - next-bar order activation
  - runtime `OrderIntent` creation
- `PendingOrderRequest` in `src/quantcraft/trading/order_requests.py` is the
  current request-side validation object.

### Current Runtime Order And Matching Surface

- `OrderIntent` in `src/quantcraft/trading/domain/intents.py` is still
  quantity-only and `market|limit` only.
- `Order` in `src/quantcraft/trading/domain/orders.py` is a frozen aggregate
  with:
  - `id`
  - `symbol`
  - `side`
  - `quantity`
  - `order_type`
  - `limit_price`
  - `tag`
  - `filled_quantity`
- `match_order()` in `src/quantcraft/trading/domain/matching.py` assumes every
  active order is already executable and only distinguishes `market` vs
  `limit`.

### Current Backtest Path Construction

- `ConservativeOHLCVExecutionModel.tick_events_for_bar()` in
  `src/quantcraft/backtest/execution_model.py` emits:
  - `open`
  - canonical turning points
  - decisive crossed `limit_price` points for currently active orders
- `_run_backtest()` in `src/quantcraft/backtest/runtime.py` currently:
  - activates pending orders at the next bar
  - loops ticks for that bar
  - matches every active order on every tick
  - skips flat `sell` orders as the long-only no-op rule

### Current Sizing Pressure

- `resolve_pending_order_request()` and helper anchor-price logic in
  `src/quantcraft/trading/sizing.py` currently know only:
  - ordinary market buy anchors
  - ordinary limit buy anchors
- Stop-aware `%` sizing is therefore still unresolved. This plan keeps
  `stop_market` quantity-only in the first shipped slice.

## Recommended Implementation Strategy

The future code slice should use these tactical decisions.

### 1. Keep The Existing `Order` Aggregate Shape

Do **not** introduce runtime subclass hierarchies in the first shipped slice.

Use the existing discriminated dataclass pattern:

- extend `OrderType` with shipped `stop_market`
- extend `OrderIntent`, `PendingOrderRequest`, and `Order` with explicit
  trigger facts
- keep `Order` as the one aggregate that protects trigger and fill legality

This is the smallest change that still preserves the approved durable design.

### 2. Normalize At The Strategy/Request Boundary

The public strategy API should accept:

- `order_type="stop_market"`
- `stop_price=...`

It should **not** accept user-facing `trigger_condition`.

Normalization rule for the first slice:

- infer `trigger_condition` while still inside the active `on_bar()` context
- use the active closed bar's `close` as the current submission-time reference
  price, because that is the only public strategy-time executable reference
  available today
- if `stop_price > bar.close`, infer `crosses_above`
- if `stop_price < bar.close`, infer `crosses_below`
- if `stop_price == bar.close`, reject the request as ambiguous/in-market for
  the first slice

This keeps user UX exchange-like while preserving durable runtime facts.

Validation ownership for the first slice should be explicit:

- contextual intake validation belongs in `Strategy.buy()` / `Strategy.sell()`
  or a small request-normalization helper they call
- that layer owns:
  - `stop_price == active_bar.close` rejection
  - `qty_percent + stop_market` rejection
  - `trigger_condition` inference
- `PendingOrderRequest.__post_init__()` should keep only shape validation that
  does not require active-bar context, such as:
  - missing `stop_price`
  - invalid finite numeric checks
  - `limit_price` forbidden on `stop_market`

### 3. Keep `stop_price` Out Of Runtime Truth

Use this field naming split:

- strategy/request surface: `stop_price`
- normalized runtime intent/order fields: `trigger_price`

`PendingOrderRequest` may still carry `stop_price` because it is the public
request-layer object, but `OrderIntent` and `Order` should only carry runtime
`trigger_*` fields.

### 4. Keep Trigger Detection Separate From Fill Matching

The matcher should not grow into a stateful stop engine.

Preferred shape:

- add a narrow trigger predicate/helper
- keep `match_order()` responsible only for executable orders
- once a dormant `stop_market` is triggered, reuse the ordinary market-fill
  branch on the same decisive executable point

This preserves the approved `trigger layer + underlying executable behavior`
direction.

### 5. Make Execution-Model Compression Stop-Aware

The execution model must generate decisive synthetic points for stop crossings
the same way it already does for resting limit crossings.

That means:

- gap-through stop triggers happen at `open`
- intrabar stop triggers require decisive `trigger_price` points inside the
  canonical segment traversal
- the path stays canonical and order-independent
- only the compression to decisive events is active-order-aware

### 6. Keep Same-Point Trigger/Fill, But Use Two-Phase Ordering

Per synthetic tick:

1. process already-executable active orders first
2. detect dormant stop orders whose trigger fires on that same point
3. record trigger facts on those orders
4. immediately route newly triggered `stop_market` orders through the existing
   market-fill path on that same point

This preserves:

- same-point trigger/fill
- no retroactive pre-trigger fills
- existing active-order priority ahead of newly triggered orders

### 7. Defer Stop-Aware `%` Sizing Explicitly

First shipped code slice should support:

- `quantity` with `stop_market`

First shipped slice should reject:

- `qty_percent` with `stop_market`

Reason:

- current sizing reservation and buy-anchor logic only model ordinary market
  and limit behavior
- using `next_bar.open` or `stop_price` as a hidden anchor for `%` sizing would
  be an unapproved pricing-policy decision, not a small feature add

This defer is narrower and safer than silently inventing stop-aware sizing
semantics in the same slice.

It also needs one extra protection on the ordinary `%` sizing path:

- dormant `stop_market` orders must not leak into `_active_buy_cash_reservation()`
  as if they were already ordinary market buys
- the first shipped code should either:
  - exclude dormant `stop_market` from active buy-cash reservations, or
  - hard-fail if a future edit tries to route `stop_market` into the ordinary
    `%` sizing anchor path without an explicit policy decision

## Task 1: Freeze The Public Stop-Market Contract In Tests

**Files:**
- Modify: `tests/unit/trading/test_contracts.py`
- Modify: `tests/unit/research/test_strategy_surface.py`

**Step 1: Write the failing tests**

Add tests that lock the public contract:

- `OrderIntent` supports shipped `stop_market`
- `PendingOrderRequest` accepts `stop_price` for `stop_market`
- contextual intake validation rejects:
  - missing `stop_price`
  - `limit_price` on `stop_market`
  - `qty_percent` on `stop_market`
  - `stop_price == active_bar.close`
- `Strategy.buy()` / `Strategy.sell()` auto-infer `trigger_condition`
- inference uses the active closed bar's `close` as the first-slice baseline
- side alone does not determine `trigger_condition`
- `init()` still cannot create stop requests, so there is no first-slice
  fallback inference baseline outside `on_bar()`

Representative test examples:

```python
def test_stop_market_request_above_close_infers_crosses_above() -> None:
    runtime = _runtime(StopMarketAboveCloseStrategy())
    runtime.handle_bar(_closed_bar(close=100.0))
    assert runtime.order_state().pending == (
        PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            stop_price=120.0,
            trigger_condition="crosses_above",
            tag="entry",
        ),
    )
```

```python
def test_stop_market_qty_percent_is_rejected_in_first_slice() -> None:
    class PercentStopStrategy(Strategy):
        def on_bar(self, bar: BarEvent) -> None:
            self.buy(qty_percent=50.0, order_type="stop_market", stop_price=120.0)
```

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest -q tests/unit/trading/test_contracts.py tests/unit/research/test_strategy_surface.py
```

Expected:

- failures for missing `stop_price` / `trigger_condition` fields and missing
  `stop_market` strategy support

**Step 3: Write minimal implementation**

Update only the request and strategy surfaces:

- `src/quantcraft/trading/domain/intents.py`
- `src/quantcraft/trading/order_requests.py`
- `src/quantcraft/research/strategy.py`
- `src/quantcraft/backtest/strategy_runtime.py`

Core changes:

- extend shipped `OrderType` to include `stop_market`
- add `TriggerCondition = Literal["crosses_above", "crosses_below"]`
- add request-only `stop_price`
- add normalized `trigger_condition` on `PendingOrderRequest`
- track active bar close inside `Strategy` while `on_bar()` is running
- perform contextual stop validation and infer `trigger_condition` inside
  `buy()` / `sell()` or a tiny helper they own

**Step 4: Run tests to verify they pass**

Run the same targeted command from Step 2.

Expected:

- PASS

**Step 5: Commit**

```bash
git add tests/unit/trading/test_contracts.py tests/unit/research/test_strategy_surface.py src/quantcraft/trading/domain/intents.py src/quantcraft/trading/order_requests.py src/quantcraft/research/strategy.py src/quantcraft/backtest/strategy_runtime.py
git commit -m "feat: add stop-market request normalization"
```

## Task 2: Promote `OrderIntent` And Runtime `Order` To Trigger-Aware Truth

**Files:**
- Modify: `src/quantcraft/trading/domain/intents.py`
- Modify: `src/quantcraft/trading/domain/orders.py`
- Modify: `tests/unit/trading/test_orders.py`

**Step 1: Write the failing tests**

Add tests that lock runtime order facts:

- `OrderIntent` carries `trigger_price` and `trigger_condition`
- `Order` carries:
  - `trigger_price`
  - `trigger_condition`
  - `trigger_type`
  - `triggered_at`
- `Order.from_intent()` preserves normalized trigger facts
- dormant `stop_market` is not executable
- `Order.trigger(...)` marks the order triggered once
- triggered `stop_market` becomes executable as market behavior
- `Order.apply_fill()` rejects fill-before-trigger for dormant stop orders

Representative test examples:

```python
def test_stop_market_order_from_intent_preserves_trigger_fields() -> None:
    order = Order.from_intent(
        order_id=7,
        intent=OrderIntent(
            symbol="BTC/USDT",
            side="buy",
            quantity=1.0,
            order_type="stop_market",
            trigger_price=120.0,
            trigger_condition="crosses_above",
        ),
    )
    assert order.trigger_type == "last"
    assert order.is_triggered is False
```

```python
def test_dormant_stop_market_rejects_fill_application() -> None:
    with pytest.raises(ValueError, match="dormant stop order"):
        order.apply_fill(fill)
```

**Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest -q tests/unit/trading/test_orders.py
```

Expected:

- failures for missing runtime trigger fields and missing `trigger()` behavior

**Step 3: Write minimal implementation**

Update `OrderIntent` and `Order` only:

- add runtime `trigger_price`
- add runtime `trigger_condition`
- add runtime `trigger_type` with first-slice fixed value `"last"`
- add `triggered_at`
- add `is_triggered`, `is_executable`, and `executable_order_type` helpers
- add `trigger(timestamp=...) -> Order`

Keep one aggregate and avoid new exported event types.

**Step 4: Run test to verify it passes**

Run the same targeted command from Step 2.

Expected:

- PASS

**Step 5: Commit**

```bash
git add tests/unit/trading/test_orders.py src/quantcraft/trading/domain/intents.py src/quantcraft/trading/domain/orders.py
git commit -m "feat: add trigger-aware runtime orders"
```

## Task 3: Keep Matching Pure While Adding Trigger Predicates

**Files:**
- Modify: `src/quantcraft/trading/domain/matching.py`
- Modify: `tests/unit/trading/test_matching_and_state.py`

**Step 1: Write the failing tests**

Add tests that split trigger detection from fill matching:

- dormant stop orders never fill through `match_order()`
- `crosses_above` trigger predicate fires on equality and gap-through prices
- `crosses_below` trigger predicate fires on equality and gap-through prices
- triggered `stop_market` fills through the same market slippage path as
  ordinary market orders
- non-stop `market` and `limit` behavior is unchanged

Representative test examples:

```python
def test_triggered_stop_market_reuses_market_fill_semantics() -> None:
    triggered = dormant.trigger(timestamp=60)
    fill = match_order(triggered, tick, costs)
    assert fill == ordinary_market_fill
```

**Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest -q tests/unit/trading/test_matching_and_state.py
```

Expected:

- failures for missing trigger predicate and missing executable-order reuse

**Step 3: Write minimal implementation**

Add narrow helpers in `matching.py`:

- `is_order_triggered(order, tick) -> bool`
- `triggered_orders_for_tick(...)` only if a tiny local helper materially
  reduces runtime duplication
- make `match_order()` operate on `order.executable_order_type` instead of raw
  `order.order_type`

Do **not** duplicate market-fill logic for `stop_market`.

**Step 4: Run test to verify it passes**

Run the same targeted command from Step 2.

Expected:

- PASS

**Step 5: Commit**

```bash
git add tests/unit/trading/test_matching_and_state.py src/quantcraft/trading/domain/matching.py
git commit -m "feat: add stop trigger predicates to matcher"
```

## Task 4: Make The Execution Model Emit Stop-Crossing Decisive Points

**Files:**
- Modify: `src/quantcraft/backtest/execution_model.py`
- Modify: `tests/unit/backtest/test_execution_model.py`

**Step 1: Write the failing tests**

Add tests that lock path compression behavior:

- active dormant `stop_market` above current path emits a decisive
  `trigger_price` point when the canonical segment crosses it
- active dormant `stop_market` below current path emits a decisive
  `trigger_price` point when the canonical segment crosses it
- gap-through stop triggers still happen at `open`, with no fabricated
  intermediate gap ticks
- limit-crossing behavior remains unchanged
- trigger tick is included in the emitted post-trigger path

Representative test examples:

```python
def test_rising_segment_emits_stop_crossing_tick() -> None:
    ticks = model.tick_events_for_bar(... active_orders=(stop_order,))
    assert tuple(tick.last for tick in ticks) == (100.0, 95.0, 110.0, 120.0, 118.0)
```

**Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest -q tests/unit/backtest/test_execution_model.py
```

Expected:

- failures because the current execution model only emits limit-crossing
  decisive prices

**Step 3: Write minimal implementation**

Generalize `_crossing_prices_for_segment()`:

- keep canonical path selection unchanged
- collect decisive prices from:
  - active resting limits
  - active dormant stop triggers
- sort and deduplicate by segment direction
- never fabricate intermediate gap ticks

**Step 4: Run test to verify it passes**

Run the same targeted command from Step 2.

Expected:

- PASS

**Step 5: Commit**

```bash
git add tests/unit/backtest/test_execution_model.py src/quantcraft/backtest/execution_model.py
git commit -m "feat: emit decisive stop crossings in execution model"
```

## Task 5: Integrate Stop-Market Ordering Into The Backtest Runtime Loop

**Files:**
- Modify: `src/quantcraft/backtest/strategy_runtime.py`
- Modify: `src/quantcraft/backtest/runtime.py`
- Modify: `src/quantcraft/trading/sizing.py`
- Modify: `tests/unit/backtest/test_order_sizing_activation.py`
- Modify: `tests/integration/research/support_backtest_runner.py`
- Modify: `tests/integration/research/test_backtest_execution_semantics.py`

**Step 1: Write the failing tests**

Add integration tests that lock runtime orchestration:

- bar-created stop orders activate on the next bar only
- `crosses_above` gap-through buy stop fills at the first executable `open`
- `crosses_below` gap-through buy stop fills at the first executable `open`
- `crosses_above` / `crosses_below` sell stops work the same way in long-only
  exit scope
- intrabar stop triggers fill on the same decisive point
- existing active orders keep priority ahead of newly triggered stops on the
  same point
- flat `sell(stop_market)` remains a no-op and does not leave a dormant order
- `qty_percent + stop_market` is rejected before activation
- ordinary `qty_percent` buy sizing does not treat dormant `stop_market` buys
  as already-marketable cash reservations

Representative integration fixtures:

```python
class GapUpStopEntryStrategy(Strategy):
    def on_bar(self, bar) -> None:
        self.buy(quantity=1.0, order_type="stop_market", stop_price=120.0, tag="entry")
```

```python
def test_backtest_runner_fills_gap_crossed_buy_stop_market_at_open() -> None:
    result = run_engine_backtest(...)
    assert tuple((fill.side, fill.price, fill.timestamp) for fill in result.trade_log) == (
        ("buy", 150.0, 120),
    )
```

**Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest -q tests/unit/backtest/test_order_sizing_activation.py tests/integration/research/test_backtest_execution_semantics.py
```

Expected:

- failures for missing stop activation, missing same-point runtime handling,
  and missing first-slice `%` sizing rejection

**Step 3: Write minimal implementation**

Update the runtime in two places.

In `strategy_runtime.py`:

- convert normalized pending requests into `OrderIntent(trigger_*)`

In `runtime.py`:

- split each tick into:
  1. already-executable order pass
  2. trigger detection pass for dormant stop orders
  3. same-point fill pass for newly triggered stop orders
- preserve active-order iteration order within each pass
- keep `_is_flat_exit_order()` behavior intact for long-only `sell` no-op

In `sizing.py`:

- keep the first-slice defer hard by ensuring dormant `stop_market` does not
  flow through ordinary market/limit buy-anchor reservation helpers
- add the narrowest logic that preserves current `%` sizing behavior for
  ordinary orders without implicitly inventing stop-aware reservation semantics

**Step 4: Run test to verify it passes**

Run the same targeted command from Step 2.

Expected:

- PASS

**Step 5: Commit**

```bash
git add tests/unit/backtest/test_order_sizing_activation.py tests/integration/research/support_backtest_runner.py tests/integration/research/test_backtest_execution_semantics.py src/quantcraft/backtest/strategy_runtime.py src/quantcraft/backtest/runtime.py
git commit -m "feat: wire stop-market orders into backtest runtime"
```

## Task 6: Add Canonical Stop-Market Regression Coverage

**Files:**
- Create: `tests/integration/research/test_canonical_stop_market_contract.py`
- Modify: `tests/integration/research/support_backtest_runner.py`

**Step 1: Write the failing test**

Add one or two cheap canonical regressions:

- one `crosses_above` entry workflow
- one `crosses_below` exit or entry workflow

Keep them small and deterministic, matching current repository regression
style.

**Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest -q tests/integration/research/test_canonical_stop_market_contract.py
```

Expected:

- FAIL until the support strategies or expectations are added correctly

**Step 3: Write minimal implementation**

Add only the strategy fixtures or helper data needed for the new regression
file.

**Step 4: Run test to verify it passes**

Run the same targeted command from Step 2.

Expected:

- PASS

**Step 5: Commit**

```bash
git add tests/integration/research/test_canonical_stop_market_contract.py tests/integration/research/support_backtest_runner.py
git commit -m "test: add canonical stop-market regressions"
```

## Task 7: Sync Shipped Docs To The New Public Contract

**Files:**
- Modify: `docs/product-specs/backtest-mvp.md`
- Modify: `docs/product-specs/research-ergonomics.md`
- Modify: `docs/product-specs/order-sizing.md`
- Modify: `docs/design-docs/backtest-execution-semantics.md` only if the
  shipped stop-crossing compression needs a governing clarification

**Step 1: Write the doc updates**

Sync only shipped truth:

- `stop_market` is now part of shipped backtest scope
- strategy surface accepts `stop_price` for `stop_market`
- stop-aware `%` sizing remains deferred
- same-point trigger/fill and stop-crossing decisive-path behavior are
  documented in the canonical language

**Step 2: Run repo-local doc verification**

Run:

```bash
uv run poe repo-check
```

Expected:

- PASS

**Step 3: Commit**

```bash
git add docs/product-specs/backtest-mvp.md docs/product-specs/research-ergonomics.md docs/product-specs/order-sizing.md docs/design-docs/backtest-execution-semantics.md
git commit -m "docs: document shipped stop-market contract"
```

## Task 8: Run Full Verification Before Review

**Files:**
- No code changes in this task.

**Step 1: Run targeted lanes**

```bash
uv run pytest -q tests/unit/trading/test_contracts.py tests/unit/trading/test_orders.py tests/unit/trading/test_matching_and_state.py tests/unit/backtest/test_execution_model.py tests/unit/backtest/test_order_sizing_activation.py tests/unit/research/test_strategy_surface.py tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_canonical_stop_market_contract.py
```

Expected:

- PASS

**Step 2: Run required repo-local gates**

```bash
uv run poe verify-runtime
uv run poe verify
uv run poe repo-check
```

Expected:

- all PASS

**Step 3: Review against the approved contracts**

Explicit review checklist:

- no trigger direction derived from `side` alone
- no stop-specific duplicated fill engine
- no pre-trigger path reused for post-trigger semantics
- no intermediate synthetic gap ticks
- no public `%` sizing support for `stop_market`
- no widening of public event exports beyond current `TickEvent`, `BarEvent`,
  and `FillEvent`

**Step 4: Final commit**

```bash
git status --short
```

Expected:

- only intended source, test, and docs changes remain

## Acceptance Notes For The Future Implementation Session

The future code session should not call this slice done unless all of the
following are true:

- `stop_market` works end-to-end from `Strategy.buy()/sell()` through
  `BacktestEngine.run(...)`
- trigger facts are durable runtime fields, not recomputed ad hoc from `side`
- stop-crossing decisive ticks are emitted by the backtest execution model
- same-point trigger/fill semantics are implemented with explicit ordering
- flat `sell(stop_market)` is still a no-op
- `qty_percent + stop_market` is still explicitly deferred

## Evaluator Review

- Findings:
  - This plan maps the approved stop spec and test matrix onto current source
    seams without reopening the core design.
  - The plan makes one tactical defer explicit: `qty_percent` remains unsupported
    for `stop_market` in the first shipped slice because current sizing anchors
    do not encode trigger-aware pricing semantics.
- Verification evidence:
  - `uv run poe repo-check`
    -> `repository checks passed`
- Final disposition:
  - `complete`
