# Active Plan Template

- Date: `2026-04-18`
- Task: `Document trading-kernel and unified-runtime architecture insights from research and discussion`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  Preserve the architecture insights gathered from repo analysis, cross-library research, and design discussion in a durable dated document that can guide future `quantleet` engine work without silently becoming governing architecture.
- Governing docs:
  - `AGENTS.md`
  - `ARCHITECTURE.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/quantleet-architecture.md`
  - `docs/design-docs/unified-strategy-runtime-design.md`
  - `docs/PLANS.md`
- Why these are governing:
  - `AGENTS.md` defines the required planner/generator/evaluator workflow.
  - `ARCHITECTURE.md` and `docs/design-docs/*` define the current approved package and ownership boundaries.
  - `docs/PLANS.md` defines where active work records and non-governing historical material should live.
- In-repo scope:
  - Create one active plan for this documentation slice.
  - Create one dated research note under `docs/plans/` capturing the distilled insights.
- Out-of-repo scope:
  - No product-surface or engine code changes.
  - No promotion of new governing architecture authority.
- Tier A progression requested: `no`
- Approval record, if required:
  - Not required for this Tier B documentation-only slice.
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The repository contains a dated document summarizing:
    - what current `quantleet` does and does not implement
    - what was learned from Nautilus, LEAN, backtrader, Zipline, and Freqtrade
    - the recommended layered model for `Strategy`, `Intent`, `Order`, `Fill`, and account state
    - the specific implementation watchpoints for shared backtest/paper/live design
  - The document is clearly non-governing and dated.
  - Repo checks continue to pass.
- Out of scope:
  - Updating public API
  - Changing `trading` or `backtest` code
  - Revising the approved design docs

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - The new document must be internally consistent with approved architecture docs and must not overstate current implementation truth.
- Acceptance artifact location:
  - `docs/plans/2026-04-18-trading-kernel-architecture-insights.md`
- How the generator and evaluator agreed on done before execution:
  - The slice is done when the document preserves the research signal without changing governing architecture and `repo-check` passes.
- Checks the evaluator will use:
  - Review wording against `ARCHITECTURE.md` and approved design docs.
  - Verify placement under `docs/plans/` matches `docs/PLANS.md`.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - The new note claims governing authority.
  - The note contradicts current approved architecture boundaries.
  - Verification is omitted or fails.

## Generator Work Log

- Planned slice order:
  1. Create the active plan.
  2. Write the dated research note.
  3. Run repo verification.
  4. Close the plan with evaluator findings and evidence.
- Notes:
  - The note should synthesize current discussion rather than introduce new product commitments.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No material findings for this documentation-only slice.
  - The new note stays in `docs/plans/` as non-governing dated research, which
    matches `docs/PLANS.md`.
  - The note does not redefine approved architecture authority and instead
    summarizes current truth plus future-facing insights.
- Verification evidence:
  - `2026-04-18`: `uv run poe repo-check` -> `repository checks passed`
- Final disposition:
  - Accepted.
