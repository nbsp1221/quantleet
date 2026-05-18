# Coverage Regression Gate Experiment Plan

- Date: 2026-05-18
- Task: Evaluate whether Quantleet should add a base/head coverage regression
  gate and determine a practical allowed-drop threshold.
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Turn the coverage regression gate research into a local experiment and
  report whether the gate is useful, what threshold to use, and what performance
  trade-off it introduces.
- Governing docs:
  - `AGENTS.md`
  - `docs/RELIABILITY.md`
  - `docs/references/testing.md`
  - `docs/references/coverage-regression-gate-research.md`
  - `docs/plans/2026-05-17-diff-coverage-gate-plan.md`
  - `docs/plans/2026-05-17-check-command-gate-alignment-plan.md`
- In-repo scope:
  - Add the research report.
  - Define an experiment plan.
  - Run local coverage measurements over recent commits.
  - Compare candidate thresholds: `0.00`, `0.25`, `0.50`, `1.00`.
  - Measure runtime cost.
  - Report whether the gate should be added.
- Out-of-repo scope:
  - Do not implement the production gate in this slice.
  - Do not change coverage thresholds in `pyproject.toml`.
  - Do not commit or push.
- Approval record, if required: not required.

## Experiment Design

Use recent commit transitions on `main`:

```text
base commit -> head commit
```

For each transition:

1. create or reuse a temporary worktree for the base commit
2. run coverage on the default pytest lane
3. collect total combined line/branch coverage from `coverage json`
4. create or reuse a temporary worktree for the head commit
5. run the same coverage command
6. compute `drop = base_coverage - head_coverage`
7. record runtime for each coverage collection

Coverage command:

```bash
uv run coverage erase
uv run coverage run -m pytest -q
uv run coverage json -o coverage.json
```

The experiment measures the same coverage concept as the current repository
gate: coverage.py combined coverage with branch measurement enabled in
`pyproject.toml`.

## Candidate Thresholds

- `0.00`: no coverage drop allowed
- `0.25`: tiny noise budget
- `0.50`: moderate noise budget
- `1.00`: loose regression budget

For each threshold, count how many recent transitions would have failed.

## Success Criteria For The Experiment

- At least five recent commit transitions are measured, unless older commits
  cannot run under the current local environment.
- Runtime cost is measured for base/head coverage collection.
- The report distinguishes:
  - whether the gate is meaningful
  - recommended threshold
  - expected local runtime overhead
  - implementation risks
- The plan records the actual evidence instead of relying on the theory in the
  research document.

## Experiment Results

The experiment used six recent commits after the Python `3.12` baseline was
introduced:

| Commit | Subject | Coverage | Runtime |
| --- | --- | ---: | ---: |
| `4d29e4e` | Set Python 3.12 beta baseline | `93.577465%` | `43s` |
| `4bd962c` | Add GitHub Actions CI workflow | `93.577465%` | `42s` |
| `a29b796` | Add PyPI release workflow | `93.577465%` | `42s` |
| `93c2f1b` | Standardize coverage quality gates | `90.738397%` | `49s` |
| `e19e7ec` | Add diff coverage verification gates | `90.738397%` | `49s` |
| `52c8d6c` | Rename verification gate to check | `90.754002%` | `49s` |

Transition results:

| Transition | Base | Head | Drop | `0.00` | `0.25` | `0.50` | `1.00` |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| `4d29e4e -> 4bd962c` | `93.577465%` | `93.577465%` | `0.000000` | pass | pass | pass | pass |
| `4bd962c -> a29b796` | `93.577465%` | `93.577465%` | `0.000000` | pass | pass | pass | pass |
| `a29b796 -> 93c2f1b` | `93.577465%` | `90.738397%` | `2.839068` | fail | fail | fail | fail |
| `93c2f1b -> e19e7ec` | `90.738397%` | `90.738397%` | `0.000000` | pass | pass | pass | pass |
| `e19e7ec -> 52c8d6c` | `90.738397%` | `90.754002%` | `-0.015605` | pass | pass | pass | pass |

Threshold failure counts:

| Allowed drop | Failures |
| ---: | ---: |
| `0.00` | `1 / 5` |
| `0.25` | `1 / 5` |
| `0.50` | `1 / 5` |
| `1.00` | `1 / 5` |

Runtime:

- mean single coverage run: `45.67s`
- mean uncached base/head pair runtime: `91.20s`
- current local `check` already pays for one coverage run through
  `coverage-gates`
- an uncached regression gate would add roughly one extra coverage run, about
  `42-49s` in this experiment

Raw command used for each commit:

```bash
uv run coverage erase
uv run coverage run -m pytest -q
uv run coverage json -o coverage.json
```

The large `2.839068` percentage-point drop happened in the commit that
standardized coverage quality gates. This is a useful signal: the proposed gate
would have caught a meaningful coverage movement. It also shows that intentional
coverage-policy changes need an explicit override or documented approval path.

## Initial Recommendation

