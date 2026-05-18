# Coverage Regression Gate Implementation Plan

- Date: 2026-05-18
- Task: Add a baseline-relative coverage regression gate to the default
  `check` path.
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Implement a local coverage regression gate that fails `uv run poe check`
  when current working-tree coverage drops more than `0.25` percentage points
  below the committed coverage baseline.
- Governing docs:
  - `AGENTS.md`
  - `docs/RELIABILITY.md`
  - `docs/references/testing.md`
  - `docs/references/coverage-regression-gate-research.md`
  - `docs/plans/2026-05-17-diff-coverage-gate-plan.md`
  - `docs/plans/2026-05-17-check-command-gate-alignment-plan.md`
  - `docs/plans/2026-05-18-coverage-regression-gate-experiment-plan.md`
- Why these are governing:
  - `AGENTS.md` defines the one-command local gate expectation.
  - `docs/RELIABILITY.md` defines coverage as a local hard gate.
  - `docs/references/testing.md` defines the repository test command surface.
  - The research and experiment docs define the threshold, performance
    constraints, and decision to include this gate in `check`.
- In-repo scope:
  - Add a committed coverage baseline JSON artifact.
  - Add a repo-local script for coverage regression checks and safe baseline
    updates.
  - Add the regression gate to `coverage-gates`, and therefore to `check`.
  - Add a baseline update/bootstrap command for explicit maintenance.
  - Update repo-check required task contracts and docs.
  - Add structure/unit tests for baseline behavior, pass/fail behavior,
    anti-lowering behavior, and command wiring.
- Out-of-repo scope:
  - No hosted coverage service integration.
  - No Codecov or GitHub-only dependency.
  - No change to the existing `90%` full-project floor.
  - No change to the existing `80%` changed-lines floor.
  - No production implementation that reruns pytest twice for current coverage.
