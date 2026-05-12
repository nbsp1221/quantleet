# Stage 3.5 Direct Backtest API Implementation Plan

- Date: 2026-05-12
- Task: implement Stage 3.5 direct backtest class-plus-config API alignment
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: replace the current direct backtest strategy-instance input with the
  Stage 3.5 `BacktestEngine.run(strategy=StrategyClass, config=...)` contract,
  while reusing the existing `Strategy` and `StrategyConfig` construction model.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/direct-backtest-class-config-api.md`
  - `docs/product-specs/direct-backtest-class-config-api-test-scenarios.md`
  - `docs/product-specs/strategy-configuration-contract.md`
  - `docs/product-specs/strategy-configuration-contract-test-scenarios.md`
  - `docs/product-specs/reporting-config-source-of-truth.md`
  - `docs/product-specs/reporting-config-source-of-truth-test-scenarios.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/parameter-exploration-test-scenarios.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/public-beta-documentation.md`
  - `docs/product-specs/wfa-prerequisite-roadmap.md`
  - `docs/product-specs/walk-forward-analysis-readiness.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing: the slice changes the public direct backtest API,
  strategy/config construction, report provenance, parameter-study composition,
  current public examples, and WFA readiness tracking.
- In-repo scope:
  - `src/quantleet/backtest`
  - `src/quantleet/strategy` only if a narrow reusable type/error is required
  - `src/quantleet/research/parameter_exploration.py`
  - current tests under `tests/unit`, `tests/integration`, `tests/smoke`,
    `tests/structure`, and `tests/perf` that exercise direct backtests
  - current public docs, docs-site examples, README snippets, and maintained
    notebooks that demonstrate direct backtests
- Out-of-repo scope: external repositories, package release work, live broker
  connectors, exchange credentials, and network-backed live verification.
- Tier A progression requested: `no`
- Approval record, if required: not required; this is Tier B backtest,
  strategy, research, docs, and test work. No `trading` or `execution`
  implementation semantics are changed.
- Verification commands:
  - `uv run pytest -q tests/unit/backtest/test_direct_class_config_api.py`
  - `uv run pytest -q tests/unit/backtest/test_engine.py`
  - `uv run pytest -q tests/integration/research/test_backtest_engine_entrypoints.py`
  - `uv run pytest -q tests/integration/research/test_backtest_result_reporting_contract.py`
  - `uv run pytest -q tests/integration/strategy/test_strategy_config_construction.py`
  - `uv run pytest -q tests/integration/research/test_parameter_study_grid_search.py`
  - `uv run pytest -q tests/smoke/local/test_public_beta_examples.py`
  - `uv run poe repo-check`
  - `uv run poe verify-runtime`
  - `uv run poe verify`
  - `git diff --check`
- Success criteria:
  - direct backtests accept `strategy=StrategyClass` plus optional
    `config=StrategyConfigInstance`
  - direct strategy instances and dict configs are rejected before data loading
  - omitted config materializes `StrategyClass.config_type()`
  - every direct run constructs a fresh strategy instance
  - report metadata records the copied materialized `strategy_config`
  - `ParameterStudy` calls the same class-plus-config engine surface
  - current public examples and smoke tests teach only the new API
  - runtime-sensitive verification passes
- Out of scope:
  - WFA implementation
  - strategy factories or arbitrary dependency injection hooks
  - dict-to-config coercion in `BacktestEngine.run`
  - compatibility shims for pre-beta direct strategy instances
  - changes to trading or execution order semantics

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - compare implementation diff against this plan and the Stage 3.5 product and
    test specs
  - check that implementation reuses existing `Strategy` and `StrategyConfig`
    paths instead of adding a parallel construction model
  - verify that source loading happens only after strategy/config preflight
  - verify that public docs, smoke examples, and structure checks no longer
    teach direct strategy instances for current direct backtest usage
  - verify that temporary grep-style transition checks are either removed before
    completion or explicitly promoted to durable structure checks by a separate
    policy decision
