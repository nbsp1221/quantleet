# Parameter Exploration Objective Contract Plan

- Date: 2026-05-02
- Task: Record the first-beta objective selection contract
- Status: `complete`
- Risk class: `Tier B`
- Requestor: retn0
- Owner: Codex

## Planner Contract

- Goal: Update the parameter exploration product spec with the approved
  single-objective beta contract and first-class objective metric examples.
- Governing docs:
  - `AGENTS.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/quantcraft-architecture.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing: They define repo workflow, product-spec authority,
  report-surface contracts, package boundaries, and verification lanes.
- In-repo scope:
  - Update `docs/product-specs/parameter-exploration.md`.
  - Record verification evidence in this plan.
- Out-of-repo scope:
  - No new external research collection beyond already-discussed library
    references.
  - No implementation, test, dependency, or runtime package changes.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is a product documentation
  update for planned research tooling and does not modify `trading` or
  `execution` code.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Success criteria:
  - The spec states that beta `objective` is a single
    `(metric_path, direction)` tuple.
  - The spec lists `returns.total_return`, `risk.max_drawdown`,
    `risk.sharpe_ratio`, and `trades.profit_factor` as first-class objective
    examples with directions.
  - The spec excludes multi-objective, weighted objective, Pareto-front
    selection, and custom objective callables from beta scope.
  - The settled metric-path and callable questions are removed from open
    questions.
- Out of scope:
  - Implementing objective extraction or ranking.
  - Adding result-level constraints or filters.
  - Designing multi-objective optimization.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - The updated spec is internally consistent with the approved
    `ParameterStudy(...).grid_search(...)` UX.
  - The beta objective contract remains simple and single-objective.
  - Remaining open questions are still genuinely unresolved.
- Acceptance artifact location:
  - `docs/product-specs/parameter-exploration.md`
  - this plan's `## Evaluator Review`
- How the generator and evaluator agreed on done before execution: The approved
  decision was single objective only, with documented metric-path examples and
  no beta custom callable or multi-objective support.
- Checks the evaluator will use:
  - Review the diff against the approved decision.
  - Confirm no runtime or Tier A behavior was introduced.
  - Run the verification commands.
- Auto-fail conditions:
  - The spec still lists first-class objective paths or custom callables as open
    questions.
  - The spec implies weighted or multi-objective beta selection.
  - Verification fails without documented reason.

## Generator Work Log

- Planned slice order:
  1. Add the approved single-objective contract to the product spec.
  2. Add first-class objective examples and beta non-goals.
  3. Remove settled objective questions.
  4. Run verification.
  5. Record evaluator findings and evidence.
- Notes:
  - Approved objective contract: one `(metric_path, direction)` tuple.
  - Approved first-class examples:
    `("returns.total_return", "max")`,
    `("risk.max_drawdown", "min")`,
    `("risk.sharpe_ratio", "max")`,
    `("trades.profit_factor", "max")`.
- Blockers or scope changes: None.

## Evaluator Review

- Findings: No blocking findings. The product spec now states that beta
  objective selection is single-objective only, documents the four first-class
  objective examples, excludes custom callables and multi-objective/weighted
  selection from beta scope, and removes the settled objective questions from
  open questions.
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
  - `uv run pytest tests/structure/docs tests/structure/repo -q` ->
    `67 passed in 0.19s`
- Final disposition: Accepted for this documentation slice.
