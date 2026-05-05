# Order Reservation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement uniform `qty_percent` support for market, limit, stop-market, and stop-limit orders with conservative reservation, explicit rejection events, and behavior-first test coverage.

**Architecture:** The implementation keeps `qty_percent` at the strategy/request boundary, resolves it into fixed runtime `Order.quantity`, and places reservation/rejection ownership in the backtest runtime account-control layer. Domain `Order` remains responsible only for order invariants.

**Tech Stack:** Python, dataclasses, pytest, Ruff, mypy, uv, Poe task runner.

---

## Repo Workflow Planner Contract

- Date: `2026-04-29`
- Task: `Implement the order reservation and stop-family percent sizing slice`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `Naki (thread user)`
- Owner: `Codex`

### Planner Contract

- Goal:
  - Implement the accepted order reservation product spec and test scenario
    artifact.
  - Keep this document as the active planner/generator/evaluator artifact for
    the implementation slice.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/order-reservation.md`
  - `docs/product-specs/order-sizing.md`
  - `docs/product-specs/stop-limit.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/order-lifecycle-and-sizing-design.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-29-order-reservation-test-scenarios.md`
  - `docs/plans/2026-04-29-order-reservation-spec-review.md`
- Why these are governing:
  - They define repository workflow, architecture boundaries, package topology,
    product behavior, backtest execution semantics, test strategy, and the
    accepted human decisions for this Tier A trading slice.
- In-repo scope:
  - Implement the order reservation and rejection behavior described in this
    plan.
  - Add and update behavior-first tests for strategy intake, sizing,
    activation, runtime execution, result reporting, and documentation status.
  - Update product specs only where implementation changes make older status
    notes stale.
- Out-of-repo scope:
  - None.
- Tier A progression requested: `yes`
- Approval record, if required:
  - Requestor: `Naki (thread user)`
  - Human approver: `Naki (thread user)`
  - Verification marker:
    explicit thread request on `2026-04-29` to write the concrete implementation
    plan after full codebase investigation.
  - Granted scope:
    Tier A implementation of conservative order reservation and rejection
    behavior in `src/quantleet/trading`, `src/quantleet/backtest`,
    `src/quantleet/research`, focused unit and integration tests, and product
    documentation status updates for `qty_percent` support across `market`,
    `limit`, `stop_market`, and `stop_limit`.
  - Expiration:
    end of this `2026-04-29` implementation-plan slice.
  - Audit reference:
    this active plan.
- Verification commands:
  - focused red/green pytest commands listed in each task
  - `uv run pytest tests/unit/trading tests/unit/backtest tests/unit/research tests/integration/research -q`
  - `uv run ruff check .`
  - `uv run mypy src`
  - `uv run python scripts/coverage_check.py`
  - `uv run python scripts/repo_check.py`
  - `uv build`
  - `uv run poe verify-runtime`
- Success criteria:
  - The implementation follows this how-focused plan with TDD evidence.
  - The touched source and test files match the architecture boundaries
    identified here unless evaluator review records a justified deviation.
  - The plan preserves the accepted product decisions: no trigger-time percent
    recalculation, explicit validation errors for invalid shape, explicit
    rejection events for runtime/account failures, and account-control ownership
    for reservation.
  - Focused tests and final verification pass or any unavailable verification
    is explicitly reported.
- Out of scope:
  - Expanding beyond the approved single-symbol long-only backtest/research
    scope.
  - Live trading, paper trading, margin, leverage, shorts, cancel/replace,
    OCO/OTO/bracket orders, trailing stops, reduce-only, post-only, or
    time-in-force.

### Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Close only after the implementation plan is grounded in current repository
    structure and after fresh repository-document verification passes.
- Acceptance artifact location:
  - `docs/plans/2026-04-29-order-reservation-implementation-plan.md`
- How the generator and evaluator agreed on done before execution:
  - The document must tell a future implementer what to change, in what order,
    how to test each step, and where the architecture boundaries are.
- Checks the evaluator will use:
  - Compare against accepted product and test-scenario docs.
  - Compare against current source and test layout.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - prescribing trigger-time percent recalculation
  - moving `qty_percent` into runtime `Order`
  - putting reservation ownership into domain `Order`
  - allowing silent no-op rejection paths
  - omitting TDD steps or verification commands
  - changing files outside the granted implementation scope

### Generator Work Log

- Planned slice order:
  1. Read governing docs and accepted decisions.
  2. Survey source and tests for strategy order requests, order intents, domain
     orders, backtest execution, result surfaces, and existing validation.
  3. Identify reusable code and gaps.
  4. Write the concrete implementation plan.
  5. Run `uv run poe repo-check`.
  6. Record evaluator findings and final disposition.
- Notes:
  - This document began as the how-focused implementation plan and became the
    active implementation/evaluation artifact for the current work slice.
- Blockers or scope changes:
  - During codebase review, one stale product-spec sentence still allowed
    "no order or explicit rejection" for over-budget explicit quantity buys.
    It was corrected to require an explicit rejection event before this
    implementation plan was finalized.

## Repository Research Summary

### Technology And Infrastructure

- Language and runtime:
  - Python `>=3.13`
  - strict `mypy`
  - `ruff` formatting and linting
  - `pytest` with unit, integration, structure, smoke, and perf lanes
- Package and task tooling:
  - `uv`
  - Poe task runner
  - `uv_build`
- Runtime shape:
  - installable local-first library under `src/quantleet`
  - no web server, database, queue, or HTTP API surface in the current package
- Default verification:
  - `uv run poe verify`
  - runtime-sensitive backtest or research changes must also use
    `uv run poe verify-runtime`
  - this implementation slice uses focused tests plus `uv run poe verify-runtime`

### Architecture And Structure

The codebase follows a capability-first package topology:

- `quantleet.trading` owns shared trading kernel concepts.
- `quantleet.trading.domain` owns order, fill, matching, cost, and state
  invariants.
- `quantleet.trading.sizing` already owns shared sizing policy functions
  outside the domain-order object.
- `quantleet.research` owns strategy authoring ergonomics.
- `quantleet.backtest` owns historical runtime orchestration, synthetic OHLCV
  execution, and result assembly.

Important boundary findings:

- `trading` must not depend on `research`, `backtest`, `execution`, or
  `integrations`.
- `backtest` may depend on `trading`.
- `research` may depend on `trading` and public `backtest` surfaces.
- Domain `Order` already owns many invariants and execution-local transitions,
  but it must not absorb cash, margin, or reservation fields.
- Reservation and rejection orchestration should therefore sit in `backtest`
  runtime/account-control code while using reusable sizing policy from
  `trading.sizing`.

### Current Code Path

The current order path is:

```text
Strategy.buy/sell
  -> PendingOrderRequest
  -> _StrategyDriver.activate_pending_order_requests
  -> resolve_pending_order_request
  -> PendingOrderRequest.to_order_intent
  -> Order.from_intent
  -> ConservativeOHLCVExecutionModel tick events
  -> match_order
  -> apply_fill
  -> BacktestResult(trade_log, equity_curve, final_state, summary)
