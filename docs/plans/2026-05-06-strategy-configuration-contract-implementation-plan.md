# Strategy Configuration Contract Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to
> implement this plan task-by-task.

**Goal:** Build the Stage 1 canonical `quantleet.strategy` contract with
`Strategy`, `StrategyConfig`, immutable materialized configs, normalized
snapshots, and migration-compatible `quantleet.research.Strategy` re-export.

**Architecture:** Introduce a new shallow top-level capability package,
`quantleet.strategy`, as the shared strategy/runtime authoring surface.
Move the existing strategy runtime surface out of `research`, keep `research`
as a compatibility facade, and keep `BacktestEngine` instance execution intact.
Implement config discovery/materialization through the config object and
strategy construction path, not through user-facing helper functions.

**Tech Stack:** Python 3.13, standard-library dataclasses/typing primitives,
pytest, Ruff, mypy, Poe/uv verification.

---

## Implementation Goal

Implement the Stage 1 Strategy Configuration Contract described by:

- `docs/product-specs/strategy-configuration-contract.md`
- `docs/product-specs/strategy-configuration-contract-test-scenarios.md`

This is the prerequisite foundation for later `ParameterStudy` migration,
reporting source-of-truth cleanup, and WFA resume. It is not the WFA
implementation and must not migrate `ParameterStudy` or reporting in this
slice.

## Implementation Scope

In scope:

- Create canonical package `quantleet.strategy`.
- Move or re-home the existing `Strategy` runtime surface from
  `quantleet.research.strategy` into `quantleet.strategy`.
- Move the strategy data view primitives currently in
  `quantleet.research.series` into `quantleet.strategy.series` so
  `quantleet.strategy` does not depend on `research`.
- Keep `quantleet.research.Strategy` and `quantleet.research.series` as
  compatibility re-export paths.
- Add `StrategyConfig` as a dataclass-like framework base.
- Add public config exception hierarchy:
  - `StrategyConfigError`
  - `StrategyConfigDeclarationError`
  - `StrategyConfigValidationError`
  - `StrategyConfigMutationError`
- Support canonical strategy declaration:

  ```python
  class MyConfig(StrategyConfig):
      lookback: int = 14


  class MyStrategy(Strategy[MyConfig]):
      ...
  ```

- Support public advanced fallback:

  ```python
  class MyStrategy(Strategy):
      config_type = MyConfig
  ```

- Accept same-type redundant declarations and reject conflicting declarations.
- Treat config-less strategies as empty config.
- Enforce materialized `StrategyConfig` immutability.
- Validate MVP config fields:
  - public annotated fields only
  - `_`-prefixed fields ignored as private/internal
  - every canonical field has a default
  - inherited fields allowed
  - subclass redeclarations override inherited fields
  - stable field order: base fields first, then subclass fields
  - defaults are report-safe JSON scalar values
  - supported annotations: `str`, `int`, `float`, `bool`, and explicit
    optional forms of those primitives
  - `None` allowed only for explicitly optional fields
  - strict `bool`/`int` ambiguity rejection
- Expose runtime config as `self.config`.
- Expose normalized snapshot mapping from the materialized config object.
- Add tests under the new `tests/unit/strategy` and
  `tests/integration/strategy` taxonomy.
- Add/update structure and public import tests for `quantleet.strategy`.
- Update architecture/doc routing tests to recognize `strategy` as a shared
  Tier B capability package.

Out of scope:

- WFA implementation.
- `ParameterStudy(..., strategy=StrategyClass)` migration.
- `candidate_parameters` / row-level `strategy_config` result migration.
- Reporting model migration from `strategy_parameters` to `strategy_config`.
- `BacktestEngine.run(strategy=StrategyClass, config=...)`.
- Parameter descriptor DSL such as `IntParameter(...)`.
- Range, choice, enum, `Literal`, collection, or custom-object config fields.
- Paper/live runner behavior.
- Public `discover_config_schema(...)` or `materialize_config(...)` helper
  functions.

## Codebase Investigation Results

### Project Structure

The repository is a Python 3.13 package using `uv`, `poethepoet`, `pytest`,
`ruff`, `mypy`, and `uv_build`.

Current package roots under `src/quantleet`:

- `data`
- `trading`
- `research`
- `backtest`
- `execution`
- `integrations`

Current test taxonomy:

- `tests/unit`
- `tests/integration`
- `tests/structure`
- `tests/smoke`
- `tests/perf`

Default verification is driven through Poe:

- `uv run poe verify`
- `uv run poe verify-runtime`
- `uv run poe repo-check`
- targeted `uv run pytest ...`

### Relevant Existing Modules

