# Parameter Exploration Product Spec Review Plan

- Date: 2026-05-02
- Task: Review the parameter exploration product spec with parallel third-party
  subagent reviewers
- Status: `complete`
- Risk class: `Tier B`
- Requestor: retn0
- Owner: Codex

## Planner Contract

- Goal: Orchestrate independent reviews of the parameter exploration product
  spec, apply clear low-risk documentation fixes, and report remaining
  questions that require human judgment.
- Governing docs:
  - `AGENTS.md`
  - `ARCHITECTURE.md`
  - `docs/PLANS.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/quantcraft-architecture.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
- Why these are governing: They define repo workflow, product-spec authority,
  current research/backtest scope, package boundaries, and verification lanes.
- In-repo scope:
  - Review `docs/product-specs/parameter-exploration.md`.
  - Apply only documentation clarifications that preserve approved product
    intent and scope.
  - Record verification evidence in this plan.
- Out-of-repo scope:
  - No new external API usage, dependency changes, or non-repo edits.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is a product documentation
  review and does not modify `trading` or `execution` code.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Success criteria:
  - At least three independent subagent reviews are collected with distinct
    perspectives.
  - Findings are synthesized and deduplicated.
  - Clear documentation-only improvements are applied without changing approved
    product scope.
  - Human-judgment questions are separated from auto-applied fixes.
  - Verification passes or failures are recorded.
- Out of scope:
  - Changing approved beta product scope.
  - Writing the test-scenario spec.
  - Implementing parameter exploration.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - The final report names the reviewers, perspectives, major findings, applied
    changes, and unresolved human questions.
  - The spec remains internally consistent after any edits.
  - Any open product decisions are not decided silently.
- Acceptance artifact location:
  - `docs/product-specs/parameter-exploration.md`
  - this plan's `## Evaluator Review`
- How the generator and evaluator agreed on done before execution: The review
  is complete when subagent evidence has been synthesized, low-risk doc fixes
  are applied, and verification evidence is recorded.
- Checks the evaluator will use:
  - Review subagent outputs and final diff.
  - Confirm no code/runtime/Tier A behavior was changed.
  - Run the verification commands.
- Auto-fail conditions:
  - Fewer than three independent reviewer perspectives complete.
  - Product scope is changed without human approval.
  - Verification fails without documented reason.

## Generator Work Log

- Planned slice order:
  1. Dispatch independent read-only reviewers.
  2. Review the spec locally while reviewers run.
  3. Synthesize findings and classify fixes vs. human questions.
  4. Apply clear documentation-only fixes.
  5. Run verification.
  6. Record evaluator findings and evidence.
- Notes:
  - Reviewer context should stay minimal: spec path, role, and expected evidence.
  - Write ownership remains with Codex only.
  - Reviewers used:
    - Tesla: requirements and product intent.
    - Heisenberg: edge cases and failure scenarios.
    - Mendel: architecture and implementation feasibility.
    - Kuhn: testability.
  - Clear documentation fixes applied:
    - Rejected combinations are full rejected rows, not aggregate-only counts.
    - Constraint exceptions become failed rows by default and respect
      `fail_fast=True`.
    - Strategy freshness requires one `strategy_factory` call per admissible
      run, not reset/reuse of a mutated strategy.
    - Parameter candidate values are ordered sequences; unordered containers and
      duplicate candidate values are invalid.
    - Selection helper diagnostics, no-eligible-row behavior, and tie ordering
      are explicit.
    - Undefined structured record values use `None`.
    - Parameter values remain nested under `parameters` in records to avoid row
      field collisions.
    - Source-load failures are clarified as pre-study data/source concerns.
    - `ParameterStudy` is marked as the planned public contract rather than an
      existing contract.
    - Beta result storage is clarified as in-memory only with no persistence,
      resume, retry queue, caching, or streaming storage.
- Blockers or scope changes: None.

## Evaluator Review

- Findings: No blocking findings after applying documentation clarifications.
  Remaining questions require human priority or trade-off judgment and are
  reported to the requestor rather than silently decided.
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
  - `uv run pytest tests/structure/docs tests/structure/repo -q` ->
    `67 passed in 0.27s`
- Final disposition: Accepted for this documentation review slice.