Add the feature to the default `check` path, but do not add it as a naive
always-run uncached gate.

Recommended policy:

- use a baseline-relative gate with `allowed_drop = 0.25` percentage points
- compare coverage.py's total combined line/branch percentage
- fail when `base_coverage - head_coverage > 0.25`
- allow explicit documented override for intentional coverage-policy changes
  or large test harness restructuring

Why `0.25`:

- the experiment found no ordinary noise between unchanged-quality transitions
- the only real drop was much larger than every candidate threshold
- `0.25` matches the intended "tiny noise budget" policy without making the
  gate as brittle as strict `0.00`
- `0.50` and `1.00` produced the same result in this sample, but they give away
  more regression budget without evidence that Quantleet needs that much slack

Performance recommendation:

- include the gate in `check`
- avoid computing baseline coverage during `check`
- use a committed `.coverage-baseline.json` artifact as the baseline source of
  truth
- reuse the existing `.coverage` data from `coverage-gates` for head coverage
- do not run pytest a second time for head coverage

The gate is meaningful, but the performance trade-off is material. Uncached, it
approximately doubles the coverage portion of local verification. With a
committed baseline artifact, it can be reduced to one normal head coverage run
plus a cheap comparison.

## Check Integration Addendum

The user rejected keeping this as a separate command because agent sessions can
forget optional gates. The revised product direction is:

- the production gate should become part of the default `check` path
- the implementation must minimize added runtime through a committed baseline
  artifact and head coverage reuse
- the experiment must prove both behavior and optimization before implementation

Revised optimization hypothesis:

- `check` already runs `coverage-gates`, so head coverage data should be reused
  from the existing coverage run instead of running tests again
- the baseline coverage percentage should be read from a committed
  `.coverage-baseline.json` file
- comparison cost should be close to `coverage json` plus a small comparison
  script, not another pytest run

Additional experiment requirements:

- measure cached/prototype comparison cost
- prove pass behavior on the current head
- prove fail behavior with an artificial uncovered source-code change
- update the recommendation assuming the gate is included in `check`

## Check Integration Optimization Experiment

Prototype:

- temporary script: `/tmp/quantcraft_covreg_experiment.py`
- baseline cache key: `git rev-parse HEAD`
- baseline artifact: coverage.py JSON report cached by commit SHA
- head coverage: reuse the current `.coverage` data produced by the normal
  coverage run, then run only `coverage json`
- comparison: `base_coverage - head_coverage > 0.25`

This prototype used a local cache to prove that the comparison itself can be
cheap when the baseline percentage is already available. The later design
decision replaced the cache source of truth with a committed
`.coverage-baseline.json` file, which keeps the same cheap comparison property
without hidden local cache state.

The prototype intentionally mirrors how this should work inside `check`:

1. `coverage-gates` runs pytest once under coverage.py
2. coverage.py writes XML for `diff-cover`
3. the regression gate writes JSON from the same `.coverage` data
4. the regression gate compares head JSON with cached baseline JSON

Optimized runtime results:

| Case | Head coverage run | Regression gate time | Base | Head | Drop | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| current head, cold cache | `45s` | `50.59s` | `90.754001%` | `90.754001%` | `0.000000` | pass |
| current head, warm cache | already paid | `0.51s` | `90.754001%` | `90.754001%` | `0.000000` | pass |
| artificial uncovered source, warm cache | `50s` | `0.50s` | `90.754001%` | `89.826975%` | `0.927026` | fail, exit code `2` |

The fail probe added an untested source file under `src/quantleet` in a
temporary detached worktree under `/tmp`. The repository worktree was not
modified.

Optimization conclusion:

- the gate can be included in `check`
- baseline computation during `check` must be avoided
- comparison cost is about `0.5s` when baseline data is already available
- head coverage must reuse the `.coverage` data already produced by
  `coverage-gates`
- production implementation should not run pytest a second time for head
  coverage
- production implementation should read the baseline from committed
  `.coverage-baseline.json`, not from a local cache

## Evaluator Review

- Findings:
  - The experiment supports the feature as a useful regression signal.
  - The optimization experiment shows the gate can belong in the default local
    `check` command if baseline coverage is read from a committed artifact and
    head coverage data is reused.
  - The recommended threshold is `0.25` percentage points.
- Verification evidence:
  - `4d29e4e`, `4bd962c`, `a29b796`, `93c2f1b`, `e19e7ec`, and `52c8d6c` were
    measured in detached worktrees under `/tmp`.
  - All six coverage runs completed successfully.
  - The raw result table is recorded above.
  - Cold-cache prototype on current head passed with `50.59s` baseline cache
    generation and `0.000000` coverage drop.
  - Warm-cache prototype on current head passed with `0.51s` comparison time.
  - Warm-cache prototype with artificial uncovered source failed with
    `0.927026` coverage drop and exit code `2`.
- Final disposition:
  - Accepted for experiment. Next implementation slice should add the gate to
    `check` with a committed `.coverage-baseline.json` artifact and head
    coverage reuse.
