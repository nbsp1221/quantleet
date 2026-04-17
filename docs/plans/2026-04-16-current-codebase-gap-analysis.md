# Current Codebase Gap Analysis

- Date: 2026-04-16
- Status: `approved-analysis`
- Scope: current `src/quantcraft` package topology versus the approved
  capability-first target architecture
- Related active plan:
  - [2026-04-16-codebase-gap-analysis-and-migration-blueprint.md](2026-04-16-codebase-gap-analysis-and-migration-blueprint.md)

## Purpose

This document records the concrete gap between:

- the approved capability-first target defined in
  [ARCHITECTURE.md](../../ARCHITECTURE.md),
  [quantcraft-architecture.md](../design-docs/quantcraft-architecture.md), and
  [package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)
- the current shipped codebase under `src/quantcraft`

It is not a detailed implementation plan for one refactor PR.
It is an analysis baseline plus migration-sequencing reference that later
implementation slices must cite and refine.

## Current Topology Snapshot

The current installable package contains three real top-level contexts plus a
few root-level support or compatibility modules:

```text
src/quantcraft/
  __init__.py
  exchange.py
  _repo_tools.py
  _notebook_tools.py
  data/
    domain/
    application/
    adapters/
  research/
    domain/
    application/
    adapters/
    indicators/
      pure/
      runtime/
  trading/
    domain/
    application/
    adapters/
```

Notably absent today:

- `backtest/`
- `execution/`
- `integrations/`
- `cli/`
- `_shared/`

## Target Topology Snapshot

The approved long-lived package topology is capability-first:

```text
src/quantcraft/
  data/
  trading/
  research/
  backtest/
  execution/
  integrations/
  _shared/
```

Important target rules:

- `backtest` is a peer runtime context, not a `research` sub-owner
- `integrations` owns external system translation
- internal package depth should stay shallow by default
- repo-wide `domain / application / adapters` is not the long-lived organizing
  principle

Separately, the packaged CLI surface is expected to live under:

- `src/quantcraft/cli`

but it is a distributed product surface, not a peer bounded context.

## Findings

### 1. Backtest runtime still lives under `research`

This is the largest semantic mismatch.

Current code:

- [src/quantcraft/research/application/backtest.py](../../src/quantcraft/research/application/backtest.py)
  owns `_run_backtest`, `BacktestResult`, `BacktestSummary`, and exposure/report
  types
- [src/quantcraft/research/application/engine.py](../../src/quantcraft/research/application/engine.py)
  wires `BacktestEngine` directly to that module
- [src/quantcraft/research/adapters/execution_model.py](../../src/quantcraft/research/adapters/execution_model.py)
  owns the backtest execution model
- [src/quantcraft/research/__init__.py](../../src/quantcraft/research/__init__.py)
  exports `BacktestEngine` from the research package root

Why this matters:

- target ownership says `research` should own strategy ergonomics, indicators,
  analytics, and alpha-search helpers
- target ownership says `backtest` should own historical runtime orchestration,
  path construction, and reporting

Practical consequence:

- migration cannot be only a directory move
- it must preserve the current public `quantcraft.research` surface while
  introducing `quantcraft.backtest`

### 2. External integrations are embedded in `data` and root-level shims

Current code:

- [src/quantcraft/data/adapters/exchange_backend.py](../../src/quantcraft/data/adapters/exchange_backend.py)
  imports `ccxt` directly and defines exchange-facing behavior
- [src/quantcraft/exchange.py](../../src/quantcraft/exchange.py) re-exports
  that implementation as a root-level compatibility module
- [src/quantcraft/__init__.py](../../src/quantcraft/__init__.py) dynamically
  exposes `Exchange`, `MarketType`, and `TimeBar`

Why this matters:

- target ownership says venue and vendor protocol translation belongs in
  `integrations`
- `data` should own normalized data contracts and data workflows, not provider
  protocol code
- current root-level `exchange.py` is a transitional public surface, not a
  target topology fit

Practical consequence:

- introducing `integrations` is not optional if the target topology is to become
  real
- the root `quantcraft.Exchange` compatibility surface must survive through an
  intermediate stage

### 3. Context-internal layer-first skeletons still dominate the tree

Current code still carries `domain / application / adapters` under `data`,
`research`, and `trading`, including empty package placeholders such as:

- [src/quantcraft/data/application/__init__.py](../../src/quantcraft/data/application/__init__.py)
- [src/quantcraft/trading/application/__init__.py](../../src/quantcraft/trading/application/__init__.py)
- [src/quantcraft/trading/adapters/__init__.py](../../src/quantcraft/trading/adapters/__init__.py)