- Acceptance artifact location: this plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution: the generator
  must implement only the planned files and behaviors, then the evaluator must
  cite fresh command output in this document before marking the slice complete.
- Checks the evaluator will use:
  - targeted tests listed in the planner contract
  - `uv run poe repo-check`
  - `uv run poe verify-runtime`
  - `uv run poe verify`
  - `git diff --check`
  - focused `rg` transition checks for old current-public examples during the
    implementation session
- Auto-fail conditions:
  - `BacktestEngine.run` still accepts a direct strategy instance as a supported
    path
  - `BacktestEngine.run` accepts dict config input
  - `ParameterStudy` constructs the strategy instance itself for normal
    candidate execution
  - a new strategy construction API bypasses `Strategy.__init__` or
    `StrategyConfig`
  - report config is derived from `Strategy.parameters()`, mutable runtime
    state, or introspection of arbitrary public attributes
  - current public docs or smoke examples still teach the old direct-instance
    usage

## Implementation Goal

Stage 3.5 changes direct backtesting from "the caller passes a ready strategy
object" to "the caller passes a strategy class and, optionally, a typed config
object." The engine becomes the single owner of direct-run strategy
construction.

The target direct call is:

```python
result = engine.run(
    bars=bars,
    strategy=SmaCrossStrategy,
    config=SmaCrossConfig(fast=10, slow=30),
    label="sma-cross",
)
```

Config-less and default-config strategies may omit `config`:

```python
result = engine.run(source=source, strategy=SmaCrossStrategy)
```

## Scope And Non-Scope

In scope:

- update `BacktestEngine.run` public signature and runtime preflight
- keep `_run_backtest` and `_StrategyDriver` operating on an already
  materialized strategy instance
- update `ParameterStudy` to call `engine.run(..., strategy=StrategyClass,
  config=ConfigInstance, ...)`
- migrate tests, support strategies, smoke examples, docs, and notebooks that
  represent the current public direct backtest surface
- preserve existing report, result, and execution semantics

Not in scope:

- WFA fold orchestration or result objects
- paper/live execution
- new config serialization APIs
- dependency injection for non-config strategy constructor arguments
- historical archived plans or completed design records unless a current
  structure check treats them as active public surface

## Codebase Survey Findings

The project is a Python 3.13 library under `src/quantleet` with strict `ruff`,
`mypy`, `pytest`, coverage, repo checks, and `uv`/`poe` verification tasks.

Relevant package contexts:

- `quantleet.strategy` owns `Strategy`, `StrategyConfig`, and strategy
  construction validation.
- `quantleet.backtest` owns direct historical execution and report creation.
- `quantleet.research` owns parameter exploration and composes the public
  backtest surface.
- `quantleet.data` owns `BarSeries`, `TimeBar`, and data source loading.
- `quantleet.trading` owns trading-domain objects; Stage 3.5 should not change
  those semantics.

Current canonical construction path:

- `src/quantleet/strategy/strategy.py`
  - `Strategy.__init__(config=None)` materializes config through
    `_materialize_config`.
  - `Strategy.config_type()` resolves the declared config class.
  - exact config type matching already exists via
    `type(config) is self.config_type`.
  - runtime state reset already happens during construction.
- `src/quantleet/strategy/config.py`
  - `StrategyConfig` validates declared JSON-scalar fields.
  - `to_mapping()` returns the reportable snapshot shape.
  - `StrategyConfigValidationError` already covers config mismatch and invalid
    values.

Current direct backtest path:

- `src/quantleet/backtest/engine.py`
  - `BacktestEngine.run` currently accepts `strategy: StrategyLike`.
  - it validates bars/source exclusivity, snapshots
    `validate_strategy_like_config(strategy).to_mapping()`, loads data, then
    calls `_run_backtest`.
- `src/quantleet/backtest/runtime.py`
  - `_run_backtest` takes a concrete `StrategyLike` instance and a
    `strategy_config` mapping. This should remain the runtime boundary.
