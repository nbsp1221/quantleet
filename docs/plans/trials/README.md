# Trial Artifacts

This directory holds repo-local evidence records for workflow or authority-change
experiments.

Two record types are valid here:

- `authority-trial`: a scored comparison that can count toward a migration
  evidence gate
- `exception-record`: a blocked or host-unavailable run that documents why the
  trial could not legitimately count

For the Compound Engineering migration, Phase 1 and 1.5 use artifacts at:

- `docs/plans/trials/YYYY-MM-DD-ce-authority-trial.md`

Start from [TEMPLATE.md](./TEMPLATE.md). The governing plan for this trial set
is [2026-04-13-ce-workflow-migration-plan.md](../2026-04-13-ce-workflow-migration-plan.md).

Exception records are useful operational evidence, but they do **not** satisfy
the migration evidence gate by themselves.

Use this directory for workflow experiments only. It is not the active plan
system for ordinary repository work.
