# Parameter Exploration Final Decisions Review Plan

- Date: 2026-05-02
- Task: Reflect final parameter exploration spec decisions and review the
  updated product spec with subagents
- Status: `complete`
- Risk class: `Tier B`
- Requestor: retn0
- Owner: Codex

## Planner Contract

- Goal: Update the parameter exploration product spec with the final decisions
  on grid size, non-finite metrics, and failed-row diagnostics, then collect
  independent subagent review on the updated document.
- Governing docs:
  - `AGENTS.md`
  - `docs/PLANS.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
- Why these are governing: They define repo workflow, product-spec authority,
  planned first-beta parameter exploration scope, research/backtest reliability
  expectations, and Tier boundaries.
- In-repo scope:
  - Update `docs/product-specs/parameter-exploration.md`.
  - Record the review workflow and verification evidence in this plan.
  - Apply only documentation clarifications that preserve the approved beta
    product scope.
- Out-of-repo scope:
  - No dependency changes, non-repo edits, live credentials, external connector
    usage, or implementation work.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is a Tier B documentation
  update and review; it does not alter `trading` or `execution` behavior.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Success criteria:
  - The spec reflects the three approved decisions:
    - keep `max_candidates=1000` and retain successful `BacktestResult`
      values in memory
    - preserve `math.inf` internally while emitting JSON/CSV-safe record
      state for non-finite metrics
    - require `failure_stage`, `error_type`, and `error_message` on failed rows
  - At least three independent subagent reviews are collected on the updated
    spec.
  - Findings are synthesized, and any remaining human-judgment questions are
    separated from clear documentation fixes.
  - Verification passes or failures are recorded.
- Out of scope:
  - Implementing `ParameterStudy` or `GridSearchResult`.
  - Writing the test-scenario spec.
  - Changing approved beta product scope.
  - Adding persistence, parallelism, plotting, weighted objectives, or
    optimizer backends.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - The updated spec is internally consistent with the approved decisions.
  - Subagent review covers product intent, edge cases, architecture, and
    testability.
  - The final report names reviewers, perspectives, major findings, applied
    changes, open questions, and verification evidence.
- Acceptance artifact location:
  - `docs/product-specs/parameter-exploration.md`
  - this plan's `## Evaluator Review`
- How the generator and evaluator agreed on done before execution: The slice is
  done when the spec is updated, subagent review is synthesized, clear
  scope-preserving fixes are applied if needed, and verification evidence is
  recorded.
- Checks the evaluator will use:
  - Review the diff against this plan and governing docs.
  - Confirm no runtime code or Tier A behavior changed.
  - Run the verification commands.
- Auto-fail conditions:
  - Fewer than three independent reviewer perspectives complete.
  - The spec silently changes approved product scope.
  - Verification fails without a documented reason.

## Generator Work Log

- Planned slice order:
  1. Update the spec with the three approved decisions.
  2. Dispatch independent read-only reviewers against the updated spec.
  3. Synthesize findings and classify clear fixes versus human questions.
  4. Apply scope-preserving documentation fixes if needed.
  5. Run verification.
  6. Record evaluator findings and evidence.
- Notes:
  - Write ownership remains with Codex only.
  - Reviewers receive the updated product spec and a narrow review lens.
  - Reviewers used:
    - Kierkegaard: requirements and product intent.
    - Locke: edge cases and failure scenarios.
    - Parfit: architecture and implementation feasibility.
    - Ptolemy: testability.
  - Initial spec updates applied:
    - Kept `max_candidates=1000` as the beta guardrail and paired it with
      in-memory retention of every successful engine-produced `BacktestResult`.
    - Preserved meaningful `math.inf` internally while requiring
      JSON/CSV-safe metric-state fields in simple records.
    - Required failed-row diagnostics to include `failure_stage`, `error_type`,
      and `error_message`, with tracebacks excluded from default records.
  - Review-driven clarifications applied:
    - All-rejected grids return an inspectable `GridSearchResult` with rejected
      rows, zero successful rows, and zero eligible selection rows.
    - Constraint callables must return a real `bool`; non-boolean outcomes are
      constraint failures.
    - `fail_fast=True` applies to all failed-row stages.
    - Invalid unknown or non-scalar objective paths are whole-search input
      errors, not per-row `metric_extraction` failures.
    - `metric_extraction` is reserved for unexpected per-row extraction
      failures on known comparison metrics.
    - Every exported comparison metric in simple records has a companion
      metric-state field; `NaN` normalizes to `None` with state
      `"undefined"`.
    - `error_type` is the exception class name.
    - Rejected rows do not receive fake `failure_stage` values.
- Blockers or scope changes: None.

## Evaluator Review

- Findings: No remaining blocking findings after applying scope-preserving
  documentation clarifications from subagent review.
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
  - `uv run pytest tests/structure/docs tests/structure/repo -q` ->
    `67 passed`
- Final disposition: Accepted for this documentation update and review slice.
