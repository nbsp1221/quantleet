# Agent-First Repository Setup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restructure `quantcraft` into a local-first, agent-legible repository with system-of-record docs, explicit financial safety gates, and mechanical guardrails aligned with the approved design.

**Architecture:** Keep the project as one Python package for now, but add a repository knowledge system, local command surface, and structural checks that enforce domain boundaries and safety tiers. Start with the smallest mechanical rules that protect future growth into backtesting, paper trading, live trading, and quant tooling without overbuilding.

**Tech Stack:** Python 3.13, uv, pytest, mypy, ruff, markdown docs, local scripts

---

### Task 1: Add the repository entrypoint documents

**Files:**
- Create: `AGENTS.md`
- Create: `ARCHITECTURE.md`
- Modify: `README.md`
- Test: `tests/test_repo_docs.py`

**Step 1: Write the failing tests**

Add tests that assert:

- `AGENTS.md` exists and is not empty
- `ARCHITECTURE.md` exists and is not empty
- `README.md` contains a short project description and setup section

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_repo_docs.py -q`
Expected: FAIL because the new docs do not exist or are empty.

**Step 3: Write minimal implementation**

Create:

- `AGENTS.md` with:
  - short repository map
  - standard commands
  - safety-tier summary
  - rule that Tier A domains require stronger human gate
- `ARCHITECTURE.md` with:
  - domain map
  - layer model
  - allowed dependency directions
  - safety-tier definitions
- `README.md` with:
  - project purpose
  - current scope
  - local verification commands

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_repo_docs.py -q`
Expected: PASS

### Task 2: Create the system-of-record docs layout

**Files:**
- Create: `docs/DESIGN.md`
- Create: `docs/PLANS.md`
- Create: `docs/QUALITY_SCORE.md`
- Create: `docs/RELIABILITY.md`
- Create: `docs/SECURITY.md`
- Create: `docs/design-docs/index.md`
- Create: `docs/design-docs/core-beliefs.md`
- Create: `docs/exec-plans/active/index.md`
- Create: `docs/exec-plans/completed/index.md`
- Create: `docs/exec-plans/tech-debt-tracker.md`
- Create: `docs/product-specs/index.md`
- Create: `docs/references/index.md`
- Create: `docs/generated/index.md`
- Test: `tests/test_docs_structure.py`

**Step 1: Write the failing tests**

Add tests that assert all required system-of-record files and directories exist.

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_docs_structure.py -q`
Expected: FAIL because the required docs structure does not exist yet.

**Step 3: Write minimal implementation**

Create the required files with short but concrete content:

- indexes that explain what belongs in each section
- `core-beliefs.md` containing the repository's agent-first golden principles
- `QUALITY_SCORE.md` with an initial grading table
- `RELIABILITY.md` with local verification and reproducibility rules
- `SECURITY.md` with secrets and live-trading safety rules
- `tech-debt-tracker.md` with an initial empty template

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_docs_structure.py -q`
Expected: PASS

### Task 3: Migrate planning conventions into the new structure

**Files:**
- Modify: `docs/plans/`
- Modify: `docs/PLANS.md`
- Modify: `docs/exec-plans/active/index.md`
- Modify: `docs/exec-plans/completed/index.md`
- Test: `tests/test_plan_indexes.py`

**Step 1: Write the failing tests**

Add tests that assert:

- `docs/PLANS.md` indexes the historical plan set
- active/completed plan indexes exist and are linked
- current planning directories are discoverable from the new top-level plan doc

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_plan_indexes.py -q`
Expected: FAIL because plan indexing and migration notes are missing.

**Step 3: Write minimal implementation**

Update the planning docs so that:

- current `docs/plans/` content is indexed
- the repository documents the transition to `docs/exec-plans/active` and `docs/exec-plans/completed`
- historical docs remain discoverable without moving everything in the same batch

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_plan_indexes.py -q`
Expected: PASS

### Task 4: Add the local command surface agents must use

**Files:**
- Create: `scripts/repo_check.py`
- Create: `scripts/notebook_validate.py`
- Create: `scripts/live_smoke.py`
- Modify: `pyproject.toml`
- Modify: `AGENTS.md`
- Test: `tests/test_local_commands.py`

**Step 1: Write the failing tests**

Add tests that assert:

- the repository exposes documented local command entrypoints
- `AGENTS.md` references the standard commands
- command wrappers exist on disk

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_local_commands.py -q`
Expected: FAIL because the command wrappers do not exist yet.

**Step 3: Write minimal implementation**

Add local scripts that provide stable entrypoints for:

- `repo-check`
- `notebook-validate`
- `live-smoke`

Expose them through `pyproject.toml` script entrypoints or a documented equivalent.

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_local_commands.py -q`
Expected: PASS

