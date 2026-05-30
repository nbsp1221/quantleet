# Mutation Aggregate Gate

- Date: 2026-05-30
- Task: Change the default mutation gate from sequential lane checks to one aggregate `trading` plus `backtest` run.
- Status: `complete`
- Risk class: `Tier A`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Make `uv run poe mutation-gates` run mutmut once across both default mutation targets and enforce one aggregate 80% score threshold.
- Governing docs:
  - `AGENTS.md`
  - `docs/RELIABILITY.md`
  - `docs/references/testing.md`
  - `docs/plans/2026-05-30-mutation-score-gates.md`
- Why these are governing: The change modifies the default quality gate command surface and its documented mutation policy.
- In-repo scope: Update the mutation gate wrapper, structure tests, and quality-gate documentation.
- Out-of-repo scope: No CI workflow changes and no external services.
- Tier A progression requested: `yes`
- Approval record, if required:
  - Requestor: user
  - Human approver: user
  - Check marker: `uv run poe mutation-gates`
  - Granted scope: default mutation gate policy for `trading` and `backtest`
  - Expiration: this task slice
  - Audit reference: user request on 2026-05-30 to prefer the common aggregate mutation score gate before adding stricter per-folder policy
- Verification commands:
  - `uv run ruff format scripts/mutation_gate.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_coverage_harness.py`
  - `uv run ruff check scripts/mutation_gate.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_coverage_harness.py`
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py -q`
  - `uv run poe mutation-gates`
- Success criteria:
  - `mutation-gates` performs one mutmut run over both `src/quantleet/trading` and `src/quantleet/backtest`.
  - The default hard gate checks one aggregate score against the 80% threshold.
  - Targeted one-lane commands remain available for deeper investigation.
  - Documentation no longer describes the default gate as sequential per-lane enforcement.
- Out of scope:
  - Fixing surviving mutants.
  - Adding path-level mutation score thresholds.
  - Changing CI workflow files.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The default mutation gate must represent the common aggregate mutation-score policy while preserving targeted commands for local diagnosis.
- Acceptance artifact location: this plan and final chat report.
- How the generator and evaluator agreed on done before execution: The user challenged the per-folder 80% policy as premature and requested the general aggregate approach first.
- Checks the evaluator will use:
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py -q`
  - `uv run poe mutation-gates`
- Auto-fail conditions:
  - `mutation-gates` still runs `trading` and `backtest` as two separate mutmut runs.
  - The default gate enforces per-folder scores.
  - The aggregate gate uses a backtest-incompatible covered-lines pre-pass.

## Generator Work Log

- Planned slice order:
  1. Add a combined aggregate mutmut configuration for the default gate.
  2. Update tests and docs to describe one aggregate score threshold.
  3. Run targeted structure and mutation-gate checks.
- Notes:
  - `mutation-gates` maps the public `all` selector to an internal `aggregate` mutmut configuration.
  - The aggregate config mutates `src/quantleet/trading` and `src/quantleet/backtest` in one mutmut run.
  - The aggregate config uses `mutate_only_covered_lines=false` because the backtest lane previously required avoiding the covered-lines pre-pass.
  - Targeted `mutation-trading` and `mutation-backtest` commands remain available for investigation.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - Accepted: `mutation-gates` now runs one aggregate mutmut execution instead of sequential per-lane executions.
  - Accepted: the default hard gate enforces one aggregate 80% mutation score.
  - Accepted: the default gate currently fails because the aggregate score is below threshold, not because of tool errors.
  - Residual risk: aggregate scoring can hide path-level weakness if one area improves enough to compensate for another; this is intentionally left for later evidence-based hardening.
- Verification evidence:
  - `uv run ruff format scripts/mutation_gate.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_coverage_harness.py`: passed; one file reformatted.
  - `git diff --check`: passed.
  - `uv run ruff check scripts/mutation_gate.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_coverage_harness.py`: passed.
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py -q`: passed, `25 passed in 0.06s`.
  - `uv run poe mutation-gates`: failed as expected, `lane=aggregate total=2945 killed=2001 survived=922 no_tests=22 suspicious=0 timeout=0 segfault=0 score=67.95% threshold=80%`.
  - Post-run cleanup: generated `mutants/` artifacts removed and the default `[tool.mutmut]` block restored to `src/quantleet/trading`.
- Final disposition:
  - Complete. The default mutation gate now follows the common aggregate score policy and currently blocks at 67.95%.