- `src/quantleet/research/strategy.py`
  - owns current public `Strategy`
  - contains `PositionView`
  - initializes `_pending_order_requests`, causal `data`, and `position`
  - exposes `init`, `display_name`, `parameters`, `on_bar`, `buy`, `sell`
  - imports `OHLCVDataView` and `SeriesView` from `quantleet.research.series`
  - imports trading events/intents/state/order requests from `quantleet.trading`

- `src/quantleet/research/series.py`
  - owns `SeriesView`, `_SeriesBuffer`, `OHLCVDataView`
  - used by `Strategy`, `ta`, indicator runtime, tests, and docs

- `src/quantleet/research/__init__.py`
  - lazy public facade for `Strategy`, `ParameterStudy`, `GridSearchResult`,
    `GridSearchRow`, `qc`, `ta`
  - must keep `Strategy` as a compatibility re-export

- `src/quantleet/backtest/strategy_runtime.py`
  - uses `StrategyLike` protocol rather than concrete `Strategy`
  - `_StrategyDriver` calls `_reset_runtime_state`, `init`, `_handle_bar`,
    and reads `_pending_order_requests`
  - this path should remain protocol-based and should not require
    `BacktestEngine` to construct strategy classes in Stage 1

- `src/quantleet/backtest/engine.py`
  - `BacktestEngine.run(...)` accepts a strategy instance
  - validates exactly one of `bars` or `source`
  - calls `_run_backtest(...)`
  - must remain unchanged in behavior for Stage 1

- `src/quantleet/backtest/reporting.py`
  - `RunManifest.strategy_parameters` still comes from
    `_strategy_parameters(strategy)`
  - Stage 3 owns this migration; do not change it in Stage 1

- `src/quantleet/research/parameter_exploration.py`
  - `ParameterStudy` currently requires `strategy_factory`
  - grid validation already contains reusable JSON-scalar and deterministic
    grid-shape logic
  - Stage 2 owns migration to `strategy=StrategyClass`; do not change this in
    Stage 1 except imports if needed

- `src/quantleet/_repo_tools.py`
  - defines architecture/domain rules used by `uv run poe repo-check`
  - currently does not know about a `strategy` top-level package
  - must be updated when `src/quantleet/strategy` is added

### Existing Architecture Constraints

From `ARCHITECTURE.md` and `docs/design-docs/package-topology-and-naming.md`:

- Top-level packages express capability/runtime contexts.
- Avoid vague root names such as `core`, `common`, or `utils`.
- `_shared` is not allowed to own business meaning.
- `trading` and `execution` are Tier A.
- `research` and `backtest` are Tier B.
- `execution` must not depend on `research`.
- Product surfaces must not own engine semantics.

Implication: `Strategy` and `StrategyConfig` should not stay under `research`
as canonical owner. The new top-level `quantleet.strategy` package is the
correct capability package.

### Existing Canonical Paths To Preserve

- `BacktestEngine.run(bars=..., strategy=...)` and
  `BacktestEngine.run(source=..., strategy=...)` remain the low-level
  direct-run paths.
- `ParameterStudy(..., strategy_factory=...).grid_search(...)` remains current
  implemented behavior until Stage 2.
- `quantleet.research.Strategy` remains importable as a migration/re-export
  path.
- `quantleet.research.series.SeriesView` remains importable as a
  migration/re-export path.
- `result.report.run.strategy_parameters` remains current reporting behavior
  until Stage 3.

### Reusable Code And Patterns

Reuse:

- `MappingProxyType` pattern from `GridSearchRow.__post_init__` for immutable
  mapping snapshots where useful.
- Existing JSON-scalar semantics from `parameter_exploration.py`, but do not
  import private research helpers into `strategy`. Reimplement the small
  primitive validation locally in `quantleet.strategy.config` to avoid a
  `strategy -> research` dependency.
- Existing `Strategy` order intake and runtime state methods.
- Existing `_StrategyDriver` protocol boundary in backtest.
- Existing structure-test style in `tests/structure/architecture`.
- Existing public import smoke-test style in `tests/smoke/local` and
  `tests/integration/commands`.

Do not reuse by importing:

- private `quantleet.research.parameter_exploration._validate_json_scalar`
  from `quantleet.strategy`
- private backtest runtime helpers from `quantleet.strategy`
- `quantleet.research.series` from `quantleet.strategy`

### Affected Areas

Directly affected:

- new `src/quantleet/strategy/*`
- `src/quantleet/research/strategy.py`
- `src/quantleet/research/series.py`
- `src/quantleet/research/__init__.py`
- imports in research indicator code if they should point at canonical
  `quantleet.strategy.series`
- architecture repo tools and structure tests
- strategy/config unit and integration tests
- public import smoke/build tests

