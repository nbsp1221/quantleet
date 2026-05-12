# Reporting Config Source Of Truth

## Status

- Status: `implemented`
- Class: `product-spec`
- Scope: current implemented Stage 3 reporting provenance cleanup after the
  `ParameterStudy` strategy API migration and before walk-forward analysis
  resumes

Related documents:

- [strategy-configuration-contract.md](strategy-configuration-contract.md)
- [strategy-configuration-contract-test-scenarios.md](strategy-configuration-contract-test-scenarios.md)
- [direct-backtest-class-config-api.md](direct-backtest-class-config-api.md)
- [wfa-prerequisite-roadmap.md](wfa-prerequisite-roadmap.md)
- [parameter-exploration.md](parameter-exploration.md)
- [parameter-exploration-test-scenarios.md](parameter-exploration-test-scenarios.md)
- [research-ergonomics.md](research-ergonomics.md)
- [backtest-mvp.md](backtest-mvp.md)
- [backtest-plotting.md](backtest-plotting.md)
- [public-beta-documentation.md](public-beta-documentation.md)
- [../design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)
- [../RELIABILITY.md](../RELIABILITY.md)
- [../SECURITY.md](../SECURITY.md)

This document defines the product contract for Stage 3: backtest reports must
record strategy execution configuration from the framework-owned
`StrategyConfig` snapshot, not from strategy-authored self-reporting metadata.

It is not an implementation plan and not a test spec. It defines what must be
true for the public product contract, docs, examples, notebooks, and later WFA
planning.

## Background And Problem Definition

Quantleet's first-beta research workflow now has a canonical strategy
configuration model:

- strategies declare configurable execution settings through
  `Strategy[MyConfig]`
- `StrategyConfig` defines schema, defaults, validation, and immutable
  materialized config snapshots
- `ParameterStudy` expands study-level `parameters={...}` into
  `candidate_parameters` plus full row-level `strategy_config`
- selected study rows expose `best.strategy_config` as the selected execution
  snapshot

The remaining report surface still carries the older model:

- `BacktestReport.run.strategy_parameters` is populated by calling
  `Strategy.parameters()`
- `Strategy.parameters()` lets strategy instances self-report arbitrary
  metadata
- that self-reported metadata can silently disagree with the actual
  `StrategyConfig` that created or configured the run

That mismatch is a source-of-truth problem. A user can select a row whose
`strategy_config` says `{"fast": 5, "slow": 20}` while the corresponding
backtest report can still expose strategy-authored `strategy_parameters` that
say something else. This makes reports harder to trust, harder to compare, and
unsafe as a basis for future WFA fold records.

The problem is not that Quantleet lacks another metadata feature. The problem is
that the same run can appear to have two different configuration truths:

- the framework-owned config snapshot used by research/study workflows
- strategy-authored metadata returned by `Strategy.parameters()`

Stage 3 removes that ambiguity. Report provenance must come from
`StrategyConfig`, and the old `parameters()` reporting hook must stop being part
of the canonical strategy surface.

## Goals

- Make `StrategyConfig` the single source of truth for strategy execution
  configuration in reports.
- Replace report-facing `strategy_parameters` with `strategy_config`.
- Remove `Strategy.parameters()` from the canonical strategy surface.
- Ensure `ParameterStudy` rows and their successful backtest reports cannot
  silently disagree about the selected full config snapshot.
- Preserve lightweight config-less strategies by representing them as
  `strategy_config == {}`.
- Keep `Strategy.display_name` and run labels available as human-readable
  identity metadata, separate from machine-readable execution config.
- Clean up managed current docs, examples, tests, fixtures, and notebooks so
  they teach the new contract only.
- Leave historical/audit records intact unless they read as current product
  authority.
- Keep WFA paused until reporting provenance is no longer ambiguous.

## Non-Goals

This stage does not define or require:

- walk-forward analysis implementation
- a WFA result model
- paper trading or live trading behavior
- WFA-specific usage of `BacktestEngine.run(strategy=StrategyClass,
  config=...)`
