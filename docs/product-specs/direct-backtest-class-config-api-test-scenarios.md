# Direct Backtest Class+Config API Test Scenarios

## Status

- Status: `draft`
- Class: `product-test-scenarios`
- Scope: Stage 3.5 test target for direct backtest class-plus-config API
  alignment

Related documents:

- [direct-backtest-class-config-api.md](direct-backtest-class-config-api.md)
- [strategy-configuration-contract.md](strategy-configuration-contract.md)
- [strategy-configuration-contract-test-scenarios.md](strategy-configuration-contract-test-scenarios.md)
- [reporting-config-source-of-truth.md](reporting-config-source-of-truth.md)
- [reporting-config-source-of-truth-test-scenarios.md](reporting-config-source-of-truth-test-scenarios.md)
- [parameter-exploration.md](parameter-exploration.md)
- [parameter-exploration-test-scenarios.md](parameter-exploration-test-scenarios.md)
- [wfa-prerequisite-roadmap.md](wfa-prerequisite-roadmap.md)
- [walk-forward-analysis-readiness.md](walk-forward-analysis-readiness.md)
- [backtest-mvp.md](backtest-mvp.md)
- [research-ergonomics.md](research-ergonomics.md)
- [public-beta-documentation.md](public-beta-documentation.md)

This document defines the tests that should prove Stage 3.5 is complete before
WFA resume planning.

It is not an implementation plan. It describes the behavior, documentation, and
transition checks the implementation plan should turn into concrete tests.

## What Good Tests Mean For This Stage

Stage 3.5 changes a public API shape. Good tests for this slice must protect
the user-facing contract, not merely execute the new branch once.

Good tests are:

- **contract-focused**: they assert the public call shape and observable result,
  not private helper names
- **fresh-instance aware**: they prove each `engine.run(...)` creates a new
  strategy instance and does not reuse state from another run
- **preflight-oriented**: they prove invalid strategy/config inputs fail before
  data loading or backtest execution
- **provenance-aware**: they assert `report.run.strategy_config` records the
  materialized config snapshot used for execution
- **composition-focused**: they prove `ParameterStudy` uses the same direct
  class-plus-config API instead of a parallel construction path
- **documentation-aware**: they keep current public examples aligned with the
  new API while avoiding permanent brittle grep gates for transition-only
  cleanup
- **small and deterministic**: they use tiny checked-in bars and local fake
  sources, with no network access and no environment-variable dependency

Bad tests for this stage include:

- tests that assert private helper function names
- tests that only check type annotations without executing the public call
- tests that keep both old and new APIs alive for compatibility
- tests that rely on slow market fixtures when a two- or three-bar fixture is
  enough
- long-lived text scans that fail future docs for harmless historical mentions
  of the old API

## Test Taxonomy

Use four test classes.

### Unit Contract Tests

Purpose:

- lock call-shape validation, config materialization, error timing, and fresh
  strategy construction around `BacktestEngine.run(...)`

Likely location:

- `tests/unit/backtest/test_engine.py`
- `tests/unit/backtest/test_direct_class_config_api.py`

### Integration Contract Tests

Purpose:

- prove the real backtest path, report builder, and research composition work
  together with the new API

Likely location:

- `tests/integration/research/test_backtest_engine_entrypoints.py`
- `tests/integration/research/test_backtest_result_reporting_contract.py`
- `tests/integration/research/test_parameter_study_grid_search.py`
- `tests/integration/strategy/test_strategy_config_construction.py`

### Public Example And Smoke Tests

Purpose:

- prove public beta examples execute using the new API

Likely location:

- `tests/smoke/local/test_public_beta_examples.py`
- `tests/smoke/local/test_backtest_result_reporting_quickstart.py`
- existing docs/site or README structure tests where they execute snippets

These are permanent tests when they execute public examples or assert current
beta examples still run.

### Temporary Transition Checks

Purpose:

