# Strategy Configuration Contract Spec

## Status

- Status: `draft`
- Class: `product-spec`
- Scope: Stage 1 unified strategy configuration contract before
  `ParameterStudy` migration, reporting metadata changes, and walk-forward
  analysis resume

Related documents:

- [strategy-configuration-contract-test-scenarios.md](strategy-configuration-contract-test-scenarios.md)
- [wfa-prerequisite-roadmap.md](wfa-prerequisite-roadmap.md)
- [walk-forward-analysis-readiness.md](walk-forward-analysis-readiness.md)
- [walk-forward-analysis.md](walk-forward-analysis.md)
- [parameter-exploration.md](parameter-exploration.md)
- [research-ergonomics.md](research-ergonomics.md)
- [backtest-mvp.md](backtest-mvp.md)
- [../design-docs/unified-strategy-runtime-design.md](../design-docs/unified-strategy-runtime-design.md)
- [../design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)

This document defines the product contract for strategy configuration. It is not
an implementation plan and does not resume WFA implementation. It intentionally
records several downstream decisions for `ParameterStudy` and reporting so those
stages do not rediscover or contradict the Stage 1 contract.

Functional requirements in this document have two roles:

- Stage 1 defines the shared strategy configuration contract and any
  contract-level discovery, materialization, and validation behavior needed to
  make that contract observable.
- Stage 2 and Stage 3 apply the contract to `ParameterStudy` and reporting.
  Requirements labeled as downstream are not required to ship in the first
  Stage 1 implementation slice.

## Background And Problem Definition

Quantleet currently has a useful first-beta research loop:

- users subclass `Strategy`
- `BacktestEngine.run(...)` executes a `Strategy` class with an optional
  `StrategyConfig` instance after Stage 3.5 alignment
- `ParameterStudy(...).grid_search(...)` runs finite parameter grids through a
  user-provided legacy callable construction API
- `BacktestReport.run.strategy_parameters` is populated from
  `Strategy.parameters()`

This works for the current beta surface, but it is the wrong contract to harden
for a framework intended to support coherent backtest, research, paper trading,
and future live trading workflows.

The WFA product discussion exposed the problem. Walk-forward analysis needs to
repeat the following pattern across train and test folds:

1. materialize a candidate strategy configuration
2. create a fresh strategy instance
3. run a backtest
4. record which full configuration was actually used
5. select a configuration on the train slice
6. recreate a fresh strategy with that selected configuration on the test slice
7. report fold-level out-of-sample outcomes without confusing selected values,
   defaults, and runtime metadata

If Quantleet builds WFA directly on the current legacy callable construction API public API,
the product risks turning a transitional implementation adapter into a durable
user-facing contract. The issue is not the WFA algorithm itself. The issue is
that Quantleet does not yet have a canonical strategy configuration contract.

The current `Strategy.parameters()` hook also creates a source-of-truth problem.
It asks the strategy instance to self-report metadata, but it does not guarantee
that the reported values match the configuration that created the strategy or
the values selected by a study.

This spec solves the product-contract problem before implementation continues.

## Goals

- Define Quantleet's canonical strategy configuration model.
- Make strategy configuration explicit enough for the framework to discover,
  validate at a basic level, materialize, record, and later serialize.
- Keep ordinary strategy authoring lightweight enough for a Pine Script-like
  first-run DX.
- Separate strategy configuration schema/defaults from study-specific search
  spaces.
- Make full materialized config snapshots the source of truth for execution and
  reporting.
- Preserve fresh strategy construction as a framework guarantee for study
  workflows.
- Remove the old callable construction path from active study workflows so the
  config-backed `strategy=StrategyClass` contract is the only public study UX.
- Record downstream decisions needed for `ParameterStudy` migration and
  reporting metadata cleanup without requiring all downstream migrations in one
  implementation slice.
- Keep WFA paused until the prerequisite strategy configuration and reporting
  contracts are resolved.

