# Reporting Config Source Of Truth Test Scenarios

## Status

- Status: `implemented`
- Class: `product-test-spec`
- Scope: current implemented Stage 3 test scenarios for reporting provenance
  cleanup after the `ParameterStudy` strategy API migration and before
  walk-forward analysis resumes

Related documents:

- [reporting-config-source-of-truth.md](reporting-config-source-of-truth.md)
- [strategy-configuration-contract.md](strategy-configuration-contract.md)
- [strategy-configuration-contract-test-scenarios.md](strategy-configuration-contract-test-scenarios.md)
- [parameter-exploration.md](parameter-exploration.md)
- [parameter-exploration-test-scenarios.md](parameter-exploration-test-scenarios.md)
- [wfa-prerequisite-roadmap.md](wfa-prerequisite-roadmap.md)
- [research-ergonomics.md](research-ergonomics.md)
- [backtest-mvp.md](backtest-mvp.md)
- [public-beta-documentation.md](public-beta-documentation.md)
- [../design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)
- [../RELIABILITY.md](../RELIABILITY.md)
- [../SECURITY.md](../SECURITY.md)

This document turns the Stage 3 product contract in
[reporting-config-source-of-truth.md](reporting-config-source-of-truth.md) into
a test scenario contract. It does not implement tests and does not extend
product scope. Tests derived from this document should prove externally
observable reporting provenance, not private helper names or the internal
mechanism used to capture config snapshots.

## Test Target Intent And Core Contract

Stage 3 exists because the same backtest run can currently appear to have two
configuration truths:

- the framework-owned `StrategyConfig` snapshot used by strategy construction,
  parameter studies, and selected study rows
- strategy-authored metadata returned by `Strategy.parameters()` and exposed as
  `report.run.strategy_parameters`

Tests must prove that Stage 3 removes that ambiguity.

The core test contract is:

- report-facing execution config comes only from the materialized
  `StrategyConfig` snapshot attached to the strategy instance
- reports expose the full snapshot as `report.run.strategy_config`
- reports do not expose `report.run.strategy_parameters`
- report generation does not call `Strategy.parameters()` and does not use it
  as a fallback
- `strategy_config` is a normalized plain `dict[str, JSON scalar]`
- config-less strategies report `{}`
- `Strategy.display_name` and run `label` remain human-readable identity
  metadata, not execution config
- successful `ParameterStudy` rows and their backtest reports expose matching
  full `strategy_config` snapshots
- managed current docs, examples, tests, fixtures, notebooks, and report
  snapshots teach the new contract only
- historical or audit records may keep older terms only when they are not
  current product authority

Tests must not prove profitability, WFA behavior, trading recommendations, or a
future direct `BacktestEngine.run(strategy=StrategyClass, config=...)` API.

## Testing Philosophy

Tests are long-lived product assets. A refactor of snapshot plumbing,
report-manifest construction, dataclass choices, or helper names should not
require changing tests unless the Stage 3 product contract changes.

External testing guidance used for this spec:

- Google Testing Blog recommends testing behaviors rather than methods because
  user-visible behavior can span methods and a method can expose many
  behaviors:
  [Testing on the Toilet: Test Behaviors, Not Methods](https://testing.googleblog.com/2014/04/testing-on-toilet-test-behaviors-not.html).
- The Practical Test Pyramid recommends a balanced automated suite with many
  cheap lower-level tests, fewer integration tests, and only the system-level
  tests that justify their cost:
  [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html).
- Microsoft unit testing guidance emphasizes readable, deterministic tests that
  avoid private implementation details:
  [Unit testing best practices](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices).
- pytest guidance supports tests outside application code and explicit,
  modular fixtures for reusable setup:
  [pytest Good Integration Practices](https://pytest.org/en/7.4.x/goodpractices.html),
  [pytest fixtures](https://docs.pytest.org/en/7.1.x/explanation/fixtures.html).

Operational rules:

1. Test observable report, result, study-row, docs, and fixture contracts.
2. Do not assert private helper names, internal generic inspection mechanics,
   or the exact internal object that builds the report manifest.
3. Use unit tests for local normalization, shape, and metadata-boundary
   contracts that can be observed without a full backtest.
4. Use integration tests where the risk is cross-module drift between
   `strategy`, `backtest`, and `research`.
5. Use regression and structure checks for migration-sensitive stale-surface
   failures such as `strategy_parameters` returning through current fixtures or
   docs.
6. Keep tests small, named by behavior, and explicit about input config and
   expected snapshot.
7. Treat failures from invalid direct backtest strategy/config inputs as visible
   contract failures, not as prompts to invent fallback metadata behavior.

## Test Scope And Non-Scope

In scope:

- direct backtest report config snapshots for strategy classes plus explicit
  config objects
- direct backtest report config snapshots for config-less strategies
- removal of `strategy_parameters` from report-facing current contracts
- negative guardrails proving `Strategy.parameters()` cannot affect reports
- snapshot copying at run start rather than after runtime mutation
- normalized plain mapping shape for `strategy_config`
- distinction between `strategy_config`, `candidate_parameters`,
  `display_name`, and run `label`
- `ParameterStudy` row/report alignment for successful rows
- visible failure for invalid direct strategy/config input at the reporting
  boundary
- current managed docs, examples, notebooks, fixtures, and canonical report
  snapshots using the new contract
- historical/audit exception checks where current product routing is relevant

Out of scope:

- WFA implementation, WFA result models, or WFA fold-level assertions
- paper trading, live trading, execution, or broker integration tests
- profitability or optimization-quality assertions
- a new arbitrary `metadata={...}` report feature
- new strategy performance metrics
- descriptor/range DSL tests for strategy parameters
- WFA-specific `BacktestEngine.run(strategy=StrategyClass, config=...)` tests
  for a later WFA phase
- tests that require changelog or release-note rewriting
- tests that require public migration notes for pre-release
  `Strategy.parameters()` examples

## Proposed Test Placement

| Layer | Proposed location | Purpose |
| --- | --- | --- |
| Unit | `tests/unit/backtest/test_report_strategy_config_contract.py` | Report run-manifest shape, plain mapping snapshots, absence of `strategy_parameters`, and metadata-boundary behavior that can be observed without running a full strategy workflow. |
| Unit | `tests/unit/backtest/test_report_strategy_config_snapshot.py` | Snapshot timing: defaults plus overrides are copied at run start and do not change because strategy runtime state mutates later. |
| Unit | `tests/unit/backtest/test_direct_class_config_api.py` | Invalid direct strategy/config inputs fail visibly instead of silently reporting `{}`. |
| Integration | `tests/integration/backtest/test_backtest_report_strategy_config.py` | Real `BacktestEngine.run(...)` with configured and config-less strategy classes produces the expected report contract. |
| Integration | `tests/integration/research/test_parameter_study_report_strategy_config.py` | Real `ParameterStudy` successful rows and retained backtest reports expose identical full `strategy_config` snapshots while preserving partial `candidate_parameters`. |
| Regression | `tests/regression/backtest/test_strategy_parameters_removed_from_reports.py` | A strategy that still defines `parameters()` cannot influence reports, and stale `strategy_parameters` access is absent from current report objects/records. |
| Structure | `tests/structure/docs/test_reporting_config_source_of_truth_docs.py` | Current docs, examples, notebooks, and canonical snapshots do not teach or serialize the old current contract. |
| Structure | `tests/structure/architecture/test_reporting_config_boundaries.py` | `strategy` owns config semantics, `backtest` owns report generation, and `research` composes both without moving source-of-truth ownership. |
| Notebook validation | existing notebook validation lane | Tracked notebooks that teach tunable strategy settings execute against the config-backed pattern. |

No browser-style E2E tests are required. This is a Python library/reporting
contract with no UI. End-to-end confidence should come from a small documented
workflow or notebook validation path once managed examples are migrated, but the
P0 completion gate belongs in focused integration and regression tests.

## Unit Test Scenarios

### U1: Report Run Manifest Uses `strategy_config`

Purpose: prove the report-facing field name and shape.

Scenarios:

| Case | Input | Expected behavior |
| --- | --- | --- |
| configured strategy | `Strategy[SmaConfig]` with `fast=10`, default `slow=20` | `report.run.strategy_config == {"fast": 10, "slow": 20}`. |
| defaulted config fields | strategy constructed with only one override | default fields are present in `strategy_config`. |
| config-less strategy | strategy with no explicit config fields | `report.run.strategy_config == {}`. |
| plain mapping shape | configured strategy report | `strategy_config` is a plain `dict`, not a `StrategyConfig` object. |
| old field removed | any current report | `strategy_parameters` is absent from the report run contract. |

Required assertions:

- expected snapshots are written directly in tests
- tests do not assert private report-builder helper names
- absence checks cover object access and any current record/export shape that
  exposes report run metadata

### U2: `Strategy.parameters()` Cannot Affect Reports

Purpose: protect against the old self-reporting source returning through a
fallback path.

Scenarios:

| Case | Input | Expected behavior |
| --- | --- | --- |
| stale method returns conflicting data | strategy config is `{"fast": 5}`, `parameters()` returns `{"fast": 999}` | report records `{"fast": 5}`. |
| stale method raises | `parameters()` raises an exception | report generation succeeds if the strategy config contract is otherwise valid. |
| stale method has side effects | `parameters()` increments a counter | counter remains unchanged after report generation. |
| config-less stale method | config-less strategy defines `parameters()` returning data | report records `{}`. |

Required assertions:

- report generation must not call `parameters()`
- tests verify observable output and side effects, not call stacks or private
  implementation details
- the method remaining on a user strategy class is not itself a failure; only
  framework use of it is a failure

### U3: Snapshot Is Copied At Run Start

Purpose: prove the report represents input provenance, not runtime state.

Scenarios:

| Case | Input | Expected behavior |
| --- | --- | --- |
| runtime attribute mutation | strategy mutates `self.fast` or another runtime attribute | report `strategy_config` remains the start snapshot. |
| attempted config mutation | strategy attempts to mutate `self.config` where the config contract rejects mutation | the existing config-contract error behavior applies; report contract does not reinterpret runtime state. |
| display name derived from config | `display_name` returns `"SMA 5/20"` | report may expose display name, but `strategy_config` remains the mapping. |
| run label provided | `label="candidate-a"` | label remains identity metadata and is not nested into `strategy_config`. |

Required assertions:

- `strategy_config` includes only public `StrategyConfig` fields
- `display_name` and `label` never become config keys unless they are actual
  public `StrategyConfig` fields
- the test should use a minimal deterministic run or contract-level report path
  rather than inspecting private runtime storage

### U4: Invalid Strategy-Like Config Metadata Fails Visibly

Purpose: prevent invalid custom objects from silently reporting `{}`.

Scenarios:

| Case | Input | Expected behavior |
| --- | --- | --- |
| missing config metadata | custom strategy-like object accepted by runtime shape but lacking valid config | explicit validation error before a misleading report is produced. |
| non-`StrategyConfig` config object | object exposes `config` as a plain dict or arbitrary object | explicit validation error. |
| invalid snapshot values | config snapshot contains a non-JSON-safe object | failure is attributed to the `StrategyConfig` contract, not papered over by report fallback. |

Required assertions:

- failure is visible and contract-level
- tests avoid requiring an exact full error string before the implementation
  plan chooses error wording
- config-less official `Strategy` subclasses still report `{}`, so invalid
  custom strategy-like objects are tested separately from valid config-less
  strategies

## Integration Test Scenarios

### I1: Configured Direct Backtest Report

Purpose: prove the public direct backtest workflow records the materialized
config snapshot.

Scenario:

1. Define a tiny `StrategyConfig` with public JSON-scalar fields and defaults.
2. Define a `Strategy[Config]` that uses `self.config` during a deterministic
   backtest.
3. Run `BacktestEngine.run(bars=..., strategy=ConfiguredStrategy, config=config)`.
4. Inspect `result.report.run.strategy_config`.

Expected behavior:

- the report contains the full snapshot, including defaulted fields
- the report has no `strategy_parameters`
- the strategy outcome is incidental; the assertion targets report provenance

### I2: Config-Less Direct Backtest Report

Purpose: preserve lightweight quickstart strategies.

Scenario:

1. Define a minimal config-less strategy.
2. Run a deterministic direct backtest.
3. Inspect the report.

Expected behavior:

- `result.report.run.strategy_config == {}`
- there is no `strategy_parameters`
- the test does not require constructor-argument inference

### I3: ParameterStudy Row And Report Alignment

Purpose: prove cross-module source-of-truth alignment.

Scenario:

1. Define a configured strategy with defaults.
2. Run a small `ParameterStudy` grid.
3. Select a successful row.
4. Compare `row.strategy_config`,
   `row.backtest.report.run.strategy_config`, and
   `row.candidate_parameters`.

Expected behavior:

- `row.strategy_config` is the full materialized snapshot
- `row.backtest.report.run.strategy_config == row.strategy_config`
- `row.candidate_parameters` remains only the partial override audit trail
- no assertion treats the report as the selection source of truth

### I4: ParameterStudy Config-Less Default Candidate

Purpose: prove the empty-config path composes with study/report inspection.

Scenario:

1. Run the canonical config-aware study path with an empty parameter set for a
   valid config-less strategy, if that path remains supported by Stage 2.
2. Inspect the successful row and retained backtest report.

Expected behavior:

- row-level `strategy_config == {}`
- report-level `strategy_config == {}`
- no stale `strategy_parameters` field appears

If the implemented Stage 2 contract does not expose a config-less study path,
this scenario should be omitted rather than used to expand Stage 3.

### I5: Managed Example With Tunable Settings

Purpose: prove current public examples teach config-backed settings.

Scenario:

1. Execute or validate a managed example/notebook that teaches tunable SMA or
   RSI settings.
2. Inspect the produced report or documented expected output where practical.

Expected behavior:

- tunable settings are modeled as `StrategyConfig` fields
- the report records those settings as `strategy_config`
- the example does not teach `Strategy.parameters()` or constructor arguments
  as the canonical reportable settings path

## Regression And Contract Test Scenarios

### R1: Old Report Field Does Not Return

Purpose: prevent compatibility drift during implementation.

Scenarios:

- current report objects do not expose `run.strategy_parameters`
- current report record/dict/export shapes do not include
  `strategy_parameters`
- canonical report snapshots and fixtures use `strategy_config`
- current docs and examples do not present `strategy_parameters` as current API

### R2: Old Strategy Hook Does Not Return

Purpose: protect the canonical strategy surface.

Scenarios:

- framework report generation does not call `parameters()`
- base `Strategy` no longer exposes `parameters()` as a canonical method
- current docs and examples do not instruct strategy authors to implement
  `parameters()` for reporting
- user strategies that define `parameters()` are allowed as ordinary Python
  methods, but the framework ignores them for report config

### R3: Historical/Audit Exception Remains Narrow

Purpose: preserve audit history without confusing current users.

Scenarios:

- historical plans or notes may contain older terminology when clearly
  describing past state
- current product-routing docs must point to the new product spec and test spec
- docs under current public/user-facing surfaces do not rely on the historical
  exception

### R4: JSON-Scalar Report Contract Holds

Purpose: protect portable report output.

Scenarios:

- accepted strategy config snapshots contain only JSON scalar values
- snapshots are plain-data comparable
- non-scalar config needs are not silently serialized by reporting tests
- future domain-object serialization tests are deferred to a separate product
  spec

## Normal Flows

- configured direct backtest records full `strategy_config`
- config-less direct backtest records `{}`
- configured `ParameterStudy` row and retained report agree on full config
- display name and label remain available as readable identity metadata
- managed tunable examples use `StrategyConfig` and `self.config`

## Failure Flows

- stale `parameters()` returns conflicting data and is ignored
- stale `parameters()` raises and report generation does not call it
- invalid custom strategy-like config metadata fails visibly
- stale report fixtures containing `strategy_parameters` fail regression checks
- current docs teaching old report fields fail docs/structure checks
- non-JSON-safe config snapshot values fail under the strategy config contract

## Edge Cases And Boundary Conditions

- empty config maps to exactly `{}`
- one-field config maps to a one-key dict
- defaulted fields appear even when not overridden
- falsey JSON scalar values such as `0`, `0.0`, `False`, `""`, and explicit
  allowed `None` are preserved rather than dropped
- config field names that resemble report fields remain nested inside
  `strategy_config`
- `label` and `display_name` do not enter `strategy_config`
- runtime attributes and mutable runtime state do not enter `strategy_config`
- historical documents may contain old terms only when not routed as current
  authority

## Test Data And Fixture Strategy

Use small, deterministic fixtures whose expected snapshots are readable in the
test body.

Recommended fixtures:

| Fixture | Shape | Purpose |
| --- | --- | --- |
| `SmaConfig` | `fast: int = 5`, `slow: int = 20`, `enabled: bool = True` | Normal configured strategy snapshots. |
| `ConfiguredSmaStrategy` | `Strategy[SmaConfig]` using `self.config.fast` and `self.config.slow` | Direct report and study alignment scenarios. |
| `ConfigLessStrategy` | Minimal `Strategy` with no explicit config fields | `{}` report behavior. |
| `ConflictingParametersStrategy` | Valid config plus `parameters()` returning conflicting data | Negative guardrail for old self-reporting. |
| `RaisingParametersStrategy` | Valid config plus `parameters()` raising | Prove report generation does not call stale hook. |
| `RuntimeMutatingStrategy` | Valid config plus runtime attribute mutation | Snapshot timing and metadata-boundary scenarios. |
| `InvalidStrategyLike` | Custom object with missing or invalid config metadata | Visible validation failure. |
| `small_bars` | 6 to 12 deterministic bars | Cheap direct and study integration runs. |
| `report_snapshot_fixture` | Current canonical serialized report shape | Regression check that old field names are absent. |

Fixture rules:

- Keep strategy/config classes local to test modules unless shared reuse
  materially improves clarity.
- Put expected `strategy_config` mappings directly in assertions.
- Do not hide expected snapshots behind helper functions that reimplement
  production normalization.
- Use market data only when crossing the real `BacktestEngine` or
  `ParameterStudy` boundary.
- Keep notebook/example validation in the existing repository validation lane.

## Mock, Stub, And Fake Use Criteria

Prefer real Quantleet objects for product-contract tests:

- real `StrategyConfig` subclasses
- real `Strategy` subclasses
- real `BacktestEngine.run(...)` integration paths
- real `ParameterStudy` workflows for row/report alignment
- real report objects and current record/export shapes

Allowed fakes:

- a minimal report-manifest fake for unit tests that isolate field shape before
  a full backtest is needed
- a contract-shaped invalid strategy-like object for negative validation tests
- a small fake notebook/example output only if the docs validation harness
  already uses such fixtures

Avoid:

- patching private report-builder helpers
- mocking `StrategyConfig` itself
- replacing `BacktestEngine` in tests whose purpose is real report integration
- interaction assertions when a state/output assertion proves the contract
- exact full error-message assertions before implementation wording is chosen
- filesystem-wide text searches that cannot distinguish current authority from
  historical/audit context

## What Tests Must Verify

Tests must verify:

- configured direct reports expose `report.run.strategy_config`
- config-less direct reports expose `strategy_config == {}`
- `strategy_config` is a plain normalized dict snapshot
- default config fields appear in report snapshots
- falsey JSON scalar values survive normalization
- `strategy_parameters` is absent from current report contracts
- `Strategy.parameters()` does not affect report config and is not called by
  reporting
- user-defined `parameters()` methods are ignored rather than forbidden by
  Stage 3
- `display_name` and `label` remain separate from execution config
- successful `ParameterStudy` rows and retained reports agree on full
  `strategy_config`
- `candidate_parameters` remains distinct from full `strategy_config`
- invalid custom strategy-like config metadata fails visibly
- managed current docs, examples, notebooks, tests, fixtures, and report
  snapshots use the new contract
- historical/audit exceptions do not override current product authority

## What Tests Must Not Verify

Tests must not verify:

- private helper names or call graphs
- a specific internal storage type beyond the public plain-dict snapshot
- exact complete error strings unless the implementation plan promotes them to
  public messages
- strategy profitability or optimizer quality
- WFA fold behavior
- paper or live trading behavior
- a future direct class-plus-config backtest API
- arbitrary run metadata bags
- automatic inference of constructor arguments or public runtime attributes
- serialization of future domain objects such as instruments, venues, bar
  types, or decimals

## Test-Level Priorities

| Priority | Level | Required before Stage 3 implementation is complete | Reason |
| --- | --- | --- | --- |
| P0 | Integration | Yes | Proves real direct backtest reports and `ParameterStudy` reports agree with the product contract. |
| P0 | Regression | Yes | Prevents old `strategy_parameters` and `Strategy.parameters()` reporting paths from surviving. |
| P0 | Unit | Yes | Localizes snapshot shape, empty-config, stale-hook, and invalid-strategy-like failures. |
| P1 | Structure/docs | Yes for managed current surfaces touched by Stage 3 | Prevents public/current docs and fixtures from teaching stale contracts. |
| P1 | Notebook/example validation | Yes when notebooks/examples are migrated in the implementation slice | Confirms managed educational workflows still run. |
| P2 | Broader smoke/E2E | Optional | Useful for release confidence, but not the primary guard for this library contract. |

## Success Conditions

This test spec is successful when later implementation plans can derive tests
that prove:

- report config provenance comes from `StrategyConfig`
- `strategy_parameters` is absent from current report-facing contracts
- `Strategy.parameters()` no longer affects report output
- config-less strategies remain valid and report `{}`
- direct backtest reports expose full config snapshots
- `ParameterStudy` rows and retained reports expose the same full snapshot
- partial `candidate_parameters` and full `strategy_config` remain distinct
- human-readable identity metadata stays separate from execution config
- invalid custom strategy-like objects do not silently produce misleading
  `{}` reports
- managed current docs, examples, notebooks, tests, fixtures, and snapshots are
  aligned with the new contract
- WFA planning can depend on report config snapshots without reopening the
  source-of-truth question

## Open Questions

- None for the Stage 3 reporting source-of-truth test contract.
