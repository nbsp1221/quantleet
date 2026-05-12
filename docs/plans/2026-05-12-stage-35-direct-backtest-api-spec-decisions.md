# Stage 3.5 Direct Backtest API Spec Decisions Plan

- Date: 2026-05-12
- Task: Record Stage 3.5 human decisions in the product spec and a separate
  test-scenarios spec
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Turn the Stage 3.5 tracking document into a decision-bearing product
  spec and add a concrete test-scenarios spec that can feed implementation
  planning.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/direct-backtest-class-config-api.md`
  - `docs/product-specs/wfa-prerequisite-roadmap.md`
  - `docs/product-specs/walk-forward-analysis-readiness.md`
  - `docs/product-specs/walk-forward-analysis.md`
  - `docs/product-specs/reporting-config-source-of-truth.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - The repo contract requires an active plan for non-trivial document changes.
  - Stage 3.5 is a WFA prerequisite under the product-spec routing surface.
  - The package topology and safety docs constrain this to Tier B
    `backtest`, `strategy`, and `research` planning.
- In-repo scope:
  - Update `direct-backtest-class-config-api.md` with the closed decisions from
    the Stage 3.5 grill-me pass.
  - Add `direct-backtest-class-config-api-test-scenarios.md`.
  - Route the new test-scenarios spec from `docs/product-specs/index.md`.
  - Keep this as product/test specification work only.
- Out-of-repo scope:
  - No code implementation, package dependency changes, network calls, external
    connectors, or non-repo files.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is Tier B documentation work
  and does not change `trading` or `execution`.
- Verification commands:
  - `uv run poe repo-check`
  - `git diff --check`
- Success criteria:
  - Product spec records the human decisions as closed policy.
  - Test-scenarios spec defines good Stage 3.5 tests and concrete scenarios for
    code behavior, documentation/examples, and temporary transition checks.
  - The docs distinguish permanent executable-doc/smoke checks from temporary
    old-API-removal checks.
  - WFA remains paused and Stage 4 remains blocked on Stage 3.5 completion or
    explicit human deferral.
  - Fresh verification passes.
- Out of scope:
  - Implementing the new `BacktestEngine.run(...)` API.
  - Editing README, docs/site, tests, or source code to the new API.
  - Writing the Stage 3.5 implementation plan.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm every closed Stage 3.5 decision is represented in the product spec.
  - Confirm the test-scenarios spec is concrete enough to guide implementation.
  - Confirm no source code, tests, or Tier A files changed.
  - Confirm verification evidence is fresh.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - This plan records scope, decisions to capture, verification commands, and
    auto-fail conditions before edits.
- Checks the evaluator will use:
  - Manual diff review.
  - `uv run poe repo-check`
  - `git diff --check`
- Auto-fail conditions:
  - Any code or test implementation changes.
  - Product spec leaves a closed grill-me decision as open.
  - Test-scenarios spec treats temporary old-API text checks as permanent
    hard gates.
  - WFA implementation is authorized by accident.
  - Verification fails without a documented blocker.

## Generator Work Log

- Planned slice order:
  1. Patch the Stage 3.5 product spec with closed policy decisions. `complete`
  2. Add the Stage 3.5 test-scenarios spec. `complete`
  3. Route the test-scenarios spec from the product-spec index. `complete`
  4. Review the diff for scope and terminology. `complete`
  5. Run verification. `complete`
  6. Record evaluator findings. `complete`
- Notes:
  - Existing Stage 3.5 tracking edits from 2026-05-11 remain in the working
    tree and are continued, not reverted.
  - The user requested no more large-policy questions unless needed.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings. The Stage 3.5 product spec now records the closed
    human decisions for class-plus-config direct backtests, strict config
    policy, default config behavior, early validation, `ParameterStudy`
    alignment, public docs cleanup, temporary transition checks, and WFA
    construction reuse.
  - The separate test-scenarios spec defines good-test criteria and concrete
    unit, integration, reporting, documentation, smoke, and temporary
    transition scenarios.
  - The test-scenarios spec explicitly distinguishes permanent executable
    public-example checks from temporary old-API text checks.
  - No source code, test implementation, or Tier A files changed.
- Verification evidence:
  - `uv run poe repo-check` passed with `repository checks passed`.
  - `git diff --check` passed.
- Final disposition:
  - Accepted. The Stage 3.5 product/test spec decision slice is ready to feed a
    technical implementation plan.