- prevent missed old direct-instance examples while Stage 3.5 edits current
  public docs and managed specs

Likely location:

- a temporary structure test under `tests/structure/docs/`
- a narrow one-off implementation-plan checklist

These checks are not automatically permanent hard gates. After implementation
confirms current public docs/examples/specs have been cleaned and executable
examples remain covered, old-API grep-style checks should be removed unless a
separate repo-check policy decision promotes them.

## Core Scenarios

### U1: Direct Backtest Accepts Strategy Class And Explicit Config

Given:

- a `StrategyConfig` subclass with fields such as `fast` and `slow`
- a `Strategy[ThatConfig]` subclass
- a small valid `BarSeries`

When:

```python
result = engine.run(
    bars=bars,
    strategy=ConfiguredStrategy,
    config=ConfiguredConfig(fast=5, slow=20),
)
```

Then:

- the run succeeds
- the strategy instance receives `ConfiguredConfig(fast=5, slow=20)`
- `result.report.run.strategy_config == {"fast": 5, "slow": 20}`

This is the primary happy path.

### U2: Direct Backtest Accepts Strategy Class With Omitted Config

Given:

- a strategy with declared config defaults

When:

```python
result = engine.run(
    bars=bars,
    strategy=ConfiguredStrategy,
)
```

Then:

- the run succeeds
- the engine materializes `ConfiguredStrategy.config_type()`
- report `strategy_config` contains the full default snapshot

### U3: Config-Less Strategy Produces Empty Config Snapshot

Given:

- a simple `Strategy` subclass with no declared config fields

When:

```python
result = engine.run(
    bars=bars,
    strategy=ConfigLessStrategy,
)
```

Then:

- the run succeeds
- `result.report.run.strategy_config == {}`

This preserves the quickstart ergonomics.

### U4: Wrong Config Type Fails Before Data Loading

Given:

- `ExpectedStrategy.config_type is ExpectedConfig`
- an instance of `OtherConfig`
- a fake `source` whose `load()` method records whether it was called

When:

```python
engine.run(
    source=source,
    strategy=ExpectedStrategy,
    config=OtherConfig(...),
)
```

Then:

- the call fails before `source.load()`
- the error identifies the strategy/config mismatch
- no backtest execution starts

This proves strict matching and early failure.

### U5: Dict Config Input Is Rejected

Given:

- a configured strategy class

When:

```python
engine.run(
    bars=bars,
    strategy=ConfiguredStrategy,
    config={"fast": 5, "slow": 20},
)
```

Then:

- the call fails before backtest execution
- the error explains that `config` must be a `StrategyConfig` instance or
  omitted

### U6: Strategy Instance Input Is Rejected

Given:

- a constructed strategy instance

When:

```python
engine.run(
    bars=bars,
    strategy=ConfiguredStrategy(ConfiguredConfig(...)),
)
```

Then:

- the call fails before backtest execution
- no compatibility branch converts the instance back into supported input

The exact exception type belongs to the implementation plan, but the user-facing
message should clearly point to `strategy=StrategyClass, config=...`.

### U7: Non-Strategy Class Input Is Rejected

Given:

- a class that is not a `Strategy` subclass

When:

```python
engine.run(
    bars=bars,
    strategy=NotAStrategy,
)
```

Then:

- the call fails before backtest execution
- the error states that `strategy` must be a `Strategy` class

### U8: Default Config Materialization Failure Fails Early

Given:

- a strategy whose `config_type()` raises during default materialization or
  validation
- a fake `source` that records whether it was loaded

When:

```python
engine.run(
    source=source,
    strategy=BadDefaultConfigStrategy,
)
```

Then:

- the call fails before `source.load()`
- the failure is reported as config materialization or validation failure

### U9: Strategy Construction Failure Fails Early

Given:

- a strategy class whose constructor raises for a valid config object
- a fake `source` that records whether it was loaded

When:

```python
engine.run(
    source=source,
    strategy=RaisingStrategy,
    config=RaisingStrategyConfig(...),
)
```

