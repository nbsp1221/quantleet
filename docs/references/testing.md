# Testing Reference

Use this reference when adding or moving tests in `quantcraft`.

## Top-Level Taxonomy

- `tests/unit`
- `tests/integration`
- `tests/structure`
- `tests/smoke`

## Placement Rules

- Put isolated deterministic behavior in `tests/unit`
- Put cross-module and command-surface verification in `tests/integration`
- Put repository, docs, and architecture rules in `tests/structure`
- Put sanity checks in `tests/smoke`

## Source Mirroring

Mirror the source layout inside these areas once a matching source package path exists:

- `tests/unit`
- `tests/integration`

The current codebase is still pre-domain in places, so transitional domain-intent names such as `market_data` are acceptable until the source tree is moved under the new bounded contexts.

Do not force repository-rule checks into a source mirror.

## Smoke Policy

- `tests/smoke/local` is for local smoke verification
- `tests/smoke/live` is for explicit-only network-backed checks
- live tests do not belong in the default `pytest` lane
- use `uv run poe test-live` when you explicitly want the live lane
- use `uv run poe test-live` or target `tests/smoke/live` explicitly when you want live coverage

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
