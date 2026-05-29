# Repo Entry Contract

`AGENTS.md` is the repo entry contract for agent work in `quantleet`.

This file is the map, not the encyclopedia.
The deeper docs under `docs/` are the system of record for architecture,
product scope, workflow policy, and package structure.

## Workflow Contract

Use a planner/generator/evaluator loop for any non-trivial change.

1. Planner
   - read the governing docs for the task
   - create or update an active plan under [`docs/plans/`](docs/plans/)
   - record scope, governing docs, approval needs, check commands, and
     success criteria before editing
2. Generator
   - make only the in-repo changes allowed by the active plan
   - keep work scoped to the approved slice
3. Evaluator
   - review the diff against the plan, governing docs, and fresh check
     evidence
   - report findings first

Required artifacts:

- planner artifact: active plan under `docs/plans/`
- evaluator artifact: evaluator-owned acceptance contract plus review findings
  in the active plan
- check artifact: fresh command output cited by the evaluator

Use the active plan as the single definition of done for the current slice.
Compound Engineering is tracked in
[`docs/plans/2026-04-13-ce-workflow-migration-plan.md`](docs/plans/2026-04-13-ce-workflow-migration-plan.md);
the repo contract does not require external `ce:*` commands.

## Governing Docs

Read the governing docs for the task before changing code:

- [`README.md`](README.md)
- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`docs/product-specs/index.md`](docs/product-specs/index.md)
- [`docs/design-docs/index.md`](docs/design-docs/index.md)
- [`docs/design-docs/package-topology-and-naming.md`](docs/design-docs/package-topology-and-naming.md)
- [`docs/RELIABILITY.md`](docs/RELIABILITY.md)
- [`docs/SECURITY.md`](docs/SECURITY.md)
- [`docs/DESIGN.md`](docs/DESIGN.md)
- [`docs/PLANS.md`](docs/PLANS.md)

## Repo Scope And Approval

Default scope is this repository only.

- non-repo files, external connectors, sensitive environment variables, and
  task-driven network access are out of scope unless a named human approval
  record allows them
- Tier A domains are `trading` and `execution`
- Tier A work and any scope expansion require a human approval record in the
  active plan before implementation is treated as approved or review is closed

The approval record must include the requestor, human approver, check
marker, granted scope, expiration, and an audit reference allowed by
[`docs/SECURITY.md`](docs/SECURITY.md).

## Plans And Trials

- active plans live in [`docs/plans/`](docs/plans/)
- start plan artifacts from [`docs/plans/TEMPLATE.md`](docs/plans/TEMPLATE.md)
- workflow trial and exception records live in
  [`docs/plans/trials/`](docs/plans/trials/)
- historical docs elsewhere under `docs/` are not workflow authority; when they
  disagree, the active plan and governing docs win

## Repo-Local Check

Use the repository command surface; do not replace it with ad hoc scripts or
package-level CLI shims.

- default check: `uv run poe check`
- formatting: `uv run poe format`
- coverage-only check: `uv run poe coverage`
- changed-lines coverage check: `uv run poe coverage-diff`
- baseline-relative coverage check: `uv run poe coverage-baseline`
- bootstrap or explicitly raise coverage baseline: `uv run poe coverage-baseline-update`
- combined coverage gates: `uv run poe coverage-gates`
- dead-code check: `uv run poe dead-code`
- dependency declaration check: `uv run poe dependency-check`
- targeted trading mutation check: `uv run poe mutation-trading`
- runtime-sensitive backtest or research changes: `uv run poe check-runtime`
- live checks: `uv run poe test-live`
- performance checks: `uv run poe perf-check`
- package artifact checks: `uv run poe twine-check`
- repo/document checks: `uv run poe repo-check`

The repo-local harness commands remain valid:

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy src`
- `uv run python scripts/repo_check.py`
- `uv run python scripts/notebook_validate.py`
- `uv run python scripts/live_smoke.py`
- `uv build`
- `uvx twine check --strict dist/*.whl dist/*.tar.gz`

Keep the hard gates intact:

- do not bypass architecture checks
- live tests stay out of the default lane
- performance checks stay out of the default lane
- changes under the runtime-sensitive backtest or research path must also run
  `uv run poe check-runtime`
