# Walk-Forward Analysis Spec

## Status

- Status: `paused`
- Class: `product-spec`
- Scope: paused product target for a future single-symbol walk-forward
  validation-study workflow

Related documents:

- [research-ergonomics.md](research-ergonomics.md)
- [parameter-exploration.md](parameter-exploration.md)
- [walk-forward-analysis-readiness.md](walk-forward-analysis-readiness.md)
- [backtest-mvp.md](backtest-mvp.md)
- [backtest-plotting.md](backtest-plotting.md)
- [data-ingestion.md](data-ingestion.md)
- [../design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)
- [../design-docs/quantleet-architecture.md](../design-docs/quantleet-architecture.md)
- [../research/2026-03-23-python-quant-library-landscape.md](../research/2026-03-23-python-quant-library-landscape.md)
- [../research/libraries/backtesting-py.md](../research/libraries/backtesting-py.md)
- [../research/libraries/vectorbt.md](../research/libraries/vectorbt.md)
- [../research/libraries/pybroker.md](../research/libraries/pybroker.md)

This document records the product target and accepted decisions for Quantleet
walk-forward analysis research workflows. It is currently paused and must not
be treated as authorization to implement WFA.

The pause is intentional. WFA remains a desired validation-study workflow, but
design discussion exposed a deeper product-contract risk: the current
`strategy_factory`-centered parameter-study surface may be an implementation
adapter rather than the long-lived user-facing strategy configuration contract
needed by research, backtest, paper trading, and live trading. Implementing WFA
directly on top of that transitional surface could harden the wrong public API
and create refactoring debt across later validation and execution workflows.

Before WFA implementation resumes, Quantleet must complete a readiness analysis
of the blockers listed in
[walk-forward-analysis-readiness.md](walk-forward-analysis-readiness.md) and
choose the next refactoring slice deliberately.

This product spec therefore defines what must be preserved when WFA is
resumed: user intent, result semantics, naming decisions, and validation-study
positioning. It intentionally leaves lower-level module layout, helper names,
test mechanics, and prerequisite refactoring scope to later documents.

## Background And Problem Definition

Quantleet already has the pieces needed for a useful first single-symbol
research loop:

- a deterministic `BacktestEngine`
- normalized historical `BarSeries` input
- a `Strategy` authoring surface
- structured `BacktestResult.report` output
- `result.plot()` inspection
- constrained finite parameter exploration through `ParameterStudy`

That loop can answer whether a strategy and parameter combination produced a
backtest result on one historical range. It does not yet answer the more
important research-validation question:

> Did this parameter choice survive data it was not selected on?

A user can currently run a grid search over the full available dataset and rank
the rows by a metric. That is useful for exploration, but it can easily reward
parameters that fit historical noise. Without an official out-of-sample
workflow, users must hand-roll train/test splits, repeat parameter searches,
rerun selected strategies on future slices, stitch together results, and invent
their own diagnostics. Those ad hoc loops are error-prone and will drift across
notebooks, examples, and agents.

Walk-forward analysis exists to make the first validation workflow official. It
should let a user repeatedly select parameters using only an in-sample training
window, evaluate the selected parameters on the immediately following
out-of-sample window, and inspect whether the strategy remains coherent across
time. The output must emphasize out-of-sample evidence, not the in-sample score
that selected the parameters.

This feature is still desired if Quantleet is positioned as a tool for finding
and screening alpha candidates rather than only as a correct backtest runner. A
correct backtest engine proves that a historical simulation was computed
consistently. Walk-forward analysis helps users judge whether a research result
is robust enough to deserve further investigation. That value does not justify
shipping WFA on top of a strategy-parameter contract that the project already
believes may need to change.

## Pause Decision

Implementation of WFA is paused.

Accepted decisions that remain valid:

- WFA is a Validation Study, not a parameter recommendation engine.
- The public concept name should remain `WalkForwardStudy`.
- `WalkForwardOptimizer` should be avoided for the user-facing product name.
- The result UX should not be centered on `best_params`.
- The MVP result surface should emphasize `oos_summary`.
- `oos_report` is not permanently excluded; it may be added later if the
  product defines continuous OOS account/report semantics clearly.
