# Parameter Exploration Test Scenarios

## Status

- Status: `planned`
- Class: `product-spec`
- Scope: first-beta `ParameterStudy(...).grid_search(...)` test scenarios

Related documents:

- [parameter-exploration.md](parameter-exploration.md)
- [research-ergonomics.md](research-ergonomics.md)
- [backtest-mvp.md](backtest-mvp.md)
- [backtest-plotting.md](backtest-plotting.md)
- [backtest-plotting-test-scenarios.md](backtest-plotting-test-scenarios.md)
- [../RELIABILITY.md](../RELIABILITY.md)
- [../SECURITY.md](../SECURITY.md)
- [../design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)

This document turns the product intent in
[parameter-exploration.md](parameter-exploration.md) into a test scenario
contract. It does not define implementation internals. Tests derived from this
document should prove the public beta behavior of parameter exploration through
observable contracts.

## Testing Basis

The first-beta feature exists so a single-symbol research user can compare a
small, finite strategy parameter grid without writing custom backtest loops.
The core contract is:

- `quantleet.research.ParameterStudy` is the public research study container.
- `ParameterStudy(...).grid_search(...)` accepts finite ordered parameter
  values, an optional constraint, an optional single objective, and a beta
  candidate-count guardrail.
- The study receives materialized `bars: BarSeries`; it does not accept
  `source=` in beta.
- Each admissible combination runs through the existing `BacktestEngine`
  historical execution path with fresh strategy state.
- The result is a `GridSearchResult` comparison artifact, not only a best run.
- Successful, rejected, and failed candidate outcomes remain distinguishable.
- Selection uses one explicit objective tuple and must be deterministic.
- Simple record output is stable and portable, including explicit metric-state
  fields for undefined and non-finite metrics.
- Every successful row retains its engine-produced `BacktestResult` for report
  and plot inspection.

Tests must therefore validate the comparison and inspection contract, not
whether an explored strategy is profitable.

## Testing Philosophy

Tests are long-lived product assets. A refactor of internal enumeration,
storage, or helper names should not require changing tests unless the external
contract changes.

Operational rules:

1. Test behaviors and contracts, not private methods. Google Testing Blog and
   *Software Engineering at Google* both recommend behavior-focused tests over
   method-mirroring tests because one method can expose many user-visible
   behaviors:
   [Testing on the Toilet: Test Behaviors, Not Methods](https://testing.googleblog.com/2014/04/testing-on-toilet-test-behaviors-not.html),
   [Software Engineering at Google, Chapter 12](https://abseil.io/resources/swe-book/html/ch12.html).
2. Keep each test complete and concise. Inputs and expected outputs should be
   visible enough that a human or agent can diagnose a failure without
   re-reading production internals.
3. Use a layered suite. Fast unit tests should cover validation, ranking, and
   record-shape rules; narrow integration tests should prove the public study
   workflow composes with real `BacktestEngine`, `Strategy`, `BarSeries`,
   `BacktestReport`, and `BacktestResult` contracts. This follows the test
   pyramid and narrow integration guidance:
   [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html).
4. Prefer real Quantcraft objects at module boundaries. Use fakes only where
   the test is explicitly about boundary interaction, such as proving no
   backtests run after preflight validation fails. Test doubles must be
   contract-shaped and small.
5. Keep tests in the existing repository test taxonomy. Pytest recommends
   tests outside application code and import modes that avoid surprising path
   behavior; Quantcraft already uses `src/`, `tests/`, and
   `--import-mode=importlib`:
   [pytest Good Integration Practices](https://docs.pytest.org/en/latest/explanation/goodpractices.html).
6. Treat new integration failures as design feedback. If an integration test
   exposes a bug that lower-level tests cannot localize, add or refine a
   lower-level contract test before closing the implementation slice.

## Test Scope

In scope:

- parameter grid validation and deterministic enumeration
- raw cartesian candidate counting and `max_candidates` behavior
- constraint filtering, constraint failures, and all-rejected grids
- strategy class construction behavior and fresh strategy state per admissible run
- composition with real `BacktestEngine.run(bars=..., strategy=StrategyClass, config=...)`
- rejected, successful, and failed row contracts
- single-objective validation, ranking, ties, `best()`, and `top(n)`
- undefined, `NaN`, and meaningful infinity metric handling
- `to_records()` shape and JSON/CSV-safe metric-state fields
- selected-run `BacktestResult.report` and `BacktestResult.plot()` access path
- public import, docs, and package-boundary checks for the research surface

Out of scope:

- proving market, limit, stop-market, stop-limit, or `qty_percent` execution
  semantics from scratch; those stay governed by the existing backtest and
  order specs
- profitability or statistical validity of selected parameters
- multi-objective, weighted-objective, Pareto, random, Bayesian, SAMBO, or
  walk-forward optimization
- public parallelism controls, persistence, resume, retry queues, caching, or
  streaming storage
- `GridSearchResult` heatmaps, pairwise plots, dashboards, or visual table
  rendering
- live, paper, multi-symbol, multi-timeframe, short, leverage, or margin flows
- pandas-only output requirements
- testing private helper names or exact storage layout

## Proposed Test Placement

| Layer | Proposed location | Purpose |
| --- | --- | --- |
| Unit | `tests/unit/research/test_parameter_grid_validation.py` | Finite ordered grid validation, JSON-scalar value policy, candidate counting, and deterministic enumeration. |
| Unit | `tests/unit/research/test_parameter_study_preflight.py` | Public call-shape validation, materialized-bars requirement, `max_candidates`, objective validation, and no-run preflight failures. |
| Unit | `tests/unit/research/test_grid_search_result_selection.py` | `best()`, `top(n)`, eligibility, ties, missing objectives, and non-finite ranking behavior. |
| Unit | `tests/unit/research/test_grid_search_records.py` | Stable simple-record shape, nested candidate/config snapshots, metric-state fields, and failure diagnostics. |
| Integration | `tests/integration/research/test_parameter_study_grid_search.py` | Real `ParameterStudy` plus `BacktestEngine` finite-grid workflows over deterministic `BarSeries`. |
| Integration | `tests/integration/research/test_parameter_study_failures.py` | Constraint, strategy construction, backtest, and metric-extraction failure behavior with real public workflows where practical. |
| Integration | `tests/integration/research/test_parameter_study_selected_run.py` | Selected-row access to normal `BacktestResult.report` and `BacktestResult.plot()`. |
| Smoke | `tests/smoke/local/test_public_imports.py` | `ParameterStudy` remains importable from `quantleet.research`. |
| Structure | `tests/structure/architecture/test_parameter_exploration_boundaries.py` | Research owns study UX, composes public backtest surface, and does not add Tier A or optimizer dependency drift. |
| Docs | `tests/structure/docs/test_parameter_exploration_docs.py` | Product docs and examples keep the canonical beta workflow and avoid out-of-scope optimizer claims. |
| Notebook or example validation | existing notebook/example validation lane, if an example is added | The canonical constrained-grid example runs without hidden setup. |

No browser-style E2E tests are required for beta because the feature is a
library workflow with no UI. The closest end-to-end coverage should be a local
smoke or notebook/example validation that exercises the documented import and
canonical example path. That docs/example validation is a P1 docs-release
guardrail, not a P0 feature-completion gate. P0 coverage for the canonical user
workflow belongs in integration tests that exercise the same public API flow.

## Test Data And Fixture Strategy

Use small, deterministic fixtures whose expected behavior is easy to inspect.
Avoid large market fixtures unless the test specifically needs an existing
regression data shape.

| Fixture | Shape | Purpose |
| --- | --- | --- |
| `small_rising_bars` | 6 to 12 bars with rising closes | deterministic no-drawdown or simple long-only runs. |
| `crossing_bars` | enough bars for short moving averages to cross | canonical SMA-style comparison example. |
| `no_trade_bars` | bars that keep a simple strategy flat | undefined trade-derived metric scenarios. |
| `drawdown_bars` | rise, fall, partial recovery | nonzero risk metric comparison. |
| `two_trade_bars` | deterministic win/loss outcomes | finite profit factor and win-rate assertions. |
| `profit_factor_infinite_report` | minimal result/report object or real run that produces wins and no losses | meaningful `math.inf` ranking and record-state behavior. |
| `fake_counting_engine` | contract-shaped fake with `run(...)` call log | prove preflight failures do not run backtests and admissible runs call the engine once. |
| `raising_strategy_construction` | strategy constructor that raises for one parameter value | `strategy_construction` failure rows and `fail_fast=True`. |
| `raising_strategy` | strategy whose `init()` or `on_bar()` raises for one parameter value | `backtest` failure rows and continue-by-default behavior. |
| `constraint_raises` | constraint that raises for one combination | constraint failure rows and `fail_fast=True`. |
| `constraint_returns_non_bool` | constraint returning `1`, `0`, `None`, or `"yes"` | invalid constraint outcome behavior. |

Fixture rules:

- Expected values should be explicit in the test body or fixture docstring.
- Helpers may build `BarSeries`, but must not hide the behavior under test.
- Do not reimplement the production grid enumeration or ranking algorithm in
  test helpers.
- Use real `BacktestEngine` integration fixtures for cross-module confidence.
- Use fakes only for preflight, call-count, and hard-to-trigger metric
  extraction boundaries.

## Mock, Stub, And Fake Policy

Prefer real objects when validating public Quantcraft contracts:

- use real `BarSeries` and `TimeBar` values
- use real `Strategy` subclasses for integration workflows
- use real `BacktestEngine` for successful run, backtest failure, report, and
  selected-run inspection scenarios
- use real `BacktestResult.report` metrics when the scenario depends on
  report/backtest integration

Allowed fakes:

- a fake engine with a public `run(...)`-shaped method for preflight tests that
  must prove no backtests start
- a minimal contract-shaped result/report only when a specific metric state
  cannot be generated cheaply through a real backtest
- a fake plotting dependency only to prove selected-run inspection calls the
  normal `BacktestResult.plot()` path without asserting Matplotlib internals

Avoid:

- mocking private helper calls
- asserting implementation-specific storage fields
- patching cartesian-product helpers
- replacing `BacktestEngine` in tests whose purpose is real integration
- interaction assertions when a state/output assertion can prove the contract

## Unit Scenarios

### U1: Parameter Grid Validation

Purpose: prevent ambiguous or unserializable search spaces before any backtest
runs.

Scenarios:

| Case | Input | Expected behavior |
| --- | --- | --- |
| one parameter | `{"fast": [5, 10]}` | accepted, two candidates. |
| multiple ordered parameters | `{"fast": [5, 10], "slow": [20, 50]}` | deterministic cartesian rows in documented order. |
| empty grid | `{}` | accepted as one default-config candidate. |
| non-string parameter name | `{1: [5]}` | invalid and identifies the key type. |
| empty parameter name | `{"": [5]}` | invalid and identifies the empty name. |
| unknown parameter name | `{"missing": [5]}` | invalid before any backtest because the key is not a public `StrategyConfig` field. |
| private parameter name | `{"_fast": [5]}` | invalid before any backtest because private config fields are not public search-space fields. |
| dotted parameter name | `{"fast.length": [5]}` | invalid unless it is a declared public config field, which normal `StrategyConfig` declarations do not support. |
| reserved-looking parameter name | `{"status": [5]}` | accepted only when `status` is a declared public config field and remains nested under `candidate_parameters` and `strategy_config`. |
| empty value list | `{"fast": []}` | invalid and names `fast`. |
| unordered values | `{"fast": {5, 10}}` | invalid because row identity would be unstable. |
| duplicate values | `{"fast": [5, 5]}` | invalid because candidate identity is ambiguous. |
| supported scalar values | `str`, `int`, finite `float`, `bool`, `None` | accepted as parameter values. |
| unsupported values | object, callable, class, datetime, decimal, enum, container, `NaN`, `inf`, `-inf` | invalid and message names parameter, value, and type. |

Required assertions:

- validation happens before strategy construction or engine calls
- invalid values raise `ValueError`; invalid argument types or call shapes raise
  `TypeError`
- parameter names remain exact user-facing config field names in accepted
  candidate rows
- candidate overrides remain nested under `candidate_parameters` and full
  config snapshots remain nested under `strategy_config` in exported records
- top-level record fields remain intact when parameter names match fields such
  as `status`, `run_index`, `candidate_parameters`, `strategy_config`, or
  `error_type`

### U2: Raw Candidate Limit

Purpose: ensure large searches are deliberate and counted before constraints.

Scenarios:

- a grid with exactly 1000 raw combinations is accepted by default
- a grid with 1001 raw combinations fails before any backtest runs
- a grid with 1001 raw combinations and a constraint that would reject most
  rows still fails because counting is raw cartesian count before filtering
- `max_candidates=5000` allows a larger grid
- `max_candidates=None` disables the safety limit
- invalid `max_candidates` values, including `True`, `False`, `0`, `-1`,
  `1.5`, and `"1000"`, fail clearly

Required assertions:

- failure diagnostics include raw candidate count and configured limit
- invalid `max_candidates` values use `ValueError` for invalid values and
  `TypeError` for invalid types
- no strategy construction or engine call occurs on limit failure

### U3: Constraint Outcomes

Purpose: distinguish user-filtered combinations from failed backtests.

Scenarios:

- `constraint=lambda p: p["fast"] < p["slow"]` produces both successful and
  rejected rows
- every combination rejected returns an inspectable `GridSearchResult` with
  zero successful rows and zero eligible rows
- a constraint exception produces a failed row with
  `failure_stage="constraint"` by default
- the same constraint exception raises with `fail_fast=True`
- truthy/falsy non-boolean constraint returns are invalid outcomes and produce
  constraint failed rows by default
- `fail_fast=True` raises on non-boolean constraint returns
- a constraint that attempts to mutate its received full `strategy_config`
  mapping cannot corrupt stored row identity or later callback inputs

Required assertions:

- rejected rows are not failed rows
- rejected rows do not receive fake `failure_stage`
- candidate, rejected, successful, failed, and eligible counts are visible and
  internally consistent

### U4: Objective Validation

Purpose: keep ranking deliberate and single-objective in beta.

Scenarios:

- accepted objectives include the full beta comparison metric path set, with
  first-class examples:
  - `("equity.final", "max")`
  - `("returns.total_return", "max")`
  - `("risk.max_drawdown", "min")`
  - `("trades.closed_count", "max")`
  - `("trades.win_rate", "max")`
  - `("risk.sharpe_ratio", "max")`
  - `("trades.profit_factor", "max")`
  - `("costs.total_fees", "min")`
  - `("exposure.ratio", "max")`
  - `("execution.order_rejection_count", "min")`
- missing objective allows records but makes `best()` and `top(n)` without an
  objective raise clear diagnostics
- invalid direction fails for values other than `"max"` or `"min"`
- multi-objective lists, weighted expressions, Pareto requests, and callables
  are invalid
- unknown objective paths and non-scalar objective paths fail as whole-search
  input errors before any strategy construction or engine calls

Required assertions:

- invalid objective errors do not become per-row `metric_extraction` failures
- tests do not imply a universal default ranking metric

### U5: Selection Helpers

Purpose: prove `GridSearchResult` ranking is deterministic and honest about
eligibility.

Scenarios:

- `best()` returns the highest eligible row for `"max"`
- `best()` returns the lowest eligible row for `"min"`
- `top(n)` returns eligible rows in objective order
- `top(n)` returns all eligible rows when `n` exceeds the eligible row count
- `top(n)` rejects `n <= 0`
- failed and rejected rows are never eligible
- undefined objective values are not eligible
- `NaN` objective values are treated as undefined and ineligible
- meaningful `math.inf` and `-math.inf` objective values are eligible and sort
  by normal numeric ordering
- ties preserve `run_index`; `best()` selects the first tied row
- no eligible rows makes `best()` raise and `top(n)` return an empty sequence
  while preserving the inspectable artifact

Required assertions:

- returned selected rows expose `candidate_parameters`, `strategy_config`, and
  their retained `BacktestResult`
  when successful
- selection tests do not depend on private sorting helpers

### U6: Failed Row Diagnostics

Purpose: keep failure handling debuggable without leaking traceback details into
default records.

Scenarios:

- strategy construction raises for one combination
- real strategy `init()` raises for one combination
- real strategy `on_bar()` raises for one combination
- metric extraction unexpectedly fails for a known comparison metric
- each default failure path continues to later combinations
- `fail_fast=True` raises on the first failed-row stage:
  `"constraint"`, `"strategy_construction"`, `"backtest"`, or
  `"metric_extraction"`

Required assertions:

- failed rows include `candidate_parameters`, `strategy_config`,
  `failure_stage`, `error_type`, and
  `error_message`
- `error_type` is the exception class name, such as `"ValueError"`
- default records do not include traceback, cause chains, or local traceback
  paths
- failed rows do not expose fake reports or fake plots
- `metric_extraction` failed rows are not eligible and are not required to
  expose the underlying `BacktestResult` through normal selected-run helpers

### U7: Record Output Shape

Purpose: make comparison output stable for notebooks, CLIs, CSV/dataframe
conversion, and agents.

Scenarios:

- one record exists for every raw candidate outcome
- successful, rejected, and failed rows share a stable top-level shape
- every record includes a top-level `status` value of `"success"`,
  `"rejected"`, or `"failed"`
- candidate overrides are nested under `candidate_parameters`
- full materialized configs are nested under `strategy_config`
- `candidate_parameters` and `strategy_config` are the required nested config
  fields
- non-metric fields use the product-spec record keys and row-state nullability:
  `run_index`, `status`, `candidate_parameters`, `strategy_config`, `run.label`, `strategy.class_name`,
  `strategy.display_name`, `run.symbol`, `run.timeframe`, `run.initial_cash`,
  `execution.model_name`, `rejection_stage`, `failure_stage`, `error_type`,
  and `error_message`
- metric keys use dotted report paths such as `"returns.total_return"`
- companion metric-state fields append `_state`, such as
  `"returns.total_return_state"`
- successful rows include beta comparison dimensions:
  strategy identity, run identity, execution assumptions, final equity, total
  return, max drawdown, Sharpe ratio, closed trade count, win rate, profit
  factor, total fees, exposure ratio, and order rejection count
- every exported comparison metric has a companion metric-state field
- finite metric state is `"defined"`
- missing, report `None`, report `NaN`, rejected-row metrics, and failed-row
  metrics are `None` with state `"undefined"`
- report `math.inf` is represented as metric value `None` and state
  `"positive_infinity"` in simple records
- meaningful report `-math.inf` is represented as metric value `None` and state
  `"negative_infinity"` in simple records

Required assertions:

- portable records do not emit non-standard `Infinity`, `-Infinity`, or `NaN`
  float tokens
- direct report inspection and ranking preserve meaningful infinity internally

### U8: Study Construction And Public Call Shape

Purpose: protect the beta UX from accepting deferred-scope shortcuts.

Scenarios:

- constructing `ParameterStudy(engine=..., bars=..., strategy=StrategyClass)`
  succeeds with materialized `BarSeries`
- passing `source=` to `ParameterStudy` or `grid_search(...)` is not accepted
  in beta
- public `grid_search(...)` does not expose `n_jobs`, `workers`, `parallel`, or
  `executor`
- public API does not require pandas objects

Required assertions:

- failures use clear call-shape or validation diagnostics
- call-shape and invalid argument-type failures use `TypeError`
- tests verify public signatures or public errors, not private constructor
  storage

## Integration Scenarios

### I1: Canonical Small Grid Search

Purpose: prove the documented beta workflow works through real public surfaces.

Flow:

1. build deterministic `crossing_bars`
2. construct `BacktestEngine(initial_cash=...)`
3. define an SMA-style `Strategy` subclass with `fast` and `slow`
4. construct `ParameterStudy(engine=engine, bars=bars, strategy=StrategyClass)`
5. call `grid_search(parameters=..., constraint=..., objective=...)`

Required assertions:

- raw candidate, rejected, successful, and failed counts match explicit
  expectations
- all admissible combinations produce successful rows
- row order and `run_index` are deterministic
- `to_records()` includes comparison metrics and metric-state fields
- `best()` returns a successful selected row with matching `strategy_config`

### I2: Fresh Strategy State Per Run

Purpose: prevent strategy and engine run-state leakage across candidate runs.

Flow:

1. strategy class increments instance-local state during `init()` and
   `on_bar()`
2. run at least two admissible combinations
3. inspect per-row strategy metadata or output behavior that would differ if
   an instance were reused

Required assertions:

- strategy class is constructed once per admissible run
- no mutated strategy instance is reused across combinations
- no broker, order, report, account, or strategy runtime state leaks through a
  reused `BacktestEngine` object across candidate runs
- rejected rows do not construct the strategy

### I3: Continue By Default On Mixed Failures

Purpose: prove routine failures remain visible without aborting the whole study.

Flow:

1. define a grid with one normal combination, one strategy-construction failure, and
   one backtest runtime failure
2. run with default `fail_fast=False`

Required assertions:

- result contains successful and failed rows
- each failed row identifies the correct `failure_stage`
- later combinations still run after an earlier failure
- `failed()` returns the failed rows without hiding successful rows

### I4: Fail Fast Debugging Mode

Purpose: prove the explicit debugging path raises instead of recording rows.

Flow:

1. reuse a mixed-failure grid
2. run with `fail_fast=True`

Required assertions:

- the original exception type is re-raised on the first failing combination
- the original traceback is preserved
- the raised diagnostic exposes the failing parameters and stage through a
  Python exception note or equivalently visible standard diagnostic
- no misleading partial success artifact is returned

### I5: No-Trade And Undefined Metrics

Purpose: keep successful but sparse runs honest.

Flow:

1. run a strategy that never closes trades
2. rank by a metric that remains defined, such as total return
3. inspect trade-derived metrics

Required assertions:

- the row is a successful run, not failed
- no-trade metrics such as win rate or profit factor are undefined, not zero
- undefined objective values are ineligible when selected as the objective
- records use `None` plus `"undefined"` metric-state fields

### I6: Meaningful Infinity Metric

Purpose: preserve real report semantics while keeping records portable.

Flow:

1. create or simulate a successful result whose `trades.profit_factor` is
   `math.inf`
2. rank by `("trades.profit_factor", "max")`
3. export records

Required assertions:

- the row is eligible for selection
- direct selected-row report inspection preserves `math.inf`
- `to_records()` stores the metric value as `None` and the state as
  `"positive_infinity"`

### I7: Selected Run Inspection

Purpose: prove comparison rows connect back to normal backtest inspection.

Flow:

1. run a small successful grid
2. select `best()`
3. inspect `best.backtest.report`
4. call `best.backtest.plot()` when plotting dependencies are available

Required assertions:

- selected row uses an engine-produced `BacktestResult`
- the report path is the normal `BacktestResult.report`
- the plot path is the normal `BacktestResult.plot()` when plotting
  dependencies are installed; parameter exploration tests should assert access
  to this normal path without re-testing Matplotlib figure internals
- rejected and failed rows do not expose fake report or plot objects

### I8: Materialized Bars Only

Purpose: avoid hidden data loading and beta API drift.

Flow:

1. build or load a materialized `BarSeries`
2. pass the `BarSeries` into `ParameterStudy`
3. run a small grid
4. separately attempt to pass `source=` to `ParameterStudy` or
   `grid_search(...)`

Required assertions:

- the materialized `BarSeries` workflow succeeds
- attempts to pass a source object directly are rejected by the beta public
  surface

## Structure, Contract, Smoke, And Regression Scenarios

### S1: Public Import Surface

Required assertions:

- `from quantleet.research import ParameterStudy, ta` works
- `from quantleet.strategy import Strategy` works
- `ParameterStudy` is not promoted from `quantleet.backtest`
- public docs use `quantleet.strategy` for the canonical `Strategy` import

### S2: Package Boundary

Required assertions:

- parameter exploration implementation lives under the research capability
  boundary
- `research` composes the public `backtest` surface
- `backtest` does not import `research` to provide optimizer behavior
- `trading` and `execution` do not import parameter exploration code
- no heavy external optimizer dependency is introduced for beta

### S3: Public API Does Not Expose Deferred Controls

Required assertions:

- docs and public signatures do not expose `n_jobs`, `workers`, `parallel`, or
  custom executors
- docs and public signatures do not expose `source=` on `ParameterStudy`
- docs do not promote heatmaps, dashboards, visual table renderers, persistence,
  resume, or multi-objective optimization as beta behavior

### S4: Canonical Example Regression

Required assertions:

- the canonical constrained SMA-style grid example runs in the local example or
  notebook validation lane when the example is added; this is a P1 docs-release
  guardrail
- the example prints or exposes comparison output before selected-run report or
  plot inspection
- docs state that grid results are research diagnostics, not trading
  recommendations

### S5: Built Artifact Import Regression

Required assertions:

- the built package artifact exposes `quantleet.research.ParameterStudy`
- local smoke import tests pass from the installed artifact context used by the
  current command tests

## What Tests Should Verify

Tests should verify:

- public call shapes and documented imports
- deterministic candidate identity and row order
- clear validation errors at public boundaries
- visible counts and status distinctions
- row eligibility and objective-based selection
- failure diagnostics and `fail_fast` behavior
- stable record schema and metric-state semantics
- selected-run inspection through existing backtest result surfaces
- architecture boundaries that keep research experimentation separate from
  execution semantics

Tests should not verify:

- private helper names
- private class layout
- exact internal storage containers
- exact string formatting beyond required diagnostic content
- exact strategy profitability
- visual styling of selected-run plots
- order execution semantics already covered by lower-level backtest/order tests
- pandas-specific dataframe behavior unless pandas support becomes an explicit
  output contract

## Priority By Test Level

P0 before feature completion:

- U1 parameter grid validation
- U2 raw candidate limit
- U3 constraint outcomes
- U4 objective validation
- U5 selection helpers
- U6 failed row diagnostics
- U7 record output shape
- U8 study construction and public call shape
- I1 canonical small grid search
- I2 fresh strategy state per run
- I3 continue by default on mixed failures
- I4 fail-fast debugging mode
- I5 no-trade and undefined metrics
- I6 meaningful infinity metric
- I7 selected-run inspection
- I8 materialized bars only
- S1 public import surface
- S2 package boundary
- S3 no deferred controls

P1 for beta hardening:

- S4 canonical example regression as a docs-release guardrail
- S5 built artifact import regression
- additional regression tests for bugs found during implementation

P2 after beta:

- performance-adjacent study-size checks beyond the `max_candidates` guardrail
- richer example/notebook matrices
- tests for future search methods, parallel execution, persistence, or
  visualization after those become product scope

## Success Conditions

The test suite derived from this spec is sufficient when:

- every closed product decision in
  [parameter-exploration.md](parameter-exploration.md) has contract coverage or
  an explicit out-of-scope statement
- invalid inputs fail before backtests where the product spec requires
  preflight behavior
- the canonical study workflow passes through real public Quantcraft surfaces
- success, rejection, and failure outcomes are visible and distinguishable
- record output is stable, structured, and portable
- selected successful rows can inspect normal reports and plots without reruns
- default verification covers cheap unit/integration/structure/smoke scenarios
- runtime-sensitive implementation work also runs `uv run poe verify-runtime`
- no test encodes private implementation details that would block a legitimate
  internal refactor

## Open Questions

- None for the product/test-spec stage. The technical implementation plan may
  still choose internal helper names and file layout, but it should not reopen
  the beta product contracts above.
