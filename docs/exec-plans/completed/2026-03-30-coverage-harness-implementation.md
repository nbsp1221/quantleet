# Coverage Harness Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a repository-enforced coverage harness so AI agents must keep `src/quantleet` line coverage at or above 90% and `src/quantleet/trading/domain/*` line coverage at 100%.

**Architecture:** Treat coverage as a repo-local verification guardrail, not as a substitute for contract tests or structure checks. Measure only shipped source code under `src/quantleet`, keep tests/scripts/notebooks out of the reported threshold, and enforce the approved risk-based policy through the same `scripts/` + `poe` command surface that already drives lint, typecheck, tests, build, and repo checks.

**Tech Stack:** Python 3.13, `coverage.py`, `pytest`, `poethepoet`, repo-local harness scripts under `scripts/`, structure tests under `tests/structure/`.

## Lifecycle

- status: completed
- completed_on: 2026-03-30

## Current Status

- Slice 1: complete
- Slice 2: complete
- Slice 3: complete
- Slice 4: complete
- Slice 5: complete
- Slice 6: complete
- Slice 7: complete

## Approved Policy

- Global source coverage gate:
  - target: `src/quantleet`
  - metric: line coverage
  - threshold: `>= 90%`
- Tier A core coverage gate:
  - target: `src/quantleet/trading/domain/*`
  - metric: line coverage
  - threshold: `== 100%`
- Out of scope for this slice:
  - branch coverage gates
  - patch coverage
  - per-file thresholds outside `trading/domain`
  - notebook/test/script coverage
  - CI-only coverage systems outside the repo-local harness

## Success Criteria

This slice is complete only when all of the following are true:

1. `coverage.py` is a repo-managed dev dependency and the repository has a documented, reproducible source-only coverage command.
2. Coverage measurement excludes non-source code from threshold evaluation and reports on `src/quantleet` only.
3. A repo-local harness command fails when:
   - global `src/quantleet` line coverage is below `90%`, or
   - any file under `src/quantleet/trading/domain/` is below `100%` line coverage.
4. `uv run poe verify` includes the coverage gate.
5. Repository docs describe the coverage policy and command surface clearly enough that future agents do not need to guess how coverage is enforced.
6. Structure tests pin the command surface and threshold policy so future drift is caught mechanically.
7. Full repository verification passes from the current state after the harness is added.

---

### Task 1: Lock the approved coverage policy with failing structure tests

**Files:**
- Create: `tests/structure/repo/test_coverage_harness.py`
- Modify: `tests/structure/repo/test_poe_task_contracts.py`
- Reuse: `pyproject.toml`
- Reuse: `docs/RELIABILITY.md`

**Step 1: Write the failing tests**

Add structure tests that assert:

- the repository exposes a dedicated coverage command through the `poe` task surface
- `verify` includes the coverage task
- the approved thresholds are represented as:
  - global source coverage `>= 90`
  - `trading/domain` file coverage `== 100`
- the measured scope is source-only and targets `src/quantleet`

Suggested test names:

