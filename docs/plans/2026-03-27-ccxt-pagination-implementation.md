# CCXT Historical Pagination Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add automatic historical pagination to `quantcraft.data.CCXTDataSource` so users can fetch realistic multi-month Binance `ccxt` OHLCV ranges and feed them directly into the current backtest workflow without changing the public `load()` API.

**Architecture:** Keep the public `DataSource -> load() -> typed bars` contract unchanged. Put the pagination loop inside `src/quantcraft/data/adapters/ccxt_source.py`, keep `Exchange.fetch_ohlcv(...)` as the lower-level single-call primitive, and preserve the existing `data -> research` dependency direction. Treat any exploratory notebook work as optional human validation, not as harness-critical infrastructure.

**Tech Stack:** Python 3.13, `ccxt`, `pytest`, current `quantcraft.data` ingestion surface, current `quantcraft.research` backtest path, repository structure checks.

---

### Task 1: Lock the pagination contract with failing unit tests

**Files:**
- Modify: `tests/unit/data/adapters/test_ccxt_source.py`
- Modify: `tests/unit/market_data/test_exchange_fetch_ohlcv.py`
- Reuse: `src/quantcraft/data/adapters/ccxt_source.py`
- Reuse: `src/quantcraft/data/adapters/exchange_backend.py`

**Step 1: Write the failing tests**

Extend `tests/unit/data/adapters/test_ccxt_source.py` so the public contract is pinned before code changes:

- `CCXTDataSource.load()` automatically paginates
- no new public knob such as `paginate=True`
- `limit=` remains a total returned-bar cap, not an exposed page-size control
- duplicate boundary candles are not returned when the provider treats `since` as inclusive
- pagination stops on:
  - an empty page
  - a short final page
  - reaching `end`
  - reaching the requested total `limit`

Also add one guard test in `tests/unit/market_data/test_exchange_fetch_ohlcv.py` that confirms `Exchange.fetch_ohlcv(...)` remains a single-call primitive and does not become pagination-aware.

Suggested test names:

```python
def test_ccxt_source_load_paginates_until_end(...) -> None: ...

def test_ccxt_source_avoids_duplicate_rows_when_since_is_inclusive(...) -> None: ...

def test_ccxt_source_limit_caps_total_rows_not_page_size(...) -> None: ...

def test_exchange_fetch_ohlcv_remains_single_call_primitive(...) -> None: ...
```

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/unit/data/adapters/test_ccxt_source.py tests/unit/market_data/test_exchange_fetch_ohlcv.py -q
```

Expected:
- FAIL because `CCXTDataSource.load()` currently performs only one fetch

**Step 3: Write the minimal implementation**

Only after the tests fail, implement the smallest private helper structure inside `src/quantcraft/data/adapters/ccxt_source.py`:

- keep `CCXTDataSource` as the public type
- keep `load()` as the only public method
- add a private timeframe-to-milliseconds helper
- add a private pagination loop
- treat `limit` as the cap on the final returned sequence

Do not:

- change the public constructor
- add async support
- add retries, cache, persistence, or completeness validation

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/unit/data/adapters/test_ccxt_source.py tests/unit/market_data/test_exchange_fetch_ohlcv.py -q
```

Expected:
- PASS

**Step 5: Commit**

```bash
git add src/quantcraft/data/adapters/ccxt_source.py tests/unit/data/adapters/test_ccxt_source.py tests/unit/market_data/test_exchange_fetch_ohlcv.py
git commit -m "✨ Add CCXT historical pagination loop"
```

### Task 2: Harden paginated bar assembly correctness

**Files:**
- Modify: `src/quantcraft/data/adapters/ccxt_source.py`
- Modify: `tests/unit/data/adapters/test_ccxt_source.py`
- Reuse: `src/quantcraft/data/domain/bars.py`

**Step 1: Write the failing tests**

Add tests that pin correctness of the assembled historical range:

- every returned row is normalized into canonical `data.domain.OHLCVBar`
- returned rows are strictly increasing by timestamp
- rows at or beyond `end` are excluded
- non-advancing provider pages do not silently loop forever or emit duplicates

Suggested test names:

```python
def test_ccxt_source_returns_monotonic_canonical_bars(...) -> None: ...

def test_ccxt_source_excludes_rows_at_or_beyond_end(...) -> None: ...

def test_ccxt_source_rejects_or_breaks_non_advancing_page_sequences(...) -> None: ...
```

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/unit/data/adapters/test_ccxt_source.py -q
```

Expected:
- FAIL on the new correctness assertions

**Step 3: Write the minimal implementation**

In `src/quantcraft/data/adapters/ccxt_source.py`:

- normalize every raw row into `OHLCVBar`
- trim rows outside the requested `[start, end)` range
- deduplicate inclusive overlap by timestamp
- guard against non-advancing cursor movement

Keep these decisions private to the adapter. Do not create a new public validator/helper surface.

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/unit/data/adapters/test_ccxt_source.py -q
```

