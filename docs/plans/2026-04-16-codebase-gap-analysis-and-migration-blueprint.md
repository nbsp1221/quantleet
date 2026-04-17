# Active Plan

- Date: 2026-04-16
- Task: current codebase structure gap analysis against the approved capability-first target architecture
- Status: `complete`
- Risk class: `Tier B`
- Requestor: repository owner
- Owner: Codex

## Planner Contract

- Goal:
  - produce a concrete, repo-wide analysis of how the current `src/quantcraft`
    structure differs from the approved package topology and dependency
    direction
  - capture the gap as a migration blueprint that can guide later code-moving
    slices without pretending the codebase already matches the docs
  - record the newly approved final cleanup stage that prefers completeness over
    backward compatibility for unreleased legacy paths
- Governing docs:
  - [`README.md`](../../README.md)
  - [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
  - [`docs/design-docs/index.md`](../design-docs/index.md)
  - [`docs/design-docs/quantcraft-architecture.md`](../design-docs/quantcraft-architecture.md)
  - [`docs/design-docs/package-topology-and-naming.md`](../design-docs/package-topology-and-naming.md)
  - [`docs/RELIABILITY.md`](../RELIABILITY.md)
  - [`docs/SECURITY.md`](../SECURITY.md)
- Why these are governing:
  - they define the approved capability-first target, dependency rules,
    product-surface boundaries, verification expectations, and safety tiering
- In-repo scope:
  - analyze `src/quantcraft`, `tests`, and structure-check coverage relevant to
    package ownership and migration sequencing
  - write analysis and migration-blueprint documentation under `docs/plans/`
- Out-of-repo scope:
  - moving code
  - changing imports
  - adding import-linter or new mechanical gates
  - external framework or package changes
- Tier A progression requested: `no`
- Approval record, if required:
  - not required for this documentation and analysis slice
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - current package layout is inventoried with concrete evidence
  - gap analysis distinguishes target-authority docs from transitional code
  - migration blueprint identifies staged move order, public-surface risk, test
    impact, and temporary exception handling
  - analysis is cross-checked through read-only subagent fan-out and synthesized
    in the parent agent
- Out of scope:
  - deciding final implementation details for each migration slice
  - performing package moves or test rewrites
  - closing every historical plan/doc inconsistency

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - an active plan records the governing docs, analysis scope, review method,
    and verification surface before analysis output is written
  - the resulting blueprint names the current-to-target package mismatches by
    context, not just general observations
  - the resulting blueprint explains why each migration stage exists and what it
    must preserve
  - subagent findings are evidence-bearing and the final synthesis explicitly
    accepts, rejects, or reframes them
- Acceptance artifact location:
  - this active plan
  - a linked migration-blueprint document under `docs/plans/`
- How the generator and evaluator agreed on done before execution:
  - done is analysis completeness plus cross-validated synthesis, not code
    movement
- Checks the evaluator will use:
  - document diff review against governing docs
  - subagent evidence review
  - `uv run poe repo-check`
- Auto-fail conditions:
  - the blueprint implies code already matches the target when it does not
  - findings are summary-only with no source evidence
  - no explicit staged migration order is proposed
  - repo verification is missing

## Generator Work Log

- Planned slice order:
  1. inventory current source and test topology
  2. run read-only research split for context ownership, test/public-surface
     impact, and mechanical-rule implications
  3. synthesize findings into one migration blueprint
  4. run repo verification and close the evaluator section
- Notes:
  - subagent orchestration is required by the request; subagents stay read-only
    and evidence-oriented
- Blockers or scope changes:
  - 2026-04-16: scope extended to add a final legacy-eradication stage to the
    migration baseline after the initial analysis draft was reviewed

## Evaluator Review

- Findings:
  - current code still materially differs from the approved capability-first
    target:
    - `backtest` ownership remains under `research`
    - `integrations` does not yet exist as a first-class package owner
    - root/public and test surfaces still freeze several transitional import
      paths
    - structure and verification checks still encode parts of the old layout
  - the migration baseline must therefore be additive-first:
    - introduce target package roots first
    - preserve current compatibility surfaces explicitly
    - widen guardrails before behavior moves into new packages
  - the final migration stage is now explicitly defined as a deliberate
    legacy-removal stage:
    - once the new topology is real, unreleased compatibility shims may be
      removed
    - architectural completeness is preferred over preserving transitional
      import paths
- Verification evidence:
  - source and test topology inventory captured in
    [2026-04-16-current-codebase-gap-analysis.md](2026-04-16-current-codebase-gap-analysis.md)
  - read-only research split:
    - `Peirce`: topology/context mismatch review
    - `Cicero`: test/public-surface review
    - `Lovelace`: structure-check and verification-lane review
  - read-only review fan-out after synthesis:
    - `Volta`: Approved: no material findings.
    - `Parfit`: Approved: no material findings.
    - `Plato`: Approved: no material findings.
  - `uv run poe repo-check`
- Final disposition:
  - complete