- arbitrary custom report metadata such as `metadata={...}`
- a replacement for run `label` or `Strategy.display_name`
- new strategy performance metrics
- new optimization algorithms
- a descriptor/range DSL for strategy parameters
- changelog or release-note rewriting
- compatibility aliases for removed pre-beta report fields

## User Intent

The intended user is a Python quant researcher or developer who needs to know
which exact strategy configuration produced a reported result.

They want to:

- run a direct backtest and inspect a report whose config metadata is
  trustworthy
- run a parameter study and compare rows whose selected configs line up with
  the backtest reports behind those rows
- distinguish the full materialized config from partial search-space overrides
- use simple config-less strategies without unnecessary ceremony
- rely on `display_name` and `label` for readable names without confusing those
  names with execution config
- carry selected configs into future WFA planning without reverse-engineering
  strategy-authored metadata

They are not asking Quantleet to infer hidden constructor arguments, inspect
arbitrary strategy attributes, or provide a general metadata bag.

## Core Requirements

### Single Config Source

The canonical execution-config source for reports is the materialized
`StrategyConfig` snapshot attached to the strategy instance.

Report generation must not call `Strategy.parameters()` and must not preserve
`Strategy.parameters()` as a compatibility fallback.

### Report Field Naming

Reports expose strategy execution config as:

- `report.run.strategy_config`

Reports must not expose the old field as a current or compatibility alias:

- `report.run.strategy_parameters`

The old name is removed because `parameters` now has a specific study-level
meaning: the search-space input passed to `ParameterStudy.grid_search(...)`.
Row-level study results already distinguish partial `candidate_parameters` from
full `strategy_config`; reports must use the same vocabulary.

### Snapshot Shape

`report.run.strategy_config` is a normalized plain mapping:

```python
dict[str, JSON scalar]
```

It contains only public `StrategyConfig` fields and their materialized values.
It is not a live `StrategyConfig` object and not an immutable mapping wrapper.

The snapshot is copied at the start of the backtest run. It represents the run's
input provenance, not strategy runtime state after execution.

### Config-Less Strategies

Strategies without explicit config fields remain valid for direct simple
backtests and examples.

Their report config snapshot is:

```python
{}
```

This is the only supported representation of "no strategy config." It does not
mean the framework should infer constructor arguments or public instance
attributes.

### Strategy Metadata Boundary

`Strategy.display_name` remains supported as human-readable metadata.

Run `label` remains supported as user-visible run identity.

Neither `display_name` nor `label` is execution config. They must not be used as
machine-readable substitutes for `strategy_config`.

`Strategy.parameters()` is removed from the canonical strategy surface rather
than repurposed as a metadata hook.

### Managed Surface Cleanup

Current managed product surfaces must move to the new contract:

- source code and type/protocol contracts
- active tests and fixtures
- public docs under `docs/site`
- README examples and current beta documentation
- current product specs and test specs
- notebooks and smoke examples
- canonical report snapshots

Historical/audit material may keep older terms when it is clearly describing
past decisions, previous plans, or problem background. Historical material must
not be edited merely to erase audit history.

If a historical-looking document is still routed as current product authority,
its current-contract language must be updated.

## Functional Requirements

### Direct Backtest Reporting

Given a strategy class plus materialized config, a direct backtest report
exposes the full config snapshot in `report.run.strategy_config`.

Example expected product shape:

```python
class SmaConfig(StrategyConfig):
    fast: int = 5
    slow: int = 20


class SmaStrategy(Strategy[SmaConfig]):
    ...


result = engine.run(bars=bars, strategy=SmaStrategy, config=SmaConfig(fast=10))

result.report.run.strategy_config
# {"fast": 10, "slow": 20}
```

The report does not expose `strategy_parameters`.

### ParameterStudy Reporting Alignment

For every successful `ParameterStudy` row:

- `row.strategy_config` is the selected or attempted full config snapshot
- `row.backtest.report.run.strategy_config` matches that same full snapshot
- `row.candidate_parameters` remains the partial override audit trail

The report must not become the source of truth for study selection. The row and
the report must agree because both are derived from the same materialized
config snapshot.

### Config-Less Direct Run

A strategy with no explicit config fields produces:

```python
result.report.run.strategy_config == {}
```

This behavior preserves low-ceremony examples and simple strategies without
reintroducing strategy-authored self-reporting.

### Managed Example Migration

Managed examples that expose tunable strategy settings must express those
settings through `StrategyConfig`.

Examples may remain config-less only when their strategy has no user-tunable
execution settings worth reporting.

Constructor arguments may still exist for advanced manual Python use, but
managed docs and examples must not teach constructor arguments as the canonical
way to express reportable strategy settings.

### Notebook Migration

Tracked notebooks are part of the managed current surface.

If a notebook teaches or executes tunable strategy settings, it must use the
config-backed pattern. Notebook validation remains part of completion evidence
for the eventual implementation slice.

### StrategyLike Contract

Any strategy-like object accepted by the backtest runtime must provide config
metadata compatible with the report contract.

Objects that do not provide a valid config snapshot are outside the Stage 3
runtime contract. The product does not define a fallback that silently reports
`{}` for invalid custom strategy-like objects.

## Non-Functional Requirements

- The contract must be simple enough for first-beta users to understand:
  execution config lives in `StrategyConfig`.
- Report config snapshots must be deterministic, portable, and suitable for
  JSON/CSV-style records.
- The reporting contract must not depend on strategy-authored self-reporting
  callbacks.
- The migration must be breaking and clean before public beta; compatibility
  aliases must not preserve the old ambiguity.
- The design must preserve capability ownership:
  - `quantleet.strategy` owns strategy config semantics
  - `quantleet.backtest` owns historical runtime reporting
  - `quantleet.research` composes those surfaces for studies
- The stage must not create Tier A trading or execution behavior.
- Errors caused by invalid custom strategy-like config contracts should be
  visible rather than hidden by fallback metadata.
- The product contract must not imply that selected or optimized configs are
  trading recommendations.

## Key Scenarios

### Scenario 1: Configured Strategy Direct Backtest

A user defines `StrategyConfig`, constructs a strategy with an override, and
runs a direct backtest.

The report's run manifest exposes the full config snapshot used for that run.
Defaults not explicitly overridden are still present.

### Scenario 2: Config-Less Quickstart Strategy

A user writes a minimal strategy without tunable settings.

The direct backtest remains valid and the report records `strategy_config == {}`.

### Scenario 3: ParameterStudy Selected Row Inspection

A user runs a grid search, calls `best()`, and inspects the selected run.

The selected row's `strategy_config` and the selected run report's
`strategy_config` match exactly. The user does not need to inspect
`Strategy.parameters()` or parse formatted report text.

### Scenario 4: Config-Derived Display Name

A strategy returns a readable display name derived from config values, such as
`"SMA 5/20"`.

The report may show that display name, but the machine-readable execution
config remains `strategy_config`.

### Scenario 5: Managed Example With Tunable Parameters

A public example teaches an RSI or SMA strategy with tunable periods and
thresholds.

Those values are modeled as `StrategyConfig` fields and accessed through
`self.config`, so the report records them automatically.

### Scenario 6: Historical Audit Document

A completed plan or research note refers to `strategy_parameters` while
describing the older state of the system.

That historical reference may remain if it is clearly audit history and not
current guidance.

## Edge Cases And Failure Scenarios

- A strategy overrides or still defines `parameters()`: the method is no longer
  part of the canonical surface and must not affect report config.
- A managed current example uses `parameters()` to feed report metadata: the
  example is stale and must be migrated.
- A report fixture still includes `strategy_parameters`: the fixture represents
  the old contract and must be updated.
- A `ParameterStudy` successful row has a `strategy_config` that differs from
  its `backtest.report.run.strategy_config`: this is a product-contract
  failure.
