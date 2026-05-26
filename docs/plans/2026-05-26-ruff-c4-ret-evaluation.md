# Ruff C4 RET Evaluation

- Date: 2026-05-26
- Task: Evaluate adding `C4` and `RET` to the Ruff hard-gate rule set.
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Add the low-noise Ruff rule families `C4` and `RET` to the existing
  baseline and report whether the current repository violates them.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing: This is repository quality-gate configuration
  evaluation, so the repo workflow and check-surface docs govern the slice.
- In-repo scope:
  - `pyproject.toml`
  - this active plan
  - any directly required low-risk lint fixes if violations are found
- Out-of-repo scope: none
- Tier A progression requested: `no`
- Approval record, if required: not required; no Tier A behavior changes are
  planned.
- Verification commands:
  - `uv run ruff check . --statistics`
  - `uv run ruff check .`
- Success criteria:
  - `C4` and `RET` are evaluated against the current repository.
  - Any violations are reported or fixed if purely mechanical.
  - Final recommendation is recorded.
- Out of scope:
  - Adding other Ruff rule families
  - Broad refactors unrelated to `C4` or `RET`

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Confirm fresh Ruff output after
  adding `C4` and `RET`, and classify whether the rule families are ready for
  hard-gate use.
- Acceptance artifact location: this plan and final user report
- How the generator and evaluator agreed on done before execution: The user
  requested applying item 1 and evaluating whether violations exist.
- Checks the evaluator will use:
  - `uv run ruff check . --statistics`
  - `uv run ruff check .`
  - `git diff -- pyproject.toml docs/plans/2026-05-26-ruff-c4-ret-evaluation.md`
- Auto-fail conditions:
  - `C4` or `RET` are not actually included in the evaluated config.
  - Fresh Ruff output is not collected.

## Generator Work Log

- Planned slice order:
  - Add this active plan.
  - Update Ruff `select` with `C4` and `RET`.
  - Run Ruff and inspect violations.
  - Record evaluation.
- Notes:
  - Adding `C4` and `RET` exposed one `C420` finding.
  - Ruff safely fixed the finding by replacing an unnecessary dict
    comprehension with `dict.fromkeys`.
  - No `RET` findings were reported.
- Blockers or scope changes: none

## Evaluator Review

- Findings:
  - `C4` and `RET` are suitable hard-gate additions for the current repository.
  - The only violation was mechanical and is fixed.
- Verification evidence:
  - `uv run ruff check . --statistics`: passed with no findings.
  - `uv run ruff format --check .`: passed, 199 files already formatted.
  - `uv run mypy src`: passed with no issues in 61 source files.
- Final disposition: complete; recommend keeping `C4` and `RET` enabled.
