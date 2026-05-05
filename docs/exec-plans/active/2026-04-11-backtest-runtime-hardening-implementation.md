# Backtest Runtime Hardening Implementation Plan

> **For Codex:** REQUIRED SUB-SKILLS: use `systematic-debugging` before changing runtime or backtest semantics, `test-driven-development` before each behavior change, and `verification-before-completion` before claiming any slice is done. Reviewer agents must read the slice-relevant spec and this plan before reviewing.

**Goal:** Harden the current backtest runtime so that indicator causality, runtime ownership, OHLCV execution approximation, and shared trading-semantics boundaries are explicit, testable, and safe for future paper/live extension without changing the current public research UX.

**Architecture:** Keep the current public `quantleet.research` surface and current single-symbol long-only Backtest MVP behavior stable, while making three internal contracts explicit: indicator runtime contract, backtest execution-model contract, and order-activation policy contract. Shared trading meaning remains in `trading`, historical approximation remains in `research`, and any ambiguity between them must be resolved through tests and documented stop conditions rather than agent inference.

**Tech Stack:** Python 3.13, `uv`, `pytest`, `pytest-benchmark`, `ruff`, `mypy`, `quantleet.data`, `quantleet.research`, `quantleet.trading`

## Lifecycle

- status: active
- status_reason: implementation and verification are complete, but the plan remains active until human review confirms archival.

## Current Status

- Slice 1: complete
- Slice 2: complete
- Slice 3: complete
- Slice 4: complete
- Slice 5: complete

---

## Required Reading Before Any Task

Every worker and reviewer must read:

- `AGENTS.md`
- `ARCHITECTURE.md`
- `docs/RELIABILITY.md`
- `docs/design-docs/quantleet-architecture.md`
- `docs/design-docs/architecture-governance.md`
- `docs/product-specs/backtest-mvp.md`
- `docs/product-specs/research-ergonomics.md`
- `docs/plans/2026-04-10-backtest-runtime-hardening-design.md`

Workers touching indicator internals must also read:

- `docs/plans/2026-04-08-ta-layer-refactor-design.md`
- `docs/exec-plans/completed/2026-04-08-ta-layer-refactor-implementation.md`

Workers touching the backtest hot path must also read:

- `docs/research/2026-04-03-rsi-performance-analysis.md`
- `docs/exec-plans/completed/2026-04-03-indicator-performance-optimization.md`

## Batch Intent

This batch is not a public feature expansion.

It exists to turn already-approved design direction into explicit internal
contracts and stronger repository checks while preserving the current shipped
Backtest MVP and research ergonomics surface.

Required preserved behavior:

- `Strategy.init()` / `Strategy.on_bar()` public UX
- `SeriesView` indexing semantics and visible-prefix guard
- `ta.*` / `qc.*` public names and signatures
- `BacktestEngine.run(bars=..., strategy=...)`
- `BacktestEngine.run(source=..., strategy=...)`
- current single-symbol long-only deterministic result contracts
- current canonical RSI perf gate

## Non-Negotiable Guardrails

1. Do not change the current public `quantleet.research` API in this batch.
2. Do not change the current implemented Backtest MVP semantics unless the
   canonical product spec is first updated with human approval.
3. Do not move fill matching, fill application, or trading state transitions
   out of `trading`.
4. Do not leave OHLCV execution approximation hidden in the backtest loop once
   the execution-model slice begins.
5. Do not expose a public `BacktestExecutionModel` configuration surface in
   this batch. Internal architecture split comes first.
6. Do not introduce `execution` package implementation work in this batch.
7. Do not loosen the current perf gate, canonical RSI result-shape assertions,
   or coverage thresholds to make the batch pass.
8. Do not silently resolve semantic divergence between:
   - product specs
   - current tested behavior
   - runtime implementation
   - pure/reference indicator outputs
9. Any Tier A semantic change must stop for human review even if tests are green.

## Human-Gate Conditions

Stop and ask the human before proceeding if any of the following occurs:

- indicator warmup, `NaN`, or visibility semantics disagree between current
  tests, current product spec, and proposed runtime contract
- moving order activation into `trading.application` would change current
  backtest scheduling behavior rather than merely making it explicit
- `BacktestExecutionModel` needs public constructor/config exposure to complete
  the batch
- preserving current semantics would require adding new public event types such
  as `OrderEvent` or `TimerEvent`
- current canonical RSI fixture parity fails after a structural refactor and
  the cause is not immediately obvious
- a proposed boundary check would enforce speculative future architecture
  rather than a currently declared contract

## Explicit Ownership Boundaries For This Batch

These boundaries are part of the implementation contract for this batch.

### Shared Trading Meaning

The following remain owned by `trading`:

- order-intent meaning
- matching semantics
- fee/slippage cost application
- fill application
- cash / position / realized PnL / unrealized PnL / equity state transitions
- long-only `sell while flat` interpretation

Canonical code paths today:

- `src/quantleet/trading/domain/intents.py`
- `src/quantleet/trading/domain/matching.py`
- `src/quantleet/trading/domain/state.py`

### Historical Approximation

The following remain owned by `research`:

- converting historical `BarSeries` into execution-driving market events
- intrabar path assumptions for OHLCV bars
- synthetic book assumptions for the current backtest-only model
- strategy-facing orchestration around the shared trading kernel

Canonical code paths today:

- `src/quantleet/research/adapters/execution_model.py`
- `src/quantleet/research/application/backtest.py`
- `src/quantleet/research/application/_runtime.py`

### Order Activation Policy In This Batch

Current implementation owner:

- `research.application`

Target post-batch shape:

- explicit policy object or isolated rule with no backtest-loop-internal
  ad hoc activation logic

Important:

- this batch may isolate the policy and add tests
- this batch must not claim that final long-lived ownership in
  `trading.application` is fully settled unless no behavior changes and the
  docs stay aligned

## Required Deliverables

The batch is incomplete unless all of the following exist in the final state.

### 1. Explicit Indicator Runtime Contract

Deliverables:

- a documented runtime contract for official indicators
- explicit runtime ownership distinct from pure/reference ownership
- tests that protect:
  - visible-prefix causality
  - append-only update behavior
  - rebuild fallback behavior
  - parity with current pure/reference outputs
  - current warmup and `NaN` behavior

At minimum, the final repository must make it obvious which path is:

- canonical runtime path
- pure/reference path
- optimization-only precompute path

### 2. Explicit Backtest Execution Model

Deliverables:

- a named internal `BacktestExecutionModel` abstraction
- an internal default implementation named
  `ConservativeOHLCVExecutionModel`
- preservation of current intrabar ordering semantics:
  - bullish/doji: `open -> low -> high -> close`
  - bearish: `open -> high -> low -> close`
- preservation of current synthetic same-price bid/ask snapshot model
- result or summary metadata recording the execution-model identity used

### 3. Explicit Order Activation Policy

Deliverables:

- a named policy boundary for “orders created on bar close become active on the
  next execution segment”
- removal of hidden activation timing assumptions from the backtest loop body
- regression tests proving current next-bar activation still holds

### 4. Boundary Checks

Deliverables:

- structure checks that prevent:
  - `research` from reimplementing fill state transitions
  - `execution` from later growing a second position engine unnoticed
  - runtime-sensitive indicator work from bypassing the runtime lane docs/checks
- updated docs and tests for any newly promoted mechanical rule

## Forbidden Final States

The batch is incomplete if any of these remain true:

- official indicator runtime still depends on “precomputed full history that
  happens to look causal” as the only semantic authority
- OHLCV execution approximation still exists only as unnamed helper functions
  plus backtest-loop coupling
- order activation timing still exists only as timestamp comparison logic
  embedded in the loop with no named policy
- `research` owns fill-application logic or trading-state mutation logic
- structure checks remain silent about the new explicit boundaries

## Slice Plan

### Slice 1: Semantic Lock And Contract Test Expansion

**Intent:** Lock the current runtime-sensitive behavior before introducing new
internal abstractions.

**Ownership:**

- `tests/unit/research/`
- `tests/integration/research/`
- `tests/structure/repo/`
- `tests/structure/architecture/`
- `docs/plans/2026-04-10-backtest-runtime-hardening-design.md`
- `docs/exec-plans/active/2026-04-11-backtest-runtime-hardening-implementation.md`

**Files to read before coding:**

- `src/quantleet/research/ta.py`
- `src/quantleet/research/indicators/runtime/base.py`
- `src/quantleet/research/indicators/runtime/runtime.py`
- `src/quantleet/research/indicators/runtime/factory.py`
- `src/quantleet/research/application/backtest.py`
- `src/quantleet/research/adapters/execution_model.py`

**Required work:**

- add missing tests for the runtime contract fields proposed by the design
  document before changing implementation
- expand tests to make current behavior explicit for:
  - append-only growth
  - reset/rebuild behavior
  - visible-prefix causality
  - current next-bar order activation
  - current execution path metadata expectations if absent

**Must not do in this slice:**

- no production refactor yet beyond tiny test-enabling seams
- no public doc drift that redefines product behavior

**Acceptance:**

- current runtime-sensitive semantics are locked in tests first
- any ambiguity is surfaced as a stop condition, not guessed around

### Slice 2: Indicator Runtime Contract Introduction

**Intent:** Separate runtime indicator ownership from pure/reference ownership
without changing current public `ta.*` ergonomics.

**Ownership:**

- `src/quantleet/research/indicators/runtime/`
- `src/quantleet/research/indicators/pure/`
- `src/quantleet/research/ta.py`
- `tests/unit/research/indicators/runtime/`
- `tests/unit/research/test_indicator_surface.py`
- `tests/integration/research/test_canonical_rsi_contract.py`
- `tests/perf/test_rsi_backtest_benchmark.py`

**Required work:**

- introduce the explicit runtime contract shape actually used by official
  indicators
- keep pure/reference functions as parity and fixture-lock authority
- route runtime-capable indicators through explicit runtime ownership
- keep rebuild fallback for non-append invalidation

**Indicator priority for this batch:**

- mandatory first set: `sma`, `ema`, `rsi`, `atr`
- optional only if the first set is stable and still clean: `cci`, `bb`, `macd`

