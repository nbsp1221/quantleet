# Ruff PT DTZ Evaluation

- Date: 2026-05-26
- Task: Add `PT` and `DTZ` to Ruff configuration and report violations without fixing them.
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Configure Ruff to include `PT` and `DTZ`, then collect fresh violation
  evidence without applying fixes.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing: This is lint-gate configuration evaluation.
- In-repo scope:
  - `pyproject.toml`
  - this active plan
- Out-of-repo scope: none
- Tier A progression requested: `no`
- Approval record, if required: not required.
- Verification commands:
  - `uv run ruff check . --statistics`
  - `uv run ruff check .`
- Success criteria:
  - `PT` and `DTZ` are included in the Ruff config.
  - Fresh violation output is collected without modifying violation sites.
  - Findings are summarized by rule family and likely remediation class.
- Out of scope:
  - Fixing `PT` or `DTZ` findings
  - Adding other rule families

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Confirm config inclusion and
  report fresh Ruff failures without applying fixes.
- Acceptance artifact location: this plan and final user report
- How the generator and evaluator agreed on done before execution: The user
  explicitly requested applying the config but not fixing violations.
- Checks the evaluator will use:
  - `git diff -- pyproject.toml docs/plans/2026-05-26-ruff-pt-dtz-evaluation.md`
  - `uv run ruff check . --statistics`
  - `uv run ruff check .`
- Auto-fail conditions:
  - `PT` or `DTZ` are absent from config.
  - Any `PT` or `DTZ` violation site is modified in this slice.

## Generator Work Log

- Planned slice order:
  - Add this active plan.
  - Update Ruff config with `PT` and `DTZ`.
  - Run Ruff without `--fix`.
  - Summarize failures.
- Notes:
  - `PT` and `DTZ` were added to `pyproject.toml`.
  - Fresh Ruff output initially reported 14 findings, all under `tests/`.
  - The 14 findings were fixed after user approval to continue remediation.
  - The naive-datetime rejection test keeps an intentional `# noqa: DTZ001`
    because adding `tzinfo` would invalidate the test purpose.
- Blockers or scope changes: none

## Evaluator Review

- Findings:
  - `src/` has no `PT` or `DTZ` findings.
  - `notebooks/` has no `PT` or `DTZ` findings.
  - `tests/` initially had 14 findings:
    - 10 `PT007` pytest parametrization value-shape findings.
    - 1 `PT006` pytest parametrization name-shape finding.
    - 1 `PT012` multi-statement `pytest.raises` block.
    - 1 `PT018` composite assertion.
    - 1 `DTZ001` naive `datetime(...)` construction.
  - No human approval was required beyond the user's explicit instruction to
    proceed; all fixes were test-style or explicit-test-intent preservation.
- Verification evidence:
  - Initial `uv run ruff check . --statistics` failed with 14 findings.
  - After remediation, `uv run ruff check . --statistics` passed with no
    findings.
  - `uv run mypy src` passed with no issues in 61 source files.
  - Targeted test pass over affected test files: 184 passed, 1 warning.
  - `uv run poe check` passed, including format, Ruff, mypy, coverage gates,
    build, Twine check, repo check, and notebook validation.
- Final disposition: complete; recommend keeping `PT` and `DTZ` enabled.
