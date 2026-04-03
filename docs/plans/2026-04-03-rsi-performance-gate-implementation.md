# RSI Performance Gate Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Add a benchmark-backed performance regression gate for the canonical
RSI backtest scenario using standard benchmarking tooling and explicit repository
commands.

**Architecture:** Reuse the existing canonical RSI benchmark scenario, move the
mechanical timing gate onto `pytest-benchmark`, and expose it through a separate
repository command surface instead of mixing timing-sensitive checks directly
into the default correctness lane.

**Tech Stack:** Python 3.13, `uv`, `pytest`, `pytest-benchmark`,
`quantcraft`, repo-local `poe`

---

### Task 1: Add The Benchmark Dependency

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add the failing expectation**

Document the required dependency addition in the plan:

- add `pytest-benchmark` to the `dev` dependency group

**Step 2: Verify current environment lacks the benchmark tool**

Run:

```bash
uv run pytest --benchmark-only
```

Expected:

- command fails because the benchmark plugin is not installed

**Step 3: Add the minimal dependency**

Update `pyproject.toml` so the repository dev environment includes
`pytest-benchmark`.

**Step 4: Verify the tool is now available**

Run:

```bash
uv sync
uv run pytest --benchmark-only
```

Expected:

- benchmark-only mode is recognized by pytest

### Task 2: Add The Canonical RSI Benchmark Test

**Files:**
- Create: `tests/fixtures/backtest/binance_usdm_btcusdtusdt_1h_2025.csv`
- Create: `tests/perf/test_rsi_backtest_benchmark.py`
- Optionally create: `tests/perf/support.py`

**Step 1: Write the failing benchmark test**

Create a benchmark test that:

- uses the canonical repository-tracked fixture dataset
- excludes data fetch and load from the timed region
- measures the backtest execution call only
- validates result shape after the benchmark run

The fixture dataset must be:

- stored under `tests/fixtures/backtest/`
- plain `CSV`
- committed to Git
- schema-fixed as `timestamp,open,high,low,close,volume`
- validated for `8760` rows before use

The test should assert:

- first-run and benchmark result are valid
- closed trades remain `118`
- final equity remains `1038523.5766`

**Step 2: Run the perf test to verify the red state**

Run:

```bash
uv run pytest tests/perf/test_rsi_backtest_benchmark.py -q
```

Expected:

- fail because the new benchmark test or supporting fixtures are not fully wired

**Step 3: Implement the minimal benchmark fixture flow**

Build the test around `pytest-benchmark` so setup and timed execution are
separated cleanly.

The setup path should:

- load the CSV fixture into the benchmark input structure before timing starts
- construct the strategy and engine objects outside the measured call when
  possible without changing the meaning of the benchmark
- keep only the backtest execution call inside the timed region

**Step 4: Re-run until green**

Run:

```bash
uv run pytest tests/perf/test_rsi_backtest_benchmark.py -q
```

Expected:

- benchmark test passes and reports runtime stats

### Task 3: Add Threshold-Based Regression Failure

**Files:**
- Modify: `pyproject.toml`
- Optionally create: `pytest.ini` config section or equivalent benchmark config

**Step 1: Define the threshold policy**

Encode the canonical RSI thresholds:

- first-run `< 1.0s`
- steady-state median `< 1.0s`

**Step 2: Add a repo-local perf-check command**

Add a dedicated command such as:

```bash
uv run poe perf-check
```

that runs the benchmark lane with the threshold failure configuration.

**Step 3: Verify threshold behavior**

Run:

```bash
uv run poe perf-check
```

Expected:

- pass when current runtime is within threshold
- fail mechanically if benchmark stats exceed threshold

### Task 4: Document The Performance Gate

**Files:**
- Modify: `AGENTS.md`
- Modify: `docs/RELIABILITY.md`
- Modify: `docs/references/developer-tasks.md`
- Modify: `docs/research/2026-04-02-backtest-throughput-benchmark.md`

**Step 1: Document the command surface**

Explain that:

- `verify` remains the correctness lane
- `perf-check` is the explicit performance-regression lane
- agents working on runtime-sensitive changes must run both

**Step 2: Document the canonical benchmark contract**

State:

- canonical fixture dataset path and schema
- canonical RSI scenario
- threshold values
- why performance checks stay separate from default correctness checks

**Step 3: Verify docs stay consistent**

Run:

```bash
uv run python scripts/repo_check.py
```

Expected:

- repository docs and plan references remain valid

### Task 5: Final Verification

**Files:**
- No new files expected beyond prior tasks

**Step 1: Run the focused benchmark lane**

Run:

```bash
uv run poe perf-check
```

Expected:

- performance gate passes

**Step 2: Run the standard repository lane**

Run:

```bash
uv run poe verify
```

Expected:

- existing correctness lane still passes

**Step 3: Summarize the final contract**

Record:

- benchmark command
- threshold values
- whether the gate passed on the current machine