## Non-Goals

This spec does not define or require:

- WFA implementation
- a full WFA resume plan
- a full paper-trading or live-trading runner
- a dependency-injection container
- a Freqtrade-style parameter descriptor DSL such as `IntParameter(...)`
- min/max, categorical-choice, or domain-specific parameter validation
- objective aliases such as `objective="sharpe"`
- callable objectives
- new optimization algorithms
- `BacktestEngine.run(strategy=StrategyClass, config=...)` as a required first
  implementation slice
- backward compatibility as a blocker for the current unpublished beta

## User Intent

The intended user is a Python quant researcher or developer who wants a compact
strategy authoring experience without giving up reproducibility and future
portability.

They want to:

- write a strategy with minimal ceremony
- define strategy defaults once
- run the same strategy through direct backtests, parameter studies, and future
  WFA without rewriting construction logic
- understand which configuration values were actually used for a run
- trust that study result rows, selected configurations, and report metadata do
  not silently disagree
- vary search spaces per experiment without editing the strategy source
- avoid ad hoc construction boilerplate for ordinary strategies
- use custom strategy constructors only when they preserve the framework config
  contract

They are not asking Quantleet to infer profitable strategies or hide
overfitting risk. They are asking Quantleet to make the strategy configuration
contract clear enough that validation studies can be trusted.

## Core Requirements

### Canonical Contract

Quantleet's canonical strategy contract is a `Strategy` class paired with an
explicit, framework-recognizable strategy configuration schema.

In the first version, the product expression for this schema is `StrategyConfig`.
The important product requirement is not the exact implementation shape. The
important requirement is that strategy settings are not hidden inside arbitrary
lambda factories.

Canonical user-facing DX should require only the strategy generic declaration
when the relationship is unambiguous:

```python
class RSIStrategyConfig(StrategyConfig):
    rsi_period: int = 14
    oversold: float = 30.0


class RSIStrategy(Strategy[RSIStrategyConfig]):
    def on_bar(self, bar) -> None:
        period = self.config.rsi_period
```

Users should not need to repeat `config_type = RSIStrategyConfig` in the
canonical path. An explicit `config_type` may exist only as an advanced fallback
or migration compatibility path when runtime inference is impossible or
intentionally avoided.

`config_type = MyConfig` is a public advanced fallback, not an internal-only
escape hatch. The canonical docs and examples should teach `Strategy[Config]`,
but advanced users may declare `config_type` directly. If `Strategy[Config]`
and `config_type = Config` both declare the same config type, the declaration is
accepted as redundant. If they declare different config types, Quantleet must
fail config-contract validation immediately.

`Strategy[Config]` is the canonical user-facing declaration. The technical plan
may decide whether the implementation derives the effective schema through
generic introspection, subclass registration, or another internal mechanism.
What must be observable is that Quantleet can discover exactly one effective
`StrategyConfig` schema for a canonical strategy class.

Stage 1 does not expose `discover_config_schema(...)` or
`materialize_config(...)` as user-facing public APIs. Discovery,
materialization, and normalization may be implemented as internal or
framework-owned runtime behavior. The user-facing contract is the
`Strategy[Config]` declaration, framework-owned construction/normalization, and
the resulting config instance plus normalized snapshot.

The following are config-contract validation failures and must be detected
before grid expansion or backtest execution:

- a non-empty study search space targets a strategy with no declared config
  schema
- a declared config type is not a `StrategyConfig`
- more than one config declaration is present and they conflict
- a fallback `config_type` conflicts with the canonical generic declaration

### StrategyConfig Versus Study Parameters

`StrategyConfig` and study-level `parameters={...}` are different concepts.

- `StrategyConfig` defines the strategy's configurable schema and default
  values.
- Study-level `parameters` define the search space for a specific research run.
- A study candidate is a partial override derived from that search space.
- A materialized config snapshot is the full effective configuration used or
  intended for one run.