- Tier A progression requested: `no`
- Approval record, if required: not required.
- Verification commands:
  - `uv run poe format-check`
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py -q`
  - `uv run pytest tests/unit/scripts/test_coverage_baseline.py -q`
  - `uv run poe repo-check`
  - `uv run poe coverage-gates`
  - `uv run poe check`
- Success criteria:
  - `uv run poe check` includes the regression gate through `coverage-gates`.
  - The regression gate reuses existing `.coverage` data and does not run pytest
    again for current coverage.
  - The baseline JSON artifact is committed and reviewable.
  - Check mode reads the local working-tree baseline artifact.
  - Coverage drop of `<= 0.25` percentage points passes.
  - Coverage drop of `> 0.25` percentage points fails with a clear message.
  - `coverage-baseline` automatically raises `.coverage-baseline.json` when
    current coverage improves.
  - `coverage-baseline` never lowers `.coverage-baseline.json`.
  - Existing full-project and changed-lines coverage gates remain intact.
- Out of scope:
  - Implementing an automatic baseline-lowering bypass in `check`.
  - Using local cache artifacts as the source of truth.
  - Replacing `diff-cover`.

## Implementation Goal

Add a third coverage gate:

```text
base_coverage = coverage total recorded in committed baseline artifact
head_coverage = coverage total for current working tree
drop = base_coverage - head_coverage
fail if drop > 0.25
```

The gate must run inside the default `check` command so agents cannot forget it.
The implementation must avoid an extra pytest run by consuming the same
coverage data that `coverage-gates` already produced.

## Current Codebase Facts

Current command surface in `pyproject.toml`:

- `coverage` runs `coverage run -m pytest -q` and `coverage report -m`
- `coverage-diff` runs pytest under coverage and then runs `diff-cover`
- `coverage-gates` runs pytest once under coverage, then:
  - `coverage report -m`
  - `coverage xml -o coverage.xml --fail-under=0`
  - `diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80`
- `check` runs `coverage-gates` and therefore is the correct integration point

Current coverage settings:

- `tool.coverage.report.fail_under = 90`
- `tool.coverage.run.branch = true`
- `tool.coverage.run.source = ["quantleet"]`

Existing reusable paths:

- `src/quantleet/_repo_tools.py`
  - owns repo contract checks and required Poe task lists
- `scripts/repo_check.py`
  - runs repo and architecture contract checks
- `tests/structure/repo/test_coverage_harness.py`
  - owns coverage command contract tests
- `tests/structure/repo/test_poe_task_contracts.py`
  - owns Poe task surface tests
- `tests/structure/repo/test_repo_check_contracts.py`
  - owns repo-check fixture coverage for Poe tasks

## Proposed Files

Add:

- `.coverage-baseline.json`
  - committed baseline artifact for the coverage regression gate
- `scripts/coverage_baseline.py`
  - CLI for baseline-relative coverage regression checks and safe baseline
    updates
- `tests/unit/scripts/test_coverage_baseline.py`
  - unit tests for parsing, baseline source selection, threshold comparison,
    update behavior, and command construction

Modify:

- `pyproject.toml`
  - add `coverage-baseline`
  - add `coverage-baseline-update`
  - append `coverage-baseline` to `coverage-gates`
- `src/quantleet/_repo_tools.py`
  - add `coverage-baseline` and `coverage-baseline-update` to
    `REQUIRED_POE_TASKS`
- `tests/structure/repo/test_coverage_harness.py`
  - assert `coverage-gates` includes the regression gate after XML/diff-cover
- `tests/structure/repo/test_poe_task_contracts.py`
  - assert both tasks exist and are documented where required
- `tests/structure/repo/test_repo_check_contracts.py`
  - update inline Poe fixtures
- `docs/RELIABILITY.md`
  - document the regression gate, threshold, and baseline update policy
- `docs/references/testing.md`
  - document the new coverage gate role
- `AGENTS.md`
  - add command surface entries if needed

## Baseline Artifact

Path:

```text
.coverage-baseline.json
```

Shape:

```json
{
  "schema_version": 1,
  "baseline_commit": "52c8d6cb16712872e687ccf19022e16c2bbc0a94",
  "coverage_percent": 90.754001,
  "allowed_drop": 0.25,
  "coverage_tool": "coverage.py",
  "coverage_command": "coverage run -m pytest -q",
  "coverage_run_branch": true,
  "coverage_run_source": ["quantleet"]
}
```

The baseline artifact is the source of truth. Local cache files are not used for
pass/fail decisions.

Why a committed artifact:

- no cold-cache coverage run is needed inside `check`
- the threshold baseline is visible in review
- baseline changes are versioned with the code that justified them
- agents cannot forget a separate command because `check` still owns the gate

Why this path:

- `pytest-coverage-gate` documents a root-level `.coverage-baseline` file and
  recommends committing it to version control
- Kubeflow Pipelines uses a root-level `.coverage-baseline.json` for its
  coverage baseline script
- Wormhole uses a package-root `.coverage-baseline` for its coverage-check
  tool
- a root-level dotfile matches the observed coverage-baseline convention better
  than an invented `quality/coverage-baseline.json` directory path
- JSON is retained because coverage.py can emit JSON and this project needs
  structured metadata around the measured percentage

## External Practice Check

Web research supports the committed-baseline/ratchet direction.

Relevant examples:

- `pytest-coverage-gate` is a Python pre-commit hook that reads coverage XML and
  compares it with a baseline file. Its documentation recommends committing
  `.coverage-baseline` to version control, blocks regressions, and updates the
  baseline when coverage improves. As of this review, the GitHub repository has
  `0` stars, so it does not satisfy the project's minimum `100` star threshold
  for adopting a new quality-gate dependency.
- Kubeflow Pipelines uses `frontend/scripts/coverage-baseline.mjs` and a
  root-level `.coverage-baseline.json` for capture/compare coverage baseline
  workflows. The repository has more than `4,000` GitHub stars, so it is strong
  evidence for the `coverage-baseline` naming pattern and dotfile baseline
  artifact.
- Wormhole uses a `scripts/coverage-check/` tool and a package-root
  `.coverage-baseline` artifact. The repository has more than `1,800` GitHub
  stars, so it is strong evidence for storing committed coverage baselines next
  to the package/tooling boundary and managing checks through repository
  scripts.
- `jest-coverage-ratchet` uses a similar ratchet idea for Jest. It compares the
  current coverage summary against configured thresholds and updates thresholds
  upward when current coverage improves.
- `diff-cover` remains the right tool for changed-line coverage. Its own
  documentation frames diff coverage as a code-review accountability gate for
  touched lines, which is complementary to this project-wide regression gate.
- Coverage evolution research shows that patch coverage and project coverage
  capture different signals. High patch coverage does not necessarily imply
  improved non-patch coverage, and steady aggregate coverage can hide line-level
  changes. This supports keeping all three gates: full-project floor,
  changed-line coverage, and baseline-relative regression.

Conclusion:

- a committed baseline artifact is a known, practical strategy
- automatic upward ratcheting is common
- automatic downward ratcheting is risky and should not be the default
- no known Python library found in this review satisfies the minimum `100` star
  adoption threshold while matching this exact policy
- Quantleet should directly implement the small repo-local script while
  following observed conventions:
  - baseline artifact: `.coverage-baseline.json`
  - Python helper: `scripts/coverage_baseline.py`, matching this repository's
    existing snake_case script naming
  - Poe tasks: `coverage-baseline` and `coverage-baseline-update`, matching the
    repository's hyphenated command naming

## Check Algorithm

Default command:

```bash
uv run python scripts/coverage_baseline.py check \
  --baseline .coverage-baseline.json \
  --allowed-drop 0.25 \
  --current-json coverage-baseline-current.json
