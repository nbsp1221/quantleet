# ccxt Runtime Dependency Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `ccxt` as the latest runtime dependency using `uv` only.

**Architecture:** Keep dependency management canonical through `uv`. Add `ccxt` to `[project].dependencies`, let `uv` refresh `uv.lock`, and verify both packaging metadata and runtime import.

**Tech Stack:** uv, Python 3.13, ccxt

---

### Task 1: Add the runtime dependency

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`

**Step 1:** Run `uv add ccxt`.

**Step 2:** Confirm that `pyproject.toml` now lists `ccxt` under `[project].dependencies`.

**Step 3:** Confirm that `uv.lock` was updated by `uv`.

### Task 2: Verify the environment

**Files:**
- None

**Step 1:** Run `uv run python -c "import ccxt; print(ccxt.__version__)"`.

**Step 2:** Run `uv run pytest -q`.

**Step 3:** Run `uv run ruff check .`.

**Step 4:** Run `uv run mypy src`.

**Step 5:** Run `uv build`.
