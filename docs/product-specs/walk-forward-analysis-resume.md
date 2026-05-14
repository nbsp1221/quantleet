# Walk-Forward Analysis Resume Spec

## Status

- Status: `implemented`
- Class: `product-spec`
- Scope: Stage 4 product contract for resuming the first single-symbol
  walk-forward validation slice after WFA prerequisites

Related documents:

- [walk-forward-analysis.md](walk-forward-analysis.md)
- [walk-forward-analysis-resume-test-scenarios.md](walk-forward-analysis-resume-test-scenarios.md)
- [walk-forward-analysis-readiness.md](walk-forward-analysis-readiness.md)
- [wfa-prerequisite-roadmap.md](wfa-prerequisite-roadmap.md)
- [direct-backtest-class-config-api.md](direct-backtest-class-config-api.md)
- [parameter-exploration.md](parameter-exploration.md)
- [reporting-config-source-of-truth.md](reporting-config-source-of-truth.md)
- [strategy-configuration-contract.md](strategy-configuration-contract.md)
- [research-ergonomics.md](research-ergonomics.md)
- [backtest-mvp.md](backtest-mvp.md)

This document resumes WFA product planning after Stage 3.5. It defines the
first WFA product slice at the what/why level. It is not a test spec and not a
technical implementation plan.

## Background And Problem Definition

Quantleet can already run deterministic single-symbol backtests and compare a
finite strategy-parameter grid through `ParameterStudy`. That is enough to ask
"which candidate performed best on this historical range?" It is not enough to
ask the more important research-validation question:

> Did the selected parameters survive data they were not selected on?

Before Stage 4, WFA was intentionally paused. The blocker was not the
walk-forward algorithm itself. The blocker was that WFA would have hardened
strategy construction, config provenance, and reporting semantics that were not
yet settled. Those prerequisites are now clear enough for product planning:

- strategies use explicit `StrategyConfig` declarations
- `ParameterStudy` receives `strategy=StrategyClass`
- reports expose the framework-owned `report.run.strategy_config`
- direct backtests use `BacktestEngine.run(strategy=StrategyClass, config=...)`

Stage 4 therefore resumes WFA planning without reintroducing the old callable
or direct-instance construction model. The first WFA slice should make honest
train/test validation easy while keeping the output conservative: it should
show out-of-sample evidence, not imply a tradable strategy or a continuous live
account simulation.

## Goals

- Provide Quantleet's first official walk-forward validation workflow.
- Let users repeatedly select parameters on an in-sample training window and
  evaluate the selected config on the following out-of-sample test window.
- Compose the existing `BacktestEngine`, `ParameterStudy`, `Strategy`, and
  `StrategyConfig` contracts instead of teaching a separate construction model.
- Make out-of-sample fold evidence more prominent than the in-sample selection
  score.
- Preserve enough train-search detail for users to understand why each fold
  selected a config.
- Record fold failures and rejected candidates explicitly so fragile validation
  runs remain inspectable.
- Keep the first slice deterministic, sequential, single-symbol, and based on
  materialized `BarSeries` input.

## Non-Goals

The first resumed WFA product slice is not:

- WFA implementation authorization by itself
- a general optimizer or parameter recommendation engine
- a replacement for `ParameterStudy`
- a replacement for `BacktestEngine`
- multi-symbol, multi-timeframe, portfolio, short, leverage, margin, paper, or
  live trading support
- live scheduled re-optimization
- Bayesian, genetic, SAMBO, random-search, or adaptive optimization
- purged, embargoed, combinatorial, anchored, or expanding cross-validation
- custom user-provided fold objects
- calendar-duration, timestamp-boundary, or pandas-offset windowing
- a continuous account simulation across test folds
- an `oos_report` or stitched OOS equity curve
- a statistical significance engine
- a pandas-first output contract
- a claim that out-of-sample performance will continue in the future

## User Intent

The primary user is a Python quant researcher or developer screening a
single-symbol strategy before deciding whether deeper research or forward
testing is justified.

They want to:

- provide a strategy class and a finite set of config candidates
- choose one explicit objective for in-sample selection
- define simple train and test window sizes without hand-writing folds
- verify that selected parameters are tested only on later unseen bars
- inspect which config was selected in each fold
- compare train metrics and test metrics fold by fold
- see whether selected parameters are stable or jump around
- understand failures without losing the rest of the validation run
- export stable structured records without depending on pandas