Example:

```python
class RSIStrategyConfig(StrategyConfig):
    rsi_period: int = 14
    oversold: float = 30.0
    risk_per_trade: float = 0.01
```

```python
result = ParameterStudy(
    engine=engine,
    bars=bars,
    strategy=RSIStrategy,
).grid_search(
    parameters={
        "rsi_period": [7, 14, 21],
        "oversold": [20.0, 30.0, 40.0],
    },
    objective=("risk.sharpe_ratio", "max"),
)
```

The candidate `{ "rsi_period": 7, "oversold": 20.0 }` materializes to the full
config snapshot:

```python
RSIStrategyConfig(
    rsi_period=7,
    oversold=20.0,
    risk_per_trade=0.01,
)
```

Study-level `parameters` are partial config override sets, not standalone
strategy inputs.

### Materialized Config Snapshot

The materialized `StrategyConfig` snapshot is the canonical source of execution
configuration for studies, backtests created through canonical class+config
paths, and reports.

Runtime strategy code receives a `StrategyConfig` instance as `self.config`.
Study, report, and export-facing surfaces expose the same effective values as a
normalized plain mapping. The mapping is derived from the materialized config
and is the stable comparison/reporting shape.

The MVP materialization rule is:

```text
full config = StrategyConfig defaults + candidate overrides
```

Future specs may add a base-config override layer:

```text
full config = StrategyConfig defaults + base config override + candidate overrides
```

That extension must not change the Stage 1 rule that reports and study results
center the full materialized config snapshot, not the partial candidate mapping.

### Immutability Contract

Materialized strategy configs are immutable run snapshots. Strategy code must
not mutate its config during a run. The executed config snapshot and reported
config snapshot must refer to the same effective values.

This is an enforced product contract, not merely a documentation convention.
Runtime `self.config` field reassignment must fail fast with a public config
mutation error. Normalized snapshot mappings must be detached from runtime
mutation so report and study comparisons cannot drift after materialization.

### Ordinary Construction DX

Strategy authors should not need to write `__init__` just to receive config in
ordinary parameterized strategies. The framework-provided construction path must
materialize config and make it available as `self.config` before strategy
lifecycle methods run.

Custom strategy constructors are allowed as an advanced escape hatch. When a
strategy author overrides construction behavior, they are responsible for
preserving the framework contract, including config availability, fresh run
state, and consistency between executed config and reported config.

The technical implementation plan must make the construction order observable
enough for tests: when config is attached, when runtime state is initialized,
and what a custom constructor must preserve. Config-less subclasses that use the
ordinary base-class construction path must remain valid.

### Config-Less Strategies

Strategies may omit an explicit config declaration when they do not expose
configurable fields. Quantleet treats them as having an empty config.

Any study-level search space with non-empty `parameters` requires a declared
config schema containing those keys.

### Removed Callable Construction Role

legacy callable construction API is not the canonical strategy configuration contract.

It is not part of the active `ParameterStudy` public API. Custom construction
needs must be expressed through `Strategy` classes that still preserve the
framework-owned config materialization, reporting, validation, and portability
guarantees.

### Shared Product Surface

The strategy configuration contract is shared product surface for backtesting,
research, paper trading, and future live trading. It must not be modeled as a
research-only concept.

The chosen package path is `quantleet.strategy`.

Canonical imports are:

```python
from quantleet.strategy import Strategy, StrategyConfig
```

`quantleet.research.Strategy` may remain as a migration/re-export path, but it
is not the canonical owner. `research`, `backtest`, and future `execution` may
depend on `quantleet.strategy`; `quantleet.strategy` must not depend on
`research`, `backtest`, or `execution`.

## Functional Requirements

### Config Field Discovery

The MVP config field model is intentionally small:

- config fields are annotated public fields
- field names starting with `_` are private/internal and not configurable fields
- every canonical config field must have a default value
- required config fields without defaults are reserved for a future
  base-config/explicit-config extension
