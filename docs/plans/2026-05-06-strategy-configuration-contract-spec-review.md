# Strategy Configuration Contract Spec Review Plan

- Date: 2026-05-06
- Task: Review the Strategy Configuration Contract product spec with
  independent subagent lenses and apply non-controversial documentation fixes
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Orchestrate at least three independent third-party reviews of
  `docs/product-specs/strategy-configuration-contract.md`, synthesize findings,
  apply clear documentation improvements, and report remaining human decisions.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/strategy-configuration-contract.md`
  - `docs/product-specs/wfa-prerequisite-roadmap.md`
  - `docs/product-specs/walk-forward-analysis-readiness.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing:
  - The repo contract requires a planner/generator/evaluator loop for
    non-trivial documentation changes.
  - The target spec and related roadmap define the product contract under
    review.
  - Existing parameter exploration and research ergonomics specs document the
    current surface the new contract must supersede or route to downstream
    stages.
  - Architecture and package topology docs constrain ownership and public
    surface placement.
- In-repo scope:
  - Review `docs/product-specs/strategy-configuration-contract.md`.
  - Apply clear, non-controversial documentation improvements to the spec and
    any necessary routing/plan notes.
  - Record subagent review synthesis and verification evidence in this plan.
- Out-of-repo scope:
  - No network research, connectors, secrets, or out-of-repo files.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is Tier B product
  documentation review and does not modify `trading` or `execution`.
- Verification commands:
  - `uv run poe repo-check`
  - `git diff --check`
  - `git diff --check --no-index /dev/null docs/product-specs/strategy-configuration-contract.md; test $? -le 1`
  - `git diff --check --no-index /dev/null docs/plans/2026-05-06-strategy-configuration-contract-spec-review.md; test $? -le 1`
- Success criteria:
  - At least three subagents review the spec from distinct viewpoints.
  - Each subagent returns evidence-backed findings.
  - Clear improvements that do not alter product intent or scope are applied.
  - Product-scope changes, trade-off-heavy questions, and priority decisions are
    left for human judgment.
  - Final response reports subagents used, major issues, applied changes, and
    unresolved human questions.
- Out of scope:
  - Source-code changes.
  - Implementing the strategy configuration contract.
  - Changing the product intent without user approval.
  - WFA implementation or WFA resume planning.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm all delegated review lenses were independent and read-only.
  - Confirm applied edits are scope-preserving clarifications.
  - Confirm no implementation details were over-specified beyond the product
    contract.
  - Confirm fresh repository/document verification passes.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - This plan defines review lenses, permitted edits, verification commands,
    and escalation criteria before subagent fan-out and edits.
- Checks the evaluator will use:
  - Subagent final responses.
  - Manual diff review.
  - `uv run poe repo-check`
  - `git diff --check`
- Auto-fail conditions:
  - Fewer than three subagent reviews.
  - Any source-code edit.
  - Any unapproved change to product direction, scope, or priority.
  - Any WFA implementation requirement added to the Stage 1 spec.

## Generator Work Log

- Planned slice order:
  1. Launch read-only subagent review fan-out.
  2. Synthesize findings into actionable categories.
  3. Apply only non-controversial documentation clarifications.
  4. Run verification.
  5. Record evaluator findings and final disposition.
- Notes:
  - Existing untracked WFA/spec docs are prior session work and will not be
    reverted.
  - Launched four read-only subagents:
    - product intent / requirements reviewer
    - edge cases / failure scenarios reviewer
    - architecture / implementation feasibility reviewer
    - testability reviewer
  - Applied only documentation clarifications that preserve the already-agreed
    product direction.
- Blockers or scope changes:
  - None.

## Subagent Review Synthesis

- Product intent reviewer:
  - Found the core product intent coherent and aligned with the WFA prerequisite
    roadmap.
  - Flagged Stage 1 versus Stage 2/3 boundary blur, reporting requirements
    appearing as current functional requirements, `selected_config` terminology,
    and immutable semantics versus unresolved enforcement.
- Edge/failure reviewer:
  - Flagged conflict between the new empty `parameters={}` rule and current
    implemented `ParameterStudy` docs/tests.
  - Flagged underspecified malformed-grid rules, config declaration failures,
    config default portability, and factory-path row shape.
- Architecture/feasibility reviewer:
  - Flagged Stage 1/Stage 2 boundary blur, current `Strategy` not yet generic or
    config-aware, reporting transition ambiguity, package ownership risk for
    future `execution`, and direct instance run metadata tradeoffs.
- Testability reviewer:
  - Flagged missing observable Stage 1 acceptance surface, row-level criteria
    for empty search spaces, qualitative error behavior, and reporting migration
    test assertions.
- Changes applied from review:
  - Added a role split explaining that Stage 1 defines the shared contract while
    Stage 2/3 apply it to `ParameterStudy` and reporting.
  - Clarified `Strategy[Config]` as canonical user-facing declaration while
    leaving internal discovery mechanics to the technical plan.
  - Added config-contract validation failure examples for missing, invalid,
    ambiguous, and conflicting config declarations.
  - Added an architecture constraint that the chosen package path must be legal
    for future `execution` usage and must not force execution to depend on
    `quantleet.research`.
  - Relabeled study preflight as a search-space validation contract that Stage 2
    wires into `ParameterStudy`.
  - Added explicit supersession wording for future canonical
    `parameters={}` behavior versus current implemented `ParameterStudy`
    behavior.
  - Preserved existing deterministic grid-shape protections as the default
    carry-forward rule.
  - Relabeled reporting snapshot requirements as Stage 3 downstream reporting
    contract and clarified Stage 1/2 should not rely on current
    `strategy_parameters` as source of truth.
  - Clarified factory rows do not receive canonical materialized-config row
    guarantees unless Stage 2 explicitly designs a representation.
  - Defined `selected_config` as a WFA role-specific name for a materialized
    `strategy_config`.
  - Added Stage 2 requirements for empty-search-space rows, preflight error
    types/messages, constraint input, and factory-row representation.
- Deferred for human judgment:
  - Whether direct backtests should become class+config canonical earlier than
    currently planned.
  - How strongly immutability must be enforced.
  - Whether config defaults must be JSON-scalar/report-safe in MVP.
  - How to handle optional fields and `None` defaults/candidates.
  - Whether constraints receive candidate parameters, full strategy config, or
    both.
  - What public fallback behavior exists for `config_type`.
  - Whether dropping direct-run `Strategy.parameters()` metadata is acceptable
    during the unpublished beta migration.

## Evaluator Review

- Findings:
  - No blocking findings.
  - Four read-only subagents reviewed the spec with distinct lenses and
    evidence-backed findings.
  - Applied edits are documentation clarifications: stage boundary labels,
    downstream-contract labels, terminology definitions, validation timing, and
    routing of unresolved tradeoffs to later specs/human decisions.
  - No code or Tier A runtime behavior was modified.
  - The spec still keeps WFA paused and does not require WFA implementation,
    objective aliasing, a parameter descriptor DSL, or
    `BacktestEngine.run(strategy=StrategyClass, config=...)` in Stage 1.
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
  - `git diff --check` -> exit 0
  - `git diff --check --no-index /dev/null docs/product-specs/strategy-configuration-contract.md; test $? -le 1` -> exit 0
  - `git diff --check --no-index /dev/null docs/product-specs/wfa-prerequisite-roadmap.md; test $? -le 1` -> exit 0
  - `git diff --check --no-index /dev/null docs/plans/2026-05-06-strategy-configuration-contract-spec-review.md; test $? -le 1` -> exit 0
- Final disposition:
  - Accepted for this documentation review slice.
