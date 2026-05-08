# Strategy Configuration Contract Product Spec Plan

- Date: 2026-05-06
- Task: Write the Stage 1 Strategy Configuration Contract product spec
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Create a product spec that defines Quantleet's unified strategy
  configuration contract before `ParameterStudy` migration, reporting metadata
  changes, or WFA implementation continue.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/wfa-prerequisite-roadmap.md`
  - `docs/product-specs/walk-forward-analysis-readiness.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - The repo contract requires an active plan, governing-doc review, scoped
    edits, evaluator review, and fresh verification.
  - The WFA prerequisite roadmap defines this as Stage 1 and keeps Stage 2
    through Stage 4 visible.
  - Existing parameter exploration and research ergonomics specs document the
    current `strategy_factory` and `Strategy.parameters()` surface that this
    spec must intentionally supersede or route to later stages.
  - Architecture and topology docs define capability ownership and prevent
    treating shared strategy runtime contracts as product-surface concerns.
- In-repo scope:
  - Create `docs/product-specs/strategy-configuration-contract.md`.
  - Update product spec routing in `docs/product-specs/index.md`.
  - Update `docs/product-specs/wfa-prerequisite-roadmap.md` related documents
    or Stage 1 pointers if needed.
  - Record evaluator review and verification evidence in this plan.
- Out-of-repo scope:
  - No external files, connectors, secrets, network research, or generated
    artifacts outside this repository.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is product documentation
  under Tier B scope and does not modify `trading` or `execution`.
- Verification commands:
  - `uv run poe repo-check`
  - `git diff --check`
- Success criteria:
  - The new product spec includes background/problem definition, goals,
    non-goals, user intent, core requirements, functional requirements,
    non-functional requirements, scenarios, edge/failure cases, external
    contracts, success conditions, and open questions.
  - The spec captures the grill-me decisions without overcommitting to a
    detailed implementation plan.
  - The spec marks implementation-required scope as Stage 1 and records Stage 2
    and Stage 3 downstream decisions without forcing them into one batch.
  - Product spec routing points readers to the new spec for strategy
    configuration contract work.
  - Fresh verification passes.
- Out of scope:
  - Code changes.
  - Tests for implementation behavior.
  - WFA implementation or WFA resume planning.
  - ParameterStudy migration implementation.
  - Backtest reporting implementation changes.
  - A full parameter descriptor DSL, objective alias registry, DI container, or
    paper/live runner design.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Review the diff against the plan and governing docs.
  - Confirm no code or Tier A behavior was modified.
  - Confirm the new spec can act as a source of truth for later test specs and
    technical implementation plans.
  - Confirm downstream Stage 2/3 decisions are recorded as downstream
    requirements rather than implementation-required Stage 1 scope.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - The planner contract above defines the exact document scope, verification
    commands, and non-goals before edits.
- Checks the evaluator will use:
  - Manual diff review against this plan.
  - `uv run poe repo-check`
  - `git diff --check`
- Auto-fail conditions:
  - Any source-code change.
  - Any WFA implementation requirement added to the Stage 1 spec.
  - Any claim that `StrategyConfig` descriptor DSL, objective aliasing, or
    `BacktestEngine.run(strategy=StrategyClass, config=...)` must be built in
    the first slice.
  - Any undocumented Tier A scope expansion.

## Generator Work Log

- Planned slice order:
  1. Create the Stage 1 product spec.
  2. Add routing from the product spec index.
  3. Add roadmap related-document pointer to the new spec.
  4. Review diff and run verification.
- Notes:
  - Existing untracked WFA docs are treated as prior user/session work and will
    not be reverted.
  - Created `docs/product-specs/strategy-configuration-contract.md`.
  - Updated `docs/product-specs/index.md` to route strategy configuration work
    to the new spec.
  - Updated `docs/product-specs/wfa-prerequisite-roadmap.md` to link the Stage 1
    governing spec.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings.
  - The diff is documentation-only and does not modify source code or Tier A
    runtime behavior.
  - The new product spec includes the requested sections: background/problem
    definition, goals, non-goals, user intent, core requirements, functional
    requirements, non-functional requirements, key scenarios, edge/failure
    cases, external contracts, success conditions, and open questions.
  - Stage 1 implementation-required scope is limited to the unified strategy
    configuration contract. `ParameterStudy` migration and reporting
    source-of-truth changes are recorded as downstream Stage 2 and Stage 3
    requirements rather than forced into the first implementation slice.
  - The spec keeps WFA paused and does not introduce WFA implementation,
    objective aliasing, a parameter descriptor DSL, or a required
    `BacktestEngine.run(strategy=StrategyClass, config=...)` implementation.
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
  - `git diff --check` -> exit 0
  - `git diff --check --no-index /dev/null docs/product-specs/strategy-configuration-contract.md; test $? -le 1` -> exit 0
  - `git diff --check --no-index /dev/null docs/product-specs/wfa-prerequisite-roadmap.md; test $? -le 1` -> exit 0
  - `git diff --check --no-index /dev/null docs/plans/2026-05-06-strategy-configuration-contract-product-spec.md; test $? -le 1` -> exit 0
- Final disposition:
  - Accepted for this documentation slice.
