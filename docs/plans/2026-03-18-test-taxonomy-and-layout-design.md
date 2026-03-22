# Test Taxonomy And Layout Design

## Goal

Define a test structure for `quantcraft` that remains legible as the repository grows, makes it obvious what each test is validating, and separates deterministic local verification from network-backed validation.

This design is intentionally aligned with two constraints:

- the repository should have predictable structure, not organically flat sprawl
- test code is a long-term asset and must be organized with the same care as production code

## Current Problem

The current repository still uses a flat `tests/` layout:

- `tests/test_exchange.py`
- `tests/test_import.py`
- `tests/test_repo_docs.py`
- `tests/test_docs_structure.py`
- `tests/test_plan_indexes.py`
- `tests/test_local_commands.py`
- `tests/test_repo_checks.py`
- `tests/test_architecture_rules.py`
- `tests/test_financial_policies.py`
- `tests/test_quality_ops.py`

That shape is acceptable for initial bootstrap work, but it will degrade quickly once `quantcraft` grows into:

- market data
- backtesting
- paper trading
- execution
- risk
- portfolio
- research
- ML tooling

In a larger repository, a flat test tree creates three problems:

1. it becomes hard to tell what a file is testing
2. it becomes hard to decide which tests belong in default verification vs optional verification
3. test fixtures and execution policy gradually become implicit and tangled

## Design Principles

This design follows these principles:

1. test location should communicate test intent
2. default local verification should stay deterministic and fast
3. network-backed validation should not run in the default test lane
4. `unit` and `integration` tests should mirror the source-code structure
5. repository-structure tests should stay separate from source-behavior tests
6. naming should make the tested subject and behavior visible
7. fixture scope should match the directory boundaries of the tests that use it

## Proposed Top-Level Test Taxonomy

The top-level test tree should be organized by test type, not by domain.

Recommended structure:

```text
tests/
  unit/
  integration/
  structure/
  smoke/
  conftest.py
```

### Why Type-First At The Top Level

This gives immediate visibility into:

- speed expectations
- runtime assumptions
- whether the test is about code behavior or repository contracts
- whether the test should run by default

This is a more useful first split than domain-first for a large repository because the first operational question is usually:

- "what kind of verification is this?"

not:

- "which domain does this belong to?"

## Internal Layout Rules

### `unit/`

`unit` tests validate isolated logic and should mirror the source-code structure as closely as practical.

Examples:

```text
tests/unit/market_data/...
tests/unit/backtest/...
tests/unit/common/...
```

Rules:

- no network access
- no external process dependency unless strictly local and deterministic
- narrow fixtures
- focus on pure behavior and edge conditions

### `integration/`

`integration` tests validate behavior across multiple modules, interfaces, or repository command surfaces.

These should also mirror the source-code structure when they are testing source-facing domains.

Examples:

```text
tests/integration/market_data/...
tests/integration/backtest/...
tests/integration/commands/...
```

Rules:

- can cross module boundaries
- should still be deterministic by default
- should not rely on live external services in the default lane

### `structure/`

`structure` tests validate repository rules rather than production-code behavior.

They should not be forced into a source-mirror shape because their subject is the repository itself.

Recommended structure:

```text
tests/structure/architecture/...
tests/structure/docs/...
tests/structure/repo/...
```

Examples of what belongs here:

- architecture boundary checks
- required document checks
- plan index checks
- repository command contracts
- quality scaffolding checks

### `smoke/`

`smoke` tests validate minimal end-to-end sanity.

They should be separated into:

```text
tests/smoke/local/...
tests/smoke/live/...
```

Rules:

- `smoke/local` may be part of broader validation flows when deterministic
- `smoke/live` is always explicit and never part of the default test lane

`live` tests are the place for:

- network-backed exchange calls
- remote API availability checks
- minimal external contract checks

## Default Execution Policy

The test layout must correspond to a clear execution policy.

### Default Test Lane

