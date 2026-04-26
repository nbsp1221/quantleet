# Active Plan

- Date: `2026-04-23`
- Task: `Implement the first stop-trigger order slice end-to-end`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Implement the approved first shipped stop-trigger slice as code:
    - strategy/request-side `stop_market` support
    - runtime trigger-aware `OrderIntent` and `Order`
    - matcher-side trigger predicates with market-fill reuse
    - stop-aware synthetic decisive points in the backtest execution model
    - end-to-end backtest support and tests
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
  - `docs/plans/2026-04-23-stop-trigger-order-implementation-plan.md`
- Why these are governing:
  - They define the repo workflow, Tier A constraints, current shipped
    backtest/research contract, the matching-versus-path-construction boundary,
    and the approved stop-trigger semantics and test matrix for this slice.
- In-repo scope:
  - Modify only the files needed for the first shipped `stop_market` slice and
    its tests under:
    - `src/quantcraft/research/`
    - `src/quantcraft/trading/`
    - `src/quantcraft/backtest/`
    - `tests/unit/`
    - `tests/integration/research/`
  - Update this active plan with evaluator findings and fresh verification
    evidence before close.
- Out-of-repo scope:
  - no live-service work
  - no new external connectors
  - no non-repo file changes outside read-only comparator inspection already
    completed in the approved design slices
- Tier A progression requested: `yes`
- Approval record, if required:
  - Tier A implementation approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread direction on `2026-04-23` to treat the three approved
      stop-trigger documents as closed, then implement the feature end-to-end
      with subagent orchestration, verification, and final review
    - Granted scope:
      repository-local code and test changes for the first shipped
      `stop_market` slice in `trading`, `backtest`, and `research`, including
      runtime-sensitive verification
    - Expiration:
      end of this `2026-04-23` execution slice
    - Audit reference:
      this active plan plus the approved `2026-04-23` spec/test/implementation
      plan documents
- Verification commands:
  - `uv run pytest -q tests/unit/trading/test_contracts.py tests/unit/research/test_strategy_surface.py`
  - `uv run pytest -q tests/unit/trading/test_orders.py`
  - `uv run pytest -q tests/unit/trading/test_matching_and_state.py`
  - `uv run pytest -q tests/unit/backtest/test_execution_model.py`
  - `uv run pytest -q tests/unit/backtest/test_order_sizing_activation.py`
  - `uv run pytest -q tests/integration/research/test_backtest_execution_semantics.py`
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Success criteria:
  - `stop_market` can be requested from `Strategy.buy()` and `Strategy.sell()`
    with `stop_price`.
  - request normalization infers and persists runtime `trigger_condition`
    using the active closed-bar `close`.
  - dormant runtime `stop_market` orders do not fill before trigger.
  - matcher reuses ordinary market-fill semantics after trigger rather than
    introducing stop-specific fill logic.
  - execution-model decisive-point compression emits stop-crossing points
    causally and preserves gap semantics.
  - end-to-end integration tests cover gap, intrabar, same-point trigger/fill,
    multi-stop ordering, and long-only no-op behavior.
  - `uv run poe verify-runtime` and `uv run poe repo-check` pass fresh.
- Out of scope:
  - `stop_limit`
  - trailing stops
  - stop-aware `%` sizing support beyond explicit first-slice rejection
  - paper/live runtime work
  - public event-surface expansion beyond existing exports

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close only when the implemented code matches the approved spec and test
    matrix, the diff remains bounded to the first shipped `stop_market` slice,
    and fresh runtime-sensitive verification passes.
- Acceptance artifact location:
  - this active plan
  - changed source and test files for the first shipped stop-trigger slice
- How the generator and evaluator agreed on done before execution:
  - The slice is done when:
    1. the first failing tests were written before each implementation batch
    2. the code implements only the approved `stop_market` scope
    3. evaluator review finds no unresolved material contract mismatches
    4. fresh verification evidence is recorded here
- Checks the evaluator will use:
  - compare the diff against the approved `2026-04-23` spec/test docs
  - compare the final code against the execution-plan file targets and defers
  - run the targeted test commands
  - run `uv run poe verify-runtime`
  - run `uv run poe repo-check`
- Auto-fail conditions:
  - deriving `trigger_condition` from `side` alone
  - introducing a second stop-specific fill path instead of reusing market
    matching after trigger
  - allowing dormant stop orders to leak into ordinary `%` sizing reservation
    semantics
  - applying stop orders retroactively to the bar that created them
  - widening the slice into `stop_limit`, trailing, or paper/live semantics

## Generator Work Log

- Planned slice order:
  1. Run a read-only research split over the main seams and synthesize the
     implementation handoff.
  2. Execute TDD batches for:
     - public request normalization
     - runtime trigger-aware orders
     - matching trigger predicates
     - execution-model decisive points
     - runtime/integration semantics and `%`-sizing defer
  3. Run runtime-sensitive verification.
  4. Run read-only review fan-out and fix only material findings.
  5. Record evaluator findings and close.
- Notes:
  - One local writer owns all edits.
  - Read-only subagents are used only for bounded exploration and final review.
  - The current branch is `dev`, so no branch switch is required for this
    execution slice.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No unresolved material findings.
  - Read-only review fan-out surfaced two maintainability issues before close:
    duplicate stop fixtures in
    `tests/integration/research/support_backtest_runner.py` and duplicate
    execution-model stop scenarios in
    `tests/unit/backtest/test_execution_model.py`.
  - Both were cleaned before the final verification pass.
- Verification evidence:
  - Targeted regression lane:
    - `uv run pytest -q tests/unit/trading/test_contracts.py tests/unit/research/test_strategy_surface.py tests/unit/trading/test_orders.py tests/unit/trading/test_matching_and_state.py tests/unit/backtest/test_execution_model.py tests/unit/backtest/test_order_sizing_activation.py tests/unit/trading/test_sizing.py tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_canonical_stop_market_contract.py`
    - Result: `124 passed in 0.10s`
  - Repo/document lane:
    - `uv run poe repo-check`
    - Result: `repository checks passed`
  - Runtime-sensitive lane:
    - `uv run poe verify-runtime`
    - Result:
      - `ruff check .`: pass
      - `mypy src`: pass
      - `pytest -q`: `398 passed, 3 skipped`
      - coverage: `92%`, with `src/quantcraft/trading/domain/` at `100%`
      - `uv build`: pass
      - `scripts/repo_check.py`: pass
      - notebook validation: 4 notebooks validated
      - perf check: `2 passed`, steady-state median about `121.4 ms`
  - Default verify lane:
    - `uv run poe verify`
    - Result:
      - `ruff check .`: pass
      - `mypy src`: pass
      - `pytest -q`: `398 passed, 3 skipped`
      - coverage: `92%`
      - `uv build`: pass
      - `scripts/repo_check.py`: pass
      - notebook validation: 4 notebooks validated
- Final disposition:
  - `accepted`
