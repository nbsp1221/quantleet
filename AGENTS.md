# Repo Entry Contract

`AGENTS.md` is the self-contained repo entry contract for agent work in
`quantcraft`.

## Workflow Contract

Use a structured planner/generator/evaluator loop for any non-trivial change.
The repo contract is the behavior below, not any host-specific command name.

1. Planner
   - read the governing docs for the task
   - create or update an active plan under [`docs/plans/`](docs/plans/)
   - record scope, governing docs, approval needs, verification commands, and
     success criteria before editing code
2. Generator
   - make only the in-repo changes allowed by the active plan
   - keep work scoped to the approved slice
   - record blockers or scope changes in the active plan instead of silently
     widening scope
3. Evaluator
   - review the resulting diff against the plan, governing docs, and fresh
     verification evidence
   - report findings first
   - do not treat missing verification, missing approval, or ambiguous routing
     as acceptable

One operator may fill more than one role, but the artifacts must stay separate:

- planner artifact: active plan under `docs/plans/`
- evaluator artifact: an evaluator-owned acceptance contract plus review findings
  in the active plan; use a linked trial/exception record only for workflow
  experiments or blocked runs
- verification artifact: fresh command output cited by the evaluator

Before generator work starts, the active plan must contain an evaluator-owned
acceptance contract that names what "done" means for the current slice and how
it will be checked.

Compound Engineering is the workflow migration hypothesis tracked in
[`docs/plans/2026-04-13-ce-workflow-migration-plan.md`](docs/plans/2026-04-13-ce-workflow-migration-plan.md).
This repo contract does **not** require external `ce:*` commands in order to be
understandable or executable.

## Governing Docs

Read the governing docs for the task before changing code:

- [`README.md`](README.md): project purpose and local setup
- [`ARCHITECTURE.md`](ARCHITECTURE.md): domain map, dependency rules, safety
  tiers
- [`docs/product-specs/index.md`](docs/product-specs/index.md): route to the
  governing product spec for the current scope
- [`docs/design-docs/index.md`](docs/design-docs/index.md): route to the
  governing long-lived design doc when architecture or repo rules change
- [`docs/RELIABILITY.md`](docs/RELIABILITY.md): verification and reproducibility
  rules
- [`docs/SECURITY.md`](docs/SECURITY.md): repo-scope, secrets, and financial
  safety rules

## Repo Scope And Approval

Default scope is this repository only.

- Non-repo files, external connectors, sensitive environment variables, and
  task-driven network access are out of scope unless a named human approval
  record allows them.
- Tier A domains are `trading` and `execution`. Do not claim autonomous
  completion for Tier A work.
- Tier A work and any scope expansion require a human approval record in the
  active plan under `docs/plans/` before implementation is treated as approved
  or review is treated as closed.

The approval record must include at least:

- requestor
- human approver
- countersignature or equivalent verification marker
- scope granted
- expiration
- audit reference or sanitized audit link allowed by
  [`docs/SECURITY.md`](docs/SECURITY.md)

If the approval record is missing or not verifiable, stop and record the
blocker in the active plan.

## Plans And Trials

- New active plans live in [`docs/plans/`](docs/plans/).
- Start planner artifacts from [`docs/plans/TEMPLATE.md`](docs/plans/TEMPLATE.md).
- Workflow trial and exception records live in
  [`docs/plans/trials/`](docs/plans/trials/).
- Trials are evidence records. They do not change repo authority on their own.
- Historical documents elsewhere under `docs/` do not set current workflow
  authority. If a historical artifact disagrees with the active plan under
  `docs/plans/` or the governing docs listed above, the active plan and
  governing docs win.

## Repo-Local Verification

Use the repository command surface; repo-local harness commands remain the
stable direct surface, and they must not be replaced with ad hoc scripts or
package-level CLI shims.

- default verification: `uv run poe verify`
- formatting: `uv run poe format`
- coverage-only check: `uv run poe coverage`
- runtime-sensitive research changes: `uv run poe verify-runtime`
- live checks: `uv run poe test-live`
- performance checks: `uv run poe perf-check`
- repo/document checks: `uv run poe repo-check`
- repo-local harness commands: `uv run pytest -q`, `uv run ruff check .`,
  `uv run mypy src`, `uv run python scripts/coverage_check.py`,
  `uv run python scripts/repo_check.py`,
  `uv run python scripts/notebook_validate.py`,
  `uv run python scripts/live_smoke.py`, `uv build`

Keep the hard gates intact:

- do not bypass architecture checks
- live tests are explicit-only and stay out of the default lane
- performance checks are explicit-only and stay out of the default lane
- runtime-sensitive research changes under
  `src/quantcraft/research/ta.py`,
  `src/quantcraft/research/adapters/execution_model.py`,
  `src/quantcraft/research/indicators/runtime/`,
  `src/quantcraft/research/indicators/pure/`,
  `src/quantcraft/research/application/backtest.py`, or
  `src/quantcraft/research/application/order_activation.py`
  must also run `uv run poe verify-runtime`
