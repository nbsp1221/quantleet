# Diff Coverage Gate Plan

- Date: 2026-05-17
- Task: Add a local changed-lines coverage gate using `diff-cover`.
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Add a repo-local command that checks coverage for the current working
  tree diff before commit, and include that command in the default `verify`
  lane so AI agents have one hard-to-bypass verification interface. The command
  should cover staged changes, unstaged changes, and new untracked source files,
  and it should fail when changed-line coverage is below `80%`.
- Governing docs:
  - `AGENTS.md`
  - `docs/PLANS.md`
  - `docs/RELIABILITY.md`
  - `docs/references/testing.md`
  - `docs/references/test-quality-evaluation-report-2026-05-16.md`
- Why these are governing:
  - `AGENTS.md` requires planner/generator/evaluator workflow, repo-local
    command surfaces, and verification evidence.
  - `docs/PLANS.md` defines where active plans live.
  - `docs/RELIABILITY.md` defines local verification and coverage guardrails.
  - `docs/references/testing.md` defines test lane policy.
  - The test quality report records why the next quality-gate work should focus
    on changed-test review and targeted structure checks before heavier gates.
- In-repo scope:
  - Add `diff-cover` as a development dependency.
  - Add a Poe command for changed-lines coverage.
  - Configure the command to generate a coverage XML report from the default
    pytest lane and then evaluate the current git diff with `diff-cover`.
  - Include staged changes, unstaged changes, and untracked source files.
  - Add the changed-lines coverage command to the default local verification
    path.
  - Add or update structure tests that lock the command contract.
  - Update reliability/testing docs and AGENTS command surface if needed.
- Out-of-repo scope:
  - No GitHub Actions workflow change in this slice.
  - No Codecov or hosted coverage integration.
  - No mutation testing or flaky-test tooling.