- Splitter and cross-validation toolkit concepts should remain internal or
  advanced until the primary user workflow is stable.

Reason for pausing:

- WFA would exercise the strategy parameter contract harder than the current
  single-slice `ParameterStudy`.
- Current `ParameterStudy` uses `strategy_factory` as the public construction
  path.
- The emerging product direction favors an explicit `Strategy` plus
  `StrategyConfig` style contract, with factory behavior treated as an
  adapter or advanced escape hatch.
- Choosing the WFA implementation path before resolving that contract would
  likely turn an expedient API into a long-lived product promise.

Resume criteria:

- Known blockers in `walk-forward-analysis-readiness.md` have been analyzed.
- The project has selected the next refactoring slice or explicitly decided
  that WFA can safely proceed without it.
- Any chosen prerequisite product spec has been written before technical
  implementation planning begins.

## Goals

- Provide the first official overfitting-resistance workflow in Quantleet.
- Let users run repeated train-then-test validation without manually composing
  folds, grid searches, and backtest reruns.
- Keep the public API small enough for notebook users to understand quickly.
- Preserve `ParameterStudy` as the single-slice parameter comparison primitive.
- Make out-of-sample results the center of the user-facing output.
- Record selected parameters per fold so users can inspect stability over time.
- Surface fold-level train and test metrics in a structured, exportable form.
- Make failure states inspectable without hiding failed or rejected folds.
- Keep the first slice deterministic, sequential, single-symbol, and
  materialized-bars based.
- Avoid implying that walk-forward output proves a strategy is tradable or is
  financial advice.

## Non-Goals

The first walk-forward analysis product slice is not:

- a general-purpose optimizer
- Bayesian, SAMBO, genetic, or adaptive optimization
- random search
- purged cross-validation, combinatorial cross-validation, or embargoed
  cross-validation
- multi-symbol, multi-timeframe, portfolio, short, leverage, margin, paper, or
  live-trading support
- live scheduled re-optimization
- a paper-trading runtime
- a replacement for `ParameterStudy`
- a replacement for `BacktestEngine`
- a continuous portfolio simulation that carries cash, positions, or open
  orders across fold boundaries
- a promise that out-of-sample performance will continue in the future
- a statistical significance engine
- a GUI, heatmap product, or full tear sheet product
- a pandas-first API requirement
- a public commitment to every advanced diagnostic used by commercial
  walk-forward tools

Some of these capabilities may become later product slices. They must not be
smuggled into the first walk-forward analysis contract.

## User Intent

The primary user is a Python quant researcher or developer evaluating a
single-symbol strategy before deciding whether deeper research or forward
testing is justified.

They want to:

- define a finite set of strategy parameters
- choose one explicit objective metric for in-sample selection
- specify how much historical data is used for training and how much future
  data is used for testing
- avoid hand-writing fold boundaries
- confirm that out-of-sample performance does not collapse immediately after
  parameter selection
- see whether selected parameters are stable across folds
- compare train and test metrics without parsing formatted text
- keep every fold's selected run inspectable enough for report and plot
  investigation
- receive clear diagnostics when the validation result looks fragile

They are not asking Quantleet to discover a profitable strategy. They are
asking Quantleet to make honest train/test validation difficult to misuse.

## Decision Summary

The user-facing model is a research-level study object:

- `quantleet.research.WalkForwardStudy` owns the walk-forward UX.
- `WalkForwardStudy(...).run(...)` is the first execution method.
- `WalkForwardStudy` composes the existing backtest and parameter exploration
  surfaces; it does not introduce a second execution engine.
- The public result concept is `WalkForwardResult`.
- The fold-level result concept is `WalkForwardFold`.
- The first public workflow receives materialized `bars: BarSeries`; it does
  not accept `source=` in the first slice.
- The first public workflow is rolling walk-forward analysis.
- `step_size=None` means the test window advances by exactly `test_size`.
- The default fold shape is an "easy mode": each out-of-sample window starts
  immediately after its in-sample window and has no gap unless a later spec
  adds one.
- The first slice uses finite parameter sets and grid-style enumeration through
  `ParameterStudy`.
- `ParameterStudy` remains the primitive for comparing parameters within one
  training slice.