The default `pytest` lane should include:

- `unit`
- `integration`
- `structure`

These tests should be:

- deterministic
- local-first
- reasonably fast

### Explicit-Only Lanes

These must not be part of the default test lane:

- `smoke/live`

This is necessary because `quantcraft` is a financial and quant repository where network variance, exchange availability, rate limits, and external state can make verification nondeterministic.

### Optional Local Smoke

`smoke/local` can remain separate even if deterministic. The point is to preserve semantic clarity: a smoke test is still different from a unit or integration test even when it is local.

## Markers

The taxonomy should be reflected in `pytest` markers as well.

Recommended markers:

- `unit`
- `integration`
- `structure`
- `smoke`
- `live`
- `slow`

Markers should not replace directory structure, but they should reinforce execution policy.

This allows useful execution lanes such as:

- fast default checks
- structure-only checks
- no-live verification
- explicit live validation

## Naming Rules

File names should clearly show both subject and behavior.

Preferred pattern:

```text
test_<subject>_<behavior>.py
```

Good examples:

- `test_exchange_fetch_ohlcv.py`
- `test_domain_boundaries.py`
- `test_required_docs.py`
- `test_public_imports.py`
- `test_exchange_live_smoke.py`

Avoid broad or opaque names such as:

- `test_exchange.py`
- `test_repo.py`
- `test_misc.py`

## Fixture Boundaries

Fixture scope should follow directory boundaries.

Recommended approach:

- `tests/conftest.py`
  - only truly global fixtures
- `tests/unit/.../conftest.py`
  - unit-only fixtures for that domain
- `tests/integration/.../conftest.py`
  - integration-only fixtures
- `tests/smoke/.../conftest.py`
  - smoke-specific fixtures

This prevents `conftest.py` from turning into a hidden global dependency bucket.

## Mapping The Current Tests

The current flat tests should be migrated like this:

- `tests/test_exchange.py`
  - -> `tests/unit/market_data/test_exchange_fetch_ohlcv.py`
- `tests/test_import.py`
  - -> `tests/smoke/local/test_public_imports.py`
- `tests/test_repo_docs.py`
  - -> `tests/structure/repo/test_repository_entrypoint_docs.py`
- `tests/test_docs_structure.py`
  - -> `tests/structure/docs/test_system_of_record_docs.py`
- `tests/test_plan_indexes.py`
  - -> `tests/structure/docs/test_plan_indexes.py`
- `tests/test_local_commands.py`
  - -> `tests/integration/commands/test_local_command_entrypoints.py`
- `tests/test_repo_checks.py`
  - -> `tests/structure/repo/test_repo_check_contracts.py`
- `tests/test_architecture_rules.py`
  - -> `tests/structure/architecture/test_domain_boundaries.py`
- `tests/test_financial_policies.py`
  - -> `tests/structure/docs/test_financial_policy_docs.py`
- `tests/test_quality_ops.py`
  - -> `tests/structure/repo/test_quality_scaffolding.py`

## Enforcement Rules

This taxonomy should not remain a documentation-only convention.

The repository should enforce:

1. no new flat test files directly under `tests/`
2. `unit` and `integration` tests must follow source-mirroring rules
3. `structure` and `smoke` tests must use the purpose-specific tree
4. live tests must not run in the default lane

These rules should eventually be checked by repository structure validation.

## Non-Goals

This design does not try to:

- define every future fixture in advance
- add performance or benchmark taxonomy yet
- finalize every future domain subtree before those domains exist
- merge smoke and integration into one category

The focus is only on establishing a durable and comprehensible baseline taxonomy.

## Success Criteria

This design is successful when:

- the top-level test tree immediately shows test intent
- `unit` and `integration` mirror source structure
- `structure` clearly owns repository-rule checks
- `smoke/live` is separated from default test execution
- file names make test purpose obvious
- fixture scope follows test boundaries
- future AI-added tests have an explicit place to go
