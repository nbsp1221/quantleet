# Verify Coverage Gates Optimization Plan

- Date: 2026-05-17
- Task: Reduce duplicate pytest executions in the default `verify` lane.
- Status: `active`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Keep the same local verification guarantees while changing `verify` so
  pytest runs once for coverage-backed correctness, full-project coverage, and
  changed-line coverage.
- Governing docs:
  - `AGENTS.md`
  - `docs/RELIABILITY.md`
  - `docs/references/testing.md`
  - `docs/plans/2026-05-17-diff-coverage-gate-plan.md`
- Why these are governing:
  - `AGENTS.md` requires repo-local command surfaces and planner/generator/
    evaluator evidence.
  - `docs/RELIABILITY.md` defines the default verification and coverage
    guardrails.
  - `docs/references/testing.md` defines test command lane semantics.
  - The diff coverage plan defines the changed-lines gate contract.
- In-repo scope:
  - Add a public Poe task named `coverage-gates`.
  - Make `coverage-gates` run pytest once under coverage.py, then generate both
    the full-project coverage report and the XML report for `diff-cover`.
  - Update `verify` to call `coverage-gates` instead of separate `test`,
    `coverage`, and `coverage-diff` lanes.
  - Keep standalone `test`, `coverage`, and `coverage-diff` commands available.
  - Update repo-check task surface, structure tests, and docs.
  - Measure `verify` before and after the change.
- Out-of-repo scope:
  - No GitHub Actions workflow change.
  - No switch to pytest-cov in this slice.
  - No custom Python wrapper script.
- Tier A progression requested: `no`
- Approval record, if required: not required.
- Verification commands:
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py -q`
  - `uv run poe coverage-gates`
  - `uv run poe repo-check`
  - `TIMEFMT='real %E user %U sys %S'; time uv run poe verify`
- Success criteria:
  - `coverage-gates` exists and is documented.
  - `coverage-gates` runs `coverage run -m pytest -q` exactly once.
  - `coverage-gates` runs `coverage report -m` to enforce the existing `90%`
    full-project combined line/branch gate.
  - `coverage-gates` runs `coverage xml -o coverage.xml --fail-under=0`.
  - `coverage-gates` runs `diff-cover coverage.xml --compare-branch HEAD
    --include-untracked --fail-under 80`.
  - `verify` uses `coverage-gates` and no longer runs separate `test`,
    `coverage`, and `coverage-diff` tasks.
  - Standalone `test`, `coverage`, and `coverage-diff` commands remain
    available.
  - Final `verify` passes.
  - Final measured `verify` wall time is lower than the pre-change baseline.
- Out of scope:
  - Removing standalone commands.
  - Changing coverage thresholds.
  - Changing CI.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm command contracts are updated and locked by tests.
  - Confirm docs describe the integrated gate without implying the standalone
    commands were removed.
  - Confirm `verify` executes pytest only through `coverage-gates`.
  - Confirm pre/post timing evidence exists.
- Acceptance artifact location:
  - this plan
- How the generator and evaluator agreed on done before execution:
  - Done means the same coverage guarantees are retained, but the default
    verification path removes duplicate pytest runs and demonstrates a measured
    speedup.
- Checks the evaluator will use:
  - targeted structure tests
  - `coverage-gates`
  - `repo-check`
  - timed `verify`
- Auto-fail conditions:
  - The `90%` full-project coverage gate is weakened or skipped.
  - The `80%` changed-lines coverage gate is weakened or skipped.
  - `verify` still runs the default pytest suite more than once.
  - A custom wrapper is introduced when Poe plus existing tools are sufficient.

## Generator Work Log

- Planned slice order:
  - Record pre-change `verify` timing.
  - Add `coverage-gates` Poe task.
  - Change `verify` to use `coverage-gates`.
  - Update repo-check task surface and structure tests.
  - Update docs and the prior diff coverage plan language.
  - Run targeted tests, command checks, and timed `verify`.
- Notes:
  - Pre-change baseline: `TIMEFMT='real %E user %U sys %S'; time uv run poe verify`
    returned `real 125.57s user 121.94s sys 1.95s`.
  - Implemented `coverage-gates` as a Poe sequence using coverage.py and
    diff-cover directly.
  - Updated `verify` to run `coverage-gates` instead of separate `test`,
    `coverage`, and `coverage-diff` tasks.
  - Kept standalone `test`, `coverage`, and `coverage-diff` commands available.
  - Updated command-surface docs, repo-check task requirements, and structure
    tests.
- Blockers or scope changes:
  - None at planning time.

## Evaluator Review

- Findings:
  - No blocker or important issues found.
  - The implementation keeps the existing full-project `90%` coverage gate and
    changed-lines `80%` coverage gate.
  - `verify` no longer runs the standalone `test`, `coverage`, and
    `coverage-diff` tasks, so the default pytest suite is executed once through
    `coverage-gates`.
  - The prior diff coverage plan was updated to avoid claiming that `verify`
    directly calls `coverage-diff`; the default verification path now includes
    the changed-lines gate through `coverage-gates`.
- Verification evidence:
  - Pre-change timed baseline:
    `TIMEFMT='real %E user %U sys %S'; time uv run poe verify`
    - result: `real 125.57s user 121.94s sys 1.95s`
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py -q`
    - result: `22 passed in 0.09s`
  - `uv run poe repo-check`
    - result: `repository checks passed`
  - `uv run poe coverage-gates`
    - result: `739 passed, 4 skipped, 1 warning in 44.33s`
    - result: full-project coverage `TOTAL ... 91%`
    - result: diff-cover reported `No lines with coverage information in this diff.`
  - Post-change timed verification:
    `TIMEFMT='real %E user %U sys %S'; time uv run poe verify`
    - result: `real 64.64s user 58.76s sys 1.24s`
    - result: lint, typecheck, coverage-gates, build, repo-check, and
      notebook validation passed
  - Measured improvement:
    - absolute wall-time reduction: `60.93s`
    - relative wall-time reduction: approximately `48.5%`
- Final disposition:
  - Accepted. The default local verification lane now preserves the same
    coverage gates while reducing duplicate pytest execution.
