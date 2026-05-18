# Coverage Regression Gate Research

Date: 2026-05-18

## Question

Quantleet currently has two coverage gates:

- full-project combined line/branch coverage must stay at or above `90%`
- changed-line coverage for the current diff must stay at or above `80%`

This research evaluates whether Quantleet should also add a baseline-relative
coverage regression gate:

```text
head_coverage >= base_coverage - allowed_drop
```

For example, if base coverage is `95.00%` and head coverage is `94.80%`,
the drop is `0.20` percentage points. With `allowed_drop = 0.25`, that would
pass. If head coverage is `94.60%`, the drop is `0.40` percentage points and
would fail.

## Why This Gate Exists

Absolute coverage and changed-line coverage catch different failures:

- absolute coverage prevents the whole project from falling below a known floor
- changed-line coverage checks whether the current diff is exercised
- regression coverage checks whether the project is quietly moving backward
  even when both absolute and changed-line gates still pass

This matters for agent-led development because an agent can make a change that
passes the changed-line gate and remains above the global floor while still
causing a large overall coverage drop.

## Industry Signals

Codecov's project coverage status is the closest hosted equivalent. Its
`target: auto` mode compares a pull request or commit against base coverage, and
its `threshold` setting allows a configured coverage drop before failing the
status check.

Codecov's patch coverage status is separate: it measures adjusted lines in the
pull request or commit. That separation matches Quantleet's current split
between full-project coverage and changed-line coverage.

Codecov support material also documents a real failure mode where patch coverage
passes while project coverage drops. Their recommended mitigation is to use the
project status threshold to define an acceptable coverage drop.

GitHub Action based tools expose similar ideas. For example,
`insightsengineering/coverage-action` supports a
`coverage-rate-reduction-failure` mode that fails when overall coverage
percentage decreases compared to a diff branch. It also exposes stricter modes
around uncovered statement increases.

Python-local tools are less complete:

- `coverage.py` supports absolute `fail_under`, but does not compare base and
  head reports by itself
- `pytest-cov` wraps coverage.py and likewise does not provide base/head
  regression gating as its core feature
- `diff-cover` is well suited to changed-line coverage, not whole-project
  regression relative to a baseline
- `pycobertura` can compare Cobertura XML files and is a plausible local
  building block, but its documented philosophy emphasizes uncovered-line
  regressions more than simple coverage-rate drops
- `pytest-coverage-gate` is closer to the committed-baseline model: it reads a
  baseline file, blocks coverage regressions, and documents committing that
  baseline file to version control. Its GitHub repository currently has `0`
  stars, so it is useful prior art but not a dependency candidate under
  Quantleet's `>= 100` star adoption rule.
- Kubeflow Pipelines uses `frontend/scripts/coverage-baseline.mjs` and writes a
  `.coverage-baseline.json` artifact for coverage baseline capture and
  comparison. The repository has more than `4,000` GitHub stars, so this is
  strong evidence for the `coverage-baseline` naming pattern and root-level
  dotfile JSON artifact.
- Wormhole uses a `scripts/coverage-check/` tool and a package-root
  `.coverage-baseline` file. The repository has more than `1,800` GitHub stars,
  so this is strong evidence that committed coverage baselines are commonly
  managed through repository scripts rather than through package source modules.
- `jest-coverage-ratchet` shows the same ratchet idea in the JavaScript
  ecosystem by updating thresholds upward when coverage improves

## Design Implications For Quantleet

A regression gate is meaningful if Quantleet can produce a reliable base
coverage number and compare it against the current work without adding too much
local latency.

The main implementation question is not the formula. The formula is simple:

```text
drop = base_total_coverage - head_total_coverage
fail if drop > allowed_drop
```

The real implementation question is how to obtain `base_total_coverage`:

- run coverage on `HEAD` or another baseline in a temporary worktree
- read a committed or generated baseline artifact
- rely on CI services such as Codecov
- cache the baseline locally and invalidate it when the baseline commit changes

For Quantleet's local agent harness, relying only on a hosted service is not
enough. Agents need local feedback. A local implementation therefore needs a
repeatable base/head measurement strategy.

## Risks

- Running coverage twice can roughly double coverage-gate runtime.
- Small denominator changes can create noisy percentage movement.
- Removing covered lines can reduce total coverage even if no new uncovered code
  was added.
- A percentage drop alone does not prove test quality declined.

These risks argue for a tolerance such as `0.25` or `0.50` percentage points
rather than a strict no-drop policy.

## Recommendation After Experiment

The repository-local experiment in
[`../plans/2026-05-18-coverage-regression-gate-experiment-plan.md`](../plans/2026-05-18-coverage-regression-gate-experiment-plan.md)
supports adding this gate to the default `check` path.

Recommended policy:

- allowed drop: `0.25` percentage points
- comparison: coverage.py total combined line/branch percentage
- failure condition: `base_coverage - head_coverage > 0.25`
- integration: default `uv run poe check`

Recommended implementation shape:

- reuse the `.coverage` data already produced by `coverage-gates` for head
  coverage
- commit `.coverage-baseline.json` and compare against the local checked-out
  baseline file
- automatically update the baseline in the default `coverage-baseline` check
  when coverage improves, unless a human-reviewed policy change intentionally
  lowers it
- avoid rerunning pytest for head coverage
- avoid local baseline cache as the source of truth
- directly implement the repo-local script because no reviewed library meets
  the `>= 100` star threshold while matching the required policy
- name the repo-local script `scripts/coverage_baseline.py`, following this
  repository's existing snake_case Python script convention
- expose the default ratcheting check as `coverage-baseline`, following this
  repository's hyphenated Poe task convention and the observed OSS
  `coverage-baseline` naming pattern
- keep `coverage-baseline-update` only as an explicit bootstrap/maintenance
  command that can create or raise the baseline but cannot lower it

The gate should not live only as an optional command. Agent sessions can miss
optional checks, so the reliable interface is still one default local gate:
`uv run poe check`.

## Sources

- Codecov status checks: https://docs.codecov.com/v5.0/docs/commit-status
- Codecov project coverage drop support note:
  https://codecovpro.zendesk.com/hc/en-us/articles/15822623087515-Unexpected-drop-in-project-coverage-for-Pull-Request
- coverage-action:
  https://github.com/insightsengineering/coverage-action
- pycobertura:
  https://pypi.org/project/pycobertura/
- diff-cover:
  https://pypi.org/project/diff-cover/
- coverage.py:
  https://coverage.readthedocs.io/
- pytest-coverage-gate:
  https://pypi.org/project/pytest-coverage-gate/
- Kubeflow Pipelines coverage baseline script:
  https://github.com/kubeflow/pipelines/blob/master/frontend/scripts/coverage-baseline.mjs
- Wormhole coverage-check docs:
  https://github.com/wormhole-foundation/wormhole/blob/main/scripts/coverage-check/README.md
- jest-coverage-ratchet:
  https://npm.io/package/jest-coverage-ratchet
- Large-scale test coverage evolution study:
  https://www.cs.cmu.edu/~mhilton/docs/ase18coverage.pdf
