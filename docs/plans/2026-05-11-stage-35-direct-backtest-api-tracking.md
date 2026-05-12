# Stage 3.5 Direct Backtest API Tracking Plan

- Date: 2026-05-11
- Task: Add Stage 3.5 tracking for direct backtest class-plus-config API
  alignment before WFA resume planning
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Update the WFA prerequisite documents so Stage 3.5 is visible as the
  next focused decision slice before Stage 4 WFA resume planning.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/wfa-prerequisite-roadmap.md`
  - `docs/product-specs/walk-forward-analysis-readiness.md`
  - `docs/product-specs/walk-forward-analysis.md`
  - `docs/product-specs/reporting-config-source-of-truth.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - The repo contract requires an active plan before non-trivial doc changes.
  - The WFA roadmap and readiness docs define the paused WFA prerequisite path.
  - The reporting spec already records direct-backtest class-plus-config API
    alignment as a WFA prerequisite after Stage 3.
  - Architecture and package-topology docs constrain ownership to `backtest`,
    `strategy`, and `research` without touching Tier A domains.
- In-repo scope:
  - Add a Stage 3.5 product-spec tracking document for direct backtest
    class-plus-config API alignment.
  - Update product-spec routing, WFA roadmap, WFA readiness, and WFA paused spec
    references so Stage 3.5 is visible before Stage 4.
  - Keep Stage 3.5 decisions open for the next grill-me pass.
- Out-of-repo scope:
  - No network research, external connectors, generated docs deployment, or
    non-repo files.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is Tier B documentation
  planning and does not modify `trading` or `execution`.
- Verification commands:
  - `uv run poe repo-check`
  - `git diff --check`
- Success criteria:
  - Stage 3.5 appears as a distinct WFA prerequisite between Stage 3 and Stage
    4.
  - The new tracking doc explains the work in plain language and lists the
    human decisions for the next grill-me pass.
  - Stage 4 remains WFA resume planning and is not treated as WFA
    implementation.
  - No source code or test behavior changes.
  - Fresh verification passes.
- Out of scope:
  - Implementing `BacktestEngine.run(strategy=StrategyClass, config=...)`.
  - Deciding the final Stage 3.5 API details.
  - Writing the full Stage 3.5 implementation plan.
  - Resuming Stage 4 WFA product planning.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm Stage 3.5 is discoverable from the product-spec index and WFA
    prerequisite roadmap.
  - Confirm the documents preserve WFA as paused and keep Stage 3.5 decisions
    open for human review.
  - Confirm no source code, tests, or Tier A files changed.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - This plan records the exact documentation scope, non-goals, verification
    commands, and auto-fail conditions before edits.
- Checks the evaluator will use:
  - Manual diff review against this plan and governing docs.
  - `uv run poe repo-check`
  - `git diff --check`
- Auto-fail conditions:
  - Any implementation code changes.
  - Any document says WFA implementation may start before Stage 3.5 decisions
    are closed or explicitly deferred.
  - Any Stage 3.5 API decision is presented as final without a human decision.
  - Verification fails without a documented blocker.

## Generator Work Log

- Planned slice order:
  1. Add the Stage 3.5 tracking product spec.
  2. Route the new spec from the product-spec index.
  3. Update the WFA prerequisite roadmap sequence and dependency rules.
  4. Update WFA readiness and paused WFA spec wording.
  5. Run verification.
  6. Record evaluator findings.
- Notes:
  - The user explicitly paused Stage 4 grill-me and requested Stage 3.5 tracking
    first.
  - The next grill-me pass should focus only on Stage 3.5 decisions.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings. Stage 3.5 is now discoverable from the product-spec
    index, the WFA prerequisite roadmap, the WFA readiness review, and the
    paused WFA spec.
  - The new tracking spec keeps final API choices open for the next human
    decision pass and does not authorize implementation.
  - WFA remains paused; Stage 4 is explicitly blocked on Stage 3.5 completion
    or explicit human deferral.
  - No source code, tests, or Tier A files changed.
- Verification evidence:
  - `uv run poe repo-check` passed with `repository checks passed`.
  - `git diff --check` passed.
- Final disposition:
  - Accepted. The Stage 3.5 tracking slice is complete and ready for a focused
    grill-me decision pass.