Indirectly affected:

- Many tests import `Strategy` from `quantleet.research`; these should continue
  passing through re-export.
- Some tests import `Strategy` from `quantleet.research.strategy`; this module
  should remain a re-export compatibility path.
- Some tests import `SeriesView` from `quantleet.research.series`; this module
  should remain a re-export compatibility path.
- Coverage gate covers new source files, so tests must cover the new package
  well enough to keep global coverage above 90%.

## Architecture And Design Pattern

### Package Ownership

Create a new package:

```text
src/quantleet/strategy/
  __init__.py
  config.py
  series.py
  strategy.py
```

Responsibilities:

- `config.py`
  - `StrategyConfig`
  - config field discovery
  - config value validation
  - normalized snapshot mapping
  - exception hierarchy

- `series.py`
  - `SeriesView`
  - `OHLCVDataView`
  - `_SeriesBuffer`

- `strategy.py`
  - `PositionView`
  - `Strategy`
  - generic config declaration resolution
  - runtime `self.config` setup
  - existing order-intake behavior

- `__init__.py`
  - public exports:
    - `Strategy`
    - `StrategyConfig`
    - `StrategyConfigError`
    - `StrategyConfigDeclarationError`
    - `StrategyConfigValidationError`
    - `StrategyConfigMutationError`

Do not export public discovery/materialization helper functions.

### Compatibility Re-Exports

Replace `src/quantleet/research/strategy.py` with a compatibility re-export:

```python
from quantleet.strategy import Strategy

__all__ = ["Strategy"]
```

Replace `src/quantleet/research/series.py` with compatibility re-exports:

```python
from quantleet.strategy.series import OHLCVDataView, SeriesView

__all__ = ["OHLCVDataView", "SeriesView"]
```

Update `src/quantleet/research/__init__.py` so `Strategy` is loaded from
`quantleet.strategy`, while `ParameterStudy`, `qc`, and `ta` remain under
`research`.

### StrategyConfig Mechanics

Use a small standard-library implementation rather than dataclass inheritance
or pydantic.

Recommended internal model:

```python
@dataclass(frozen=True, slots=True)
class _ConfigField:
    name: str
    annotation: object
    value_type: type[str] | type[int] | type[float] | type[bool]
    optional: bool
    default: JSONConfigScalar
```

Public scalar type:

```python
JSONConfigScalar = str | int | float | bool | None
```

`StrategyConfig.__init_subclass__` should:

1. collect inherited `__config_fields__` from `StrategyConfig` bases
2. inspect subclass `__annotations__`
3. ignore names starting with `_`
4. reject public annotated fields without defaults
5. reject unsupported annotations
6. validate defaults against annotation and JSON-scalar policy
7. apply subclass redeclarations over inherited fields
8. store stable field metadata on the class

`StrategyConfig.__init__(**overrides)` should:

1. reject unknown override keys
2. validate override values against field metadata
3. merge defaults plus overrides
4. store an immutable mapping or copied dict internally
5. mark the instance frozen

`StrategyConfig.__getattribute__` should return materialized values for config
field names before class attributes, so class-level defaults do not mask
overrides.

`StrategyConfig.__setattr__` should raise
`StrategyConfigMutationError` after materialization for any mutation attempt.

Expose normalized snapshot via an instance method:

```python
config.to_mapping() -> dict[str, JSONConfigScalar]
```

This is not a public materialization helper. It is the object-level normalized
snapshot required by the product contract.

### Optional Type Handling

Support only these annotations:

- `str`
- `int`
- `float`
- `bool`
- `str | None`
- `int | None`
- `float | None`
- `bool | None`
- `Optional[str]`
- `Optional[int]`
- `Optional[float]`
- `Optional[bool]`

Implementation should use `typing.get_origin`, `typing.get_args`, and
`types.UnionType` handling for PEP 604 unions.

Validation rules:

- `bool` accepted only for `bool`
- `int` accepted for `int`, not `bool`
- `int` accepted for `float`
- `float` accepted for `float` only if finite
- `bool` rejected for `int` and `float`
- `None` accepted only when optional
- `str` accepted only for `str`

Reject:

- `Literal`
- `Enum`
- collections
- custom classes
- callables
- non-finite float defaults/values

### Strategy Generic And Config Resolution

Make `Strategy` generic:

```python
ConfigT = TypeVar("ConfigT", bound=StrategyConfig)

class Strategy(Generic[ConfigT], ABC):
    config_type: ClassVar[type[StrategyConfig]]
```

`Strategy.__init_subclass__` should:

1. infer config type from `Strategy[Config]` where present
2. read explicit `config_type` fallback where present
3. accept no declaration as empty `StrategyConfig`
4. accept same-type redundant declaration
5. reject conflicting declarations
6. reject config declarations that are not `StrategyConfig` subclasses

Runtime construction:

```python
def __init__(self, config: ConfigT | None = None) -> None:
    materialized = config if config is not None else self.config_type()
    self.config = materialized
    self._reset_runtime_state()
```

Also block reassignment of `strategy.config` after initialization. A custom
constructor that bypasses `super().__init__()` remains an advanced
user-responsibility failure path.

Config-less strategies use `StrategyConfig()` as the empty config instance.
`StrategyConfig().to_mapping()` returns `{}`.

### Dependency Rules

Update architecture rules so `strategy` is recognized as a Tier B shared
capability:

- add `strategy` to Tier B domains in `_repo_tools.py`
- allow:
  - `strategy -> trading`
  - `research -> strategy`
  - `backtest -> strategy`
  - `execution -> strategy`
- do not allow:
  - `strategy -> research`
  - `strategy -> backtest`
  - `strategy -> execution`
  - `strategy -> integrations`

`quantleet.strategy` should depend only on standard library and
`quantleet.trading`.

## Data And Control Flow

### Config Declaration Flow

```text
user defines StrategyConfig subclass
  -> StrategyConfig.__init_subclass__ collects/validates fields
  -> class stores stable field metadata
```

Failure examples:

- public annotation without default
- unsupported annotation
- non-scalar default
- non-optional `None`

### Strategy Declaration Flow

```text
user defines Strategy[MyConfig]
  -> Strategy.__init_subclass__ resolves effective config type
  -> same-type config_type fallback accepted
  -> conflicting config declarations rejected
  -> class stores effective config_type
```

### Runtime Construction Flow

```text
strategy = MyStrategy()
  -> Strategy.__init__ creates MyConfig() from defaults
  -> attaches self.config
  -> resets runtime state

strategy = MyStrategy(MyConfig(rsi_period=7))
  -> Strategy.__init__ validates supplied config instance
  -> attaches self.config
  -> resets runtime state
```

### Snapshot Flow

```text
config = MyConfig(rsi_period=7)
config.to_mapping()
  -> {"rsi_period": 7, ...defaults}
```

Downstream Stage 2/3 will use this mapping for study rows and reports. Stage 1
does not wire it into `ParameterStudy` or `BacktestReport`.

## Major Files And Responsibilities

### Create

- `src/quantleet/strategy/__init__.py`
  - canonical public exports

- `src/quantleet/strategy/config.py`
  - `StrategyConfig`
  - exception hierarchy
  - field metadata
  - primitive/optional validation
  - `to_mapping()`

- `src/quantleet/strategy/series.py`
  - move existing `SeriesView`, `_SeriesBuffer`, `OHLCVDataView`

- `src/quantleet/strategy/strategy.py`
  - move existing `Strategy` and `PositionView`
  - add generic/config behavior
  - keep existing order-intake methods intact

- `tests/unit/strategy/test_strategy_config_contract.py`
  - config field discovery, inheritance, fallback declarations, invalid
    declarations

- `tests/unit/strategy/test_strategy_config_materialization.py`
  - defaults plus overrides, `to_mapping()`, primitive compatibility,
    optional compatibility, immutable config mutation failures

- `tests/unit/strategy/test_strategy_surface.py`
  - canonical `Strategy[Config]`, empty config, no `__init__` DX, config
    reassignment protection

- `tests/integration/strategy/test_strategy_config_construction.py`
  - real strategy subclass through framework construction path and
    `_StrategyDriver` or minimal backtest path where necessary

- `tests/structure/architecture/test_strategy_config_boundaries.py`
  - package ownership and dependency boundaries

- `tests/structure/docs/test_strategy_configuration_contract_docs.py`
  - product/test specs route StrategyConfig work and keep WFA paused

### Modify

- `src/quantleet/research/strategy.py`
  - convert to re-export from `quantleet.strategy`

- `src/quantleet/research/series.py`
  - convert to re-export from `quantleet.strategy.series`

- `src/quantleet/research/__init__.py`
  - load `Strategy` from `quantleet.strategy`

- `src/quantleet/research/indicators/runtime/factory.py`
  - import `SeriesView` from canonical `quantleet.strategy.series`
  - or keep compatibility import temporarily if the diff is smaller, but avoid
    any `quantleet.strategy -> quantleet.research` dependency

- `tests/smoke/local/test_public_imports.py`
  - assert `quantleet.strategy` exposes `Strategy`, `StrategyConfig`, and
    public config errors
  - assert `quantleet.research.Strategy` remains available