- A strategy stores tunable execution settings only in constructor attributes:
  managed current examples should migrate those settings to `StrategyConfig`.
  Unmanaged user code may still do this, but those hidden values are not
  reportable execution config.
- A config-less strategy reports `{}` even if it has internal runtime state.
  Internal runtime state is not strategy config.
- A custom strategy-like object lacks config metadata: this is outside the
  valid runtime/reporting contract and should fail visibly rather than silently
  falling back.
- A config snapshot contains non-JSON-safe objects: that violates the
  `StrategyConfig` contract rather than the reporting contract.
- A user wants arbitrary run notes or experiment metadata: Stage 3 does not add
  this feature; existing `label` and `display_name` remain the available
  identity fields.
- A public doc explains pre-Stage 3 behavior as current guidance: the doc is
  stale and must be updated.

## External Contracts

Stage 3 exposes the following contracts to users and downstream specs:

- `StrategyConfig` is the only canonical source for reportable strategy
  execution config.
- `Strategy.parameters()` is not part of the canonical strategy surface.
- `BacktestReport.run.strategy_config` is the report-facing full config
  snapshot.
- `BacktestReport.run.strategy_parameters` is removed, not retained as an
  alias.
- `strategy_config` is a plain `dict[str, JSON scalar]`.
- Config-less strategies report `{}`.
- `Strategy.display_name` and `BacktestEngine.run(..., label=...)` remain
  human-readable identity metadata.
- Public docs and managed examples teach config-backed tunable strategy
  settings.
- Historical/audit references may preserve older terminology only when they are
  not current product authority.
- WFA cannot resume on ambiguous report metadata.

The following contracts remain outside Stage 3:

- a future direct backtest class-plus-config API
- any explicit config override parameter on direct `BacktestEngine.run(...)`
- custom metadata bags
- WFA fold result shape

## Success Conditions

This product spec is successful when later test specs and implementation plans
can use it to verify that:

- report-facing config provenance comes from `StrategyConfig`
- `Strategy.parameters()` no longer affects reports or managed current docs
- `strategy_parameters` is absent from current report contracts and managed
  current surfaces
- `strategy_config` appears consistently across `ParameterStudy` rows and
  backtest reports
- config-less strategies remain simple and report `{}` cleanly
- tunable managed examples use `StrategyConfig`
- notebooks can be validated against the new contract
- historical/audit documents remain available without confusing current users
- WFA planning can depend on report config snapshots without reopening the
  source-of-truth question

## Resolved Follow-On Decisions

Stage 3 has no remaining product questions that should block writing its test
spec. The following adjacent decisions are resolved for planning continuity:

- Stage 3 completion should have a dedicated product-test spec before
  implementation planning.
- Stage 3.5 direct-backtest API alignment makes
  `BacktestEngine.run(strategy=StrategyClass, config=...)` the primary direct
  backtest API.
- The existing instance-based `BacktestEngine.run(strategy=...)` path is
  removed from the current public direct-backtest surface in Stage 3.5.
- Direct-backtest class-plus-config API alignment should be treated as a WFA
  prerequisite immediately after Stage 3, not as general future cleanup. This
  follow-on is tracked as Stage 3.5 in
  [direct-backtest-class-config-api.md](direct-backtest-class-config-api.md).
- Arbitrary run metadata remains out of scope. Quantleet should not add a
  distinct metadata bag until a concrete user need justifies the API,
  serialization, and safety policy.
- Future domain-object config serialization is out of scope for Stage 3 and
  must not weaken the first-beta JSON-scalar report contract. If strategy
  configs later need instruments, venues, bar types, decimal quantities, or
  other domain objects, that work needs a separate config-serialization product
  spec.
- Public docs should teach only the current canonical contract. Do not add a
  public migration note for pre-release `Strategy.parameters()` examples unless
  a later release-documentation pass decides that external readers need it.

## Open Questions

- None for the Stage 3 reporting source-of-truth product contract.
