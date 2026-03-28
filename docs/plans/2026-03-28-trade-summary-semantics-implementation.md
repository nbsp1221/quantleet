# Trade Summary Semantics Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Align `quantcraft` backtest summary metrics with mainstream backtesting-library expectations by reporting trade statistics on closed net trades rather than raw fills.

**Architecture:** Keep the current fill log and matching engine unchanged, but change the summary layer in `research.application.backtest` so user-facing trade statistics are derived from closed long-only trade slices using net PnL after fees. Preserve raw fill information separately via an explicit `total_fills` field instead of overloading `total_trades`.

**Tech Stack:** Python 3.13, existing `quantcraft.research` backtest path, existing `quantcraft.trading` state and fill events, `pytest`, repository docs/specs.

---

### Task 1: Lock the new summary contract with failing tests

**Files:**
- Modify: `tests/integration/research/test_backtest_runner.py`
- Reuse: `src/quantcraft/research/application/backtest.py`

**Step 1: Write the failing tests**

Extend the deterministic research integration tests so they pin the new user-facing contract:

- `summary.total_trades` means closed trades, not fill count
- add `summary.total_fills` for the raw fill count
- `win_rate`, `average_win`, `average_loss`, and `profit_factor` are based on net closed-trade PnL after fees

Update the existing deterministic fixture expectation and add one extra test that explicitly compares:

- gross realized PnL
- total fees
- net closed-trade statistics

Suggested test shapes:

```python
def test_backtest_runner_reports_closed_trade_count_and_total_fills() -> None:
    ...


def test_backtest_runner_trade_statistics_are_net_of_fees() -> None:
    ...
```

For the existing one-entry one-exit deterministic fixture, the pinned expectations should become:

- `total_trades == 1`
- `total_fills == 2`
- `average_win == 3.774`
- `profit_factor == inf`

because gross PnL is `4.0` and total fees are `0.226`.

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py -q
```

Expected:
- FAIL because the current summary still reports fill-count trades and gross-like trade statistics

**Step 3: Write the minimal implementation**

Implement only the minimal summary-shape changes needed for the tests:

- add `total_fills` to `BacktestSummary`
- keep `trade_log` unchanged
- keep the engine and fill generation unchanged

Do not update docs yet in this task.

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py -q
```

Expected:
- PASS

**Step 5: Commit**

```bash
git add src/quantcraft/research/application/backtest.py tests/integration/research/test_backtest_runner.py
git commit -m "✨ Align backtest trade summary semantics"
```

### Task 2: Implement net closed-trade accounting for long-only summary statistics

**Files:**
- Modify: `src/quantcraft/research/application/backtest.py`
- Reuse: `src/quantcraft/trading/domain/state.py`
- Reuse: `src/quantcraft/trading/domain/events.py`
- Test: `tests/integration/research/test_backtest_runner.py`

**Step 1: Write the failing test**

Add a test that proves fee-adjusted trade accounting stays correct when:

- there are multiple buys before a sell, or
- a sell closes only part of the position

Use the existing `OlderLimitThenNewerMarketExitStrategy` or add a purpose-built strategy to pin the intended semantics:

- `total_trades` counts closing trade slices
- `total_fills` counts all fills
- trade stats are derived from net closed-trade PnL, not raw realized PnL

Suggested shape:

```python
def test_backtest_runner_net_trade_stats_handle_partial_or_multi_fill_closes() -> None:
    ...
```

**Step 2: Run the test to verify it fails**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py -q
```

Expected:
- FAIL until the new accounting logic is implemented

**Step 3: Write the minimal implementation**

In `src/quantcraft/research/application/backtest.py`:

- keep the current `trade_log` and `TradingState` contract
- add a private accumulator for open entry-fee inventory
- on `buy` fills:
  - increase the open fee inventory by the entry fee
- on `sell` fills:
  - compute closed gross PnL from the pre-fill average entry price
  - allocate proportional entry fee from the open inventory
  - subtract both allocated entry fee and exit fee
  - append the resulting net closed-trade PnL to the trade-statistics series
- keep `summary.realized_pnl` and `summary.total_fees` as separate top-level accounting fields

Do not refactor `TradingState` or the matching engine in this task.

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py -q
```

Expected:
- PASS

**Step 5: Commit**

```bash
git add src/quantcraft/research/application/backtest.py tests/integration/research/test_backtest_runner.py
git commit -m "✨ Add net closed-trade summary accounting"
```

### Task 3: Update the canonical research/backtest docs to match the new meaning

**Files:**
- Modify: `docs/product-specs/research-ergonomics.md`
- Modify: `docs/product-specs/backtest-mvp.md`
- Modify: `docs/references/research-ergonomics-quickstart.md`
- Modify: `tests/structure/repo/test_repository_entrypoint_docs.py`

**Step 1: Write the failing docs assertions**

Add or extend structure assertions so the docs explicitly state:

- `total_trades` means closed trades
- `total_fills` is the raw fill count
- `win_rate`, `average_win`, `average_loss`, and `profit_factor` are based on net closed-trade PnL

Suggested shape:

```python
def test_current_docs_describe_closed_trade_and_fill_count_summary_terms() -> None:
    ...
```

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/structure/repo/test_repository_entrypoint_docs.py -q
```

Expected:
- FAIL because the docs do not yet state the new semantics

**Step 3: Write the minimal implementation**

Update the current implemented-scope docs so the meaning is explicit and consistent.

Do not add broader portfolio or analytics concepts in this task.

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/structure/repo/test_repository_entrypoint_docs.py -q
```

Expected:
- PASS

**Step 5: Commit**

```bash
git add docs/product-specs/research-ergonomics.md docs/product-specs/backtest-mvp.md docs/references/research-ergonomics-quickstart.md tests/structure/repo/test_repository_entrypoint_docs.py
git commit -m "📝 Document closed-trade summary semantics"
```

### Task 4: Run the full verification lane

**Files:**
- No new files required

**Step 1: Run lint**

Run:

```bash
uv run ruff check .
```

Expected:
- PASS

**Step 2: Run typecheck**

Run:

```bash
uv run mypy src
```

Expected:
- PASS

**Step 3: Run the default test lane**

Run:

```bash
uv run pytest -q
```

Expected:
- PASS

**Step 4: Run repo checks and build**

Run:

```bash
uv run python scripts/repo_check.py
uv run python scripts/notebook_validate.py
uv build
```

Expected:
- all PASS

**Step 5: Commit the verified batch**

```bash
git add src/quantcraft/research/application/backtest.py tests/integration/research/test_backtest_runner.py docs/product-specs/research-ergonomics.md docs/product-specs/backtest-mvp.md docs/references/research-ergonomics-quickstart.md tests/structure/repo/test_repository_entrypoint_docs.py
git commit -m "✨ Align backtest summary metrics with closed trades"
```
