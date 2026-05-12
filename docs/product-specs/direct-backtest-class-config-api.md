# Direct Backtest Class+Config API Alignment

## Status

- Status: `draft`
- Class: `product-spec`
- Scope: Stage 3.5 WFA prerequisite for aligning direct backtest execution with
  the canonical `Strategy` plus `StrategyConfig` construction model

Related documents:

- [strategy-configuration-contract.md](strategy-configuration-contract.md)
- [strategy-configuration-contract-test-scenarios.md](strategy-configuration-contract-test-scenarios.md)
- [direct-backtest-class-config-api-test-scenarios.md](direct-backtest-class-config-api-test-scenarios.md)
- [reporting-config-source-of-truth.md](reporting-config-source-of-truth.md)
- [wfa-prerequisite-roadmap.md](wfa-prerequisite-roadmap.md)
- [walk-forward-analysis-readiness.md](walk-forward-analysis-readiness.md)
- [walk-forward-analysis.md](walk-forward-analysis.md)
- [parameter-exploration.md](parameter-exploration.md)
- [parameter-exploration-test-scenarios.md](parameter-exploration-test-scenarios.md)
- [backtest-mvp.md](backtest-mvp.md)
- [research-ergonomics.md](research-ergonomics.md)
- [../design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)

This document defines Stage 3.5 in the WFA prerequisite sequence.

Stage 3.5 is not WFA implementation. It is the direct-backtest API cleanup that
lets direct backtests, `ParameterStudy`, and later WFA share one strategy
construction model.

## Plain-Language Summary

Direct backtests should be written as:

```python
result = engine.run(
    bars=bars,
    strategy=MyStrategy,
    config=MyConfig(fast=10, slow=30),
)
```

The user provides a strategy class and an optional `StrategyConfig` object. The
engine creates a fresh strategy instance for the run.

Config-less and default-config strategies may omit `config`:

```python
result = engine.run(
    bars=bars,
    strategy=MyStrategy,
)
```

When omitted, the engine materializes `MyStrategy.config_type()` and records the
resulting config snapshot in the report.

The older direct-instance style is removed from the current public product
surface:

```python
engine.run(bars=bars, strategy=MyStrategy(MyConfig(...)))
```

This is a pre-beta cleanup. Current docs, examples, smoke tests, and managed
specs should read as if the class-plus-config API was the intended direct
backtest design from the beginning.

## Decision

Stage 3.5 makes `BacktestEngine.run(strategy=StrategyClass, config=...)` the
primary and only current direct-backtest strategy input model.

The accepted public shape is:

```python
engine.run(
    *,
    strategy=StrategyClass,
    config=StrategyConfigInstance | None = None,
    bars=bars,
    source=source,
    label=label,
)
```

Exactly one of `bars` or `source` is still required.

The engine owns strategy instance creation for direct backtests. It must create
a fresh strategy instance for every `run(...)` call.

## Why This Stage Exists

`ParameterStudy` already receives a strategy class, materializes
`StrategyConfig` snapshots, and creates fresh configured strategy instances for
each candidate.

WFA will need the same property across train candidates and selected test
folds. If direct backtesting continues to teach strategy instances while
research studies teach strategy classes, WFA has to bridge two public
construction models.

Stage 3.5 removes that mismatch before WFA resumes.

Market practice supports this direction:

- Backtesting.py receives a strategy subclass and applies run/optimization
  parameters at execution time.
- Backtrader receives strategy classes plus constructor kwargs and instantiates
  during `run()`.
- Freqtrade and NautilusTrader route strategy construction through framework
  loading/configuration rather than asking users to pass arbitrary direct
  strategy instances into a one-off backtest call.
- PyBroker and NautilusTrader both use explicit configuration objects for
  important runtime or strategy settings.

Quantleet does not copy any one library exactly. The chosen shape follows the
common pattern that the framework owns execution-time strategy construction,
while preserving Quantleet's existing `StrategyConfig` contract.

## Goals

- Make direct backtesting use the same strategy-construction vocabulary as
  `ParameterStudy` and future WFA.
- Ensure every direct run uses a fresh strategy instance.
- Keep strategy execution config explicit, typed, immutable, and reportable.
- Preserve config-less quickstarts without ceremony.
- Remove current public examples of direct strategy-instance execution before
  first beta.
- Let WFA Stage 4 focus on folds, OOS summaries, records, and diagnostics
  rather than reopening strategy construction.

## Non-Goals

Stage 3.5 does not define or implement:

- walk-forward analysis
- WFA result objects, fold records, OOS summaries, or diagnostics
- paper or live trading execution
- changes to trading or execution semantics
- a dependency-injection framework
- strategy factories or custom constructor hooks
- arbitrary runtime dependencies such as ML models, clients, sessions, file
  handles, or service objects
- dict input as direct Python API config
- domain-object config serialization beyond the current JSON-scalar
  `StrategyConfig` contract
- compatibility aliases or migration helpers for pre-beta direct-instance
  examples

## Public API Contract

### Strategy Input

`BacktestEngine.run(...)` accepts a strategy class:

```python
strategy: type[Strategy[StrategyConfig]]
```

The strategy argument must be a `Strategy` subclass. Direct strategy instances
are not part of the current public API.

The engine materializes the run strategy as:

```python
materialized_config = config if config is not None else StrategyClass.config_type()
strategy_instance = StrategyClass(materialized_config)
```

The exact internal helper names belong to the implementation plan.

### Config Input

`config` accepts only a `StrategyConfig` instance or `None`.