### Task 5: Add repository structure and document validation checks

**Files:**
- Create: `scripts/check_docs.py`
- Create: `tests/test_repo_checks.py`
- Modify: `scripts/repo_check.py`
- Modify: `AGENTS.md`

**Step 1: Write the failing tests**

Add tests for the repository checks:

- required docs are present
- placeholders such as an empty README fail
- required indexes link to the right sections

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_repo_checks.py -q`
Expected: FAIL because the checks are not implemented yet.

**Step 3: Write minimal implementation**

Implement `scripts/check_docs.py` and wire it into `scripts/repo_check.py`.

The minimal checks should cover:

- missing required docs
- empty or placeholder project metadata
- missing plan/index links

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_repo_checks.py -q`
Expected: PASS

### Task 6: Add structural architecture enforcement

**Files:**
- Create: `scripts/check_architecture.py`
- Create: `tests/test_architecture_rules.py`
- Modify: `ARCHITECTURE.md`
- Modify: `scripts/repo_check.py`

**Step 1: Write the failing tests**

Add tests that assert the architecture checker can:

- load the documented domain and tier rules
- reject forbidden domain crossings
- distinguish Tier A domains from non-Tier A domains

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_architecture_rules.py -q`
Expected: FAIL because no architecture checker exists yet.

**Step 3: Write minimal implementation**

Implement `scripts/check_architecture.py` with a small ruleset:

- define the known domains
- define the Tier A set: `execution`, `risk`, `portfolio`
- define allowed shared modules
- fail when a module path or import violates the current rules

Start with the repository's current structure and document any temporary exemptions explicitly in `ARCHITECTURE.md`.

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_architecture_rules.py -q`
Expected: PASS

### Task 7: Encode safety and reliability policy for financial domains

**Files:**
- Modify: `docs/RELIABILITY.md`
- Modify: `docs/SECURITY.md`
- Create: `docs/product-specs/market-data.md`
- Create: `docs/product-specs/backtest.md`
- Create: `docs/product-specs/paper-trading.md`
- Create: `docs/product-specs/live-trading.md`
- Test: `tests/test_financial_policies.py`

**Step 1: Write the failing tests**

Add tests that assert:

- Tier A domains are named in reliability/security docs
- product spec stubs exist for the first major future domains
- live-trading docs contain explicit human-gate language

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_financial_policies.py -q`
Expected: FAIL because the policy docs and spec stubs are incomplete.

**Step 3: Write minimal implementation**

Fill the policy docs with concrete rules:

- Tier A domains require explicit human approval
- live trading is not agent-autonomous
- secrets handling is repository-defined
- reproducibility expectations are documented for backtests and paper trading

Create minimal product spec stubs so the future domain map is visible in-repo.

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_financial_policies.py -q`
Expected: PASS

### Task 8: Add quality tracking and cleanup scaffolding

**Files:**
- Modify: `docs/QUALITY_SCORE.md`
- Modify: `docs/exec-plans/tech-debt-tracker.md`
- Create: `scripts/update_quality_score.py`
- Create: `docs/design-docs/doc-gardening.md`
- Test: `tests/test_quality_ops.py`

**Step 1: Write the failing tests**

Add tests that assert:

- `QUALITY_SCORE.md` has initial tracked categories
- the tech debt tracker contains a usable template
- the quality update script exists
- doc gardening guidance exists

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_quality_ops.py -q`
Expected: FAIL because these files and checks do not exist yet.

**Step 3: Write minimal implementation**

Add:

- initial quality categories by domain and infrastructure layer
- debt tracker template
- a small script that can rewrite or validate the quality score file
- doc gardening instructions for recurring cleanup

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_quality_ops.py -q`
Expected: PASS

### Task 9: Verify the full repository harness

**Files:**
- None

**Step 1: Run document and structure checks**

Run: `uv run python scripts/repo_check.py`
Expected: PASS

**Step 2: Run the full test suite**

Run: `uv run pytest -q`
Expected: PASS

**Step 3: Run lint checks**

Run: `uv run ruff check .`
Expected: PASS

**Step 4: Run type checks**

Run: `uv run mypy src`
Expected: PASS

**Step 5: Run build verification**

Run: `uv build`
Expected: PASS

**Step 6: Run notebook validation**

Run: `uv run python scripts/notebook_validate.py`
Expected: PASS

### Task 10: Document the local operating loop

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/RELIABILITY.md`

**Step 1: Add the final workflow description**

Document the local-first operating loop:

- plan/spec first
- agent implementation
- local verification
- self-review against docs
- stronger human gate for Tier A domains

**Step 2: Re-run the repository checks**

Run: `uv run python scripts/repo_check.py`
Expected: PASS

**Step 3: Re-run the full gates**

Run:

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`

Expected: PASS