- public field names follow normal Python identifier rules; snake_case is
  recommended in docs and examples but is not a validation requirement
- inherited public annotated fields are config fields
- when a subclass redeclares an inherited field, the subclass declaration wins
- stable field order is base fields first, then subclass fields

The first version does not include descriptor-based parameter declarations,
range metadata, or search-space generation from the config class.

`StrategyConfig` is a dataclass-like framework base. Users declare annotations
and default class fields; they do not need to apply `@dataclass`,
`frozen=True`, pydantic models, or another implementation-specific decorator.
Quantleet is responsible for creating materialized immutable config instances,
validating supported fields, and producing normalized snapshots.

### Search-Space Validation Contract

Stage 1 defines the validation semantics for config-aware study search spaces.
Stage 2 wires those semantics into `ParameterStudy`.

Study-level search-space/schema mismatches must fail during preflight before
any backtest starts.

Preflight must treat the following as study definition errors:

- unknown config fields
- malformed parameter grids
- non-materializable candidate configs
- candidate values that fail the MVP schema compatibility rules

Runtime failures that occur after a valid config is materialized remain
candidate/run-level failures.

An empty study search space is valid and materializes exactly one candidate: the
default `StrategyConfig` snapshot. This supports fixed-config validation and
degenerate study cases.

This supersedes the current first-beta `ParameterStudy` behavior for future
canonical config-aware study workflows. Until Stage 2 migrates `ParameterStudy`,
the existing implemented parameter-exploration contract remains the current
runtime behavior.

Existing deterministic grid-shape protections should carry forward unless a
later Stage 2 spec deliberately changes them. In particular, malformed grids
include unordered candidate containers, empty value lists for non-empty search
keys, duplicate values for a key, non-finite floats, unsupported container
types, and raw cartesian grids that violate the configured candidate limit.

### MVP Candidate Value Compatibility

Canonical `StrategyConfig` defaults and study-level search-space candidate
values remain report-safe JSON scalar values in the first version.

MVP preflight validates candidate values against the declared `StrategyConfig`
schema only at the level supported by the first schema contract:

- field existence
- default availability
- JSON-scalar default and search-space values
- annotation-based primitive type compatibility

Range, choice, and domain validation are reserved for a future parameter
descriptor or validator extension.

Primitive compatibility is strict enough to avoid Python `bool`/`int`
ambiguity:

- `bool` values do not satisfy `int` or `float` fields
- `bool` fields accept only `bool`
- `int` fields accept `int` but not `bool`
- `float` fields accept `int` or `float` but not `bool`
- `str` fields accept only `str`

Fields with `None` defaults or optional annotations require careful treatment in
the technical plan, but the Stage 1 product rule is closed: `None` is allowed
only when the annotation explicitly permits it, such as `float | None` or
`Optional[float]`. Candidate value `None` is allowed only for optional fields.
Non-optional fields with `None` defaults or `None` candidate values fail
validation.

MVP `StrategyConfig` field annotations support only:

- `str`
- `int`
- `float`
- `bool`
- explicit optional forms of those primitive types

`Literal`, `Enum`, collection types, object types, custom classes, callables,
models, and runtime dependencies are not canonical config field annotations in
Stage 1. Custom runtime dependencies belong outside `StrategyConfig`; active
study workflows still use config-backed `Strategy` classes and must preserve
canonical validation, snapshot, and portability guarantees.

Public config exceptions:

- `StrategyConfigError`
- `StrategyConfigDeclarationError`
- `StrategyConfigValidationError`
- `StrategyConfigMutationError`

Declaration errors cover invalid strategy/config schema declarations.
Validation errors cover candidate, default, and search-space values that do not
fit the schema. Mutation errors cover attempts to change a materialized config.
Error messages should include actionable fragments such as the strategy name,
field name, and expected type, but exact full message strings are not part of
the stable product contract.

