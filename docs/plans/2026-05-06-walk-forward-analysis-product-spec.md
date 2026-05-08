# Walk-Forward Analysis Product Spec Plan

- Date: 2026-05-06
- Task: Walk-forward analysis product spec
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal:
  - Create a governing product-spec draft for Quantleet walk-forward analysis
    research workflows.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - The task defines a future research-layer product contract on top of the
    current backtest and parameter exploration surfaces.
  - The work changes product-spec routing but must not change runtime behavior.
  - The research layer is Tier B; `trading` and `execution` behavior are out of
    scope.
- In-repo scope:
  - Add `docs/product-specs/walk-forward-analysis.md`.
  - Update `docs/product-specs/index.md` to route future WFA work to the new
    product spec.
  - Record evaluator review and verification evidence in this plan.
- Out-of-repo scope:
  - External research, network access, implementation, API publication, and
    runtime behavior changes.
- Tier A progression requested: `no`
- Approval record, if required:
  - Not required. This slice is documentation-only Tier B work.
- Verification commands:
  - `git diff -- docs/product-specs/walk-forward-analysis.md docs/product-specs/index.md docs/plans/2026-05-06-walk-forward-analysis-product-spec.md`
  - `uv run poe repo-check`
- Success criteria:
  - The new product spec captures background, problem definition, goals,
    non-goals, user intent, requirements, scenarios, edge cases, external
    contracts, success conditions, and open questions.
  - The spec stays product-level and does not over-prescribe implementation.
  - Product-spec routing points WFA work to the new document.
  - Verification evidence is recorded in this plan.
- Out of scope:
  - Implementing `WalkForwardStudy`.
  - Writing tests for WFA behavior.
  - Updating public docs, examples, notebooks, or package exports.
  - Changing `ParameterStudy`, `BacktestEngine`, `trading`, or `execution`.

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex evaluator pass after the documentation edit.
- Evaluator-owned done contract for this slice:
  - The diff is documentation-only and limited to the plan, product spec, and
    product-spec routing index.
  - The product spec defines what and why, leaving implementation details for a
    later test spec and technical implementation plan.
  - The spec aligns with current research ergonomics and parameter exploration
    contracts.
- Acceptance artifact location:
  - This plan's `## Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - The generator must not edit runtime code or tests in this slice.
- Checks the evaluator will use:
  - Review the diff for scope creep and implementation overreach.
  - Run the verification command listed in the planner contract.
- Auto-fail conditions:
  - Runtime code changes are made.
  - The spec claims WFA is currently implemented.
  - The spec presents WFA output as proof of tradable alpha.
  - The index does not route WFA work to the new spec.

## Generator Work Log

- Planned slice order:
  1. Draft the product spec.
  2. Add the product-spec routing row.
  3. Run verification.
  4. Record evaluator review.
- Notes:
  - Product decisions already established in the conversation should be
    captured as requirements where stable.
  - Ambiguous choices should be kept under open questions.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No findings. The diff is documentation-only and limited to the active plan,
    new product spec, and product-spec routing index.
  - The product spec keeps WFA as draft/future scope and does not claim runtime
    implementation.
  - The spec defines the product contract at the what/why level and leaves
    lower-level implementation choices as open questions or later-plan work.
- Verification evidence:
  - `uv run poe repo-check`
    - Result: `repository checks passed`
  - `git diff --check -- docs/product-specs/walk-forward-analysis.md docs/product-specs/index.md docs/plans/2026-05-06-walk-forward-analysis-product-spec.md`
    - Result: no whitespace errors reported.
- Final disposition:
  - Accepted for this documentation slice.
