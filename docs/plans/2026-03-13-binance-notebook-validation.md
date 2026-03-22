# Binance Notebook Validation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add and execute one notebook that demonstrates Binance spot and USD-M OHLCV fetching with charts.

**Architecture:** Keep the notebook fully user-facing: import from `quantcraft`, fetch both datasets, convert rows to plotting inputs, and render simple close-price charts. Use `nbclient` to execute the notebook as a real validation artifact.

**Tech Stack:** Python 3.13, quantcraft, ccxt, matplotlib, nbformat, nbclient

---

### Task 1: Add notebook execution dependencies

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`

**Step 1:** Add `matplotlib`, `nbformat`, and `nbclient` to the dev dependency group using `uv`.

**Step 2:** Confirm the lockfile is updated by `uv`.

### Task 2: Create the validation notebook

**Files:**
- Create: `notebooks/binance-spot-usdm-validation.ipynb`

**Step 1:** Add cells that import `fetch_binance_ohlcv` and `BinanceMarket`.

**Step 2:** Fetch spot `BTC/USDT` `1h` `limit=200`.

**Step 3:** Fetch USD-M `BTC/USDT` `1h` `limit=200`.

**Step 4:** Build timestamp and close-price series.

**Step 5:** Render two charts with `matplotlib`.

### Task 3: Execute and verify

**Files:**
- Modify: `notebooks/binance-spot-usdm-validation.ipynb`

**Step 1:** Execute the notebook with `nbclient`.

**Step 2:** Confirm both outputs show non-empty row counts.

**Step 3:** Confirm the executed notebook is saved with outputs.

**Step 4:** Run project verification:
- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`
