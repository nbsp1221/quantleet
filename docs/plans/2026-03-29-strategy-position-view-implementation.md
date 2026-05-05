# Strategy Position View Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a small read-only `self.position` runtime view to `quantleet.research.Strategy` with the approved public fields `is_open`, `quantity`, and `average_entry_price`.

**Architecture:** Keep canonical mutable state in `trading.domain.state.TradingState`, derive a read-only strategy-facing position view in the `research` runtime layer, and bind that view onto `Strategy` during backtest execution. Do not widen the trading kernel or introduce a second mutable position model.

**Tech Stack:** Python 3.13, dataclasses, pytest, mypy, ruff, repository docs/spec harness

---

### Task 1: Lock the public contract with failing tests

**Files:**
- Modify: `tests/integration/research/test_backtest_runner.py`
- Modify: `tests/structure/docs/test_research_ergonomics_quickstart.py`

**Step 1: Write the failing tests**

Add tests that assert:

- `strategy.position.is_open`, `quantity`, and `average_entry_price` are readable during `on_bar()`
- flat state is `False / 0.0 / 0.0`
- after entry, the view reflects the open long
- after full exit, the view returns to flat values

Also add or adjust a quickstart structure test so the canonical one-position example can use `self.position.is_open` instead of a local boolean.

**Step 2: Run the targeted tests to verify they fail**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py tests/structure/docs/test_research_ergonomics_quickstart.py -q
```

Expected:

- failing assertions for missing `self.position` surface or old quickstart contract

**Step 3: Keep the failing assertions focused**

Do not over-specify account/equity fields or future scope.

**Step 4: Re-run the same targeted tests**

Expected:

- failures remain focused on the missing approved contract

### Task 2: Add the minimal read-only runtime position view

**Files:**
- Create or modify: `src/quantleet/research/application/_runtime.py`
- Modify: `src/quantleet/research/application/strategy.py`
- Modify: `src/quantleet/research/application/backtest.py`

**Step 1: Add a small read-only position view type**

Implement a minimal wrapper or runtime-owned view with exactly:

- `is_open: bool`
- `quantity: float`
- `average_entry_price: float`

Do not add cash, equity, unrealized PnL, or account fields.

**Step 2: Bind the view onto `Strategy`**

Ensure `Strategy.__init__()` has a position object available, but preserve the contract that meaningful reads are documented for `on_bar()`.

**Step 3: Update the runtime**

When the strategy handles a bar, refresh the read-only view from the current trading state before `on_bar()` executes.

**Step 4: Keep the implementation DRY**

Do not duplicate mutable position state in `research`.

**Step 5: Run targeted tests**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py -q
```

Expected:

- the new runtime surface tests pass or fail only on remaining edge cases

### Task 3: Prove increases, partial exits, and flat resets

**Files:**
- Modify: `tests/integration/research/test_backtest_runner.py`

**Step 1: Add edge-case tests**

Add deterministic integration coverage for:

- long increase updates `quantity` and `average_entry_price`
- partial exit preserves `is_open == True`
- full exit returns to `False / 0.0 / 0.0`

**Step 2: Run targeted integration tests**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py -q
```

Expected:

- all position-view behavior is pinned by integration tests

### Task 4: Update canonical docs and examples

**Files:**
- Modify: `docs/product-specs/research-ergonomics.md`
- Modify: `docs/references/research-ergonomics-quickstart.md`
- Modify: `notebooks/research-ergonomics-quickstart.ipynb`
- Modify: `tests/structure/repo/test_repository_entrypoint_docs.py`
- Modify: `tests/structure/docs/test_research_ergonomics_quickstart.py`

**Step 1: Update the product spec**

Document:

- `self.position`
- the approved three fields
- `on_bar()` runtime-view semantics
- flat-state zero defaults

**Step 2: Update the quickstart**

Replace the local `self.in_position` pattern in the canonical one-position example with `self.position.is_open` where the example remains correct under current `buy()` / `sell()` semantics.

**Step 3: Update structure tests**

Make the doc tests assert the new canonical example shape.

**Step 4: Run targeted doc tests**

Run:

```bash
uv run pytest tests/structure/docs/test_research_ergonomics_quickstart.py tests/structure/repo/test_repository_entrypoint_docs.py -q
```

Expected:

- docs and structure checks pass with the new contract

### Task 5: Simplify if the runtime logic becomes harder to reason about

**Files:**
- Modify only if needed: `src/quantleet/research/application/_runtime.py`
- Modify only if needed: `src/quantleet/research/application/backtest.py`

**Step 1: Do a narrow simplification pass**

If the new runtime binding made the code harder to read, simplify locally without changing behavior:

- keep one source of mutable truth
- centralize runtime view refresh
- avoid duplicated conversion code

**Step 2: Re-run targeted tests**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py tests/structure/docs/test_research_ergonomics_quickstart.py -q
```

Expected:

- behavior unchanged, tests still green

### Task 6: Run full verification

**Files:**
- No additional file changes required unless verification reveals a real issue

**Step 1: Run repository verification**

Run:

```bash
uv run ruff check .
uv run mypy src
uv run pytest -q
uv run python scripts/repo_check.py
uv run python scripts/notebook_validate.py
uv build
```

Expected:

- all commands pass from the current state

**Step 2: If anything fails, fix only validated issues**

Do not bundle unrelated cleanup.

### Task 7: Final review handoff

**Files:**
- No new files required

**Step 1: Request code review**

Use subagents to check:

- contract correctness
- runtime correctness
- docs/spec alignment

**Step 2: Request QA review**

Use separate QA agents to confirm:

- the original UX gap is actually closed
- no important regression was introduced

**Step 3: Summarize exact verification evidence**

Report:

- what changed
- validated issues fixed
- QA approvals
- exact commands and results
- remaining non-blocking risks