Why this matters:

- the approved architecture allows local layering when it helps
- it does not want symmetric layer-first skeletons to stay the default package
  shape

Practical consequence:

- not every `domain / application / adapters` subtree should be removed at
  once
- they should be evaluated context by context and flattened only where the
  target topology actually becomes clearer

### 4. Current public/test surface hard-codes the transitional layout

The current shipped import surface is strongly frozen.

Pinned today:

- root exports: `Exchange`, `MarketType`, `TimeBar`
  - [src/quantcraft/__init__.py](../../src/quantcraft/__init__.py)
  - [tests/smoke/local/test_public_imports.py](../../tests/smoke/local/test_public_imports.py)
  - [tests/integration/commands/test_built_artifact_imports.py](../../tests/integration/commands/test_built_artifact_imports.py)
- `quantcraft.data` exports
  - [src/quantcraft/data/__init__.py](../../src/quantcraft/data/__init__.py)
- `quantcraft.research` exports `BacktestEngine`, `Strategy`, `ta`, `qc`
  - [src/quantcraft/research/__init__.py](../../src/quantcraft/research/__init__.py)
  - [tests/structure/architecture/test_backtest_mvp_slice1.py](../../tests/structure/architecture/test_backtest_mvp_slice1.py)
  - [tests/smoke/local/test_public_imports.py](../../tests/smoke/local/test_public_imports.py)

Direct imports into transitional internals are also common:

- `quantcraft.research.application.backtest`
- `quantcraft.research.application.strategy`
- `quantcraft.research.adapters.execution_model`
- `quantcraft.trading.domain.*`

Practical consequence:

- migration must introduce compatibility re-exports before moving callers
- doc updates must trail compatibility surfaces, not lead them

### 5. Mechanical checks still assume the old layout

Current check coverage is transitional:

- [tests/structure/architecture/test_backtest_mvp_slice1.py](../../tests/structure/architecture/test_backtest_mvp_slice1.py)
  explicitly requires `domain/application/adapters` skeletons under current
  contexts
- [src/quantcraft/_repo_tools.py](../../src/quantcraft/_repo_tools.py) and
  [scripts/check_architecture.py](../../scripts/check_architecture.py) do not
  yet model `backtest` or `integrations` as first-class domains
- [docs/RELIABILITY.md](../RELIABILITY.md) and
  [tests/structure/repo/test_runtime_verification_lane.py](../../tests/structure/repo/test_runtime_verification_lane.py)
  still pin runtime-sensitive paths to `research/...`
- `uv run poe verify` does not include `tests/structure`

Practical consequence:

- migration can produce both false positives and false negatives unless checks
  are updated in lockstep
- new guardrails should land before old assumptions are deleted

## Priority Classification

### Urgent mismatches

- `backtest` missing as a real package owner
- `integrations` missing as a real package owner
- architecture scanner not knowing about `backtest` or `integrations`

### Important but staged mismatches

- root-level `exchange.py` compatibility path
- research-owned result and engine types
- research-owned execution model placement

### Lower-priority cleanup mismatches

- empty `application/` or `adapters/` placeholders
- flattening context-local package shapes
- introducing `api.py` facades where they add real value

## Migration Sequencing Baseline

The safest migration order is staged.

### Stage 0. Freeze analysis authority

Before code moves:

- keep this gap analysis and the architecture docs as the shared reference set
- do not pretend the current codebase already matches the target

### Stage 1. Introduce target package boundaries without moving behavior

Create the missing package entry points first:

- `quantcraft.backtest`
- `quantcraft.integrations`
- `quantcraft.execution`

Optional only when real package work starts:

- `quantcraft.cli`

At this stage:

- compatibility behavior may still delegate back into `research` or existing
  exchange modules
- the goal is to make the target topology importable before it is fully owned

Why first:

- later code moves need a destination
- later structure checks need concrete package roots to target

### Stage 2. Move backtest ownership behind compatibility facades

Move backtest runtime ownership out of `research` and into `backtest`, but keep
old imports working temporarily.

Compatibility that likely must exist during transition:

- `quantcraft.research.BacktestEngine`
- `quantcraft.research.application.BacktestEngine`
- `quantcraft.research.application.backtest.BacktestResult`
- `quantcraft.research.application.backtest.BacktestSummary`
- `quantcraft.research.application.backtest.ExposureSummary`
- `quantcraft.research.application.Strategy`

