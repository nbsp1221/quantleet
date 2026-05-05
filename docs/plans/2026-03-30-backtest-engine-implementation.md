# Backtest Engine Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a user-facing `BacktestEngine`, a canonical `TimeBar` single-bar type, and a self-describing `BarSeries` dataset contract so execution runs on explicit materialized data rather than hidden source metadata assumptions.

**Architecture:** Keep the current backtest kernel and result model intact, add a thin orchestration layer as `BacktestEngine`, add `TimeBar` and `BarSeries` at the `quantleet.data` boundary, and remove the public `run_backtest(...)` free-function entry during this slice so there is one canonical execution surface. This slice supports `time` bars only. Do not introduce a public generic engine base, and do not move mutable kernel state out of the existing backtest path.

**Tech Stack:** Python 3.13, dataclasses, pytest, mypy, ruff, repo-local harness scripts, current `quantleet.data` and `quantleet.research` surfaces

---

### Task 1: Lock the new execution contract with failing tests

**Files:**
- Modify: `tests/integration/research/test_backtest_runner.py`
- Modify: `tests/smoke/local/test_public_imports.py`
- Modify: `tests/structure/repo/test_repository_entrypoint_docs.py`

**Step 1: Write the failing tests**

Add tests that assert:

- `BacktestEngine` is publicly importable from `quantleet.research`
- `TimeBar` and `BarSeries` are publicly importable from `quantleet.data`
- `BacktestEngine(...).run(bars=..., strategy=...)` returns the current `BacktestResult`
- `BacktestEngine(...).run(source=..., strategy=...)` is part of the approved contract
- `run_backtest(...)` is no longer part of the public `quantleet.research` entry surface

**Step 2: Run the targeted tests to verify they fail**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py tests/smoke/local/test_public_imports.py tests/structure/repo/test_repository_entrypoint_docs.py -q
```

Expected:

- failures focused on the missing `BacktestEngine` / materialized-dataset surface and outdated docs contract

**Step 3: Keep the assertions focused**

Do not pin exact internal helper names or private module structure.

### Task 2: Add `TimeBar` and the `BarSeries` dataset contract

**Files:**
- Modify: `src/quantleet/data/domain/__init__.py`
- Create or modify: `src/quantleet/data/domain/bars.py`
- Modify: `src/quantleet/data/domain/sources.py`
- Modify: `tests/unit/data/domain/test_bars.py`

**Step 1: Add the dataset type**

Implement the approved public data types:

- `TimeBar`
- `BarSeries`

`BarSeries` owns:

- `symbol`
- `timeframe`
- `bar_type`
- `rows`

Rules:

- `rows` is a tuple of `TimeBar`
- `bar_type` must be `"time"` in this slice

Keep the dataset narrow and historical-only.

**Step 2: Update the source contract**

Make `HistoricalDataSource.load()` return `BarSeries` rather than bare rows.

Do not add hidden optional metadata assumptions to the source ABC.

**Step 3: Add contract tests**

Cover:

- valid `TimeBar` construction
- valid `BarSeries` construction
- invalid metadata
- invalid non-`time` `bar_type`
- immutability/read-only expectations
- consistency between `BarSeries` metadata and `TimeBar` rows

**Step 4: Run targeted tests**

Run:

```bash
uv run pytest tests/unit/data/domain/test_bars.py -q
```

Expected:

- dataset contract tests pass

### Task 3: Update shipped data sources to materialize the dataset

**Files:**
- Modify: `src/quantleet/data/adapters/ccxt_source.py`
- Modify: `src/quantleet/data/adapters/csv_source.py`
- Modify: `src/quantleet/data/adapters/dataframe_source.py`
- Modify: `tests/unit/data/adapters/test_dataframe_source.py`
- Modify: any directly related source-adapter tests as needed

**Step 1: Add failing tests**

Pin that shipped sources now return `BarSeries` and that the dataset metadata matches the source configuration.

**Step 2: Implement the minimal source updates**

Each shipped historical source should return a self-describing `BarSeries` with:

- `symbol`
- `timeframe`
- `bar_type = "time"`
- `rows`

**Step 3: Keep scope narrow**

Do not add new caching, persistence, async loading, or provider abstractions.

**Step 4: Run targeted source tests**

Run:

```bash
uv run pytest tests/unit/data/adapters -q
```

Expected:

- shipped sources materialize the new dataset consistently

### Task 4: Add the minimal `BacktestEngine` public surface

**Files:**
- Modify: `src/quantleet/research/__init__.py`
- Create or modify: `src/quantleet/research/application/engine.py`
- Modify: `src/quantleet/research/application/__init__.py`
- Modify: `src/quantleet/research/application/backtest.py`
- Modify: `tests/integration/research/test_backtest_runner.py`

**Step 1: Add the engine type**

Implement a narrow `BacktestEngine` that owns:

- `initial_cash`
- `costs`

Keep the public constructor small. Do not add optimizer, broker, portfolio, or generic runtime abstractions.

**Step 2: Add `run(...)`**

Implement:

- `run(bars=..., strategy=...)`
- `run(source=..., strategy=...)`

Rules:

- exactly one of `bars` or `source` must be provided
- `strategy` is a strategy instance
- invalid combinations fail clearly

**Step 3: Reuse the existing kernel**

Internally route through the current backtest path rather than duplicating the kernel loop.

**Step 4: Remove `run_backtest(...)` from the public surface**

Remove the public free-function entry so users and future agents have one canonical execution path.

If an internal helper remains inside `backtest.py`, keep it private and inaccessible from `quantleet.research`.

**Step 5: Run targeted tests**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py tests/smoke/local/test_public_imports.py -q
```

