# WFA Pause And Readiness Analysis Plan

- Date: 2026-05-06
- Task: Pause the walk-forward analysis product spec and create a readiness
  analysis for blockers that should be evaluated before WFA implementation
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Convert the WFA product spec from an active future implementation
  target into a paused validation-study decision record, then document the
  known and suspected blockers that should be analyzed before choosing the next
  refactoring slice.
- Governing docs:
  - `AGENTS.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/walk-forward-analysis.md`
  - `docs/design-docs/unified-strategy-runtime-design.md`
  - `docs/PLANS.md`
- Why these are governing:
  - The repo contract requires planner/generator/evaluator workflow for
    non-trivial changes.
  - Product specs route product authority and implemented/future scope.
  - Research ergonomics and parameter exploration define the current strategy
    and parameter-study contracts that WFA would compose.
  - The unified strategy runtime draft records the longer-lived direction for
    strategy authoring across backtest, paper, and live.
- In-repo scope:
  - Update `docs/product-specs/walk-forward-analysis.md`.
  - Update `docs/product-specs/index.md`.
  - Add a WFA readiness/blocker analysis document under `docs/product-specs/`.
  - Record evaluator findings and verification evidence in this plan.
- Out-of-repo scope: none.
- Tier A progression requested: `no`
- Approval record, if required: not required; this is documentation-only
  Tier B research/product planning work.
- Verification commands:
  - `uv run poe repo-check`
  - `git diff --check -- docs/product-specs/walk-forward-analysis.md docs/product-specs/index.md docs/product-specs/walk-forward-analysis-readiness.md docs/plans/2026-05-06-wfa-pause-readiness-analysis.md`
- Success criteria:
  - WFA spec clearly states implementation is paused.
  - WFA spec preserves accepted product decisions: Validation Study
    positioning, `WalkForwardStudy` naming, optimizer naming avoidance,
    `oos_summary` MVP emphasis, future `oos_report` allowance, and internal
    splitter/CV toolkit deferral.
  - A separate readiness document lists WFA blockers without prematurely
    choosing the next refactoring scope.
  - Readiness document includes urgency/priority criteria for future human
    decision-making.
  - Product spec index routes readers to both the paused WFA spec and the
    readiness analysis.
- Out of scope:
  - Runtime implementation.
  - Test scenario specs for WFA.
  - Technical implementation plan for strategy configuration.
  - Final selection of the next refactoring slice.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - The diff must not imply WFA is ready for implementation.
  - The diff must not decide the full StrategyConfig/refactor scope.
  - The diff must keep current implemented `ParameterStudy` behavior intact.
  - The diff must make future decision points inspectable rather than hiding
    them as implementation details.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - The plan above defines documentation-only scope, accepted WFA decisions,
    and the required readiness analysis artifact.
- Checks the evaluator will use:
  - Manual review against user instructions and governing specs.
  - `uv run poe repo-check`
  - `git diff --check`
- Auto-fail conditions:
  - Any code changes.
  - Any Tier A runtime scope.
  - Any wording that treats WFA implementation as unblocked.
  - Any wording that turns StrategyConfig into a finalized implementation
    requirement before the blocker analysis is complete.

## Generator Work Log

- Planned slice order:
  1. Mark WFA product spec as paused and add pause rationale.
  2. Preserve accepted WFA product decisions in the paused spec.
  3. Add WFA readiness/blocker analysis document.
  4. Update product spec routing index.
  5. Run documentation verification.
- Notes:
  - User explicitly requested no further questions before this documentation
    update.
- Blockers or scope changes:
  - None so far.

## Evaluator Review

- Findings:
  - No blocking findings.
  - The WFA product spec is explicitly paused and does not authorize
    implementation.
  - Accepted WFA product decisions are preserved in the paused spec.
  - The readiness document lists blockers and priority inputs without
    finalizing the next refactoring scope.
  - The product spec index routes WFA work through both the paused spec and the
    readiness review.
- Verification evidence:
  - `uv run poe repo-check`
    - Output: `repository checks passed`
  - `git diff --check -- docs/product-specs/walk-forward-analysis.md docs/product-specs/index.md docs/product-specs/walk-forward-analysis-readiness.md docs/plans/2026-05-06-wfa-pause-readiness-analysis.md`
    - Output: no whitespace errors
- Final disposition:
  - Accepted for this documentation slice.
