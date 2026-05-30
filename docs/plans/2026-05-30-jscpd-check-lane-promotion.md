# jscpd Check Lane Promotion

- Date: 2026-05-30
- Task: Promote the jscpd duplicate-code gate into the default `uv run poe check` lane.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Make `duplicate-code` a formal default check gate now that the duplicate remediation slice has proven the configured threshold passes cleanly.
- Governing docs:
  - `AGENTS.md`
  - `docs/RELIABILITY.md`
  - `docs/PLANS.md`
  - `docs/SECURITY.md`
- Why these are governing:
  - They define the repository command surface, hard-gate expectations, active-plan workflow, and safety boundary.
- In-repo scope:
  - Poe check sequence in `pyproject.toml`.
  - Repo harness required task metadata in `src/quantleet/_repo_tools.py`.
  - Repo check documentation in `AGENTS.md` and `docs/RELIABILITY.md`.
- Out-of-repo scope:
  - No commits, no worktree split, no threshold changes, no external service setup.
- Tier A progression requested: `no`
- Approval record, if required:
  - Not required. This changes repository quality gates and docs; it does not alter trading/execution production behavior.
- Verification commands:
  - `uv run poe duplicate-code`
  - `uv run poe repo-check`
  - `uv run poe check`
- Success criteria:
  - `uv run poe check` invokes `duplicate-code`.
  - Repo docs list `duplicate-code` as part of the check surface.
  - Repo harness treats `duplicate-code` as a required Poe task.
  - Fresh checks pass.
- Out of scope:
  - Changing `.jscpd.json` thresholds.
  - Adding package-lock/npm project metadata.
  - Refactoring tests or production code.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Confirm the default check lane includes `duplicate-code`, the repo harness accepts the command surface, and fresh check output proves the gate is green.
- Acceptance artifact location: This plan.
- How the generator and evaluator agreed on done before execution:
  - The generator will only update check orchestration/docs and will not change thresholds or code behavior.
- Checks the evaluator will use:
  - `uv run poe duplicate-code`
  - `uv run poe repo-check`
  - `uv run poe check`
- Auto-fail conditions:
  - `duplicate-code` is omitted from the default `check` sequence.
  - `uv run poe check` does not run jscpd.
  - Any verification command fails.

## Generator Work Log

- Planned slice order:
  - Add `duplicate-code` to the default check sequence.
  - Add `duplicate-code` to the repo-required Poe task list.
  - Update repo/reliability docs.
  - Run fresh verification.
- Notes:
  - Added `duplicate-code` to the default `check` sequence after `dead-code` and before `dependency-check`.
  - Added `duplicate-code` to the repo harness required Poe task list.
  - Updated `AGENTS.md` and `docs/RELIABILITY.md` so the formal command surface documents the new hard gate.
  - Updated structure tests and minimal repo fixtures that encode the default check-lane contract.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings. The first full `uv run poe check` correctly invoked jscpd, then failed because structure tests still encoded the previous check sequence. The contract tests and minimal repo fixtures were updated, and the full check passed afterward.
- Verification evidence:
  - `uv run pytest -q tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py`: passed, 30 passed.
  - `uv run ruff check tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py`: passed.
  - `uv run poe duplicate-code`: passed, 183 Python files, 26,931 total lines, 0 clones, 0 duplicated lines, 0 duplicated tokens.
  - `uv run poe repo-check`: passed.
  - `uv run poe check`: passed and invoked `npx --yes jscpd@4.2.4 --config .jscpd.json --noTips`; coverage run reported 813 passed, 4 skipped, 1 pre-existing dependency warning, total coverage 92%; build, Twine, repo-check, and notebook validation passed.
- Final disposition:
  - Complete. `duplicate-code` is now part of the default local quality gate and the formal repo command contract.
