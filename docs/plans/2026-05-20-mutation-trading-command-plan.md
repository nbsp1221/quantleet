# Trading Mutation Command Plan

- Date: 2026-05-20
- Task: Add a manual `uv run poe mutation-trading` command for targeted trading mutation testing.
- Status: `complete`
- Risk class: `Tier A`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Add a stable repo-local Poe command that runs mutmut against the
  `trading` kernel only, without adding mutation testing to the default
  `check` lane yet.
- Governing docs:
  - `AGENTS.md`
  - `ARCHITECTURE.md`
  - `docs/PLANS.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/references/testing.md`
- Why these are governing:
  - `AGENTS.md` requires a written active plan and repo-local command surface.
  - `ARCHITECTURE.md` identifies `trading` as the shared trading kernel and a
    Tier A context.
  - `docs/PLANS.md` defines active plan location.
  - `docs/RELIABILITY.md` defines local check lanes and Tier A safety
    expectations.
  - `docs/SECURITY.md` defines Tier A human approval expectations.
  - `docs/references/testing.md` defines testing command lane policy.
- In-repo scope:
  - Add a Poe task named `mutation-trading`.
  - Add mutmut configuration scoped to `src/quantleet/trading` and
    `tests/unit/trading`.
  - Ignore mutmut's local `mutants/` run directory.
  - Keep `check` unchanged in this slice.
  - Add structure-test coverage for the new command contract.
  - Run the new command and focused structure tests.
- Out-of-repo scope:
  - No CI workflow changes.
  - No automatic changed-file mutation gate.
  - No mutation baseline or survivor ratchet.
  - No edits to trading production code.
- Tier A progression requested: `yes`
- Approval record, if required:
  - Requestor: user
  - Human approver: user
  - Check marker: `uv run poe mutation-trading`
  - Granted scope: repo-local manual mutation command targeting `trading` only
  - Expiration: this task slice
  - Audit reference: user request on 2026-05-20 to add and verify
    `uv run poe mutation-trading`
- Verification commands:
  - `uv run poe mutation-trading`
  - `uv run pytest tests/structure/repo/test_poe_task_contracts.py -q`
  - `uv run poe repo-check`
- Success criteria:
  - `uv run poe mutation-trading` is available.
  - The command runs mutmut against `src/quantleet/trading`.
  - The command uses `tests/unit/trading` as the targeted pytest selection.
  - The default `check` sequence remains unchanged.
  - Focused structure checks pass.
  - The new mutation command completes and prints mutation results.
- Out of scope:
  - Hard-failing on a mutation score threshold.
  - Automatically running mutation testing from `check`.
  - Solving existing surviving mutants.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Confirm the command exists,
  remains manual, targets only the trading kernel, and runs successfully from a
  clean command invocation.
- Acceptance artifact location: this plan's Evaluator Review section.
- How the generator and evaluator agreed on done before execution: The planner
  contract above fixes the command name, target scope, non-goals, and check
  evidence before edits.
- Checks the evaluator will use:
  - `uv run poe mutation-trading`
  - `uv run pytest tests/structure/repo/test_poe_task_contracts.py -q`
  - `uv run poe repo-check`
- Auto-fail conditions:
  - `check` is changed to include mutation testing in this slice.
  - The mutmut configuration mutates outside `src/quantleet/trading`.
  - The mutation command cannot complete.
  - Structure tests or repo-check fail due to this change.

## Generator Work Log

- Planned slice order:
  - Add Poe and mutmut configuration.
  - Add structure-test contract.
  - Run focused verification.
  - Record evaluator evidence.
- Notes:
  - This is intentionally a manual command first; changed-file automation is a
    later slice after the manual target is stable.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings.
  - `mutation-trading` is a manual Poe task and is not included in the default
    `check` sequence.
  - Mutmut configuration is scoped to `src/quantleet/trading` with
    `tests/unit/trading`.
  - `.gitignore` excludes `/mutants/`, which mutmut creates as local run data.
- Verification evidence:
  - `uv run pytest tests/structure/repo/test_poe_task_contracts.py -q`:
    `12 passed in 0.04s`.
  - `uv run poe repo-check`: `repository checks passed`.
  - `uv run poe mutation-trading`: completed successfully; generated
    `571` mutants across `10` trading files, with `450` killed and `121`
    survived at `65.09 mutations/second`.
- Final disposition:
  - Accepted for this slice.