### Downstream Reporting Snapshot Shape

Stage 3 owns the reporting migration. The contract it must apply is:

Reports expose strategy config as a normalized plain mapping of public config
field names to values, not as a live `StrategyConfig` object.

Downstream reporting work should record `strategy_config`, not
`strategy_parameters`. The value is the fully materialized config snapshot used
for the run. The name `strategy_parameters` should be removed to avoid
confusion with study-level `parameters` search spaces and partial candidate
mappings.

Config-less strategies report an empty config snapshot `{}`. Direct instance
runs remain valid when the strategy instance exposes framework-owned
`StrategyConfig` metadata.

Stage 1 and Stage 2 must not rely on old report-level `strategy_parameters` as
the source of truth for canonical study configuration. Canonical study result
objects carry their own materialized `strategy_config` snapshots, and Stage 3
aligns reports to the same source.

### ParameterStudy Downstream Contract

Stage 2 should migrate `ParameterStudy` so that:

- `ParameterStudy(..., strategy=StrategyClass)` is the canonical construction
  path
- the old callable construction path is not accepted in the active public API
- new documentation and tests center `strategy=...`

Grid/search result rows should expose candidate-level partial overrides as
`candidate_parameters`, not `parameters`. The name `parameters` is reserved for
study-level search-space inputs.

Every materialized grid-search row should record both:

- `candidate_parameters`
- full `strategy_config`

Rows are created only after study-level preflight succeeds. Runtime-failed rows
retain the materialized `strategy_config` used or intended for the run.

This row-level `strategy_config` guarantee applies to canonical
`strategy=StrategyClass` workflows. The old callable construction path is not
part of the active row contract.

`GridSearchResult.best()` should continue returning the best eligible row. The
canonical selected execution settings are exposed as `best.strategy_config`;
`best.candidate_parameters` remains an audit trail of the partial override that
produced it.

### BacktestEngine Boundary

Study APIs must use the canonical strategy class plus materialized config path
because they need repeatable fresh strategy construction, parameter validation,
selected-config reporting, and future WFA/paper/live portability.

Stage 3.5 promotes direct class+config execution:

```python
engine.run(bars=bars, strategy=StrategyClass, config=StrategyConfig(...))
```

Stage 3.5 decides the direct BacktestEngine API: direct runs use
`strategy=StrategyClass` plus optional `config=StrategyConfig(...)`.

## Non-Functional Requirements

- The canonical path must be easy enough for a first strategy author to use
  without lambda factory boilerplate.
- The contract must remain deterministic and reproducible across repeated study
  runs.
- The config snapshot must be suitable for report/export comparison as plain
  data.
- The first implementation slice must stay small enough to verify well.
- The design must avoid coupling strategy configuration to WFA-specific
  internals.
- The design must preserve a path from research to paper/live portability
  without introducing Tier A runtime behavior in this slice.
- Errors for study-definition mistakes must be early, specific, and actionable.
- The contract must avoid implying that optimized or selected configurations
  are trading recommendations.

## Key Scenarios

### Scenario 1: Ordinary Configured Strategy

A user defines a config class with defaults, writes `Strategy[Config]`, and
accesses `self.config` in strategy logic. They do not implement `__init__`.
Study workflows can materialize fresh strategy instances from candidate
overrides.

### Scenario 2: Same Strategy, Different Search Spaces

The same strategy config schema is used across multiple experiments. Each study
passes a different `parameters={...}` search space without editing the strategy
source.

### Scenario 3: Fixed-Config Validation

A study receives `parameters={}`. It runs exactly one candidate using the
default full config snapshot. In future canonical config-aware study results,
that row's partial override is `candidate_parameters == {}` and its
`strategy_config` is the full default config snapshot.

### Scenario 4: Config-Less Strategy

A simple buy-and-hold style strategy declares no config. Direct backtests and
empty-parameter study workflows treat it as empty config. Non-empty
`parameters` fail preflight because there is no schema field to target.