Accepted:

```python
engine.run(
    bars=bars,
    strategy=SmaCrossStrategy,
    config=SmaCrossConfig(fast=10, slow=30),
)
```

Accepted:

```python
engine.run(
    bars=bars,
    strategy=SmaCrossStrategy,
)
```

Rejected:

```python
engine.run(
    bars=bars,
    strategy=SmaCrossStrategy,
    config={"fast": 10, "slow": 30},
)
```

Plain dict config input is rejected because the Python API already has a typed
`StrategyConfig` contract. Dicts remain appropriate for record output and future
serialization surfaces when a dedicated serialization spec exists.

### Default Config

If `config` is omitted, the engine uses `StrategyClass.config_type()`.

For strategies without declared fields, this produces the empty config snapshot:

```python
result.report.run.strategy_config == {}
```

For strategies with declared defaults, omission means "run with declared
defaults" and the report records the full materialized snapshot.

### Config Type Matching

Config matching is strict.

If `config` is provided, `type(config)` must be exactly
`StrategyClass.config_type`.

Rejected:

```python
engine.run(
    bars=bars,
    strategy=FastSlowStrategy,
    config=OtherConfig(...),
)
```

The run must fail before data loading or backtest execution.

Strict matching preserves the current `Strategy` contract and prevents WFA or
`ParameterStudy` from silently running the wrong config type across many runs.

### Validation And Loading Order

`BacktestEngine.run(...)` validates the strategy class, materializes the config,
creates a fresh strategy instance, and captures the config snapshot before
loading a `source`.

The intended order is:

1. validate `label`
2. validate exactly one of `bars` or `source`
3. validate `strategy` is a strategy class
4. materialize and validate `config`
5. create a fresh strategy instance
6. copy `strategy_config` from the materialized config
7. load `source` or accept `bars`
8. validate `BarSeries`
9. run the backtest

This keeps invalid strategy/config inputs from triggering slow or stateful data
loads.

### Report Snapshot

Reports continue to expose execution config as:

```python
result.report.run.strategy_config
```

The value is the full materialized config snapshot copied before the run starts.
It is a plain mapping for reporting and record output, not the live
`StrategyConfig` object.

### Failure Policy

Invalid public call shapes must fail clearly before backtest execution:

- `strategy` is not a `Strategy` subclass
- `strategy` is an already constructed strategy instance
- `config` is not `None` and not a `StrategyConfig` instance
- `config` is a `StrategyConfig` instance of the wrong exact type
- default config materialization raises
- strategy construction raises

Stage 3.5 should not add a special "forbidden legacy mode" layer. The
implementation should naturally enforce the new public type contract.

## ParameterStudy Alignment

Stage 3.5 changes `ParameterStudy` to call the direct backtest API with the
strategy class and materialized config:

```python
backtest = self.engine.run(
    bars=self.bars,
    strategy=self.strategy,
    config=prepared.config,
    label=f"grid-search-{prepared.run_index}",
)
```

`ParameterStudy` should no longer construct the strategy instance itself before
calling the engine.

This keeps direct backtests, grid search, and future WFA on one execution entry
path.

## Documentation And Example Policy

Stage 3.5 is a pre-beta breaking cleanup.

Current public surfaces should teach only the class-plus-config API:

- README quickstart
- `docs/site` quickstart, guides, examples, and reference pages
- smoke examples
- current product specs and test-scenario specs
- notebooks and managed examples that are current beta-facing material

Historical plans, audits, and previous decision records do not need to be
rewritten unless they are still routed as current product authority.

The intended current example style is:

```python
result = engine.run(
    source=source,
    strategy=SmaCrossStrategy,
    label="sma-cross",
)
```

For configured strategies:

```python
result = engine.run(
    bars=bars,
    strategy=SmaCrossStrategy,
    config=SmaCrossConfig(fast=10, slow=30),
)
```

## Test Policy

Stage 3.5 must have a separate test-scenarios spec:

- [direct-backtest-class-config-api-test-scenarios.md](direct-backtest-class-config-api-test-scenarios.md)

The test-scenarios spec should cover code behavior, `ParameterStudy`
integration, report snapshots, public examples, and documentation cleanup.

Documentation/example checks are split into two classes:

- permanent executable-doc or smoke checks that prove public examples run with
  the class-plus-config API
- temporary transition checks that search current public docs/specs for old
  direct-instance examples during the Stage 3.5 cleanup

Temporary transition checks should not become a permanent hard gate merely
because they were useful during this refactor. After implementation confirms the
current public surface has been cleaned and executable examples remain covered,
old-API grep-style checks should be removed or deliberately reclassified
through a separate repo-check policy decision.

## Relationship To WFA

Stage 4 remains WFA Resume Spec.

After Stage 3.5 is implemented, WFA must not design a separate strategy
construction API. WFA should compose the direct backtest API for train
candidates and selected test runs.

Stage 4 should resume only after Stage 3.5 is completed, or after a human
decision explicitly records why direct-backtest API alignment no longer blocks
WFA planning.

## Success Conditions

Stage 3.5 is successful when:

- direct backtests use strategy classes and optional `StrategyConfig` objects
- direct strategy instances are gone from the current public product surface
- omitted config uses the strategy's default config
- wrong config input fails before data loading
- report `run.strategy_config` records the materialized config snapshot
- `ParameterStudy` uses the direct class-plus-config API
- current public docs and examples teach the new API
- WFA can treat strategy construction as settled input for Stage 4

## Open Questions

- None for the Stage 3.5 product contract.