```python
def test_poe_verify_includes_coverage_gate() -> None: ...

def test_repository_defines_approved_coverage_thresholds() -> None: ...

def test_coverage_harness_targets_source_only() -> None: ...
```

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py -q
```

Expected:

- FAIL because the repository currently has no coverage harness

**Step 3: Keep the assertions narrow**

Do not over-specify implementation details such as whether the harness uses `coverage run`, `coverage json`, or a dedicated helper script. Pin only the policy, command surface, and scope.

**Step 4: Re-run the same tests**

Expected:

- failures stay focused on the missing harness contract

### Task 2: Add the repo-local coverage command surface

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `docs/RELIABILITY.md`

**Step 1: Add the minimal dependency and command entries**

Update the dev dependency set to include `coverage.py`.

Add a dedicated Poe task, for example:

- `uv run poe coverage`

Ensure `uv run poe verify` includes the new coverage gate.

**Step 2: Document the command surface**

Update:

- `README.md`
- `AGENTS.md`
- `docs/RELIABILITY.md`

so agents and humans see coverage as part of the standard local verification lane.

**Step 3: Run targeted structure tests**

Run:

```bash
uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py -q
```

Expected:

- structure tests now pass or fail only on the still-missing enforcement logic

### Task 3: Implement source-only coverage measurement and threshold enforcement

**Files:**
- Create: `scripts/coverage_check.py`
- Modify: `pyproject.toml`
- Reuse: `src/quantleet/`

**Step 1: Write the failing harness test**

Extend `tests/structure/repo/test_coverage_harness.py` so it also asserts:

- the coverage gate uses a repo-local script under `scripts/` or an equally explicit repo-local command path
- the gate enforces:
  - total `src/quantleet` line coverage `>= 90%`
  - per-file `src/quantleet/trading/domain/*` line coverage `== 100%`

Suggested additional test names:

```python
def test_coverage_check_enforces_global_source_threshold() -> None: ...

def test_coverage_check_enforces_trading_domain_full_coverage() -> None: ...
```

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/structure/repo/test_coverage_harness.py -q
```

Expected:

- FAIL because the enforcement logic does not exist yet

**Step 3: Implement the minimal coverage harness**

Add `scripts/coverage_check.py` that:

- runs or reads `coverage.py` results for `src/quantleet`
- evaluates source-only line coverage
- fails with a clear error if:
  - total source coverage is below `90%`
  - any `src/quantleet/trading/domain/*.py` file is below `100%`
- emits actionable remediation text for future agents

Keep the script simple and repo-local. Do not add CI-specific abstractions, hosted upload integrations, or patch-coverage logic.

**Step 4: Wire the Poe task to the script**

Ensure `uv run poe coverage` executes the coverage gate through the documented repo-local surface.

**Step 5: Run targeted tests**

Run:

```bash
uv run pytest tests/structure/repo/test_coverage_harness.py -q
uv run poe coverage
```

Expected:

- PASS

### Task 4: Make the coverage harness explainable and durable

**Files:**
- Modify: `docs/QUALITY_SCORE.md`
- Modify: `docs/RELIABILITY.md`
- Modify: `README.md`

**Step 1: Update reliability and quality docs**

Document:

- that coverage is now a standard verification guardrail
- that source-only line coverage is the measured scope
- that the repository uses a risk-based threshold policy
- that `trading/domain` is held to a stricter bar because it is Tier A kernel code

Refresh `docs/QUALITY_SCORE.md` if the new verification surface materially changes the repository quality state.

**Step 2: Keep the docs concise**

Do not turn docs into a testing manifesto. Agents only need:

- the policy
- the command
- the reason the stricter Tier A rule exists

**Step 3: Run docs/repo tests**

Run:

```bash
uv run pytest tests/structure/docs tests/structure/repo -q
```

Expected:

- PASS

### Task 5: Verify the current repository meets the new bar

**Files:**
- Modify only if the new harness reveals real coverage gaps

**Step 1: Run the new coverage gate**

Run:

```bash
uv run poe coverage
```

Expected:

- PASS from the current repository state

If it fails:

- inspect the uncovered lines
- add the smallest missing tests needed to satisfy the approved policy
- do not broaden the slice or refactor unrelated code

### Task 6: Run full repository verification

**Files:**
- No additional file changes required unless verification reveals a real issue

**Step 1: Run the full verification bundle**

Run:

```bash
uv run ruff check .
uv run mypy src
uv run pytest -q
uv run poe coverage
uv build
uv run python scripts/repo_check.py
uv run python scripts/notebook_validate.py
```

Expected:

- all commands pass from the current state

**Step 2: Fix only validated failures**

Do not bundle unrelated cleanup.

### Task 7: Final review handoff

**Files:**
- No new files required

**Step 1: Request review**

Use reviewer agents to check:

- threshold policy matches the approved human decision
- source-only scope is enforced correctly
- the harness does not accidentally count tests/scripts/notebooks toward the threshold

**Step 2: Request QA**

Use QA agents to confirm:

- `verify` now includes coverage
- failure messages are legible to future agents
- the current repository actually passes the new bar

**Step 3: Summarize exact verification evidence**

Report:

- what changed
- validated issues fixed
- QA approvals
- exact commands and results
- remaining non-blocking risks