They are not asking Quantleet to declare a strategy profitable or tradable.
They are asking for a careful validation study that makes overfitting harder to
hide.

## Core Requirements

1. WFA remains a research-layer validation study named `WalkForwardStudy`.
2. The first public result concept remains `WalkForwardResult`.
3. The fold-level result concept remains `WalkForwardFold`.
4. The first workflow accepts materialized `bars: BarSeries`; it does not
   accept `source=` directly.
5. The first workflow accepts a strategy class using the canonical
   `StrategyConfig` contract.
6. WFA must create fresh strategy state for every train candidate and selected
   test run through the existing class-plus-config path.
7. WFA must compose `ParameterStudy` for each training-window parameter search.
8. WFA must compose `BacktestEngine.run(strategy=StrategyClass, config=...)`
   for selected out-of-sample test runs.
9. WFA must not introduce a second strategy construction model.
10. WFA must not change backtest matching, trading, or execution semantics.
11. Input and contract errors must fail before running any backtests.
12. Fold-level execution failures must be recorded and the study must continue
    by default.
13. `oos_summary` must mean independent test-fold summary, not continuous
    account output.

## Functional Requirements

### Public Entry Surface

The first workflow is a study object under `quantleet.research`:

```python
study = WalkForwardStudy(
    engine=engine,
    bars=bars,
    strategy=MovingAverageCrossStrategy,
)

result = study.run(
    parameters={"fast": [5, 10, 20], "slow": [50, 100, 200]},
    objective=("returns.total_return", "max"),
    constraint=lambda config: config["fast"] < config["slow"],
    train_size=500,
    test_size=100,
)
```

This example defines the product mental model. Exact import exposure and
method signatures belong to the later implementation plan, but the product
must preserve the same shape: construct a study from engine, bars, and strategy
class; run it with finite candidates, an objective, and bar-count windows; then
inspect a structured result.

### Strategy And Config Input

Users provide a `Strategy` class. Parameter candidates are materialized into
that strategy's declared `StrategyConfig` type. WFA must not accept or teach
pre-constructed strategy instances as the primary path.

Every train candidate and every selected test run receives fresh strategy
state. Config values selected during training must flow into the selected test
run through the same `StrategyConfig` snapshot vocabulary used by reports.

### Parameter Candidates

The first workflow accepts finite parameter candidates through a
`parameters` mapping.

Requirements:

- parameter names are user-facing config field names
- parameter values are finite JSON-scalar values compatible with
  `ParameterStudy`
- empty or malformed parameter grids fail before backtests run
- unknown config fields fail before backtests run
- constraints may reject invalid config combinations
- constraints receive the full materialized `strategy_config` mapping for each
  candidate, matching `ParameterStudy`
- rejected combinations remain distinguishable from failed runs

### Objective

The first WFA slice uses the existing `ParameterStudy` objective contract:

```python
objective=("metric.path", "max")
objective=("metric.path", "min")
```

String aliases such as `"sharpe"` and callable objectives are deferred. Unknown
metric paths, invalid directions, and invalid objective shapes must fail before
any backtest runs.

### Window Definition

The first WFA slice uses bar-count windows only:

- `train_size` is the number of bars used for in-sample selection
- `test_size` is the number of bars used for out-of-sample evaluation
- `step_size=None` means `step_size == test_size`
- provided sizes must be positive integers and must not be booleans
- the bars must produce at least one complete fold before execution begins

Date strings, duration strings, timestamp ranges, pandas offsets, custom fold
objects, gaps, and embargo settings are deferred.

### Fold Mode

The first WFA slice supports rolling mode only. Each fold has a fixed-length
training window followed by the next test window. Unsupported modes such as
`"expanding"` and `"anchored"` must fail clearly until they are deliberately
specified.

### Fold Execution

For each generated fold, WFA must:

1. slice the training bars and test bars chronologically
2. run `ParameterStudy` on the training bars
3. select the best eligible training row using the objective
4. materialize the selected config for the test run
5. run a normal backtest on the test bars
6. record fold boundaries, selected config, train metrics, test metrics, and
   failure state

If no eligible row exists for a fold, WFA must record that fold with
`status="failed"` and a selection-stage reason indicating that no config was
selected. It must not fabricate a test result.

### Failure Policy

WFA has two failure classes.

Preflight input and contract failures are strict. They fail the study before
any backtest is run. Examples include invalid bars, invalid strategy class,
invalid objective, malformed parameters, invalid window sizes, unsupported
mode, raw candidate-count guardrail violations, and no complete folds.