- `src/quantleet/backtest/strategy_runtime.py`
  - `_StrategyDriver` and `StrategyLike` are runtime protocols for an already
    constructed strategy object.
  - `validate_strategy_like_config` exists only to support the old direct
    strategy-instance engine path.
- `src/quantleet/backtest/reporting.py`
  - `RunManifest.strategy_config` already stores a plain dict snapshot.
  - report creation does not need a new provenance path.

Current parameter-study path:

- `src/quantleet/research/parameter_exploration.py`
  - `ParameterStudy` already requires `strategy: type[Strategy[StrategyConfig]]`.
  - candidates already materialize `StrategyConfig` instances and snapshots.
  - normal execution currently constructs `self.strategy(prepared.config)`
    before calling `engine.run(strategy=strategy_instance, ...)`.
  - Stage 3.5 should remove this normal direct construction and call the engine
    with the strategy class plus prepared config.

Current test and example surface:

- Unit and integration tests frequently pass `Strategy()` instances into
  `engine.run`.
- `tests/support_backtest.py` and
  `tests/integration/research/support_backtest_runner.py` are high-leverage
  migration points for many call sites.
- Some test strategies currently use non-config constructor arguments, notably
  stop-limit and canonical signal strategies. These need narrow
  `StrategyConfig` classes instead of direct constructor kwargs where they flow
  through `engine.run`.
- Current public examples in `README.md`, `docs/site`, smoke tests, and
  maintained notebooks still show `strategy=SmaCrossStrategy`.
- Structure tests in `tests/structure/repo/test_repository_entrypoint_docs.py`
  assert the old signature text in current specs and must be updated.

## Existing Paths To Reuse

Reuse:

- `Strategy.__init__`, `Strategy.config_type`, and existing exact config type
  validation as the only strategy materialization mechanism.
- `StrategyConfig.to_mapping()` for report snapshots and candidate records.
- `_run_backtest` for historical runtime execution after preflight.
- `_StrategyDriver` for per-bar runtime interaction with a materialized
  strategy instance.
- `ParameterStudy` candidate preparation and config snapshot helpers.
- Existing `BarSeries` and data source validation; only move strategy/config
  preflight before data loading.
- Existing smoke and structure-test harnesses for public example verification.

Do not create:

- a second config validation system inside `backtest`
- dict-to-config coercion in the direct Python API
- a `StrategyFactory` abstraction
- a new runtime path that bypasses `_run_backtest`
- a permanent compatibility branch for direct strategy instances

## Major Files And Responsibilities

Source files:

- `src/quantleet/backtest/engine.py`
  - change `BacktestEngine.run` to accept `strategy` as a `Strategy` subclass
    and `config` as `StrategyConfig | None`
  - validate strategy/config before `source.load()`
  - instantiate a fresh strategy for every run
  - pass the concrete strategy instance and copied config mapping into
    `_run_backtest`
- `src/quantleet/backtest/strategy_runtime.py`
  - keep `StrategyLike` and `_StrategyDriver` for runtime execution
  - remove or stop exporting `validate_strategy_like_config` if no remaining
    current runtime path needs it
- `src/quantleet/research/parameter_exploration.py`
  - replace normal candidate strategy preconstruction with
    `engine.run(bars=self.bars, strategy=self.strategy,
    config=prepared.config, label=...)`
  - preserve candidate failure classification, including distinguishing
    strategy-construction failures from backtest failures
- `src/quantleet/backtest/__init__.py`
  - update exports only if a new public error type is intentionally introduced
    after implementation review

Test files:

- `tests/unit/backtest/test_direct_class_config_api.py`
  - new focused contract tests for accepted inputs, rejected inputs, preflight
    order, report snapshot, and fresh instances
- `tests/unit/backtest/test_engine.py`
  - update existing engine validation tests to pass strategy classes
