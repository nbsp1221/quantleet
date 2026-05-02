# Parameter Exploration Parameter Value Contract Plan

- Date: 2026-05-02
- Task: Record the first-beta parameter value representation contract
- Status: `complete`
- Risk class: `Tier B`
- Requestor: retn0
- Owner: Codex

## Planner Contract

- Goal: Update the parameter exploration product spec with the approved beta
  parameter value contract and close the remaining product-spec open questions.
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
  result/report metadata expectations, package boundaries, and verification
  lanes.
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
  - The spec restricts beta parameter grid values to JSON scalar values.
  - The spec rejects non-finite floats and non-scalar structured/object values
    for beta.
  - The spec requires clear errors identifying invalid parameter names, values,
    and types.
  - The spec records that a separate test-scenario spec follows product-spec
    closure.
  - The product spec no longer has open product questions.
- Out of scope:
  - Implementing parameter validation.
  - Designing custom encoders or arbitrary-object parameter support.
  - Writing the test-scenario spec in this slice.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - The updated spec keeps beta result records machine-readable and
    agent-friendly.
  - The update does not introduce runtime, dependency, or Tier A behavior.
  - The remaining product-spec open question list is removed or marked closed.
- Acceptance artifact location:
  - `docs/product-specs/parameter-exploration.md`
  - this plan's `## Evaluator Review`
- How the generator and evaluator agreed on done before execution: The approved
  decision was JSON scalar only for beta parameter grid values, with test
  scenarios deferred to a follow-up spec after product-spec closure.
- Checks the evaluator will use:
  - Review the diff against the approved decision.
  - Confirm no runtime or Tier A behavior was introduced.
  - Run the verification commands.
- Auto-fail conditions:
  - The spec still presents parameter value representation as undecided.
  - The spec allows arbitrary objects with `repr` as the beta contract.
  - The spec leaves the test-scenario timing question open.
  - Verification fails without documented reason.

## Generator Work Log

- Planned slice order:
  1. Add the approved JSON scalar parameter value contract to the product spec.
  2. Add invalid-value edge cases.
  3. Record the follow-up test-scenario spec timing.
  4. Remove the remaining open questions.
  5. Run verification.
  6. Record evaluator findings and evidence.
- Notes:
  - Approved beta parameter value types: `str`, `int`, finite `float`, `bool`,
    and `None`.
  - Rejected in beta: arbitrary objects, callables, classes, datetimes,
    decimals, enums, containers, `NaN`, and infinities.
- Blockers or scope changes: None.

## Evaluator Review

- Findings: No blocking findings. The product spec now restricts beta
  parameter grid values to JSON scalar values, rejects arbitrary objects and
  non-finite floats, requires clear invalid-value diagnostics, and replaces the
  open questions list with a follow-up artifact note for the test-scenario spec.
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
  - `uv run pytest tests/structure/docs tests/structure/repo -q` ->
    `67 passed in 0.16s`
- Final disposition: Accepted for this documentation slice.