**Important execution rule:**

- do not start by hand-rolling every indicator
- first prove the runtime contract and runtime-path plumbing on the mandatory
  first set

**Acceptance:**

- runtime path results remain parity-checked against current pure/reference
  outputs
- canonical RSI contract still passes
- `uv run poe perf-check` still passes
- no public API changes

### Slice 3: Backtest Execution Model Extraction

**Intent:** Replace unnamed OHLCV event-conversion helpers with an explicit
backtest execution-model abstraction while preserving current behavior.

**Ownership:**

- `src/quantleet/research/adapters/`
- `src/quantleet/research/application/backtest.py`
- `tests/unit/research/adapters/`
- `tests/integration/research/`

**Required work:**

- introduce internal execution-model types under `research.adapters`
- move current OHLCV path and synthetic-book assumptions behind the named
  default implementation
- keep the backtest loop consuming execution-driving events, not re-owning
  historical approximation details
- record execution-model identity in result metadata or summary metadata

**Must not do in this slice:**

- no public constructor option for alternate execution models
- no claim of venue-faithful simulation
- no new partial-fill visibility surface

**Acceptance:**

- current synthetic path tests still pass
- current deterministic backtest semantics still pass
- backtest code is more explicit without changing result shape

### Slice 4: Order Activation Policy Isolation

**Intent:** Make next-segment activation a named policy instead of an implicit
loop convention.

**Ownership:**

- `src/quantleet/research/application/`
- optionally `src/quantleet/trading/application/` only if behavior remains
  identical and ownership is unambiguous
- `tests/integration/research/`
- `tests/unit/research/application/`

**Required work:**

- isolate the activation rule behind a named policy object or rule module
- remove ad hoc timing decisions from the backtest loop body
- strengthen regression tests for:
  - next-bar activation
  - active-order precedence versus newly activated orders
  - no retroactive fills on the signal bar

**Must not do in this slice:**

- no broader event-model expansion
- no `OrderEvent` or `TimerEvent`
- no speculative live-runtime abstractions

**Acceptance:**

- current timing semantics still pass exactly
- ownership of the rule is explicit in code and docs

### Slice 5: Boundary Checks, Docs Sync, And Final Verification

**Intent:** Promote stabilized rules into structure checks and sync the
repository control plane.

**Ownership:**

- `tests/structure/architecture/`
- `tests/structure/repo/`
- `docs/RELIABILITY.md`
- `docs/QUALITY_SCORE.md`
- `docs/exec-plans/active/index.md`
- `docs/exec-plans/active/2026-04-11-backtest-runtime-hardening-implementation.md`

**Required work:**

- add structure checks for the new runtime/execution-model boundary rules
- update reliability docs if trigger paths or runtime-lane expectations change
- update repository health docs only if the batch materially changes
  implementation evidence
- keep lifecycle metadata and index state aligned

**Acceptance:**

- repository checks protect the newly explicit boundaries
- docs and checks agree on the same current policy
- batch verification passes from the current repository state

## Minimum Test Inventory Per Slice

The following existing tests are mandatory regression gates during this batch
and must not be weakened:

- `tests/unit/research/test_indicator_surface.py`
- `tests/unit/research/indicators/runtime/test_runtime.py`
- `tests/unit/research/indicators/runtime/test_factory.py`
- `tests/unit/research/adapters/test_execution_model.py`
- `tests/unit/trading/test_matching_and_state.py`
- `tests/integration/research/test_backtest_execution_semantics.py`
- `tests/integration/research/test_backtest_strategy_runtime_contract.py`
- `tests/integration/research/test_canonical_rsi_contract.py`
- `tests/perf/test_rsi_backtest_benchmark.py`
- `tests/structure/architecture/test_domain_boundaries.py`
- `tests/structure/repo/test_runtime_verification_lane.py`

## Required Verification Gates

### Per Slice

At the end of every slice, run the narrowest relevant test set first, then:

- `uv run ruff check .`
- `uv run mypy src`

### Runtime-Sensitive Slices

After any slice touching one of the following paths, run:

- `src/quantleet/research/ta.py`
- `src/quantleet/research/adapters/execution_model.py`
- `src/quantleet/research/indicators/runtime/`
- `src/quantleet/research/indicators/pure/`
- `src/quantleet/research/application/backtest.py`
- `src/quantleet/research/application/order_activation.py`

Required command:

- `uv run poe verify-runtime`

### End Of Batch

Before closing the plan, run all of:

- `uv run poe verify`
- `uv run poe verify-runtime`

## Review Protocol

For each slice, use this order:

1. implement only the stated slice scope
2. verify against the current product specs
3. verify against this execution plan
4. run the required commands from the current repository state
5. only then move to the next slice

If a slice reveals ambiguity that changes ownership, semantics, or public
contract, stop and escalate instead of continuing with a “reasonable guess.”

## Completion Rule

This plan may move from `active` to `completed` only when:

- every slice is marked `complete`
- no human-gate issue remains open
- all end-of-batch verification commands pass
- the active/completed index state and lifecycle metadata are updated in the
  same change set
