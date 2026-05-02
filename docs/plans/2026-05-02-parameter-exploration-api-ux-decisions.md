# Parameter Exploration API UX Decisions Plan

- Date: 2026-05-02
- Task: Record approved first-beta API and UX decisions for parameter exploration
- Status: `complete`
- Risk class: `Tier B`
- Requestor: retn0
- Owner: Codex

## Planner Contract

- Goal: Update the parameter exploration product spec with the API/UX decisions
  approved during brainstorming so later test specs and implementation plans do
  not re-open settled product questions.
- Governing docs:
  - `AGENTS.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/quantcraft-architecture.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing: They define the active product contract, research and
  backtest responsibility split, repo workflow, verification lane, and Tier A
  boundaries.
- In-repo scope:
  - Update `docs/product-specs/parameter-exploration.md`.
  - Record verification evidence in this plan.
- Out-of-repo scope:
  - External library docs remain research inputs only.
  - No implementation, tests, dependency, or runtime package changes.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This slice records product/API UX
  decisions for planned research tooling and does not modify `trading` or
  `execution` code.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Success criteria:
  - The product spec records the approved `ParameterStudy(...).grid_search(...)`
    model.
  - The beta data input contract is materialized `bars`, not direct `source`.
  - The spec records `objective=(metric_path, direction)`.
  - The spec records default continue-on-failure with explicit failed/rejected
    rows and `fail_fast=True` as a debug option.
  - The spec records that all successful runs retain their `BacktestResult`.
  - Settled questions are removed from the open questions list.
- Out of scope:
  - Choosing implementation internals.
  - Writing test scenarios.
  - Implementing `ParameterStudy` or result classes.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - The updated spec is internally consistent and does not contradict current
    implemented docs.
  - Settled UX decisions are clearly marked as product decisions, not loose
    examples.
  - Remaining open questions are genuinely unresolved.
- Acceptance artifact location:
  - `docs/product-specs/parameter-exploration.md`
  - this plan's `## Evaluator Review`
- How the generator and evaluator agreed on done before execution: The approved
  decisions listed in success criteria are the done contract for this doc slice.
- Checks the evaluator will use:
  - Review the diff against the approved decisions.
  - Confirm no Tier A/live/paper behavior was introduced.
  - Run the verification commands.
- Auto-fail conditions:
  - The spec still presents the approved decisions as open questions.
  - The spec makes `source=` the first-beta official `ParameterStudy` input.
  - The spec hides failed/rejected combinations.
  - Verification fails without documented reason.

## Generator Work Log

- Planned slice order:
  1. Add the approved API/UX decisions to the product spec.
  2. Remove or narrow the corresponding open questions.
  3. Run verification.
  4. Record evaluator findings and evidence.
- Notes:
  - Approved public model: `quantcraft.research.ParameterStudy`.
  - Approved execution method: `ParameterStudy.grid_search(...)`.
  - Approved result concept: `GridSearchResult` with inspectable successful
    runs.
- Blockers or scope changes: None.

## Evaluator Review

- Findings: No blocking findings. The updated product spec records the
  approved `ParameterStudy(...).grid_search(...)` UX, materialized `bars`
  input, objective tuple, default continue-on-failure behavior, `fail_fast=True`
  debug option, and retention of every successful run's `BacktestResult`.
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
  - `uv run pytest tests/structure/docs tests/structure/repo -q` ->
    `67 passed in 0.19s`
- Final disposition: Accepted for this documentation slice.
