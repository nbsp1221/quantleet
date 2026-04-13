# Legacy Control-Plane Final Retirement

- Date: 2026-04-14
- Task: remove retired legacy workflow artifacts from the active repo surface
- Status: `complete`
- Risk class: `Tier B`
- Requestor: repository owner
- Owner: Codex main agent

## Planner Contract

- Goal:
  - complete retirement of low-signal legacy control-plane artifacts so new agents see one active workflow surface
- Governing docs:
  - [`../../AGENTS.md`](../../AGENTS.md)
  - [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
  - [`../DESIGN.md`](../DESIGN.md)
  - [`../PLANS.md`](../PLANS.md)
  - [`../RELIABILITY.md`](../RELIABILITY.md)
  - [`../SECURITY.md`](../SECURITY.md)
  - [`2026-04-13-ce-workflow-migration-plan.md`](2026-04-13-ce-workflow-migration-plan.md)
  - [`2026-04-14-legacy-control-plane-retirement.md`](2026-04-14-legacy-control-plane-retirement.md)
- Why these are governing:
  - they define the active repo contract, surviving hard gates, and the evidence-backed rationale for retiring low-signal harness artifacts
- In-repo scope:
  - active docs that still mention retired control-plane artifacts
  - `docs/QUALITY_SCORE.md`
  - `docs/feedback-promotion-log.md`
  - repo-local helper code, scripts, and structure tests that still support those retired artifacts
- Out-of-repo scope:
  - none
- Tier A progression requested: `no`
- Approval record, if required:
  - not required; no Tier A or out-of-repo scope requested
- Verification commands:
  - `uv run pytest tests/structure/docs/test_plan_indexes.py tests/structure/docs/test_system_of_record_docs.py tests/structure/repo/test_no_flat_tests.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py tests/structure/repo/test_runtime_verification_lane.py -q`
  - `uv run python scripts/check_docs.py`
  - `uv run python scripts/repo_check.py`
  - `uv run poe verify`
- Success criteria:
  - active entry and routing docs no longer send agents to retired scorecard, promotion-log, or exec-plan artifacts
  - `docs/feedback-promotion-log.md` and `docs/QUALITY_SCORE.md` are removed after their rationale survives elsewhere
  - repo-local helper code, scripts, and tests no longer carry retired quality-score or exec-plan-lifecycle surfaces
  - surviving design docs preserve the rationale needed to understand why the older artifacts were retired
- Out of scope:
  - product behavior changes
  - financial-domain semantics
  - broad redesign of design or product-spec routing indexes
  - relocation of the historical `docs/exec-plans/` archive

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex review pass plus fresh subagent review
- Evaluator-owned done contract for this slice:
  - a new agent entering through `AGENTS.md` and the top-level docs sees one active workflow surface with no routed dependency on retired legacy control-plane artifacts
- Acceptance artifact location:
  - this active plan plus fresh verification output cited in the evaluator review
- How the generator and evaluator agreed on done before execution:
  - legacy artifacts may remain only as unreachable historical records; if active docs, repo-local helper code, or structure tests still route to them as current workflow authority, the slice is not done
- Checks the evaluator will use:
  - fresh targeted structure/docs tests
  - `scripts/check_docs.py`
  - repo-local review against current repo contract and simplification criteria
- Auto-fail conditions:
  - leaving contradictory active-vs-retired wording in top-level docs
  - deleting rationale without preserving the replacement explanation in surviving governing docs
  - leaving retired helper code or scripts alive without an active caller

## Generator Work Log

- Planned slice order:
  - decide the final disposition of `QUALITY_SCORE.md` and `feedback-promotion-log.md`
  - remove active routing to retired legacy artifacts from top-level docs
  - absorb the remaining rationale into surviving governing docs
  - retire matching helper code, scripts, and structure tests
  - run targeted checks and the default verification bundle
- Notes:
  - `docs/exec-plans/` remains as an unreachable historical archive because deleting or relocating it would create unnecessary churn in historical records
- Blockers or scope changes:
  - docs-only cleanup originally left `docs/QUALITY_SCORE.md` in place because tooling and tests still referenced it; that dependency was removed in the same slice, so the file was deleted before final review

## Evaluator Review

- Findings:
  - active entry docs no longer route new agents to `QUALITY_SCORE.md`, `feedback-promotion-log.md`, or `docs/exec-plans/`
  - `docs/feedback-promotion-log.md` and `docs/QUALITY_SCORE.md` carried no unique active rationale after their surviving policy was absorbed into the governing design docs, so both files were removed
  - repo-local code no longer exposes quality-score or exec-plan lifecycle helper surfaces, and the matching retirement tests and update script were removed
  - `docs/exec-plans/` remains only as a historical archive and is no longer routed from active entry docs or active repo-local checks
- Verification evidence:
  - `uv run pytest tests/structure/docs/test_plan_indexes.py tests/structure/docs/test_system_of_record_docs.py tests/structure/repo/test_no_flat_tests.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py tests/structure/repo/test_runtime_verification_lane.py -q`
  - `uv run python scripts/check_docs.py`
  - `uv run python scripts/repo_check.py`
  - `uv run poe verify`
- Final disposition:
  - complete
