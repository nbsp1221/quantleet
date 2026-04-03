# Backtest Throughput Benchmark Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to execute this plan task-by-task.

**Goal:** Build a fair benchmark harness for the canonical RSI backtest scenario,
measure `quantcraft` and selected comparator libraries, and turn the findings
into a concrete runtime target for the next optimization slice.

**Architecture:** Keep the benchmark input fixed, measure only the backtest
execution path, and separate direct event-style comparisons from
vectorized-reference comparisons. Use `/tmp` for comparator installs and scripts,
and keep repository-local artifacts focused on the `quantcraft` baseline and the
final report.

**Tech Stack:** Python 3.13, `uv`, `quantcraft`, `/tmp` comparator environments,
`backtesting.py`, `backtrader`, `vectorbt`, `pybroker`

---

## Steps

1. Establish the benchmark input

- extract or materialize the canonical `2025` RSI scenario dataset into a stable
  local artifact
- verify bar count and timestamp ordering
- keep data-loading time outside the timed backtest window

2. Add a repository-local `quantcraft` benchmark

- create a reproducible script that runs the canonical RSI strategy
- measure first-run and repeated steady-state backtest runtime
- record result-shape fields next to runtime

3. Add comparator harnesses in `/tmp`

- create one comparator root under `/tmp`
- install only the selected libraries needed for this batch
- implement one benchmark script per library using the shared dataset
- record semantic mismatches instead of hiding them

4. Run an adversarial fairness review

- have an isolated reviewer inspect whether any comparator is being measured
  unfairly
- correct benchmark methodology issues before treating the numbers as evidence

5. Summarize and set a target

- produce a result table with first-run runtime, steady-state median runtime,
  and semantic notes
- recommend a concrete `quantcraft` runtime target for the RSI optimization slice

## Verification

- `uv run poe verify`
- execute the repository-local `quantcraft` benchmark script
- execute the comparator benchmark scripts in `/tmp`
- retain the raw timing output used in the final summary
