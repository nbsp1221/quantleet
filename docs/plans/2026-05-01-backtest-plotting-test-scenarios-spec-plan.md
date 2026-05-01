# Backtest Plotting Test Scenarios Spec Plan

- Date: 2026-05-01
- Task: Define test scenarios for the first-beta backtest plotting feature.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Create a durable test-scenario spec that turns the backtest plotting product contract into behavior-focused unit, integration, smoke, structure, and performance-adjacent test scenarios.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing: the task defines acceptance tests for a first-beta backtest result workflow inside the Tier B `backtest` surface and must preserve repo-local verification policy.
- In-repo scope:
  - Add a test-scenario spec under `docs/product-specs/`.
  - Link it from `docs/product-specs/index.md`.
  - Link it from `docs/product-specs/backtest-plotting.md`.
  - Record completion and verification in this active plan.
- Out-of-repo scope:
  - Use web search to ground testing best practices in authoritative sources.
- Tier A progression requested: `no`
- Approval record, if required:
  - Human requestor: user
  - Human approver: user
  - Verification marker: explicit instruction in this thread to research best practices and write a test scenario spec.
  - Granted scope: external research of testing best practices and documentation-only changes to product specs.
  - Expiration: completion of this documentation slice on 2026-05-01.
  - Audit reference: this active plan.
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The test-scenario spec states the user's test philosophy as operational rules.
  - The scenarios test observable contract behavior, not internal implementation choices.
  - The scenarios include edge cases, representative normal cases, failure cases, integration paths, structure/import checks, and performance-adjacent scale checks.
  - The scenarios are concrete enough for a future implementation plan to translate into tests without re-deciding behavior.
  - Product-spec routing points future plot-test work to the new document.
  - `uv run poe repo-check` passes.
- Out of scope:
  - Writing test code.
  - Implementing plotting.
  - Changing package dependencies or runtime code.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The final diff must be documentation-only, must not claim tests or plotting are implemented, and must create a test plan that is broad enough to block likely implementation bugs before runtime work begins.
- Acceptance artifact location: `docs/plans/2026-05-01-backtest-plotting-test-scenarios-spec-plan.md`
- How the generator and evaluator agreed on done before execution: This planner contract defines the document scope, routing requirements, and verification gate.
- Checks the evaluator will use:
  - Inspect the scenario spec for behavior-focused coverage.
  - Inspect routing links.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - The spec only lists happy-path unit tests.
  - The spec encodes private implementation details as required test assertions.
  - The spec omits integration coverage for both `bars=...` and `source=...`.
  - The spec omits drawdown, no-fill, no-drawdown, side-effect, import, or 10,000-bar scenarios.

## Generator Work Log

- Planned slice order:
  1. Draft `docs/product-specs/backtest-plotting-test-scenarios.md`. Completed.
  2. Link it from `docs/product-specs/backtest-plotting.md`. Completed.
  3. Link it from `docs/product-specs/index.md`. Completed.
  4. Run repo-check. Completed.
- Notes:
  - External best-practice research was performed before drafting.
  - The spec defines unit, integration, smoke, structure, perf-adjacent,
    negative, and documentation scenarios.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings. The document is behavior-focused, covers edge cases
    and integration paths, avoids requiring private implementation assertions,
    and links back to the plotting product contract.
- Verification evidence:
  - `uv run poe repo-check` passed on 2026-05-01 with output:
    `repository checks passed`.
- Final disposition:
  - Accepted for this documentation slice.
