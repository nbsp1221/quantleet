# AGENTS

This file is the short map for agent work in `quantcraft`.

## Primary Sources Of Truth

- [`README.md`](README.md): project purpose, current scope, local setup
- [`ARCHITECTURE.md`](ARCHITECTURE.md): domain map, safety tiers, dependency rules
- [`docs/DESIGN.md`](docs/DESIGN.md): long-lived design index
- [`docs/design-docs/index.md`](docs/design-docs/index.md): long-lived design-doc status map with explicit `Status`, `Canonical`, `Applicability`, and `Read When` fields
- [`docs/product-specs/index.md`](docs/product-specs/index.md): product-spec status map with the same explicit fields for implemented, approved expansion, and future scope
- [`docs/product-specs/backtest.md`](docs/product-specs/backtest.md): current implemented backtest baseline entry and pointer to the canonical MVP spec
- [`docs/PLANS.md`](docs/PLANS.md): execution plan index
- [`docs/RELIABILITY.md`](docs/RELIABILITY.md): verification and reproducibility rules
- [`docs/SECURITY.md`](docs/SECURITY.md): secrets and financial safety rules
- [`docs/QUALITY_SCORE.md`](docs/QUALITY_SCORE.md): tracked repository quality state

## Standard Local Commands

Agents should use the repository command surface instead of inventing ad-hoc verification flows.

Low-level repo-local harness commands remain the stable direct surface:

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`
- `uv run python scripts/repo_check.py`
- `uv run python scripts/notebook_validate.py`
- `uv run python scripts/live_smoke.py`

Use `uv run poe` as the developer task layer on top of those repo-local harness commands:

- `uv run poe lint`
- `uv run poe format`
- `uv run poe typecheck`
- `uv run poe test`
- `uv run poe test-unit`
- `uv run poe test-integration`
- `uv run poe test-structure`
- `uv run poe test-smoke`
- `uv run poe test-live`
- `uv run poe build`
- `uv run poe repo-check`
- `uv run poe notebook-validate`
- `uv run poe live-smoke`
- `uv run poe verify`

## Safety Tiers

- Tier A: `trading`, `execution`
- Tier B: `data`, `research`
- Tier C: `ml`, notebooks, generated docs

Tier A changes require stronger human gate, explicit plan coverage, and matching reliability/security documentation.

## Agent Operating Rules

- Read the relevant spec or design doc before code changes.
- Use the design-doc and product-spec indexes as status maps: pick the row whose applicability matches the task, then read the canonical rows first.
- Read the product spec that matches the task at hand before code changes:
  - current implemented scope work should start from the current implemented-scope spec
  - approved expansion work should start from the approved next-slice spec
- Keep plans and behavioral changes in the repository.
- Do not bypass architecture checks or document checks.
- If code touches Tier A domains, stop short of claiming autonomous completion.
- Prefer the documented command surface and repository docs over local memory.
- Treat `scripts/` plus `poe` as the harness contract; do not reintroduce package-level CLI shims for repo-local DX flows.
- Live tests are explicit-only and excluded from the default `pytest` lane.
- Place new tests under the taxonomy, not as flat `tests/test_*.py` files.
- Mirror source structure inside `tests/unit` and `tests/integration` once a matching source package path exists.
- Keep repository-rule checks under `tests/structure`.
