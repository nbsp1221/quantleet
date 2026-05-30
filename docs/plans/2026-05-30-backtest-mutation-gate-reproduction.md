# Backtest Mutation Gate Reproduction

- Date: 2026-05-30
- Task: Add a backtest mutation gate to the default check lane and reproduce the current failure.
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Promote the first mutation expansion target, `src/quantleet/backtest`, into the repo-local check surface so `uv run poe check` fails on the current survivor baseline.
- Governing docs:
  - `AGENTS.md`
  - `docs/RELIABILITY.md`
  - `docs/design-docs/agentic-quality-gates.md`
  - `docs/plans/2026-05-30-full-src-mutation-telemetry-experiment.md`
- Why these are governing: This is a quality-gate change for mutation testing, not a product behavior change.
- In-repo scope: Add a lane-specific mutation gate wrapper, wire `mutation-backtest` into Poe, and update structure tests that define the command contract.
- Out-of-repo scope: No remote services.
- Tier A progression requested: `no`
- Approval record, if required: Not required; `backtest` is Tier C for this gate wiring slice.
- Verification commands:
  - `uv run poe mutation-backtest`
  - `uv run poe check`
  - `uv run pytest tests/structure/repo/test_poe_task_contracts.py -q`
- Success criteria:
  - `uv run poe mutation-backtest` fails on current backtest mutation survivors/no-test mutants.
  - `uv run poe check` reaches the new backtest mutation gate and fails for the same reason.
  - The existing `mutation-trading` mutmut configuration remains unchanged.
- Out of scope:
  - Fixing mutation survivors.
  - Establishing a survivor baseline.
  - Making `backtest` mutation pass.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The default check lane must fail for the newly added `backtest` mutation gate, and the failure reason must be the current mutation evidence rather than an unrelated command/configuration error.
- Acceptance artifact location: this plan and final chat report
- How the generator and evaluator agreed on done before execution: The user explicitly requested adding the gate first so check fails.
- Checks the evaluator will use:
  - `uv run poe mutation-backtest`
  - `uv run poe check`
  - `uv run pytest tests/structure/repo/test_poe_task_contracts.py -q`
- Auto-fail conditions:
  - `pyproject.toml` leaves the global `[tool.mutmut]` target changed away from `trading`.
  - The gate fails before running mutmut.
  - Generated mutation artifacts are committed.

## Generator Work Log

- Planned slice order:
  1. Add a small lane-specific mutation gate wrapper.
  2. Add `mutation-backtest` to Poe and include it in `check`.
  3. Update the Poe task contract tests.
  4. Run the targeted contract test and reproduce the mutation failure.
- Notes:
  - mutmut has one project-level configuration block, so lane-specific behavior needs a wrapper that restores `pyproject.toml` after execution.
  - Added `scripts/mutation_gate.py` with a `backtest` lane that temporarily applies the backtest mutmut target, runs mutmut, exports CI stats, and restores `pyproject.toml`.
  - Added the `mutation-backtest` Poe task and inserted it into the default `check` sequence after `coverage-gates`.
  - Updated structure tests that define the required Poe tasks and default `check` sequence.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - `mutation-backtest` is now part of the default `uv run poe check` hard-gate sequence.
  - The default `[tool.mutmut]` block remains targeted at `src/quantleet/trading`; the backtest lane applies its target only during wrapper execution and restores the file afterward.
  - The new gate fails for mutation evidence, not for command wiring or configuration: `survived=798` and `no_tests=22` for `src/quantleet/backtest`.
- Verification evidence:
  - `uv run ruff check scripts/mutation_gate.py tests/structure/repo/test_poe_task_contracts.py`: passed.
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py -q`: passed, `23 passed`.
  - `uv run poe mutation-backtest`: failed as intended with `total=2148 killed=1328 survived=798 no_tests=22 suspicious=0 timeout=0 segfault=0`.
  - `uv run poe check`: passed the earlier quality and coverage gates, then failed as intended at `mutation-backtest` with the same mutation stats and `Sequence aborted after failed subtask 'mutation-backtest'`.
- Final disposition:
  - Accepted for this reproduction slice. The check lane now fails on the newly introduced backtest mutation gate; survivor remediation and any baseline policy are separate follow-up work.
