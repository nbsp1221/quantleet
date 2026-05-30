# Full Source Mutation Telemetry Experiment

- Date: 2026-05-30
- Task: Run a full `src/quantleet` mutation-testing experiment and collect telemetry for future mutation gate scope decisions.
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Measure rough runtime, mutant volume, and mutation effectiveness when expanding mutation testing beyond the current `trading` target.
- Governing docs:
  - `AGENTS.md`
  - `docs/RELIABILITY.md`
  - `docs/design-docs/agentic-quality-gates.md`
  - `docs/design-docs/architecture-governance.md`
- Why these are governing: The task is a reliability-gate experiment for AI-agent-led test quality, not a product behavior change.
- In-repo scope: Run mutation telemetry against `src/quantleet` and record results in the final report.
- Out-of-repo scope: No remote services or external state changes beyond normal package/tool execution.
- Tier A progression requested: `no`
- Approval record, if required: Not required; experiment only.
- Verification commands:
  - `uv run mutmut run --max-children 4`
  - `uv run mutmut results`
  - `uv run mutmut print-time-estimates`
  - `uv run mutmut export-cicd-stats`
- Success criteria:
  - The experiment reports elapsed time, mutant counts, killed/survived/timeout/error state, and practical signal/noise observations.
  - The report identifies whether full-source mutation is a plausible default gate or should be split by bounded area.
- Out of scope:
  - Fixing tests.
  - Changing mutation configuration permanently.
  - Promoting a hard gate.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The result must distinguish telemetry from policy and must not claim full-source mutation is viable without runtime and survivor evidence.
- Acceptance artifact location: final chat report
- How the generator and evaluator agreed on done before execution: Run the experiment or report the concrete blocker if it cannot complete in the current environment.
- Checks the evaluator will use:
  - Mutmut command outputs and elapsed time.
- Auto-fail conditions:
  - Configuration is permanently changed without user request.
  - Existing user changes are reverted.
  - Mutation survivors are treated as bugs without inspection.

## Generator Work Log

- Planned slice order:
  1. Inspect mutmut CLI/config override behavior.
  2. Run full-source mutation using a temporary configuration approach if possible.
  3. Collect mutmut results, CI stats, and time estimates.
  4. Report findings and recommended next scope.
- Notes:
  - The repository currently configures mutation only for `src/quantleet/trading`.
- Blockers or scope changes:
  - Full `src/quantleet` mutation generation succeeded but the run could not
    collect tests without exclusions because mutmut generated an invalid
    `__init_subclass__` trampoline for strategy configuration classes.
  - Full package test selection also exposed mutmut covered-lines collection
    noise with `matplotlib`/`numpy` plotting tests.
  - A bounded `backtest` core experiment completed after excluding plotting and
    copying `src/quantleet` into the mutant workspace.
  - Follow-up investigation showed that excluding plotting was premature:
    the full `backtest` folder completed when the lane disabled
    `mutate_only_covered_lines` and copied `src/quantleet` into the mutant
    workspace.

## Evaluator Review

- Findings:
  - Full-source mutation is not a viable immediate hard gate with the current
    mutmut/test environment. It needs bounded lanes and explicit excludes for
    tool-noisy areas.
  - Generated full-source mutant volume was 4,880 mutants across 58 files after
    excluding `strategy/config.py` and `strategy/strategy.py`.
  - Full-source mutant distribution by top-level context was: `backtest` 1,934,
    `research` 1,744, `trading` 765, `integrations` 235, `data` 161,
    `strategy` 41.
  - The completed bounded `backtest` core run produced 1,695 mutants: 1,117
    killed and 578 survived, with no timeouts, no suspicious results, and no
    skipped/no-test mutants.
  - The bounded `backtest` core elapsed time was 35.50s wall clock with
    `--max-children 4`; mutmut reported 53.67 mutations/second.
  - Follow-up root-cause isolation found that `tests/unit/backtest` itself
    passes normally, repeated in-process `pytest.main` for the plotting tests
    also passes, and adding `pytest-forked` does not solve the failure because
    collection imports fail before forked test execution.
  - The likely failure mechanism is mutmut's `mutate_only_covered_lines=true`
    coverage pre-pass: mutmut runs coverage in process and then unloads newly
    imported modules from `sys.modules`. This is risky around NumPy/Matplotlib
    C extensions, which are not generally safe to reinitialize in the same
    process.
  - A full `src/quantleet/backtest` lane completed with
    `mutate_only_covered_lines=false`, `also_copy=["src/quantleet"]`, and
    `tests/unit/backtest`: 2,148 mutants, 1,328 killed, 798 survived,
    22 no-test mutants, no suspicious results, no timeouts, and 56.11s wall
    clock with `--max-children 4`.
  - Full-backtest survivor/no-test concentration was highest in
    `backtest/reporting.py`, `backtest/runtime.py`,
    `backtest/strategy_runtime.py`, and `backtest/plotting.py`.
  - The largest survivor clusters were `backtest/reporting.py` and
    `backtest/runtime.py`, which are strong candidates for manual survivor
    triage before any ratchet is proposed.
- Verification evidence:
  - Full-source attempt: `uv run mutmut run --max-children 4` generated 50 files
    before failing test collection on `StrategyConfig.__init_subclass__`.
  - Adjusted full-source attempt: generated 58 files and 4,880 mutants before
    failing on plotting-related `matplotlib`/`numpy` import behavior.
  - Bounded backtest core attempt: `uv run mutmut run --max-children 4` completed
    with 1,117 killed / 578 survived / 1,695 total.
  - `uv run mutmut export-cicd-stats` emitted the same bounded run totals.
  - Full-backtest follow-up attempt: `uv run mutmut run --max-children 4`
    completed with 1,328 killed / 798 survived / 22 no-tests / 2,148 total.
  - Full-backtest follow-up stats were exported with
    `uv run mutmut export-cicd-stats`.
- Final disposition:
  - Complete. Recommend bounded mutation lanes, not immediate full-source
    mutation as a hard gate.
  - Corrected recommendation: `backtest` should not be reduced to a
    plotting-excluded "core" lane solely because of the earlier failure. A full
    `backtest` lane is locally viable if that lane disables covered-line
    filtering. The remaining decision is policy: whether to accept the larger
    mutant volume and no-test mutants, then ratchet survivors after manual
    triage.
