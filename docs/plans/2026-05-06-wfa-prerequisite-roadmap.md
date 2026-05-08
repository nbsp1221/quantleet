# WFA Prerequisite Roadmap Documentation Plan

- Date: 2026-05-06
- Task: Document the full prerequisite roadmap before WFA resumes
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Add a durable product-level roadmap that preserves the agreed sequence
  from Strategy Configuration Contract work through WFA resumption.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/walk-forward-analysis.md`
  - `docs/product-specs/walk-forward-analysis-readiness.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/unified-strategy-runtime-design.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing: The work changes product-spec routing and planning
  documentation for research/backtest strategy configuration work before WFA
  resumes.
- In-repo scope:
  - Create a product-spec roadmap document under `docs/product-specs/`.
  - Link it from the WFA readiness document.
  - Add it to the product spec routing index.
  - Record evaluator review and verification evidence in this plan.
- Out-of-repo scope: none.
- Tier A progression requested: `no`
- Approval record, if required: not required; this is Tier B documentation work.
- Verification commands:
  - `uv run poe repo-check`
  - `git diff --check -- docs/product-specs/wfa-prerequisite-roadmap.md docs/product-specs/walk-forward-analysis-readiness.md docs/product-specs/index.md docs/plans/2026-05-06-wfa-prerequisite-roadmap.md`
- Success criteria:
  - The roadmap records the four-step sequence:
    1. Unified Strategy Configuration Contract
    2. ParameterStudy Strategy API Migration
    3. Reporting Config Source Of Truth
    4. WFA Resume Spec
  - The roadmap explains why WFA remains paused until the prerequisite sequence
    is deliberately advanced.
  - The roadmap preserves the relationship between P0/P1/P2 readiness blockers
    without turning later work into immediate implementation scope.
  - The product spec index routes future readers to the roadmap before starting
    strategy-config or WFA-unblocking work.
- Out of scope:
  - Implementing StrategyConfig.
  - Writing the next Strategy Configuration Contract product spec.
  - Changing runtime code, tests, examples, or public APIs.
  - Re-ranking the already accepted high-level sequence.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm the new roadmap is a planning/routing document, not an
    implementation spec.
  - Confirm it does not authorize WFA implementation.
  - Confirm it captures the complete agreed sequence and guards against losing
    later steps while the first prerequisite is being discussed.
  - Confirm routing index and WFA readiness references are consistent.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - The planner contract above defines the files, scope, verification commands,
    and success criteria before document edits.
- Checks the evaluator will use:
  - Review changed docs against the planner contract.
  - Run the listed verification commands.
- Auto-fail conditions:
  - The roadmap starts implementing or specifying code-level details.
  - The roadmap removes or weakens the WFA pause.
  - The roadmap omits any of the four agreed follow-on steps.
  - Verification fails.

## Generator Work Log

- Planned slice order:
  1. Create `docs/product-specs/wfa-prerequisite-roadmap.md`.
  2. Link it from `docs/product-specs/walk-forward-analysis-readiness.md`.
  3. Add it to `docs/product-specs/index.md`.
  4. Run verification and record evaluator review.
- Notes:
  - Existing WFA spec/readiness docs are already modified in the working tree.
    This slice builds on them and does not revert prior work.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings.
  - The roadmap is limited to product sequencing and routing; it does not
    specify implementation mechanics for `StrategyConfig`.
  - The roadmap preserves the WFA pause and explicitly blocks WFA implementation
    until prerequisite specs are deliberately advanced.
  - The four agreed stages are present and ordered.
  - The WFA readiness document and product spec index both route readers to the
    roadmap.
- Verification evidence:
  - `uv run poe repo-check`
    - Output: `repository checks passed`
  - `git diff --check -- docs/product-specs/index.md docs/product-specs/walk-forward-analysis-readiness.md`
    - Output: no whitespace errors
  - `git diff --check --no-index /dev/null docs/product-specs/wfa-prerequisite-roadmap.md`
    - Output: no whitespace errors; exit status normalized for expected
      no-index diff
  - `git diff --check --no-index /dev/null docs/plans/2026-05-06-wfa-prerequisite-roadmap.md`
    - Output: no whitespace errors; exit status normalized for expected
      no-index diff
- Final disposition:
  - Accepted.
