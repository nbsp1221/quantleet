# Backtest MVP Implementation Plan

> **For Codex:** REQUIRED SUB-SKILLS: use `subagent-driven-development` to execute this plan slice-by-slice, and require every worker/reviewer subagent to read `docs/references/openai-harness-engineering.md` plus the slice-relevant architecture/spec docs before touching code.

**Goal:** Build the first approved `Backtest MVP` implementation slice set for `quantcraft` without violating the approved architecture, governance, or Backtest MVP product spec.

**Architecture:** The implementation must preserve the approved bounded-context split (`data / trading / research / execution`) while introducing only the minimum source skeleton and shared contracts needed for the first deterministic backtest flow. The internal engine remains tick/event-driven; MVP user experience remains `on_bar`-driven. The first implementation batch prioritizes structure, contracts, and deterministic matching semantics before broader orchestration.

**Tech Stack:** Python 3.12+, `uv`, `pytest`, `ruff`, `mypy`

## Lifecycle

- status: completed
- completed_on: 2026-03-22

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
- `docs/references/openai-harness-engineering.md`
- `docs/design-docs/quantcraft-architecture.md`
- `docs/design-docs/architecture-governance.md`
- `docs/product-specs/backtest-mvp.md`

Additionally, slices that touch shared trading semantics must also read:

- `docs/design-docs/trading-kernel-contract-draft-ko.md`

## Non-Negotiable Guardrails

- Do not expand scope beyond the approved `Backtest MVP`.
- Do not introduce shorting, leverage, stop orders, trigger orders, paper/live runtime, or portfolio rebalancing.
- Do not downgrade the engine into a bar-only toy engine.
- Do not let `trading` know whether ticks came from OHLCV synthesis or live feeds.
- Do not place source-specific conversion logic inside `trading`.
- Do not bypass the test taxonomy or repository checks.
- Tier A work (`trading`) may be implemented autonomously, but must not be presented as fully human-free final approval.

## Slice Plan

### Slice 1: Source Skeleton And Contract Types

**Intent:** Establish the approved package boundaries and only the Slice 1 minimum core types for the MVP without yet building the full matching flow.

**Explicit deferrals for Slice 1:**

- do not add `OrderEvent`
- do not add `TimerEvent`
- keep both deferred to a later slice when behavior actually requires them

**Ownership:**

- `src/quantcraft/data/`
- `src/quantcraft/research/`
- `src/quantcraft/trading/`
- `tests/structure/architecture/`
- `tests/unit/trading/`

**Files:**

- Create package skeletons under:
  - `src/quantcraft/data/`
  - `src/quantcraft/research/`
  - `src/quantcraft/trading/`
- Create minimal typed modules for:
  - `OrderIntent`
  - `TickEvent`
  - `BarEvent`
  - `FillEvent`
  - basic cost config input
- Do not introduce placeholder event types for deferred contracts.
- Add structure and contract tests under:
  - `tests/structure/architecture/`
  - `tests/unit/trading/`

**Acceptance:**

- Package paths exist and follow the approved context split.
- Slice 1 contract types reflect only the approved fields needed for this slice.
- `OrderEvent` and `TimerEvent` remain explicitly deferred and absent from Slice 1 code.
- Structure tests enforce that `research -> trading` is allowed and `trading -> research` is not.
- No behavior outside approved slice scope is added.

### Slice 2: Synthetic Path And Bar/Tick Conversion

**Intent:** Implement deterministic OHLCV-to-synthetic-event conversion for the approved MVP semantics without yet building the full strategy/backtest runner.

**Ownership:**

- `src/quantcraft/research/`
- `tests/unit/research/`

**Files:**

- Create conversion modules for:
  - bullish path: `open -> low -> high -> close`
  - bearish path: `open -> high -> low -> close`
  - gap segment: `prev_close -> open`
- Add tests for:
  - no order-dependent path fabrication
  - no fills at intermediate gap prices
  - deterministic event emission from checked-in fixtures

**Acceptance:**

- The adapter produces deterministic synthetic events from OHLCV.
- The path rule does not vary to favor order outcomes.
- Gap semantics match the approved spec.

### Slice 3: Strategy Surface And Order Intake

**Intent:** Introduce the first `self`-based strategy surface with `on_bar` and `OrderIntent` emission.

**Ownership:**

- `src/quantcraft/research/`
- `src/quantcraft/trading/`
- `tests/unit/research/`

**Files:**

- Create the minimal strategy base and context/facade needed for:
  - `on_bar`
  - emitting `OrderIntent`
- Add tests for:
  - `on_bar` only after bar close
  - order intents do not apply retroactively to the current bar

**Acceptance:**

- User-facing strategy API is `self`-based.
- `on_bar` exists as the first public hook.
- Orders created from `on_bar` become effective from the next bar by default.

### Slice 4: Matching, Fill Application, And Long-Only State

**Intent:** Build the minimum matching core for `market` and `limit` orders plus long-only fill application and state updates.

**Ownership:**

- `src/quantcraft/trading/`
- `tests/unit/trading/`

**Files:**

- Add matching logic for:
  - `market`
  - `limit`
- Add long-only state application for:
  - position
  - balance
  - realized/unrealized PnL
  - equity
- Add tests for:
  - adverse slippage on `market`
  - no-worse-than-limit behavior on `limit`
  - long-only and `1x` spot-like constraints

**Acceptance:**

- Matching is array-depth capable even if the first fixtures use one-level books.
- Long-only state updates are deterministic.
- `FillEvent` minimum fields are preserved.

### Slice 5: Backtest Runner And Result Surface

**Intent:** Wire the first end-to-end deterministic backtest run from OHLCV input to output summary.

**Ownership:**

- `src/quantcraft/research/`
- `tests/integration/`

**Files:**

- Create the first backtest runner/orchestration path
- Add integration tests for:
  - checked-in OHLCV input
  - deterministic trade log
  - equity / PnL outputs

**Acceptance:**

- Single-symbol deterministic run passes from input to summary outputs.
- The run uses the shared trading kernel path rather than a separate bar-only simulation flow.

## Verification Gates Per Slice

At the end of every slice:

- run the slice-relevant tests first
- run `uv run ruff check .`
- run `uv run mypy src`
- run `uv run python scripts/repo_check.py`

At the end of the batch:

- run `uv run pytest -q`
- run `uv build`

## Review Protocol Per Slice

For every slice, use this order:

1. worker subagent implements the slice
2. spec reviewer checks only against the approved documents
3. code-quality reviewer checks maintainability and drift
4. only then move to the next slice

Do not let a later slice start while a prior slice still has open review findings.

## Human-Gate Conditions

Stop and ask the human if any of the following occurs:

- the approved spec no longer covers a required behavior
- the worker needs to change Tier A long-lived semantics, not just implement them
- the implementation would force promotion of a deferred global contract
- a reviewer finds a conflict between approved docs

## Execution Notes

- Commits are intentionally omitted from this plan because the current session policy is repository modification without commit automation.
- Slice execution should prefer minimal, test-first increments.
- Repeated ambiguity or drift found during implementation should be promoted into docs or structure checks before broadening scope.