Fold-level execution failures are recorded and execution continues by default.
Fold-level failures include train-search failure that prevents selection, no
eligible training row, selected test construction failure, selected test
backtest failure, and selected test metric extraction failure.

Candidate-row failures inside the retained train `GridSearchResult` are more
fine-grained than fold status. Constraint rejections, constraint exceptions,
strategy-config materialization failures, train candidate construction
failures, train candidate backtest failures, and train candidate metric
extraction failures remain inspectable as train-search rows. They do not make
the fold fail when another objective-eligible row can still be selected and
tested.

### Result Surface

The first result surface must expose:

- ordered `folds`
- successful and failed fold counts
- selected config by fold
- train metrics for selected rows
- test metrics for successful OOS runs
- fold boundaries
- fold failure stage and error details
- `oos_summary`
- parameter-stability information
- diagnostics or warnings
- stable record export

Fold objects must preserve each fold's train `GridSearchResult`, including
successful candidate `BacktestResult` objects. Successful selected test folds
must retain the selected test `BacktestResult`. The default record export
remains fold-summary oriented and train-candidate records are exposed
separately.

For the first slice, parameter-stability information means users can inspect
the selected `StrategyConfig` snapshot for every fold. A separate stability
score, instability diagnostic, or most-common-config summary is not part of
Stage 4.

### OOS Summary

`oos_summary` summarizes independent test folds.

It may include counts, distributions, averages, medians, minima, maxima,
positive-fold ratios, degradation summaries, and stability summaries. It must
not present fold results as a continuous account, continuous portfolio, or
live-equivalent equity curve. When there are zero successful selected test
folds, `oos_summary` still exposes counts and failure-rate information but must
not fabricate numeric metric aggregates.

### Diagnostics

Diagnostics should help users notice fragile validation results without making
trading recommendations.

The first diagnostics are fact-based and do not require numeric quality
thresholds. Required diagnostic themes include:

- fold execution failure
- no selected config for a fold
- successful test fold with undefined objective metric
- successful test fold with no closed trades
- zero successful OOS test folds

Threshold-based quality diagnostics such as train/test objective degradation,
selected-parameter instability, and OOS return concentration are deferred.

### Record Output

Canonical export must be portable structured records, not a pandas-only
dataframe.

Fold-level records should include:

- fold index
- train start and end positional indexes
- test start and end positional indexes
- train first and last observed timestamps
- test first and last observed timestamps
- selected config values when available
- objective metric path and direction
- train status
- test status
- selected train metrics
- test metrics
- failure stage
- error type
- error message

Detailed train-candidate export is part of the first slice, but separate from
the fold-level `to_records()` export.

## Non-Functional Requirements

- Deterministic output for the same bars, strategy, parameters, objective,
  costs, and window settings.
- Sequential execution in the first slice.
- No live network access during WFA execution.
- No hidden dependency on environment variables.
- Clear validation errors before expensive backtests when inputs are invalid.
- Memory use must remain bounded by explicit candidate/fold guardrails.
- Per-fold failures must be structured and inspectable.
- Type hints must remain compatible with the repository's strict mypy policy.
- Canonical output must not require pandas.
- Public docs must state that WFA is research validation evidence, not
  financial advice or a guarantee of future performance.

## Major Scenarios

### Scenario 1: First Rolling WFA Run

The user has a `BarSeries`, a `BacktestEngine`, and a strategy class. They pass
finite parameters, an objective tuple, `train_size=500`, and `test_size=100`.

Expected outcome:

- folds are generated chronologically
- each fold selects config values using training bars only
- each fold tests the selected config on the next test bars
- the result exposes fold records, selected configs, `oos_summary`, and
  diagnostics

### Scenario 2: Constrained Parameter Space

The user provides moving-average candidates and a constraint such as
`fast < slow`.

Expected outcome:

- invalid combinations are rejected during training search
- rejected combinations are not treated as successful candidates
- fold records preserve whether no eligible candidate existed

### Scenario 3: Fold-Level Failure

A candidate or selected test run fails in one fold.

Expected outcome:

- the fold records the failure stage, error type, and error message
- other folds continue by default
- final summary counts successful and failed folds

### Scenario 4: No Eligible Training Row

All candidates in a fold are rejected, fail, or have undefined objective
metrics.

Expected outcome:

- the fold records that no test run was selected
- no fake OOS test result is created
- later folds continue

### Scenario 5: Fragile OOS Performance

Training scores look strong, but test fold performance is weak, unstable, or
concentrated in one fold.

Expected outcome:

- the result still completes when runs are technically valid
- `oos_summary` centers test-fold evidence
- diagnostics warn about fragility without describing the strategy as validated
  or tradable

### Scenario 6: Not Enough Bars

The user requests windows that cannot produce one complete fold.

Expected outcome:

- the call fails before running backtests
- the error names the requested sizes and available bar count

## Edge Cases And Failure Scenarios

- `bars` is not a `BarSeries`.
- `bars` is empty.
- bars have duplicate or out-of-order timestamps.
- `strategy` is not a `Strategy` class.
- `parameters` is not a mapping.
- `parameters` is empty.
- parameter names are not strings or are unknown config fields.
- parameter values are duplicated, unsupported, non-scalar, or non-finite.
- raw candidate count exceeds the allowed guardrail.
- objective is missing, malformed, unknown, or has an invalid direction.
- `constraint` raises or returns a non-bool value.
- `train_size`, `test_size`, or `step_size` is zero, negative, boolean, or not
  an integer.
- the bars cannot produce one complete fold.
- unsupported mode is provided.
- `engine` is missing or is not a usable `BacktestEngine`.
- all candidates are rejected in a fold.
- all candidate runs fail in a fold.
- objective metric is undefined for every successful training row.
- selected test strategy construction fails.
- selected test backtest fails.
- test metrics are undefined or non-finite.
- users confuse `oos_summary` with continuous account output.

## External Contracts

- `BacktestEngine.run(...)` remains the canonical historical execution entry.
- `ParameterStudy` remains the canonical single-slice parameter exploration
  primitive.
- `StrategyConfig` remains the strategy configuration source of truth.
- `BacktestReport.run.strategy_config` remains the report-facing config
  snapshot vocabulary.
- `WalkForwardStudy` lives under the research capability.
- `BarSeries` remains the materialized historical data input for the first
  slice.
- `trading` and `execution` semantics are not changed by WFA.
- Canonical output does not require pandas.
- Public examples must not imply live trading, paper trading, leverage,
  multi-symbol portfolios, optimizer guarantees, or financial advice.

## Success Conditions

The product slice is successful when a user can:

- run a rolling walk-forward validation study on one materialized `BarSeries`
- provide finite config candidates and an explicit objective tuple
- use constraints to reject invalid candidate configs
- inspect selected configs for successful folds
- inspect train and test metrics for each fold
- inspect fold failures without losing the whole study
- see an OOS-centered summary of independent test folds
- export stable fold-level records without pandas
- understand that `oos_summary` is not a continuous account report
- understand that WFA reduces but does not eliminate overfitting risk

## Evidence Consulted

The following sources were used to close questions that do not require a human
product decision:

- Quantleet `ParameterStudy` already retains successful row `BacktestResult`
  objects, exposes `GridSearchResult.to_records()`, preserves metric states,
  validates `max_candidates`, and records `error_type` plus `error_message`.
- PyBroker documents walk-forward analysis as splitting supplied data into
  windows with train and test portions, and its `TestResult` contains portfolio
  balances, order history, and evaluation metrics.
- PyBroker source validates WFA split inputs before yielding windows and
  returns rich dataframes for portfolio, positions, orders, trades, metrics,
  bootstrap data, and signals.
- Backtesting.py documents `Backtest.optimize(...)` with `max_tries`,
  `constraint`, `return_heatmap`, and optional raw optimization output for
  inspectability.
- Backtesting.py examples use `return_heatmap=True` to inspect all permissible
  tried parameter combinations and `max_tries` to bound large searches.
- Backtrader documents `optreturn=True` as a memory-saving optimization result
  mode that returns lightweight parameter/analyzer containers rather than full
  strategy objects.
- VectorBT's open-source records layer treats structured records as a first
  class representation and exposes dataframe conversion as a convenience over
  stored record arrays.

Source links:

- PyBroker strategy reference:
  <https://www.pybroker.com/en/latest/reference/pybroker.strategy.html>
- Backtesting.py API reference:
  <https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html>
- Backtesting.py parameter heatmap example:
  <https://kernc.github.io/backtesting.py/doc/examples/Parameter%20Heatmap%20%26%20Optimization.html>
