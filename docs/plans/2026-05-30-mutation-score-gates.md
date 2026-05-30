# Mutation Score Gates

- Date: 2026-05-30
- Task: Promote trading and backtest mutation testing into the default check lane with an 80% score threshold.
- Status: `complete`
- Risk class: `Tier A`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Replace advisory mutation output with deterministic mutation score gates for `trading` and `backtest`, and include them in `uv run poe check`.
- Governing docs:
  - `AGENTS.md`
  - `docs/RELIABILITY.md`
  - `docs/design-docs/agentic-quality-gates.md`
  - `docs/plans/2026-05-20-mutation-trading-command-plan.md`
  - `docs/plans/2026-05-30-backtest-mutation-gate-reproduction.md`
- Why these are governing: The work changes the repo-local quality gate surface and promotes mutation testing from an audit lane into a default check gate.
- In-repo scope: Update the mutation gate wrapper, Poe task wiring, structure tests, and reliability docs.
- Out-of-repo scope: No CI workflow edits and no external services.
- Tier A progression requested: `yes`
- Approval record, if required:
  - Requestor: user
  - Human approver: user
  - Check marker: `uv run poe mutation-gates`
  - Granted scope: mutation gate command wiring for `trading` and `backtest`
  - Expiration: this task slice
  - Audit reference: user request on 2026-05-30 to set up 80% mutation gates for both lanes
- Verification commands:
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py -q`
  - `uv run poe mutation-trading`
  - `uv run poe mutation-backtest`
  - `uv run poe mutation-gates`
- Success criteria:
  - `mutation-trading` and `mutation-backtest` both evaluate mutation score against an 80% threshold.
  - `check` includes a mutation gate that covers both lanes.
  - Lanes run sequentially to avoid mutmut workspace collisions.
  - `trading` passes the 80% threshold with current evidence.
  - `backtest` fails the 80% threshold with current evidence.
  - The default `[tool.mutmut]` configuration is restored after lane-specific runs.
- Out of scope:
  - Fixing surviving mutants.
  - Introducing changed-file mutation selection.
  - Adding a CI workflow.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The command surface must enforce an 80% threshold for both mutation lanes and the default check lane must fail only because the current backtest score is below threshold.
- Acceptance artifact location: this plan and final chat report.
- How the generator and evaluator agreed on done before execution: The user requested 80% gates for both `trading` and `backtest` and delegated sequencing.
- Checks the evaluator will use:
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py -q`
  - `uv run poe mutation-trading`
  - `uv run poe mutation-backtest`
  - `uv run poe mutation-gates`
- Auto-fail conditions:
  - `trading` and `backtest` run concurrently against the same mutmut workspace.
  - The gate still requires zero survivors instead of the 80% threshold.
  - `pyproject.toml` is left with a lane-specific mutmut configuration after execution.
  - Generated `mutants/` artifacts are committed.

## Generator Work Log

- Planned slice order:
  1. Generalize the mutation wrapper to lane configs and score thresholds.
  2. Wire `mutation-trading`, `mutation-backtest`, and `mutation-gates` Poe tasks.
  3. Update structure tests and reliability docs.
  4. Run targeted checks and mutation evidence commands.
- Notes:
  - mutmut uses one local config/workspace, so the combined gate runs lanes sequentially.
  - `scripts/mutation_gate.py` now evaluates mutation score against an explicit threshold instead of treating every survivor as an absolute failure.
  - `uv run poe check` now includes `mutation-gates` after `coverage-gates`.
  - `mutation-gates` runs the `trading` and `backtest` lanes sequentially and returns failure if either lane misses the threshold.
  - The default `[tool.mutmut]` block remains scoped to `trading` after lane-specific execution.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - Accepted: the default check surface now includes an 80% mutation score hard gate for both `trading` and `backtest`.
  - Accepted: the combined gate runs sequentially, which avoids concurrent writes to mutmut's repo-local configuration and `mutants/` workspace.
  - Accepted: `survived` and `no_tests` mutants lower the score instead of failing independently; suspicious, timeout, and segfault mutants remain hard failures.
  - Current expected failure: `backtest` is below the 80% score threshold, so `mutation-backtest`, `mutation-gates`, and therefore `check` fail until backtest mutation coverage improves.
- Verification evidence:
  - `uv run ruff format scripts/mutation_gate.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_coverage_harness.py`: passed.
  - `git diff --check`: passed.
  - `uv run ruff check scripts/mutation_gate.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_coverage_harness.py`: passed.
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py -q`: passed, `24 passed in 0.06s`.
  - `uv run poe mutation-trading`: passed, `total=765 killed=671 survived=94 no_tests=0 suspicious=0 timeout=0 segfault=0 score=87.71% threshold=80%`.
  - `uv run poe mutation-backtest`: failed as expected, `total=2148 killed=1328 survived=798 no_tests=22 suspicious=0 timeout=0 segfault=0 score=61.82% threshold=80%`.
  - `uv run poe mutation-gates`: failed as expected after `trading` passed and `backtest` failed at `61.82%`.
- Final disposition:
  - Complete. The gate is installed and currently blocks on the known backtest mutation score deficit.
