# Active Execution Plans

This directory is a frozen historical index of plans that were still marked
active when the legacy execution-plan system was archived.

It is retained for historical discovery and internal consistency checks, not for
new active work.

The directory name and `index_status: active` metadata preserve the final
legacy state only. They do **not** mean this directory is part of the current
workflow authority.

## Metadata

- index_status: active

## Transition

New active work now lives under `docs/plans/`. This index remains only so the
legacy archive can stay navigable and mechanically consistent until it is
retired or fully migrated. Current runtime verification policy and approval
rules come from `AGENTS.md`, `docs/RELIABILITY.md`, and active plans under
`docs/plans/`, not from this directory.

## Plans

| Plan | Status | Note |
| --- | --- | --- |
| [`2026-04-11-backtest-runtime-hardening-implementation.md`](2026-04-11-backtest-runtime-hardening-implementation.md) | active | Historical carry-over: this plan was still marked active when the legacy system was frozen, but it is not the current plan authority. |
