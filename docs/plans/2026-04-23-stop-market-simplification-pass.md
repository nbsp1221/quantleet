# Active Plan

- Date: `2026-04-23`
- Task: `Run a behavior-preserving simplification pass on the first shipped stop_market slice`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Simplify the recently changed `stop_market` code without changing shipped
    behavior, verification scope, or public contracts.
  - Improve local reasoning in the strategy request path and stop-trigger
    predicate flow so the next stop-related edit stays localized.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-23-stop-trigger-order-spec-design.md`
  - `docs/plans/2026-04-23-stop-trigger-order-test-matrix-design.md`
  - `docs/plans/2026-04-23-stop-trigger-order-implementation-plan.md`
  - `docs/plans/2026-04-23-stop-trigger-order-execution.md`
- Why these are governing:
  - They define repo workflow, Tier A guardrails, the approved stop-market
    semantics, and the current shipped behavior this cleanup must preserve.
- In-repo scope:
  - Only local simplification in the stop-market slice under:
    - `src/quantcraft/research/strategy.py`
    - `src/quantcraft/trading/domain/orders.py`
    - `src/quantcraft/trading/domain/matching.py`
    - `src/quantcraft/backtest/execution_model.py`
  - Update this active plan with findings and fresh verification evidence.
- Out-of-repo scope:
  - no non-repo changes
  - no new external research beyond the already approved design work
- Tier A progression requested: `yes`
- Approval record, if required:
  - Tier A simplification approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread direction on `2026-04-23` to apply the
      `$code-simplifier` pass, review the current stop-market implementation,
      and fix only behavior-preserving quality issues
    - Granted scope:
      repository-local simplification edits for the current stop-market slice in
      `research`, `trading`, and `execution`, plus targeted verification
    - Expiration:
      end of this `2026-04-23` simplification slice
    - Audit reference:
      this active plan together with the approved `2026-04-23` stop-trigger
      spec, test matrix, implementation plan, and execution plan
- Verification commands:
  - `uv run pytest -q tests/unit/research/test_strategy_surface.py tests/unit/trading/test_orders.py tests/unit/trading/test_matching_and_state.py tests/unit/backtest/test_execution_model.py`
  - `uv run poe repo-check`
- Success criteria:
  - Request construction in `Strategy` is simpler without changing the strategy
    surface or stop-market validation behavior.
  - Stop crossing logic has a single local source of truth instead of parallel
    duplicated predicate branches.
  - No stop-market semantics, ordering, or validation contract changes.
  - Fresh targeted tests and repo checks pass.
- Out of scope:
  - runtime sequencing changes
  - new order types or new validations
  - docs or test-matrix rewrites beyond what verification requires

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close only if the simplification makes the touched code easier to modify
    while preserving the approved stop-market behavior and passing fresh
    targeted verification.
- Acceptance artifact location:
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - Keep only edits that reduce local reasoning surface in the touched files,
    preserve public behavior, and survive targeted tests.
- Checks the evaluator will use:
  - inspect the touched diff for responsibility reduction and removed duplicate
    trigger logic
  - rerun targeted tests for strategy surface, order semantics, matching, and
    execution model
  - rerun `uv run poe repo-check`
- Auto-fail conditions:
  - changing stop-market trigger semantics
  - moving complexity into vague helpers
  - broadening the cleanup into unrelated modules

## Generator Work Log

- Planned slice order:
  1. Simplify strategy-side request construction.
  2. Collapse duplicate stop crossing logic into one domain-local predicate.
  3. Run targeted verification.
  4. Record evaluator findings.
- Notes:
  - This is a cleanup-only pass; behavior must remain unchanged.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No unresolved findings.
  - The kept simplifications were intentionally narrow:
    - `Strategy.buy()` and `Strategy.sell()` now share one private request
      submission path instead of duplicating identical request assembly.
    - Stop trigger price crossing now has one domain-local source of truth on
      `Order.is_triggered_by_price(...)`, which is reused by matching and the
      execution model.
  - No behavior change was introduced in stop-market validation, trigger
    timing, or runtime sequencing.
- Verification evidence:
  - Targeted simplification lane:
    - `uv run pytest -q tests/unit/research/test_strategy_surface.py tests/unit/trading/test_orders.py tests/unit/trading/test_matching_and_state.py tests/unit/backtest/test_execution_model.py`
    - Result: `82 passed in 0.07s`
  - Repo/document lane:
    - `uv run poe repo-check`
    - Result: `repository checks passed`
- Final disposition:
  - `accepted`
