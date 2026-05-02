# Parameter Exploration Grid Size Limit Plan

- Date: 2026-05-02
- Task: Record the first-beta grid-size safety limit decision
- Status: `complete`
- Risk class: `Tier B`
- Requestor: retn0
- Owner: Codex

## Planner Contract

- Goal: Update the parameter exploration product spec with the approved default
  grid-size safety limit so later implementation work has a clear product
  contract.
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
  package responsibility boundaries, and verification lanes.
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
  - The spec defines the beta default grid-size safety limit as 1000 raw
    cartesian candidates.
  - The spec defines an explicit `max_candidates` override path, including the
    ability to disable the safety limit with an explicit value.
  - The spec clarifies that the safety check happens before constraint
    filtering.
  - The grid-size safety-limit item is removed from open questions.
- Out of scope:
  - Implementing `max_candidates`.
  - Defining progress UI, cancellation, parallel execution, or sampling.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - The updated spec is internally consistent with the approved
    `ParameterStudy(...).grid_search(...)` UX.
  - The safety limit is presented as a product decision, not a suggestion.
  - Remaining open questions are still genuinely unresolved.
- Acceptance artifact location:
  - `docs/product-specs/parameter-exploration.md`
  - this plan's `## Evaluator Review`
- How the generator and evaluator agreed on done before execution: The approved
  decision was option B: default `max_candidates=1000`, explicit override
  required for larger grids.
- Checks the evaluator will use:
  - Review the diff against the approved decision.
  - Confirm no runtime or Tier A behavior was introduced.
  - Run the verification commands.
- Auto-fail conditions:
  - The spec still lists the grid-size safety limit as an open question.
  - The spec makes large grids run silently by default.
  - Verification fails without documented reason.

## Generator Work Log

- Planned slice order:
  1. Add the approved grid-size safety limit to the product spec.
  2. Remove the corresponding open question.
  3. Run verification.
  4. Record evaluator findings and evidence.
- Notes:
  - Approved beta limit: 1000 raw cartesian candidates by default.
  - Approved override: explicit `max_candidates` value, including explicit
    disabling when the user chooses to accept unlimited candidate count risk.
- Blockers or scope changes: None.

## Evaluator Review

- Findings: No blocking findings. The product spec now defines
  `max_candidates=1000` as the first-beta default safety limit, requires an
  explicit override for larger raw cartesian grids, clarifies that the check
  happens before constraint filtering, and removes the settled question from
  open questions.
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
  - `uv run pytest tests/structure/docs tests/structure/repo -q` ->
    `67 passed in 0.19s`
- Final disposition: Accepted for this documentation slice.
