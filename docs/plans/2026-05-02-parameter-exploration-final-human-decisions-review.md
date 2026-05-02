# Parameter Exploration Final Human Decisions Review Plan

- Date: 2026-05-02
- Task: Apply final human decisions on exception policy and example validation, then re-review the specs
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Close the remaining human-confirmation questions in the product and
  test specs, then run a focused read-only subagent review before technical
  implementation planning.
- Governing docs:
  - `AGENTS.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/parameter-exploration-test-scenarios.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing: The changes close product/test-spec decisions for a
  planned first-beta research feature and must stay within the existing Tier B
  spec scope.
- In-repo scope:
  - Update `docs/product-specs/parameter-exploration.md`.
  - Update `docs/product-specs/parameter-exploration-test-scenarios.md`.
  - Record subagent review coverage and verification in this plan.
- Out-of-repo scope:
  - None.
- Tier A progression requested: `no`
- Approval record, if required: Not required; documentation-only Tier B work.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Success criteria:
  - Exception policy is closed as standard `ValueError`/`TypeError` for beta.
  - Canonical workflow testing is P0 integration coverage, while actual
    docs/example/notebook execution remains P1/docs-release validation.
  - At least three read-only subagent reviewers check the updated specs.
  - Scope-preserving fixes are applied; scope-changing questions are reported.
  - Verification passes.
- Out of scope:
  - Runtime implementation.
  - Test implementation.
  - Re-opening prior beta product scope decisions.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm the remaining open questions are removed or reduced to true future
    implementation concerns.
  - Confirm the docs do not make executable examples a P0 requirement.
  - Confirm exception policy does not introduce a custom public exception API.
  - Run planned verification commands.
- Acceptance artifact location:
  - `docs/plans/2026-05-02-parameter-exploration-final-human-decisions-review.md`
- How the generator and evaluator agreed on done before execution:
  - The planner contract above is the definition of done.
- Checks the evaluator will use:
  - Manual diff review.
  - Read-only subagent review synthesis.
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Auto-fail conditions:
  - The docs require executable examples/notebooks as P0 feature completion.
  - The docs introduce custom exception types as beta public API.
  - Verification fails.

## Generator Work Log

- Planned slice order:
  1. Apply the two human decisions to product/test specs.
  2. Run focused subagent review.
  3. Apply only clear scope-preserving improvements.
  4. Verify and report.
- Notes:
  - Applied final human decisions:
    - beta validation uses standard `ValueError`/`TypeError`, not custom public
      exception classes
    - docs/example/notebook execution is P1 docs-release validation, while P0
      canonical workflow coverage lives in integration tests
- Blockers or scope changes:
  - None.

## Subagent Review Coverage

- Ampere: product/test consistency reviewer.
  - Result: no actionable findings.
- Descartes: test quality reviewer.
  - Result: no actionable findings.
- Avicenna: implementation-readiness reviewer.
  - Accepted: record schema needed exact non-metric keys and row-state
    nullability; objective examples needed to be distinguished from the full
    accepted objective path set; `fail_fast=True` needed a single exception
    contract; docs/example gate needed to be explicit.

## Parent Synthesis

- Directly applied scope-preserving fixes:
  - Added product text stating beta validation uses `ValueError` for invalid
    values and `TypeError` for invalid argument types or call shapes.
  - Clarified docs/example/notebook execution as P1 docs-release validation,
    not P0 feature completion.
  - Renamed the four objective paths as canonical examples and explicitly
    stated that all beta comparison metric paths are valid objective paths.
  - Defined `fail_fast=True` as re-raising the original exception type with the
    original traceback and visible parameter/stage context, without custom
    Quantcraft exception classes.
  - Added a simple-record non-metric field table with stable keys and
    row-state nullability.
- Rejected or limited findings:
  - Did not make executable docs examples a P0 gate; this would contradict the
    final human decision for this slice.

## Evaluator Review

- Findings:
  - No blocking findings remain after applying the focused review fixes.
- Verification evidence:
  - `uv run poe repo-check` passed with `repository checks passed`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q` passed with
    `67 passed`.
- Final disposition:
  - Complete.