- Tier A progression requested: `no`
- Approval record, if required: not required.
- Verification commands:
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py -q`
  - `uv run poe coverage-diff`
  - `uv run poe repo-check`
  - `uv run poe verify`
- Success criteria:
  - A local command named `uv run poe coverage-diff` exists and is documented.
  - The command runs pytest under coverage.py and writes an XML coverage report
    suitable for `diff-cover`.
  - The command invokes `diff-cover` with `--include-untracked`.
  - The command uses `--fail-under 80`.
  - The command checks the current working tree diff against `HEAD`.
  - The command includes staged changes, unstaged changes, and untracked new
    source files.
  - The command evaluates changed-line coverage, not whole-file coverage.
  - The command fails when current-diff changed-line coverage is below `80%`.
  - The command passes when current-diff changed-line coverage is at least
    `80%`.
  - The command passes when the working tree has no changed source lines with
    coverage information.
  - New source files, modified staged files, and modified unstaged files are
    included in the changed-line coverage calculation.
  - The default local verification path includes the changed-lines coverage
    gate so agents cannot skip it by omission.
  - Existing full-project coverage remains unchanged: `uv run poe coverage`
    continues to enforce the single project-wide combined line/branch `90%`
    hard gate.
  - The new gate does not replace `test` or full-project `coverage`; it is a
    pre-commit changed-lines accountability check.
- Out of scope:
  - Adding `coverage-diff` to GitHub Actions CI in this slice.
  - Enforcing `100%` changed-line coverage.
  - Adding separate per-file or branch-specific diff coverage thresholds.
  - Building custom diff parsing instead of using `diff-cover`.

## Rationale And Decision Evidence

- Existing project coverage gate answers: "Is the whole project still above the
  reliability floor?"
- Diff coverage answers a different question: "Did the lines changed in this
  work receive test execution?"
- `coverage-diff` is intentionally scoped to the current pre-commit work:
  staged changes, unstaged changes, and untracked new source files.
- `coverage-diff` should not require untouched legacy lines in a changed file to
  become covered. It measures only the changed lines reported by git diff.
- The changed-lines coverage gate should be part of the default local
  verification path because agents otherwise have to remember a second command,
  which leaves an easy bypass path. The desired agent interface is one default
  verification command that runs the relevant local hard gates.
- Current CI does not call `uv run poe verify`; it calls job-specific Poe tasks
  such as `format-check`, `lint`, `typecheck`, `test`, `build`, and
  `repo-check`. Therefore adding changed-lines coverage to the default local
  verification path is a local agent gate change, not a CI workflow change.
- Clean-worktree experiment confirmed `diff-cover coverage.xml --compare-branch
  HEAD --include-untracked --fail-under 80` exits successfully when there are
  no changed lines with coverage information.
- This is valuable for AI-assisted work because an agent can make localized code
  changes that do not move the whole-project `90%` coverage number enough to
  fail the global gate.
- The selected library is `diff-cover` because it compares coverage XML with git
  diff output and directly supports coverage.py reports.
- The selected initial threshold is `80%`.
  - `60%` is too weak: the experiment showed it passes while each changed file
    still contains uncovered changed code.
  - `70%` is a minimum useful line: it failed the intentionally weak probe at
    `69.23%`.
  - `80%` adds meaningful pressure without matching the stricter global `90%`
    gate immediately.
  - `90%` may be too strict as an initial changed-lines gate because diff
    coverage is sensitive to small patches, defensive branches, and non-runtime
    edits.
  - `100%` is explicitly rejected as too risky for the first version.

## Experiment Summary

- Experiment location: `/tmp/quantleet-diffcov-exp`
- Base commit: `93c2f1b`
- Probe changes:
  - staged new source file:
    `src/quantleet/research/_diffcov_staged_new.py`
  - untracked new source file:
    `src/quantleet/research/_diffcov_untracked_new.py`
  - staged modified source file:
    `src/quantleet/research/series.py`
  - unstaged modified source file:
    `src/quantleet/research/qc.py`
- Probe result with `--include-untracked`:
  - `Total: 26 lines`
  - `Missing: 8 lines`
  - `Coverage: 69.23%`
- Threshold result:
  - `60`: passed
  - `70`: failed
  - `80`: failed
  - `90`: failed
- File-status behavior:
  - default `diff-cover` includes staged and unstaged changes
  - default `diff-cover` does not include untracked files
  - `--include-untracked` includes new untracked source files
  - `--ignore-staged` and `--ignore-unstaged` experimentally confirmed status
    filtering works, so the default plus `--include-untracked` matches the
    intended pre-commit working-tree check

## Proposed Implementation Shape

- Add `diff-cover` to the development dependency group.
- Add a public Poe task named `coverage-diff`.
- Use a simple standard-tool sequence:
  - erase prior coverage data
  - run pytest under coverage.py
  - write `coverage.xml` with coverage.py's XML fail-under disabled for this
    command
  - run `diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80`
- The command should use the current working tree diff against `HEAD`, not a
  remote PR base, because this gate is designed for local pre-commit agent
  feedback.
- Add the changed-lines coverage gate to the default local verification path.
  This keeps the existing whole-project coverage gate and adds the changed-lines
  accountability gate before build/repo checks finish.
- Prefer a public task over private helper tasks unless the command becomes too
  long or needs reuse.
- Keep `coverage` and `coverage-diff` separate:
  - `coverage`: full-project combined line/branch gate, currently `90%`
  - `coverage-diff`: changed-lines gate for current pre-commit work, `80%`
- `coverage-diff` uses `coverage xml -o coverage.xml --fail-under=0` so XML
  generation does not duplicate or obscure the existing full-project `coverage`
  gate.
- Follow-up optimization:
  `docs/plans/2026-05-17-verify-coverage-gates-optimization-plan.md` replaces
  separate `verify` calls to `test`, `coverage`, and `coverage-diff` with a
  single `coverage-gates` lane that reuses one fresh coverage run for both
  coverage gates.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm the new command exists and uses `diff-cover`.
  - Confirm `--include-untracked` and `--fail-under 80` are present.
  - Confirm the command generates fresh XML coverage before evaluating the diff.
  - Confirm the default local verification path includes the changed-lines
    coverage gate.
  - Confirm staged, unstaged, and untracked source changes are covered by an
    integration or structure-level contract, or by a documented manual
    verification run if direct automation would make tests too complex.
  - Confirm existing `coverage` semantics remain unchanged.
- Acceptance artifact location:
  - this plan
- How the generator and evaluator agreed on done before execution:
  - Done means a local pre-commit diff coverage command exists, is documented,
    is tested at the command contract level, and has fresh verification output.
- Checks the evaluator will use:
  - targeted structure tests
  - `uv run poe coverage-diff`
  - `uv run poe coverage`
  - `uv run poe repo-check`
  - `uv run poe verify`
- Auto-fail conditions:
  - The implementation parses git diffs manually instead of using `diff-cover`.
  - The changed-lines threshold is not `80`.
  - Untracked new source files are silently excluded.
  - `coverage-diff` reuses stale coverage data.
  - The default local verification path does not include the changed-lines
    coverage gate.
  - The global `coverage` gate is weakened or replaced.

## Generator Work Log

- Planned slice order:
  - Add `diff-cover` dependency.
  - Add `coverage-diff` Poe command.
  - Add the changed-lines coverage gate to the default local verification path.
  - Add structure tests for command shape and dependency presence.
  - Update docs for the new command and its relationship to `test` and
    `coverage`.
  - Run targeted tests and command-level verification.
- Notes:
  - The implementation should stay small and tool-native. Avoid new Python
    wrapper scripts unless Poe quoting or portability makes direct commands
    impractical.
  - Added `diff-cover>=10.2.0` to the development dependency group.
  - Added public Poe task `coverage-diff`.
  - Added changed-lines coverage to the default `verify` sequence.
  - Updated repo-check's required Poe task surface and structure tests.
  - Updated `AGENTS.md`, `docs/RELIABILITY.md`, and
    `docs/references/testing.md`.
  - Added `coverage.xml` to `.gitignore` because the new command generates it.
- Blockers or scope changes:
  - None at planning time.

## Evaluator Review

- Findings:
  - Initial `uv run poe verify` failed at `ruff check .` because inline TOML
    fixture `verify` arrays in structure tests exceeded the repository
    `100`-character line limit.
  - Fixed by rewriting the fixture `verify` arrays as multiline TOML arrays.
  - Three read-only subagent reviewers were used:
    - Documentation/plan compliance reviewer: found no behavior-documentation
      mismatch; flagged that this evaluator section had to be completed before
      closure.
    - Command/test contract reviewer: found no blocker, important, or minor
      issue in `pyproject.toml`, `uv.lock`, repo-check task surface, or
      structure tests.
    - Bypass/risk reviewer: found no blocker or important issue; confirmed no
      custom diff parser, no CI scope change, existing `coverage` semantics were
      not weakened, and generated `coverage.xml` is ignored.
- Verification evidence:
  - `uv run pytest tests/structure/repo/test_coverage_harness.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py -q`
    - result: `21 passed in 0.10s`
  - `uv run poe repo-check`
    - result: `repository checks passed`
  - `uv run poe coverage-diff`
    - result: `738 passed, 4 skipped, 1 warning in 71.90s`
    - result: wrote `coverage.xml`
    - result: diff-cover reported `No lines with coverage information in this diff.`
  - `uv run poe coverage`
    - result: `738 passed, 4 skipped, 1 warning in 68.28s`
    - result: `TOTAL ... 91%`
  - `git diff --check`
    - result: no output
  - `git status --short --ignored coverage.xml`
    - result: `!! coverage.xml`
  - `uv run poe verify`
    - first result: failed at lint due four long fixture lines
    - corrective action: converted fixture `verify` arrays to multiline TOML
    - final result:
      - `ruff check .`: `All checks passed!`
      - `mypy src`: `Success: no issues found in 61 source files`
      - `pytest -q`: `738 passed, 4 skipped, 1 warning in 15.66s`
      - `coverage`: `738 passed, 4 skipped, 1 warning in 54.37s`,
        `TOTAL ... 91%`
      - `coverage-diff`: `738 passed, 4 skipped, 1 warning in 51.70s`,
        diff-cover reported `No lines with coverage information in this diff.`
      - `uv build`: successfully built sdist and wheel
      - `repo-check`: `repository checks passed`
      - `notebook-validate`: validated all tracked notebooks
- Final disposition:
  - Accepted. The local changed-lines coverage gate is implemented with
    `diff-cover`, included in the default local verification path, documented,
    locked by structure tests, and verified by the repository default
    verification lane.