```

Current source evidence:

- `Strategy.buy()` / `Strategy.sell()` already expose `qty_percent`,
  `order_type`, `limit_price`, and `stop_price` at
  `src/quantleet/research/strategy.py:80`.
- `Strategy._infer_trigger_condition()` currently rejects `qty_percent` for
  all stop-family orders at `src/quantleet/research/strategy.py:188`.
- `PendingOrderRequest` validates exactly one sizing mode and validates
  `0 < qty_percent <= 100`, but currently rejects
  `qty_percent + stop_limit` at
  `src/quantleet/trading/order_requests.py:44`.
- `OrderIntent` does not yet validate positive finite quantity at
  `src/quantleet/trading/domain/intents.py:24`.
- `Order` validates positive quantity, stop-family fields, and illegal dormant
  fills at `src/quantleet/trading/domain/orders.py:31`.
- `_StrategyDriver.activate_pending_order_intents()` currently skips
  `ResolvedOrderSizing.is_noop` without emitting a public event at
  `src/quantleet/backtest/strategy_runtime.py:89`.
- `trading.sizing` already has `SizingReservations`, `ResolvedOrderSizing`,
  buy/sell percent resolution, same-cycle reservation, rounding, fee-aware
  affordability, and active-order reservation helpers at
  `src/quantleet/trading/sizing.py:28`.
- `_active_buy_cash_reservation()` currently excludes dormant stop-family buy
  orders at `src/quantleet/trading/sizing.py:235`.
- `_buy_anchor_price()` currently rejects stop-family buy requests at
  `src/quantleet/trading/sizing.py:270`.
- `_resolve_quantity_request()` currently returns quantity-only for buy
  stop-family orders and does not reserve cash at
  `src/quantleet/trading/sizing.py:108`.
- `_run_backtest()` applies fills directly and would currently rely on
  `TradingState.apply_fill()` raising if a buy is unaffordable at
  `src/quantleet/backtest/runtime.py:76`.
- `BacktestResult` currently has no order-event or rejection-event surface at
  `src/quantleet/backtest/results.py:42`.

### Existing Tests To Preserve And Extend

Reusable test locations:

- `tests/unit/research/test_strategy_surface.py`
  - strategy API validation and pending request creation
- `tests/unit/trading/test_contracts.py`
  - dataclass field contracts and exported event surfaces
- `tests/unit/trading/test_orders.py`
  - domain `Order` and `OrderIntent` invariants
- `tests/unit/trading/test_sizing.py`
  - sizing anchors, rounding, affordability, active reservation math
- `tests/unit/backtest/test_order_sizing_activation.py`
  - `_StrategyDriver` activation and same-cycle request behavior
- `tests/unit/backtest/test_execution_model.py`
  - synthetic OHLCV decisive-event behavior
- `tests/integration/research/test_order_sizing_contract.py`
  - public backtest sizing behavior
- `tests/integration/research/test_stop_limit_execution_semantics.py`
  - stop-limit trigger/fill behavior and same-event priority
- `tests/integration/research/test_backtest_result_contract.py`
  - public result object contract

Some existing tests intentionally assert old behavior and must be rewritten
rather than preserved:

- dormant stop buy orders not reducing ordinary percent buy budget
- quantity-based stop-limit buy not reserving cash before trigger
- flat sell stop-limit resolving to no new order without a rejection event
- `qty_percent + stop_limit` rejection
- `qty_percent + stop_market` strategy-surface rejection

## Implementation Design

### Chosen Approach

Use the existing policy-function style rather than introducing a full OMS or
event bus.

The implementation should:

- keep `qty_percent` only on `PendingOrderRequest`
- keep runtime `Order` quantity-based
- extend `trading.sizing` so all four order types share one anchor and
  affordability policy
- add a small explicit rejection event model
- make `_StrategyDriver` turn valid runtime/account failures into rejection
  events instead of silent skips
- make `_run_backtest` check execution affordability before applying fills
- expose rejection events on `BacktestResult` without adding accept, trigger,
  cancel, or amend events in this slice

Do not create a global message bus. The runtime loop should remain explicit and
synchronous: compute sizing, accept or reject, match, then apply or reject.

### Event Surface

Add an explicit event for runtime/account failures:

```python
OrderRejectionReason = Literal[
    "insufficient_cash",
    "insufficient_position",
    "below_minimum_size",
    "below_minimum_cost",
    "no_buy_budget_available",
    "no_closable_position",
    "buy_budget_unaffordable",
    "execution_affordability",
]

