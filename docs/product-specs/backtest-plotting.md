# Backtest Plotting Spec

## Status

- Status: `implemented`
- Class: `product-spec`
- Scope: first-beta backtest result plotting workflow

Related documents:

- [backtest-plotting-test-scenarios.md](backtest-plotting-test-scenarios.md)
- [research-ergonomics.md](research-ergonomics.md)
- [backtest-mvp.md](backtest-mvp.md)
- [../design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)
- [../design-docs/quantleet-architecture.md](../design-docs/quantleet-architecture.md)

This document defines the product contract for the implemented first-beta
backtest plot.
The corresponding test scenario contract is
[backtest-plotting-test-scenarios.md](backtest-plotting-test-scenarios.md).

## Goal

Make visual result inspection a first-class beta workflow:

```python
result = engine.run(bars=bars, strategy=MyStrategy)
fig = result.plot()
```

A user should be able to see, without reloading data or passing duplicate
inputs, whether the strategy traded where they expected, how the equity curve
evolved, and how deep the peak-to-trough drawdowns became.

## Decision Summary

- The primary beta API is `BacktestResult.plot()`.
- `BacktestResult.plot()` returns a `matplotlib.figure.Figure`.
- `matplotlib` is a normal runtime dependency for the beta package, not a
  dev-only dependency and not a plotting extra.
- Engine-produced `BacktestResult` values must retain the immutable run data
  needed for plotting.
- The implementation should use a backtest-owned plotting module. The result
  object should expose the user-facing method but should not contain plotting
  logic.
- The first plot is intentionally basic: price, fills, equity, and drawdown. It
  is not an indicator dashboard or optimizer visualization surface.
- The first beta supports a documented, no-downsampling plot size target rather
  than an unbounded charting workload.

## Why This Is The Contract

### User Value Comes First

The user has just run a backtest. The object in their hands is the result. If
the next natural question is "what happened?", `result.plot()` is the shortest
and least surprising answer.

Requiring `result.plot(bars=bars)` or `plot_backtest(bars=bars, result=result)`
forces users to keep or recreate input data that the engine already consumed.
That is especially poor for the `engine.run(source=...)` path, where the user
may not have retained the materialized `BarSeries` separately.

The beta API should make the correct workflow easy:

1. load or provide bars
2. run the engine
3. inspect the returned result

### Architecture Should Own The Run Artifact

`BacktestResult` is not only a statistics dataclass. For first-beta UX, it is
the inspection artifact for one historical run.

That means an engine-produced result should contain a backtest-owned immutable
run snapshot with the market data needed to reproduce result inspection. The
snapshot should be created from the materialized `BarSeries` during the run. It
must not retain the original data source object, perform lazy source reloads, or
depend on user-owned mutable dataframe state after the run completes.

The result method remains a facade:

- `BacktestResult.plot()` owns the public UX.
- `quantleet.backtest.plotting` owns matplotlib-specific rendering.
- `BacktestReport` owns structured analytics and readable reporting, not chart
  rendering.
- `BacktestEngine` remains the runtime entry point, not a stateful last-run
  plot holder.

This keeps capability ownership aligned with the architecture: `backtest` owns
historical runtime outputs and inspection for a historical run.

### Dependency Strategy Follows The Product Promise

Comparable libraries take different dependency approaches depending on whether
plotting is a core workflow:

| Library | Plotting dependency strategy | Product signal |
| --- | --- | --- |
| `backtesting.py` | `bokeh` is in `install_requires` | Plotting is part of the main backtest UX. See project metadata and `Backtest.plot(...)` docs: [setup.py](https://raw.githubusercontent.com/kernc/backtesting.py/master/setup.py), [API docs](https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html). |
| `vectorbt` | `matplotlib`, `plotly`, and widgets are base dependencies | Portfolio analysis includes rich charting as a normal capability. See [pyproject.toml](https://raw.githubusercontent.com/polakowo/vectorbt/master/pyproject.toml) and [Portfolio plotting docs](https://vectorbt.dev/api/portfolio/base/). |
| `quantstats` | `matplotlib` and `seaborn` are base dependencies, `plotly` is optional | Static report plotting is core, Plotly conversion is extra. See [pyproject.toml](https://raw.githubusercontent.com/ranaroussi/quantstats/main/pyproject.toml) and [PyPI metadata](https://pypi.org/project/QuantStats/). |
| `backtrader` | `matplotlib` is an optional `plotting` extra | Plotting is built in but installation keeps it optional. Backtrader is a historical/popular comparator rather than a current-practice anchor. See [installation docs](https://www.backtrader.com/docu/installation/) and [setup.py](https://raw.githubusercontent.com/mementum/backtrader/master/setup.py). |
| `PyBroker` | No core matplotlib dependency; docs show manual matplotlib usage | Result data is exposed and users plot manually. See [installation docs](https://www.pybroker.com/en/latest/install.html), [backtest docs](https://www.pybroker.com/en/latest/notebooks/2.%20Backtesting%20a%20Strategy.html), and [setup.cfg](https://raw.githubusercontent.com/edtechre/pybroker/master/setup.cfg). |

For `quantleet`, the first-beta product promise is closer to `backtesting.py`,
`vectorbt`, and `quantstats` than to PyBroker's manual plotting model. Basic
plotting is part of the implemented beta inspection path, so `pip install
quantleet` should be enough for `result.plot()` to work.
This accepts Matplotlib's transitive dependency footprint in favor of a
zero-extra plotting workflow for the beta user.

Comparable libraries commonly expose drawdown inspection, although default
placement varies: `backtesting.py` and `backtrader` make drawdown opt-in,
`vectorbt` supports explicit drawdown and underwater subplots, and
return-analysis libraries such as `quantstats` treat underwater drawdown charts
as a standard analytics/reporting view. Quantcraft chooses to include drawdown
in the first beta default plot because the beta plot is meant to pair trade
inspection with basic risk inspection.

Implementation must therefore move the existing `matplotlib>=3.10.8`
requirement from `[dependency-groups].dev` into `[project.dependencies]` and
refresh the lockfile. It may still import matplotlib lazily inside the plotting
module to keep normal imports cheap and to keep rendering concerns out of
result models.

## Public API

### Required Path

The required beta path is:

```python
result = BacktestEngine(...).run(bars=bars, strategy=StrategyType)
fig = result.plot()
```

The same must work for:

```python
result = BacktestEngine(...).run(source=source, strategy=StrategyType)
fig = result.plot()
```

### Method Contract

`BacktestResult.plot()`:

- requires no user-supplied bars, source, dataframe, or report object
- returns a `matplotlib.figure.Figure`
- does not call `show()`
- does not write files
- does not reload market data
- does not mutate the result
- works for runs with no fills
- raises a clear `ValueError` when called on a manually constructed
  `BacktestResult` without a run snapshot

The first public method must require no arguments. Keyword-only presentation
options may be added only when they are documented and tested. `bars` and
`source` must not become public parameters on `result.plot()`.

`BacktestResult` must not import Matplotlib at normal runtime import time. If a
return annotation is exposed from `results.py`, it must use `TYPE_CHECKING`,
quoted annotations, or another approach that preserves localized plotting
imports. The concrete Matplotlib import belongs in `quantleet.backtest.plotting`.

### Non-Primary APIs

These are not the beta public path:

- `plot_backtest(bars=..., result=...)`
- `result.plot(bars=...)`
- `BacktestEngine.plot()`
- `result.report.plot()`

An internal helper may exist if it keeps rendering code clean, but the user
contract remains `result.plot()`.

## Plot Content

The first-beta plot must include:

- a top price panel using the run's close prices
- buy and sell fill markers on the price panel
- a middle equity panel using the run equity curve
- a bottom drawdown panel using the run drawdown curve
- a title that identifies the run's symbol and timeframe
- stable axis labels and legend text

Candlesticks are allowed later but are not required for first beta. A close
price line is acceptable because the first user value is fast inspection of
fills versus price, equity, and drawdown, not full charting-terminal fidelity.

Minimum labels and legend entries:

- price line legend: `Close`
- buy marker legend: `Buy`
- sell marker legend: `Sell`
- equity line legend: `Equity`
- drawdown line legend: `Drawdown`
- price panel y-axis label: `Price`
- equity panel y-axis label: `Equity`
- drawdown panel y-axis label: `Drawdown (%)`
- shared x-axis label: `Time (UTC)`

The title format is `{symbol} {timeframe} Backtest`.

Default layout:

- three vertically stacked axes in price, equity, drawdown order
- shared x-axis
- default figure size of 12 by 8 inches
- panel height ratio of `3:2:1`
- per-panel legends
- light grid lines on all panels
- visible zero baseline on the drawdown panel

Fill markers use each fill's timestamp and execution price. Buy fills use the
`Buy` marker series, and sell fills use the `Sell` marker series. A no-fill run
omits buy/sell marker artists and omits buy/sell legend entries; it must still
show the close price, equity, and drawdown panels.

Default visual semantics:

- close price uses a neutral dark line so execution markers remain visible
- equity uses a distinct blue line
- buy fills use green upward triangle markers
- sell fills use red downward triangle markers
- fill markers use a light edge stroke so they remain visible on top of the
  price line
- drawdown uses a red underwater line with a subtle red fill to reinforce that
  it represents loss
- the drawdown zero baseline uses neutral gray

Drawdown values use the same ratio convention as the existing report risk
surface: stored values are fractions, where `0.0` means no drawdown and
positive values represent peak-to-trough loss relative to the running equity
peak. For each bar:

```text
running_peak[t] = max(equity_curve[:t + 1])
drawdown[t] = (
    0.0
    if running_peak[t] <= 0.0
    else max((running_peak[t] - equity_curve[t]) / running_peak[t], 0.0)
)
```

Drawdown values are rounded to 12 decimal places. They are not clamped at
`1.0`; if equity falls below zero after a positive running peak, drawdown may
exceed 100%.

The result stores drawdown as positive loss fractions because that is the
analytics convention used by summary/reporting. The plot renders those values
as an underwater series below zero by multiplying stored drawdown values by
`-1`, then formats the y-axis as percentages under the `Drawdown (%)` label.
This keeps the result data easy to compare numerically while making the visual
risk panel read as drawdown rather than upside.

A flat or monotonically rising equity curve plots drawdown as an all-zero
`Drawdown` series with the visible zero baseline rather than omitting the panel.

The x-axis uses UTC datetimes converted from canonical UTC epoch-millisecond
bar and fill timestamps. This follows the data ingestion contract, which
normalizes tabular timestamps to UTC milliseconds, and Matplotlib's documented
date plotting path, which provides date-aware tick locators and formatters for
`datetime` values.

A plottable result with zero bar timestamps is invalid for `plot()` and must
raise a clear `ValueError` naming the empty run data. A plottable result with a
single bar is valid and should produce the same three-panel figure with
one-point price, equity, and drawdown series.

## Run Snapshot Contract

Engine-produced results must retain an immutable backtest-owned snapshot with
the minimum data required for plotting.

Minimum snapshot content:

- symbol
- timeframe
- bar type
- bar timestamps
- close values

`symbol`, `timeframe`, and `bar_type` are required non-empty metadata for
plottable engine-produced results because the current canonical input type is
`BarSeries`.

The first beta minimum intentionally stores only the market data used by the
default plot: timestamps and closes. An implementation may keep additional
OHLCV values internally if doing so is simpler and remains immutable, but tests
and public documentation must not depend on open, high, low, or volume until
those values become part of a user-visible plotting contract.

The snapshot should be independent of the original `BarSeries` object identity
and should copy primitive values into immutable tuples or equivalent immutable
storage. It may preserve equivalent values, but it must not rely on mutable
external state. It must be created after the engine has materialized
`source.load()` or accepted explicit `bars`.

The snapshot is for result inspection, not for rerunning execution.

The snapshot owns market-bar data only. Plotting consumes the snapshot for price
series and consumes immutable `BacktestResult` values for fills, equity, and
drawdown:

- fill markers come from `BacktestResult.trade_log`
- the equity panel comes from `BacktestResult.equity_curve`
- the drawdown panel comes from `BacktestResult.drawdown_curve`

The plotting module must not recompute fills, equity, or drawdown from bars and
must not depend on `BacktestReport` as the source of plot data. `BacktestReport`
remains the structured analytics and readable reporting surface.

The runtime must populate `BacktestResult.drawdown_curve` directly from the
same marked equity stream used for `BacktestResult.equity_curve`, before or
alongside report construction. It may share a pure drawdown helper with the
reporting path, but it must not derive `drawdown_curve` by reading
`BacktestReport`, `BacktestReport.equity`, or `_ReportBuilder` internals.
The implementation should consolidate the existing max-drawdown and report
drawdown calculations around the same pure helper so `drawdown_curve`,
`summary.max_drawdown`, and report risk metrics cannot drift.

`BacktestResult.drawdown_curve` is a plot-ready immutable series with one value
per bar. It should be added as a keyword-only field with a default empty tuple
to preserve existing positional construction. Because it is a semantic result
value, it is part of `BacktestResult` equality for the first-beta result
contract. Engine-produced results must populate it, and tests should assert it
directly.

For plottable results, `len(result.equity_curve)` must equal
`len(result.drawdown_curve)` and both must equal the internal run snapshot's
bar timestamp length. If a result has a snapshot but any plot series length
does not match the bar timestamp length, `result.plot()` must raise a
`ValueError` whose message includes `timestamps`, `equity_curve`, and
`drawdown_curve` lengths.

To preserve existing positional construction without making the snapshot part
of semantic result equality, the snapshot should be added as an optional
keyword-only field, excluded from equality and repr, with a default of `None`.
A manually constructed result without this snapshot remains valid for non-plot
inspection and raises the documented `ValueError` only when `plot()` is called.

## Display And Export

`result.plot()` creates and returns a figure. It does not display, save, or
close it.

Documentation should show the normal Matplotlib usage patterns:

- notebook users may put `result.plot()` as the final cell expression
- script users may call `plt.show()` after assigning the returned figure
- users who need a file may call the standard `fig.savefig(...)`

Quantcraft should not add custom save/export helpers for the first beta.

## Scale Assumption

The first-beta plot must be verified with 10,000 bars for the single-symbol,
single-timeframe workflow. This covers a one-year 1h backtest and roughly a
one-week 1m backtest.

The 10,000-bar test is mechanical, not a subjective visual review. It should
use a non-interactive Matplotlib backend and assert that rendering succeeds,
the figure has three axes, and the close, equity, and drawdown artists each
retain 10,000 x-points without downsampling.

Inputs larger than 10,000 bars are best effort for the first beta. They should
not be rejected solely because of size, but the beta contract does not guarantee
rendering speed, label density, or readability beyond that point. No render-time
threshold is part of the beta contract. A downsampling policy remains out of
scope.

## Out Of Scope

The first-beta plot does not include:

- indicator overlays
- volume panel
- drawdown panel controls or alternate drawdown modes
- optimizer heatmaps
- Plotly, Bokeh, or browser backends
- public save/export helpers
- interactive widgets
- multi-symbol or multi-timeframe plotting
- paper or live trading plots
- downsampling policy for very large datasets

These can be designed later without weakening the first beta contract.

## Success Criteria

The plot feature is successful only if all of the following are true:

1. `result.plot()` works immediately after both supported engine entry paths.
2. A user does not have to pass bars or reload a source to plot a completed run.
3. The method returns a Matplotlib `Figure` without side effects.
4. The figure shows price, fill markers, equity, and drawdown in a legible
   three-panel layout.
5. Runs with no fills still produce a useful price/equity/drawdown figure.
6. Manually constructed results without a run snapshot fail with a clear error.
7. `matplotlib` is declared as a runtime package dependency.
8. Matplotlib imports are localized to the plotting implementation path.
9. Tests cover `bars=...`, `source=...`, no-fill behavior, returned figure type,
   timestamp conversion, literal labels/legend entries, and missing-snapshot
   error behavior.
10. Tests verify that plotting does not call `show()`, write files, reload a
    source after `engine.run(source=...)`, or mutate the result.
11. Tests verify that mutating original user-owned input data after the run
    cannot change the result snapshot or generated plot.
12. Tests verify that mismatched snapshot/equity/drawdown lengths raise a clear
    `ValueError` containing the mismatched series names and lengths.
13. Tests verify the drawdown formula, including flat/monotonically rising
    equity, zero or negative running peaks, and equity below zero after a
    positive running peak.
14. Tests verify that a flat or monotonically rising equity run produces an
    all-zero `drawdown_curve` and a visible `Drawdown` zero-line panel.
15. Tests verify that plotted drawdown renders as an underwater series while
    stored `drawdown_curve` values remain positive loss fractions.
16. Tests verify that empty plot data fails with a clear error and one-bar plot
    data produces a valid one-point figure.
17. Tests verify the no-downsampling beta target with 10,000 bars by asserting
    three axes and 10,000 retained x-points for close, equity, and drawdown.
18. Tests verify that `drawdown_curve` is populated and participates in
    `BacktestResult` equality for engine-produced result contracts.
19. Documentation and examples show `result.plot()` as the canonical plot path
    and do not show `result.plot(bars=...)` as a workaround.
20. Documentation shows notebook display, script display, and standard
    `fig.savefig(...)` usage without adding custom export helpers.

## Beta Positioning Rule

The project should not claim broad first-beta readiness only because this
plotting workflow and readable result reporting are implemented. Remaining
beta-positioning work includes fresh install guidance, constrained parameter
exploration, richer examples, release metadata/documentation cleanup, and
explicit unsupported-scope notes.