- Backtrader Cerebro reference:
  <https://backtrader.readthedocs.io/en/latest/api/cerebro.html>

Local source snapshots inspected:

- `/tmp/quantleet-wfa-research/pybroker/src/pybroker/strategy.py`
- `/tmp/quantleet-wfa-research/backtesting.py/backtesting/backtesting.py`
- `/tmp/quantleet-wfa-research/backtrader/backtrader/cerebro.py`
- `/tmp/quantleet-wfa-research/vectorbt/vectorbt/records/base.py`

## Evidence-Based Decisions

The following decisions are closed for the first WFA slice unless a later human
review explicitly reopens them.

### Result Retention

1. Each successful selected test fold retains the full `BacktestResult`.

   Rationale: Quantleet `ParameterStudy` already retains successful row
   backtests for inspectability. PyBroker also returns rich result artifacts
   for walk-forward/backtest runs. Dropping selected test results would make WFA
   less inspectable than the current single-slice study.

2. Each fold's retained train `GridSearchResult` keeps its successful candidate
   `BacktestResult` objects.

   Rationale: this follows the existing `ParameterStudy` contract and avoids a
   lossy WFA-only parallel result model. Backtesting.py's heatmap option also
   shows that candidate-level inspection is a normal optimization need.

3. The first slice does not expose a memory-light result mode.

   Rationale: Backtrader proves that lightweight optimization result modes are
   useful, but they are an additional product mode. Quantleet should first ship
   the more inspectable behavior that matches its current research API, then add
   memory-light retention only if measured memory pressure justifies it.

4. Full train and selected test result retention remains paired with an
   unlimited default WFA total-run cap in the first slice.

   Rationale: the first slice prioritizes inspectability. Large WFA runs are an
   explicit user responsibility unless users supply `max_candidates` or a
   WFA-level total-run cap. The product mitigates the risk by exposing planned
   execution scale instead of silently adding a default WFA cap or memory-light
   mode.

5. Public fold records and failure metadata store `error_type` and
   `error_message`, not raw exception objects.

   Rationale: this matches `ParameterStudy` and keeps records portable,
   deterministic, and JSON-friendly.

### Guardrails And Run Limits

6. WFA inherits the per-fold `ParameterStudy.max_candidates` guardrail.

   Rationale: this preserves the existing finite-grid safety model.

7. WFA exposes an optional total-run guardrail across all folds, but the
   default is unlimited.

   Rationale: nested WFA multiplies fold count by candidate count, but the
   comparison libraries generally do not impose a strict WFA-level default cap.
   Backtesting.py exposes `max_tries` for optimization but lets exhaustive grid
   search run by default, PyBroker exposes `windows` without a separate total
   run cap, and Backtrader focuses on memory/performance controls such as
   `optreturn` and `exactbars`. Quantleet should still let advanced users set a
   cap explicitly when they want one.

8. The total-run guardrail counts planned train candidate backtests plus one
   selected test backtest per fold.

   Rationale: this best matches user-visible runtime cost. Candidates rejected
   before backtest execution should not count as executed backtests, but raw
   planned counts should still be used for early safety checks when available.

9. The WFA total-run guardrail defaults to `None`.

   Rationale: the first slice should avoid surprising users by rejecting
   otherwise valid research runs. The product must instead make planned work
   visible before execution.

10. Planned execution scale is exposed before execution and in result metadata.

   Rationale: if the default is unlimited, the safety value comes from making
   scale visible: fold count, raw candidate count per fold, planned train
   candidate runs, planned selected test runs, and planned total runs. If a user
   supplies an explicit total-run cap, cap failures happen before any fold runs
   when the raw counts are knowable.

11. Per-fold `ParameterStudy.max_candidates` guardrail failures are checked
    before any fold runs when the raw candidate count is knowable.

    Rationale: the first slice uses the same raw grid for every fold. Letting
    earlier folds run before discovering that later folds exceed the inherited
    candidate guardrail would violate the strict preflight contract.

### Fold Selection And Status Semantics

12. A fold with no objective-eligible training row is `status="failed"` with
    failure stage `selection`.

    Rationale: no honest OOS test result can be produced without a selected
    config.

13. A fold with rejected candidates but one selected eligible row is successful.

    Rationale: constraints are normal search behavior in both Quantleet and
    Backtesting.py.

14. A fold with failed train candidates but one selected eligible row is
    successful with diagnostics.

    Rationale: the OOS test remains valid, but train-search fragility should be
    visible.