@dataclass(frozen=True, slots=True)
class OrderRejectedEvent:
    symbol: str
    side: OrderSide
    order_type: OrderType
    reason: OrderRejectionReason
    timestamp: int
    quantity: float | None = None
    order_id: int | None = None
    tag: str | None = None
```

Rationale:

- invalid input still raises `ValueError` and does not become an event
- valid runtime/account failures become durable result data
- activation-time rejection can use `order_id=None`
- trigger/fill-time rejection can use the existing runtime `order.id`
- this keeps event data stable without adding a full `OrderEvent` hierarchy

Expose it through:

```python
@dataclass(frozen=True, slots=True)
class BacktestResult:
    trade_log: tuple[FillEvent, ...]
    equity_curve: tuple[float, ...]
    final_state: TradingState
    summary: BacktestSummary
    order_events: tuple[OrderRejectedEvent, ...] = ()
    execution_model_name: str = field(default="conservative_ohlcv", compare=False, repr=False)
```

### Sizing And Reservation Policy

Update `trading.sizing` around the existing `ResolvedOrderSizing` and
`SizingReservations` types.

Buy-side anchor policy:

```text
market      -> market_buy_price + slippage
limit       -> limit_price
stop_market -> stop_price + slippage
stop_limit  -> limit_price
```

Sell-side quantity policy:

```text
market / limit / stop_market / stop_limit
  -> percentage of unreserved long position
