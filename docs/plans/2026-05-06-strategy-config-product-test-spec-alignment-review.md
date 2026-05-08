# Strategy Config Product/Test Spec Alignment Review Plan

- Date: 2026-05-06
- Task: Review the Strategy Configuration Contract product spec and test spec
  together before technical implementation planning
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Orchestrate independent subagent reviews of the product and test specs,
  synthesize findings, apply clear scope-preserving documentation fixes, and
  report remaining human decisions before technical planning.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/strategy-configuration-contract.md`
  - `docs/product-specs/strategy-configuration-contract-test-scenarios.md`
  - `docs/product-specs/wfa-prerequisite-roadmap.md`
  - `docs/product-specs/walk-forward-analysis-readiness.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/parameter-exploration-test-scenarios.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing:
  - The repo contract requires a planner/generator/evaluator loop and fresh
    verification for non-trivial documentation work.
  - The two strategy configuration docs are the artifacts under review.
  - WFA roadmap/readiness and parameter exploration docs define surrounding
    scope and current-contract interactions.
  - Architecture and reliability docs constrain package ownership, test lanes,
    and safety boundaries.
- In-repo scope:
  - Review product/test spec alignment.
  - Apply non-controversial documentation clarifications to the two strategy
    configuration docs and, if needed, routing docs.
  - Record subagent synthesis, evaluator review, and verification evidence in
    this plan.
- Out-of-repo scope:
  - No source code changes, test implementation, network research, connectors,
    secrets, or out-of-repo files.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is Tier B documentation
  review and does not modify `trading` or `execution`.
- Verification commands:
  - `uv run poe repo-check`
  - `git diff --check`
  - `git diff --check --no-index /dev/null docs/product-specs/strategy-configuration-contract.md; test $? -le 1`
  - `git diff --check --no-index /dev/null docs/product-specs/strategy-configuration-contract-test-scenarios.md; test $? -le 1`
  - `git diff --check --no-index /dev/null docs/plans/2026-05-06-strategy-config-product-test-spec-alignment-review.md; test $? -le 1`
- Success criteria:
  - At least three independent subagent reviews are completed.
  - Findings are synthesized across product intent, test quality, edge cases,
    and implementation risk.
  - Clear improvements that preserve product intent and scope are applied.
  - Questions requiring product/scope/priority/trade-off judgment are reported
    without being resolved by the agent.
  - Fresh verification passes.
- Out of scope:
  - Writing the technical implementation plan.
  - Implementing product or test code.
  - Resolving Stage 2/3 questions.
  - WFA implementation or WFA resume planning.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm review fan-out used at least three independent, read-only
    subagents.
  - Confirm applied edits are clarifications, not unapproved scope changes.
  - Confirm product and test specs remain aligned and Stage 2/3 material stays
    downstream.
  - Confirm no source code or Tier A runtime behavior changed.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - This plan defines review lenses, edit boundaries, escalation criteria, and
    verification commands before subagent fan-out.
- Checks the evaluator will use:
  - Subagent final responses.
  - Manual diff review.
  - `uv run poe repo-check`
  - `git diff --check`
- Auto-fail conditions:
  - Fewer than three subagent reviews.
  - Any code/test implementation changes.
  - Any unapproved product intent, scope, or priority change.
  - Any Stage 2/3 scenario promoted to Stage 1 completion gate without a product
    decision.

## Generator Work Log

- Planned slice order:
  1. Launch read-only subagent review fan-out.
  2. Synthesize product/test alignment findings.
  3. Apply scope-preserving document clarifications.
  4. Run verification.
  5. Record evaluator findings and final disposition.
- Notes:
  - Existing untracked WFA/spec docs are prior session work and will not be
    reverted.
- Blockers or scope changes:
  - None.

## Subagent Review Synthesis

- Subagents used:
  - Product and requirements alignment reviewer: checked whether the product
    spec still expresses the user's intent and whether Stage 1, Stage 2, and
    Stage 3 boundaries are clear.
  - Test quality reviewer: checked whether the test spec verifies observable
    contracts rather than private implementation details.
  - Edge case and failure scenario reviewer: checked boundary inputs,
    malformed declarations, rejected candidates, and failure ordering.
  - Implementation risk reviewer: checked whether the specs are clear enough to
    feed a technical implementation plan without hidden architecture decisions.
- Key synthesized findings:
  - The overall direction is aligned: Stage 1 is a shared strategy
    configuration contract, not WFA, not `ParameterStudy` migration, and not
    reporting migration.
  - The main clarity risk is mixing Stage 1 contract behavior with downstream
    Stage 2/3 application behavior. The docs already separate most of this, but
    downstream row-shape and malformed-grid hooks needed clearer labels.
  - Stage 1 tests need a public or contract-level observable surface for schema
    discovery, materialization, and snapshot normalization. Private generic
    introspection helpers should not become the test contract.
  - Test placement must follow the chosen shared strategy/runtime package path,
    not default to `research` if the implementation puts the shared contract
    elsewhere.
  - Validation failures should occur before user callbacks with side effects.
    Stage 1 should prove this for the contract-level path; Stage 2 should later
    prove it for `ParameterStudy` preflight.
  - Several questions are true implementation-plan blockers rather than
    general open questions: package ownership, observable Stage 1 surface,
    snapshot shape, inherited fields, immutability enforcement, optional/None
    handling, config default value domain, and `config_type` fallback behavior.
- Changes applied from synthesis:
  - Added downstream Stage 2 requirements for malformed-grid behavior and
    rejected/failed candidate row materialization questions.
  - Added Stage 2 test hooks for constraint-rejected and failed candidate rows.
  - Expanded open questions in both specs to include the public Stage 1
    observable surface, snapshot shape, inherited fields, same-type redundant
    `config_type`, config default value domain, duplicate-equivalent numeric
    values, and rejected-row `strategy_config` behavior.
- Human decisions intentionally not resolved:
  - Package ownership/import path for `Strategy` and `StrategyConfig`.
  - Whether Stage 1 exposes config objects, normalized mappings, or both.
  - Exact public fallback status of `config_type`.
  - Enforcement and observable behavior for immutability.
  - Whether default values are constrained to report-safe JSON scalars.
  - Stage 2 constraint and rejected-row row-shape semantics.

## Evaluator Review

- Findings:
  - No blocking findings. Four independent read-only review lenses were used.
  - Applied edits are documentation clarifications and downstream question
    surfacing; they do not change the Stage 1 product intent or promote
    Stage 2/3 work into Stage 1 completion gates.
  - No source code, tests, or Tier A runtime behavior changed.
- Verification evidence:
  - `uv run poe repo-check` passed with `repository checks passed`.
  - `git diff --check` passed.
  - `git diff --check --no-index /dev/null docs/product-specs/strategy-configuration-contract.md; test $? -le 1`
    passed.
  - `git diff --check --no-index /dev/null docs/product-specs/strategy-configuration-contract-test-scenarios.md; test $? -le 1`
    passed.
  - `git diff --check --no-index /dev/null docs/plans/2026-05-06-strategy-config-product-test-spec-alignment-review.md; test $? -le 1`
    passed.
- Final disposition:
  - Accepted for this review slice. The specs are directionally aligned for
    technical implementation planning once the listed human decisions are
    resolved or explicitly deferred in the implementation plan.
