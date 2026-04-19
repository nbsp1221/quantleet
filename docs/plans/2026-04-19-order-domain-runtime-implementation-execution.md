# Active Plan

- Date: `2026-04-19`
- Task: `Implement the first runtime Order seam`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  Implement the first runtime `Order` seam in `quantcraft` by introducing a
  trading-owned `Order` model for the current market/limit slice, migrating the
  backtest runtime away from using raw `OrderIntent` as fake runtime order
  truth, and preserving current shipped backtest semantics.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/design-docs/order-domain-runtime-design.md`
  - `docs/plans/2026-04-19-order-domain-runtime-implementation-plan.md`
- Why these are governing:
  - They define the current implemented backtest scope, Tier A rules, package
    ownership, runtime-sensitive verification, and the newly accepted draft
    boundary for `OrderIntent` versus runtime `Order`.
- Supporting references:
  - `docs/references/openai-harness-engineering.md`
  - `https://www.anthropic.com/engineering/harness-design-long-running-apps`
- Why these references matter:
  - They reinforce the repository-local harness protocol for long-running,
    agent-first work: humans steer, agents execute, repository docs are the
    system of record, and read-heavy fan-out plus bounded review loops improve
    reliability.
- In-repo scope:
  - Create `src/quantcraft/trading/domain/orders.py`
  - Update the trading/backtest runtime path to manage runtime orders for the
    current market/limit slice
  - Update focused unit/integration tests and any minimally affected docs
  - Run bounded subagent read/review loops with parent-agent write ownership
- Out-of-repo scope:
  - No live-trading implementation
  - No paper-trading implementation
  - No stop-market or stop-limit support
  - No public `Strategy` API change
- Tier A progression requested: `yes`
- Approval record, if required:
  - Tier A implementation approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request to begin implementation from the current docs,
      validate it, use `$subagent-orchestration`, and follow the harness
      protocol
    - Granted scope:
      Tier A code changes in `src/quantcraft/trading/*` and affected
      `backtest`/tests/docs required to implement the first runtime `Order`
      seam for current market/limit behavior only
    - Expiration:
      end of this `2026-04-19` implementation slice
    - Audit reference:
      this active plan, the implementation diff, and verification evidence
  - External research approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request to read the Anthropic harness-design article
    - Granted scope:
      read-only external reference lookup for harness/process guidance only
    - Expiration:
      end of this `2026-04-19` implementation slice
    - Audit reference:
      this active plan plus cited reference use in session synthesis
- Verification commands:
  - targeted TDD checks during implementation
  - `uv run pytest tests/unit/trading/test_orders.py tests/unit/trading/test_matching_and_state.py tests/unit/backtest/test_execution_model.py tests/integration/research/test_backtest_execution_semantics.py -q`
  - `uv run poe verify-runtime`
  - `uv run poe verify`
  - `uv run poe repo-check`
- Success criteria:
  - runtime `Order` exists in `quantcraft.trading.domain`
  - current market/limit behavior remains intact
  - backtest runtime no longer treats raw `OrderIntent` tuples as runtime order
    truth
  - matching remains market-fact calculation and stays bar-agnostic
  - first slice does not introduce trigger-aware stop behavior
  - verification passes with fresh evidence
- Out of scope:
  - trigger-aware order behavior
  - stop, stop-limit, trailing, bracket, cancel, or replace flows
  - portfolio, ledger, allocator, or risk-engine design
  - live/paper runtime work

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after the runtime `Order` seam is implemented,
    preserved semantics are proven by focused tests plus runtime verification,
    and bounded review fan-out leaves no material findings.
- Acceptance artifact location:
  - `src/quantcraft/trading/domain/orders.py`
  - affected runtime/test/doc files in this slice
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - This slice is done when current market/limit behavior is preserved under a
    new trading-owned runtime `Order` model, with no stop-order behavior or
    broader runtime redesign smuggled in.
- Checks the evaluator will use:
  - compare the diff against current product specs and the accepted draft
    implementation plan
  - run the targeted test command
  - run `uv run poe verify-runtime`
  - run `uv run poe verify`
  - run `uv run poe repo-check`
  - synthesize bounded reviewer findings
