# Testing Reference

Use this reference when adding or moving tests in `quantleet`.

## Top-Level Taxonomy

- `tests/unit`
- `tests/integration`
- `tests/perf`
- `tests/structure`
- `tests/smoke`

## Placement Rules

- Put isolated deterministic behavior in `tests/unit`
- Put cross-module and command-surface verification in `tests/integration`
- Put explicit-only performance regression checks in `tests/perf`
- Put repository, docs, and architecture rules in `tests/structure`
- Put sanity checks in `tests/smoke`

## Command Lanes

- `uv run poe test` runs the default pytest pass/fail lane without coverage
  collection
- `uv run poe coverage` reruns the default pytest lane under coverage.py and
  then enforces the configured coverage report gate
- `uv run poe coverage-diff` reruns the default pytest lane under coverage.py
  and enforces the changed-line coverage gate for the current diff against
  `HEAD`
- `uv run poe coverage-gates` runs pytest once under coverage.py and then
  enforces both the full-project coverage gate and the changed-line coverage
  gate
- use `coverage` when the question is whether test coverage still satisfies the
  repository reliability floor, not only whether tests pass

## Source Mirroring

Mirror the source layout inside these areas once a matching source package path exists:

- `tests/unit`
- `tests/integration`

Mirror the final capability-first owner paths whenever those owner paths exist.
Do not preserve or reintroduce transitional test names once the corresponding
source shim or legacy owner path has been removed.

Do not force repository-rule checks into a source mirror.

## Smoke Policy

- `tests/smoke/local` is for local smoke verification
- `tests/smoke/live` is for explicit-only network-backed checks
- live tests do not belong in the default `pytest` lane
- use `uv run poe test-live` when you explicitly want the live lane
- use `uv run poe test-live` or target `tests/smoke/live` explicitly when you want live coverage

## Performance Policy

- `tests/perf` is an explicit-only lane
- perf checks do not belong in the default `pytest` lane
- use `uv run poe perf-check` when you explicitly want the perf lane

## Naming

Prefer:

- `test_<subject>_<behavior>.py`

Avoid broad names such as:

- `test_exchange.py`
- `test_misc.py`

## Fixtures

- use `tests/conftest.py` only for truly shared setup
- prefer narrower `conftest.py` files closer to the tests that need them

## Prohibited Layout

Do not add new flat root-level files matching:

- `tests/test_*.py`