```

Explicit quantity requests:

- buy requests are never resized down
- if required cash exceeds available cash after active reservations and
  same-cycle reservations, return `ResolvedOrderSizing(quantity=None,
  reason="insufficient_cash")`
- sell requests are never resized down
- if quantity exceeds unreserved long position, return
  `ResolvedOrderSizing(quantity=None, reason="insufficient_position")`

Percent requests:

- buy requests may clamp only as percent affordability clamping
- sell requests use unreserved long position quantity
- subminimum results return stable reasons and become rejection events

Dormant stop-family orders:

- count in active buy cash reservations
- count in active sell quantity reservations
- remain non-executable until triggered

### Runtime Account-Control Responsibility

Keep account-control behavior in backtest runtime orchestration. Do not move it
into `Order`.

Implementation should start with helper functions or a small dataclass in
`src/quantleet/backtest/strategy_runtime.py` and
`src/quantleet/backtest/runtime.py`. Only extract a new
`src/quantleet/backtest/account.py` if the code becomes clearer after tests
force the shape.

Minimum runtime behavior:

- activation-time sizing `reason` becomes `OrderRejectedEvent`
- flat or over-reserved exits become `OrderRejectedEvent`
- rejected requests do not create `Order`
- rejected requests do not create phantom reservations
- fill-time buy affordability is checked before `apply_fill`
- if a triggered buy `stop_market` gaps beyond affordability:
  - emit `OrderRejectedEvent(reason="execution_affordability", order_id=...)`
  - do not apply fill
  - do not leave the order active
  - do not allow negative cash
  - do not partial-fill solely due to cash shortage

## Implementation Tasks

### Task 1: Add Rejection Event And Result Surface

**Files:**

- Modify: `src/quantleet/trading/domain/events.py`
- Modify: `src/quantleet/trading/domain/__init__.py`
- Modify: `src/quantleet/backtest/results.py`
- Modify: `src/quantleet/backtest/__init__.py` only if public export is needed
- Test: `tests/unit/trading/test_contracts.py`
- Test: `tests/integration/research/test_backtest_result_contract.py`

**Step 1: Write failing event contract tests**

Add a focused test to `tests/unit/trading/test_contracts.py`:

```python
def test_order_rejected_event_matches_runtime_rejection_contract() -> None:
    event_fields = fields(OrderRejectedEvent)

    assert tuple(field.name for field in event_fields) == (
        "symbol",
        "side",
        "order_type",
        "reason",
        "timestamp",
        "quantity",
        "order_id",
        "tag",
    )
```

Update the existing event export test so `OrderRejectedEvent` is no longer in
the deferred set.

**Step 2: Run the focused failing test**

Run:

```bash
uv run pytest tests/unit/trading/test_contracts.py -q
```

Expected:

- fail because `OrderRejectedEvent` is not defined or exported

**Step 3: Add the event dataclass**

Implement the event in `src/quantleet/trading/domain/events.py` using
`dataclass(frozen=True, slots=True)` and `Literal` reason codes.

Export it from `src/quantleet/trading/domain/__init__.py`.

**Step 4: Add result surface**

Add `order_events: tuple[OrderRejectedEvent, ...] = ()` to `BacktestResult`.
Keep the default empty tuple so existing tests that construct `BacktestResult`
directly do not need to pass the field unless they assert rejection behavior.

**Step 5: Verify**

Run:

```bash
uv run pytest tests/unit/trading/test_contracts.py tests/integration/research/test_backtest_result_contract.py -q
```

Expected:

- pass after tests are updated for the new public event surface

### Task 2: Tighten Domain Validation And Unlock Percent Stop-Family Intake

**Files:**

- Modify: `src/quantleet/research/strategy.py`
- Modify: `src/quantleet/trading/order_requests.py`
- Modify: `src/quantleet/trading/domain/intents.py`
- Modify: `src/quantleet/trading/domain/orders.py`
- Test: `tests/unit/research/test_strategy_surface.py`
- Test: `tests/unit/trading/test_contracts.py`
- Test: `tests/unit/trading/test_orders.py`

**Step 1: Write failing strategy-surface tests**

Add or rewrite tests so these calls are accepted into pending requests:

```python
self.buy(qty_percent=50.0, order_type="stop_market", stop_price=120.0)
self.buy(qty_percent=50.0, order_type="stop_limit", stop_price=120.0, limit_price=121.0)
self.sell(qty_percent=50.0, order_type="stop_market", stop_price=90.0)
self.sell(qty_percent=50.0, order_type="stop_limit", stop_price=90.0, limit_price=89.0)
```

Expected pending requests should preserve `qty_percent` and inferred
`trigger_condition`.

**Step 2: Write failing validation parity tests**

Add tests that `OrderIntent(quantity=0.0, ...)`,
`OrderIntent(quantity=float("nan"), ...)`, `Order(quantity=0.0, ...)`, and
`Order(quantity=float("nan"), ...)` raise `ValueError`.

**Step 3: Run focused tests**

Run:

```bash
uv run pytest tests/unit/research/test_strategy_surface.py tests/unit/trading/test_orders.py -q
```

Expected:

- stop-family percent tests fail because the current strategy and request
  layers reject them
- quantity invariant tests fail if `OrderIntent` or `Order` accepts non-finite
  values

**Step 4: Implement minimal changes**

- Remove `qty_percent` from the `_infer_trigger_condition()` signature and
  remove the stop-family percent rejection.
- Remove the `qty_percent + stop_limit` rejection from
  `PendingOrderRequest.__post_init__`.
- Add positive finite quantity validation to `OrderIntent`.
- Strengthen `Order` quantity and `filled_quantity` validation to reject
  non-finite values.

**Step 5: Verify**

Run:

```bash
uv run pytest tests/unit/research/test_strategy_surface.py tests/unit/trading/test_contracts.py tests/unit/trading/test_orders.py -q
```

Expected:

- pass
- `qty_percent` remains absent from `OrderIntent` and `Order`

### Task 3: Implement Four-Order-Type Sizing Anchors

**Files:**

- Modify: `src/quantleet/trading/sizing.py`
- Test: `tests/unit/trading/test_sizing.py`

**Step 1: Write failing anchor tests**

Cover the product anchors directly:

```python
def test_buy_percent_stop_market_uses_stop_price_plus_slippage() -> None:
    result = resolve_pending_order_request(
        request=PendingOrderRequest(
            symbol="BTC/USDT",
            side="buy",
            qty_percent=50.0,
            order_type="stop_market",
            stop_price=25.0,
            trigger_condition="crosses_above",
        ),
        state=TradingState(cash=100.0, equity=100.0),
        active_orders=(),
        market_buy_price=10.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=1.0, fee_rate=0.0),
    )

    assert result.quantity == pytest.approx(50.0 / 26.0)
    assert result.cash_consumption == pytest.approx(50.0)
