# Backtest Plotting Test Scenarios

## Status

- Status: `planned`
- Class: `product-spec`
- Scope: first-beta `BacktestResult.plot()` test scenarios

Related documents:

- [backtest-plotting.md](backtest-plotting.md)
- [research-ergonomics.md](research-ergonomics.md)
- [backtest-mvp.md](backtest-mvp.md)
- [../RELIABILITY.md](../RELIABILITY.md)

This document defines the test scenario contract for the first-beta backtest
plotting feature. It does not claim the tests or the plotting feature are
already implemented.

## Goal

Turn the product intent in [backtest-plotting.md](backtest-plotting.md) into a
test suite that catches likely design, integration, and edge-case bugs before
plotting implementation is treated as complete.

The suite should prove that:

- `result.plot()` is the only first-beta public plotting workflow users need
- engine-produced results are self-contained enough to plot
- the figure communicates price, fills, equity, and drawdown clearly
- result data ownership stays clean
- side effects do not leak into user code
- edge cases are explicit rather than accidental

## Testing Philosophy

Tests are product assets. They should be maintained with the same seriousness
as production code and should outlive implementation details.

Operational rules:

1. Test observable behavior and public contracts, not private implementation.
   A refactor of `quantcraft.backtest.plotting` should not require rewriting
   tests unless the user-visible contract changes.
2. Each test should explain one behavior. If a test name needs "and", split it
   unless the behavior is one inseparable workflow.
3. Prefer real engine paths over mocks. Use fakes only for boundary observation,
   such as a source object that counts `load()` calls.
4. Keep expected values explicit. Do not hide test truth in helper logic that
   reimplements the production algorithm.
5. Use layered coverage. Unit tests should isolate formulas and figure-contract
   helpers, integration tests should run real `BacktestEngine` workflows, smoke
   tests should protect public imports and built artifacts, structure tests
   should protect dependency/import boundaries, and performance-adjacent tests
   should protect the 10,000-bar no-downsampling contract.
6. When an integration test exposes a bug that no lower-level test catches, add
   a lower-level regression test before closing the slice.

These rules are grounded in:

- Google Testing Blog's guidance to test behaviors rather than methods:
  [Testing on the Toilet: Test Behaviors, Not Methods](https://testing.googleblog.com/2014/04/testing-on-toilet-test-behaviors-not.html)
- Google's guidance that tests should change only when behavior changes:
  [Software Engineering at Google, Chapter 12](https://abseil.io/resources/swe-book/html/ch12.html)
- Google's warning that larger tests and doubles carry contract risks:
  [Software Engineering at Google, Chapter 14](https://abseil.io/resources/swe-book/html/ch14.html)
- the test pyramid guidance to combine fast lower-level tests with fewer
  higher-level tests:
  [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- pytest's recommendation to keep tests outside application code:
  [pytest Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- Google Testing Blog's guidance to keep test logic simple:
  [Don't Put Logic in Tests](https://testing.googleblog.com/2014/07/testing-on-toilet-dont-put-logic-in.html)

## Proposed Test Placement

The implementation plan should map scenarios to these areas:

| Layer | Proposed location | Purpose |
| --- | --- | --- |
| Unit | `tests/unit/backtest/test_plotting.py` | Figure contract, drawdown formula, validation errors, no side effects local to plotting. |
| Unit | `tests/unit/backtest/test_results.py` | `BacktestResult.plot()` facade behavior, missing snapshot error, equality semantics for `drawdown_curve`. |
| Integration | `tests/integration/backtest/test_plotting.py` | Backtest-owned real `BacktestEngine.run(...)` workflows through `bars=...` and `source=...`. |
| Smoke | `tests/smoke/local/test_public_imports.py` | Public imports remain clean after adding plotting support. |
| Structure | `tests/structure/architecture/test_backtest_plotting_boundaries.py` | Matplotlib import locality and no forbidden context dependencies. |
| Perf-adjacent | `tests/perf/test_backtest_plotting_scale.py` | 10,000-bar no-downsampling mechanical contract under explicit perf lane if too expensive for default tests. |

If the 10,000-bar figure test is cheap enough under a non-interactive backend,
it may live in the normal integration suite. If it materially slows the default
lane, place it in `tests/perf/` and update the Poe task surface so the plotting
scale test is actually included in `uv run poe verify-runtime`. The current
repository performance lane is intentionally explicit, so placing a file under
`tests/perf/` is not sufficient by itself.

## Matplotlib Test Hygiene

Tests that create figures should use a non-interactive backend such as `Agg`
and close returned figures in teardown with `plt.close(fig)` or
`plt.close("all")`. This is a test hygiene rule only. The production
`result.plot()` contract remains that it returns an open figure and does not
call `show()`, `savefig()`, or `close()`.

## Test Data Strategy

Use named fixtures that describe market shape and expected result behavior:

| Fixture | Shape | Purpose |
| --- | --- | --- |
| `rising_bars` | monotonically rising close prices | no-drawdown, no-fill, all-zero drawdown behavior. |
| `falling_then_recovering_bars` | peak, drawdown, recovery | positive drawdown and recovery visualization. |
| `buy_then_sell_bars` | deterministic entry and exit opportunity | buy/sell marker placement and equity/drawdown alignment. |
| `source_once_bars` | fake source returning a `BarSeries` and counting loads | prove plot does not reload source. |
| `large_10k_bars` | 10,000 strictly increasing or patterned bars | no-downsampling and scale contract. |
| `manual_result_without_snapshot` | manually constructed `BacktestResult` | missing snapshot error remains isolated to plot. |
| `mismatched_plot_series_result` | result with snapshot/equity/drawdown length mismatch | diagnostic `ValueError`. |
| `single_bar_result` | one-bar plottable result | degenerate but valid one-point plot. |
| `empty_snapshot_result` | result with empty plot data | diagnostic empty-data failure. |

Fixtures should avoid duplicating full production algorithms. For drawdown edge
cases, use explicit equity sequences and explicit expected drawdown values.

## Unit Scenarios

### U1: Drawdown Formula

Purpose: protect the risk-inspection contract independently of Matplotlib.

Scenarios:

| Case | Equity values | Expected drawdown values |
| --- | --- | --- |
| flat | `(100.0, 100.0, 100.0)` | `(0.0, 0.0, 0.0)` |
| monotonically rising | `(100.0, 110.0, 120.0)` | `(0.0, 0.0, 0.0)` |
| simple drawdown | `(100.0, 90.0, 95.0)` | `(0.0, 0.1, 0.05)` |
| new high resets peak | `(100.0, 90.0, 120.0, 108.0)` | `(0.0, 0.1, 0.0, 0.1)` |
| zero running peak | `(0.0, -5.0, -1.0)` | `(0.0, 0.0, 0.0)` |
| negative after positive peak | `(100.0, -20.0)` | `(0.0, 1.2)` |

Required assertions:

- values are rounded to 12 decimal places
- values are not clamped at `1.0`
- the helper does not depend on `BacktestReport` or Matplotlib

### U1A: Public Plot API Shape

Purpose: protect the beta API from silently accepting workaround-style inputs.

Required assertions:

- the public `BacktestResult.plot` signature exposes no `bars`, `source`,
  dataframe, or report parameter
- `result.plot(bars=bars)` fails with the normal Python call-shape error for an
  unexpected argument
- `result.plot(source=source)` fails with the normal Python call-shape error
  for an unexpected argument
- the test does not require a figure to be created for rejected call shapes

### U2: Result Facade Requires Engine Snapshot

Purpose: preserve manual result construction while making the plot contract
honest.

Scenarios:

- manually constructed `BacktestResult` without snapshot remains valid for
  `summary`, `trade_log`, and `equity_curve`
- calling `plot()` on that result raises `ValueError`
- error message names the missing run snapshot

Required assertions:

- no Matplotlib figure is created on the missing-snapshot path
- the failure is not a generic `AttributeError` or import error

### U3: Plot Series Length Validation

Purpose: prevent silently misaligned charts.

Scenarios:

- timestamps length differs from `equity_curve`
- timestamps length differs from `drawdown_curve`
- `equity_curve` length differs from `drawdown_curve`

Required assertions:

- `result.plot()` raises `ValueError`
- message includes `timestamps`, `equity_curve`, and `drawdown_curve`
- message includes the observed lengths

### U4: Figure Contract For A Normal Result

Purpose: verify the user-visible figure contract without depending on private
renderer internals.

Input: a plottable result with three bars, one buy fill, one sell fill, equity
values, and drawdown values.

Required assertions:

- return value is a Matplotlib `Figure`
- figure has exactly three axes
- axes are ordered price, equity, drawdown
- title is `{symbol} {timeframe} Backtest`
- legends include `Close`, `Buy`, `Sell`, `Equity`, and `Drawdown`
- y-axis labels are `Price`, `Equity`, and `Drawdown (%)`
- shared x-axis label is `Time (UTC)`
- drawdown axis has a visible zero baseline
- default figure size is 12 by 8 inches
- axes share the x-axis
- axes heights preserve the intended price, equity, drawdown ordering and
  approximate `3:2:1` ratio within a reasonable tolerance
- grid lines are enabled on each panel
- the close artist uses the run snapshot's close values
- the equity artist uses `result.equity_curve`
- the drawdown artist uses `-result.drawdown_curve` because stored drawdown
  values are positive loss fractions while the plot renders an underwater
  series below zero
- buy and sell marker points use fill timestamps for x-values and fill
  execution prices for y-values

Tests should not assert exact colors, marker glyph internals, or private helper
names unless those become explicit product contract.

### U5: No-Fill Result

Purpose: prove no-fill runs still produce useful inspection output.

Input: plottable result with no fills.

Required assertions:

- price, equity, and drawdown panels exist
- buy/sell marker artists are absent
- buy/sell legend entries are absent
- `Close`, `Equity`, and `Drawdown` remain present

### U6: No-Drawdown Result

Purpose: prove no-drawdown runs do not create a blank or misleading panel.

Input: flat or monotonically rising equity and all-zero `drawdown_curve`.

Required assertions:

- drawdown panel exists
- drawdown artist contains all-zero plotted values
- drawdown legend entry remains `Drawdown`
- drawdown zero baseline is visible

### U7: Timestamp Conversion

Purpose: protect the time-axis contract.

Input: timestamps such as `0`, `60_000`, and `120_000`.

Required assertions:

- plotted x-values are UTC datetimes or Matplotlib date values derived from UTC
  datetimes
- x-axis label is `Time (UTC)`
- fill markers align with fill timestamps, not bar indexes

### U8: Matplotlib Import Locality

Purpose: keep normal imports cheap and avoid leaking plotting dependency into
non-plot workflows.

Scenarios:

- importing `quantcraft.backtest.results` does not import `matplotlib`
- importing `quantcraft.backtest` does not import `matplotlib`
- calling `result.plot()` performs the plotting import path

Required assertions:

- check `sys.modules` before and after non-plot imports
- use a fresh interpreter subprocess if needed to avoid contamination from
  prior tests

### U9: No Side Effects

Purpose: prove `plot()` is a pure inspection method.

Scenarios:

- patch `matplotlib.pyplot.show` and assert it is not called
- patch `Figure.savefig` or filesystem write APIs only if the implementation
  exposes a risk; otherwise assert no configured output path is touched
- call `plot()` twice and assert result values are unchanged

Required assertions:

- no `show()`
- no file write
- no `close()`
- no mutation of `trade_log`, `equity_curve`, `drawdown_curve`, summary, or
  result-owned plot data

### U10: Empty And Single-Bar Plot Data

Purpose: make degenerate plot inputs diagnostic rather than accidental.

Scenarios:

- a result with a snapshot but zero bar timestamps
- a plottable result with exactly one bar

Required assertions:

- zero bar timestamps raise `ValueError` naming empty run data
- one bar returns a three-axis `Figure`
- one-point close, equity, and underwater drawdown series are plotted

## Integration Scenarios

### I1: `engine.run(bars=...)` Produces Plottable Result

Purpose: prove the canonical materialized-bar workflow needs no extra user data.

Flow:

1. build deterministic `BarSeries`
2. run `BacktestEngine(...).run(bars=bars, strategy=StrategyType)`
3. call `result.plot()`

Required assertions:

- figure has three axes
- figure title metadata matches the `BarSeries`
- plotted close x/y values come from the bars used for the run
- `result.equity_curve`, `result.drawdown_curve`, and plotted timestamp series
  have matching lengths
- buy/sell markers appear when the strategy trades

### I2: `engine.run(source=...)` Produces Plottable Result Without Reload

Purpose: protect the source-backed UX that motivated `result.plot()`.

Flow:

1. create fake source with `load_count`
2. run `BacktestEngine(...).run(source=source, strategy=StrategyType)`
3. call `result.plot()`

Required assertions:

- `source.load()` is called exactly once during `run`
- `result.plot()` does not call `source.load()` again
- figure has price, equity, and drawdown panels

### I3: Source-Returned Data Is Snapshotted

Purpose: prove result inspection does not depend on mutable user/source state.

Flow:

1. fake source returns a `BarSeries`
2. run the engine
3. mutate or replace the source's stored rows after the run if the fake source
   allows it
4. call `result.plot()`

Required assertions:

- plotted close values reflect the run-time values, not later source mutation
- assertions use observable plotted data, not private snapshot object identity,
  as the primary evidence of snapshot independence

### I4: User-Owned Bar Data Mutation Cannot Change Plot

Purpose: prove explicit `bars=...` workflows are also self-contained.

Flow:

1. build `BarSeries` from a mutable upstream representation, such as raw row
   dictionaries or a dataframe-like object
2. run the engine
3. mutate that upstream representation after the run
4. call `result.plot()`

Required assertions:

- plotted series reflect the original run values
- test uses observable plotted data, not private object identity, as the main
  assertion

### I5: No-Fill Strategy Integration

Purpose: prove realistic no-trade strategies still produce useful result
inspection.

Flow:

1. use a strategy that never orders
2. run via `bars=...`
3. call `result.plot()`

Required assertions:

- no buy/sell marker entries
- price/equity/drawdown panels remain present
- drawdown behavior follows the equity path

### I6: Drawdown-Producing Strategy Integration

Purpose: prove drawdown is populated from real marked equity, not a hand-built
plot stub.

Flow:

1. use bars and a simple long strategy that enters before a price drop
2. run the engine
3. call `result.plot()`

Required assertions:

- `result.drawdown_curve` contains at least one positive value
- `result.summary.max_drawdown == max(result.drawdown_curve)`
- drawdown panel data matches `-result.drawdown_curve`, preserving the
  underwater visual convention while keeping result values positive

### I7: Plot Is Independent Of `BacktestReport`

Purpose: protect the architecture decision that report is not the plot data
source.

Acceptable approaches:

- prefer a structure test proving `quantcraft.backtest.plotting` does not
  import `quantcraft.backtest.reporting` or read `BacktestReport` internals
- use an engine-produced result and verify plot data matches result-owned fields
  rather than report-only fields
- only if necessary for an otherwise unreachable invalid state, use a narrowly
  scoped internal test factory to construct a plottable result without `_report`

Required assertions:

- `result.plot()` does not require `result.report`
- `BacktestReport.equity` is not the only path by which drawdown can be plotted

### I8: Built Artifact Runtime Dependency

Purpose: prove `pip install quantcraft` includes plotting dependency.

Flow:

1. build the package artifact
2. either inspect the wheel metadata for `Requires-Dist: matplotlib` or install
   the wheel with dependencies into a clean temporary environment
3. import `matplotlib` from that clean package environment
4. run a minimal `result.plot()` smoke path if feasible in that environment

Required assertions:

- `matplotlib` is available as a runtime dependency
- no dev dependency group is required for plotting

## Structure And Import Scenarios

### S1: No Matplotlib Import At Normal Backtest Import Time

Purpose: protect lazy import and normal library import cost.

Required assertions:

- `python -c "import quantcraft.backtest, sys; assert 'matplotlib' not in sys.modules"`
  passes in a fresh process
- a separate plot call may import Matplotlib

### S2: Plotting Code Stays In Backtest Boundary

Purpose: preserve package ownership.

Required assertions:

- plotting implementation lives under `src/quantcraft/backtest/`
- `quantcraft.backtest` and `quantcraft.backtest.plotting` do not import
  `quantcraft.research`, `quantcraft.execution`, `apps`, or deep sibling
  internals
- `trading` does not import `backtest`, `research`, or Matplotlib
- `data` does not import plotting code

### S3: Public Surface Does Not Promote Non-Primary APIs

Purpose: keep the beta API focused.

Required assertions:

- docs and examples use `result.plot()`
- docs do not show `result.plot(bars=...)`
- docs do not promote `plot_backtest(...)`, `BacktestEngine.plot()`, or
  `result.report.plot()` as beta path

## Perf-Adjacent Scenario

### P1: 10,000-Bar No-Downsampling Contract

Purpose: protect the scale promise without turning the default plot into a
benchmark suite unless necessary.

Input:

- `large_10k_bars`
- deterministic no-fill or simple-fill strategy
- non-interactive Matplotlib backend

Required assertions:

- render completes without exception
- figure has three axes
- close, equity, and drawdown artists each retain 10,000 x-points
- no source reload, no `show()`, and no file write occur
- if this scenario lives in `tests/perf/`, the implementation must update the
  Poe task surface so it runs under `uv run poe verify-runtime`

No render-time threshold is required for first beta. If a later implementation
adds one, it must live in the explicit performance lane and document the
hardware/CI assumptions.

## Negative Scenarios

These scenarios should fail loudly and diagnostically:

| Case | Expected failure |
| --- | --- |
| manual result without snapshot calls `plot()` | `ValueError` naming missing run snapshot |
| snapshot timestamps length differs from equity length | `ValueError` naming timestamps/equity/drawdown lengths |
| snapshot timestamps length differs from drawdown length | `ValueError` naming timestamps/equity/drawdown lengths |
| result has snapshot but no drawdown curve | `ValueError` naming missing or mismatched drawdown data |
| result has empty snapshot timestamps | `ValueError` naming empty run data |
| plot receives no bars/source because result was not engine-produced | no source reload attempt; direct missing-snapshot error |

Negative tests should assert the public exception type and stable diagnostic
message, not private helper call order.

## Documentation Scenarios

Documentation tests or notebook validation should cover:

- quickstart or beta docs show `fig = result.plot()` or `result.plot()`
- script docs show `plt.show()` separately from `result.plot()`
- save/export docs use `fig.savefig(...)`
- no docs imply that users must pass `bars` back into `plot()`
- no docs imply that plotting is optional-install-only after the runtime
  dependency decision

## Required Verification When Implemented

The implementation slice should run:

- focused unit tests for plotting/result behavior
- focused integration tests for `bars=...` and `source=...`
- smoke tests for public imports and built artifact imports
- structure tests for import and package-boundary rules
- `uv run poe verify`
- `uv run poe verify-runtime` if runtime code in `src/quantcraft/backtest/runtime.py`
  changes to populate snapshots or `drawdown_curve`

## Out Of Scope

This test scenario spec does not require:

- pixel-perfect visual regression screenshots
- exact Matplotlib colors or marker glyph internals
- browser rendering checks
- Plotly or Bokeh tests
- multi-symbol or multi-timeframe plot tests
- live, paper, or external-network tests
- performance timing thresholds

Those can be introduced only after the first-beta plot contract expands.
