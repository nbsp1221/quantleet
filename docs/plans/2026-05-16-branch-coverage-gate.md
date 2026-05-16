# Branch Coverage Gate

- Date: 2026-05-16
- Task: Replace custom coverage thresholds and legacy coverage wrapper with
  coverage.py's native combined line/branch coverage hard gate.
- Status: `completed`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Use coverage.py's native branch measurement and `fail_under = 90`
  report gate for one standard combined line/branch coverage threshold, routed
  through `uv run poe coverage` without a bespoke `coverage_check.py` wrapper.
- Governing docs:
  - `AGENTS.md`
  - `docs/PLANS.md`
  - `docs/RELIABILITY.md`
  - `docs/references/test-quality-evaluation-report-2026-05-16.md`
- Why these are governing:
  - `AGENTS.md` requires a planner/generator/evaluator loop.
  - `docs/PLANS.md` defines active plan location.
  - `docs/RELIABILITY.md` defines coverage guardrails.
  - The test-quality report records the measured combined line/branch baseline
    of about `91%`, which supports a standard `90%` hard gate.
- In-repo scope:
  - `pyproject.toml`
  - `AGENTS.md`
  - `docs/RELIABILITY.md`
  - coverage-related tests
  - coverage harness unit/structure tests
- Out-of-repo scope:
  - No CI workflow changes.
  - No custom function/path coverage tooling.
- Tier A progression requested: `no`
- Approval record, if required: not required.
- Verification commands:
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py tests/integration/commands/test_local_command_entrypoints.py -q`
  - `uv run poe coverage`
  - `uv run poe repo-check`
  - `uv run poe verify`
- Success criteria:
  - `scripts/coverage_check.py` is removed.
  - `uv run poe coverage` runs coverage.py commands directly without custom
    wrapper scripts or unnecessary private top-level Poe tasks.
  - Coverage collection uses coverage.py's standard `[tool.coverage.run]`
    `branch = true` configuration.
  - Coverage failure uses coverage.py's standard `[tool.coverage.report]`
    `fail_under = 90` configuration.
  - Custom JSON threshold parsing is removed.
  - Separate line, branch, and `trading/domain` thresholds are removed.
  - Tests verify the standard coverage configuration and Poe coverage command
    sequence.
  - Reliability docs state the new combined line/branch guardrail.
- Out of scope:
  - Adding separate line or branch thresholds.
  - Adding path-specific thresholds.
  - Adding mutation or flaky-test gates.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm branch coverage is measured by coverage.py native config.
  - Confirm `fail_under = 90` is the only coverage hard threshold.
  - Confirm the coverage gate passes on the current suite.
  - Confirm no active command/docs/tests still point at `coverage_check.py`.
- Acceptance artifact location:
  - this plan
- How the generator and evaluator agreed on done before execution:
  - Done means `uv run poe coverage` enforces coverage.py's native combined
    line/branch coverage threshold without custom JSON parsing or a bespoke
    coverage wrapper script.
- Checks the evaluator will use:
  - targeted coverage harness tests
  - `uv run poe coverage`
  - `uv run poe repo-check`
  - `uv run poe verify`
- Auto-fail conditions:
  - Coverage threshold decisions are made by custom JSON parsing.
  - Active command surfaces still require `scripts/coverage_check.py`.
  - Separate line/branch/domain thresholds remain.
  - The coverage gate is advisory only.

## Generator Work Log

- Planned slice order:
  - Move coverage branch/fail-under policy into `pyproject.toml`.
  - Remove `coverage_check.py` and route Poe coverage directly to coverage.py.
  - Update tests and docs.
  - Run targeted verification and full coverage gate.
- Notes:
  - Decision evidence from official docs:
    - coverage.py supports `branch = true` in coverage configuration and
      `fail_under` in report configuration.
    - pytest-cov documents `--cov-branch` and `--cov-fail-under`, and states
      that further coverage control should use coverage configuration.
    - pytest-cov's `--cov-fail-under` is a total coverage threshold, matching
      coverage.py's standard combined report semantics when branch measurement
      is enabled.
    - Poe supports underscore-prefixed private tasks for reusable internal
      references, but a one-off two-step coverage sequence is simpler as inline
      sequence commands under the public `coverage` task.
  - The current user request supersedes the prior compatibility decision to
    keep `scripts/coverage_check.py`; active command surfaces now prefer
    `uv run poe coverage`.
  - Standard policy now lives in `pyproject.toml`:
    - `[tool.coverage.run].branch = true`
    - `[tool.coverage.run].source = ["quantleet"]`
    - `[tool.coverage.report].fail_under = 90`
    - `[tool.coverage.report].show_missing = true`
  - Follow-up simplification:
    - Removed top-level `_coverage-run` and `_coverage-report` Poe tasks.
    - Kept one public `coverage` task with inline coverage.py command sequence.
- Blockers or scope changes:
  - The earlier separate branch-threshold implementation is being superseded
    because the user requested standard tool semantics and minimal custom
    logic.

## Evaluator Review

- Findings:
  - No blocker findings. The custom coverage wrapper and its wrapper-specific
    tests are removed, and the active command surface now routes coverage
    through coverage.py's native run/report commands.
  - No blocker findings on Poe task shape. Poe underscore private tasks are
    officially supported, but the final task shape avoids them because the
    coverage subtasks are not reused anywhere else.
  - `pyproject.toml` is the single coverage policy location for the default
    gate: branch measurement is enabled and `fail_under = 90` is the only hard
    coverage threshold.
  - No active command/docs/tests outside this completed plan point at
    `coverage_check.py`.
- Verification evidence:
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py tests/integration/commands/test_local_command_entrypoints.py -q`
    passed: `22 passed in 0.09s`.
  - `uv run poe coverage` passed: `736 passed, 4 skipped in 44.52s`; coverage
    report total is `91%`, satisfying the `90%` coverage.py hard gate.
  - `uv run poe repo-check` passed: `repository checks passed`.
  - `uv run poe verify` passed: ruff, mypy, pytest, coverage, build,
    repo-check, and notebook validation all completed successfully.
  - Follow-up inline Poe sequence verification passed:
    `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py -q`
    passed with `19 passed in 0.10s`.
  - Follow-up `uv run poe coverage` passed with inline sequence commands:
    `736 passed, 4 skipped in 44.54s`; coverage report total remained `91%`.
  - Follow-up `uv run poe repo-check` passed: `repository checks passed`.
- Final disposition:
  - Accepted.
