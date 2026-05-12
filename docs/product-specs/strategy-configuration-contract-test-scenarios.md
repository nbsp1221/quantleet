# Strategy Configuration Contract Test Scenarios

## Status

- Status: `planned`
- Class: `product-test-spec`
- Scope: Stage 1 test scenarios for the unified strategy configuration contract
  plus downstream test hooks for `ParameterStudy` and reporting migration

Related documents:

- [strategy-configuration-contract.md](strategy-configuration-contract.md)
- [wfa-prerequisite-roadmap.md](wfa-prerequisite-roadmap.md)
- [walk-forward-analysis-readiness.md](walk-forward-analysis-readiness.md)
- [parameter-exploration.md](parameter-exploration.md)
- [parameter-exploration-test-scenarios.md](parameter-exploration-test-scenarios.md)
- [research-ergonomics.md](research-ergonomics.md)
- [backtest-mvp.md](backtest-mvp.md)
- [../RELIABILITY.md](../RELIABILITY.md)
- [../SECURITY.md](../SECURITY.md)
- [../design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)

This document turns the Strategy Configuration Contract product spec into a
test scenario contract. It does not implement tests and does not extend product
scope. Tests derived from this document should prove the externally observable
configuration contract, not private helper names or generic-introspection
internals.

## Testing Basis

The feature exists because Quantleet needs a shared, framework-recognizable
strategy configuration contract before `ParameterStudy` migration, reporting
metadata changes, and WFA resume can safely proceed.

The core product contract is:

- `Strategy` and `StrategyConfig` are canonically imported from
  `quantleet.strategy`
- canonical strategy authors declare config with `Strategy[MyConfig]`
- `config_type = MyConfig` is a public advanced fallback, with same-type
  redundant declarations allowed and conflicting declarations rejected
- `StrategyConfig` defines schema/defaults, not study search spaces
- config fields are annotated public fields with defaults in the MVP
- inherited public annotated fields are config fields
- config-less strategies are allowed and map to empty config
- study-level `parameters` are search spaces and partial override sets
- materialization produces a full config snapshot from defaults plus candidate
  overrides
- runtime strategy code receives `self.config` as a `StrategyConfig` instance
- study/report/export-facing snapshots are normalized plain mappings
- materialized configs are immutable run snapshots enforced by the framework
- ordinary strategy authors do not need `__init__` just to receive config
- custom constructors are advanced/user-responsibility paths that must preserve
  the framework config contract
- search-space/schema mistakes fail before any backtest execution hook starts
- config defaults and candidate search-space values are JSON scalars in the MVP
- supported annotations are primitive `str`/`int`/`float`/`bool` plus explicit
  optional forms
- `None` is accepted only for explicitly optional fields
- primitive compatibility rejects Python `bool`/`int` ambiguity
- public config errors use the `StrategyConfigError` hierarchy
- Stage 2 applies the contract to `ParameterStudy`
- Stage 3 applies the contract to reporting as `strategy_config`

Tests must validate these contracts as user-visible behavior and migration
guardrails. They must not prove profitability, optimize strategy quality, or
reopen WFA.

## Testing Philosophy

Tests are long-lived product assets. A refactor of config discovery mechanics,
dataclass/frozen-object choice, or helper names should not require test changes
unless the public contract changes.

External testing guidance used for this spec:

- Google Testing Blog recommends testing behaviors rather than methods because a
  single behavior can span multiple methods and one method can expose many
  behaviors:
  [Testing on the Toilet: Test Behaviors, Not Methods](https://testing.googleblog.com/2014/04/testing-on-toilet-test-behaviors-not.html).
- The Practical Test Pyramid recommends many cheap unit tests, fewer integration
  tests, and only the system-level tests that justify their cost:
  [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html).
- pytest good integration practices recommend keeping tests outside application
  code and using a clear test directory structure; pytest fixture guidance
  supports explicit, modular fixtures for reusable setup:
  [pytest Good Integration Practices](https://docs.pytest.org/en/latest/explanation/goodpractices.html),
  [pytest fixtures](https://docs.pytest.org/en/latest/explanation/fixtures.html).

Operational rules:

1. Test observable contracts, not private implementation mechanics.
2. Cover normal flows, invalid inputs, boundaries, and migration-sensitive
   regressions.
3. Prefer unit tests for schema discovery, materialization, and validation.
4. Use integration tests only where the contract crosses strategy construction,
   study execution, backtest runtime, or reporting boundaries.
5. Use fakes only to prove negative guarantees such as "no backtest execution
   starts after preflight failure".
6. Keep examples small enough that a human or agent can infer the failure cause
   from the test name, input, and assertion.
7. Treat downstream Stage 2 and Stage 3 tests as separate test specs or
   implementation-plan inputs, not as Stage 1 completion gates.

## Test Scope

In scope for Stage 1:

- canonical `quantleet.strategy` public ownership and migration/re-export
  guardrails
- `StrategyConfig` field discovery from annotated public fields
- default-value requirement for MVP config fields
- empty config behavior for strategies without explicit config fields
- canonical `Strategy[Config]` declaration as user-facing contract
- public advanced `config_type` fallback behavior
- conflict/invalid declaration failures that can be observed without running a
  backtest
- full config materialization from defaults plus candidate overrides
- normalized mapping snapshots derived from materialized config
- preservation of default fields not present in a candidate override
- enforced immutability of materialized config instances
- primitive candidate compatibility for `str`, `int`, `float`, and `bool`
- optional primitive compatibility for explicitly optional fields
- rejection of Python `bool`/`int` ambiguity
- rejection of unknown or private config fields in candidate overrides
- no user callback, strategy construction callback, or execution hook after
  config-contract validation failure in the Stage 1 contract-level path
- placement and import-surface guardrails for a shared strategy/runtime
  contract

In scope as downstream Stage 2/3 test hooks:

- `ParameterStudy(..., strategy=StrategyClass)` canonical construction
- old callable construction keyword rejected by the active public API
- `candidate_parameters` row naming
- row-level `strategy_config`
- empty `parameters={}` producing one default-config candidate in canonical
  config-aware study workflows
- Stage 2 preflight error messages and no-engine-run behavior
- Stage 3 `strategy_config` report snapshot replacing `strategy_parameters`

Out of scope:

- WFA implementation or WFA fold-generation tests
- paper/live runner tests
- objective alias or callable objective tests
- descriptor/range DSL tests such as `IntParameter(min=..., max=...)`
- min/max, categorical, or domain validation tests
- new optimization algorithm tests
- `BacktestEngine.run(strategy=StrategyClass, config=...)` tests unless a later
  Backtest API spec promotes that path
- tests that assert private generic-inspection helper names
- tests that assert an exact immutability enforcement mechanism before the
  technical plan chooses one
- tests that treat selected configs as trading recommendations

## Proposed Test Placement

| Layer | Proposed location | Purpose |
| --- | --- | --- |
| Unit | `tests/unit/strategy/test_strategy_config_contract.py` | Config field discovery, default rules, empty config, canonical declaration behavior, fallback declaration behavior, invalid declaration errors. |
| Unit | `tests/unit/strategy/test_strategy_config_materialization.py` | Defaults-plus-overrides materialization, normalized mapping snapshots, unknown/private field rejection, primitive compatibility, optional compatibility, bool/int ambiguity. |
| Unit | `tests/unit/strategy/test_strategy_surface.py` | Strategy authoring DX: `self.config` availability, no required `__init__`, config-less strategy behavior, enforced config immutability. |
| Integration | `tests/integration/strategy/test_strategy_config_construction.py` | Fresh canonical strategy construction with real `Strategy` subclasses and a contract-shaped execution harness. |
| Structure | `tests/structure/architecture/test_strategy_config_boundaries.py` | The shared strategy config surface is not owned by a product surface and does not force future `execution` to depend on `research`. |
| Docs | `tests/structure/docs/test_strategy_configuration_contract_docs.py` | Product docs route strategy config work to the product spec and test spec, and WFA remains paused. |
| Downstream integration | later Stage 2 `tests/integration/research/test_parameter_study_strategy_config_migration.py` | `ParameterStudy(strategy=...)`, `candidate_parameters`, row-level `strategy_config`, and empty-search-space behavior. |
| Downstream integration | later Stage 3 reporting tests | `report.run.strategy_config`, removal of `strategy_parameters`, and config snapshot source-of-truth. |

No browser-style E2E tests are required. This is a Python library contract with
no UI. Full workflow confidence belongs in targeted integration tests once
Stage 2 and Stage 3 wire the contract into `ParameterStudy` and reporting.

The Stage 1 shared strategy/runtime contract lives under `quantleet.strategy`.
`research` placement remains appropriate for Stage 2 `ParameterStudy` migration
tests, not for the canonical Stage 1 strategy configuration surface.

## Fixture And Test Data Strategy

Use minimal strategy/config classes defined inside tests unless reuse improves
clarity. The classes should be obvious and behavior-free unless the scenario is
specifically about strategy lifecycle.

Recommended fixtures:

| Fixture | Shape | Purpose |
| --- | --- | --- |
| `RSIStrategyConfig` | `rsi_period: int = 14`, `oversold: float = 30.0`, `enabled: bool = True`, `label: str = "rsi"` | Normal configured strategy cases. |
| `RiskConfig` | `risk_per_trade: float = 0.01` | Prove non-searched defaults survive materialization. |
| `EmptyConfigStrategy` | strategy without explicit config fields | Config-less strategy behavior. |
| `ConfiguredStrategy` | `Strategy[RSIStrategyConfig]` accessing `self.config` | Canonical declaration and `self.config` availability. |
| `CustomInitStrategy` | overrides `__init__` and preserves framework contract | Optional advanced-path regression only after the technical plan defines observable custom-constructor responsibilities. |
| `InvalidConfigTypeStrategy` | declares a non-`StrategyConfig` config type | Declaration validation failure. |
| `ConflictingConfigStrategy` | generic config plus conflicting fallback declaration | Declaration conflict failure. |
| `NoRunEngine` or `CountingEngine` | public `run(...)` call log only | Prove validation failure prevents execution hooks. |
| `candidate_override` | `{"rsi_period": 7, "oversold": 20.0}` | Materialization with defaults. |

Fixture rules:

- Keep config classes tiny and local to the test module unless they are shared
  across many tests.
- Put expected snapshots directly in assertions.
- Do not hide materialization expectations inside helper functions.
- Avoid market-data fixtures for Stage 1 unless the test truly crosses into a
  study/backtest integration boundary.
- Do not use the future WFA fold vocabulary in Stage 1 tests except as docs
  guardrails.

## Mock, Stub, And Fake Policy

Prefer real objects for the strategy/config surface:

- real `StrategyConfig` subclasses
- real `Strategy` subclasses
- real materialized config snapshots
- real public construction/normalization path once implemented

Allowed fakes:

- `CountingEngine`/`NoRunEngine` for no-execution validation checks
- a contract-shaped construction/normalization harness if the Stage 1
  implementation exposes framework-owned behavior before `ParameterStudy`
  migration
- a minimal report/run manifest fake only in Stage 3 tests if a reporting
  boundary cannot be reached cheaply through real backtests

Avoid:

- patching private discovery helpers
- asserting `__orig_bases__`, `__init_subclass__`, or dataclass internals
- mocking `StrategyConfig` itself
- coupling tests to exact full error message strings
- running full backtests for pure config-schema validation

Stage 1 tests must exercise the chosen public or contract-level
normalization/materialization behavior. Because Stage 1 does not expose
user-facing `discover_config_schema(...)` or `materialize_config(...)` helpers,
tests should assert the behavior through public construction and config
snapshot outputs rather than importing private discovery helpers.

## What Tests Must Verify

Tests must verify:

- the canonical user can declare `Strategy[MyConfig]`
- Quantleet can discover one effective config schema for a canonical strategy
- public annotated config fields with defaults are discovered as config fields
- private fields are not configurable fields
- all MVP config fields require defaults
- inherited public annotated config fields are discovered as config fields, with
  base fields first and subclass redeclarations taking precedence
- missing/invalid/conflicting config declarations fail before execution
- config-less strategies map to empty config
- candidate overrides must target declared public config fields
- materialization preserves defaults and applies overrides
- materialized configs expose `StrategyConfig` instances at runtime and
  normalized plain mappings for snapshots
- materialized config mutation attempts fail with `StrategyConfigMutationError`
- materialized snapshots are plain-data comparable
- primitive candidate compatibility follows the product table
- optional primitive fields accept `None`; non-optional fields reject `None`
- `bool` is not accepted as `int` or `float`
- `int` is accepted for `float`
- search-space/schema mistakes prevent backtest/study execution hooks
- config-contract failures occur before constraints, strategy constructors,
  lifecycle methods, or execution hooks with user-visible side effects
- custom constructors are allowed but not part of canonical guarantee tests
- the old callable construction keyword is rejected outside canonical guarantee
  tests

## What Tests Must Not Verify

Tests must not verify:

- which private helper performs generic inference
- whether implementation uses dataclasses, pydantic-like validation, descriptors,
  `MappingProxyType`, or another internal representation
- min/max or categorical range behavior
- WFA fold splitting or OOS reporting
- paper/live runtime behavior
- exact `BacktestEngine.run(strategy=StrategyClass, config=...)` behavior before
  a later spec promotes it
- profitability, alpha quality, or optimizer recommendations

## Unit Test Scenarios

### U1: Config Field Discovery

Purpose: prove the MVP config schema is explicit, small, and inspectable.

| Case | Input | Expected behavior |
| --- | --- | --- |
| public annotated defaults | `rsi_period: int = 14`, `oversold: float = 30.0` | fields discovered with defaults. |
| private annotated field | `_cache_key: str = "x"` | not a config field and cannot be targeted by overrides. |
| unannotated class attribute | `lookback = 14` | not a config field. |
| annotated field without default | `rsi_period: int` | config-contract validation failure. |
| inherited public field | subclass config inherits `rsi_period` | inherited field is discovered. |
| subclass redeclaration | subclass redeclares inherited `risk_per_trade` | subclass default and annotation take precedence. |
| method/property on config class | `def value(...)` or `@property` | not a config field. |
| public non-snake-case field | valid Python public identifier | allowed as a field, though docs examples should prefer snake_case. |

Tests should verify stable field order: base fields first, then subclass fields.

### U2: Canonical Strategy Declaration

Purpose: prove the user-facing `Strategy[Config]` contract without testing
private generic mechanics.

| Case | Input | Expected behavior |
| --- | --- | --- |
| canonical declaration | `class S(Strategy[C])` | one effective config schema is discoverable. |
| no explicit config and no params | `class S(Strategy)` | treated as empty config. |
| no explicit config with non-empty overrides | strategy without config plus `{"x": [1]}` | validation failure before execution. |
| config type not `StrategyConfig` | `class S(Strategy[object])` | config-contract validation failure. |
| conflicting fallback | `Strategy[C]` plus fallback `config_type = D` | config-contract validation failure. |
| redundant same-type fallback | `Strategy[C]` plus fallback `config_type = C` | accepted. |
| explicit fallback only | no generic plus `config_type = C` | accepted as public advanced fallback. |

### U3: Materialization From Defaults Plus Overrides

Purpose: prove partial candidates produce full execution snapshots.

| Case | Config defaults | Candidate | Expected snapshot |
| --- | --- | --- | --- |
| no overrides | `rsi_period=14`, `oversold=30.0` | `{}` | both defaults preserved. |
| one override | same | `{"rsi_period": 7}` | `rsi_period=7`, `oversold=30.0`. |
| multiple overrides | same | `{"rsi_period": 7, "oversold": 20.0}` | both overridden. |
| default not in search | add `risk_per_trade=0.01` | no risk key | risk default preserved. |
| unknown key | same | `{"unknown": 1}` | validation failure. |
| private key | same | `{"_cache_key": "x"}` | validation failure. |

Assertions should compare normalized plain mappings where possible:

```python
assert snapshot == {
    "rsi_period": 7,
    "oversold": 20.0,
    "risk_per_trade": 0.01,
}
```

### U4: Primitive Candidate Compatibility

Purpose: prove type compatibility catches common user mistakes before execution.

| Field annotation | Candidate value | Expected behavior |
| --- | --- | --- |
| `int` | `7` | accepted. |
| `int` | `True` | rejected. |
| `int` | `7.0` | rejected. |
| `float` | `20.0` | accepted. |
| `float` | `20` | accepted. |
| `float` | `False` | rejected. |
| `bool` | `True` | accepted. |
| `bool` | `1` | rejected. |
| `str` | `"alpha"` | accepted. |
| `str` | `1` | rejected. |
| any supported field | object/callable/list/dict candidate | rejected under MVP JSON-scalar search-space policy. |
| any supported field default | object/callable/list/dict default | declaration validation failure. |
| optional primitive field | `None` | accepted only when annotation explicitly permits `None`. |
| non-optional primitive field | `None` | rejected. |
| unsupported annotation | `Literal`, `Enum`, collection, object, custom class | declaration validation failure in canonical Stage 1. |
| finite numeric field | `math.nan` or `math.inf` | rejected if Stage 2 carries forward existing finite-float grid protection. |
| float field duplicate-equivalent values | `[1, 1.0]` in one search space | handled according to the Stage 2 duplicate/normalization decision. |

Open item:

- `math.nan`/`math.inf` and duplicate-equivalent values are Stage 2 grid-shape
  questions unless the Stage 1 implementation reuses existing grid validation.

### U5: Config Immutability Contract

Purpose: protect the source-of-truth snapshot from silent drift.

Stage 1 tests should assert the product-level observable:

- assigning to a materialized `StrategyConfig` field fails with
  `StrategyConfigMutationError`
- normalized snapshot mappings are detached plain-data values
- mutating unrelated strategy runtime state cannot change the normalized config
  snapshot

Do not write mechanism-specific tests such as `FrozenInstanceError` unless the
technical plan deliberately exposes that mechanism as part of the public
contract.

### U6: Ordinary Construction DX

Purpose: prove a normal strategy author does not need constructor boilerplate.

Scenarios:

- `ConfiguredStrategy(Strategy[Config])` can access `self.config` before
  lifecycle methods run.
- `ConfiguredStrategy` does not implement `__init__`.
- a fresh strategy instance receives the materialized config for one run.
- two materializations with different candidates produce distinct effective
  config snapshots and do not share mutable runtime state.

This may be a unit or narrow integration test depending on where the
construction/normalization path lives.

## Integration Test Scenarios

### I1: Canonical Strategy Construction Harness

Purpose: prove the public strategy/config contract composes across actual
`Strategy` subclasses and the framework-owned construction path.

Flow:

1. define `RSIStrategyConfig`
2. define `RSIStrategy(Strategy[RSIStrategyConfig])` with no `__init__`
3. materialize config from defaults plus candidate override
4. construct a fresh strategy through the public/canonical framework path
5. assert strategy logic can read `self.config`
6. assert the observed config snapshot matches the materialized mapping

This should not require a real market-data backtest unless the implementation
only exposes config injection through a runtime path.

### I2: No Execution After Contract Validation Failure

Purpose: prove user mistakes fail fast before expensive or misleading execution.

Use counting callbacks or a contract-shaped fake execution hook. Stage 1 tests
should prove the config validation/materialization path does not invoke user
callbacks when validation fails. Stage 2 tests should separately prove
`ParameterStudy` preflight prevents engine runs.

Scenarios:

- unknown override key
- private override key
- invalid config declaration
- candidate type mismatch
- non-empty search space for config-less strategy

Expected:

- validation fails
- diagnostic names the offending field or strategy declaration
- no constraint, factory, constructor, lifecycle, engine, or backtest execution
  hook is invoked by the path under test

### I3: Config-Less Strategy Direct Path

Purpose: prove simple strategies remain lightweight.

Flow:

1. define a strategy with no explicit config
2. run the minimal contract path that materializes or normalizes strategy config
3. assert the effective config snapshot is `{}`
4. assert no empty config class is required from the user

If this crosses into `BacktestEngine.run(strategy=StrategyClass, config=...)`,
keep the assertion limited to the config contract and do not assert unrelated
backtest metrics.

## Downstream Stage 2 Test Hooks

These are not Stage 1 completion gates. They should be copied or refined into
the Stage 2 `ParameterStudy` migration test spec.

### S2-1: Canonical ParameterStudy Construction

```python
ParameterStudy(
    engine=engine,
    bars=bars,
    strategy=RSIStrategy,
)
```

Expected:

- canonical construction accepts `strategy=StrategyClass`
- old callable construction keyword is rejected
- canonical materialized-config row guarantees apply to
  `strategy=StrategyClass` workflows

### S2-2: Empty Search Space

Input:

```python
parameters={}
```

Expected future canonical behavior:

- one candidate row
- `candidate_parameters == {}`
- `strategy_config` equals the full default config snapshot
- one admissible run if execution proceeds
- `best().strategy_config` returns the same default snapshot when an objective is
  available

This supersedes current `ParameterStudy` behavior only after Stage 2 migration.

### S2-2a: Config-Less Empty Search Space

Input:

```python
ParameterStudy(
    engine=engine,
    bars=bars,
    strategy=ConfigLessStrategy,
).grid_search(parameters={})
```

Expected future canonical behavior:

- one candidate row
- `candidate_parameters == {}`
- `strategy_config == {}`
- one admissible run if execution proceeds

### S2-3: Candidate Row Naming

Expected future canonical behavior:

- rows expose `candidate_parameters`, not row-level `parameters`
- rows expose full `strategy_config`
- `GridSearchResult.best()` returns the row, not only the config
- `best.strategy_config` is the selected execution snapshot

### S2-4: Constraint Input

Resolved Stage 2 behavior:

- constraints receive full `strategy_config`
- constraints do not receive partial `candidate_parameters`

### S2-5: Malformed Grid Carry-Forward

These are downstream Stage 2 scenarios, not Stage 1 completion gates.

Stage 2 should carry forward deterministic grid-shape protections unless its
product spec deliberately changes them:

- unordered candidate containers are rejected
- empty value lists for non-empty search keys are rejected
- duplicate values for a key are rejected
- non-finite floats are rejected
- unsupported container types are rejected
- raw cartesian grids exceeding the candidate limit fail before callbacks
- duplicate-equivalent float values such as `[1, 1.0]` for a `float` field are
  either normalized before duplicate checks or rejected, according to the Stage
  2 decision

### S2-6: Constraint-Rejected And Failed Candidate Rows

Resolved Stage 2 behavior:

- constraints receive full `strategy_config`
- rows rejected by constraints are materialized with `strategy_config`
- runtime-failed rows retain the materialized `strategy_config` intended for
  execution

## Downstream Stage 3 Test Hooks

These are not Stage 1 completion gates. They should be copied or refined into
the Stage 3 reporting source-of-truth test spec.

### S3-1: Report Strategy Config Snapshot

Expected future canonical behavior:

- reports record `strategy_config`, not `strategy_parameters`
- `strategy_config` is a normalized plain mapping
- the snapshot comes from the framework-owned materialized config
- strategy-authored self-reporting cannot silently disagree with execution
  config

### S3-2: Direct Backtest Class Plus Config Reports Framework-Owned Config

Expected future canonical behavior:

- direct backtests run through `strategy=StrategyClass` plus optional
  `config=StrategyConfig(...)`
- omitted config materializes the strategy config type default
- config-less strategies report `strategy_config == {}`

Stage 3.5 resolves the old direct-instance ambiguity. See
[direct-backtest-class-config-api-test-scenarios.md](direct-backtest-class-config-api-test-scenarios.md).

## Contract, Regression, And Documentation Tests

### C1: Product Spec Routing

Purpose: prevent future work from bypassing the strategy configuration contract.

Assertions:

- `docs/product-specs/index.md` routes strategy config work to
  `strategy-configuration-contract.md`
- the test spec is referenced from the product spec or index
- WFA docs still state WFA is paused until prerequisites are resolved

### C2: Architecture Boundary

Purpose: preserve shared runtime ownership.

Assertions:

- `StrategyConfig` is owned by `quantleet.strategy`
- `quantleet.research.Strategy` remains only a migration/re-export path if
  present
- future execution portability is not forced to depend on `quantleet.research`
- `trading` dependency rules are not violated
- no Tier A paper/live behavior is introduced by Stage 1

### C3: Backward-Contract Regression

Purpose: prove the unpublished beta migration is intentional, not accidental.

Assertions after relevant stages:

- `Strategy.parameters()` is not used as canonical execution-config source of
  truth
- old callable construction examples are removed from active docs/examples
- tests no longer teach `GridSearchRow.parameters` as the canonical row field
  after Stage 2 migration

## Test Level Priorities

### P0

- canonical `quantleet.strategy` import ownership
- config field discovery
- defaults-only MVP rule
- canonical `Strategy[Config]` declaration
- public advanced `config_type` fallback behavior
- empty config behavior
- full materialization from defaults plus overrides
- normalized mapping snapshot behavior
- unknown/private override rejection
- primitive compatibility and `bool`/`int` ambiguity
- explicit optional primitive compatibility
- enforced materialized config immutability
- public config exception hierarchy and message fragments
- no execution after config-contract validation failure
- ordinary no-`__init__` config availability

### P1

- inherited config field order and subclass redeclaration precedence
- structure/docs routing tests
- custom constructor advanced-path regression after observable responsibilities
  are defined

### Downstream P1 When Stage 2/3 Starts

- deterministic grid-shape carry-forward once Stage 2 starts
- Stage 2 empty-search-space row shape
- Stage 2 config-less empty-search-space row shape
- Stage 2 config-backed row representation after the decision is closed
- Stage 3 report `strategy_config` snapshot

### P2

- future base-config override behavior
- `search_space` alias
- descriptor/range validation
- WFA `selected_config` fold tests

## Success Conditions

The test suite derived from this document is successful when:

- a normal user can write `Strategy[Config]` and receive `self.config` without
  constructor boilerplate
- a config-less strategy remains possible with empty config
- invalid config declarations and invalid candidate overrides fail before any
  execution hook starts
- materialized config snapshots preserve defaults and apply overrides
- runtime config is immutable and mutation attempts fail fast
- tests catch Python `bool`/`int` ambiguity
- tests catch invalid defaults, unsupported annotations, and invalid optional
  usage
- tests distinguish schema/defaults from study search spaces
- Stage 2 and Stage 3 tests can build on the same vocabulary without reopening
  Stage 1 decisions
- tests do not assert private implementation details or future WFA behavior
- repo verification can run the relevant test lanes through the existing
  `uv run poe` command surface

## Open Questions

- Stage 2 resolved that constraints receive full `strategy_config` mappings.
- In Stage 2, should duplicate-equivalent values such as `1` and `1.0` be
  normalized, rejected, or treated as distinct according to field type?
- Stage 2 resolved that constraint-rejected rows expose full
  `strategy_config`.
- Stage 2 resolved that old callable construction workflows have no active row
  shape because the keyword is rejected.
- Stage 3 resolved that `strategy_parameters` is removed immediately rather
  than kept temporarily as a compatibility alias.