- The first slice should support objective aliases for user ergonomics, but the
  canonical metric contract remains compatible with existing report metric
  paths.
- Canonical structured output is records, not a pandas-only dataframe.
- Out-of-sample summary output must be clearly labeled as fold-based OOS
  validation, not as a continuous live-equivalent portfolio simulation.

## Core Requirements

1. Walk-forward analysis must be a research-layer feature under
   `quantleet.research`.
2. It must compose existing public `BacktestEngine`, `BarSeries`, `Strategy`,
   and `ParameterStudy` surfaces.
3. It must not change `trading`, `execution`, or backtest matching semantics.
4. It must not require users to construct folds manually for the primary
   workflow.
5. It must select parameters using only in-sample data for each fold.
6. It must test selected parameters only on the immediately following
   out-of-sample window for the default rolling mode.
7. It must preserve fold order and make the timestamp boundaries of each fold
   visible.
8. It must expose selected parameters per fold.
9. It must expose train and test metrics per fold.
10. It must make out-of-sample results more prominent than in-sample selection
    scores.
11. It must make validation failures explicit rather than silently dropping
    folds.
12. It must keep output portable without requiring pandas.

## Functional Requirements

### Public Entry Surface

The first public workflow should be centered on:

```python
from quantleet.research import WalkForwardStudy

study = WalkForwardStudy(
    engine=engine,
    bars=bars,
    strategy=MovingAverageCrossStrategy,
)

result = study.run(
    parameters={"fast": [5, 10, 20], "slow": [50, 100, 200]},
    objective="sharpe",
    constraint=lambda p: p["fast"] < p["slow"],
    train_size=500,
    test_size=100,
)
```

The example above is the product target for user comprehension. Exact type
names and import exposure may be refined in the implementation plan, but the
workflow should keep the same mental model:

- construct a study from a backtest engine, materialized bars, and a strategy
  input
- call `run(...)` with parameter candidates, an objective, and window sizes
- inspect a structured `WalkForwardResult`

### Strategy Input

The study must support a way to produce a fresh strategy instance for each
training candidate and each selected test run.

The product-level contract is:

- users may provide a strategy class or a callable strategy factory
- every attempted run receives fresh strategy state
- selected parameters are passed into the strategy construction path without
  mutating shared strategy objects
- invalid strategy construction failures are captured with enough context to
  identify the fold, stage, and parameter values

The exact normalization rule for strategy classes versus callables is an open
question for the implementation plan.

### Parameter Candidates

The first public workflow must accept finite parameter candidates through a
`parameters` mapping.

Requirements:

- parameter names are stable user-facing labels
- parameter values are finite, portable scalar values compatible with the
  existing parameter exploration contract
- parameter constraints can reject invalid combinations such as `fast >= slow`
- rejected combinations remain distinguishable from failed runs
- raw candidate count must be bounded by a safety guardrail compatible with
  `ParameterStudy`

The public name should remain `parameters`, not `param_grid`, so the product
does not permanently tie the user-facing contract to one optimizer family.

### Objective

Users must be able to choose the in-sample selection metric deliberately.

Requirements:

- the canonical objective contract must remain compatible with existing
  `ParameterStudy` metric paths and directions
- concise aliases such as `"sharpe"`, `"total_return"`, and `"max_drawdown"`
  may be supported for ergonomics
- aliases must resolve to explicit metric paths and directions
- unknown objectives must fail before any backtest is run
- objective selection must be recorded in the result

Callable objectives are a future direction unless a later test spec explicitly
brings them into scope.

### Window Definition

The first workflow must let users define the validation windows without
constructing fold objects.

Requirements:

- `train_size` is the number of bars used for in-sample parameter selection in
  the first slice
- `test_size` is the number of bars used for out-of-sample evaluation in the
  first slice
- `step_size=None` means `step_size == test_size`
- `mode="rolling"` is the first supported mode
- unsupported modes such as `"expanding"` or `"anchored"` must fail clearly
  until implemented
- folds must preserve chronological order
- each fold's test window must start after its training window
- the default mode must not overlap a fold's training window with that same
  fold's test window

