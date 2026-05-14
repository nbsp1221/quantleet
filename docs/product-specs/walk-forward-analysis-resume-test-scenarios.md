# Walk-Forward Analysis Resume Test Scenarios

## Status

- Status: `implemented`
- Class: `product-test-scenarios`
- Scope: Stage 4 first-slice WFA test target after WFA resume product
  contract

Related documents:

- [walk-forward-analysis-resume.md](walk-forward-analysis-resume.md)
- [walk-forward-analysis.md](walk-forward-analysis.md)
- [wfa-prerequisite-roadmap.md](wfa-prerequisite-roadmap.md)
- [direct-backtest-class-config-api.md](direct-backtest-class-config-api.md)
- [direct-backtest-class-config-api-test-scenarios.md](direct-backtest-class-config-api-test-scenarios.md)
- [parameter-exploration.md](parameter-exploration.md)
- [parameter-exploration-test-scenarios.md](parameter-exploration-test-scenarios.md)
- [strategy-configuration-contract.md](strategy-configuration-contract.md)
- [reporting-config-source-of-truth.md](reporting-config-source-of-truth.md)
- [research-ergonomics.md](research-ergonomics.md)
- [backtest-mvp.md](backtest-mvp.md)
- [../references/testing.md](../references/testing.md)
- [../RELIABILITY.md](../RELIABILITY.md)
- [../SECURITY.md](../SECURITY.md)

This document turns the product intent in
[walk-forward-analysis-resume.md](walk-forward-analysis-resume.md) into a test
scenario contract. It is not an implementation plan. Tests derived from this
document should prove the public Stage 4 WFA behavior through observable
contracts.

## Testing Basis

Stage 4 exists so a single-symbol research user can ask a stricter question
than a single parameter grid can answer:

> Did the parameters selected on the train window survive the next unseen test
> window?

The core test contract is:

- `quantleet.research.WalkForwardStudy` is the public research study container.
- `WalkForwardStudy(...).run(...)` accepts materialized `bars: BarSeries`, a
  strategy class, finite config candidates, one explicit objective tuple, an
  optional constraint, and bar-count windows.
- Constraints receive the full materialized `strategy_config` mapping for each
  candidate, matching `ParameterStudy`.
- Each fold uses training bars only to run `ParameterStudy`.
- Each fold tests only the selected config on the following OOS bars through
  `BacktestEngine.run(strategy=StrategyClass, config=...)`.
- WFA does not introduce a parallel strategy construction path.
- WFA does not change backtest matching, trading, or execution semantics.
- Preflight input and contract errors fail before any backtests start.
- Fold-level execution failures are recorded and execution continues by
  default.
- `oos_summary` summarizes independent successful test folds; it is not a
  stitched account, continuous equity curve, or trading recommendation.
- `WalkForwardResult` and record exports expose enough fold, selection,
  failure, diagnostic, and metric-state evidence for users to inspect the run.

Tests must therefore validate train/test separation, result inspectability,
failure honesty, and source-of-truth composition. They must not validate
whether a strategy is profitable or tradable.

## Testing Philosophy

Good tests for this slice are long-lived product assets.

Operational rules:

1. Test behavior and public contracts, not private helper names. Google Testing
   Blog recommends behavior-focused tests because one public method can expose
   many separate user-visible behaviors:
   [Testing on the Toilet: Test Behaviors, Not Methods](https://testing.googleblog.com/2014/04/testing-on-toilet-test-behaviors-not.html).
2. Use a layered suite. Fast unit tests should cover fold generation,
   validation, summary, diagnostics, and record-shape rules. Integration tests
   should prove the public WFA workflow composes real `ParameterStudy`,
   `BacktestEngine`, `Strategy`, `StrategyConfig`, `BarSeries`,
   `GridSearchResult`, and `BacktestResult` contracts. This follows the
   practical test pyramid guidance that uses many focused lower-level tests
   and fewer cross-module tests:
   [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html).
3. Make inputs and expected results easy to read. A human or AI agent should
   be able to diagnose a failed test without reverse-engineering large market
   fixtures or production internals.
4. Prefer real Quantleet objects at public boundaries. Use fakes only to prove
   call timing, preflight no-run behavior, and hard-to-trigger failure states.
5. Test edge cases as first-class behavior. A WFA test suite that only covers a
   happy rolling run is not enough because this feature's product value depends
   on honest handling of invalid inputs, missing selections, failed folds,
   undefined metrics, and non-continuous OOS summaries.
6. Treat brittle tests as design feedback. If a public contract is hard to
   test without asserting private storage details, the implementation plan
   should create a clearer public result or fixture boundary rather than
   baking private assumptions into tests.

## Test Scope

In scope:

- public `WalkForwardStudy` construction shape
- materialized `BarSeries` input only
- strategy class plus `StrategyConfig` materialization
- finite parameter candidates and constraints as composed through
  `ParameterStudy`
- objective tuple validation and OOS objective metric reporting
- rolling bar-count fold generation
- `step_size=None` resolving to `test_size`
- strict preflight failures before any train or test backtest starts
- per-fold train search, selection, selected test execution, and continuation
  after fold failures
- success and failure counts
- fold boundaries as indexes and timestamps
- retained train `GridSearchResult`
- retained selected test `BacktestResult` for successful test folds
- `oos_summary` independent-fold aggregate semantics
- fact-based diagnostics without quality thresholds
- fold-level and train-candidate record export
- planned execution scale metadata and explicit total-run cap behavior
- public import and documentation examples staying within Stage 4 scope

Out of scope:

- proving trading, order matching, fills, cost, reservation, or execution
  semantics from scratch
- live, paper, short, leverage, margin, multi-symbol, multi-timeframe, or
  portfolio workflows
- source-backed WFA input
- calendar, timestamp, duration, pandas-offset, custom-fold, gap, embargo,
  anchored, or expanding windows
- random, Bayesian, SAMBO, genetic, adaptive, or parallel optimization
- callable objectives or string objective aliases
- stitched OOS equity curves, aggregate account return, `oos_report`, or
  continuous account output
- threshold-based robustness diagnostics
- pandas-only output requirements
- memory-light WFA result mode
- testing private helper names or exact storage layout

## Proposed Test Placement

| Layer | Proposed location | Purpose |
| --- | --- | --- |
| Unit | `tests/unit/research/test_walk_forward_windows.py` | Rolling fold generation, bar-count validation, boundary indexes, timestamps, and `step_size` behavior. |
| Unit | `tests/unit/research/test_walk_forward_preflight.py` | Public input validation, unsupported modes, objective shape, parameter grid shape, total-run cap, and no-run preflight failures. |
| Unit | `tests/unit/research/test_walk_forward_result_summary.py` | Fold counts, OOS metric summaries, metric-state counts, positive-fold ratio, and no stitched account fields. |
| Unit | `tests/unit/research/test_walk_forward_records.py` | Fold-level records, train-candidate records, flat keys, metric-state fields, failure fields, and JSON-safe values. |
| Unit | `tests/unit/research/test_walk_forward_diagnostics.py` | Fact-based diagnostic code, severity, message, affected fold indexes, and non-failing diagnostic behavior. |
| Integration | `tests/integration/research/test_walk_forward_study.py` | Real public WFA workflow with `ParameterStudy`, `BacktestEngine`, `StrategyConfig`, and deterministic `BarSeries`. |
| Integration | `tests/integration/research/test_walk_forward_failures.py` | Candidate failures, selection failures, selected test failures, undefined metrics, no-trade folds, and continue-by-default behavior. |
| Integration | `tests/integration/research/test_walk_forward_records.py` | Real fold records and candidate records remain joinable and portable after real backtest/report execution. |
| Smoke | `tests/smoke/local/test_public_imports.py` | `WalkForwardStudy` remains importable from the public research surface once exported. |
| Structure | `tests/structure/architecture/test_walk_forward_boundaries.py` | WFA lives in research, composes public backtest/parameter-study surfaces, and does not add Tier A dependency drift. |
| Structure | `tests/structure/docs/test_walk_forward_docs.py` | WFA docs/examples avoid unsupported aliases, source-backed input, stitched OOS reports, and trading recommendation claims. |
| Regression | existing regression lane or focused integration regression | Lock previously discovered WFA contract bugs once implementation begins. |

No browser-style E2E tests are required because Stage 4 is a library workflow
with no UI. The closest end-to-end coverage should be a smoke or executable
example test that imports the public surface and runs the canonical small WFA
example without network access.

## Test Data And Fixture Strategy

Use small deterministic fixtures. Large market fixtures are allowed only when a
real regression cannot be expressed clearly with a tiny `BarSeries`.

| Fixture | Shape | Purpose |
| --- | --- | --- |
| `wfa_bars_12` | 12 one-minute bars with monotonic timestamps | simplest complete rolling folds and boundary assertions. |
| `wfa_bars_11` | one bar short of an expected second fold | not-enough-complete-fold and boundary behavior. |
| `wfa_crossing_bars` | bars that trigger a small SMA-style strategy differently across windows | canonical train/test selection example. |
| `wfa_no_trade_bars` | bars that keep a simple strategy flat | no closed trades diagnostic. |
| `wfa_mixed_outcome_bars` | deterministic windows where selected configs produce positive and negative OOS metrics | OOS summary distributions and positive-fold ratio. |
| `CountingEngine` | contract-shaped fake engine recording `run(...)` calls | preflight no-run checks and planned/executed call counts. |
| `StateProbeStrategy` | `Strategy` subclass that exposes whether mutated state or config leaked across runs | fresh strategy state for every train candidate and selected test run. |
| `ConfiguredStrategy` | `Strategy[Config]` with small numeric config fields | config materialization, selected config records, and unknown-field validation. |
| `CandidateRaisesStrategy` | raises for one config value during train execution | train candidate failure without fold failure when another candidate is eligible. |
| `SelectedTestRaisesStrategy` | succeeds in train but raises in selected test for a fold | selected test failure, fold failure, and continuation. |
| `UndefinedMetricStudyCase` | real or minimal result setup with undefined objective metric | selection failure or diagnostic behavior depending on stage. |

Fixture rules:

- Expected fold indexes and timestamps should be visible in the test body.
- Fixture names should describe the behavior they enable, not production helper
  internals.
- Do not reimplement WFA fold generation inside test helpers.
- Do not hide the selected config expectation behind large strategy logic.
- Prefer real `BarSeries`, `TimeBar`, `Strategy`, `StrategyConfig`,
  `BacktestEngine`, and `ParameterStudy` in integration tests.
- Use fakes only where real backtests would obscure the contract or make a
  no-run assertion impossible.

## Mock, Stub, And Fake Policy

Prefer real objects for public contracts:

- real `BarSeries` for fold generation and integration flows
- real `StrategyConfig` subclasses for config materialization
- real `Strategy` subclasses for fresh-state and train/test behavior
- real `BacktestEngine` for selected test execution
- real `ParameterStudy` for train grid search
- real `BacktestResult` and `GridSearchResult` when proving retained results
  and record exports

Allowed fakes:

- fake engine call log for preflight tests that must prove no train or test
  backtest starts
- fake result/report objects only for metric states that cannot be produced
  cheaply through a deterministic real backtest
- fake diagnostic inputs only for unit-testing diagnostic aggregation, not for
  replacing the public WFA integration flow

Avoid:

- mocking private fold-slicing helpers
- asserting private storage field names
- patching `ParameterStudy` merely to avoid a small real train search
- replacing `BacktestEngine` in tests whose purpose is public integration
- interaction assertions when public result state proves the same contract

## Unit Test Scenarios

### U1: Rolling Fold Generation

Purpose: prove WFA creates chronological train/test windows without leaking
future bars into selection.

Scenarios:

| Case | Input | Expected behavior |
| --- | --- | --- |
| one complete fold | 8 bars, `train_size=5`, `test_size=3` | one fold: train `[0, 5)`, test `[5, 8)`. |
| multiple non-overlapping folds | 12 bars, `train_size=4`, `test_size=2`, `step_size=None` | folds start at `0`, `2`, `4`, `6`; resolved `step_size` is `2`. |
| explicit step size | 12 bars, `train_size=4`, `test_size=2`, `step_size=3` | folds start at `0`, `3`, `6`; incomplete trailing windows are omitted. |
| exact boundary | 10 bars, `train_size=6`, `test_size=4` | one fold using all bars. |
| not enough bars | 9 bars, `train_size=6`, `test_size=4` | strict preflight failure before backtests. |

Required assertions:

- train bars always precede test bars
- train and test slices do not overlap within a fold
- positional boundaries are start-inclusive and end-exclusive
- timestamp boundaries record first and last observed bar timestamps
- unsupported modes such as `"expanding"` and `"anchored"` fail clearly

### U2: Window And Input Preflight

Purpose: reject invalid inputs before expensive execution.

Scenarios:

| Case | Input | Expected behavior |
| --- | --- | --- |
| non-`BarSeries` bars | list or arbitrary object | fail before any backtest. |
| empty bars | empty `BarSeries` | fail before any backtest. |
| duplicate timestamps | duplicated bar timestamp | fail before any backtest. |
| out-of-order timestamps | descending or swapped timestamps | fail before any backtest. |
| invalid size type | `"500"`, `1.5`, `True`, `False`, `None` where not allowed | fail before any backtest. |
| invalid size value | `0` or negative `train_size`, `test_size`, `step_size` | fail before any backtest. |
| unsupported mode | `"expanding"` or `"anchored"` | fail before any backtest and name unsupported mode. |
| invalid engine | missing object or object without the public backtest run contract | fail before any backtest. |

Required assertions:

- preflight failures do not create a `WalkForwardResult`
- fake engine call count remains zero
- errors identify the invalid field and enough context to fix the input

### U3: Strategy And Config Preflight

Purpose: keep WFA on the canonical Stage 3.5 strategy construction path.

Scenarios:

| Case | Input | Expected behavior |
| --- | --- | --- |
| strategy class | `strategy=ConfiguredStrategy` | accepted. |
| strategy instance | `strategy=ConfiguredStrategy(...)` | rejected; WFA does not accept pre-constructed instances. |
| callable factory | `strategy=lambda config: ...` | rejected; WFA does not teach callable construction. |
| non-strategy class | arbitrary class | rejected before backtests. |
| unknown config field | `parameters={"missing": [1]}` | rejected before backtests. |
| wrong value type | unsupported config value | rejected before backtests. |

Required assertions:

- accepted candidates materialize declared `StrategyConfig` snapshots
- unknown fields do not reach `ParameterStudy` or `BacktestEngine`
- error messages guide users toward strategy class plus config fields

### U4: Parameter Candidate And Constraint Behavior

Purpose: prove WFA inherits finite-grid behavior without flattening important
candidate states.

Scenarios:

| Case | Input | Expected behavior |
| --- | --- | --- |
| finite grid | two fields with two values each | raw candidate count is visible and deterministic. |
| empty parameter mapping | `{}` | fail before any backtest. |
| empty parameter value list | `{"fast": []}` | fail before any backtest and name `fast`. |
| all rejected by constraint | `constraint=lambda config: False` | each fold records selection failure and no test run. |
| some rejected by constraint | `fast < slow` | rejected candidates remain distinguishable; eligible selected fold can succeed. |
| constraint raises | raises for one config | retained train result records candidate failure; fold can still succeed if another candidate is eligible. |
| constraint returns non-bool | returns `1`, `None`, or `"yes"` | failure behavior follows `ParameterStudy` and remains visible in train result. |

Required assertions:

- rejected candidates are not counted as successful candidates
- rejected combinations are distinguishable from execution failures
- WFA does not fabricate a test result when no candidate is eligible

### U5: Objective Preflight And Selection

Purpose: make the objective contract explicit and deterministic.

Scenarios:

| Case | Input | Expected behavior |
| --- | --- | --- |
| valid max objective | `("returns.total_return", "max")` | accepted and used for train selection. |
| valid min objective | `("risk.max_drawdown", "min")` | accepted and used for train selection. |
| string alias | `"sharpe"` | rejected before backtests. |
| callable objective | function | rejected before backtests. |
| invalid direction | `("returns.total_return", "largest")` | rejected before backtests. |
| unknown metric path | `("missing.metric", "max")` | rejected before any backtest. |
| undefined objective for all rows | no eligible objective values | fold failure at `selection`; no test run. |

Required assertions:

- objective path and direction appear in fold records
- selected config is based on train metrics only
- selected test metrics do not influence selection

### U6: Result Summary Semantics

Purpose: prove `oos_summary` is independent-fold evidence, not a continuous
account.

Scenarios:

| Case | Input | Expected behavior |
| --- | --- | --- |
| two successful OOS folds | finite test metrics | summary includes count, average, median, min, max for numeric metrics. |
| mixed positive and negative return folds | known total returns | summary includes positive-fold ratio for `returns.total_return`. |
| failed fold plus successful fold | one selected test fails | failed fold is included in counts and failure rate, excluded from numeric aggregates. |
| undefined metric state | one successful test has undefined objective metric | state count is recorded and diagnostic is emitted. |
| infinite metric state | metric is positive or negative infinity | state count is recorded without non-standard JSON float leakage. |

Required assertions:

- `oos_summary` includes the chosen objective metric when available
- numeric aggregates use successful selected test folds only
- no aggregate equity, stitched equity curve, aggregate total return, final
  account balance, or live-equivalent account field appears in the first slice

### U7: Diagnostic Semantics

Purpose: keep diagnostics factual and non-authoritative.

Scenarios:

| Case | Trigger | Expected diagnostic |
| --- | --- | --- |
| fold execution failure | selected test or train search failure affects fold | `warning` diagnostic with affected fold index. |
| no selected config | selection failure | `warning` diagnostic with affected fold index. |
| undefined OOS objective | successful test fold lacks objective metric | `warning` diagnostic with affected fold index. |
| no closed trades | successful test fold has no closed trades | `info` or `warning` diagnostic per implementation-plan decision. |
| zero successful OOS folds | every fold fails or is unselected | `warning` diagnostic for study-level result. |

Required assertions:

- diagnostics have `severity`, `code`, `message`, and affected fold indexes
  when applicable
- severities are limited to `info` and `warning`
- diagnostics do not make technically valid WFA runs fail
- no threshold-based diagnostics are emitted for train/test degradation,
  selected-parameter instability, or OOS return concentration

### U8: Record Export

Purpose: make WFA output portable and joinable.

Scenarios:

| Case | Action | Expected behavior |
| --- | --- | --- |
| fold-level export | `result.to_records()` | one flat record per fold. |
| train-candidate export | dedicated candidate export | one or more candidate records with `fold_index`. |
| successful fold | selected config and metrics exist | record includes selected config, train status, test status, selected train metrics, and test metrics. |
| failed fold | selection or test failure | record includes failure stage, `error_type`, and `error_message`. |
| metric states | undefined or infinite metrics | record includes explicit metric-state fields. |

Required assertions:

- record exports do not require pandas
- records are JSON-friendly
- candidate records can be joined to fold records by `fold_index`
- raw exception objects are not stored in public records
- top-level record keys do not collide with user config field names because
  selected config and candidate config snapshots remain nested

### U9: Planned Execution Scale And Guardrails

Purpose: make runtime cost visible while preserving the unlimited default.

Scenarios:

| Case | Input | Expected behavior |
| --- | --- | --- |
| default total cap | no total-run cap | valid run is not rejected solely because of total planned run count. |
| explicit total cap exceeded | cap below planned train candidates plus selected tests | strict preflight failure before any backtest. |
| explicit total cap allowed | cap equal to or above planned total | run proceeds. |
| per-fold candidate cap exceeded | inherited `ParameterStudy.max_candidates` is exceeded | strict preflight failure before any fold starts when raw counts are knowable. |

Required assertions:

- planned fold count, raw candidate count per fold, planned train candidate
  runs, planned selected test runs, and planned total runs are exposed in
  pre-execution metadata when supported and result metadata after execution
- candidates rejected before backtest execution are not counted as executed
  backtests
- explicit cap failures and inherited `max_candidates` failures do not start
  any fold when raw counts are knowable
- tests do not expect a default WFA total-run cap, memory-light result mode, or
  reduced result retention in Stage 4

## Integration Test Scenarios

### I1: Canonical Rolling WFA Workflow

Given:

- a deterministic `BarSeries`
- a real `BacktestEngine`
- a configured strategy class
- a finite parameter grid
- objective `("returns.total_return", "max")`
- `train_size`, `test_size`, and default `step_size`

When:

```python
study = WalkForwardStudy(engine=engine, bars=bars, strategy=ConfiguredStrategy)
result = study.run(
    parameters={"fast": [2, 3], "slow": [4, 5]},
    objective=("returns.total_return", "max"),
    constraint=lambda config: config["fast"] < config["slow"],
    train_size=6,
    test_size=3,
)
```

Then:

- folds are chronological
- each fold retains its train `GridSearchResult`
- successful folds expose `selected_config`
- successful selected tests retain `BacktestResult`
- `oos_summary` is populated from selected test folds
- `to_records()` returns one fold-level row per fold
- no public output implies a continuous account
- fold-level selected config snapshots provide first-slice parameter-stability
  evidence; no separate stability score or summary is expected

### I2: Fresh Strategy State Across Train Candidates And Test Runs

Purpose: prove WFA does not reuse strategy instances across candidates or
folds.

Expected behavior:

- every train candidate receives a fresh strategy instance
- every selected test run receives a fresh strategy instance
- state mutated in one run does not appear in another run
- selected test config equals the selected train config snapshot
- exact constructor-call counts are supporting evidence only; the durable
  contract is that user-visible strategy state and config do not leak between
  runs

### I3: WFA Composes Existing Canonical Paths

Purpose: prove Stage 4 does not introduce a second construction or execution
model.

Expected behavior:

- train search produces the same result shape as `ParameterStudy`
- selected test uses `BacktestEngine.run(strategy=StrategyClass, config=...)`
- report-facing config snapshots use `report.run.strategy_config`
- WFA does not require or expose pre-built strategy instances

### I4: Continue After Fold Failure

Purpose: prove fold-level failures are evidence, not automatic study aborts.

Expected behavior:

- one fold's selected test backtest fails
- the fold has `status="failed"` and failure stage `test_backtest`
- later folds still execute
- result-level success and failed counts match observed fold statuses
- diagnostics include the failing fold

### I5: No Eligible Training Row

Purpose: prove WFA does not fabricate OOS evidence.

Expected behavior:

- a fold with all candidates rejected, failed, or objective-ineligible has
  `status="failed"`
- failure stage is `selection`
- no selected test `BacktestResult` exists for that fold
- later folds continue when possible

### I6: OOS Summary Excludes Failed Folds From Numeric Aggregates

Purpose: prevent misleading summaries.

Expected behavior:

- failed folds, including folds with no selected config, affect fold counts and
  failure rates
- failed folds do not contribute fabricated numeric metrics
- successful OOS folds determine numeric aggregate fields
- when zero folds have successful OOS tests, the summary still exposes counts
  and failure-rate information without numeric aggregate values

### I7: Record Exports From Real Results

Purpose: prove real integration results are portable.

Expected behavior:

- fold records contain boundaries, selected config, statuses, objective path,
  metrics, metric states, failure fields, and error metadata
- fold records keep selected config snapshots nested under `selected_config`
  so user config fields cannot collide with top-level record fields
- train-candidate records include `fold_index`
- records can be serialized with standard JSON encoders after expected
  timestamp handling is applied by the implementation contract

## Structure, Smoke, And Docs Scenarios

### S1: Public Import Smoke

Expected behavior:

- `WalkForwardStudy` is importable from the public research surface selected
  by the implementation plan
- import does not require optional plotting, pandas, network, or live exchange
  dependencies

### S2: Architecture Boundary

Expected behavior:

- WFA code is owned by `quantleet.research`
- WFA composes public `quantleet.backtest`, `quantleet.strategy`, and
  `quantleet.data` contracts
- `trading` and `execution` do not depend on WFA
- no Tier A domain change is required by WFA tests

### S3: Documentation Contract

Expected behavior:

- public examples use `StrategyClass + StrategyConfig`
- public examples use objective tuple syntax, not aliases or callables
- public examples use materialized `BarSeries`, not `source=`
- docs describe WFA as validation evidence, not strategy recommendation
- docs do not show `oos_report`, stitched OOS equity, live trading, paper
  trading, leverage, or multi-symbol examples for Stage 4

### S4: Regression Capture

Expected behavior:

- every blocker or important bug found during Stage 4 implementation receives
  a focused regression test at the narrowest useful level
- regression tests describe the external behavior that broke, not the private
  implementation defect

## What Tests Must Not Assert

Tests must not assert:

- exact private helper function names
- private storage layout
- that WFA manually loops in a particular helper rather than composing public
  contracts
- profitability, tradability, or future performance
- threshold-based quality judgments
- pandas dataframe output as the canonical result
- stitched account values or continuous OOS equity
- exact traceback text
- live exchange connectivity or environment variables

Tests may assert exact public field names once the implementation plan fixes
them as exported contract fields.

## Test Level Priorities

| Priority | Coverage | Reason |
| --- | --- | --- |
| P0 | Canonical WFA workflow integration | Proves the user can run the core Stage 4 validation flow. |
| P0 | Preflight no-run failures | Prevents expensive and misleading partial execution from invalid inputs. |
| P0 | Train/test separation and selected config flow | Protects the core WFA validity claim. |
| P0 | Fold failure recording and continuation | Protects the agreed failure policy. |
| P0 | `oos_summary` independent-fold semantics | Prevents the most dangerous user misunderstanding. |
| P0 | Fold-level records and failure metadata | Makes results inspectable by users and agents. |
| P1 | Diagnostics | Ensures fragile results are visible without overclaiming. |
| P1 | Planned execution scale and explicit cap | Keeps unlimited default understandable and controllable. |
| P1 | Structure/docs/smoke checks | Keeps public surface and documentation aligned. |
| P2 | Regression tests for bugs discovered during implementation | Expands coverage only where real defects prove risk. |

## Success Conditions

The Stage 4 WFA test suite is sufficient when it proves:

- users can run the canonical rolling WFA flow on one materialized `BarSeries`
- WFA selects configs using train windows only
- selected configs are tested on later OOS windows only
- strategy construction uses the canonical class-plus-config path
- WFA composes `ParameterStudy` and `BacktestEngine` instead of bypassing them
- invalid inputs fail before backtests start
- fold-level failures are recorded and later folds continue by default
- no selected config means no fabricated test result
- successful selected test folds retain `BacktestResult`
- folds retain train `GridSearchResult`
- fold-level `selected_config` snapshots are the first-slice parameter-stability
  evidence
- `oos_summary` summarizes independent test folds and excludes stitched
  account semantics
- diagnostics are structured, factual, and non-failing
- record exports are portable, flat, joinable, and pandas-independent
- public examples do not teach unsupported Stage 4 features

## Open Test Questions

The product contract has no open product questions, but the implementation
plan must close these test-detail questions before concrete tests are written:

1. Which exact public module exports `WalkForwardStudy`,
   `WalkForwardResult`, `WalkForwardFold`, diagnostics, and summary types?
2. What are the exact public field names for `oos_summary`, planned execution
   scale metadata, diagnostics, and record exports?
3. How should timestamp values be represented in JSON-friendly record exports:
   datetime objects, ISO-8601 strings, or an existing Quantleet timestamp
   convention?
4. What exact diagnostic code strings should be public and stable?
5. Should a successful test fold with no closed trades emit `info` or
   `warning` in the first implementation?