```

Add companion tests for:

- `buy(qty_percent=50, stop_limit, stop_price=25, limit_price=20)` -> `2.5`
- `buy(qty_percent=50, stop_limit, stop_price=25, limit_price=30)` -> `50 / 30`
- ordinary market slippage still uses market anchor
- ordinary limit fee still uses limit anchor

**Step 2: Run focused tests**

Run:

```bash
uv run pytest tests/unit/trading/test_sizing.py -q
```

Expected:

- fail because `_buy_anchor_price()` rejects stop-family requests

**Step 3: Implement anchor helper**

Update `_buy_anchor_price()`:

```python
if request.order_type == "stop_market":
    if request.stop_price is None:
        raise ValueError("stop_market buy requests require a stop_price")
    return round(request.stop_price + _slippage(costs), 12)
if request.order_type in {"limit", "stop_limit"}:
    if request.limit_price is None:
        raise ValueError(f"{request.order_type} buy requests require a limit_price")
    return request.limit_price
return round(market_buy_price + _slippage(costs), 12)
```

Use a tiny private `_slippage(costs)` helper if it removes duplication.

**Step 4: Verify**

Run:

```bash
uv run pytest tests/unit/trading/test_sizing.py -q
```

Expected:

- anchor tests pass

### Task 4: Convert Quantity And Percent Sizing Failures Into Stable Runtime Reasons

**Files:**

- Modify: `src/quantleet/trading/sizing.py`
- Test: `tests/unit/trading/test_sizing.py`

**Step 1: Write failing affordability tests**

Add tests for:

- explicit market buy quantity exceeds unreserved cash -> `quantity is None`,
  `reason == "insufficient_cash"`
- explicit limit buy quantity exceeds unreserved cash -> same
- explicit stop-market buy quantity exceeds stop-price reservation -> same
- explicit stop-limit buy quantity exceeds limit-price reservation -> same
- explicit sell quantity exceeds unreserved long position -> `insufficient_position`
- dormant stop-market buy reduces later buy percent basis
- dormant stop-limit buy reduces later buy percent basis
- dormant stop-market sell reduces later sell percent basis
- dormant stop-limit sell reduces later sell percent basis

**Step 2: Run focused tests**

Run:

```bash
uv run pytest tests/unit/trading/test_sizing.py -q
```

Expected:

- fail on current dormant-stop and explicit-quantity behavior

**Step 3: Implement resolver changes**

Change `_resolve_quantity_request()` to receive:

- `state`
- `active_orders`
- `reservations`

Use the same reservation-aware available-resource basis as percent sizing.

For buy quantity:

```text
available_cash = state.cash - active_buy_cash_reservation - same_cycle_buy_cash
required_cash = quantity * anchor_price * (1 + fee_rate)
if required_cash > available_cash + tolerance:
    return ResolvedOrderSizing(quantity=None, reason="insufficient_cash")
