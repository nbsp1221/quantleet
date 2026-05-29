- Date: 2026-05-28
- Task: Add an experimental Deptry dependency gate
- Status: `active`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Add Deptry as a repository-local dependency declaration check, wire it
  into the existing Poe check surface, and resolve the package dependency
  findings without suppressing them.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `docs/PLANS.md`
- Why these are governing:
  - `AGENTS.md` defines the canonical repository check surface and planner
    workflow.
  - `README.md` documents contributor setup around `uv run poe check`.
  - `docs/PLANS.md` defines where active plan artifacts live.
- In-repo scope:
  - `pyproject.toml`
  - `uv.lock`
  - `AGENTS.md`
  - Poe contract tests and repo-check contract helpers
  - this plan artifact
- Out-of-repo scope: none
- Tier A progression requested: `no`
- Approval record, if required: not required; this changes repository quality
  tooling only and does not alter trading or execution behavior.
- Verification commands:
  - `uv run poe dependency-check`
  - `uv run poe check`
- Success criteria:
  - Deptry is a dev dependency managed by `uv`.
  - Deptry settings live in `pyproject.toml`.
  - A Poe task exposes the dependency declaration check using existing task
    naming style.
  - The default `check` sequence includes the new dependency gate.
  - The new gate passes after the dependency findings are resolved.
- Out of scope:
  - Suppressing findings with ignores.
  - Broadly relocating repository tooling beyond the files required to resolve
    the Deptry findings.
  - Changing runtime behavior.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: inspect the diff for scope
  control, then run the new targeted task and default check to prove the new
  gate is active and passes after the findings are resolved.
- Acceptance artifact location: this plan.
- How the generator and evaluator agreed on done before execution: this plan
  defines the only intended edits and expected failing verification.
- Checks the evaluator will use:
  - `uv run poe dependency-check`
  - `uv run poe check`
- Auto-fail conditions:
  - The gate is not reachable via Poe.
  - `uv run poe check` does not include the Deptry task.
  - Dependency findings are suppressed instead of structurally resolved.
  - Any source/test behavior is modified in this slice.

## Generator Work Log

- Planned slice order:
  - Add Deptry to the development dependency group.
  - Add `[tool.deptry]` configuration with first-party and module-name mapping
    needed to avoid known setup noise.
  - Add `dependency-check` Poe task and include it in `check`.
  - Update repository task contracts for the new required task.
  - Add NumPy as a direct runtime dependency because runtime code imports it
    directly.
  - Move notebook validation helpers out of package source and into
    repository-local scripts because `nbformat` and `nbclient` remain dev
    dependencies.
  - Run targeted and aggregate checks to confirm the gate passes.
- Notes:
  - Initial scan root is `src` because Deptry is being used here to validate
    installable package runtime dependencies. Repository scripts may use
    development dependencies by design and are covered by repo-check and
    notebook validation.
  - Notebooks are ignored for this first gate so dependency package checks focus
    on importable source.
  - Known first-party module is `quantleet`; `ta-lib` maps to import module
    `talib`.
- Blockers or scope changes:
  - The user requested fixing the known findings after the failing-gate
    experiment, so this plan now records both the failed experiment and the
    remediation evidence.

## Evaluator Review

- Findings:
  - No suppression-based workaround was used. NumPy is now a direct runtime
    dependency because package code imports `numpy` directly.
  - Notebook validation helpers were moved from package source to
    `scripts/notebook_tools.py`, keeping `nbformat` and `nbclient` as
    development dependencies.
  - `_repo_tools.py` is also repository-tooling shaped, but it does not import
    third-party development dependencies and is a broad existing contract for
    structure tests and scripts. Moving it is a separate follow-up, not required
    to resolve the current Deptry findings.
- Verification evidence:
  - `uv run poe dependency-check` failed with 10 Deptry findings:
    - `DEP004` for `nbformat` and `nbclient` imported from
      `src/quantleet/_notebook_tools.py` while declared as dev dependencies.
    - `DEP003` for `numpy` imported from indicator modules while available only
      as a transitive dependency.
  - `uv run poe check` passed `format-check`, `lint`, and `dead-code`, then
    aborted after the new `dependency-check` subtask reported the same 10
    findings.
  - `uv run pytest tests/structure/repo/test_coverage_harness.py
    tests/structure/repo/test_poe_task_contracts.py
    tests/structure/repo/test_repo_check_contracts.py -q` passed with 30 tests.
  - `uv run poe dependency-check` passed after remediation: Deptry scanned 60
    files and found no dependency issues.
  - `uv run ruff check .` passed.
  - `uv run pytest tests/structure/repo/test_coverage_harness.py
    tests/structure/repo/test_poe_task_contracts.py
    tests/structure/repo/test_repo_check_contracts.py
    tests/integration/commands/test_local_command_entrypoints.py -q` passed
    with 33 tests.
  - `uv run mypy src` passed with 60 source files.
  - `uv run python scripts/notebook_validate.py` passed and validated all five
    tracked notebooks.
  - `uv run poe check` passed: 814 tests passed, 4 skipped, 1 warning; Deptry,
    mypy, coverage, build, twine, repo-check, and notebook validation all
    completed successfully.
- Final disposition: complete.
