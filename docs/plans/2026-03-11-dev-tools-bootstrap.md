# Dev Tools Bootstrap Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add minimal modern development tooling for this `uv` + Python 3.13 library using `pytest`, `mypy`, and `ruff`.

**Architecture:** Keep all tool configuration in `pyproject.toml` using officially supported sections. Add only the smallest test scaffold needed to make `pytest` meaningful.

**Tech Stack:** uv, pytest, mypy, ruff, Python 3.13

---

### Task 1: Add minimal test scaffold

**Files:**
- Create: `tests/test_import.py`

**Step 1:** Add a minimal import smoke test for the package.

**Step 2:** Run `uv run pytest -q`.
Expected: fail because `pytest` is not installed yet.

### Task 2: Add dev dependencies and tool configuration

**Files:**
- Modify: `pyproject.toml`

**Step 1:** Add a `dev` dependency group with `pytest`, `mypy`, and `ruff`.

**Step 2:** Add minimal official config sections:
- `[tool.pytest.ini_options]`
- `[tool.mypy]`
- `[tool.ruff]`
- `[tool.ruff.lint]`

**Step 3:** Refresh the lockfile with `uv lock`.

### Task 3: Verify the toolchain

**Files:**
- None

**Step 1:** Run `uv run pytest -q`.

**Step 2:** Run `uv run ruff check .`.

**Step 3:** Run `uv run mypy src`.

**Step 4:** Run `uv build`.