```

For sell quantity:

```text
net_closable = state.position_quantity - active_sell_quantity - same_cycle_sell_quantity
if quantity > net_closable + tolerance:
    return ResolvedOrderSizing(quantity=None, reason="insufficient_position")
```

Update `_active_buy_cash_reservation()` so it includes dormant stop-family buy
orders instead of skipping them.

Update `_order_buy_anchor_price()`:

- `stop_market` -> `trigger_price + slippage`
- `stop_limit` -> `limit_price`
- `limit` -> `limit_price`
- `market` -> `market_buy_price + slippage`

**Step 4: Verify**

Run:

```bash
uv run pytest tests/unit/trading/test_sizing.py -q
```

Expected:

- pass
- old tests that expected dormant stops to be ignored are rewritten to expect
  conservative reservation

### Task 5: Emit Activation-Time Rejection Events

**Files:**

- Modify: `src/quantleet/backtest/strategy_runtime.py`
- Modify: `src/quantleet/backtest/runtime.py`
- Test: `tests/unit/backtest/test_order_sizing_activation.py`

**Step 1: Write failing driver tests**

Add tests that activation returns or records rejection events for:

- flat percent sell
- explicit buy quantity exceeding cash
- explicit sell quantity exceeding position
- percent quantity below minimum
- same-cycle second request exhausted by first accepted request

The assertion should verify:

```python
assert runtime.order_state().active == ()
assert runtime.order_state().order_events == (
    OrderRejectedEvent(
        symbol="BTC/USDT",
        side="buy",
        order_type="market",
        reason="insufficient_cash",
        timestamp=120,
        quantity=None,
        order_id=None,
        tag="too-large",
    ),
)
```

Use the exact field values from the final `OrderRejectedEvent` contract.

**Step 2: Run focused tests**

Run:

```bash
uv run pytest tests/unit/backtest/test_order_sizing_activation.py -q
```

Expected:

- fail because `_StrategyOrderState` has no rejection-event surface and the
  driver silently skips no-op sizing

**Step 3: Implement activation event plumbing**

Extend `_StrategyOrderState` with:

```python
order_events: tuple[OrderRejectedEvent, ...] = ()
```

In `_StrategyDriver`, keep a per-run `_order_events` tuple or list.

When `sizing.is_noop`:

- append `OrderRejectedEvent(...)`
- do not create `Order`
- do not reserve resources

Do the same for any remaining flat-exit guard if it still exists after Task 4.

**Step 4: Wire result collection**

In `_run_backtest()`, after `runtime.activate_pending_order_requests(...)`,
extend a local `order_events: list[OrderRejectedEvent]` from
`runtime.order_state().order_events` or from a drain method.

Prefer a drain method if repeated `order_state()` snapshots would otherwise
duplicate historical events:

```python
new_order_events = runtime.drain_order_events()
order_events.extend(new_order_events)
```

The drain method is a runtime orchestration detail, not a domain concern.

**Step 5: Verify**

Run:

```bash
uv run pytest tests/unit/backtest/test_order_sizing_activation.py -q
```

Expected:

- pass
- no rejected request creates a phantom active order

### Task 6: Reject Unaffordable Trigger-Time Execution

**Files:**

- Modify: `src/quantleet/backtest/runtime.py`
- Reuse: `src/quantleet/trading/sizing.py`
- Test: `tests/unit/backtest/test_engine.py` or
  `tests/integration/research/test_order_reservation_contract.py`

**Step 1: Write failing gap-overspend integration test**

Create a new integration test file if needed:

- `tests/integration/research/test_order_reservation_contract.py`

Scenario:

- bar 1 close `100`
- strategy submits `buy(qty_percent=100, order_type="stop_market",
  stop_price=105)`
- activation reserves quantity based on `105`
- next bar gap opens far above the reservation basis
- actual market fill would cost more than cash

Expected:

```python
assert result.trade_log == ()
assert result.final_state.cash == 100.0
assert result.final_state.position_quantity == 0.0
assert result.order_events == (
    OrderRejectedEvent(
        symbol="BTC/USDT",
        side="buy",
        order_type="stop_market",
        reason="execution_affordability",
        timestamp=120,
        quantity=...,
        order_id=1,
        tag="gap-entry",
    ),
)
```

Use deterministic zero fee or explicit fee values so the expected quantity is
easy to read.

**Step 2: Run the failing test**

Run:

```bash
uv run pytest tests/integration/research/test_order_reservation_contract.py -q
```

Expected:

- fail because current runtime either applies until `apply_fill` raises or has
  no rejection surface

**Step 3: Implement execution affordability check**

Before `_apply_runtime_fill(...)`, check buy affordability using all cash not
reserved by other open buy orders.

Conceptual helper:

```python
def _buy_fill_is_affordable(
    *,
    fill: FillEvent,
    state: TradingState,
    order: Order,
    active_orders: tuple[Order, ...],
    costs: CostConfig,
    market_buy_price: float,
) -> bool:
    other_buy_reservations = active_buy_cash_reservation_excluding(order.id)
    required_cash = round((fill.price * fill.quantity) + fill.fee, 12)
    return required_cash <= round(state.cash - other_buy_reservations, 12) + 1e-12