- `tests/integration/commands/test_built_artifact_imports.py`
  - assert built wheel exposes `quantleet.strategy`

- `tests/structure/architecture/test_capability_package_roots.py`
  - add `src/quantleet/strategy/__init__.py`

- `tests/structure/architecture/test_domain_boundaries.py`
  - assert strategy dependency rules

- `src/quantleet/_repo_tools.py`
  - add `strategy` to known Tier B domains and allowed dependency edges

- `ARCHITECTURE.md`
  - add `strategy` to top-level contexts and dependency rules

- `docs/design-docs/package-topology-and-naming.md`
  - include `quantleet.strategy.api` only if choosing facade wording; otherwise
    note `strategy` as a capability package in the topology guidance

- `README.md`, `docs/site/quickstart.md`,
  `docs/site/guides/strategy-authoring.md`,
  `docs/site/reference/public-api.md`
  - update canonical strategy import examples to use:

    ```python
    from quantleet.strategy import Strategy
    from quantleet.research import qc, ta
    ```

  - do not migrate `ParameterStudy` examples to `strategy=...` in this stage

## Test Implementation Plan

Use TDD by adding focused failing tests first.

### Unit Tests

`tests/unit/strategy/test_strategy_config_contract.py`:

- public annotated defaults become fields
- `_private` annotated fields are ignored
- unannotated class attributes are ignored
- missing default raises `StrategyConfigDeclarationError`
- inherited public fields are included
- subclass redeclaration wins
- stable order is base fields then subclass fields
- unsupported annotations raise `StrategyConfigDeclarationError`
- non-scalar defaults raise `StrategyConfigDeclarationError`
- non-optional `None` default raises `StrategyConfigDeclarationError`
- optional `None` default is accepted
- same-type `Strategy[Config]` plus `config_type = Config` is accepted
- conflicting generic/fallback config raises `StrategyConfigDeclarationError`
- explicit fallback-only `config_type = Config` is accepted
- invalid fallback type raises `StrategyConfigDeclarationError`
- config-less strategy gets empty config

`tests/unit/strategy/test_strategy_config_materialization.py`:

- no overrides preserves defaults
- partial overrides preserve non-searched defaults
- unknown override raises `StrategyConfigValidationError`
- private override raises `StrategyConfigValidationError`
- primitive compatibility table:
  - `int`: accepts `int`, rejects `bool`, rejects `float`
  - `float`: accepts finite `int` and finite `float`, rejects `bool`
  - `bool`: accepts `bool`, rejects `1`
  - `str`: accepts `str`, rejects non-strings
  - optional primitive accepts `None`
  - non-optional rejects `None`
  - non-finite float rejects
- `to_mapping()` returns detached plain dict
- `config.field = value` raises `StrategyConfigMutationError`
- assigning a new public attr after materialization raises
  `StrategyConfigMutationError`

`tests/unit/strategy/test_strategy_surface.py`:

- `class S(Strategy[C])` can read `self.config.field`
- `S()` materializes default config
- `S(C(field=...))` uses provided config
- `S(config=...)` keyword works if the technical implementation supports it
  cleanly; otherwise use positional config only and document that choice in the
  test name
- `class S(Strategy)` gets empty config
- ordinary no-`__init__` strategy construction initializes runtime state
- existing order-intake behavior remains available
- `strategy.config = other_config` raises `StrategyConfigMutationError`

### Integration Tests

`tests/integration/strategy/test_strategy_config_construction.py`:

- define a configured strategy with no `__init__`
- use `_StrategyDriver` or a small `BacktestEngine` run to prove:
  - `init()` sees `self.config`
  - `on_bar()` sees `self.config`
  - runtime state resets still work
  - config mutation attempts during lifecycle fail before orders are emitted

Keep this test narrow. Do not assert optimizer or reporting migration behavior.

### Structure And Smoke Tests

`tests/structure/architecture/test_strategy_config_boundaries.py`:

- `src/quantleet/strategy/__init__.py` exists
- `strategy` is recognized by architecture checks
- `quantleet.strategy` does not import `research`, `backtest`, or `execution`
- `research`, `backtest`, and `execution` may import `strategy` under the
  architecture rules

`tests/smoke/local/test_public_imports.py`:

- `import quantleet.strategy`
- `quantleet.strategy.Strategy`
- `quantleet.strategy.StrategyConfig`
- public exception types
- `quantleet.research.Strategy` still exists as migration path

`tests/integration/commands/test_built_artifact_imports.py`:

- same public import assertions inside the built wheel smoke script

### Regression Tests To Preserve

Existing tests that use `quantleet.research.Strategy` or
`quantleet.research.strategy.Strategy` should continue passing through
re-exports. Do not mass-rewrite all tests unless needed for canonical docs or
new package assertions.

