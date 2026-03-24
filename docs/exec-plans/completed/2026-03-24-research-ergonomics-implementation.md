# Research Ergonomics Implementation Plan

> **For Codex:** REQUIRED SUB-SKILLS: use `subagent-driven-development` to execute this plan slice-by-slice, and require every worker/reviewer subagent to read `docs/references/openai-harness-engineering.md` plus the slice-relevant architecture/spec docs before touching code.

**Goal:** Build the first approved `Research Ergonomics` slice set on top of the completed Backtest MVP so that users and future agents share one clear research-facing strategy, series, indicator, helper, and result surface.

**Architecture:** This batch stays inside the `research` bounded context and extends the existing Backtest MVP surface without changing the underlying trading semantics. The implementation should introduce a small public API under `quantcraft.research`, a controlled causal `SeriesView`, a thin `ta.*` wrapper surface, a small `qc.*` helper surface, a richer result layer, and canonical quickstart assets while keeping examples out of `src/`.

**Tech Stack:** Python 3.12+, `uv`, `pytest`, `ruff`, `mypy`, repo-local `scripts/` harness

## Lifecycle

- status: completed
- completed_on: 2026-03-24

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
- `docs/product-specs/research-ergonomics.md`

Slices that touch existing trading/backtest execution flow must also read:

- `docs/design-docs/trading-kernel-contract-draft-ko.md`

## Non-Negotiable Guardrails

- Do not expand scope beyond the approved `Research Ergonomics` spec.
- Do not change long-only, `1x`, `market/limit`, or current Backtest MVP order semantics.
- Do not expose raw `pandas.Series` or raw `numpy.ndarray` objects as the public research strategy surface.
- Do not let `research` duplicate `trading` semantics or move matching/state logic out of `trading`.
- Do not put example strategies under `src/`.
- Do not add plotting, parameter sweeps, walk-forward tooling, dedicated anti-bias diagnostics, paper trading, or live trading in this batch.
- Do not make `TA-Lib` fallback behavior part of the user-facing contract in this batch.

## Slice Plan

### Slice 1: Public Research API And Strategy Contract

**Intent:** Replace the current minimal strategy surface with the approved public `research` ergonomics entrypoint and the official `Strategy` contract.

**Ownership:**

- `src/quantcraft/research/`
- `tests/unit/research/application/`
- `tests/structure/architecture/`

**Files:**

- Modify: `src/quantcraft/research/__init__.py`
- Modify: `src/quantcraft/research/application/__init__.py`
- Modify: `src/quantcraft/research/application/strategy.py`
- Modify/Create: `tests/unit/research/application/test_strategy_surface.py`
- Modify/Create: relevant architecture tests under `tests/structure/architecture/`

**Acceptance:**

- `from quantcraft.research import Strategy, ta, qc, run_backtest` is the approved public import path.
- `Strategy` is an abstract base class.
- `Strategy` exposes `init()` and `on_bar()` as the only official hooks.
- `init()` is allowed to bind indicators and prepare state, but order creation from `init()` is rejected.
- `sell()` remains documented and enforced as long exit in the current long-only scope.
- No new lifecycle hooks are introduced.

### Slice 2: SeriesView And Causal Data Surface

**Intent:** Introduce the approved small causal `SeriesView` and make the strategy surface consume it instead of exposing raw history arrays directly.

**Ownership:**

- `src/quantcraft/research/`
- `src/quantcraft/research/domain/`
- `tests/unit/research/`

**Files:**

- Create/Modify: `src/quantcraft/research/domain/` modules for `SeriesView` and related small read-only types
- Modify: `src/quantcraft/research/application/strategy.py`
- Modify/Create: unit tests under `tests/unit/research/`

**Acceptance:**

- The public series contract supports only:
  - `series[index]`
  - `len(series)`
  - `series.latest`
  - `series.is_empty`
- `series[0]` means current confirmed value and positive indices walk backward in time.
- Negative indexing is rejected.
- Missing-history and warmup behavior surface as `na` semantics with `NaN` representation and `qc.is_na(...)`.
- The public strategy-facing surface does not expose raw pandas/numpy objects.

### Slice 3: Indicator Wrapper Surface And Helper Surface