### Scenario 5: Unsupported Legacy Construction Path

An advanced user attempts to supply the legacy callable construction path for
custom construction. Quantleet rejects that path in active study workflows
because config-backed strategy classes are the canonical portability and
reporting guarantee path.

### Scenario 6: Future WFA Fold

A future WFA fold selects one row from train results. The fold records both the
partial `candidate_parameters` that won and the full `selected_config` that is
used for the out-of-sample test run. `selected_config` is a WFA role-specific
name for the materialized `strategy_config` selected by the train slice.

## Edge Cases And Failure Scenarios

- `parameters` includes a key not declared by `StrategyConfig`: fail preflight.
- `parameters` includes a private config key such as `_cache_key`: fail
  preflight.
- a config field has no default in MVP: fail config-contract validation.
- an `int` field receives `True`: fail preflight.
- a `float` field receives `True`: fail preflight.
- a `bool` field receives `1`: fail preflight.
- a field value violates a future min/max business rule but passes primitive
  type compatibility: not caught by MVP unless a later validator extension is
  added.
- a config default is a list, dict, object, callable, model, or other
  non-scalar value: fail canonical config declaration validation.
- a non-optional field has a `None` default or receives a `None` candidate:
  fail validation.
- an explicitly optional primitive field has a `None` default or receives a
  `None` candidate: accept.
- an annotated public field uses an unsupported canonical annotation such as
  `Literal`, `Enum`, a collection, or a custom object type: fail canonical
  config declaration validation.
- a strategy mutates `self.config` during a run: unsupported behavior; the
  product contract requires configs to be immutable run snapshots and mutation
  attempts to fail fast.
- a custom constructor does not preserve config availability or fresh runtime
  state: user-responsibility advanced-path failure.
- a low-level instance run has no framework-owned config snapshot: report
  `strategy_config` as `{}`.
- a strategy has no config declaration and non-empty study parameters: fail
  preflight.
- a config declaration is missing, ambiguous, invalid, or conflicts with a
  fallback declaration: fail config-contract validation before grid expansion.
- a valid config materializes but strategy execution fails during `on_bar`: keep
  this as a candidate/run-level failure in the relevant study result.

## External Contracts

The following contracts must be visible to users and stable enough for later
test specs and implementation plans:

Stage 1:

- canonical shared owner is `quantleet.strategy`
- canonical strategies declare config through `Strategy[MyConfig]`
- `config_type = MyConfig` is a public advanced fallback; same-type redundant
  declarations are allowed and conflicting declarations fail
- `StrategyConfig` defines schema/defaults, not study search spaces
- study-level `parameters` define search spaces, not full config snapshots
- every materialized candidate has a full `strategy_config`
- runtime strategy code receives a `StrategyConfig` instance as `self.config`
- study/report/export-facing snapshots expose normalized plain mappings
- materialized configs are immutable run snapshots enforced by the framework
- ordinary strategy authors do not need to implement `__init__` just to receive
  config
- config-less strategies are allowed and map to empty config
- inherited config fields are allowed with base fields first, then subclass
  fields
- legacy callable construction is not part of the active public study API
- study preflight fails fast for schema/search-space mistakes
- MVP config defaults and search-space values are report-safe JSON scalars
- MVP annotations are primitive `str`/`int`/`float`/`bool` plus explicit
  optional forms only
- `None` is supported only for explicitly optional fields
- primitive compatibility rejects Python `bool`/`int` ambiguity
- public config errors use the `StrategyConfigError` hierarchy

Downstream Stage 2:

- future grid rows use `candidate_parameters`, not row-level `parameters`

Stage 3:

- report-facing config snapshots are plain mappings
- reporting uses `strategy_config`, not `strategy_parameters`

Direct backtest boundary:

- `BacktestEngine.run(strategy=StrategyClass, config=...)` is the direct
  backtest construction path after Stage 3.5.