Existing `ParameterStudy` tests should continue passing unchanged, including
`strategy_factory` behavior.

Existing report snapshot tests should continue passing unchanged; do not
replace `strategy_parameters` in Stage 1.

## Implementation Order

### Task 1: Add Architecture Tests For `strategy` Package

**Files:**

- Modify: `tests/structure/architecture/test_capability_package_roots.py`
- Modify: `tests/structure/architecture/test_domain_boundaries.py`
- Create: `tests/structure/architecture/test_strategy_config_boundaries.py`

**Steps:**

1. Add failing tests that expect `src/quantleet/strategy/__init__.py`.
2. Add failing tests that `strategy` can depend on `trading`.
3. Add failing tests that `research`, `backtest`, and `execution` can depend on
   `strategy`.
4. Add failing tests that `strategy` cannot depend on `research`, `backtest`,
   or `execution`.
5. Run:

   ```bash
   uv run pytest tests/structure/architecture -q
   ```

Expected: fails because `strategy` package and architecture rules do not exist
yet.

### Task 2: Update Architecture Rule Surface

**Files:**

- Modify: `src/quantleet/_repo_tools.py`
- Modify: `ARCHITECTURE.md`
- Modify: `docs/design-docs/package-topology-and-naming.md`

**Steps:**

1. Add `strategy` as a Tier B domain.
2. Add allowed dependency edges:
   - `strategy -> trading`
   - `research -> strategy`
   - `backtest -> strategy`
   - `execution -> strategy`
3. Update architecture docs to list `strategy` as a top-level context.
4. Run:

   ```bash
   uv run pytest tests/structure/architecture -q
   uv run poe repo-check
   ```

Expected: structure tests still fail until package exists, but architecture
rule assertions for dependency validation should pass after package creation in
the next task.

### Task 3: Create `quantleet.strategy` Package And Move Series Surface

**Files:**

- Create: `src/quantleet/strategy/__init__.py`
- Create: `src/quantleet/strategy/series.py`
- Modify: `src/quantleet/research/series.py`
- Modify: `src/quantleet/research/indicators/runtime/factory.py`

**Steps:**

1. Move the contents of `research/series.py` into `strategy/series.py`.
2. Turn `research/series.py` into a re-export shim.
3. Update indicator runtime imports to the canonical `quantleet.strategy.series`
   path where practical.
4. Keep `SeriesView` behavior unchanged.
5. Run:

   ```bash
   uv run pytest tests/unit/research/test_series.py tests/unit/research/test_indicator_surface.py -q
   ```

Expected: existing series and indicator tests pass.

### Task 4: Add `StrategyConfig` Tests

**Files:**

- Create: `tests/unit/strategy/test_strategy_config_contract.py`
- Create: `tests/unit/strategy/test_strategy_config_materialization.py`

**Steps:**

1. Write tests for declaration, inheritance, fallback declaration, defaults,
   unsupported annotations, optional handling, and public exceptions.
2. Write tests for materialization, `to_mapping()`, primitive compatibility,
   unknown/private override failure, and immutability.
3. Run:

   ```bash
   uv run pytest tests/unit/strategy/test_strategy_config_contract.py tests/unit/strategy/test_strategy_config_materialization.py -q
   ```

Expected: fails because `StrategyConfig` is not implemented yet.

### Task 5: Implement `StrategyConfig`

**Files:**

- Create: `src/quantleet/strategy/config.py`
- Modify: `src/quantleet/strategy/__init__.py`

**Steps:**

1. Add exception hierarchy.
2. Add `JSONConfigScalar` type alias.
3. Add private `_ConfigField` dataclass.
4. Implement field collection and validation in `__init_subclass__`.
5. Implement `StrategyConfig.__init__(**overrides)`.
6. Implement `__getattribute__` for field reads.
7. Implement `__setattr__` mutation guard.
8. Implement `to_mapping()`.
9. Export public types from `quantleet.strategy`.
10. Run:

    ```bash
    uv run pytest tests/unit/strategy/test_strategy_config_contract.py tests/unit/strategy/test_strategy_config_materialization.py -q
    uv run mypy src
    ```

Expected: new config tests and typing pass.

### Task 6: Move And Extend `Strategy`

**Files:**

- Create: `src/quantleet/strategy/strategy.py`
- Modify: `src/quantleet/research/strategy.py`
- Modify: `src/quantleet/research/__init__.py`
- Modify: `src/quantleet/strategy/__init__.py`

**Steps:**

1. Move existing `PositionView` and `Strategy` implementation into
   `strategy/strategy.py`.
