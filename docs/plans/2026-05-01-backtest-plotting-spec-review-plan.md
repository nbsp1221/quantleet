# Backtest Plotting Spec Review Plan

- Date: 2026-05-01
- Task: Review the first-beta backtest plotting spec with parallel subagents and apply clear documentation fixes.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Use at least three read-only reviewer subagents to find material issues in the plotting spec, then apply only issues whose fix is clear from evidence and best practices.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing: the task reviews and may revise a product spec for a first-beta public result workflow, while preserving repository workflow, capability ownership, and Tier B verification expectations.
- In-repo scope:
  - Review `docs/product-specs/backtest-plotting.md`.
  - Update the plotting spec and related routing/spec references only if findings have one clear best-practice fix.
  - Record review and verification outcome in this plan.
- Out-of-repo scope:
  - Web research is allowed only if needed to resolve best-practice or dependency evidence.
- Tier A progression requested: `no`
- Approval record, if required:
  - Human requestor: user
  - Human approver: user
  - Verification marker: explicit request in this thread to use subagent orchestration and apply clear document fixes without further confirmation.
  - Granted scope: read-only subagent review of the plotting spec and single-writer documentation fixes within the product spec surface.
  - Expiration: completion of this review slice on 2026-05-01.
  - Audit reference: this active plan.
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - At least three reviewer subagents return evidence-backed findings or empty-findings reports.
  - Parent synthesis deduplicates and filters findings.
  - Clear, evidence-backed fixes are applied without asking the user.
  - Human-intent questions, if any, are separated from applied fixes.
  - The final state passes `uv run poe repo-check`.
- Out of scope:
  - Implementing plotting.
  - Changing package dependencies.
  - Modifying runtime, tests, examples, or notebooks.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Review coverage must include multiple independent lenses, applied edits must stay documentation-only, and the final report must distinguish applied fixes from human-intent questions.
- Acceptance artifact location: `docs/plans/2026-05-01-backtest-plotting-spec-review-plan.md`
- How the generator and evaluator agreed on done before execution: This planner contract defines the review scope, write boundary, and verification gate.
- Checks the evaluator will use:
  - Inspect subagent outputs for evidence.
  - Inspect diff for scope control.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - Fewer than three subagent reviews are used.
  - A reviewer is asked to edit files.
  - The parent applies changes requiring product-priority judgment without asking the user.
  - The final documentation claims plotting is already implemented.

## Generator Work Log

- Planned slice order:
  1. Dispatch API/UX reviewer. Completed.
  2. Dispatch architecture/data-ownership reviewer. Completed.
  3. Dispatch packaging/dependency reviewer. Completed.
  4. Dispatch testing/implementation-readiness reviewer. Completed.
  5. Synthesize findings. Completed.
  6. Apply clear fixes. Completed.
  7. Run repo-check. Completed.
- Notes:
  - Reviewers are read-only; the parent is the only writer.
  - Applied fixes clarified plot data ownership, immutable snapshot behavior,
    constructor compatibility, timestamp rendering, no-fill rendering, display
    patterns, dataset scale, dependency metadata, import locality, and
    verification requirements.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings remain for this documentation review slice. Four
    read-only subagents produced evidence-backed review output, and the parent
    applied the findings with one clear documentation fix. No human-intent
    question remained after synthesis.
- Verification evidence:
  - `uv run poe repo-check` passed on 2026-05-01 with output:
    `repository checks passed`.
- Final disposition:
  - Accepted for this review slice.