Expected:

- the new engine tests pass or fail only on remaining docs gaps

### Task 5: Remove hidden source-metadata assumptions

**Files:**
- Modify: `src/quantleet/research/application/engine.py`
- Modify: `tests/integration/research/test_backtest_runner.py`

**Step 1: Add failing tests for the approved metadata rule**

Pin the approved behavior:

- `source` path works because `source.load()` returns `BarSeries`
- engine does not reach into undeclared source attributes such as `source.symbol`
- engine accepts only `BarSeries` whose `bar_type == "time"`
- engine does not expose a separate public `bar_type` knob in this slice

**Step 2: Implement the simplest coherent rule**

Use the materialized dataset as the sole metadata carrier for execution.

The engine should no longer read hidden source attributes.

**Step 3: Re-run targeted tests**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py -q
```

Expected:

- source-path metadata behavior is explicit and covered

### Task 6: Update canonical docs and examples

**Files:**
- Modify: `docs/product-specs/research-ergonomics.md`
- Modify: `docs/product-specs/backtest-mvp.md`
- Modify: `docs/product-specs/data-ingestion.md`
- Modify: `docs/references/research-ergonomics-quickstart.md`
- Modify: `README.md`
- Modify: `notebooks/research-ergonomics-quickstart.ipynb`
- Modify: `tests/structure/docs/test_research_ergonomics_quickstart.py`
- Modify: `tests/structure/repo/test_repository_entrypoint_docs.py`

**Step 1: Update the specs**

Document:

- `BacktestEngine`
- `TimeBar`
- `BarSeries`
- `run(bars=..., strategy=...)`
- `run(source=..., strategy=...)`
- the removal of the public `run_backtest(...)` entry in favor of the engine path

**Step 2: Update quickstart and README**

Show the new preferred user path with `BacktestEngine`.

Use `TimeBar` / `BarSeries` language consistently; do not describe `source` metadata as implicit object attributes anymore.

**Step 3: Update structure tests**

Assert that the canonical docs reference the new entry point and dataset contract consistently.

**Step 4: Run targeted doc tests**

Run:

```bash
uv run pytest tests/structure/docs/test_research_ergonomics_quickstart.py tests/structure/repo/test_repository_entrypoint_docs.py -q
```

Expected:

- docs and structure checks pass with the new preferred execution surface

### Task 7: Simplify if the new entry layer adds avoidable complexity

**Files:**
- Modify only if needed: `src/quantleet/research/application/engine.py`
- Modify only if needed: `src/quantleet/research/application/backtest.py`
- Modify only if needed: `src/quantleet/data/domain/bars.py`

**Step 1: Do a narrow simplification pass**

If the new engine/dataset boundary made the execution path harder to reason about:

- centralize argument validation
- keep one kernel entry path
- avoid duplicated `source -> dataset -> engine` branching in multiple places

**Step 2: Re-run targeted tests**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py tests/unit/data/domain/test_bars.py tests/structure/docs/test_research_ergonomics_quickstart.py -q
```

Expected:

- behavior unchanged and tests still green

### Task 8: Run full verification

**Files:**
- No additional file changes required unless verification reveals a validated issue

**Step 1: Run repository verification**

Run:

```bash
uv run poe verify
```

Expected:

- all default repository verification checks pass from the current state

**Step 2: If anything fails, fix only validated issues**

Do not bundle unrelated cleanup.

### Task 9: Final review handoff

**Files:**
- No new files required

**Step 1: Request code review**

Use subagents to check:

- `TimeBar` / `BarSeries` contract correctness
- execution contract correctness
- canonical single-entry execution surface correctness
- docs/spec alignment

**Step 2: Request QA review**

Use separate QA agents to confirm:

- the original UX problem is materially improved
- the source/data boundary is less ambiguous than before
- no important regression was introduced

**Step 3: Summarize exact verification evidence**

Report:

- what changed
- validated issues fixed
- QA approvals
- exact commands and results
- remaining non-blocking risks