```

If unaffordable:

- append `OrderRejectedEvent(reason="execution_affordability", order_id=order.id, ...)`
- do not call `_apply_runtime_fill`
- do not append the order back to `remaining_orders`

Sell affordability should already be protected by position reservations and
`_is_flat_exit_order`, but add a symmetric rejection event if an active sell
somehow exceeds current unreserved position.

**Step 4: Verify focused runtime tests**

Run:

```bash
uv run pytest tests/integration/research/test_order_reservation_contract.py tests/unit/backtest/test_engine.py -q
```

Expected:

- pass
- no `ValueError("insufficient cash")` escapes for valid runtime gap failure

### Task 7: Add End-To-End Reservation Contract Tests

**Files:**

- Create: `tests/integration/research/test_order_reservation_contract.py`
- Modify only if needed: `tests/integration/research/support_backtest_runner.py`

**Step 1: Add public behavior tests**

Cover the minimum first-release matrix from the scenario spec:

- `qty_percent + market` buy still works
- `qty_percent + limit` buy uses `limit_price`
- `qty_percent + stop_market` buy uses `stop_price + slippage`
- `qty_percent + stop_limit` buy uses `limit_price`
- dormant stop-market buy reduces later buy available cash
- dormant stop-limit buy reduces later buy available cash
- dormant stop-market sell reduces later sell available position
- dormant stop-limit sell reduces later sell available position
- triggered stop-limit remains open and still blocks later competing orders
- explicit-vs-percent same-cycle competition rejects the unaffordable explicit
  request rather than resizing it
- rejected request does not create a phantom reservation

Keep tests behavior-first. Assert fills, final state, active/rejection outcome,
and public `order_events`; do not assert private helper calls.

**Step 2: Run integration tests**

Run:

```bash
uv run pytest tests/integration/research/test_order_reservation_contract.py -q
```

Expected:

- pass after Tasks 1-6

### Task 8: Update Existing Tests That Encode Old Policy

**Files:**

- Modify: `tests/unit/trading/test_sizing.py`
- Modify: `tests/unit/backtest/test_order_sizing_activation.py`
- Modify: `tests/unit/research/test_strategy_surface.py`
- Modify: `tests/integration/research/test_order_sizing_contract.py`
- Modify: `tests/integration/research/test_stop_limit_execution_semantics.py`
- Modify: `tests/integration/research/test_backtest_result_contract.py`

**Step 1: Replace old expectations**

Rewrite, do not delete blindly:

- dormant stop buy ignored -> dormant stop buy reserves cash
- dormant stop-limit buy ignored -> dormant stop-limit buy reserves cash
- quantity stop-limit buy does not reserve cash -> quantity stop-limit buy
  reserves cash and may reject if unaffordable
- flat sell stop-limit no-op -> explicit rejection event
- `qty_percent + stop_limit` rejected -> accepted at request surface and
  resolved later
- `qty_percent + stop_market` rejected -> accepted at request surface and
  resolved later

**Step 2: Run affected tests**

Run:

```bash
uv run pytest tests/unit/trading/test_sizing.py tests/unit/backtest/test_order_sizing_activation.py tests/unit/research/test_strategy_surface.py tests/integration/research/test_order_sizing_contract.py tests/integration/research/test_stop_limit_execution_semantics.py tests/integration/research/test_backtest_result_contract.py -q
```

Expected:

- pass

### Task 9: Documentation And Structure Alignment

**Files:**

- Modify: `docs/product-specs/order-sizing.md`
- Modify: `docs/product-specs/stop-limit.md`
- Modify: `docs/product-specs/order-reservation.md`
- Modify: `docs/product-specs/index.md`
- Modify: structure docs tests only if existing status-map tests require it

**Step 1: Update status notes**

After code and tests pass:

- mark `order-reservation.md` implemented or partially implemented according
  to actual delivered scope
- remove obsolete "qty_percent + stop_market remains out of scope" wording from
  `order-sizing.md` status notes
- remove obsolete first-slice `qty_percent is not supported for stop_limit`
  language from `stop-limit.md` or explicitly mark it historical
- update product-spec index status maps if structure tests require it

**Step 2: Run docs checks**

Run:

```bash
uv run poe repo-check
uv run pytest tests/structure/docs -q
```

Expected:

- pass

### Task 10: Full Verification

**Files:**

- No new files unless verification reveals failures

**Step 1: Run runtime-sensitive lane**

Run:

```bash
uv run poe verify-runtime
```

Expected:

- `lint` passes
- `mypy src` passes
- default tests pass
- coverage gate passes
- build passes
- repo-check passes
- notebook validation passes
- performance check passes

**Step 2: If runtime-sensitive lane is too slow locally**

At minimum, run and record:

```bash
uv run pytest tests/unit/trading tests/unit/backtest tests/unit/research tests/integration/research -q
uv run ruff check .
uv run mypy src
uv run python scripts/coverage_check.py
uv run python scripts/repo_check.py
uv build
```

Do not claim the implementation is complete unless the missing verification is
explicitly reported.

## Design Constraints For Implementers

- Do not add `qty_percent` to `Order` or `OrderIntent`.
- Do not make `Order` hold cash, position, margin, reservation, or buying-power
  fields.
- Do not catch invalid strategy/domain input and turn it into rejection events.
  Invalid shape raises `ValueError`.
- Do not silently skip valid runtime/account failures.
- Do not let `TradingState.apply_fill()` be the first place where expected
  runtime affordability rejection is discovered.
- Do not add venue-specific `reserve_on_accept` versus `check_on_trigger`
  configuration in this MVP.
- Do not implement cancel, replace, amend, expire, short selling, leverage,
  margin, OCO, OTO, bracket, trailing stops, post-only, reduce-only, or
  time-in-force.

## Implementation Work Log

- Implemented slices:
  1. Added `OrderRejectedEvent` and `BacktestResult.order_events`.
  2. Accepted `qty_percent` for `stop_market` and `stop_limit` strategy
     requests.
  3. Added positive finite quantity validation to runtime order intent and
     order creation.
  4. Extended sizing anchors and reservation accounting for all four order
     types.
  5. Converted activation-time account/resource failures into rejection events.
  6. Converted unaffordable trigger-time buy execution into rejection events
     before state mutation.
  7. Updated product docs and structure tests for the narrower
     `OrderRejectedEvent` public event surface.

## Commit Slice Guidance

Future implementation should commit in small slices:

1. `feat: add order rejection result surface`
2. `feat: accept percent sizing for stop-family requests`
3. `feat: reserve stop-family order resources on accept`
4. `feat: emit order rejection events from backtests`
5. `test: cover conservative order reservation contracts`
6. `docs: mark order reservation policy implemented`

## Evaluator Review

- Findings:
  - No blocking findings.
  - Final subagent review found no remaining blockers after the documentation
    and stop-family sell-reservation coverage fixes.
  - The implementation preserves the accepted product decisions: no
    trigger-time percent recalculation, explicit validation errors for invalid
    shape, explicit rejection events for valid runtime/account failures, and
    runtime account-control ownership for reservation behavior.
  - `qty_percent` remains absent from runtime `OrderIntent` and `Order`.
  - `BacktestResult.order_events` was appended without breaking the legacy
    positional `execution_model_name` constructor slot.
- Verification evidence:
  - `uv run pytest tests/integration/research/test_backtest_result_contract.py tests/integration/research/test_order_reservation_contract.py tests/unit/backtest/test_order_sizing_activation.py tests/unit/trading/test_sizing.py -q`:
    `32 passed`.
  - `uv run poe verify-runtime`:
    `ruff` passed, `mypy src` passed, full pytest `476 passed, 3 skipped`,
    coverage policy passed at `92%`, build passed, repository checks passed,
    notebooks validated, and performance benchmark passed.
  - Final read-only subagent re-review:
    no blockers; targeted stop-family sell-reservation tests passed
    `2 passed`.
  - `uv run pytest tests/unit/trading tests/unit/backtest tests/unit/research tests/integration/research tests/structure -q`:
    `415 passed`.
  - `uv run ruff check .`: `All checks passed!`.
  - `uv run mypy src`: `Success: no issues found in 51 source files`.
- Final disposition:
  - Implementation completed against this plan. Final runtime-sensitive
    verification and independent reviewer fan-out remain as closeout gates.
