# Stop-Limit Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement first-slice `stop_limit` orders for the current single-symbol
research/backtest workflow.

**Architecture:** Extend the existing stop-family and limit-order seams instead
of adding a parallel stop-limit engine. `trading` remains the shared order and
matching kernel; `backtest` remains the owner of OHLC path construction and
post-trigger causal traversal; `research` remains the public strategy-authoring
surface.

**Tech Stack:** Python 3.13, dataclasses, pytest, mypy, ruff, Poe/uv repo
verification.

---

# Active Plan

- Date: `2026-04-27`
- Task: `Implement stop_limit orders`
- Status: `implemented-pending-human-review`
- Risk class: `Tier A`
- Requestor: `Naki (thread user)`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Implement `order_type="stop_limit"` as a first-class stop-family order for
    current `Strategy.buy()` / `Strategy.sell()` and `BacktestEngine.run(...)`
    flows.
  - Preserve the product rule: dormant before trigger; after trigger, execute as
    an ordinary limit order; never reuse pre-trigger price movement to fill.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/design-docs/index.md`
  - `docs/SECURITY.md`
  - `docs/RELIABILITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/product-specs/stop-limit.md`
  - `docs/product-specs/order-sizing.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/design-docs/order-domain-runtime-design.md`
  - `docs/design-docs/order-lifecycle-and-sizing-design.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/plans/2026-04-27-stop-limit-test-scenarios.md`
- Why these are governing:
  - They define Tier A workflow, package ownership, product and design routing,
    current research/backtest scope, the stop-limit product contract, order
    lifecycle boundaries, sizing limits, and canonical OHLC execution semantics.
- In-repo scope:
  - Add `stop_limit` to the existing trading-domain order type surface.
  - Generalize existing `stop_market` trigger seams into stop-family helpers
    where this reduces hard-coded branching.
  - Extend strategy request validation and trigger-condition inference for
    `stop_limit`.
  - Extend conservative OHLC decisive-event traversal so a stop-limit can fill
    on same-point trigger or on the causal path tail after trigger.
  - Add focused unit and integration tests from the minimum implementation-ready
    batch in `docs/plans/2026-04-27-stop-limit-test-scenarios.md`.
  - Add a small canonical public stop-limit contract only after lower-layer
    behavior is stable.
- Out-of-repo scope:
  - None for implementation.
- Tier A progression requested: `yes`
- Approval record, if required:
  - Planning approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request on `2026-04-27` to move from finalized spec and
      test scenario documents into a concrete implementation plan after full
      codebase investigation.
    - Granted scope:
      docs-only implementation plan authoring, read-only in-repo codebase
      investigation, and read-only subagent review orchestration.
    - Expiration:
      end of this implementation-plan authoring slice.
    - Audit reference:
      this active plan.
  - Code implementation approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request on `2026-04-27` to implement from the finalized
      product spec, test scenario plan, and implementation plan; use
      `subagent-orchestration`; run thorough review; and report before commit
      so the human can inspect changes.
    - Granted scope:
      in-repository stop-limit implementation, tests, and active-plan evaluator
      updates limited to the source and test files listed in this plan.
    - Expiration:
      before any commit, PR, out-of-repo change, or scope expansion beyond this
      stop-limit implementation slice.
    - Audit reference:
      this active plan.
- Verification commands:
  - During TDD:
    - `uv run pytest tests/unit/trading/test_contracts.py -q`
    - `uv run pytest tests/unit/trading/test_orders.py -q`
    - `uv run pytest tests/unit/trading/test_matching_and_state.py -q`
    - `uv run pytest tests/unit/trading/test_sizing.py -q`
    - `uv run pytest tests/unit/research/test_strategy_surface.py -q`
    - `uv run pytest tests/unit/backtest/test_order_sizing_activation.py -q`
    - `uv run pytest tests/unit/backtest/test_execution_model.py -q`
    - `uv run pytest tests/integration/research/test_stop_limit_execution_semantics.py -q`
    - `uv run pytest tests/integration/research/test_canonical_stop_limit_contract.py -q`
  - Final:
    - `uv run poe repo-check`
    - `uv run poe verify-runtime`
    - `uv run poe verify`
- Success criteria:
  - All minimum implementation-ready scenarios from the test scenario plan have
    passing tests.
  - `stop_market`, `market`, `limit`, and supported `qty_percent` behavior do
    not regress.
  - `trading` remains bar-unaware.
  - `backtest` owns all OHLC path and causal tail traversal logic.
  - `qty_percent + stop_limit` is rejected in the first slice.
  - Trigger-only events do not appear in `BacktestResult.trade_log`.
  - Final verification commands pass and are recorded in the evaluator section.
- Out of scope:
  - `qty_percent + stop_limit`
  - stop-loss/take-profit aliases
  - bracket/OCO/OTO
  - trailing stop-limit
  - cancel/modify/replace
  - shorting, margin, leverage
  - multi-symbol or multi-timeframe behavior
  - paper/live trading
  - venue-specific trigger references beyond `last`
  - venue-specific price bands
  - public order-event or partial-fill contracts

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - The implementation is accepted only if it follows the active plan, preserves
    governing architecture boundaries, and has fresh verification evidence.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - Generator must execute tasks in TDD order, update this work log when scope
    changes, and preserve the success criteria above.
- Checks the evaluator will use:
  - Compare diff against `docs/product-specs/stop-limit.md`.
  - Compare test coverage against
    `docs/plans/2026-04-27-stop-limit-test-scenarios.md`.
  - Inspect source boundaries against `ARCHITECTURE.md` and
    `docs/design-docs/backtest-execution-semantics.md`.
  - Run the final verification command set.
- Auto-fail conditions:
  - `trading` imports or inspects `TimeBar`, `BarSeries`, OHLC values, or
    backtest execution-model internals.
  - Stop-limit duplicates limit matching instead of routing through existing
    limit semantics.
  - Pre-trigger OHLC movement can fill a stop-limit after later trigger.
  - `qty_percent + stop_limit` silently creates an order.
  - `stop_market` behavior changes without a test and explicit plan note.
  - Trigger-only events appear in public `trade_log`.
  - Final `verify-runtime` is skipped.

## Codebase Survey

### Package And Folder Placement

Do not add a new package or folder for stop-limit. Existing package ownership is
already adequate:

- `src/quantleet/trading/domain/`
  - shared order contracts, runtime order lifecycle, matching, and state
- `src/quantleet/trading/`
  - request normalization and sizing
- `src/quantleet/research/`
  - strategy authoring surface
- `src/quantleet/backtest/`
  - OHLC execution model, strategy activation, and backtest runtime
- `tests/unit/trading/`
  - local domain/request/sizing contracts
- `tests/unit/research/`
  - strategy surface contracts
- `tests/unit/backtest/`
  - activation and OHLC decisive-event contracts
- `tests/integration/research/`
  - public engine path contracts

This follows `docs/design-docs/package-topology-and-naming.md`: package names
stay capability-first, not order-type-specific.

### Current Stop-Market Flow

Current call flow before this implementation:

1. `Strategy.buy()` / `Strategy.sell()` accept `order_type`, `quantity`,
   `qty_percent`, `limit_price`, `stop_price`, and `tag` in
   `src/quantleet/research/strategy.py`.
2. `_infer_trigger_condition()` currently only accepts `stop_market`, rejects
   `qty_percent`, rejects missing/equal stop price, and compares `stop_price`
   with the active closed bar close.
3. `PendingOrderRequest` validates request shape in
   `src/quantleet/trading/order_requests.py`.
4. `_StrategyDriver.activate_pending_order_requests()` resolves sizing at next
   bar activation in `src/quantleet/backtest/strategy_runtime.py`.
5. `OrderIntent` and `Order` carry trigger fields plus `limit_price`, but
   validations currently reserve trigger facts for `stop_market` only.
6. `ConservativeOHLCVExecutionModel.tick_events_for_bar()` emits decisive ticks
   for active limits and dormant `stop_market` triggers.
7. `_run_backtest()` processes executable active orders first, then newly
   triggered dormant orders at the same event point.
8. `match_order()` already routes executable orders through market or limit
   matching based on `order.executable_order_type` and `order.limit_price`.

### Reusable Existing Functions And Classes

Reuse directly:

- `PendingOrderRequest` fields: `stop_price`, `trigger_condition`,
  `limit_price`, `tag`
- `OrderIntent` trigger and limit fields
- `Order` trigger and limit fields
- `Order.from_intent()`
- `Order.trigger()`, after generalizing it to stop-family orders
- `Order.is_triggered_by_price()`, after generalizing its error messages and
  guard from `stop_market` to stop-family
- `is_order_triggered()`, after recognizing dormant `stop_limit`
- `match_order()` and `_match_notional()` for ordinary limit execution
- `SizingConstraints`, `ResolvedOrderSizing`, `SizingReservations`
- `_StrategyDriver.activate_pending_order_requests()`
- `_run_backtest()` same-event priority loop
- `ConservativeOHLCVExecutionModel.infer_intrabar_prices()`

Add only small local helpers where they remove repeated branching, such as:

- `_is_stop_order_type(order_type: OrderType) -> bool`
- `_is_stop_limit_order_type(order_type: OrderType) -> bool`
- `_stop_limit_tail_crossing_price(order, start, end) -> float | None`

Keep helpers local to the owning module unless shared by multiple modules.

### Hard Part

Most of the implementation is straightforward generalization. The only
non-trivial part is `src/quantleet/backtest/execution_model.py`.

Current decisive events are computed from active orders at bar start. That works
for ordinary limits and stop-market triggers. For stop-limit, a dormant order
can become a working limit in the middle of a bar. If the trigger point is not
marketable but a later point on the same bar's causal path crosses the limit,
the execution model must include that post-trigger limit crossing without using
pre-trigger prices.

The implementation should keep the canonical path fixed, but extend traversal
so bar-local traversal can emit, in causal order:

1. existing ordinary limit crossings
2. dormant stop trigger crossings
3. for stop-limit only, a later limit crossing after the trigger point, whether
   that crossing occurs later in the same segment or in a later segment of the
   same bar

Do not materialize every price step. This remains a decisive-event compression
of the canonical path.

## Implementation Design

### Source Files To Modify

- `src/quantleet/trading/domain/intents.py`
  - Add `stop_limit` to `OrderType`.
  - Generalize validation into stop-family branches.
  - `stop_market`: require trigger facts, reject `limit_price`.
  - `stop_limit`: require trigger facts and `limit_price`.
  - Non-stop orders: reject trigger facts and `triggered_at` remains runtime
    only on `Order`.
- `src/quantleet/trading/domain/orders.py`
  - Mirror `OrderIntent` validation.
  - Dormant `stop_market` and dormant `stop_limit` are non-executable.
  - Triggered `stop_market` has executable type `market`.
  - Triggered `stop_limit` has executable type `limit`.
  - Trigger preserves order id, order type, trigger facts, limit price, tag, and
    filled quantity.
- `src/quantleet/trading/domain/matching.py`
  - `is_order_triggered()` recognizes untriggered stop-family orders.
  - `match_order()` should not need stop-limit-specific fill logic.
- `src/quantleet/trading/order_requests.py`
  - `stop_limit` requires `stop_price`, inferred `trigger_condition`, and
    `limit_price`.
  - `qty_percent + stop_limit` is rejected.
  - `stop_price` and `trigger_condition` are valid for stop-family orders only.
  - `trigger_type="last"` is assigned for stop-family order types.
- `src/quantleet/trading/sizing.py`
  - Explicit quantity `stop_limit` buy requests do not reserve ordinary cash
    before trigger in the first slice.
  - Dormant active buy `stop_limit` orders do not reduce ordinary percent-buy
    budget.
  - Triggered buy `stop_limit` orders reserve cash like ordinary buy limits.
- `src/quantleet/research/strategy.py`
  - Infer trigger condition for `stop_market` and `stop_limit`.
  - Preserve current public API; no new parameters.
  - Reject `qty_percent` for stop-family first-slice orders.
  - Error text should say "stop-family" or name the concrete order type when it
    helps users.
- `src/quantleet/backtest/execution_model.py`
  - Extend crossing-price discovery to stop-limit causal tail cases.
  - Keep `trading` bar-unaware.
- `src/quantleet/backtest/strategy_runtime.py`
  - Generalize flat sell no-op from `stop_market` to stop-family where needed.
  - Existing runtime processing should mostly work after order/matching
    generalization.
- `src/quantleet/backtest/runtime.py`
  - Keep same-event priority semantics.
  - Only change if tests show triggered-but-unfilled stop-limits are not carried
    forward correctly.
- `tests/support_backtest.py`
  - Add stop-limit canonical helper only if adding the canonical integration
    contract in this slice.
- `tests/integration/research/support_backtest_runner.py`
  - Add small class-per-scenario strategies for stop-limit integration tests.

### Test Files To Modify Or Add

- Modify `tests/unit/trading/test_contracts.py`
- Modify `tests/unit/trading/test_orders.py`
- Modify `tests/unit/trading/test_matching_and_state.py`
- Modify `tests/unit/trading/test_sizing.py`
- Modify `tests/unit/research/test_strategy_surface.py`
- Modify `tests/unit/backtest/test_order_sizing_activation.py`
- Modify `tests/unit/backtest/test_execution_model.py`
- Add `tests/integration/research/test_stop_limit_execution_semantics.py`
- Modify `tests/integration/research/support_backtest_runner.py`
- Add `tests/integration/research/test_canonical_stop_limit_contract.py`
- Modify `tests/support_backtest.py` only if the canonical contract needs shared
  helpers.

## Generator Work Log

- Planned slice order:
  1. Contract and request surface.
  2. Runtime order lifecycle.
  3. Matching delegation.
  4. Strategy surface.
  5. Sizing and activation guardrails.
  6. Execution-model causal traversal.
  7. Public engine integration.
  8. Canonical regression.
  9. Full verification and evaluator review.
- Notes:
  - Code implementation is intentionally not started in this authoring slice.
  - Subagent exploration confirmed the existing generalization is strong, but
    `execution_model.py` is the main semantic risk.
- Blockers or scope changes:
  - Code implementation requires the pending Tier A code implementation
    approval record to be filled before generator edits begin.

## TDD Task Plan

### Task 1: Order Type And Request Contract

**Files:**

- Modify: `tests/unit/trading/test_contracts.py`
- Modify: `tests/unit/trading/test_orders.py`
- Modify: `tests/unit/research/test_strategy_surface.py`
- Modify: `src/quantleet/trading/domain/intents.py`
- Modify: `src/quantleet/trading/order_requests.py`
- Modify: `src/quantleet/research/strategy.py`

**Step 1: Write failing tests**

Add tests that prove:

- `OrderType` includes `stop_limit`.
- `PendingOrderRequest(order_type="stop_limit", quantity=1.0, stop_price=105,
  limit_price=106, trigger_condition="crosses_above")` is accepted.
- Missing `stop_price`, missing `limit_price`, non-finite prices, non-positive
  prices, missing sizing, `qty_percent`, mixed sizing, and equality against
  reference last are rejected.
- Limit price does not affect trigger-condition inference.

Minimal strategy-surface cases:

```python
class StopLimitAboveCloseBuyStrategy(Strategy):
    def on_bar(self, bar: BarEvent) -> None:
        self.buy(
            quantity=1.0,
            order_type="stop_limit",
            stop_price=120.0,
            limit_price=121.0,
            tag="stop-limit-entry",
        )