```

Steps:

1. Confirm `.coverage` exists. If missing, fail with an operational error that
   tells the caller to run through `coverage-gates`.
2. Generate current coverage JSON from existing coverage data:

   ```bash
   coverage json -o coverage-baseline-current.json
   ```

3. Read baseline JSON from the local working tree file:

   ```text
   .coverage-baseline.json
   ```
4. Read `totals.percent_covered` from the current JSON.
5. Compute:

   ```python
   drop = baseline["coverage_percent"] - current_percent
   ```

6. Pass if `drop <= 0.25`; fail otherwise.
7. Delete `coverage-baseline-current.json` unless a debug flag requests
   keeping it.

Why read the local baseline file:

- matches the project intent that the baseline is a committed file managed with
  normal code changes
- keeps the algorithm simple and deterministic
- avoids extra Git object reads, branch comparisons, or hidden cache state
- ratchets upward inside `coverage-baseline` itself, so the default `check`
  path records improvements without relying on an agent to remember a second
  command

## Baseline Check And Ratchet Algorithm

Default command:

```bash
uv run python scripts/coverage_baseline.py check \
  --baseline .coverage-baseline.json \
  --allowed-drop 0.25 \
  --current-json coverage-baseline-current.json
```

Steps:

1. Confirm `.coverage` exists.
2. Generate current JSON from existing `.coverage`.
3. Read the local working-tree baseline JSON.
4. If current coverage is higher than the baseline, update
   `.coverage-baseline.json` and pass.
5. If current coverage is equal to the baseline, leave the baseline unchanged
   and pass.
6. If current coverage is lower than the baseline but within the allowed
   `0.25` percentage point drop, leave the baseline unchanged and pass.
7. If current coverage is lower than the baseline by more than `0.25`
   percentage points, fail.
8. Print a clear message explaining whether the baseline was raised,
   unchanged, tolerated, or failed.

This matches the ratchet convention: coverage gains become the new floor
automatically, but coverage losses never lower the floor automatically.

## Explicit Baseline Update Command

Default command:

```bash
uv run python scripts/coverage_baseline.py update \
  --baseline .coverage-baseline.json \
  --current-json coverage-baseline-current.json
```

This command exists for initial bootstrap and explicit maintenance. It uses the
same one-way rule as `check`: create or raise the baseline from current
coverage, but do not lower an existing baseline.

Lowering policy:

- the first implementation should not expose a normal baseline-lowering command
- if lowering is genuinely needed, use a documented plan and a manual baseline
  edit or a future explicitly named command
- reviewers should treat baseline lowering as a quality policy change

## Coverage Value

Read the current total from:

```python
json_data["totals"]["percent_covered"]
```

This is the same coverage.py combined total used by the current report with
branch measurement enabled.

## Output And Exit Codes

Check output should include:

- baseline source: `.coverage-baseline.json`
- baseline coverage
- current coverage
- drop
- allowed drop
- pass/fail/raised

Failure example:

```text
coverage regression failed: base=90.754001%, current=89.826975%, drop=0.927026 percentage points, allowed=0.25
```

Exit codes:

- `0`: pass, tolerated drop, or successful upward baseline update
- `1`: operational error, such as missing `.coverage` or invalid JSON
- `2`: coverage regression failure
- `3`: baseline update refused because it would lower the baseline

## Poe Task Design

Add:

```toml
"coverage-baseline" = {
  cmd = "uv run python scripts/coverage_baseline.py check --baseline .coverage-baseline.json --allowed-drop 0.25 --current-json coverage-baseline-current.json",
  help = "Fail on coverage regression and automatically raise the committed baseline on improvement"
}

