# Ruff RUF100 Evaluation

- Date: 2026-05-26
- Task: Evaluate adding `RUF100` to the Ruff hard-gate rule set.
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Add `RUF100` to catch unused `noqa` directives and report whether the
  current repository violates it.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing: This is repository lint-gate configuration work.
- In-repo scope:
  - `pyproject.toml`
  - this active plan
  - mechanical unused-`noqa` cleanup if detected
- Out-of-repo scope: none
- Tier A progression requested: `no`
- Approval record, if required: not required.
- Verification commands:
  - `uv run ruff check . --statistics`
  - `uv run ruff check .`
- Success criteria:
  - `RUF100` is evaluated against the current repository.
  - Any unused `noqa` findings are fixed or reported.
- Out of scope:
  - Adding other Ruff rule families
  - Broad lint cleanup unrelated to `RUF100`

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Confirm fresh Ruff output after
  adding `RUF100` and classify whether it is ready for hard-gate use.
- Acceptance artifact location: this plan and final user report
- How the generator and evaluator agreed on done before execution: The user
  requested applying the second recommended rule.
- Checks the evaluator will use:
  - `uv run ruff check . --statistics`
  - `uv run ruff check .`
  - `git diff -- pyproject.toml docs/plans/2026-05-26-ruff-ruf100-evaluation.md`
- Auto-fail conditions:
  - `RUF100` is not actually included in the evaluated config.
  - Fresh Ruff output is not collected.

## Generator Work Log

- Planned slice order:
  - Add this active plan.
  - Update Ruff config with `RUF100`.
  - Run Ruff and inspect violations.
  - Record evaluation.
- Notes:
  - Adding `RUF100` exposed two unused `# noqa: E402` directives.
  - Ruff safely removed both unused directives.
- Blockers or scope changes: none

## Evaluator Review

- Findings:
  - `RUF100` is suitable as a hard-gate addition for the current repository.
  - The only findings were mechanical cleanup and are fixed.
- Verification evidence:
  - `uv run ruff check . --statistics`: passed with no findings.
  - `uv run ruff format --check .`: passed, 199 files already formatted.
  - `uv run mypy src`: passed with no issues in 61 source files.
- Final disposition: complete; recommend keeping `RUF100` enabled.