## Stage Boundaries

### Stage 1 Required Scope

This spec's implementation-required scope is limited to the unified strategy
configuration contract:

- `StrategyConfig` product contract
- `Strategy[Config]` canonical declaration
- empty config behavior
- defaults-only MVP config fields
- schema/defaults versus search-space separation
- materialized config snapshot semantics
- enforced config immutability
- contract-level config discovery, materialization, and validation behavior
  needed by future study preflight
- removal of the old callable construction path from active study workflows
- shared strategy/runtime ownership, not research-only ownership

Stage 1 does not have to migrate `ParameterStudy`. If Stage 1 ships helper
behavior, acceptance should be framed around observable config schema discovery,
full config materialization from defaults plus overrides, and validation failure
before any user callback or execution hook is invoked by that contract-level
path.

### Downstream Stage 2 Requirements

Stage 2 should specify and implement the `ParameterStudy` migration:

- canonical `strategy=StrategyClass`
- `ParameterStudy(engine=..., bars=..., strategy=StrategyClass)` as the only
  active study construction path
- `candidate_parameters`
- row-level `strategy_config`
- best-row UX centered on `best.strategy_config`
- empty `parameters={}` producing one default-config candidate in canonical
  config-aware workflows
- preflight error types and messages for schema/search-space mistakes
- constraints receive full `strategy_config` mappings
- the config-backed row representation for current research workflows
- deterministic malformed-grid behavior for unordered candidate containers,
  empty value lists, duplicate or duplicate-equivalent values, non-finite
  floats, unsupported containers, and candidate-limit violations
- rejected and failed candidate rows are materialized with full
  `strategy_config`; constraint-rejected rows expose `strategy_config`

### Stage 3 Requirements

Stage 3 should specify and implement the reporting source-of-truth change:

- remove `Strategy.parameters()` from the canonical strategy surface
- replace report-facing `strategy_parameters` with `strategy_config`
- ensure report snapshots come from framework-owned materialized config values
- define how low-level instance runs represent empty or unavailable config

### Downstream Stage 4 Requirement

WFA remains paused until the relevant prior stages are completed or explicitly
superseded. WFA must not resume on a public contract that hardens
the old callable construction path as the canonical research-study path.

## Success Conditions

This product spec is successful when:

- implementation plans can build Stage 1 without reopening the canonical
  strategy configuration decision
- `ParameterStudy` migration planning can cite a clear distinction between
  `parameters`, `candidate_parameters`, and `strategy_config`
- reporting planning can cite a clear rule that materialized config snapshots
  are the source of truth
- WFA planning can resume later without hardening the old callable construction
  path
  UX
- the spec keeps ordinary strategy authoring lightweight while preserving a
  path to reproducible paper/live portability
- the product index routes future strategy configuration work to this document

## Open Questions

- Should a future `config=` base override be added to `ParameterStudy`,
  `BacktestEngine`, both, or neither?
- Stage 2 resolved that constraints receive full `strategy_config` mappings.
- Stage 2 resolved that the old callable construction path has no active row
  shape because it is not part of the public study API.
- In Stage 2, should duplicate-equivalent values such as `1` and `1.0` be
  normalized, rejected, or treated as distinct according to field type?
- Stage 2 resolved that constraint-rejected rows expose full
  `strategy_config`.
- Stage 3 resolved that `strategy_parameters` is removed immediately rather
  than kept as a compatibility alias.
- When should Quantleet introduce range/choice validators or descriptor-style
  parameter declarations?
- Should `search_space` become an alias for study-level `parameters` after the
  current migration is stable?
- Stage 3.5 resolved that direct instance runs are not the current public
  direct-backtest API.
- Stage 3.5 resolved that
  `BacktestEngine.run(strategy=StrategyClass, config=...)` is the primary
  direct backtest API.
- What migration wording should docs use if external pre-release readers saw
  old callable construction examples before the public beta?
