# Active Plan

- Date: `2026-04-16`
- Task: `Rollback conservative limit-semantics code changes while preserving investigation and design docs`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - revert the uncommitted runtime and test changes made for the conservative limit-semantics slice
  - preserve all related design, investigation, and planning documents for future follow-up
  - restore code and tests to the pre-change `HEAD` state without deleting documentation artifacts
- Governing docs:
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/index.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
- Why these are governing:
  - they define the repo workflow, runtime-sensitive verification rules, and current backtest/research authority; the rollback intentionally preserves newer docs while restoring code behavior
- In-repo scope:
  - restore modified research runtime and related tests to `HEAD`
  - add a rollback plan artifact documenting the intentional doc/code divergence
- Out-of-repo scope:
  - deleting design/investigation docs
  - reworking architecture documents
  - new semantics implementation work
- Tier A progression requested: `no`
- Approval record, if required:
  - not required; rollback scope is limited to `research` and tests
- Verification commands:
  - `uv run pytest tests/unit/research/adapters/test_execution_model.py tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py -q`
  - `uv run pytest tests/integration/research -q`
  - `uv run poe verify-runtime`
- Success criteria:
  - the six modified code/test files match `HEAD`
  - docs created during the investigation remain in the working tree
  - runtime-sensitive verification passes from the post-rollback state
  - the rollback plan records that docs are intentionally retained for later work
- Out of scope:
  - reconciling docs with the restored code
  - removing historical plan artifacts

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - done means the runtime and tests are restored to `HEAD`, documentation remains present, and runtime-sensitive verification passes with no unintended code differences outside the rollback scope
- Acceptance artifact location:
  - `docs/plans/2026-04-16-limit-semantics-code-rollback-plan.md`
- How the generator and evaluator agreed on done before execution:
  - this plan fixes the rollback scope, preserves docs by explicit exception, and names the verification commands before edits begin
- Checks the evaluator will use:
  - `git diff --stat`
  - targeted test diff review
  - `uv run poe verify-runtime`
- Auto-fail conditions:
  - any design/investigation doc is deleted
  - any non-target code path is changed
  - runtime verification is skipped or failing

## Generator Work Log

- Planned slice order:
  - add rollback plan
  - restore runtime files to `HEAD`
  - restore affected tests to `HEAD`
  - run runtime-sensitive verification
- Notes:
  - intentional temporary doc/code divergence is accepted because the user explicitly requested code rollback while preserving docs
- Blockers or scope changes:
  - none yet

## Evaluator Review

- Findings:
  - the six rollback-targeted code/test files now match `HEAD`; `git diff --stat` is empty for that target set
  - documentation artifacts from the conservative-semantics investigation remain present and are now the only working-tree changes
  - the repository is intentionally left in a temporary doc/code divergence state because the user requested rollback of code only
- Verification evidence:
  - `git diff --stat -- src/quantcraft/research/adapters/execution_model.py src/quantcraft/research/application/backtest.py tests/integration/research/support_backtest_runner.py tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py tests/unit/research/adapters/test_execution_model.py` -> no output
  - `uv run pytest tests/unit/research/adapters/test_execution_model.py tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py -q` -> `20 passed in 0.11s`
  - `uv run pytest tests/integration/research -q` -> `24 passed in 0.87s`
  - `uv run poe verify-runtime` -> lint, mypy, full pytest, coverage, build, repo-check, notebook validation, and perf check all passed
  - `git status --short` -> only docs and plan artifacts remain modified/untracked
- Final disposition:
  - `accepted`
