# Test Coverage Command Contract

- Date: 2026-05-17
- Task: Clarify and verify the repo-local `test` and `coverage` command
  contract.
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Keep `uv run poe test` as the plain test pass/fail lane, and keep
  `uv run poe coverage` as the explicit coverage.py lane that reruns tests,
  measures coverage, and enforces the hard coverage gate.
- Governing docs:
  - `AGENTS.md`
  - `docs/RELIABILITY.md`
  - `docs/references/testing.md`
  - `pyproject.toml`
- Why these are governing:
  - `AGENTS.md` defines the repo command surface and required verification
    workflow.
  - `docs/RELIABILITY.md` defines local verification and coverage guardrails.
  - `docs/references/testing.md` defines testing lane policy.
  - `pyproject.toml` owns Poe task definitions and coverage.py policy.
- In-repo scope:
  - `pyproject.toml`
  - `docs/RELIABILITY.md`
  - `docs/references/testing.md`
  - structure tests for the command contract
- Out-of-repo scope:
  - No CI workflow changes.
  - No dependency changes.
- Tier A progression requested: `no`
- Approval record, if required: not required.
- Verification commands:
  - `uv run pytest tests/structure/repo/test_coverage_harness.py -q`
  - `uv run poe test`
  - `uv run poe coverage`
  - `uv run poe repo-check`
- Success criteria:
  - `test` runs `pytest -q` without coverage collection.
  - `coverage` reruns pytest under coverage.py and then runs coverage.py report.
  - The coverage report remains governed by coverage.py's `fail_under = 90`.
  - Docs state that `coverage` is intentionally heavier than `test` because it
    reruns tests to collect and enforce coverage.
- Out of scope:
  - Removing `test` from `verify`.
  - Adding pytest-cov.
  - Adding custom coverage wrapper scripts.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm the command definitions match the intended contract.
  - Confirm the direct command-surface tests pass.
  - Confirm `test`, `coverage`, and repo-check execute successfully.
- Acceptance artifact location:
  - this plan
- How the generator and evaluator agreed on done before execution:
  - Done means the command names and behavior are clear to humans and enforced
    by structure tests.
- Checks the evaluator will use:
  - targeted structure tests
  - `uv run poe test`
  - `uv run poe coverage`
  - `uv run poe repo-check`
- Auto-fail conditions:
  - `test` collects coverage.
  - `coverage` only reports stale coverage data without rerunning tests.
  - Coverage threshold enforcement is moved back to custom code.

## Generator Work Log

- Planned slice order:
  - Make Poe task help text explicit.
  - Add docs explaining the `test` versus `coverage` split.
  - Tighten structure tests for the command contract.
  - Run targeted and command-level verification.
- Notes:
  - The command shape remains aligned with the OSS survey: a public
    `coverage` task is the clearest standalone coverage gate name.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocker findings. `test` remains a plain pytest pass/fail lane, and
    `coverage` reruns pytest under coverage.py before enforcing the report
    gate.
  - Command docs now explicitly describe why `coverage` is heavier than
    `test`.
  - Structure tests now enforce that the `test` Poe task does not include
    coverage collection.
- Verification evidence:
  - `uv run pytest tests/structure/repo/test_coverage_harness.py -q` passed:
    `5 passed in 0.01s`.
  - `uv run poe test` passed: `737 passed, 4 skipped in 14.33s`.
  - `uv run poe coverage` passed: `737 passed, 4 skipped in 46.45s`; coverage
    report total remained `91%`.
  - `uv run poe repo-check` passed: `repository checks passed`.
- Final disposition:
  - Accepted.