```

Expected pending request:

```python
PendingOrderRequest(
    symbol="BTC/USDT",
    side="buy",
    quantity=1.0,
    order_type="stop_limit",
    stop_price=120.0,
    trigger_condition="crosses_above",
    limit_price=121.0,
    tag="stop-limit-entry",
)
```

**Step 2: Run failing tests**

Run:

```bash
uv run pytest tests/unit/trading/test_contracts.py tests/unit/research/test_strategy_surface.py -q
```

Expected:

- Failures show `stop_limit` is not in `OrderType` and current strategy
  validation treats `stop_price` as valid only for `stop_market`.

**Step 3: Implement minimal source changes**

- Add `"stop_limit"` to `OrderType`.
- In `PendingOrderRequest.__post_init__`, introduce stop-family validation.
- In `PendingOrderRequest.to_order_intent()`, set `trigger_type="last"` for
  stop-family orders.
- In `Strategy._infer_trigger_condition()`, treat `stop_market` and
  `stop_limit` as stop-family.
- Reject `qty_percent` for both stop-family types in the first slice.

**Step 4: Run tests**

```bash
uv run pytest tests/unit/trading/test_contracts.py tests/unit/research/test_strategy_surface.py -q
```

Expected: pass.

**Step 5: Do not commit unless the user asks**

The repo does not require per-task commits in this session.

### Task 2: Runtime Order Lifecycle

**Files:**

- Modify: `tests/unit/trading/test_orders.py`
- Modify: `src/quantleet/trading/domain/intents.py`
- Modify: `src/quantleet/trading/domain/orders.py`

**Step 1: Write failing tests**

Add tests that prove:

- `OrderIntent(order_type="stop_limit")` requires trigger facts and
  `limit_price`.
- `Order.from_intent()` preserves `trigger_price`, `trigger_condition`,
  `trigger_type`, `limit_price`, and `tag`.
- Dormant stop-limit is open, untriggered, and not executable.
- `trigger(timestamp=...)` preserves order id and `order_type="stop_limit"`.
- Triggered stop-limit becomes executable with `executable_order_type=="limit"`.
- `apply_fill()` rejects dormant stop-limit fills and accepts triggered fills.

**Step 2: Run failing tests**

```bash
uv run pytest tests/unit/trading/test_orders.py -q
```

Expected: stop-limit construction or lifecycle tests fail.

**Step 3: Implement minimal source changes**

- Generalize order validation into stop-family helper logic.
- Keep `stop_market` rejecting `limit_price`.
- Require `stop_limit.limit_price`.
- Change `is_executable`, `executable_order_type`,
  `is_triggered_by_price()`, and `trigger()` to support stop-family orders.

**Step 4: Run tests**

```bash
uv run pytest tests/unit/trading/test_orders.py -q
```

Expected: pass.

### Task 3: Matching Delegation

**Files:**

- Modify: `tests/unit/trading/test_matching_and_state.py`
- Modify: `src/quantleet/trading/domain/matching.py`
- Modify: `src/quantleet/trading/domain/orders.py` only if Task 2 missed a
  lifecycle helper.

**Step 1: Write failing tests**

Add tests for Catalog B1-B6:

- dormant buy/sell stop-limit returns `None` even when ordinary limit would
  fill
- triggered buy stop-limit equals ordinary buy limit matching
- triggered sell stop-limit equals ordinary sell limit matching
- triggered buy/sell stop-limit remains unfilled when price is worse than limit
- `is_order_triggered()` returns true for dormant stop-limit on equality and
  false after it is already triggered

**Step 2: Run failing tests**

```bash
uv run pytest tests/unit/trading/test_matching_and_state.py -q
```

Expected: trigger detection ignores stop-limit until generalized.

**Step 3: Implement minimal source changes**

- Make `is_order_triggered()` recognize dormant stop-family orders.
- Leave `match_order()` without stop-limit-specific branches unless a failing
  test proves a gap.

**Step 4: Run tests**

```bash
uv run pytest tests/unit/trading/test_matching_and_state.py -q
```

Expected: pass.

### Task 4: Sizing And Activation Guardrails

**Files:**

- Modify: `tests/unit/trading/test_sizing.py`
- Modify: `tests/unit/backtest/test_order_sizing_activation.py`
- Modify: `src/quantleet/trading/sizing.py`
- Modify: `src/quantleet/backtest/strategy_runtime.py`

**Step 1: Write failing tests**

Add tests that prove:

- `qty_percent + stop_limit` is rejected before runtime order creation.
- dormant active buy stop-limit does not reduce ordinary percent-buy budget.
- triggered active buy stop-limit reserves cash like an ordinary active limit.
- flat sell stop-limit activation does not leave a dormant short-entry order.

**Step 2: Run failing tests**

```bash
uv run pytest tests/unit/trading/test_sizing.py tests/unit/backtest/test_order_sizing_activation.py -q
```

Expected: dormant stop-limit reservation and flat sell guards fail until
generalized.

**Step 3: Implement minimal source changes**

- In `_resolve_quantity_request()`, treat explicit-quantity dormant buy
  stop-limit like dormant stop-market for first-slice cash reservation.
- In `_active_buy_cash_reservation()`, skip dormant stop-family buy orders.
- Ensure triggered buy stop-limit falls through to limit anchor price.
- Generalize `_StrategyDriver` flat sell stop guard to stop-family orders.

**Step 4: Run tests**

```bash
uv run pytest tests/unit/trading/test_sizing.py tests/unit/backtest/test_order_sizing_activation.py -q
```

Expected: pass.

### Task 5: Execution Model Causal Traversal

**Files:**

- Modify: `tests/unit/backtest/test_execution_model.py`
- Modify: `src/quantleet/backtest/execution_model.py`

**Step 1: Write failing tests**

Add execution-model tests for:

- stop-limit trigger decisive ticks are emitted for crosses above and below.
- same-point trigger/fill eligibility emits the trigger price.
- pre-trigger low/high does not emit a stop-limit limit crossing before trigger.
- post-trigger tail emits the later limit crossing in causal order:
  - buy path `80 -> 70 -> 105 -> 106 -> 95 -> 90` as compressed decisive
    ticks for stop `105`, limit `95`
  - sell path `120 -> 130 -> 95 -> 94 -> 105 -> 110` as compressed decisive
    ticks for stop `95`, limit `105`
- ordinary limit and stop-market decisive-event behavior remains unchanged.

**Step 2: Run failing tests**

```bash
uv run pytest tests/unit/backtest/test_execution_model.py -q
```

Expected: post-trigger tail tests fail because current traversal only sees
active orders at segment start.

**Step 3: Implement minimal source changes**

Preferred design:

- keep `infer_intrabar_prices()` as the canonical path source
- introduce or refactor toward a bar-level traversal helper owned by
  `ConservativeOHLCVExecutionModel.tick_events_for_bar()`
- traverse the bar's canonical segments in order inside that helper
- do not rely on independent `_crossing_prices_for_segment()` calls with only
  the original `active_orders` snapshot; that shape cannot remember that a
  stop-limit triggered earlier in the same bar
- carry a bar-local view of stop-limit orders that have hypothetically
  triggered earlier in this same synthetic path construction
- collect candidate prices in path order
- for ordinary limits, keep existing behavior
- for dormant stop-family orders, add trigger crossing when the trigger is
  crossed after the current segment start
- for dormant stop-limit orders, if trigger is crossed:
  - use the trigger crossing as the tail start
  - if the trigger price is already marketable against the limit, no extra
    limit crossing is needed
  - otherwise, continue evaluating only the path after that trigger point for a
    later limit crossing
- sort and de-duplicate only within the current monotonic segment, or use an
  explicit `(segment_index, path_position)` ordering if collecting candidates
  across segments
- never reorder candidates across canonical segment boundaries

Do not inspect bars in `trading`. Do not insert prices outside the canonical
path.

**Step 4: Run tests**

```bash
uv run pytest tests/unit/backtest/test_execution_model.py -q
```

Expected: pass.

### Task 6: Engine Integration Semantics

**Files:**

- Add: `tests/integration/research/test_stop_limit_execution_semantics.py`
- Modify: `tests/integration/research/support_backtest_runner.py`
- Modify: `src/quantleet/backtest/runtime.py` only if needed.
- Modify: previous source files only if integration exposes a lower-layer gap.

**Step 1: Write failing tests**

Add class-per-scenario strategies in `support_backtest_runner.py` or local test
classes for:

- C1 buy gap-through within limit fills at open
- C2 buy gap-through beyond limit triggers but does not fill
- C3 buy same-point trigger/fill
- C5 buy post-trigger tail fill at limit
- C6 buy pullback-style stop-limit
- D1 sell gap-through within limit fills at open
- D2 sell gap-through beyond limit triggers but does not fill
- D3 sell same-point trigger/fill
- D5 sell post-trigger tail fill at limit
- D6 sell take-profit-style stop-limit
- E2 later bar fills triggered working limit
- E3 existing executable order appears before newly triggered stop-limit in
  public fill ordering when cash is sufficient
- E4 source-based run path matches bars-based semantics
- E5 flat sell stop-limit does not become a short entry

**Step 2: Run failing tests**

```bash
uv run pytest tests/integration/research/test_stop_limit_execution_semantics.py -q
```

Expected: failures should identify any runtime carry-forward or event-ordering
gaps.

**Step 3: Implement minimal source changes**

- Prefer no change to `runtime.py` if Task 2/3 made triggered unfilled
  stop-limits remain open naturally.
- If needed, adjust only the active-order replacement logic so triggered but
  unfilled stop-limits stay active.
- Preserve existing executable-before-newly-triggered processing.

**Step 4: Run tests**

```bash
uv run pytest tests/integration/research/test_stop_limit_execution_semantics.py -q
```

Expected: pass.

### Task 7: Canonical Stop-Limit Public Contract

**Files:**

- Add: `tests/integration/research/test_canonical_stop_limit_contract.py`
- Modify: `tests/support_backtest.py` only if helper reuse is valuable.

**Step 1: Write failing tests**

Add a small synthetic canonical public contract first, not a BTC fixture digest
matrix:

- buy stop-limit trigger-and-fill
- buy stop-limit trigger-without-fill
- sell stop-limit trigger-and-fill
- sell stop-limit trigger-without-fill

Assert public outcomes:

- fill count
- fill timestamps
- fill side
- fill price
- final position
- trigger-only absence from `trade_log`

**Step 2: Run failing tests**

```bash
uv run pytest tests/integration/research/test_canonical_stop_limit_contract.py -q
```

Expected: should pass if prior integration is complete; otherwise expose public
contract gaps.

**Step 3: Implement minimal source changes**

- Prefer test/helper-only changes in this task.
- Do not add fixture-backed digest helpers unless the synthetic canonical tests
  are too weak to protect public behavior.

**Step 4: Run tests**

```bash
uv run pytest tests/integration/research/test_canonical_stop_limit_contract.py -q
```

Expected: pass.

### Task 8: Regression And Full Verification

**Files:**

- Modify: this plan's `Evaluator Review` section.

**Step 1: Run focused regression**

```bash
uv run pytest tests/unit/trading tests/unit/backtest tests/unit/research/test_strategy_surface.py -q
uv run pytest tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_stop_limit_execution_semantics.py tests/integration/research/test_canonical_stop_limit_contract.py -q
```

Expected: pass.

**Step 2: Run repo checks**

```bash
uv run poe repo-check
```

Expected: pass.

**Step 3: Run runtime-sensitive verification**

```bash
uv run poe verify-runtime
```

Expected: pass.

**Step 4: Run default verification**

```bash
uv run poe verify
```

Expected: pass.

**Step 5: Evaluator review**

Record:

- findings first
- verification evidence
- final disposition

## Evaluator Review

- Findings:
  - No blocking findings remain in the implementation diff.
  - Review finding resolved:
    execution-model guidance now requires bar-level traversal state for
    stop-limit orders triggered earlier in the same bar, so C5/D5 post-trigger
    tail fills are implementable without reusing pre-trigger prices.
  - Review finding resolved:
    causal tail examples now preserve canonical OHLC segment order.
  - Review finding resolved:
    the plan explicitly includes no-sizing `stop_limit` validation.
  - Review finding resolved:
    the governing-doc list now includes the AGENTS-required routing docs
    `docs/product-specs/index.md`, `docs/design-docs/index.md`, and
    `docs/DESIGN.md`.
  - Review finding resolved during implementation:
    same-segment stop-limit tail crossings are now covered and implemented for
    buy `crosses_below` and sell `crosses_above` cases, preventing optimistic
    endpoint fills after an in-segment trigger.
  - Review finding resolved during implementation:
    `PendingOrderRequest` now rejects `qty_percent + stop_limit` during order
    normalization instead of allowing the request to fail later in sizing.
  - Review finding resolved during implementation:
    stop-limit runtime validation tests now cover missing trigger price,
    trigger condition, trigger type, and limit price.
  - Review finding resolved during implementation:
    limit-price-independent trigger inference tests now cover buy/sell variants
    where the stop is below the reference last and a sell-above-reference case.
  - Review finding resolved during implementation:
    same-event priority tests now distinguish the already executable limit
    order from the newly triggered stop-limit order by fill quantity.
  - Review finding resolved during implementation:
    canonical public stop-limit tests now assert fill quantity in addition to
    side, price, timestamp, fill count, and final position.
  - Residual gate:
    implementation is intentionally not committed; user requested a report
    before commit for direct human review.
- Verification evidence:
  - Focused unit regression:
    `uv run pytest tests/unit/trading tests/unit/backtest tests/unit/research/test_strategy_surface.py -q`
    - `151 passed in 0.10s`
  - Focused integration regression:
    `uv run pytest tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_stop_limit_execution_semantics.py tests/integration/research/test_canonical_stop_limit_contract.py -q`
    - `39 passed in 0.05s`
  - `uv run poe repo-check`
    - `Poe => uv run python scripts/repo_check.py`
    - `repository checks passed`
  - `git diff --check`
    - passed with no output
  - `uv run poe verify-runtime`
    - `ruff check .`
    - `All checks passed!`
    - `mypy src`
    - `Success: no issues found in 51 source files`
    - `pytest -q`
    - `448 passed, 3 skipped`
    - `coverage policy check passed`
    - `uv build` built sdist and wheel successfully
    - `repository checks passed`
    - notebooks validated:
      `binance-spot-usdm-validation.ipynb`,
      `binance-usdm-rsi-2024-ad-hoc.ipynb`,
      `research-ergonomics-quickstart.ipynb`,
      `spot-cross-exchange-price-comparison.ipynb`
    - performance check:
      `tests/perf/test_rsi_backtest_benchmark.py -q -x --run-perf`
      `2 passed`
  - `uv run poe verify`
    - `ruff check .`
    - `All checks passed!`
    - `mypy src`
    - `Success: no issues found in 51 source files`
    - `pytest -q`
    - `448 passed, 3 skipped`
    - `coverage policy check passed`
    - `uv build` built sdist and wheel successfully
    - `repository checks passed`
    - notebooks validated:
      `binance-spot-usdm-validation.ipynb`,
      `binance-usdm-rsi-2024-ad-hoc.ipynb`,
      `research-ergonomics-quickstart.ipynb`,
      `spot-cross-exchange-price-comparison.ipynb`
- Final disposition:
  - Implementation is ready for human review before commit.
