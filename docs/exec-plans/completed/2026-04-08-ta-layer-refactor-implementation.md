# TA Layer Refactor Implementation

## Lifecycle

- status: completed
- completed_on: 2026-04-09

## Status

- Class: `implementation`
- Scope: execute the TA layer refactor from approved design to verified final state

Related documents:

- [../../plans/2026-04-08-ta-layer-refactor-design.md](../../plans/2026-04-08-ta-layer-refactor-design.md)
- [../../product-specs/research-ergonomics.md](../../product-specs/research-ergonomics.md)
- [../../RELIABILITY.md](../../RELIABILITY.md)
- [../../design-docs/architecture-governance.md](../../design-docs/architecture-governance.md)
- [../../references/openai-harness-engineering.md](../../references/openai-harness-engineering.md)

## Role

This document is the execution authority for the TA layer refactor.

Implementation agents must use:

- the design document for structure and contract decisions
- this document for milestones, blocking conditions, verification, and final completion

## Non-Negotiable Rules

1. The final state must not contain compatibility shims, deprecated aliases, or
   old naming remnants.
2. If semantic divergence is observed, the work must stop and escalate to a human.
3. Partial migration is not complete.
4. Code, tests, current product spec, and quickstart/reference docs must be
   updated in the same change set.

## Semantic Lock Before Backend Swap

Before switching computation to `TA-Lib`, first lock the current implementation
contract with fixtures and tests.

Target indicators:

- `sma`
- `ema`
- `rsi`
- `atr`
- `cci`
- `bb`
- `macd`

For each indicator, semantic lock must cover:

1. public signature
2. warmup behavior
3. `NaN` behavior
4. invalid-parameter behavior
5. return shape
6. multi-output ordering or field mapping

Precedence rule:

- the current implemented product spec wins over observed code
- if current code disagrees with the canonical implemented product spec, do not
  write semantic-lock tests yet; stop and escalate to a human first

Rules:

- do not start with the backend swap before semantic lock exists
- if the current product spec, current code, `TA-Lib`, or Pine disagree on a
  canonical fixture, stop and escalate instead of guessing

## Required Deliverables

### Source Layout

The following files must exist:

- `src/quantcraft/research/indicators/__init__.py`
- `src/quantcraft/research/indicators/pure/__init__.py`
- `src/quantcraft/research/indicators/pure/sma.py`
- `src/quantcraft/research/indicators/pure/ema.py`
- `src/quantcraft/research/indicators/pure/rsi.py`
- `src/quantcraft/research/indicators/pure/atr.py`
- `src/quantcraft/research/indicators/pure/cci.py`
- `src/quantcraft/research/indicators/pure/bb.py`
- `src/quantcraft/research/indicators/pure/macd.py`
- `src/quantcraft/research/indicators/runtime/__init__.py`
- `src/quantcraft/research/indicators/runtime/base.py`
- `src/quantcraft/research/indicators/runtime/views.py`
- `src/quantcraft/research/indicators/runtime/runtime.py`
- `src/quantcraft/research/indicators/runtime/factory.py`

### Legacy Removal

The following files must not exist in the final state:

- `src/quantcraft/research/_indicator_kernels.py`
- `src/quantcraft/research/_indicator_runtime.py`
- `tests/unit/research/test_indicator_runtime.py`

### Test Layout

The following files must exist:

- `tests/unit/research/test_indicator_surface.py`
- `tests/unit/research/indicators/pure/test_sma.py`
- `tests/unit/research/indicators/pure/test_ema.py`
- `tests/unit/research/indicators/pure/test_rsi.py`
- `tests/unit/research/indicators/pure/test_atr.py`
- `tests/unit/research/indicators/pure/test_cci.py`
- `tests/unit/research/indicators/pure/test_bb.py`
- `tests/unit/research/indicators/pure/test_macd.py`
- `tests/unit/research/indicators/runtime/test_runtime.py`
- `tests/unit/research/indicators/runtime/test_views.py`
- `tests/unit/research/indicators/runtime/test_factory.py`

## Required Structure Checks

