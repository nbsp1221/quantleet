# Parameter Exploration Parallel Scope Plan

- Date: 2026-05-02
- Task: Record the first-beta parallel execution scope decision
- Status: `complete`
- Risk class: `Tier B`
- Requestor: retn0
- Owner: Codex

## Planner Contract

- Goal: Update the parameter exploration product spec with the approved beta
  execution model: sequential execution only, no public parallel controls, and
  deterministic row identity that leaves room for future parallelism.
- Governing docs:
  - `AGENTS.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/quantcraft-architecture.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing: They define repo workflow, product-spec authority,
  backtest/research execution boundaries, package responsibilities, and
  verification lanes.
- In-repo scope:
  - Update `docs/product-specs/parameter-exploration.md`.
  - Record verification evidence in this plan.
- Out-of-repo scope:
  - No new external research collection beyond already-discussed library
    references.
  - No implementation, test, dependency, or runtime package changes.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is a product documentation
  update for planned research tooling and does not modify `trading` or
  `execution` code.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Success criteria:
  - The spec states that beta P0 `grid_search(...)` executes candidates
    sequentially.
  - The spec states that beta P0 exposes no public `n_jobs`, `workers`,
    `parallel`, or `executor` controls.
  - The spec requires deterministic row identity/order that can survive future
    bounded parallel execution.
  - The settled parallel execution question is removed from open questions.
- Out of scope:
  - Implementing parallel execution.
  - Choosing thread/process/Ray/joblib execution internals.
  - Defining cancellation, progress callbacks, worker failure, or serialization
    policies.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - The updated spec keeps beta execution simple and deterministic.
  - The update does not introduce runtime, dependency, or Tier A behavior.
  - Remaining open questions are still genuinely unresolved.
- Acceptance artifact location:
  - `docs/product-specs/parameter-exploration.md`
  - this plan's `## Evaluator Review`
- How the generator and evaluator agreed on done before execution: The approved
  decision was sequential-only beta execution with future-compatible row
  identity and no public parallel controls.
- Checks the evaluator will use:
  - Review the diff against the approved decision.
  - Confirm no runtime or Tier A behavior was introduced.
  - Run the verification commands.
- Auto-fail conditions:
  - The spec still lists parallel execution as an open question.
  - The spec implies beta support for `n_jobs`, workers, parallel mode, or custom
    executors.
  - The spec fails to preserve deterministic row identity/order.
  - Verification fails without documented reason.

## Generator Work Log

- Planned slice order:
  1. Add the approved sequential-only execution boundary to the product spec.
  2. Add deterministic row identity/order requirements.
  3. Remove the settled parallel execution question.
  4. Run verification.
  5. Record evaluator findings and evidence.
- Notes:
  - Approved P0: sequential candidate execution.
  - Deferred: public parallel controls and executor internals.
- Blockers or scope changes: None.

## Evaluator Review

- Findings: No blocking findings. The product spec now states that beta P0
  candidate execution is sequential, exposes no public `n_jobs`, `workers`,
  `parallel`, or `executor` controls, and requires deterministic row identity
  and ordering suitable for future bounded parallel execution. The settled
  parallel execution question was removed from open questions.
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
  - `uv run pytest tests/structure/docs tests/structure/repo -q` ->
    `67 passed in 0.17s`
- Final disposition: Accepted for this documentation slice.