15. The first slice does not expose a third public `partial` fold status.

    Rationale: `success`/`failed` plus diagnostics and counts is enough for the
    first slice and avoids status vocabulary that users must learn too early.

16. The first slice does not expose a public fail-fast option.

    Rationale: continue-by-default was already confirmed. A fail-fast flag is
    operational control that can be added later without changing the core
    product contract.

### Failure Taxonomy

17. Public fold-level failure stages are `train_search`, `selection`,
    `test_strategy_construction`, `test_backtest`, and
    `test_metric_extraction`.

    Rationale: these stages separate train search failures from selected OOS
    failures. Preflight and fold-generation failures occur before a public
    `WalkForwardResult` exists.

18. Train candidate failures keep the existing `ParameterStudy` stages inside
    the retained train `GridSearchResult`: `constraint`,
    `strategy_construction`, `backtest`, and `metric_extraction`.

    Rationale: flattening these stages would throw away already-available
    information.

19. Selected test strategy construction uses the fold-level stage
    `test_strategy_construction`.

    Rationale: it avoids ambiguity with train candidate construction failures.

20. Strict preflight failures do not appear in result records.

    Rationale: no `WalkForwardResult` exists when preflight fails.

21. Records include exception class names as `error_type` and messages as
    `error_message`.

    Rationale: this matches `ParameterStudy` and keeps failures inspectable
    without storing exception objects.

### OOS Summary Content

21. `oos_summary` summarizes the same metric paths already extracted by
    `ParameterStudy`, at least for successful selected test folds.

    Rationale: reusing the existing metric vocabulary prevents WFA from
    inventing a second research metric registry.

22. `oos_summary` includes count, average, median, minimum, and maximum for
    each defined numeric metric.

    Rationale: distribution summaries fit the independent-fold semantics better
    than a single stitched equity value.

23. `oos_summary` includes state counts for undefined, positive-infinity, and
    negative-infinity metric states.

    Rationale: Quantleet already preserves metric states in `ParameterStudy`;
    silently coercing those values would hide important validation facts.

24. `oos_summary` includes a positive-fold ratio for `returns.total_return`.

    Rationale: this is a simple concentration signal that does not imply a
    continuous account.

25. `oos_summary` does not include aggregate equity or aggregate total return
    across folds in the first slice.

    Rationale: aggregate return across folds can imply a stitched account,
    which the first slice explicitly excludes.

26. `oos_summary` always includes the chosen objective metric when it is
    available on successful test folds.

    Rationale: the central WFA question is whether the train-selected objective
    survived OOS.

27. Failed folds, including folds with no selected config, are included in
    fold counts and failure rates, but excluded from numeric metric aggregates
    that require a successful OOS test.

    Rationale: this keeps summary denominators honest without fabricating
    metrics for missing test runs.

### Diagnostics

28. The first slice includes only fact-based diagnostics that do not require
    numeric quality thresholds.

    Rationale: comparison libraries generally provide metrics, records,
    analyzers, or bootstrap outputs and leave strategy-quality interpretation to
    the user. Quantleet should avoid overclaiming by automatically judging
    strategy quality in the first WFA slice.

29. Required fact-based diagnostics are fold execution failure, no selected
    config for a fold, successful test fold with undefined objective metric,
    successful test fold with no closed trades, and zero successful OOS test
    folds.

    Rationale: these facts directly affect whether the result can be
    interpreted. They do not require arbitrary performance thresholds.

30. Train/test objective degradation, selected-parameter instability, and OOS
    return concentration are not automatic first-slice diagnostics.

    Rationale: those are useful analysis themes, but numeric thresholds would
    be product-opinionated and are not common defaults in the comparison
    libraries. The first slice should expose records and summaries that let
    users inspect those patterns manually.

31. Fold-level `selected_config` snapshots are sufficient first-slice
    parameter-stability evidence.

    Rationale: users can see whether selected configs repeat or jump around
    fold by fold without Quantleet inventing a stability score or threshold.
    A separate stability summary can be added later if real usage shows that
    users need a more compressed view.

32. Diagnostics are structured objects with `severity`, `code`, `message`, and
    affected fold indexes when applicable.

    Rationale: structured diagnostics are easier for notebooks, tests, exports,
    and agents to inspect than plain strings.

