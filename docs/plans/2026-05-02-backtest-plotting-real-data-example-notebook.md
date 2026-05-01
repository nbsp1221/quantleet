# Active Plan

- Date: 2026-05-02
- Task: Add a real-data notebook example for `BacktestResult.plot()`
- Status: `active`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Provide a notebook that shows the complete user flow for
  `BacktestResult.plot()` using an actual checked-in BTC historical dataset and
  a realistic strategy.
- Governing docs:
  - `AGENTS.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/product-specs/backtest-plotting-test-scenarios.md`
  - `docs/references/research-ergonomics-quickstart.md`
- Why these are governing:
  - The repo contract requires a plan and fresh verification for non-trivial
    changes.
  - The plotting spec defines the canonical user-facing plot API.
  - The quickstart defines the current notebook/example tone and import paths.
- In-repo scope:
  - Add or update notebook/docs/tests needed to demonstrate `result.plot()` on
    real checked-in data.
- Out-of-repo scope:
  - No network data fetches, no external services, no live exchange calls.
- Tier A progression requested: `no`
- Approval record, if required: Not required; this is example/documentation and
  deterministic notebook validation, not Tier A trading/execution work.
- Verification commands:
  - `uv run python scripts/notebook_validate.py`
  - `uv run pytest tests/structure/docs/test_research_ergonomics_quickstart.py -q`
  - `uv run poe repo-check`
- Success criteria:
  - A notebook demonstrates `CSVDataSource -> BacktestEngine.run(...) ->
    result.summary/result.report/result.plot()` as one coherent flow.
  - The notebook uses the checked-in Binance USD-M BTC/USDT 1h 2025 fixture.
  - The strategy is realistic enough for an example and does not depend on
    tests-only helpers.
  - Notebook validation executes the example without network access.
- Out of scope:
  - Changing plotting behavior.
  - Introducing live data dependencies.
  - Broad documentation redesign.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - The notebook is executable, deterministic, and uses public package APIs.
  - The example calls `result.plot()` directly without passing bars/source back
    into plotting.
  - Fresh verification evidence is recorded in this plan.
- Acceptance artifact location:
  - This plan's evaluator review section.
- How the generator and evaluator agreed on done before execution:
  - Done is the success criteria plus the listed verification commands.
- Checks the evaluator will use:
  - Notebook validation and focused docs structure tests.
- Auto-fail conditions:
  - The notebook requires network access.
  - The notebook imports from `tests.support_backtest`.
  - The notebook shows `result.plot(bars=...)`, `plot_backtest(...)`, or
    `BacktestEngine.plot()`.

## Generator Work Log

- Planned slice order:
  - Confirm fixture data and public CSV source path.
  - Add real-data example notebook.
  - Add structure assertions so the example remains discoverable.
  - Run notebook/docs/repo verification.
- Notes:
  - Added `notebooks/backtest-plotting-real-data-example.ipynb`.
  - The notebook uses public APIs only: `CSVDataSource`, `BacktestEngine`,
    `Strategy`, `qc`, `ta`, and `CostConfig`.
  - The notebook loads the checked-in Binance USD-M BTC/USDT 1h 2025 CSV
    fixture, runs an RSI 30/70 long-only strategy, inspects summary/report
    values, and renders `fig = result.plot()`.
- Blockers or scope changes:

## Evaluator Review

- Findings:
  - No blocking findings. The example is deterministic, network-free, and
    demonstrates the intended user flow without importing tests-only helpers or
    passing bars/source back into plotting.
- Verification evidence:
  - `uv run pytest tests/structure/docs/test_research_ergonomics_quickstart.py -q`
    passed with `4 passed`.
  - `uv run python scripts/notebook_validate.py` passed and validated
    `backtest-plotting-real-data-example.ipynb` plus the existing tracked
    notebooks.
  - `uv run poe repo-check` passed with `repository checks passed`.
- Final disposition:
  - Complete.