- `tests/unit/backtest/test_strategy_like_report_config_validation.py`
  - replace old arbitrary `StrategyLike` metadata tests with class-plus-config
    report snapshot tests, or remove if fully covered by the new contract file
- `tests/unit/research/support_parameter_study.py`
  - update `CountingEngine.run` to accept and record `strategy` class plus
    `config`
- `tests/unit/research/test_grid_search_records.py`
  - update direct engine call to the new API
- `tests/integration/research/test_parameter_study_grid_search.py`
  - assert one fresh strategy instance per admissible candidate through the
    engine-owned path
- `tests/integration/research/test_backtest_engine_entrypoints.py`
  - update `bars` and `source` entrypoint tests to the class-plus-config API
  - add or keep source-not-called assertions for invalid preflight
- `tests/integration/research/test_backtest_result_reporting_contract.py`
  - update report provenance assertions to pass strategy classes/configs
- `tests/integration/strategy/test_strategy_config_construction.py`
  - update configured strategy construction and mutation tests to the new API
- `tests/support_backtest.py`
  - change canonical backtest runner helpers to accept strategy classes and
    optional configs
  - convert constructor-argument signal strategies to config-backed strategies
    where they are run through `BacktestEngine`
- `tests/integration/research/support_backtest_runner.py`
  - update runner helpers to the class-plus-config shape
  - convert stop-limit constructor-argument strategies to config-backed
    strategies
- `tests/smoke/local/test_public_beta_examples.py`
  - update public beta examples to the new API
- `tests/smoke/local/test_backtest_result_reporting_quickstart.py`
  - update quickstart smoke path
- `tests/structure/repo/test_repository_entrypoint_docs.py`
  - update required current-doc API markers

Docs and examples:

- `README.md`
- `docs/site/quickstart.md`
- `docs/site/guides/backtesting.md`
- `docs/references/research-ergonomics-quickstart.md`
- `notebooks/research-ergonomics-quickstart.ipynb`
- maintained real-data example notebooks that act as current examples
- current product specs that still describe the old direct run signature:
  `backtest.md`, `backtest-mvp.md`, `research-ergonomics.md`,
  `data-ingestion.md`, `backtest-plotting.md`,
  `reporting-config-source-of-truth.md`,
  `reporting-config-source-of-truth-test-scenarios.md`, and related current
  test scenario docs

## Data And Control Flow

Target `BacktestEngine.run` flow:

1. Validate `label`.
2. Validate exactly one of `bars` or `source`.
3. Validate `strategy` is a `Strategy` subclass, not an instance or unrelated
   class.
4. Validate `config` is `None` or a `StrategyConfig` instance; reject dicts.
5. Materialize the strategy before data loading:
   - if `config is None`, call `strategy.config_type()`
   - construct `strategy_instance = strategy(materialized_config)`
   - let existing `Strategy.__init__` enforce exact config type and default
     validation
6. Copy `strategy_config = strategy_instance.config.to_mapping()` before
   runtime execution.
7. Load or validate bars.
8. Call `_run_backtest(bars=..., strategy=strategy_instance,
   strategy_config=strategy_config, ...)`.
9. Return the existing `BacktestResult`.

Target `ParameterStudy.grid_search` flow:

1. Validate parameter grid and strategy config keys as today.
2. Materialize candidate `StrategyConfig` as today.
3. Run constraints against the candidate config snapshot as today.
4. Call the engine with the strategy class and candidate config.
5. Record success, rejection, construction failure, backtest failure, and metric
   extraction failure in the existing `GridSearchRow` shape.

## Architecture And Pattern Choices

Use the existing capability boundaries:

- `strategy` remains the owner of config declaration and materialization.
- `backtest` orchestrates direct run preflight and historical runtime.
- `research` composes `backtest`; it does not redefine direct strategy
  construction.

Use a thin orchestration helper in `backtest.engine` only if it reduces
duplication inside `BacktestEngine.run`. The helper should be private and should
return a simple materialized pair such as `(strategy_instance,
strategy_config_mapping)`.