"coverage-baseline-update" = {
  cmd = "uv run python scripts/coverage_baseline.py update --baseline .coverage-baseline.json --current-json coverage-baseline-current.json",
  help = "Bootstrap or explicitly raise the committed coverage baseline"
}
```

Update `coverage-gates` sequence:

```toml
"coverage-gates" = {
  sequence = [
    { cmd = "coverage erase" },
    { cmd = "coverage run -m pytest -q" },
    { cmd = "coverage report -m" },
    { cmd = "coverage xml -o coverage.xml --fail-under=0" },
    { cmd = "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80" },
    "coverage-baseline",
  ],
  help = "Run tests once and enforce full-project, changed-lines, and regression coverage gates"
}
```

`check` does not need a direct change because it already calls
`coverage-gates`.

## Test Plan

Unit tests for `scripts/coverage_baseline.py`:

- computes `drop` correctly
- passes when drop is exactly `0.25`
- fails when drop is greater than `0.25`
- treats negative drop as pass
- reads `totals.percent_covered`
- reads baseline JSON from the local working-tree artifact in check mode
- detects missing `.coverage`
- does not call `coverage run` for current coverage
- check mode raises the baseline when current coverage improves
- check mode leaves the baseline unchanged when current coverage is equal
- check mode leaves the baseline unchanged for a tolerated drop
- update mode can create or raise the baseline for explicit maintenance
- update mode does not lower the baseline by default
- returns exit code `2` for regression failure
- returns exit code `3` for refused baseline lowering

Structure tests:

- `coverage-baseline` exists as a Poe task
- `coverage-baseline-update` exists as a Poe task
- `coverage-gates` includes `coverage-baseline`
- `coverage-gates` still runs `coverage run -m pytest -q` exactly once
- `coverage-gates` still runs `coverage report -m`
- `coverage-gates` still runs `coverage xml`
- `coverage-gates` still runs `diff-cover`
- `check` still calls `coverage-gates`, not separate coverage tasks
- repo-check requires `coverage-baseline` and `coverage-baseline-update`

Integration or smoke test:

- use a small temporary fake repo only if cheap
- simulate committed baseline JSON and current coverage JSON
- confirm command exits `0` for pass, `2` for fail, and `3` for refused
  lowering
- avoid running the full real pytest suite inside unit tests

Full verification:

- `uv run poe coverage-gates`
- `uv run poe coverage-baseline-update`
- `uv run poe check`

## Performance Expectations

From the experiment:

- normal current coverage run: about `45s`
- committed baseline comparison: about `0.5s`

Expected production behavior:

- every `check`: about `+0.5s`
- no extra pytest run
- no cold-cache penalty

This is faster and simpler than the cache-based plan because the baseline is
reviewed and committed rather than computed locally.

## Migration And Compatibility

- Existing `coverage`, `coverage-diff`, and `coverage-gates` remain available.
- Existing thresholds stay unchanged:
  - full-project coverage: `90%`
  - changed-lines coverage: `80%`
  - regression allowed drop: `0.25` percentage points
- `.coverage-baseline.json` becomes a tracked quality policy artifact.
- Normal `check` automatically raises the baseline when current coverage
  improves and never lowers it.
- Explicit update/bootstrap only creates or raises the baseline; it never lowers
  an existing baseline.
- Initial bootstrap creates the committed baseline artifact before the gate is
  considered fully enforced.

## Risks And Mitigations

- Risk: an agent manually lowers the baseline file to pass.
  - Mitigation: normal check/update modes never lower the baseline; reviewers
    treat manual baseline lowering as an explicit policy change.
- Risk: baseline JSON becomes stale after tool/config changes.
  - Mitigation: include coverage settings metadata and update the baseline in
    the same change that intentionally changes coverage policy.
- Risk: intentional coverage policy changes are blocked.
  - Mitigation: require a documented plan/approval for lowering this gate rather
    than silently bypassing it.
- Risk: current JSON dirties the worktree.
  - Mitigation: delete `coverage-baseline-current.json` after comparison,
    unless a debug flag asks to keep it.

## Open Questions

- Should baseline lowering have a future explicit command?
  - Recommended: not in the first implementation.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for the implementation slice:
  - The gate is in `check` through `coverage-gates`.
  - The gate uses `0.25` percentage points.
  - The gate reuses current coverage data and does not rerun pytest.
  - Check mode reads the local committed baseline artifact.
  - Check mode automatically raises the baseline when current coverage improves.
  - Check and update modes cannot lower the baseline by default.
  - Pass and fail decisions are tested.
  - `uv run poe check` passes locally.
- Acceptance artifact location:
  - this plan or the implementation slice plan derived from it
- Checks the evaluator will use:
  - focused unit tests
  - focused structure tests
  - `uv run poe repo-check`
  - `uv run poe coverage-gates`
  - `uv run poe check`
- Auto-fail conditions:
  - The implementation makes `coverage-baseline` optional outside `check`.
  - The implementation reruns pytest for current coverage.
  - The implementation uses local cache as the pass/fail source of truth.
  - Normal check or update mode lowers the baseline.
  - Coverage improvements require a separate command before the default
    `check` path records them.
  - The threshold is not `0.25`.

## Implementation Order

1. Add `scripts/coverage_baseline.py` with pure helpers and a small CLI.
2. Add unit tests for helper functions and CLI pass/fail/update behavior.
3. Add committed `.coverage-baseline.json`.
4. Add `coverage-baseline` and `coverage-baseline-update` Poe tasks.
5. Append `coverage-baseline` to `coverage-gates`.
6. Update repo-check required Poe task list and structure tests.
7. Update `docs/RELIABILITY.md`, `docs/references/testing.md`, and `AGENTS.md`
   if the command surface changes.
8. Run focused tests.
9. Run `uv run poe coverage-gates`.
10. Run `uv run poe coverage-baseline-update` and confirm it can create or
    raise the baseline but does not lower it.
11. Run `uv run poe check`.
12. Record final verification evidence.

## Implementation Evidence

- Added `scripts/coverage_baseline.py`.
- Added committed baseline artifact `.coverage-baseline.json`.
- Added Poe tasks:
  - `coverage-baseline`
  - `coverage-baseline-update`
- Appended `coverage-baseline` to `coverage-gates`, so `uv run poe check`
  executes the baseline gate through the default coverage lane.
- Kept CI on the plain `uv run poe test` lane because `coverage-diff` and
  `coverage-baseline` are local working-tree gates based on staged, unstaged,
  and untracked changes. CI should use a separate PR-base coverage design, such
  as Codecov project/patch coverage, rather than local `HEAD` comparison.
- Updated repo-check contracts so the approved coverage baseline command,
  changed-lines gate, single pytest coverage run, and final `coverage-baseline`
  step are mechanically checked.
- Updated `AGENTS.md`, `docs/RELIABILITY.md`, and
  `docs/references/testing.md`.

## Evaluator Review Findings

Subagent review fan-out:

- Policy and documentation review: no issues found.
- Implementation and operational risk review:
  - Important: `current-json` cleanup could delete a pre-existing path after a
    generation failure.
  - Important: CI did not execute the coverage gates.
  - Important: non-finite numeric values could bypass the intended error path.
  - Minor: baseline writes should be atomic.
- Test adequacy review:
  - Medium: CLI exit propagation needed command-path coverage.
  - Medium: no-pytest-rerun behavior needed behavior coverage.
  - Medium: repo-check command-surface contracts were too weak.
  - Low: auto-raise metadata coverage was shallow.

Review issue disposition:

- Fixed `current-json` cleanup to delete only generated files that did not
  preexist.
- Rejected non-finite values for JSON and CLI numeric inputs.
- Wrote baseline artifacts through a same-directory temp file plus atomic
  replace.
- Did not put `coverage-gates` in CI after convention review. The gate is
  intentionally local because it evaluates local staged, unstaged, and
  untracked changes against `HEAD`; CI should use PR-base coverage semantics if
  coverage comparison is needed there.
- Added repo-check command-shape validation and negative tests.
- Added tests for script entrypoint exit behavior, subprocess command shape,
  generated JSON cleanup, pre-existing JSON preservation, and full baseline
  metadata.
- Re-reviewed after fixes:
  - operational re-review: no issues found
  - test re-review: remaining suggestions were covered by added tests

## Verification Evidence

- `uv run pytest tests/unit/scripts/test_coverage_baseline.py -q`
  - `13 passed`
- `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py tests/integration/commands/test_poe_task_runner.py -q`
  - `27 passed`
- `uv run poe format-check`
  - `199 files already formatted`
- `uv run poe lint`
  - `All checks passed`
- `uv run poe repo-check`
  - `repository checks passed`
- `uv run poe coverage-gates`
  - `756 passed, 4 skipped, 1 warning`
  - full-project coverage passed at `91%`
  - changed-line coverage passed at `95%`
  - baseline gate passed with baseline and current both `90.758392%`
- `uv run poe coverage-baseline-update`
  - baseline unchanged when current coverage equaled the baseline
- Manual CLI experiments with existing `.coverage` data:
  - baseline below current coverage: auto-raise passed
  - baseline exactly `0.25` percentage points above current coverage:
    tolerated drop passed
  - baseline `0.26` percentage points above current coverage: failed with exit
    code `2`
  - missing `.coverage` with pre-existing current JSON: failed with exit code
    `1` and preserved the pre-existing file
- `uv run poe check`
  - `756 passed, 4 skipped, 1 warning`
  - coverage baseline unchanged at `90.758392%`
  - build and Twine checks passed
  - repo-check passed
  - notebook validation passed
- `git diff --check`
  - passed