- Auto-fail conditions:
  - changing public strategy ergonomics
  - introducing stop-order behavior
  - moving bar-aware logic into `trading`
  - leaving raw `OrderIntent` as runtime order truth
  - claiming success without fresh verification evidence

## Generator Work Log

- Planned slice order:
  1. Read current code and gather independent hotspot analysis.
  2. Write failing tests for the new runtime `Order` seam.
  3. Implement `trading.domain.orders` and narrow matcher updates.
  4. Migrate backtest runtime ownership from raw intents to runtime orders.
  5. Run focused verification, then fan out bounded review.
  6. Apply fixes, rerun verification, and close the plan.
- Notes:
  - Parent agent owns all writes.
  - Delegated work stays read-only until review.
  - Default subagent model for this slice is `gpt-5.4` with `high`
    reasoning effort, per user request.
- Blockers or scope changes:
  - Current implementation kept the first slice narrower than the earlier draft
    implementation plan:
    - trigger-aware stop behavior remains deferred
    - matcher contract remains `FillEvent | None`
    - `Strategy` still emits only pending `OrderIntent`
  - Current write set:
    - `src/quantcraft/trading/domain/orders.py`
    - `src/quantcraft/trading/domain/matching.py`
    - `src/quantcraft/trading/domain/__init__.py`
    - `src/quantcraft/backtest/strategy_runtime.py`
    - `src/quantcraft/backtest/runtime.py`
    - `src/quantcraft/backtest/execution_model.py`
    - `tests/unit/trading/test_orders.py`
    - `tests/unit/trading/test_matching_and_state.py`
    - `tests/unit/backtest/test_execution_model.py`
    - `docs/plans/2026-04-19-order-domain-runtime-implementation-execution.md`
  - Pre-existing carryover docs remain dirty in the worktree but are outside
    this implementation slice and were not modified as part of this code pass:
    - `docs/design-docs/index.md`
    - `docs/research/index.md`
    - `docs/plans/2026-04-19-trading-kernel-canonical-model-design-session-plan.md`
    - `docs/design-docs/order-domain-runtime-design.md`
    - `docs/plans/2026-04-19-order-domain-documentation-systemization-plan.md`
    - `docs/plans/2026-04-19-order-domain-runtime-implementation-plan.md`
    - `docs/plans/2026-04-19-order-domain-spec-design-plan.md`
    - `docs/research/2026-04-19-order-domain-architecture-comparison.md`

## Evaluator Review

- Findings:
  - Read-heavy hotspot fan-out confirmed the narrow code path:
    - keep `Strategy` emitting pending `OrderIntent`
    - move runtime order truth into a trading-owned `Order`
    - keep `matching` bar-agnostic and fill-driven
    - keep `backtest` responsible for path construction
  - First review fan-out found three material issues and they were fixed:
    1. dead projection indirection in `strategy_runtime` / `runtime`
    2. redundant `Order.state` field for a slice that only needs open/fill
       behavior
    3. missing malformed-order validation for negative or overfilled carried
       state and malformed limit orders
  - Follow-up review found no remaining material correctness or closeability
    issues after those fixes.
  - Residual risk:
    - `backtest/order_activation.py` is now unused by the active runtime path.
      It was left untouched because removing dormant files was outside this
      slice’s minimum runtime-Order goal.
- Verification evidence:
  - `uv run pytest tests/unit/trading/test_orders.py tests/unit/trading/test_matching_and_state.py tests/unit/backtest/test_execution_model.py tests/integration/research/test_backtest_execution_semantics.py -q`
    -> `40 passed in 0.04s`
  - `uv run poe verify-runtime`
    -> passed on `2026-04-19`, including:
    - `317 passed, 3 skipped`
    - trading-domain coverage at `100%`
    - `repository checks passed`
    - notebook validation passed
    - perf check `2 passed`
  - `uv run poe verify`
    -> passed on `2026-04-19`
  - `uv run poe repo-check`
    -> `repository checks passed` on `2026-04-19`
- Final disposition:
  - `complete`