**Intent:** Add the approved `ta.*` and `qc.*` user-facing ergonomics layer without leaking backend details into strategy code.

**Ownership:**

- `src/quantcraft/research/`
- `tests/unit/research/`

**Files:**

- Create: `src/quantcraft/research/ta.py`
- Create: `src/quantcraft/research/qc.py`
- Modify: `src/quantcraft/research/__init__.py`
- Modify/Create: unit tests under `tests/unit/research/`

**Acceptance:**

- Approved baseline indicators exist with the approved signatures:
  - `sma`
  - `ema`
  - `rsi`
  - `macd`
  - `atr`
  - `cci`
  - `bollinger_bands`
- Multi-output indicators return named result objects:
  - Bollinger: `upper`, `middle`, `lower`
  - MACD: `macd`, `signal`, `histogram`
- Indicator bindings created in `init()` behave like causal live views rather than frozen snapshots.
- Approved helpers exist:
  - `qc.is_na`
  - `qc.crossover`
  - `qc.crossunder`
- Public strategy examples and tests do not import `talib`, `numpy`, or `pandas` directly for the canonical path.

### Slice 4: Expanded Backtest Result Surface

**Intent:** Extend `BacktestResult` beyond MVP minimal outputs so the first research-facing result contract is useful without adding plotting.

**Ownership:**

- `src/quantcraft/research/application/`
- `tests/unit/research/application/`
- `tests/integration/research/`

**Files:**

- Modify: `src/quantcraft/research/application/backtest.py`
- Modify/Create: unit and integration tests under `tests/unit/research/application/` and `tests/integration/research/`

**Acceptance:**

- `BacktestResult` and/or nested summary objects expose the approved baseline metrics:
  - trade log
  - equity curve
  - final balance
  - final equity
  - total return
  - max drawdown
  - total trades
  - win rate
  - average win
  - average loss
  - profit factor
  - simple exposure summary
- The result surface remains deterministic and derived from the shared backtest path.
- Plotting is not added.

### Slice 5: Canonical Examples And Quickstart Assets

**Intent:** Create the first canonical usage path for users and future agents without polluting `src/` with example code.

**Ownership:**

- `docs/`
- notebooks or notebook-validation surfaces as needed
- `tests/integration/research/`
- `tests/structure/docs/`

**Files:**

- Create/Modify: a short quickstart doc under `docs/`
- Create/Modify: a supporting notebook under the approved notebook area
- Modify/Create: integration or doc-structure tests as needed

**Acceptance:**

- Canonical quickstart flow demonstrates:
  1. subclass `Strategy`
  2. bind indicators in `init()`
  3. evaluate signals and place orders in `on_bar()`
  4. call `run_backtest(...)`
  5. inspect summary/result
  6. inspect equity curve and trade log in the notebook
- Canonical examples are:
  - primary: `SMA crossover`
  - secondary: `RSI 30/70 mean reversion`
- Example and quickstart code use explicit `quantity=1`.
- Example assets live outside `src/`.
- Doc/notebook assets remain aligned with the canonical public import path.

## Review Protocol Per Slice

For every slice, use this order:

1. worker subagent implements the slice
2. spec reviewer checks only against approved docs and this plan
3. code-quality reviewer checks maintainability, drift risk, and OpenAI-style harness alignment
4. only then move to the next slice

Do not let a later slice start while a prior slice still has open review findings.

## Verification Gates Per Slice

At the end of every slice:

- run the slice-relevant tests first
- run `uv run ruff check .`
- run `uv run mypy src`
- run `uv run python scripts/repo_check.py`

At the end of the batch:

- run `uv run pytest -q`
- run `uv build`

## Human-Gate Conditions

Stop and ask the human if any of the following occurs:

- the approved `Research Ergonomics` spec no longer covers a required behavior
- a proposed public API change would materially alter the approved strategy, series, indicator, helper, or result contract
- implementation pressure would force a change to current Backtest MVP or Tier A trading semantics
- reviewers find a conflict between the approved spec and existing canonical architecture/governance docs

## Execution Notes

- The public ergonomics surface should stay deliberately small.
- Prefer adding tests for user-visible semantics over exposing more convenience APIs.
- Repeated ambiguity found during implementation should be promoted into docs or structure checks before scope broadens.
