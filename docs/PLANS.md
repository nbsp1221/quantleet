# Plan Pointers

This document is a lightweight location guide for plans in `quantcraft`. It is
not a lifecycle tracker.

- New active plans live in [`plans/`](plans/).
- Start active plan work from [`plans/TEMPLATE.md`](plans/TEMPLATE.md).
- Workflow trial and exception artifacts live in [`plans/trials/`](plans/trials/).
- Historical material elsewhere under `docs/` does not route current work.

For current work:

- keep the active task plan in `docs/plans/`
- record Tier A or repo-scope expansion approval in that active plan when
  required by [`../AGENTS.md`](../AGENTS.md)
- Durable architecture or contract drafts do not belong in `docs/plans/`; they
  belong in [`design-docs/`](design-docs/).
- Older records in `docs/plans/` may still contain archived design or decision
  material from before the current governance model. Treat those as audit
  history, not as active architecture authority.
- If a historical document conflicts with an active plan, trust `docs/plans/`
  plus the governing docs linked from `AGENTS.md`.

For workflow experiments:

- trial records are evidence artifacts, not authority by themselves
- host-unavailable or gate-blocked records count as failures or exceptions, not
  migration passes

For Compound Engineering migration work:

- the governing migration plan is
  [`plans/2026-04-13-ce-workflow-migration-plan.md`](plans/2026-04-13-ce-workflow-migration-plan.md)
- start new trial records from [`plans/trials/TEMPLATE.md`](plans/trials/TEMPLATE.md)
