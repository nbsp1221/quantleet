# Parameter Exploration Spec

## Status

- Status: `implemented`
- Class: `product-spec`
- Scope: first-beta constrained parameter exploration for single-symbol
  research backtests

Related documents:

- [research-ergonomics.md](research-ergonomics.md)
- [parameter-exploration-test-scenarios.md](parameter-exploration-test-scenarios.md)
- [backtest-mvp.md](backtest-mvp.md)
- [backtest-plotting.md](backtest-plotting.md)
- [data-ingestion.md](data-ingestion.md)
- [../design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)
- [../design-docs/quantleet-architecture.md](../design-docs/quantleet-architecture.md)
- [../research/2026-03-23-python-quant-library-landscape.md](../research/2026-03-23-python-quant-library-landscape.md)
- [../research/libraries/backtesting-py.md](../research/libraries/backtesting-py.md)

This document defines the product target for the first-beta research workflow:
comparing a finite set of strategy parameter combinations against the existing
single-symbol backtest and report surfaces.

This is a product spec, not an implementation plan. It defines what must be
true for the user experience and architecture. It intentionally leaves
lower-level helper names, storage internals, and execution mechanics to later
test scenario and technical implementation plans.

## Decision Summary

The first-beta user-facing model is a research-level study object:

- `quantleet.research.ParameterStudy` owns the parameter exploration UX.
- `ParameterStudy(...).grid_search(...)` is the first search method.
- `ParameterStudy` receives materialized `bars: BarSeries`; it does not accept
  `source=` in the first beta.
- The search objective is expressed as `objective=(metric_path, direction)`,
  where `direction` is `"max"` or `"min"`.
- `grid_search(...)` continues by default when an individual combination fails.
  Failed and constraint-rejected combinations remain visible as result rows.
- `fail_fast=True` is the debugging option for raising on the first failed
  combination.
- `grid_search(...)` uses a beta default `max_candidates=1000` safety limit
  against the raw cartesian grid size before constraint filtering. Larger grids
  require an explicit override such as `max_candidates=5000` or
  `max_candidates=None`.
- The beta keeps every successful engine-produced `BacktestResult` in memory so
  selected runs can be inspected without rerunning. This policy stays paired
  with the default `max_candidates=1000` guardrail.
- Report metrics may contain meaningful non-finite values such as
  `trades.profit_factor == math.inf`. Ranking and direct report inspection
  preserve those internal values, while simple record output uses JSON/CSV-safe
  metric state fields.
- Failed rows must expose `failure_stage`, `error_type`, and `error_message`.
  Tracebacks are not included in default structured records; users use
  `fail_fast=True` when they need the original stack trace.
- The beta does not introduce custom public exception classes for parameter
  exploration validation. Invalid values raise `ValueError`; invalid call
  shapes or invalid argument types raise `TypeError`; diagnostics must still be
  specific enough for notebook users and agents to fix the input.
- The first-beta result concept is `GridSearchResult`: a comparison artifact
  with rows, aggregate counts, selection helpers, and access to every successful
  run's `BacktestResult`.

This product deliberately avoids `BacktestEngine.optimize(...)` for beta. A
parameter study is a research workflow, while `BacktestEngine.run(...)` remains
the single historical execution entry point.

## Research Inputs

The product target is informed by existing Quantcraft contracts, local
inspection of cloned financial libraries under `/tmp`, and official public
documentation.