String durations, timestamps, ratios, pandas offsets, custom folds, gap sizes,
embargo, and anchored or expanding windows are future scope unless a later spec
adds them.

### Fold Execution

For each generated fold, the study must:

1. run parameter exploration on the training bars
2. select the best eligible row according to the objective
3. create a fresh strategy using the selected parameters
4. run a normal backtest on the test bars
5. record fold boundaries, selected parameters, train metrics, test metrics,
   and failure state

If no eligible parameter row exists for a fold, the fold must be reported as
not selected or failed. The product must not fabricate test results for that
fold.

### Result Surface

The first result surface must support:

- `result.folds`
- fold count and successful/failed fold counts
- out-of-sample summary metrics
- selected parameters by fold
- structured record export
- basic parameter stability information
- basic diagnostics or warnings

The product target may include names such as:

```python
result.folds
result.oos_summary
result.to_records()
result.selected_parameters_by_fold
result.parameter_stability()
result.diagnostics
```

The exact attribute names belong to the later implementation plan, but the
result object must make those concepts available.

### Out-Of-Sample Summary Semantics

The OOS summary must be defined carefully.

The first slice may summarize independent test folds and may provide stitched
OOS return or equity-like analytics, but it must not imply that cash,
positions, open orders, or reservations are carried continuously across fold
boundaries unless that behavior is explicitly implemented and documented.

The result must make this distinction visible in docs and structured metadata.

### Diagnostics

The first diagnostics should help users notice fragile validation outcomes
without turning the result into a binary trading recommendation.

Candidate diagnostics include:

- train/test metric degradation
- selected parameter instability
- OOS profit concentrated in too few folds
- fold failure rate
- OOS drawdown materially worse than in-sample drawdown
- no eligible parameters in one or more folds

Diagnostics must be phrased as research warnings, not as trading advice or
strategy approval.

### Record Output

Record output must be portable and stable enough for notebooks, CSV/JSON
conversion, and agent inspection.

Records should include:

- fold index
- train start and end timestamps
- test start and end timestamps
- selected parameters
- objective path and direction
- train status and test status
- train metric values
- test metric values
- failure stage, error type, and error message when applicable

Records should not require pandas. A pandas convenience wrapper may be added
later if the dependency policy allows it.

## Non-Functional Requirements

- Deterministic output for the same bars, parameters, objective, and costs.
- Sequential execution in the first slice.
- No live network access during WFA execution unless the user separately
  materializes data through existing data-source surfaces before running the
  study.
- No hidden dependency on local environment variables.
- Clear validation errors before expensive backtests when call shapes are
  invalid.
- Memory use bounded by the existing parameter exploration safety model.
- Structured failures instead of swallowed exceptions for per-fold run errors.
- Strong type hints consistent with the existing Python 3.13 strict mypy
  policy.
- No pandas requirement for canonical output.
- No new dependency that weakens the current package footprint without a
  separate implementation plan decision.
- Documentation must explicitly state that WFA is a research diagnostic and not
  a guarantee of future performance.

## Major Scenarios

### Scenario 1: First WFA Run

The user has a materialized `BarSeries`, a `BacktestEngine`, and a strategy
class or factory. They define a small parameter mapping, choose `"sharpe"` as
the objective, set `train_size=500`, `test_size=100`, and run the study.

Expected outcome:

- folds are generated chronologically
- each fold selects parameters from training bars only
- each fold tests the selected parameters on the following test bars
- the result exposes fold records, selected parameters, OOS summary, and
  diagnostics

### Scenario 2: Constrained Parameter Space

The user tests moving-average parameters and provides a constraint requiring
`fast < slow`.

Expected outcome:

- invalid candidate combinations are rejected during the training search
- rejected combinations do not appear as successful candidates
- fold records preserve enough information to see whether no eligible row
  existed

### Scenario 3: Fragile OOS Performance

The train objective is strong in most folds, but test results are poor or
concentrated in one fold.

Expected outcome:

- the result still completes when runs are technically valid
- diagnostics identify train/test degradation or concentration risk
- the output does not describe the strategy as validated or tradable

### Scenario 4: Strategy Construction Failure

One parameter combination causes the strategy factory to raise.

Expected outcome:

- the failing combination is recorded with stage and error information
- other combinations and folds continue unless the later implementation plan
  adds an explicit fail-fast mode
- the user can identify the fold and parameters that caused the failure

### Scenario 5: Not Enough Bars

The user asks for `train_size=500` and `test_size=100`, but the series cannot
produce even one complete fold.

Expected outcome:

- the call fails before running any backtests
- the error names the requested sizes and available bar count

## Edge Cases And Failure Scenarios

- `bars` is not a `BarSeries`.
- `bars.rows` is empty.
- bars are too short for one fold.
- bars have duplicate or out-of-order timestamps.
- `train_size`, `test_size`, or `step_size` is zero, negative, boolean, or not
  an integer in the first slice.
- `step_size` is larger than the remaining data and creates fewer folds than
  the user expects.
- unsupported `mode` is provided.
- `parameters` is empty.
- parameter values are duplicated, unsupported, non-finite, or not portable.
- `constraint` raises or returns a non-bool value.
- objective alias is unknown.
- objective metric is undefined for every successful training row.
- all candidates are rejected in a fold.
- all candidate runs fail in a fold.
- selected strategy construction fails for the test run.
- the test backtest fails after a successful train selection.
- test fold has no fills or no closed trades, producing undefined metrics.
- non-finite metrics such as infinite profit factor appear in train or test
  reports.
- a strategy mutates external shared state between folds.
- fold-level test windows overlap because of invalid future custom settings.
- users confuse stitched OOS analytics with a continuous account simulation.

## External Contracts

The feature must preserve these externally visible contracts:

- `BacktestEngine.run(...)` remains the canonical historical execution entry.
- `ParameterStudy` remains the single-slice parameter exploration surface.
- `WalkForwardStudy` lives under the research capability, not under
  `backtest`, `trading`, or `execution`.
- `BarSeries` remains the materialized historical data input for this slice.
- `Strategy` order semantics remain governed by the existing research and
  backtest specs.
- `trading` remains independent of research and walk-forward code.
- The result must not require pandas for canonical inspection.
- Public examples must not imply live trading, paper trading, shorting,
  leverage, multi-symbol portfolios, or optimizer guarantees.
- WFA output must be described as research validation evidence, not financial
  advice or a strategy recommendation.

## Success Conditions

The product slice is successful when a user can:

- run a rolling walk-forward study on a single-symbol `BarSeries`
- provide finite parameter candidates and a deliberate objective
- use a constraint to reject invalid combinations
- inspect selected parameters for every successful fold
- compare train and test metrics for every fold
- inspect an OOS-centered summary
- export stable records without pandas
- see clear failure information for bad folds or bad parameter combinations
- understand from docs that WFA reduces but does not eliminate overfitting risk
- understand that the first WFA slice is not a paper/live or continuous-account
  simulation

## Open Questions

1. Should the public constructor argument be `strategy` only, or should both
   `strategy` and `strategy_factory` be accepted?
2. If a strategy class is provided, should Quantleet call it as
   `StrategyClass(**params)`, require a `parameters` constructor convention, or
   require users to pass an explicit factory?
3. Which objective aliases are part of the first public contract?
4. Should callable objectives be supported in the first slice or deferred until
   after metric-path objectives are stable?
5. Should the first WFA run continue by default after a fold failure, or should
   fold-level failures fail the whole study unless a `continue_on_error` option
   is set?
6. What is the exact name for the OOS aggregate: `oos_summary`, `oos_report`,
   `oos_result`, or another name that avoids continuous-account confusion?
7. Should successful test `BacktestResult` objects be retained for every fold,
   or should the first slice retain only structured metrics to bound memory?
8. Should there be a `max_candidates` guardrail on each training fold, inherited
   directly from `ParameterStudy`, or a WFA-specific total-run guardrail across
   all folds?
9. Should `step_size` default to `test_size` in all future modes, or only in
   rolling mode?
10. Should optional pandas `to_frame()` be in the first slice, or should record
    output be the only public export until dependency policy is revisited?
11. Which diagnostics are required for the first product slice versus later
    robustness work?
12. Should public docs call the feature "walk-forward analysis" or
    "walk-forward validation" when explaining the workflow to new users?
