# Mutation Gate Simplification

- Date: 2026-05-30
- Task: Simplify the mutation hard gate to match common mutmut usage patterns.
- Status: `complete`
- Risk class: `Tier A`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Keep the intended aggregate mutation score hard gate while removing custom
  lane orchestration and temporary mutmut configuration rewriting.
- Governing docs:
  - `AGENTS.md`
  - `docs/RELIABILITY.md`
  - `docs/references/testing.md`
  - `docs/plans/2026-05-30-mutation-aggregate-gate.md`
- Why these are governing: The change modifies the default quality gate command
  surface and reliability documentation.
- In-repo scope: Update Poe task wiring, mutmut configuration, the mutation score
  checker script, structure tests, and local documentation.
- Out-of-repo scope: No CI workflow or external service changes.
- Tier A progression requested: `yes`
- Approval record, if required:
  - Requestor: user
  - Human approver: user
  - Check marker: `uv run poe mutation-gates`
  - Granted scope: default aggregate mutation hard gate for `trading` and
    `backtest`
  - Expiration: this task slice
  - Audit reference: user request on 2026-05-30 to remove anti-patterns found
    during external mutmut hard-gate case research
- Verification commands:
  - `uv run ruff format scripts/check_mutation_score.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_coverage_harness.py`
  - `uv run ruff check scripts/check_mutation_score.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_coverage_harness.py`
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py -q`
  - `uv run poe mutation-gates`
- Success criteria:
  - `mutation-gates` uses direct mutmut CLI steps followed by a thin score
    checker.
  - The mutmut target scope lives in the static `[tool.mutmut]` configuration.
  - The checker reads `mutants/mutmut-cicd-stats.json` and enforces the
    configured aggregate threshold.
  - The command surface no longer exposes custom lane orchestration as the
    default contract.
- Out of scope:
  - Fixing surviving mutants.
  - Adding per-path thresholds.
  - Adding changed-file mutation selection.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The implementation must preserve
  the aggregate mutation hard-gate intent while making the implementation look
  like the public mutmut examples: direct mutmut execution plus a small JSON
  score check.
- Acceptance artifact location: this plan and final chat report.
- How the generator and evaluator agreed on done before execution: The user
  asked to remove anti-patterns after case research showed that custom runners
  are only justified for special monorepo, changed-only, or retry workflows.
- Checks the evaluator will use:
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py -q`
  - `uv run poe mutation-gates`
- Auto-fail conditions:
  - The score checker rewrites `pyproject.toml`.
  - The default gate invokes a custom mutmut runner instead of direct mutmut CLI
    steps.
  - The default gate no longer covers both `trading` and `backtest`.

## Generator Work Log

- Planned slice order:
  1. Replace the mutation wrapper with a thin stats checker.
  2. Move aggregate mutmut scope into static pyproject configuration.
  3. Simplify Poe tasks and documentation to the aggregate gate contract.
  4. Run structure checks and the mutation gate to capture current failure
     evidence.
- Notes:
  - Replaced the custom mutation runner with `scripts/check_mutation_score.py`,
    which only reads exported mutmut CI stats and enforces
    `[tool.mutation_score].fail_under`.
  - Moved the aggregate `trading` plus `backtest` scope into the static
    `[tool.mutmut]` block.
  - Changed `mutation-gates` to direct mutmut CLI steps followed by the score
    checker.
  - Removed the current command-surface contract for `mutation-trading` and
    `mutation-backtest`; historical plan files still describe the previous
    experiments.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - Accepted: `mutation-gates` now uses direct mutmut CLI execution and a thin
    JSON score checker, matching the dominant public examples found during
    research.
  - Accepted: the default mutmut scope is static and covers both
    `src/quantleet/trading` and `src/quantleet/backtest`.
  - Accepted: the gate still fails for the intended reason, the current
    aggregate mutation score deficit.
  - Residual risk: removing targeted lane tasks means one-folder diagnostics now
    require a temporary local mutmut config change or a future separately
    justified profile mechanism.
- Verification evidence:
  - `uv run ruff format scripts/check_mutation_score.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_coverage_harness.py`: passed, 3 files left unchanged.
  - `uv run ruff check scripts/check_mutation_score.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_coverage_harness.py`: passed.
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py -q`: passed, `23 passed in 0.05s`.
  - `uv run poe mutation-gates`: failed as intended after successful mutmut run,
    results, and CI stats export; checker reported `total=2945 killed=2001
    survived=922 no_tests=22 suspicious=0 timeout=0 segfault=0 score=67.95%
    threshold=80%`.
  - `uv run python scripts/check_mutation_score.py`: failed as intended on the
    exported stats with `score=67.95% threshold=80%`.
  - `git diff --check`: passed.
- Final disposition:
  - Complete. The implementation keeps the aggregate hard-gate intent while
    removing the custom runner/config-rewrite anti-patterns from the current
    command surface.
