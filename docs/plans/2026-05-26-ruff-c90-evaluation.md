# Active Plan

- Date: 2026-05-26
- Task: Evaluate Ruff C90 as a hard lint gate
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Temporarily add `C90` to the Ruff lint gate without changing implementation code, then measure the current violation count and gate impact.
- Governing docs: `AGENTS.md`, `README.md`, `docs/PLANS.md`, `docs/plans/TEMPLATE.md`
- Why these are governing: They define the repository workflow contract, check surface, plan artifact location, and current Python contributor commands.
- In-repo scope: `pyproject.toml`, this plan artifact, and read-only lint/check evaluation.
- Out-of-repo scope: none.
- Tier A progression requested: `no`
- Approval record, if required: not required; this slice changes lint configuration only and does not modify runtime behavior.
- Verification commands:
  - `uv run ruff check src tests scripts --select C90 --statistics`
  - `uv run ruff check .`
  - `uv run poe check` if the targeted gate unexpectedly passes
- Success criteria: `C90` is evaluated without source/test implementation changes, and the evaluator records the violation count plus gate outcome.
- Out of scope: Refactoring or suppressing C90 violations.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Confirm the configuration diff used for evaluation was limited to adding `C90`, collect fresh Ruff output, and report whether the configured gate passes.
- Acceptance artifact location: this plan document.
- How the generator and evaluator agreed on done before execution: The user explicitly requested adding C90 to the gate and evaluating violations without fixing them.
- Checks the evaluator will use:
  - `git diff -- pyproject.toml`
  - `uv run ruff check src tests scripts --select C90 --statistics`
  - `uv run ruff check .`
- Auto-fail conditions: Any source/test code refactor, any C90 suppression added, or any unrelated tracked file edit beyond the plan and Ruff config.

## Generator Work Log

- Planned slice order:
  - Add the active plan.
  - Add `C90` to Ruff `select`.
  - Run targeted and configured Ruff checks.
- Notes:
  - This is intentionally a measurement pass.
  - Added `C90` to Ruff `select`.
  - Removed `C90` from Ruff `select` after evaluation at user request.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - `C90` failed the temporary Ruff gate with 10 violations.
  - All current violations are in `src/`; no `tests` or `scripts` violations were reported by the targeted scan.
  - The highest outlier is `collect_doc_issues` at complexity 60.
  - Three violations are in Tier A trading modules. They require explicit approval before behavior-affecting refactors are treated as approved.
- Verification evidence:
  - `uv run ruff config lint.mccabe.max-complexity`: default value is 10.
  - `uv run ruff check src tests scripts --select C90 --statistics`: `10 C901 complex-structure`; exit 1.
  - `uv run ruff check src tests scripts --select C90`: exit 1 with the 10 violation locations recorded in the final report.
  - `uv run ruff check .`: exit 1 with the same 10 `C901` violations while `C90` was selected.
- Final disposition:
  - Measurement complete. `C90` is not part of the active Ruff gate after the user requested removal.
