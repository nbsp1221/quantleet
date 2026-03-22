# Test Taxonomy And Layout Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reorganize the `quantcraft` test suite into a durable taxonomy where test purpose is obvious, default verification stays deterministic, and live/network-backed validation is separated from the default lane.

**Architecture:** Use a type-first test tree with `unit`, `integration`, `structure`, and `smoke` at the top level. Mirror the source layout inside `unit` and `integration`, keep repository-rule checks under `structure`, and split `smoke` into `local` and `live` so external verification never pollutes the default test path.

**Tech Stack:** Python 3.13, pytest, pytest markers, repository structure checks

---

### Task 1: Introduce the new test directory skeleton

**Files:**
- Create: `tests/unit/.gitkeep`
- Create: `tests/integration/.gitkeep`
- Create: `tests/structure/.gitkeep`
- Create: `tests/smoke/.gitkeep`
- Modify: `README.md`
- Test: `tests/structure/repo/test_test_tree_layout.py`

**Step 1: Write the failing test**

Add a structure test that asserts the top-level taxonomy directories exist:

- `tests/unit`
- `tests/integration`
- `tests/structure`
- `tests/smoke`

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/structure/repo/test_test_tree_layout.py -q`
Expected: FAIL because the directories do not exist yet.

**Step 3: Write minimal implementation**

Create the directories and add a brief note in `README.md` describing the new taxonomy at a high level.

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/structure/repo/test_test_tree_layout.py -q`
Expected: PASS

### Task 2: Move the current market-data unit tests into mirrored unit layout

**Files:**
- Move: `tests/test_exchange.py` -> `tests/unit/market_data/test_exchange_fetch_ohlcv.py`
- Modify: `pyproject.toml`
- Test: `tests/unit/market_data/test_exchange_fetch_ohlcv.py`

**Step 1: Move the file without changing behavior**

Place the existing exchange behavior tests under the mirrored unit path.

**Step 2: Run the moved test**

Run: `uv run pytest tests/unit/market_data/test_exchange_fetch_ohlcv.py -q`
Expected: PASS

**Step 3: Register markers if needed**

Prepare pytest marker configuration for the new taxonomy.

**Step 4: Re-run the moved test**

Run: `uv run pytest tests/unit/market_data/test_exchange_fetch_ohlcv.py -q`
Expected: PASS

### Task 3: Move the import smoke test into smoke/local

**Files:**
- Move: `tests/test_import.py` -> `tests/smoke/local/test_public_imports.py`
- Test: `tests/smoke/local/test_public_imports.py`

**Step 1: Move the file**

Keep the test behavior identical, but place it under the local smoke category.

**Step 2: Run the moved test**

Run: `uv run pytest tests/smoke/local/test_public_imports.py -q`
Expected: PASS

### Task 4: Move repository-rule tests into structure subtrees

**Files:**
- Move: `tests/test_repo_docs.py` -> `tests/structure/repo/test_repository_entrypoint_docs.py`
- Move: `tests/test_docs_structure.py` -> `tests/structure/docs/test_system_of_record_docs.py`
- Move: `tests/test_plan_indexes.py` -> `tests/structure/docs/test_plan_indexes.py`
- Move: `tests/test_repo_checks.py` -> `tests/structure/repo/test_repo_check_contracts.py`
- Move: `tests/test_architecture_rules.py` -> `tests/structure/architecture/test_domain_boundaries.py`
- Move: `tests/test_financial_policies.py` -> `tests/structure/docs/test_financial_policy_docs.py`
- Move: `tests/test_quality_ops.py` -> `tests/structure/repo/test_quality_scaffolding.py`

**Step 1: Move each file into the new subtree**

Preserve behavior while making the test intent visible from the path.

**Step 2: Run the moved structure tests**

Run:

- `uv run pytest tests/structure/repo -q`
- `uv run pytest tests/structure/docs -q`
- `uv run pytest tests/structure/architecture -q`

Expected: PASS

### Task 5: Move command-surface tests into integration

**Files:**
- Move: `tests/test_local_commands.py` -> `tests/integration/commands/test_local_command_entrypoints.py`
- Test: `tests/integration/commands/test_local_command_entrypoints.py`

**Step 1: Move the file**

Keep the assertions intact, but place the command-surface checks under integration.

**Step 2: Run the moved test**

Run: `uv run pytest tests/integration/commands/test_local_command_entrypoints.py -q`
Expected: PASS

### Task 6: Add pytest markers and default execution policy

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/conftest.py`
- Create: `tests/smoke/live/__init__.py`
- Test: `tests/structure/repo/test_pytest_markers.py`

**Step 1: Write the failing test**

Add a structure test that asserts:

- `unit`, `integration`, `structure`, `smoke`, `live`, and `slow` markers are documented in pytest config
- the default repository guidance excludes live tests from the default lane

**Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/structure/repo/test_pytest_markers.py -q`
Expected: FAIL because the markers and policy are not fully configured yet.

**Step 3: Write minimal implementation**

Update pytest config to register the markers and add minimal shared guidance in `tests/conftest.py`.

**Step 4: Re-run the marker test**

Run: `uv run pytest tests/structure/repo/test_pytest_markers.py -q`
Expected: PASS

### Task 7: Add repository enforcement for the new taxonomy

**Files:**
- Modify: `scripts/check_docs.py`
- Modify: `scripts/repo_check.py`
- Create: `tests/structure/repo/test_no_flat_tests.py`

**Step 1: Write the failing test**

Add a structure test that asserts:

- new flat `tests/test_*.py` files are not allowed
- the taxonomy directories are treated as the supported layout

**Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/structure/repo/test_no_flat_tests.py -q`
Expected: FAIL because the repository checker does not enforce the taxonomy yet.

**Step 3: Write minimal implementation**

Extend the repository check logic so it flags new flat root-level test files and recognizes the supported taxonomy.

**Step 4: Re-run the taxonomy enforcement test**

Run: `uv run pytest tests/structure/repo/test_no_flat_tests.py -q`
Expected: PASS

### Task 8: Update repository docs to explain the test taxonomy

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `ARCHITECTURE.md`
- Create: `docs/references/testing.md`

**Step 1: Document the taxonomy**

Explain:

- top-level test categories
- source-mirroring rule for `unit` and `integration`
- purpose-specific rule for `structure` and `smoke`
- default policy that excludes live tests

**Step 2: Add the testing reference**

Create a repository-local testing reference that future agents should follow when adding tests.

**Step 3: Re-run repository structure checks**

Run: `uv run repo-check`
Expected: PASS

### Task 9: Run the full fresh verification set

**Files:**
- None

**Step 1: Run the full suite**

Run: `uv run pytest -q`
Expected: PASS

**Step 2: Run lint**

Run: `uv run ruff check .`
Expected: PASS

**Step 3: Run type checks**

Run: `uv run mypy src`
Expected: PASS

**Step 4: Run build**

Run: `uv build`
Expected: PASS

**Step 5: Run repository checks**

Run: `uv run repo-check`
Expected: PASS

### Task 10: Validate test selection behavior

**Files:**
- None

**Step 1: Run unit-only and structure-only examples**

Run:

- `uv run pytest tests/unit -q`
- `uv run pytest tests/structure -q`

Expected: PASS

**Step 2: Confirm live tests remain explicit-only**

Run: `uv run pytest tests/smoke/live -q`
Expected: either no tests collected yet or PASS when future live tests exist, but never part of the default lane.