In this slice, the following structure checks are required deliverables, not
optional follow-up work:

1. indicator package layout check
2. legacy alias absence check
3. current-docs old-naming absence check
4. approved public naming table check
5. `ta.bb` result-object contract check

Recommended location:

- `tests/structure/repo/test_indicator_refactor_contracts.py`

At minimum, these checks must protect:

- existence of the approved source layout
- absence of legacy source/test paths
- absence of `ta.bollinger_bands` in current docs/code/tests
- documentation of `ta.bb` as the canonical public name
- preservation of the `BollingerBandsResult.middle/upper/lower` contract

## Milestones

### M1. Semantic Lock

- lock current indicator semantics in tests
- add divergence detection

Completion condition:

- current public behavior is locked before any pure/backend swap

### M2. Pure Layer Introduction

- add the `TA-Lib` dependency
- introduce pure indicator modules
- write pure indicator tests

Completion condition:

- pure tests pass

### M3. Runtime Layer Migration

- introduce the runtime adapter layer
- make `ta.py` use the new runtime layer
- preserve live strategy bindings

Completion condition:

- runtime tests pass
- public surface tests pass

### M4. Public Naming Realignment

- introduce `ta.bb` as the canonical public surface
- remove `ta.bollinger_bands`
- remove old naming from current docs and quickstarts

Completion condition:

- no legacy alias remains anywhere in the current repository state

### M5. Legacy Removal And Final Verification

- remove old internal files
- add structure checks
- run final verification

Completion condition:

- the full success gate passes

## Success Gate

If any one item fails, the work is not complete.

### Mechanical Completion Checklist

| Gate | Protected behavior | Required evidence |
| --- | --- | --- |
| semantic lock | the contract is locked before backend swap | per-indicator semantic-lock tests |
| package layout | the approved package layout exists | source/test structure checks |
| public surface | Pine-aligned naming is canonical | `ta.bb` surface tests + alias-absence checks |
| bb result contract | `ta.bb` keeps the Pythonic named-result contract | public surface tests + structure checks |
| pure layer | indicator math lives in the pure layer | pure tests pass |
| runtime layer | the live causal contract still holds | runtime tests pass |
| legacy removal | no old naming or shims remain | structure checks + grep-equivalent checks |
| repo verification | repo-wide correctness and runtime lanes still hold | `verify` + `verify-runtime` pass |

### Required Verification Commands

Before the final report, all of the following commands must be run from the
current repository state:

```bash
uv run pytest tests/unit/research/test_indicator_surface.py -q
uv run pytest tests/unit/research/indicators/pure -q
uv run pytest tests/unit/research/indicators/runtime -q
uv run pytest tests/structure/repo/test_indicator_refactor_contracts.py -q
uv run poe verify
uv run poe verify-runtime
```

### Final-State Conditions

All of the following must be true in the final state:

1. the approved source layout exists
2. the approved test layout exists
3. `ta.bb` exists as the canonical public surface
4. `ta.bollinger_bands` does not exist
5. the `BollingerBandsResult` public contract is preserved
6. no legacy shim remains
7. no old internal source/test file remains
8. current docs contain no old naming remnants

Allowed exceptions:

- `docs/plans/`
- `docs/exec-plans/completed/`

In other words, only historical plan/design records are allowed to retain legacy
names.

## Blocking Conditions

Stop and escalate to a human if any of the following is observed:

- mismatch between current product spec, current code, `TA-Lib`, and Pine semantics
- inability to keep the named-result `ta.bb` public contract
- inability to lock warmup / `NaN` / seed behavior unambiguously from the current
  product spec

Agents must not resolve these conflicts autonomously.

## Product Spec Update Rule

Do not update `docs/product-specs/research-ergonomics.md` before the code
changes exist.

When implementing, update all of the following in the same change set:

- code
- tests
- `docs/product-specs/research-ergonomics.md`
- quickstart/reference docs

## Final Report Rule

The final report is allowed only when all of the following are true:

- the full success gate passes
- every required verification command has been run
- no blocking condition is active
- no shim, alias, or legacy path remains
