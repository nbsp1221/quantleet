# Minimal Binance OHLCV Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add the smallest Binance OHLCV fetch function for spot and USD-M futures.

**Architecture:** Keep the implementation in a single module with a tiny enum, a tiny dataclass, and one function. Use CCXT exchange classes directly and normalize raw rows into typed records.

**Tech Stack:** Python 3.13, ccxt, pytest, mypy, ruff

---

### Task 1: Write the failing tests

**Files:**
- Create: `tests/test_binance.py`

**Step 1:** Write a test that verifies `BinanceMarket.SPOT` selects `ccxt.binance()` and normalizes one OHLCV row.

**Step 2:** Write a test that verifies `BinanceMarket.USDM` selects `ccxt.binanceusdm()` and forwards `end` through `params`.

**Step 3:** Run `uv run pytest tests/test_binance.py -q`.
Expected: fail because the module does not exist yet.

### Task 2: Write the minimal implementation

**Files:**
- Create: `src/quantcraft/binance.py`
- Modify: `src/quantcraft/__init__.py`

**Step 1:** Add `BinanceMarket`.

**Step 2:** Add `OHLCVBar`.

**Step 3:** Add `fetch_binance_ohlcv(...)`.

**Step 4:** Export the new symbols from `quantcraft.__init__`.

### Task 3: Verify the feature and the project gates

**Files:**
- None

**Step 1:** Run `uv run pytest tests/test_binance.py -q`.

**Step 2:** Run `uv run pytest -q`.

**Step 3:** Run `uv run ruff check .`.

**Step 4:** Run `uv run mypy src`.

**Step 5:** Run `uv build`.