Do not move `_run_backtest` to class-plus-config input. `_run_backtest` is a
lower-level runtime function and should continue receiving the already
constructed strategy object that `_StrategyDriver` knows how to drive.

Strategy construction failure classification is the only design point with
trade-off. The preferred implementation is to preserve existing
`ParameterStudy` row semantics without making `ParameterStudy` build strategy
instances itself for normal execution. If the engine needs to expose a
distinguishable construction failure signal, keep it as narrow as possible and
document whether it is public or private before exporting it.

## Test Implementation Plan

Add focused unit tests first:

- strategy class plus explicit config succeeds and reports the config snapshot
- omitted config materializes defaults and reports the full default snapshot
- config-less strategy reports `{}`
- wrong config type fails before `source.load()`
- dict config fails before `source.load()`
- strategy instance fails before `source.load()`
- non-strategy class fails before `source.load()`
- default config materialization errors fail before `source.load()`
- strategy constructor errors fail before `source.load()`
- repeated direct runs create fresh strategy instances

Then update integration tests:

- `bars` and `source` entrypoints still produce the same result semantics
- report run metadata still contains `strategy_class_name`,
  `strategy_display_name`, copied `strategy_config`, and no
  `strategy_parameters`
- `ParameterStudy` uses the direct class-plus-config API and preserves candidate
  records
- mutation tests still fail through `StrategyConfigMutationError`

Then update public example tests:

- smoke tests execute README-style and docs-site examples with
  `strategy=StrategyClass`
- structure tests assert the current docs mention the new canonical signature
- transition `rg` checks confirm no current public example teaches
  `strategy=SomeStrategy(...)` for direct backtests

Temporary transition check guidance:

- a one-off implementation checklist `rg` is acceptable during migration
- a committed grep-style test should be removed before final completion unless
  it is deliberately promoted to a durable current-docs policy

## Migration And Compatibility

This is a pre-beta breaking cleanup. Do not add compatibility shims.

Existing direct-instance examples should be edited as if the class-plus-config
API had been the intended design from the start. For example:

```python
- result = engine.run(source=source, strategy=SmaCrossStrategy, label="sma")
+ result = engine.run(source=source, strategy=SmaCrossStrategy, label="sma")
```

For configured strategies:

```python
- result = engine.run(bars=bars, strategy=SmaCrossStrategy(SmaCrossConfig(...)))
+ result = engine.run(
+     bars=bars,
+     strategy=SmaCrossStrategy,
+     config=SmaCrossConfig(...),
+ )
```

Test-only strategies with constructor arguments should become config-backed
strategies when those arguments represent run configuration. If a value is not
strategy configuration but test fixture data, prefer a small purpose-built
strategy class or test helper that keeps fixture data outside the public direct
run path.

## Risks And Mitigations

- Risk: `ParameterStudy` loses its current `strategy_construction` failure
  classification.
  - Mitigation: explicitly test failure-stage preservation and keep any engine
    construction failure signal narrow.
- Risk: broad test churn hides execution-semantics regressions.
  - Mitigation: change call shapes and constructor config plumbing without
    changing order/runtime assertions; run `verify-runtime`.
- Risk: canonical fixture helpers depend on constructor args for signal data.
  - Mitigation: convert only run-time strategy parameters to `StrategyConfig`;
    keep fixture-derived data generation in helpers and pass resulting config
    snapshots deliberately.
- Risk: docs cleanup misses current public examples.
  - Mitigation: use focused `rg` transition checks during the implementation
    session and keep executable smoke tests as the durable gate.
- Risk: over-abstracting the new path creates a second construction framework.
  - Mitigation: reuse `Strategy.__init__` and `StrategyConfig`; keep any helper
    private and local to `backtest.engine`.

## Implementation Order