2. Update imports to use `quantleet.strategy.series`.
3. Make `Strategy` generic over `StrategyConfig`.
4. Add config declaration resolution in `__init_subclass__`.
5. Add `config_type` fallback handling.
6. Add default empty config behavior.
7. Add base constructor config materialization:

   ```python
   def __init__(self, config: ConfigT | None = None) -> None:
       ...
   ```

8. Protect `strategy.config` reassignment.
9. Turn `research/strategy.py` into a re-export shim.
10. Update `research/__init__.py` lazy import for `Strategy`.
11. Run:

    ```bash
    uv run pytest tests/unit/research/test_strategy_surface.py -q
    uv run pytest tests/unit/strategy -q
    uv run mypy src
    ```

Expected: existing strategy behavior remains compatible and new strategy tests
pass.

### Task 7: Add Strategy Surface Tests

**Files:**

- Create: `tests/unit/strategy/test_strategy_surface.py`
- Create: `tests/integration/strategy/test_strategy_config_construction.py`

**Steps:**

1. Test `Strategy[Config]` construction with default config.
2. Test provided config instance.
3. Test config-less strategy.
4. Test no-`__init__` strategy lifecycle.
5. Test `self.config` availability in `init()` and `on_bar()`.
6. Test config mutation failure during lifecycle.
7. Run:

   ```bash
   uv run pytest tests/unit/strategy tests/integration/strategy -q
   ```

Expected: passes.

### Task 8: Update Public Import And Build Smoke Tests

**Files:**

- Modify: `tests/smoke/local/test_public_imports.py`
- Modify: `tests/integration/commands/test_built_artifact_imports.py`

**Steps:**

1. Assert `quantleet.strategy` imports cleanly.
2. Assert canonical exports exist.
3. Assert `quantleet.research.Strategy` still exists.
4. Assert root `quantleet` still does not export direct symbols unless a later
   public API spec changes that.
5. Run:

   ```bash
   uv run pytest tests/smoke/local/test_public_imports.py -q
   uv run pytest tests/integration/commands/test_built_artifact_imports.py -q
   ```

Expected: passes.

### Task 9: Update User-Facing Docs For Canonical Import

**Files:**

- Modify: `README.md`
- Modify: `docs/site/quickstart.md`
- Modify: `docs/site/guides/strategy-authoring.md`
- Modify: `docs/site/reference/public-api.md`
- Modify: any structure docs tests that assert old quickstart import strings

**Steps:**

1. Replace canonical strategy imports with:

   ```python
   from quantleet.strategy import Strategy
   from quantleet.research import qc, ta
   ```

2. Do not change `ParameterStudy` examples to `strategy=...`.
3. Mention `quantleet.research.Strategy` only as a migration-compatible
   re-export if public docs need to explain it.
4. Run:

   ```bash
   uv run pytest tests/structure/docs -q
   ```

Expected: docs structure tests pass.

### Task 10: Full Verification

Run targeted verification first:

```bash
uv run pytest tests/unit/strategy tests/integration/strategy -q
uv run pytest tests/unit/research/test_strategy_surface.py tests/unit/research/test_series.py -q
uv run pytest tests/structure/architecture tests/structure/docs -q
uv run pytest tests/smoke/local/test_public_imports.py -q
uv run mypy src
uv run poe repo-check
```

Then run required repo verification:

```bash
uv run poe verify-runtime
```

Reason: this slice moves strategy runtime code that is listed in the
runtime-sensitive research/backtest path. `verify-runtime` includes default
verification plus the performance gate.

## Migration And Compatibility

Compatibility preserved:

- `from quantleet.research import Strategy`
- `from quantleet.research.strategy import Strategy`
- `from quantleet.research.series import SeriesView, OHLCVDataView`
- existing direct `BacktestEngine.run(..., strategy=StrategyInstance)` behavior
- existing `ParameterStudy(..., strategy_factory=...)` behavior
- existing `Strategy.parameters()` behavior for report metadata until Stage 3

Intentional new canonical path:

```python
from quantleet.strategy import Strategy, StrategyConfig
```

Avoid:

- deleting old imports in this stage
- updating `ParameterStudy` constructor signatures
- changing report dataclasses
- changing public root package `quantleet.__all__`

## Risks And Mitigations

### Risk: Architecture Checks Reject New Top-Level Package

Mitigation:

- update `_repo_tools.py` domain lists and dependency edges before relying on
  repo-check
- add structure tests for the new package and dependency rules

### Risk: Moving `SeriesView` Breaks Indicators

Mitigation:

- keep `quantleet.research.series` as a re-export shim
- run existing `test_series.py`, `test_indicator_surface.py`, and indicator
  runtime tests