33. Diagnostic severities are `info` and `warning`.

    Rationale: first-slice diagnostics are facts, not quality judgments.
    `critical` implies a thresholded severity policy and is deferred until a
    later robustness-diagnostics slice deliberately designs that behavior.

34. Diagnostics never make a technically valid WFA run fail.

    Rationale: diagnostics describe research fragility after execution; they
    are not preflight contract errors.

35. Diagnostic thresholds are not part of the first slice.

    Rationale: threshold tuning is a separate ergonomics and product-opinion
    surface. The first slice exposes the facts needed to compute such warnings
    later without defining arbitrary cutoffs now.

### Record Export

36. `WalkForwardResult.to_records()` returns one fold-level record per fold.

    Rationale: this gives the primary export a stable grain and avoids mixing
    fold-level and candidate-level rows.

37. The first slice also exposes a separate train-candidate record export.

    Rationale: retained train `GridSearchResult` already has candidate records,
    and Backtesting.py's heatmap pattern shows that candidate-level inspection
    is important for optimization review.

38. Candidate-level export includes `fold_index` on every row.

    Rationale: without a fold key, candidate rows cannot be reliably joined to
    fold outcomes.

39. Record exports use flat top-level metadata and metric keys while keeping
    config snapshots nested under names such as `selected_config`,
    `candidate_parameters`, and `strategy_config`.

    Rationale: this matches `ParameterStudy.to_records()` where candidate
    overrides and full config snapshots stay nested to avoid collisions with
    user-defined config field names, while metric and status fields remain easy
    to export.

40. Records include metric state fields for undefined or infinite metric
    values.

    Rationale: this matches `ParameterStudy` and prevents non-standard JSON
    float tokens from leaking into records.

41. Pandas `to_frame()` is not part of the first slice.

    Rationale: VectorBT and PyBroker rely heavily on dataframe outputs, but
    Quantleet's first-beta contract already prefers portable records and avoids
    pandas-only canonical output.

### Fold Boundary Records

42. Fold boundaries are recorded as both positional indexes and timestamps.

    Rationale: indexes make slicing auditable; timestamps make records readable.

43. Positional boundaries use start-inclusive, end-exclusive indexes.

    Rationale: this matches Python slicing and makes train/test reconstruction
    unambiguous.

44. Timestamp boundaries record first and last observed bar timestamps.

    Rationale: users read observed timestamps more naturally than exclusive
    timestamp bounds, while index fields preserve exact slicing semantics.

45. `mode`, `train_size`, `test_size`, and resolved `step_size` are result-level
    metadata.

    Rationale: those values apply to the whole run and do not need to be
    repeated on every fold record unless export usability later requires it.

### Public Naming And Docs

46. The feature label remains "walk-forward analysis"; docs explain it as
    validation.

    Rationale: `WalkForwardStudy` and the existing WFA docs already use the
    analysis name, and PyBroker also uses Walkforward Analysis terminology.

47. The public OOS property remains `oos_summary`.

    Rationale: the name avoids `oos_report` and `oos_result`, which could imply
    a continuous account or a standalone backtest result.

48. Fold output uses `selected_config` as the canonical name.

    Rationale: Stage 1 through Stage 3.5 made `StrategyConfig` the source of
    truth. `selected_parameters` can appear in explanatory text only when it
    helps users understand the concept.

49. Docs describe WFA as reducing overfitting risk, never preventing
    overfitting.

    Rationale: WFA is evidence, not proof. The first slice must avoid optimizer
    or trading-recommendation claims.

50. Public examples include financial-advice and future-performance caveats in
    narrative text.

    Rationale: this is consistent with the repository's beta positioning and
    financial disclaimer.

### Scope Boundaries Before Test Spec

51. Source-backed WFA input remains outside the first slice.

    Rationale: materialized `BarSeries` input is already decided and keeps WFA
    execution free of live/network data-source concerns.

52. Expanding and anchored modes are simply unsupported values that fail
    clearly.

    Rationale: reserved pseudo-supported mode vocabulary creates a product
    promise before those modes are designed.

53. Objective aliases are not shown in first-slice user examples.

    Rationale: Stage 4 explicitly defers aliases; examples should teach only
    the supported objective tuple contract.

## Open Product Questions

None for the Stage 4 resume product contract.

Future slices may reopen:

- WFA-level total-run default limits if runtime evidence shows users need a
  stronger safety brake than transparent planned-run metadata.
- threshold-based robustness diagnostics if Quantleet deliberately chooses a
  more opinionated validation-warning product.
