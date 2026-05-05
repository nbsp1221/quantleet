# Active Plan

- Date: `2026-04-22`
- Task: `Implement the first qty_percent strategy-sizing slice`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  Implement the first shipped `qty_percent` slice for the current
  single-symbol, long-only backtest/research workflow so that strategy authors
  can use `buy(qty_percent=...)` and `sell(qty_percent=...)`, while runtime
  `OrderIntent` and runtime `Order` remain quantity-only.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/order-sizing.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-22-order-sizing-implementation-plan.md`
- Why these are governing:
  - They define the repo workflow, Tier A approval boundary, current shipped
    backtest/research contracts, the future `qty_percent` spec we are shipping
    in this slice, package ownership rules, and the approved implementation
    approach for keeping raw percent sizing out of the quantity-based trading
    kernel.
- In-repo scope:
  - Add additive `qty_percent` support to the strategy surface.
  - Introduce one neutral shared pending-request seam outside
    `trading.domain`.
  - Add one canonical percent-sizing policy outside `trading.domain`.
  - Resolve percent requests at backtest activation time using reservation- and
    affordability-aware rules.
  - Keep `OrderIntent` and runtime `Order` quantity-only.
  - Add focused unit/integration/structure doc tests and update shipped docs.
- Out-of-repo scope:
  - none
- Tier A progression requested: `yes`
- Approval record, if required:
  - Tier A implementation approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request on `2026-04-22` to begin implementation from the
      approved sizing docs, use `$subagent-orchestration`, and verify
      implementation plus test coverage before final reporting
    - Granted scope:
      Tier A/B repository-local code, test, and doc changes required to ship
      the first `qty_percent` sizing slice for the current backtest/research
      workflow only
    - Expiration:
      end of this `2026-04-22` implementation slice
    - Audit reference:
      this active plan, the implementation diff, subagent review outputs, and
      fresh verification evidence
- Verification commands:
  - targeted failing/passing TDD test runs during implementation
  - `uv run pytest tests/unit/research/test_strategy_surface.py tests/unit/trading/test_contracts.py tests/unit/trading/test_orders.py tests/unit/trading/test_sizing.py tests/unit/backtest/test_order_sizing_activation.py tests/integration/research/test_order_sizing_contract.py -q`
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Success criteria:
  - `Strategy.buy/sell()` support additive `qty_percent` with explicit
    validation and without regressing the existing `quantity` path.
  - Pending strategy requests are no longer modeled directly as `OrderIntent`.
  - Runtime activation resolves percent requests into concrete quantity using
    the documented reserved-adjusted buy basis, net-closable sell basis,
    price-anchor rules, and general affordability clamp.
  - `OrderIntent` and runtime `Order` remain quantity-only.
  - End-to-end backtest tests prove `qty_percent` behavior, including serial
    same-cycle resolution and flat-sell no-op behavior.
  - Shipped docs are updated so `order-sizing.md` is no longer future-only.
  - Fresh verification passes with evidence.
- Out of scope:
  - `target_percent`, rebalancing, multi-symbol allocation
  - leverage or buying-power semantics
  - live/paper runtime implementation
  - stop-family orders

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after the shipped `qty_percent` behavior matches the
    docs, the trading kernel stays quantity-only, bounded subagent review finds
    no unresolved material issues, and fresh runtime-sensitive verification
    passes.
- Acceptance artifact location:
  - relevant code/test/doc files in this slice
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - This slice is done when the implementation follows the documented
    `pending request -> runtime resolution -> quantity-only OrderIntent/Order`
    path, covers the new semantics with focused tests, and promotes the product
    docs to shipped authority without reopening the sizing meaning.
- Checks the evaluator will use:
  - compare the diff against `docs/product-specs/order-sizing.md` and the
    implementation-plan handoff
  - run the targeted test command
  - run `uv run poe verify-runtime`
  - run `uv run poe repo-check`
  - synthesize subagent review findings for architecture, correctness, and
    coverage quality
- Auto-fail conditions:
  - raw `qty_percent` leaks into `trading.domain.OrderIntent` or runtime
    `Order`
  - buy-side semantics drift from requested-position-budget plus affordability
    clamp
  - sell-side semantics drift from net-closable basis
  - same-bar retroactive activation is introduced
  - the slice is closed without fresh runtime-sensitive verification evidence

## Generator Work Log

- Planned slice order:
  1. Run read-heavy subagent fan-out on architecture, coverage/test surface,
     and runtime hotspot behavior.
  2. Write failing tests for the new public API and quantity-only kernel
     boundary.
  3. Add the neutral shared pending-request seam and sizing policy.
  4. Teach backtest activation to resolve percent requests serially.
  5. Add end-to-end tests and doc promotions.
  6. Run bounded review fan-out, fix findings, rerun verification, and close.
- Notes:
  - Parent agent owns all writes.
  - Delegated agents stay read-only.
  - Existing dirty docs from prior planning work are outside this code slice
    unless they are explicitly modified here as part of shipping the feature.
- Read-only architecture review synthesis:
  - Safe writer-owned code files:
    - `src/quantleet/research/strategy.py`
    - `src/quantleet/backtest/strategy_runtime.py`
    - `src/quantleet/backtest/runtime.py`
    - new neutral support files outside `trading.domain`, as already approved by
      the implementation plan:
      `src/quantleet/trading/order_requests.py`
      `src/quantleet/trading/sizing.py`
  - Safe writer-owned test/doc files:
    - `tests/unit/research/test_strategy_surface.py`
    - `tests/unit/trading/test_contracts.py`
    - `tests/unit/trading/test_orders.py`
    - `tests/unit/trading/test_sizing.py`
    - `tests/unit/backtest/test_order_sizing_activation.py`
    - `tests/integration/research/test_order_sizing_contract.py`
    - shipped product-spec routing/docs touched by this slice
  - Do not widen `trading.domain`:
    - `src/quantleet/trading/domain/intents.py:10-16` is the current
      quantity-only `OrderIntent` minimum contract and should stay unchanged
    - `src/quantleet/trading/domain/orders.py:9-40` is the runtime quantity-only
      `Order` contract and should stay unchanged
  - Evidence:
    - `docs/product-specs/order-sizing.md:142-167` requires raw `qty_percent`
      to resolve before runtime `Order` creation and forbids leaking it into the
      runtime order model
    - `docs/plans/2026-04-22-order-sizing-implementation-plan.md:143-164`
      assigns intake validation to `research`, activation timing to `backtest`,
      and keeps the neutral request seam plus sizing policy outside
      `trading.domain`
    - `src/quantleet/research/strategy.py:41-116` currently stores pending
      `OrderIntent` directly and therefore owns the public intake change
    - `src/quantleet/backtest/strategy_runtime.py:13-132` currently activates
      pending `OrderIntent` objects directly into runtime `Order` and therefore
      owns the runtime-resolution seam
    - `src/quantleet/backtest/runtime.py:39-105` currently activates pending
      orders before each bar and therefore owns same-bar timing preservation
- Read-only runtime semantics review synthesis:
  - Minimal runtime data required by the shared sizing resolver:
    - request data: `side`, `order_type`, `qty_percent`, `limit_price`
    - buy resource basis: `TradingState.cash`
    - sell resource basis: `TradingState.position_quantity`
    - reservations: active runtime orders plus each order's
      `remaining_quantity`
    - affordability inputs: `CostConfig`
    - buy-side anchor: one executable buy reference price supplied by the
      current runtime
  - Source evidence:
    - `src/quantleet/trading/domain/state.py:9-15` defines the current
      state fields; `cash` and `position_quantity` are the only current runtime
      resource bases for spot-like long-only sizing
    - `src/quantleet/trading/domain/state.py:27-45` enforces buy affordability
      as `price * quantity + fee <= cash` and sell closability as
      `quantity <= position_quantity`
    - `src/quantleet/trading/domain/orders.py:42-48` exposes unresolved
      `remaining_quantity`, which is the existing canonical reservation unit
    - `src/quantleet/trading/domain/matching.py:30-45` derives fill price and
      fee from order side, order type, and `CostConfig`
    - `src/quantleet/trading/domain/costs.py:7-19` defines the current fee
      and slippage inputs available to the runtime
    - `src/quantleet/backtest/execution_model.py:45-72` emits the executable
      per-bar tick path beginning at bar open, which is the correct market-buy
      affordability anchor in the current backtest model
    - `src/quantleet/backtest/execution_model.py:102-140` shows limit orders
      are evaluated against their own `limit_price` crossings, which supports
      using submitted `limit_price` as the conservative limit-buy anchor
    - `src/quantleet/backtest/runtime.py:43-49` activates pending orders
      before each bar and builds the executable tick path from the full active
      order tuple, so same-cycle percent requests must resolve serially against
      evolving reservations
    - `src/quantleet/backtest/runtime.py:51-91` replaces active orders after
      fills, meaning reservation-aware sell sizing should key off unresolved
      active exits rather than original order size
    - `src/quantleet/backtest/strategy_runtime.py:63-70` is the activation
      seam where pending requests must stop being raw strategy intake and start
      becoming quantity-only runtime orders
- Blockers or scope changes:
  - Final review surfaced one material buy-side reservation bug:
    percent buys were reserving the pre-rounding requested budget instead of
    the actual resolved order budget, which could under-size later same-cycle
    percent buys when quantity increments were coarse.
  - Fixed in `src/quantleet/trading/sizing.py` and locked by
    `tests/unit/trading/test_sizing.py`.

## Evaluator Review

- Findings:
  - No unresolved material findings after final implementation review.
  - One material issue was found during evaluator review and fixed before
    close:
    buy-side serial reservations now use the actual rounded order budget
    instead of the pre-rounding requested budget, keeping same-cycle percent
    buys aligned with the documented unresolved-remainder reservation rule.
  - Read-only review synthesis confirmed:
    - raw `qty_percent` does not appear in `src/quantleet/trading/domain/*`
    - strategy-facing `%` intake stays in `src/quantleet/research/strategy.py`
    - activation-time resolution stays in `src/quantleet/backtest/strategy_runtime.py`
    - shipped product-spec routing now promotes `docs/product-specs/order-sizing.md`
      to governing current scope
- Verification evidence:
  - `uv run pytest tests/unit/research/test_strategy_surface.py tests/unit/trading/test_contracts.py tests/unit/trading/test_orders.py tests/unit/trading/test_sizing.py tests/unit/backtest/test_order_sizing_activation.py tests/integration/research/test_order_sizing_contract.py -q`
    -> `58 passed in 0.05s`
  - `uv run pytest tests/structure/docs/test_system_of_record_docs.py tests/structure/repo/test_index_status_maps.py tests/structure/repo/test_repository_entrypoint_docs.py tests/structure/docs/test_research_ergonomics_quickstart.py -q`
    -> `21 passed in 0.03s`
  - `uv run poe verify-runtime`
    -> `ruff check .` passed
    -> `mypy src` passed
    -> `pytest -q` => `357 passed, 3 skipped`
    -> coverage policy check passed at `92%`
    -> `uv build` passed
    -> notebook validation passed for 4 notebooks
    -> perf check passed:
       `test_rsi_backtest_steady_state_median_is_within_threshold` median about
       `124.6ms`
  - `uv run poe repo-check`
    -> `repository checks passed`
- Final disposition:
  - `complete`
