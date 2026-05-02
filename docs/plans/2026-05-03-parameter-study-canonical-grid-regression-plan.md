# Parameter Study Canonical Grid Regression Plan

- Date: `2026-05-03`
- Task: Promote the validated ParameterStudy external-comparison experiment into a first-party canonical regression test.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `User`
- Owner: `Codex`

## Planner Contract

- Goal: Add a deterministic integration regression that runs `ParameterStudy(...).grid_search(...)` over the checked-in BTC CSV fixture and pins the validated Quantcraft best-row output.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `docs/RELIABILITY.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/parameter-exploration-test-scenarios.md`
  - `docs/plans/2026-05-02-parameter-study-external-comparison-experiment-plan.md`
- Why these are governing: They define the repo test lanes, runtime-sensitive research verification requirements, parameter exploration product contract, expected test placement, and the completed comparison evidence this regression is promoting.
- In-repo scope:
  - Add one integration test file under `tests/integration/research/`.
  - Reuse the existing checked-in BTC CSV fixture and public `ParameterStudy` workflow.
  - Pin only stable workflow outputs: counts, best parameters, selected metrics, selected-run report linkage, and strict JSON-safe records.
- Out-of-repo scope: None.
- Tier A progression requested: `no`
- Approval record, if required: Not required; this is research-path test coverage only and does not modify `trading` or `execution`.
- Verification commands:
  - `uv run pytest tests/integration/research/test_parameter_study_canonical_grid_contract.py -q`
  - `uv run pytest tests/integration/research/test_parameter_study_grid_search.py tests/integration/research/test_parameter_study_canonical_grid_contract.py -q`
  - `uv run poe verify-runtime`
- Success criteria:
  - The new test uses `ParameterStudy` and `BacktestEngine.run(bars=...)`, not a duplicate execution loop.
  - The test uses `tests/fixtures/backtest/binance_usdm_btcusdtusdt_1h_2025.csv` via repo support helpers.
  - The test pins validated Quantcraft best-row output for the experiment strategies.
  - The test avoids third-party comparison dependencies.
  - Fresh focused and runtime verification pass.
- Out of scope:
  - Re-running third-party libraries in CI.
  - Adding optimizer semantics, parallelism, persistence, heatmaps, or broad strategy profitability claims.

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice: Review the diff against the governing docs and confirm the regression is first-party, deterministic, cheap enough for integration, and scoped to validated workflow outputs.
- Acceptance artifact location: This plan's Evaluator Review section plus final user report.
- How the generator and evaluator agreed on done before execution: The planner contract above defines the exact test purpose, scope, and verification commands before code edits.
- Checks the evaluator will use:
  - Inspect the new test for external dependency usage or duplicated engine semantics.
  - Confirm expected values match the completed comparison plan's Quantcraft output.
  - Run focused tests and runtime verification.
- Auto-fail conditions:
  - Adding `backtesting.py`, `backtrader`, `vectorbt`, or optimizer dependencies to default tests.
  - Testing competitor outputs instead of Quantcraft's validated output.
  - Expanding production implementation scope.
  - Reporting completion without fresh verification evidence.

## Generator Work Log

- Planned slice order:
  1. Add a focused canonical BTC grid regression test. `complete`
  2. Verify RED with an intentionally incomplete expected value. `complete`
  3. Fill the validated Quantcraft expected outputs. `complete`
  4. Run focused integration tests. `complete`
  5. Review the diff and address blocker or important issues. `complete`
  6. Run `uv run poe verify-runtime`. `complete`
- Notes:
  - The checked-in external-comparison plan is the source for expected best-row values.
  - RED evidence: the first focused run failed on the intentionally incomplete
    SMA `returns.total_return` expectation, proving the new regression catches
    metric drift.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocker or important issues found.
  - The regression is first-party only: it uses `ParameterStudy`,
    `BacktestEngine.run(bars=...)`, repo strategy classes, and the checked-in BTC
    CSV fixture via `load_canonical_bars()`.
  - The test does not add or invoke `backtesting.py`, `backtrader`, `vectorbt`,
    optimizer dependencies, parallel controls, persistence, or visualization
    scope.
  - The pinned values match the Quantcraft best-row outputs recorded in
    `docs/plans/2026-05-02-parameter-study-external-comparison-experiment-plan.md`.
- Verification evidence:
  - `uv run pytest tests/integration/research/test_parameter_study_canonical_grid_contract.py -q`
    - RED run: failed as expected on placeholder SMA metric.
    - GREEN run: `3 passed in 5.01s`.
  - `uv run ruff check tests/integration/research/test_parameter_study_canonical_grid_contract.py`
    - `All checks passed!`
  - `uv run pytest tests/integration/research/test_parameter_study_grid_search.py tests/integration/research/test_parameter_study_canonical_grid_contract.py -q`
    - `5 passed in 5.03s`.
  - `uv run poe verify-runtime`
    - `ruff check .`: passed.
    - `mypy src`: passed, `Success: no issues found in 55 source files`.
    - `pytest -q`: `612 passed, 4 skipped in 11.30s`.
    - `coverage_check.py`: passed, total coverage `93%`.
    - `uv build`: built sdist and wheel successfully.
    - `repo_check.py`: passed.
    - `notebook_validate.py`: validated all tracked notebooks.
    - `pytest tests/perf -q -x --run-perf`: `3 passed in 1.84s`.
- Final disposition: Accepted.
