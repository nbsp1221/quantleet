# Active Plan

- Date: 2026-05-02
- Task: Improve `BacktestResult.plot()` chart colors and marker visibility
- Status: `active`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Make the first-beta plot visually legible by giving price, equity,
  drawdown, buy markers, sell markers, and drawdown baseline distinct semantic
  colors.
- Governing docs:
  - `AGENTS.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/product-specs/backtest-plotting-test-scenarios.md`
  - `docs/plans/2026-05-02-backtest-plotting-implementation-plan.md`
- Why these are governing:
  - The repo contract requires a planner/generator/evaluator loop.
  - The plotting spec and test scenarios define the public plotting behavior.
  - The implementation plan owns the current plotting implementation contract.
- In-repo scope:
  - `quantcraft.backtest.plotting`
  - plotting unit/integration tests
  - plotting spec text if needed to lock the UI contract
- Out-of-repo scope:
  - No live data, no external service calls, no product scope expansion.
- Tier A progression requested: `no`
- Approval record, if required: Not required.
- Verification commands:
  - `uv run pytest tests/unit/backtest/test_plotting.py tests/integration/backtest/test_plotting.py -q`
  - `uv run ruff check src/quantcraft/backtest/plotting.py tests/unit/backtest/test_plotting.py tests/integration/backtest/test_plotting.py`
  - `uv run mypy src`
  - `uv run poe repo-check`
- Success criteria:
  - Buy markers are green upward triangles.
  - Sell markers are red downward triangles.
  - Drawdown is visually negative: red line plus subtle red filled area below
    zero.
  - Price, equity, drawdown, marker, and baseline colors are not all Matplotlib
    default blue.
  - Existing public API remains `BacktestResult.plot()`.
  - Subagent review fan-out finds no blocking issues after implementation.
- Out of scope:
  - New plot configuration API.
  - Candlestick rendering.
  - Interactive charting.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Tests assert semantic colors/markers and no public API shape changes.
  - Review fan-out checks UX/spec, correctness/testing, and architecture.
- Acceptance artifact location:
  - This plan's evaluator review section.
- How the generator and evaluator agreed on done before execution:
  - Done is the success criteria plus passing verification commands.
- Checks the evaluator will use:
  - Focused plotting tests, lint, mypy, repo-check, and subagent review.
- Auto-fail conditions:
  - Any public plotting argument is added.
  - Markers depend on Matplotlib default color cycle.
  - Drawdown is still blue-only or lacks a visible negative-area treatment.

## Generator Work Log

- Planned slice order:
  - Add explicit semantic color constants in plotting.
  - Apply colors to price, equity, drawdown, zero baseline, and fills.
  - Update tests to assert color/marker/filled drawdown contract.
  - Update spec text to record the semantic color contract.
  - Run verification and subagent review.
- Notes:
  - Added explicit semantic color constants to `quantcraft.backtest.plotting`.
  - Price now uses a neutral dark line, equity uses blue, drawdown uses a red
    underwater line with subtle red fill, the zero baseline uses gray, buy
    markers use green upward triangles, and sell markers use red downward
    triangles with a light edge stroke.
  - Updated plotting unit tests to assert line colors, marker colors, marker
    shapes, marker edge strokes, marker size, drawdown fill, and zero baseline
    color.
  - Updated the plotting product spec to record the default visual semantics.
  - Subagent architecture review found that `plotting.py` imported
    `BacktestResult` at runtime only for typing. Fixed by moving it under
    `TYPE_CHECKING` and adding a structure test for plotting runtime imports.
- Blockers or scope changes:

## Evaluator Review

- Findings:
  - UX/spec review: no material issues. Residual risk is subjective screenshot
    polish, but artist properties and spec alignment are correct.
  - Correctness/testing review: no material findings. Focused tests now cover
    semantic colors, marker face/edge colors, marker shapes, drawdown line
    color, zero-line color, and red fill. Public API drift is covered by
    `tests/unit/backtest/test_results.py`.
  - Maintainability/architecture review: one material issue fixed. The plotting
    module no longer imports `BacktestResult` at runtime just for typing, and
    structure tests now guard against runtime imports from result/reporting in
    `plotting.py`.
- Verification evidence:
  - `uv run pytest tests/unit/backtest/test_plotting.py tests/integration/backtest/test_plotting.py tests/unit/backtest/test_results.py tests/structure/architecture/test_backtest_plotting_boundaries.py -q`
    passed with `30 passed`.
  - `uv run ruff check src/quantcraft/backtest/plotting.py tests/unit/backtest/test_plotting.py tests/integration/backtest/test_plotting.py tests/structure/architecture/test_backtest_plotting_boundaries.py`
    passed.
  - `uv run mypy src` passed.
  - `uv run poe repo-check` passed with `repository checks passed`.
- Final disposition:
  - Complete.
