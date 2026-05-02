# Parameter Exploration Visualization Scope Plan

- Date: 2026-05-02
- Task: Record the first-beta visualization scope decision
- Status: `complete`
- Risk class: `Tier B`
- Requestor: retn0
- Owner: Codex

## Planner Contract

- Goal: Update the parameter exploration product spec with the approved beta
  visualization boundary: structured comparison output and selected-run plot are
  in scope; heatmap and visual table renderers are deferred.
- Governing docs:
  - `AGENTS.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/quantcraft-architecture.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing: They define repo workflow, product-spec authority,
  report/result plotting scope, package boundaries, and verification lanes.
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
  - The spec states that beta P0 includes structured comparison output,
    selection helpers, records export, and selected-run `BacktestResult.plot()`.
  - The spec states that beta P0 excludes heatmap plotting and visual table
    renderers.
  - The spec preserves structured table-like data output as distinct from
    visual table rendering.
  - The settled visualization question is removed from open questions.
- Out of scope:
  - Implementing result plotting, heatmaps, or table renderers.
  - Choosing a future heatmap API.
  - Adding plotting dependencies or visual regression tests.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - The updated spec does not contradict the existing `BacktestResult.plot()`
    product contract.
  - The beta P0 comparison output remains structured and machine-readable.
  - Remaining open questions are still genuinely unresolved.
- Acceptance artifact location:
  - `docs/product-specs/parameter-exploration.md`
  - this plan's `## Evaluator Review`
- How the generator and evaluator agreed on done before execution: The approved
  decision was to defer heatmap and visual table renderers while keeping
  structured comparison output and selected-run inspection in beta P0.
- Checks the evaluator will use:
  - Review the diff against the approved decision.
  - Confirm no runtime or Tier A behavior was introduced.
  - Run the verification commands.
- Auto-fail conditions:
  - The spec still lists visualization scope as an open question.
  - The spec implies heatmap or visual table rendering is required for beta P0.
  - The spec removes structured comparison records from beta P0.
  - Verification fails without documented reason.

## Generator Work Log

- Planned slice order:
  1. Add the approved visualization boundary to the product spec.
  2. Remove the settled visualization question.
  3. Run verification.
  4. Record evaluator findings and evidence.
- Notes:
  - Approved P0: structured comparison result, helpers, records export, and
    selected successful run `BacktestResult.plot()`.
  - Deferred: heatmap plotting and visual table renderer.
- Blockers or scope changes: None.

## Evaluator Review

- Findings: No blocking findings. The product spec now keeps structured
  comparison output, records export, and selected successful run
  `BacktestResult.plot()` in beta P0 while explicitly deferring heatmap
  plotting and visual table rendering. The settled visualization question was
  removed from open questions.
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
  - `uv run pytest tests/structure/docs tests/structure/repo -q` ->
    `67 passed in 0.19s`
- Final disposition: Accepted for this documentation slice.