1. Add the new unit contract test file for `BacktestEngine.run`.
2. Implement the class-plus-config path in `src/quantleet/backtest/engine.py`.
3. Remove or isolate the old `validate_strategy_like_config` engine dependency.
4. Update existing unit tests and direct test helpers to pass strategy classes.
5. Update `ParameterStudy` and its unit/integration tests.
6. Convert constructor-argument test strategies that flow through
   `BacktestEngine` to `StrategyConfig`-backed classes.
7. Update integration, perf, and smoke test call sites.
8. Update current public docs, docs-site pages, and maintained notebooks.
9. Run focused `rg` transition checks for current public surfaces.
10. Run targeted tests.
11. Run `uv run poe repo-check`.
12. Run `uv run poe verify-runtime`.
13. Run `uv run poe verify`.
14. Run `git diff --check`.
15. Fill the evaluator review section with findings and fresh command output.

## Success Conditions

- New public direct backtest API is the only current direct strategy input
  shape.
- Config input is typed and explicit; dict input is rejected.
- Strategy construction is engine-owned and fresh for each direct run.
- `ParameterStudy` shares the same engine path.
- Reports continue to expose copied `strategy_config` and never
  `strategy_parameters`.
- Current public docs and examples no longer teach direct strategy instances.
- Full runtime-sensitive verification passes.

## Open Questions

- None for product intent.
- Implementation detail to resolve during coding: whether preserving
  `ParameterStudy`'s `strategy_construction` failure stage needs a narrow
  backtest construction error type, or whether existing exception types are
  sufficient without adding public API surface.

## Generator Work Log

- Planned slice order:
  1. contract tests
  2. engine implementation
  3. research composition update
  4. test helper and fixture migration
  5. docs and example cleanup
  6. verification and evaluator review
- Notes:
  - Codebase survey completed before writing this plan.
  - The implementation should prefer small local edits over broad abstractions.
  - Implemented `BacktestEngine.run(strategy=StrategyClass, config=...)`.
  - Updated `ParameterStudy` to call the same direct engine path.
  - Migrated tests, smoke examples, docs-site examples, maintained notebooks,
    and current product docs to the Stage 3.5 API.
  - Kept the construction failure signal internal to `backtest.engine`.
- Blockers or scope changes:
  - No human scope change was required.

## Evaluator Review

- Findings:
  - Subagent correctness/testing review found no blocker or important issues.
    Minor R2 coverage gap was fixed by adding a report snapshot independence
    assertion.
  - Subagent architecture/API review found one important issue: canonical test
    fixture data was stored on shared strategy classes. Fixed by creating
    run-local strategy subclasses for fixture-bound canonical strategies.
  - Subagent docs/spec review found no blockers and three important cleanup
    issues. Fixed the direct-instance negative example, current reporting test
    scenario wording, and Stage 1 open-question residue.
  - The construction failure signal is kept internal as
    `_BacktestStrategyConstructionError` and is not exported from
    `quantleet.backtest`.
- Verification evidence:
  - `uv run pytest -q tests/unit/backtest tests/unit/research tests/integration/research tests/integration/strategy tests/smoke/local`
    passed: `372 passed`.
  - `uv run pytest -q tests/structure tests/perf/test_backtest_plotting_scale.py tests/integration/backtest/test_plotting.py`
    passed: `149 passed`.
  - `uv run ruff check .` passed: `All checks passed!`.
  - `uv run mypy src` passed: `Success: no issues found in 59 source files`.
  - `uv run pytest -q` passed: `700 passed, 4 skipped`.
  - `uv run poe verify-runtime` passed after review fixes, including `ruff`,
    `mypy`, full pytest, coverage policy, `uv build`, `repo-check`, notebook
    validation, and `tests/perf --run-perf`.
  - `uv run poe repo-check` passed: `repository checks passed`.
  - `git diff --check` passed.
  - Focused transition check for README/docs-site/references/notebooks/smoke
    old direct-instance examples returned no matches.
  - Focused product-spec transition check returned only intentional negative
    examples in `direct-backtest-class-config-api*.md`.
- Final disposition: complete.
