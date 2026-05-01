# Backtest Plotting Spec Plan

- Date: 2026-05-01
- Task: Define the first-beta backtest plotting product spec and dependency decision.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Create a durable product spec for the first-beta `BacktestResult.plot()` workflow, including the public API, result-data ownership, dependency strategy, and success criteria.
- Governing docs:
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing: plotting is a first-beta research/backtest UX contract, changes the documented public result workflow, and must preserve the capability-first package ownership and Tier B verification expectations.
- In-repo scope:
  - Add a product spec under `docs/product-specs/`.
  - Update product-spec routing.
  - Add cross-reference from the existing research ergonomics result surface.
- Out-of-repo scope:
  - Use web search and official/project sources only as evidence for the dependency strategy decision.
- Tier A progression requested: `no`
- Approval record, if required:
  - Human requestor: user
  - Human approver: user
  - Verification marker: explicit user instruction in this thread to always perform web search before decisions and to write the spec using mandatory matplotlib dependency direction.
  - Granted scope: external research of plotting/dependency strategies in comparable Python quant libraries for this spec task.
  - Expiration: completion of this spec document slice on 2026-05-01.
  - Audit reference: this active plan.
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - A new product spec records what the first-beta plot feature is and is not.
  - The spec explains why `result.plot()` is the primary API.
  - The spec records why engine-produced `BacktestResult` must retain a run snapshot rather than asking users to pass bars again.
  - The spec records matplotlib as a normal runtime dependency for the beta plot workflow.
  - The spec defines concrete success and non-goal conditions for implementation.
  - Product-spec routing points future work to the new spec.
- Out of scope:
  - Implementing `BacktestResult.plot()`.
  - Moving `matplotlib` from dev dependencies to runtime dependencies.
  - Updating examples or notebooks.
  - Changing backtest runtime behavior.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The diff must be documentation-only, must not touch Tier A code, must not claim plotting is already implemented, and must include fresh repo-check evidence.
- Acceptance artifact location: `docs/plans/2026-05-01-backtest-plotting-spec-plan.md`
- How the generator and evaluator agreed on done before execution: The planner contract above is the definition of done for this documentation slice.
- Checks the evaluator will use:
  - Review the diff against the governing docs and requested decisions.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - Spec routes users to `plot_backtest(...)` or `result.plot(bars=...)` as the primary beta API.
  - Spec leaves the dependency decision ambiguous.
  - Spec presents optional matplotlib installation as the beta default.
  - Spec claims implementation is complete.

## Generator Work Log

- Planned slice order:
  1. Add `docs/product-specs/backtest-plotting.md`.
  2. Update `docs/product-specs/index.md`.
  3. Update `docs/product-specs/research-ergonomics.md`.
  4. Run `uv run poe repo-check`.
- Notes:
  - External research evidence was refreshed in this thread before writing the spec.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings. The slice is documentation-only, routes future plot work to the new product spec, records `result.plot()` as the primary beta API, and records `matplotlib` as a required runtime dependency for the beta plot workflow.
- Verification evidence:
  - `uv run poe repo-check` passed on 2026-05-01 with output: `repository checks passed`.
- Final disposition:
  - Accepted for this documentation slice.