Why before docs change:

- tests and quickstarts still treat those import paths as canonical
- a hard cut would break shipped usage and built-artifact checks

### Stage 3. Update guardrails for the target topology

Only after new package roots exist:

- expand architecture scanning to know `backtest` and `integrations`
- widen runtime-sensitive trigger paths beyond `research/...`
- add structure checks for target package boundaries and any chosen facades
- keep old checks only while they still reflect an intentional transitional
  contract

Why here:

- behavioral moves into new packages should not outrun their verification
- this stage reduces both false positives and false negatives for the later
  moves

### Stage 4. Materialize `integrations` and reduce root shim ownership

Move provider and venue protocol code toward:

- `quantcraft.integrations.venues.*`
- future `quantcraft.integrations.data_vendors.*`

During transition:

- root `quantcraft.Exchange` and `quantcraft.exchange` compatibility may remain
- `quantcraft.data` should continue exposing normalized data-facing surfaces

Why after Stage 2:

- backtest ownership is the more central architecture mismatch
- integrations work should not be mixed into the first runtime move

### Stage 5. Flatten local package shapes where that improves legibility

Once ownership is correct:

- evaluate each context independently
- remove empty or ceremonial layer packages
- keep local layering only where it materially helps navigation

This is intentionally last.

Why:

- ownership mistakes are higher risk than naming or depth cleanup
- flattening too early makes compatibility work harder

## Compatibility Rules For Later Migration Slices

The following rules should govern later implementation slices:

- preserve existing documented public imports until replacement imports and docs
  are both ready
- prefer additive package introduction before subtractive package removal
- add new structural guardrails before removing old ones
- keep `trading` as the shared kernel throughout; do not create a second kernel
  inside `backtest` or `execution`
- treat docs as shipped truth for current public imports until the
  compatibility layer is in place

These rules apply to transitional stages only.
They are not a permanent promise that every old import path must survive.

## Stage 6. Remove legacy traces and accept deliberate breaking cleanup

After the new topology is real, verified, and documented, the final cleanup
stage should remove transitional baggage on purpose.

This stage exists because the project is not yet a released public package.
At this phase, architectural completeness and internal coherence are more
important than preserving every compatibility shim.

Expected work in this stage:

- remove compatibility re-exports that only existed for migration
- replace remaining legacy import paths in code, tests, examples, and docs
- remove root-level or transitional shim modules whose only job was backward
  compatibility
- remove doc caveats that describe now-obsolete transitional ownership
- delete structure checks that protected legacy package layouts
- align public API docs, smoke tests, and built-artifact tests to the final
  chosen surface

Deliberate breaking changes are acceptable here when they remove transitional
layout debt and bring the shipped surface in line with the approved
architecture.

Examples of acceptable Stage 6 cleanup:

- retiring `quantcraft.research.application.backtest` after the final
  `quantcraft.backtest` surface is established
- retiring root compatibility paths such as `quantcraft.exchange` if their
  ownership has moved into the final package topology
- removing compatibility aliases from `quantcraft.__init__` once the intended
  root surface is explicitly narrowed

Stage 6 should only begin after:

- the new package owners are already real
- migration guardrails target the new topology
- docs and tests can be updated in one coherent pass
- the remaining compatibility surfaces are known to be transitional rather than
  still serving a necessary staged rollout

## Cross-Check Evidence

This analysis was cross-checked through read-only subagent fan-out:

- `Peirce`: source-topology and context mismatch review
  - confirmed that `backtest`, `execution`, and `integrations` are still absent
    as real packages
  - confirmed that backtest ownership still lives under `research`
  - confirmed that exchange/provider protocol code still sits in `data` plus a
    root shim
- `Cicero`: test/public-surface dependency review
  - confirmed that root exports, `quantcraft.data`, and
    `quantcraft.research` are hard-pinned by smoke, built-artifact, and doc
    tests
  - confirmed that `quantcraft.research.application` remains part of the
    current shipped compatibility surface
- `Lovelace`: structure-check and verification-lane review
  - confirmed that current architecture scanning does not know `backtest` or
    `integrations`
  - confirmed that `verify-runtime` triggers still point at `research/...`
  - confirmed that current structure tests still encode layer-first skeleton
    assumptions

Those reviews converged on the same core result:

- the target architecture is approved and coherent
- the current codebase is still materially transitional
- the first real migration work should introduce target package owners and
  compatibility seams before any cleanup pass tries to flatten or rename
  internals