- `backtesting.py` provides a compact reference UX: `Backtest.optimize(...)`
  accepts parameter value sets, a constraint, an objective metric, and optional
  heatmap output. Its docs frame grid search as evaluating explicit parameter
  combinations and inspecting the resulting heatmap:
  [Backtest.optimize](https://www.mintlify.com/kernc/backtesting.py/concepts/backtest)
  and
  [Parameter Heatmap & Optimization](https://kernc.github.io/backtesting.py/doc/examples/Parameter%20Heatmap%20%26%20Optimization.html).
- Backtrader's `optstrategy(...)` is a useful reference for strategy
  parameter iteration and fresh strategy instantiation per run:
  [Cerebro optimization docs](https://www.backtrader.com/docu/cerebro/).
- QuantStats reinforces that research output should be structured,
  comparison-ready, and report-oriented, not only a selected "best" value.
- vectorbt and PyBroker show valuable later directions such as vectorized
  multi-parameter analytics and walk-forward analysis. Those are intentionally
  beyond the first-beta Quantcraft scope.

The library comparison should inform Quantcraft's UX bar without making any
competitor API shape the Quantcraft contract.

The approved Quantcraft UX borrows the useful parts of these precedents without
copying their ownership model:

- like `backtesting.py`, the beta supports finite grid search with constraints
  and explicit metric selection
- like scikit-learn and Ray Tune, the search returns a structured result object
  rather than only a best value
- like scikit-learn's `error_score`/raise split and Ray Tune's `fail_fast`
  controls, the beta keeps routine failed attempts inspectable while preserving
  an explicit raise path for debugging
- like Optuna, the result model treats individual attempted configurations as
  inspectable study outcomes
- unlike `backtesting.py`, the search method does not live on the backtest
  engine because Quantcraft keeps research experimentation separate from
  historical execution

The record-output contract is also shaped by Python and pandas serialization
behavior: Python can emit `Infinity` and `NaN` by default, but that is outside
strict JSON compliance, while pandas JSON output normalizes missing values to
`null`. Quantcraft therefore keeps meaningful non-finite metric values in the
internal report/ranking layer and uses explicit state fields in portable record
output.

## Background And Problem Definition

Quantcraft now has the core pieces needed for a credible first research loop:

- users can define a `Strategy`
- `BacktestEngine` can run the strategy on materialized `BarSeries` or a
  historical data source
- engine-produced `BacktestResult` values expose structured `result.report`
  data and basic `result.plot()` inspection
- market, limit, stop-market, stop-limit, and percentage-sizing order workflows
  exist in the current backtest/research scope

The missing product capability is not another order primitive. It is the
ability to compare strategy variants without writing ad hoc loops and custom
metric extraction every time.

Today, a user who wants to answer "which SMA window pair looks least bad on
this dataset?" must manually:

1. create many strategy variants
2. run the engine repeatedly
3. remember which parameters produced each result
4. extract metrics from each `BacktestReport`
5. sort, filter, and inspect the run they care about
6. avoid accidental state reuse across runs

That is a beta-blocking UX gap. Parameter exploration is the bridge between a
single impressive demo run and a useful research tool. Without it, users cannot
quickly compare strategies, and later examples will either hide loops in
notebooks or teach inconsistent patterns.

The problem is also architectural. Parameter exploration must compose the
existing research, backtest, and reporting surfaces. It must not create a second
execution engine, duplicate order semantics, or encode optimizer-specific
statistics outside `BacktestReport`.

## Goals

- Let a beta user define a small, finite parameter space and compare all
  admissible combinations through the normal historical backtest path.
- Make the natural output a comparison artifact, not just the single best run.
- Preserve a clear path from comparison rows back to the underlying successful
  run so users can inspect `result.report` and `result.plot()` for selected
  configurations.
- Make strategy identity, parameter values, run labels, execution assumptions,
  and selected metrics visible without parsing formatted text.
- Support explicit constraints such as `fast < slow`.
- Keep result ranking deliberate. Users should know which metric or objective
  they are ranking by, and the product should not imply that one metric proves a
  strategy is good.
- Protect users from accidental state leakage by requiring each attempted
  parameter combination to run with fresh strategy state.
- Keep the first beta scope small enough to implement and test well.
- Keep beta execution deterministic and sequential while preserving enough row
  identity for future bounded parallel execution.

## Non-Goals

The first-beta parameter exploration feature is not:

- a general-purpose optimizer
- Bayesian, SAMBO, genetic, or model-based optimization
- random search or adaptive sampling
- parallel execution controls such as `n_jobs`, `workers`, `parallel`, or
  custom executors
- persistence, resume, retry queues, result caching, or streaming result storage
- multi-objective, weighted-objective, or Pareto-front selection
- custom objective callables
- walk-forward analysis
- train/test splitting or out-of-sample validation
- anti-overfitting diagnostics
- heatmap plotting
- visual table rendering
- multi-symbol, multi-timeframe, portfolio, short, leverage, margin, paper, or
  live-trading support
- a replacement for `BacktestEngine`
- a second execution model with separate order semantics
- a pandas-first API requirement
- a promise that the top-ranked parameter combination is tradable

Some of these capabilities may become later product slices. They must not be
smuggled into the beta parameter exploration contract.

## User Intent

The primary user is a Python quant researcher or developer evaluating a
single-symbol strategy before deciding whether deeper work is justified.

They want to:

- try a finite set of parameter values without rewriting their strategy
- reject invalid combinations such as a fast moving average longer than the
  slow moving average
- compare headline return, risk, trade, cost, and exposure metrics side by side
- rank or filter the runs by an explicit metric
- inspect the selected run's report and plot
- understand when a combination failed versus merely performed poorly
- keep the workflow reproducible enough for notebooks, examples, and agents

They are not asking the library to discover a profitable strategy for them.
They are asking the library to make honest comparison easy.

## Canonical Beta UX

The first-beta workflow starts by materializing historical data once:

```python
from quantleet.backtest import BacktestEngine
from quantleet.data import DataFrameDataSource
from quantleet.research import ParameterStudy, ta
from quantleet.strategy import Strategy, StrategyConfig, StrategyConfigValidationError


class SmaConfig(StrategyConfig):
    fast: int = 5
    slow: int = 20

    def validate(self) -> None:
        if self.fast >= self.slow:
            raise StrategyConfigValidationError("fast must be less than slow")


class SmaCross(Strategy[SmaConfig]):
    @property
    def display_name(self) -> str:
        return "SMA Cross"

    def init(self) -> None:
        self.fast = ta.sma(self.data.close, length=self.config.fast)
        self.slow = ta.sma(self.data.close, length=self.config.slow)

    def on_bar(self, bar) -> None:
        if self.fast[-1] > self.slow[-1] and not self.position.is_open:
            self.buy(qty_percent=1.0)
        elif self.fast[-1] < self.slow[-1] and self.position.is_open:
            self.sell(qty_percent=1.0)


source = DataFrameDataSource(df, symbol="AAPL", timeframe="1d")
bars = source.load()

engine = BacktestEngine(initial_cash=10_000, costs=costs)

study = ParameterStudy(
    engine=engine,
    bars=bars,
    strategy=SmaCross,
)

results = study.grid_search(
    parameters={
        "fast": [5, 10, 20],
        "slow": [20, 50, 100],
    },
    constraint=lambda config: config["fast"] < config["slow"],
    objective=("returns.total_return", "max"),
)

records = results.to_records()
print(records[:5])

best = results.best()
print(best.strategy_config)
print(best.backtest.report)
fig = best.backtest.plot()
```

`ParameterStudy` can be reused for multiple searches over the same engine, bars,
and strategy class:

```python
coarse = study.grid_search(
    parameters={"fast": [5, 10, 20], "slow": [50, 100, 200]},
    constraint=lambda config: config["fast"] < config["slow"],
    objective=("returns.total_return", "max"),
)

fine = study.grid_search(
    parameters={"fast": [8, 10, 12], "slow": [80, 100, 120]},
    constraint=lambda config: config["fast"] < config["slow"],
    objective=("risk.max_drawdown", "min"),
)
```

Large grids must be deliberate:

```python
results = study.grid_search(
    parameters=large_parameter_grid,
    constraint=lambda config: config["fast"] < config["slow"],
    objective=("returns.total_return", "max"),
    max_candidates=5000,
)
```

The comparison artifact exposes records for notebooks, CLIs, CSV/dataframe
conversion, and agent inspection:

```python
records = results.to_records()
top_five = results.top(5)
failed = results.failed()
rejected = results.rejected()
```

## Core Requirements

1. Parameter exploration must operate over an explicit, finite parameter grid.
   Infinite generators, implicit ranges, and hidden search spaces are outside
   the first-beta contract.
2. The product must expose the count of candidate combinations before or during
   execution. In the first beta, this means preflight diagnostics for rejected
   over-limit grids plus aggregate counts on the returned `GridSearchResult`;
   it does not require a public progress callback, logging API, or pre-run
   dry-run API.
3. The first beta must reject raw cartesian grids above 1000 candidates by
   default, before constraint filtering, unless the user supplies an explicit
   `max_candidates` override.
4. Parameter enumeration must be deterministic for the same inputs. Candidate
   order follows the user-provided parameter mapping order, then each
   parameter's ordered candidate-value sequence. `run_index` is zero-based in
   that deterministic raw candidate order.
5. Each admissible run must use fresh strategy state. Reusing a mutated
   strategy instance across combinations is not acceptable.
6. The user must be able to express constraints over parameter combinations.
   Rejected combinations are not failed backtests and should be distinguishable
   from runtime failures.
7. All successful runs must produce metrics from the engine-produced
   `BacktestResult.report` structure. Parameter exploration must not parse
   `BacktestReport.to_text()` output.
8. The comparison output must retain parameter values, run identity, run
   status, and selected report metrics in a machine-readable shape.
9. Failed combinations must remain visible as failures by default. Silent
   omission makes comparisons misleading.
10. Undefined metrics, such as a Sharpe ratio on insufficient data or a win rate
   with no closed trades, must stay explicit as undefined values. They must not
   be converted into zero.
11. Ranking must be tied to an explicit objective expressed as
    `(metric_path, direction)`, where `direction` is `"max"` or `"min"`. The
    first beta must not silently declare a universal "best" strategy.
12. The comparison artifact must provide a documented way to get from a
    successful row to the corresponding backtest inspection path. The user
    should not have to rerun a selected configuration just to inspect its
    report or plot.
13. The feature must stay within the current single-symbol, single-timeframe,
    long-or-flat historical backtest scope.
14. `ParameterStudy` is the first-beta public study container. Additional search
    methods may be added later, but `BacktestEngine` must not become the
    research optimizer surface.

## Functional Requirements

### Parameter Space

- Users can provide one or more named parameters, each with a finite set of
  ordered candidate values.
- Parameter names are user-facing search-space labels backed by public
  `StrategyConfig` fields and must be preserved exactly in comparison output.
- Parameter names must be non-empty strings and must be declared public fields
  on the strategy's `StrategyConfig`. Unknown names, private names, dotted names
  that are not config fields, and names that are not valid config field
  declarations are invalid study definitions.
- Non-string parameter names are invalid because portable record output uses
  JSON-object-compatible parameter names.
- Empty parameter grids are valid and run one default-config candidate. Empty
  candidate value lists and unordered candidate containers such as `set` are
  invalid.
- Duplicate parameter combinations are invalid in beta. Duplicate values within
  a single parameter's candidate list must be rejected because they create
  ambiguous counts and row identities.
- Beta parameter grid values must be JSON scalar values: `str`, `int`, finite
  `float`, `bool`, or `None`.
- Beta parameter grid values must not be arbitrary objects, callables, classes,
  datetimes, decimals, enums, containers, `NaN`, or positive/negative infinity.
- Invalid parameter value errors must identify the parameter name, offending
  value, and value type clearly enough for notebook users and agents to fix the
  grid without guessing.
- `grid_search(...)` defaults to `max_candidates=1000`, measured against the
  raw cartesian product before constraint filtering.
- A grid whose raw cartesian size exceeds `max_candidates` must fail before
  running any backtests.
- Users can deliberately allow larger grids by passing a larger
  `max_candidates` value.
- Users can deliberately disable the safety limit with `max_candidates=None`.
  This is an explicit user choice and should not be the default beta behavior.
  Non-`None` `max_candidates` values must be positive integers; booleans,
  floats, strings, zero, and negative values are invalid.
- The first beta must not add a second resource envelope such as
  `candidate_count * bar_count`. The default `max_candidates=1000` guardrail and
  explicit user override are the product contract for beta.
- Passing `max_candidates=None` or a larger explicit limit means the user has
  deliberately accepted larger in-memory result retention. Documentation should
  say this plainly; beta does not add persistence or streaming storage to make
  large studies safe by default.

### Candidate Filtering

- Users can optionally provide a constraint that decides whether a parameter
  combination is admissible.
- Constraints receive the full materialized `strategy_config` mapping for the
  candidate being evaluated. Callback code must not be able to corrupt stored
  row identity or later callback inputs; implementations should satisfy this by
  passing an immutable mapping or a defensive copy.
- Constraint-rejected combinations must be represented as rejected rows, not
  only aggregate counts, so users can understand the explored space.
- If every combination is rejected, the user receives a clear diagnostic rather
  than an empty successful result. `grid_search(...)` returns an inspectable
  `GridSearchResult` containing the rejected rows, with zero successful rows and
  zero eligible rows for selection.
- If the constraint itself raises an error, the output must identify the
  affected combination and the constraint failure. By default this produces a
  failed row with a constraint-failure diagnostic; `fail_fast=True` raises on
  the first constraint exception.
- Constraint callables must return a real `bool`. Truthy or falsy non-boolean
  return values are invalid constraint outcomes; by default they produce a
  failed row with `failure_stage="constraint"`, and `fail_fast=True` raises.

### Run Execution

- `ParameterStudy` is constructed with an existing `BacktestEngine`,
  materialized `BarSeries`, and a `Strategy` class.
- Each admissible combination runs through the existing historical
  `BacktestEngine.run(bars=..., strategy=StrategyClass, config=...)` behavior.
- Reusing the same `BacktestEngine` object across a study must not leak
  per-run broker, order, strategy, report, or account state across candidate
  runs. The study may rely on `BacktestEngine.run(...)` only if that public run
  path provides run-scoped state isolation.
- The strategy class must be constructed once per admissible run with the
  materialized `StrategyConfig`. Reusing and resetting a previously mutated
  strategy instance is not sufficient because arbitrary user state may not be
  reset safely.
- The first-beta feature officially supports materialized `bars=...`.
- `ParameterStudy` must not accept `source=` in the first beta. Users should
  call `source.load()` once before constructing the study.
- A future `ParameterStudy.from_source(..., materialize="once")` style
  convenience constructor may be considered later, but it is not part of this
  beta contract.
- Run labels or run identifiers must be stable enough to trace a comparison row
  back to the exact parameter combination and underlying result.
- Beta P0 candidate execution is sequential. `grid_search(...)` must not expose
  public `n_jobs`, `workers`, `parallel`, or `executor` controls.
- Comparison rows must retain deterministic identity and ordering, such as a
  stable `run_index` tied to candidate enumeration, so future bounded parallel
  execution can preserve user-visible ordering.
- `grid_search(...)` defaults to `fail_fast=False`. Runtime failures produce
  failed rows; `fail_fast=True` raises on the first failed combination for
  debugging.
- In `fail_fast=True` mode, user-code failures re-raise the original exception
  type with the original traceback. The raised exception should include
  parameter and failure-stage context through a Python exception note or an
  equivalently visible standard diagnostic, without replacing it with a custom
  public Quantcraft exception type.
- Failed rows must identify the stage that failed. Beta stage labels are:
  - `"constraint"` for constraint callable failures
  - `"strategy_construction"` for strategy construction failures
  - `"backtest"` for failures during `BacktestEngine.run(...)`, strategy
    `init()`, or strategy `on_bar()` execution
  - `"metric_extraction"` for failures while resolving report metric paths
- `fail_fast=True` applies to all failed-row stages: `"constraint"`,
  `"strategy_construction"`, `"backtest"`, and `"metric_extraction"`.

### Objective And Selection

- `grid_search(...)` accepts an optional `objective=(metric_path, direction)`.
- The beta objective contract is single-objective. `objective` must be exactly
  one `(metric_path, direction)` tuple, not a list of objectives, a weighted
  objective expression, a Pareto-front request, or a callable.
- `metric_path` identifies a scalar metric from the structured report surface,
  such as `"returns.total_return"` or `"risk.max_drawdown"`.
- `direction` is `"max"` or `"min"`.
- Canonical beta objective examples are:
  - `("returns.total_return", "max")`
  - `("risk.max_drawdown", "min")`
  - `("risk.sharpe_ratio", "max")`
  - `("trades.profit_factor", "max")`
- The beta comparison metric path set is:
  - `"equity.final"`
  - `"returns.total_return"`
  - `"risk.max_drawdown"`
  - `"risk.sharpe_ratio"`
  - `"trades.closed_count"`
  - `"trades.win_rate"`
  - `"trades.profit_factor"`
  - `"costs.total_fees"`
  - `"exposure.ratio"`
  - `"execution.order_rejection_count"`
- Objective paths must be drawn from the beta comparison metric path set unless
  a later spec expands objective support. All beta comparison metric paths are
  valid objective paths. Unknown objective paths are input errors and must fail
  before any backtest runs.
- When an objective is supplied, result helpers such as `best()` and `top(n)`
  use it by default.
- When no objective is supplied, comparison records are still valid, but callers
  must provide an objective to `best(...)` or `top(...)`; otherwise selection
  helpers raise a clear diagnostic.
- Unknown objective paths, objective paths that resolve to non-scalar report
  values, and `top(n)` calls with `n <= 0` are invalid and must fail with clear
  diagnostics.
- Unknown or non-scalar objective paths are whole-search input errors, not
  per-row failures. They must fail before any backtest runs.
- The `"metric_extraction"` failed-row stage is reserved for unexpected
  per-row failures while extracting known comparison metrics from an
  engine-produced `BacktestResult`. It is not used for an invalid objective
  path supplied by the caller.
- Failed and rejected rows are never eligible for `best()` or `top(...)`.
- Rows with undefined objective values are not eligible unless a later design
  explicitly adds an undefined-value ranking policy.
- Rows with objective values that are meaningful non-finite numbers in the
  engine-produced report, such as `math.inf`, remain eligible for selection
  according to normal numeric ordering. Non-finite values that represent
  undefined metrics, such as `NaN`, are treated as undefined and are not
  eligible.
- If no row is eligible for selection, `best()` must raise a clear diagnostic
  and `top(n)` must return an empty sequence while leaving the full comparison
  artifact inspectable.
- If `n` exceeds the number of eligible rows, `top(n)` returns all eligible rows
  in objective order. It does not raise merely because fewer than `n` rows are
  eligible.
- Metric ties preserve deterministic row order. The first tied row by
  `run_index` is selected by `best()`, and `top(n)` preserves that order.

### Comparison Output

- The primary output is a `GridSearchResult` comparison artifact containing one
  row per raw candidate outcome.
- A row must distinguish at least these states:
  - rejected by constraint
  - successful backtest
  - failed before or during backtest execution
- Simple record output must include a top-level `status` field with exact beta
  values:
  - `"success"`
  - `"rejected"`
  - `"failed"`
- Successful rows must expose at least these beta comparison dimensions:
  - parameters
  - run label or run identifier
  - strategy identity
  - execution assumptions from the report manifest, such as symbol, timeframe,
    initial cash, and configured costs when those fields are available from the
    existing report surface
  - final equity
  - total return
  - max drawdown
  - Sharpe ratio
  - closed trade count
  - win rate
  - profit factor
  - total fees
  - exposure ratio
  - order rejection count
- Undefined metric values must remain explicit and machine-readable.
- Undefined metric values in structured records use `None`.
- Non-finite metric values that are meaningful, such as positive infinity for
  profit factor when there are winning closed trades and no losing closed
  trades, must not be collapsed into an undefined value internally.
- Direct `BacktestResult.report` inspection and selection/ranking preserve
  meaningful `math.inf` values.
- Simple record output, including `to_records()`, must be JSON/CSV-friendly:
  the metric value field uses `None` for non-finite values, and a companion
  metric-state field distinguishes the reason. For example,
  `trades.profit_factor` is `None` and `trades.profit_factor_state` is
  `"positive_infinity"` when the report value is `math.inf`.
- Simple records use dotted report metric paths as metric keys, for example
  `"returns.total_return"` and `"trades.profit_factor"`. Companion state fields
  append `_state` to the dotted metric key, for example
  `"returns.total_return_state"`.
- Every exported comparison metric in simple records must have a companion
  metric-state field, even when the metric is finite, so successful, failed, and
  rejected rows share a stable schema.
- Supported beta metric-state values are:
  - `"defined"` for finite scalar values
  - `"undefined"` for unavailable metrics represented as `None`, including
    report `None`, report `NaN`, and metrics that were not produced because a
    row was rejected or failed
  - `"positive_infinity"` for `math.inf`
  - `"negative_infinity"` for meaningful `-math.inf`
- The artifact must be convertible to simple records suitable for notebooks,
  CLI display, CSV/dataframe conversion, or agent inspection. The first beta
  should not require pandas as the only output shape.
- Candidate overrides must remain nested under `candidate_parameters`, and the
  full materialized config must remain nested under `strategy_config`, so user
  parameter names cannot collide with top-level row fields.
- `candidate_parameters` and `strategy_config` are the required nested config
  fields in simple records. Other top-level fields use stable string keys.
- Simple records must expose these non-metric fields with stable keys:

  | Key | Success | Rejected | Failed | Notes |
  | --- | --- | --- | --- | --- |
  | `run_index` | `int` | `int` | `int` | Zero-based raw candidate order. |
  | `status` | `"success"` | `"rejected"` | `"failed"` | Exact beta status enum. |
  | `candidate_parameters` | `dict[str, JSON scalar]` | `dict[str, JSON scalar]` | `dict[str, JSON scalar]` | Partial overrides from the search space. |
  | `strategy_config` | `dict[str, JSON scalar]` | `dict[str, JSON scalar]` | `dict[str, JSON scalar]` | Full materialized config snapshot. |
  | `run.label` | `str` or `None` | `None` | `None` | From `BacktestReport.run.run_label` when a result exists. |
  | `strategy.class_name` | `str` or `None` | `None` | `None` | From `BacktestReport.run.strategy_class_name`. |
  | `strategy.display_name` | `str` or `None` | `None` | `None` | From `BacktestReport.run.strategy_display_name`. |
  | `run.symbol` | `str` or `None` | `None` | `None` | From `BacktestReport.run.symbol`. |
  | `run.timeframe` | `str` or `None` | `None` | `None` | From `BacktestReport.run.timeframe`. |
  | `run.initial_cash` | finite `float` or `None` | `None` | `None` | From `BacktestReport.run.initial_cash`. |
  | `execution.model_name` | `str` or `None` | `None` | `None` | From `BacktestReport.execution.execution_model_name`. |
  | `rejection_stage` | `None` | stage `str` | `None` | `"strategy_config"` or `"constraint"` for rejected rows. |
  | `failure_stage` | `None` | `None` | stage `str` | One of the beta failure-stage labels. |
  | `error_type` | `None` | `str` or `None` | `str` | Exception class name when a rejection or failure has an error object. |
  | `error_message` | `None` | `str` or `None` | `str` | Human-readable rejection or failure message. |

  Every exported comparison metric key listed in the beta comparison metric
  path set must also appear in every record, paired with its `_state` key. Metric
  values are `None` for rejected and failed rows.
- Structured table-like data output is in scope; a first-party visual table
  renderer is not part of beta P0.
- The artifact should keep ranking, filtering, and selection understandable.
  Users should be able to ask for the top configurations by an explicit metric
  and then inspect a selected run.
- The artifact must expose aggregate counts for candidate, rejected,
  successful, failed, and eligible rows.
- Count invariants:
  - `candidate_count == rejected_count + successful_count + failed_count`
  - `eligible_count` is objective-dependent
  - when an objective is available, `eligible_count` is the number of successful
    rows with a defined or meaningful non-finite objective value
  - when no objective is available, `eligible_count` is zero until a selection
    helper is called with an explicit objective
- Failed rows must include enough diagnostic information for debugging:
  parameter values, `failure_stage`, `error_type`, and `error_message`.
- `error_type` is the exception class name, such as `"ValueError"`.
- Default structured records must not include tracebacks, exception cause
  chains, or local traceback paths. Users who need the original stack trace use
  `fail_fast=True` to reproduce the failing combination in raise mode.
- Simple records should keep a stable row shape. Diagnostic fields may be
  present with `None` values for successful and rejected rows, but rejected rows
  are not failures and must not receive a fake `failure_stage`.

### Inspection Path

- A user must be able to inspect the selected successful run's report through
  the normal `BacktestResult.report` path.
- A user must be able to plot a selected successful run through the normal
  `BacktestResult.plot()` path when plotting dependencies are available.
- Beta P0 does not include a `GridSearchResult` heatmap, pairwise parameter
  surface plot, dashboard, or visual table renderer.
- Every successful row must retain its corresponding engine-produced
  `BacktestResult` in the first beta. Beta P0 storage is in-memory only and
  intentionally does not include persistence, resume, retry queues, result
  caching, or streaming result storage.
- This in-memory retention policy is deliberate for beta and is scoped by the
  default `max_candidates=1000` guardrail. Larger in-memory studies are allowed
  only through explicit user override.
- Rejected and failed rows must not expose fake reports or fake plots.
- A `"metric_extraction"` failed row is still a failed comparison row and is
  not eligible for normal selected-run helpers. The beta contract does not
  require failed rows to expose the underlying `BacktestResult`, even if an
  engine-produced result existed before metric extraction failed.
- The comparison artifact must not require users to reconstruct hidden engine
  inputs just to understand a row.

### Documentation And Examples

- The first beta must include a canonical `ParameterStudy(...).grid_search(...)`
  example that compares a small moving average strategy grid with a
  `fast < slow` style constraint.
- The example must show comparison output first, then selected-run report or
  plot inspection.
- The example must call out that grid results are research diagnostics, not
  trading recommendations.
- The official canonical example is a beta-release documentation requirement.
  Technical feature completion does not require executing a docs example or
  notebook as P0; P0 coverage for the same workflow belongs in integration
  tests. Executing the official example or notebook is a P1 docs-release
  guardrail once that artifact exists.
- The docs must avoid naming the feature as a broad optimizer unless the
  implementation actually provides optimizer semantics beyond explicit grid
  comparison.

## Nonfunctional Requirements

- Determinism: Given the same bars, engine settings, strategy class, parameter
  grid, and constraint, exploration order and successful run metrics should be
  reproducible. Beta P0 execution is sequential, and result row identity must
  not depend on runtime scheduling.
- Architectural fit: The feature should belong to the research/experiment UX
  layer while composing `BacktestEngine` and `BacktestResult`. It must not
  weaken `trading` or duplicate execution semantics.
- Data clarity: The first beta should run against materialized `BarSeries`
  values so repeated runs use one explicit historical dataset.
- Transparency: Users must see candidate counts, rejected counts, successful
  counts, failure counts, and objective-dependent eligible counts.
- Failure hygiene: Runtime failures must include enough parameter context to
  debug the run and must identify the failure stage, exception type, and
  exception message without emitting full tracebacks into default structured
  records.
- Validation hygiene: Public validation failures use standard Python exception
  classes in beta. Use `ValueError` for invalid values and `TypeError` for
  invalid argument types or call shapes; do not add a custom public exception
  hierarchy for the first beta.
- Performance realism: The first beta should be efficient for small grids and
  honest about larger grids. It should reject grids above 1000 raw cartesian
  candidates by default unless explicitly overridden, and it should not imply
  vectorbt-scale vectorized parameter analysis or parallel optimization.
- Serialization clarity: Portable record output should avoid non-standard JSON
  float tokens such as `Infinity` or `NaN`; non-finite report metrics need
  explicit metric-state fields instead.
- Dependency restraint: The feature should not introduce a heavy optimization
  dependency for the first beta.
- Notebook friendliness: Outputs should be stable, readable, and convertible
  without forcing a display-only representation.
- Agent friendliness: Outputs should be structured enough for agents to inspect
  and compare without scraping prose.
- Security and scope: The feature must not require live credentials, live
  trading permissions, external network access beyond user-selected historical
  data loading, or non-repo workflow expansion.
- Reliability: Runtime-sensitive implementation work that changes research or
  backtest execution paths must use the runtime verification lane defined in
  `docs/RELIABILITY.md`.

## Major Scenarios

### 1. Compare A Small Moving Average Grid

A user defines a moving average crossover strategy with `fast` and `slow`
parameters. They provide finite candidate values, run exploration on one
materialized `BarSeries`, and receive a comparison artifact with one row per
candidate outcome.

The user can select by an explicit objective and inspect the selected run's
`BacktestResult.report`.

### 2. Filter Invalid Parameter Combinations

A user provides `fast=[5, 10, 20]` and `slow=[10, 20, 50]` with a `fast < slow`
constraint. The comparison artifact makes it clear how many combinations were
candidate, how many were rejected by the constraint, and how many were actually
backtested.

### 3. Compare Risk, Not Only Return

A user ranks by total return but also sees max drawdown, exposure, order
rejection count, and trade count. A high-return row with severe drawdown or very
few trades is visibly different from a more stable row.

### 4. Inspect The Selected Run

After selecting a successful row, the user can inspect the normal report and
plot path for that exact run. The selected run is not a separate kind of
artifact with different semantics.

### 5. Handle A No-Trade Configuration

Some parameter combinations produce no closed trades. Those rows remain valid
successful runs, but trade-derived metrics such as win rate or profit factor are
undefined rather than zero.

### 6. Keep Runtime Failures Visible

One parameter combination causes strategy construction or `on_bar()` logic to
raise. The comparison artifact identifies the failed combination and continues
by default. When debugging, the user can pass `fail_fast=True` to raise on the
first failed combination.

### 7. Materialize Source-Backed Data Deliberately

A user wants to run exploration from a historical data source. The user calls
`source.load()` once, then passes the resulting `BarSeries` into
`ParameterStudy`. Hidden repeated source loads are not part of the beta UX.

## Edge Cases And Failure Scenarios

- The parameter grid is empty.
- A parameter has no candidate values.
- Candidate values are duplicated.
- Candidate values are provided in unordered containers such as `set`.
- Candidate values are not safely representable in output.
- Candidate values are non-JSON-scalar values, such as objects, callables,
  datetimes, decimals, enums, containers, `NaN`, or infinities.
- Parameter names collide with reserved comparison row fields.
- The full cartesian product is unexpectedly large.
- The raw cartesian product exceeds `max_candidates`.
- The constraint rejects every combination.
- The constraint raises for one combination.
- Strategy construction raises for one combination.
- `init()` or `on_bar()` raises during one run.
- `source.load()` fails before the user constructs `ParameterStudy`; this is
  governed by data-ingestion/source contracts, not by `ParameterStudy`.
- A run succeeds but contains order rejections.
- A run succeeds with no fills or no closed trades.
- A run succeeds with an open final position.
- A run produces undefined annualized or risk metrics.
- A run produces a meaningful non-finite trade metric such as
  `trades.profit_factor == math.inf`.
- Two parameter combinations produce identical metric values.
- The selected ranking metric is missing or undefined for some rows.
- The selected ranking metric has mixed numeric and undefined values.
- A manually constructed result without an engine report appears in a row.
- `ParameterStudy` is constructed with a data source instead of materialized
  bars.
- A user attempts to use multi-symbol, multi-timeframe, shorting, leverage,
  paper, or live execution with this first-beta workflow.

## External Contracts

Parameter exploration depends on, and must not redefine, these existing
contracts:

- `quantleet.strategy.Strategy` is the canonical user-facing strategy subclass
  surface.
- `quantleet.research.Strategy` remains a compatibility re-export until the
  migration path is removed by a later spec.
- `Strategy.display_name` is human-readable strategy identity metadata.
- Reportable execution config comes from the materialized `StrategyConfig`
  snapshot.
- `BacktestEngine.run(...)` is the current historical execution entry point.
- `bars` must be a `quantleet.data.BarSeries`.
- `source.load()` returns a `BarSeries`, but `ParameterStudy` itself receives
  `bars`, not `source`, in the first beta.
- Engine-produced `BacktestResult` exposes structured `result.report`.
- Engine-produced reports may contain meaningful non-finite Python float values
  such as `math.inf`; parameter exploration preserves those for direct report
  inspection and ranking while normalizing portable record output.
- `BacktestReport` exposes grouped return, risk, trade, cost, exposure,
  execution, and run-manifest data.
- `BacktestResult.plot()` is the first-beta visual inspection path for one
  successful run.
- Current order semantics are governed by the backtest, order sizing,
  reservation, and stop-limit specs. Parameter exploration must not reinterpret
  market, limit, stop-market, stop-limit, or `qty_percent` behavior.
- The current beta execution scope remains single-symbol, single-timeframe,
  historical, long-or-flat, and non-live.
- Tier A `trading` and `execution` work requires explicit human approval before
  implementation can be treated as approved.

The new planned public contract introduced by this spec is
`quantleet.research.ParameterStudy` as the first-beta parameter exploration
study container.

## Success Conditions

The product feature is beta-ready when:

- a user can compare a small finite strategy parameter grid without writing
  custom backtest loops
- the public beta workflow uses `ParameterStudy(...).grid_search(...)`
- the study input is a materialized `BarSeries`
- invalid combinations can be filtered by explicit constraints
- successful, rejected, and failed outcomes are distinguishable
- failed outcomes are retained by default and `fail_fast=True` exists for
  debugging
- comparison rows expose parameter values and report-derived metrics in a
  structured form
- the user can inspect the report and plot for any successful run
- beta P0 provides structured comparison output, not heatmap or visual table
  rendering
- selection uses an explicit objective tuple such as
  `("returns.total_return", "max")`
- the beta objective contract is single-objective only
- undefined metrics are represented honestly
- meaningful non-finite metrics are preserved internally and represented with
  explicit JSON/CSV-safe metric state in structured records
- candidate counts and failure counts are visible
- grids above 1000 raw cartesian candidates require explicit user override
- the implementation composes existing `research`, `backtest`, and `reporting`
  surfaces instead of creating parallel execution semantics
- candidate execution is sequential in beta P0, with deterministic row identity
  that can support future bounded parallel execution
- parameter grid values are restricted to JSON scalar values
- beta result storage is in-memory only
- failed rows include `failure_stage`, `error_type`, and `error_message`, and
  default record output excludes tracebacks
- official docs include a canonical constrained-grid example
- the feature does not require live credentials, paper/live execution, external
  optimizers, or pandas-only output

## Implementation Status

The first-beta parameter exploration surface is implemented in
`quantleet.research.ParameterStudy`. Grid results are research diagnostics, not
trading recommendations.

## Follow-Up Product Artifacts

The product decisions in this spec are closed for the beta parameter
exploration slice. The dedicated test-scenario contract is
[parameter-exploration-test-scenarios.md](parameter-exploration-test-scenarios.md).
Technical implementation planning should use both documents as source of
truth.