Then:

- the call fails before `source.load()`
- the strategy-construction exception is visible

This distinguishes config validation from strategy construction.

### U10: Every Direct Run Uses A Fresh Strategy Instance

Given:

- a strategy class that records instance identities or increments an instance
  creation counter

When:

```python
first = engine.run(bars=bars, strategy=CountingStrategy)
second = engine.run(bars=bars, strategy=CountingStrategy)
```

Then:

- two distinct strategy instances were created
- no runtime state leaks from the first run to the second

Avoid asserting private runtime details. Use a small observable counter or
strategy-authored test hook local to the test.

## Integration Scenarios

### I1: Source-Based Direct Run Uses New API

Given:

- a real local `HistoricalDataSource`
- a config-less strategy class

When:

```python
result = engine.run(
    source=source,
    strategy=StrategyClass,
    label="research-run",
)
```

Then:

- the run succeeds
- report run metadata includes the label and empty strategy config
- no direct strategy instance appears in the test call

### I2: BarSeries-Based Direct Run Uses New API

Given:

- a materialized `BarSeries`
- a configured strategy class

When:

```python
result = engine.run(
    bars=bars,
    strategy=StrategyClass,
    config=StrategyConfigInstance,
)
```

Then:

- the run succeeds through the real runtime path
- report config matches the provided config snapshot

### I3: Exactly One Of Bars Or Source Still Applies

Given:

- valid strategy class and config input

When:

- neither `bars` nor `source` is provided
- both `bars` and `source` are provided

Then:

- each call fails before strategy execution

This confirms Stage 3.5 changes strategy construction, not data input rules.

### I4: ParameterStudy Uses The Direct Class+Config API

Given:

- a small parameter grid
- a test engine or spy engine that records its `run(...)` call arguments

When:

```python
ParameterStudy(
    engine=engine,
    bars=bars,
    strategy=ConfiguredStrategy,
).grid_search(parameters={...})
```

Then:

- the engine receives `strategy=ConfiguredStrategy`
- the engine receives `config=prepared_config`
- the study does not pass a preconstructed strategy instance
- row `strategy_config` and row backtest report `strategy_config` agree

Use a focused spy test for call shape and an integration test for real
`BacktestEngine` behavior.

### I5: ParameterStudy Failure Stages Remain Distinguishable

Given:

- one candidate that fails config materialization
- one candidate that fails strategy construction
- one candidate whose backtest fails

When:

```python
result = study.grid_search(parameters=..., fail_fast=False)
```

Then:

- config failures remain rejected or failed according to the existing
  `ParameterStudy` contract
- strategy construction failures remain attributed to
  `"strategy_construction"`
- backtest failures remain attributed to `"backtest"`

Stage 3.5 must not collapse nested-study failure diagnostics.

## Reporting Scenarios

### R1: Report Snapshot Uses Materialized Explicit Config

Given:

- explicit config with one overridden value and one default value

When:

```python
result = engine.run(
    bars=bars,
    strategy=StrategyClass,
    config=Config(fast=5),
)
```

Then:

- `result.report.run.strategy_config` includes both the override and defaults
- the report does not expose old `strategy_parameters`

### R2: Report Snapshot Is A Copy

Given:

- a config object used in a direct run

When:

- the report is inspected after the run

Then:

- `report.run.strategy_config` is a plain mapping snapshot
- it is not the live `StrategyConfig` object
- mutating returned record copies cannot mutate the original config

## Documentation And Public Example Scenarios

### D1: README Quickstart Teaches The New API

The README quickstart should show:

```python
result = engine.run(
    source=source,
    strategy=SmaCrossStrategy,
    label="sma-cross",
)
```

It should not teach direct construction in the current quickstart:

```python
strategy=SmaCrossStrategy()
```

### D2: Docs Site Backtesting Guide Teaches The New API

Current public docs under `docs/site` should use:

```python
engine.run(source=source, strategy=StrategyClass, ...)
engine.run(bars=bars, strategy=StrategyClass, config=Config(...), ...)
```

They should not present direct strategy instances as the current recommended
path.

### D3: Smoke Examples Execute With The New API

Smoke examples should run actual public workflows with strategy classes and
optional config objects.

Permanent smoke coverage should focus on executable examples, not broad text
searches.

### D4: Current Product Specs And Test Specs Are Updated

Current authority docs should describe direct backtests through the class-plus
config API.

Examples:

- `backtest-mvp.md`
- `research-ergonomics.md`
- `parameter-exploration.md`
- `reporting-config-source-of-truth.md`
- current test-scenarios specs that show direct backtests

Historical plans and completed audit records may keep old examples when they
describe past work and are not routed as current product authority.

## Temporary Transition Checks

### T1: Old Direct-Instance Examples Are Absent From Current Public Surface

During Stage 3.5 implementation, a temporary structure check may search current
public docs and examples for patterns such as:

```python
engine.run(..., strategy=SomeStrategy(...))
BacktestEngine(...).run(..., strategy=SomeStrategy(...))
```

The check should be scoped narrowly to current public surfaces:

- `README.md`
- `docs/site/`
- current product specs and test-scenarios specs
- smoke/local examples or tests that double as public examples

The check should exclude:

- `docs/plans/`
- historical audit material
- changelog entries that intentionally describe past changes
- implementation tests where the old input is deliberately asserted to fail

### T2: Temporary Checks Are Removed Or Reclassified After Cleanup

After Stage 3.5 implementation proves the current public surface is clean and
executable examples remain covered, temporary old-API text checks should not
linger as accidental permanent gates.

The implementation plan must choose one of:

- remove the transition-only structure check before closing the slice
- keep it only with an explicit evaluator note that it is temporary and must be
  removed in the same slice after docs are cleaned
- promote a narrowed permanent rule through a separate repo-check governance
  decision

The default recommendation is removal after cleanup.

## Negative Scenarios

### N1: Old API Is Not Kept As Compatibility

Tests should not prove the old API still works.

Avoid:

```python
result = engine.run(bars=bars, strategy=StrategyClass(Config(...)))
assert result.report.run.strategy_config == ...
```

The only old-API behavior worth testing is that current public direct-instance
input fails clearly.

### N2: Dict Config Is Not Silently Materialized

Tests should not normalize dicts into config objects inside `engine.run(...)`.

Any future dict serialization path needs a separate product spec.

### N3: WFA Does Not Get A New Construction API

When WFA planning resumes, tests should assume the Stage 3.5 direct API is the
strategy construction path. Do not add WFA-only strategy factory tests unless a
later human decision explicitly reopens this policy.

## Verification Lane For Implementation

Stage 3.5 implementation touches runtime-sensitive backtest and research paths.
The implementation plan should run at least:

```bash
uv run poe verify-runtime
uv run poe verify
```

Useful targeted commands during development:

```bash
uv run pytest tests/unit/backtest -q
uv run pytest tests/unit/research -q
uv run pytest tests/integration/research -q
uv run pytest tests/integration/strategy -q
uv run pytest tests/smoke/local -q
uv run poe repo-check
```

The final evaluator should cite fresh output from the commands selected by the
implementation plan.

## Success Conditions

The Stage 3.5 test target is complete when:

- direct backtests through strategy class plus explicit config are tested
- direct backtests through strategy class plus omitted config are tested
- config-less strategies still work and report `{}`
- wrong config type, dict config, non-strategy input, and direct strategy
  instance input fail before execution
- at least one test proves invalid config does not load a source
- report config snapshots are tested for explicit and default configs
- `ParameterStudy` is tested to call the new direct API
- public smoke examples execute with the new API
- current public docs/examples are cleaned during implementation
- temporary old-API text checks are removed or explicitly not promoted after
  cleanup