Expected:
- PASS

**Step 5: Commit**

```bash
git add src/quantcraft/data/adapters/ccxt_source.py tests/unit/data/adapters/test_ccxt_source.py
git commit -m "✨ Harden paginated CCXT bar assembly"
```

### Task 3: Prove paginated ingestion still feeds the backtest path

**Files:**
- Modify: `tests/integration/research/test_backtest_runner.py`
- Reuse: `src/quantcraft/data/adapters/ccxt_source.py`
- Reuse: `src/quantcraft/research/application/backtest.py`

**Step 1: Write the failing integration test**

Add one integration test that:

- monkeypatches the `ccxt` backend to return multiple OHLCV pages
- loads the bars through `CCXTDataSource`
- passes those bars into `run_backtest(...)`
- asserts the resulting summary and trade log are valid

Suggested test name:

```python
def test_backtest_runner_accepts_paginated_ccxt_source_rows(...) -> None: ...
```

Use a minimal strategy:

- one entry after the first eligible bar
- one exit on a later bar

This test is about `data -> research` compatibility, not about strategy richness.

**Step 2: Run the test to verify it fails**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py -q
```

Expected:
- FAIL until the paginated `CCXTDataSource` path is complete

**Step 3: Write the minimal implementation**

Adjust only the production code needed for the integration test. Prefer refining the adapter rather than widening `run_backtest(...)` or the `research` public surface.

**Step 4: Run the test to verify it passes**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_runner.py -q
```

Expected:
- PASS

**Step 5: Commit**

```bash
git add tests/integration/research/test_backtest_runner.py src/quantcraft/data/adapters/ccxt_source.py
git commit -m "✨ Prove paginated data works with backtest"
```

### Task 4: Update current implemented-scope docs without widening the public surface

**Files:**
- Modify: `docs/product-specs/data-ingestion.md`
- Modify: `README.md`
- Modify: `tests/structure/repo/test_repository_entrypoint_docs.py`

**Step 1: Write the failing docs/structure assertions**

Add or extend structure assertions so the docs state the shipped behavior:

- `CCXTDataSource.load()` paginates automatically
- pagination is internal, not a new public option
- `limit` caps the total returned rows
- `load()` returns the best available closed historical bars for the requested range
- Binance via `ccxt` remains the first guaranteed path

Suggested test name:

```python
def test_readme_mentions_paginated_ccxt_ingestion_capability() -> None: ...
```

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/structure/repo/test_repository_entrypoint_docs.py -q
```

Expected:
- FAIL because the docs do not yet mention pagination behavior

**Step 3: Write the minimal implementation**

Update:

- `docs/product-specs/data-ingestion.md`
- `README.md`

Document only the durable behavior:

- automatic pagination is internal to `CCXTDataSource.load()`
- no public pagination control is added
- completeness validation is still out of scope

Do not promote exploratory notebook work into the official harness or product-spec surface.

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/structure/repo/test_repository_entrypoint_docs.py -q
```

Expected:
- PASS

**Step 5: Commit**

```bash
git add docs/product-specs/data-ingestion.md README.md tests/structure/repo/test_repository_entrypoint_docs.py
git commit -m "📝 Document paginated CCXT ingestion"
```

### Task 5: Run the full repository verification lane

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
uv build
```

Expected:
- both PASS

**Step 5: Commit the verified batch**

```bash
git add src/quantcraft/data/adapters/ccxt_source.py tests/unit/data/adapters/test_ccxt_source.py tests/unit/market_data/test_exchange_fetch_ohlcv.py tests/integration/research/test_backtest_runner.py docs/product-specs/data-ingestion.md README.md tests/structure/repo/test_repository_entrypoint_docs.py
git commit -m "✨ Add automatic CCXT historical pagination"
```

### Optional Manual Validation: Ad hoc RSI 30/70 notebook

**Files:**
- Optional create: `notebooks/binance-usdm-rsi-2024-ad-hoc.ipynb`

This is intentionally outside the core harness.

If a human wants a disposable exploratory artifact after the code slice is complete:

- fetch 2024 Binance USDM `BTC/USDT:USDT` `1h` bars through `CCXTDataSource`
- run a simple RSI 30/70 strategy
- render:
  - price chart
  - buy/sell markers
  - equity curve
  - summary metrics such as return, win rate, max drawdown, and profit factor

Do not add this notebook to the required validation lane unless product intent later changes.
