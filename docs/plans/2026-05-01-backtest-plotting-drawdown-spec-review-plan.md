# Backtest Plotting Drawdown Spec Review Plan

- Date: 2026-05-01
- Task: Add drawdown to the first-beta backtest plotting spec and re-review with subagents.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Update the first-beta plot contract so `result.plot()` includes drawdown as a required panel, then run a read-only multi-agent review and apply clear documentation fixes.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing: this changes a first-beta result-visualization product contract, must remain inside the `backtest` capability boundary, and must preserve the repo's planner/generator/evaluator workflow.
- In-repo scope:
  - Update `docs/product-specs/backtest-plotting.md`.
  - Record subagent review synthesis and verification in this plan.
- Out-of-repo scope:
  - Use official/project web documentation only to confirm comparable-library drawdown treatment.
- Tier A progression requested: `no`
- Approval record, if required:
  - Human requestor: user
  - Human approver: user
  - Verification marker: explicit instruction in this thread to include drawdown and re-run subagent-orchestrated review.
  - Granted scope: external research of comparable plotting/drawdown docs and documentation-only changes to the plotting spec.
  - Expiration: completion of this review slice on 2026-05-01.
  - Audit reference: this active plan.
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The plot spec requires price/fills, equity, and drawdown panels for beta.
  - The drawdown data source, label/legend, alignment, empty/no-loss behavior, and tests are explicit.
  - At least three read-only subagents review the updated spec with evidence-backed output.
  - Clear fixes are applied by the parent as single writer.
  - Human-intent questions, if any, are reported separately.
  - `uv run poe repo-check` passes.
- Out of scope:
  - Implementing plotting.
  - Changing runtime result models.
  - Changing package dependencies.
  - Updating examples or notebooks.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The final diff must be documentation-only, must not claim drawdown plotting is already implemented, and must reflect subagent evidence rather than unreviewed expansion.
- Acceptance artifact location: `docs/plans/2026-05-01-backtest-plotting-drawdown-spec-review-plan.md`
- How the generator and evaluator agreed on done before execution: This active plan defines the write boundary, review coverage, and verification gate.
- Checks the evaluator will use:
  - Inspect spec diff for drawdown completeness and scope control.
  - Inspect subagent outputs for evidence-backed findings.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - Drawdown remains out of scope.
  - The spec makes `BacktestReport` the primary plot data source without resolving the existing result-owned plotting decision.
  - Fewer than three subagents review the updated spec.
  - The final documentation claims implementation is complete.

## Generator Work Log

- Planned slice order:
  1. Update plotting spec with required drawdown panel. Completed.
  2. Dispatch read-only reviewers. Completed.
  3. Synthesize findings. Completed.
  4. Apply clear fixes. Completed.
  5. Run repo-check. Completed.
- Notes:
  - Comparable-library evidence confirms drawdown is a first-class plot/report feature in established backtesting and analytics libraries.
  - Four read-only reviewers were used: API/UX, architecture/data ownership,
    implementation/testing, and external-library comparator.
  - Applied fixes clarified that drawdown is included by product decision even
    though comparator defaults vary, added default layout details, fixed the
    drawdown display unit, made the drawdown formula normative, required
    result-owned `drawdown_curve`, and strengthened success criteria.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings remain for this documentation slice. Reviewers raised
    material issues around default inclusion evidence, drawdown formula
    ambiguity, layout defaults, zero-drawdown rendering, equality semantics, and
    10,000-bar verification; the spec now addresses those points.
- Verification evidence:
  - `uv run poe repo-check` passed on 2026-05-01 with output:
    `repository checks passed`.
- Final disposition:
  - Accepted for this review slice.