### Risk: Generic Config Discovery Becomes Too Clever

Mitigation:

- tests assert observable config behavior, not `__orig_bases__` mechanics
- keep `config_type` fallback public advanced path
- reject conflicts early

### Risk: `StrategyConfig` Immutability Interferes With Class Defaults

Mitigation:

- store materialized values in a private internal mapping
- use `__getattribute__` to return instance materialized field values before
  class-level defaults
- block mutation through `__setattr__`
- compare snapshots via `to_mapping()`

### Risk: Custom Strategy Constructors Bypass Config Setup

Mitigation:

- preserve `super().__init__()` compatibility
- document custom constructors as advanced/user-responsibility
- keep canonical tests focused on no-`__init__` strategy authoring and
  constructors that call `super().__init__()`

### Risk: Coverage Drops From New Source Files

Mitigation:

- write unit tests before implementation for all config branches
- run `uv run poe coverage` or full `uv run poe verify-runtime`

### Risk: Docs Accidentally Teach Stage 2 API Early

Mitigation:

- update only strategy import paths
- do not show `ParameterStudy(strategy=...)` until Stage 2
- keep WFA paused docs intact

## Success Conditions

Implementation is successful when:

- `quantleet.strategy` is importable from source and built wheel.
- `Strategy` and `StrategyConfig` are canonical exports from
  `quantleet.strategy`.
- `quantleet.research.Strategy` still imports as a compatibility re-export.
- Existing strategy/backtest/parameter-study tests still pass.
- `StrategyConfig` validates fields/defaults according to the Stage 1 contract.
- `Strategy[Config]` and `config_type` fallback work as specified.
- Materialized config instances are immutable.
- `to_mapping()` returns detached normalized plain mappings.
- `Strategy` runtime behavior and order-intake behavior remain unchanged.
- Architecture checks accept `strategy` as a shared Tier B capability package.
- No Stage 2/3 behavior is implemented accidentally.
- `uv run poe verify-runtime` passes.

## Verification Commands

Run during implementation:

```bash
uv run pytest tests/unit/strategy -q
uv run pytest tests/integration/strategy -q
uv run pytest tests/unit/research/test_strategy_surface.py tests/unit/research/test_series.py -q
uv run pytest tests/structure/architecture tests/structure/docs -q
uv run pytest tests/smoke/local/test_public_imports.py -q
uv run mypy src
uv run poe repo-check
```

Final gate:

```bash
uv run poe verify-runtime
```

If runtime performance gate fails after the move, investigate import/runtime
regressions before broadening scope. Do not bypass the performance gate.

## Open Questions

No Stage 1 human product decisions remain open.

Downstream Stage 2/3 questions remain open and must not be resolved in this
implementation:

- constraint callback input shape
- duplicate-equivalent grid values such as `1` and `1.0`
- constraint-rejected row `strategy_config` representation
- advanced `strategy_factory` row shape
- `strategy_parameters` removal versus compatibility alias

## Documentation Consistency Addendum

### Scope

After Stage 1 implementation, user-facing docs, concept docs, example docs, and
notebooks must teach `quantleet.strategy.Strategy` as the canonical strategy
authoring path. Historical execution plans remain audit records and are not
rewritten.

This addendum exists because future agent runs learn from repository-local
examples. Leaving current examples on the compatibility import path makes the
legacy path look canonical and increases the cost of later shim removal.

### Updated Surfaces

- Product specs:
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/data-ingestion.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/parameter-exploration-test-scenarios.md`
- Design/concept docs:
  - `docs/design-docs/unified-strategy-runtime-design.md`
- Reference/example docs:
  - `docs/references/research-ergonomics-quickstart.md`
- Notebooks:
  - `notebooks/research-ergonomics-quickstart.ipynb`
  - `notebooks/binance-usdm-rsi-2024-ad-hoc.ipynb`
  - `notebooks/backtest-plotting-real-data-example.ipynb`
- Structure and smoke tests that assert those examples:
  - `tests/structure/docs/test_research_ergonomics_quickstart.py`
  - `tests/structure/docs/test_parameter_exploration_docs.py`
  - `tests/structure/repo/test_repository_entrypoint_docs.py`
  - `tests/smoke/local/test_public_beta_examples.py`

### Acceptance Contract

- Non-historical docs and notebooks no longer teach
  `from quantleet.research import Strategy`.
- Compatibility references to `quantleet.research.Strategy` remain only where
  they explicitly describe the migration/re-export path.
- `ParameterStudy`, `ta`, and `qc` remain under `quantleet.research`.
- No Stage 2 API such as `ParameterStudy(strategy=...)` is introduced.
- Targeted structure/smoke/notebook validation passes.
