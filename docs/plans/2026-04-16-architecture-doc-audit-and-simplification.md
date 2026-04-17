# Active Plan

- Date: `2026-04-16`
- Task: `Audit and simplify the refreshed architecture docs until third-party review reaches approved state`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - run an exhaustive review of the newly refreshed architecture and governance docs
  - simplify wording and structure where needed without changing intended meaning
  - use read-only subagent review fan-out and parent synthesis loops until no material findings remain
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/core-beliefs.md`
  - `docs/design-docs/quantcraft-architecture.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/architecture-governance.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/backtest.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/data-ingestion.md`
  - `docs/references/openai-harness-engineering.md`
  - `Python 아키텍처 구현 질문.md`
  - `docs/plans/2026-04-16-architecture-doc-foundation-refresh.md`
- Why these are governing:
  - they contain the refreshed architecture truth, the workflow protocol that must remain intact, the external reference used to justify the doc shape, and the user-approved architecture conclusion that must remain consistent
- In-repo scope:
  - audit the changed governing docs for:
    - readability and naturalness
    - unnecessary or duplicated content
    - fit with the harness-engineering reference and repo workflow
    - section ordering and structure quality
    - cross-document consistency
  - apply behavior-preserving simplifications to the docs
  - run at least one review fan-out and one re-review fan-out
- Out-of-repo scope:
  - code changes
  - package moves
  - `.importlinter` implementation
  - new architectural decisions beyond the already approved capability-first v0 direction
- Tier A progression requested: `no`
- Approval record, if required:
  - not required for this documentation-only review slice
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - no unresolved material findings remain across readability, protocol-fit, structure, and consistency lenses
  - the docs remain consistent with the capability-first v0 architecture
  - the docs still respect the harness-engineering principle that `AGENTS.md` is a concise map and `docs/` is the deeper system of record
  - repo/document checks pass after the final simplification pass
- Out of scope:
  - proving source code conforms to the new architecture
  - writing the code migration plan

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - done means a full parent synthesis of read-only reviewer findings has been completed, all required fixes have been applied, a second review pass finds no remaining blocking or medium-severity issues, and repo/document verification passes
- Acceptance artifact location:
  - `docs/plans/2026-04-16-architecture-doc-audit-and-simplification.md`
- How the generator and evaluator agreed on done before execution:
  - this plan fixes the review criteria, the required review loop, and the verification command before edits begin
- Checks the evaluator will use:
  - subagent review fan-out with evidence-backed findings
  - parent synthesis with required-fix versus advisory separation
  - re-review after fixes
  - `uv run poe repo-check`
- Auto-fail conditions:
  - reviewer output is accepted without evidence
  - only one review pass is performed
  - conflicting document guidance remains unresolved
  - verification is skipped or failing

## Generator Work Log

- Planned slice order:
  - gather current changed-doc set
  - run first read-only review fan-out
  - synthesize and fix required issues
  - run second read-only review fan-out
  - apply any last narrow simplifications
  - run repo/document verification
- Notes:
  - write ownership stays with the parent agent only
  - review agents stay read-only and must return evidence
- Blockers or scope changes:
  - first fan-out found two medium issues and two low issues; the final slice expanded only narrowly to fix those findings and the repo-check regression introduced while simplifying `AGENTS.md`

## Evaluator Review

- Findings:
  - first review fan-out synthesis:
    - required fix: `AGENTS.md` was still too dense for a harness-style entry surface and needed a clearer map-first shape
    - required fix: `docs/design-docs/architecture-governance.md` said “four distinct document classes” while listing six items
    - required fix: transitional backtest-ownership caveats were repeated too heavily across current-scope product specs
    - advisory but fixed: `docs/product-specs/backtest-mvp.md` repeated execution semantics across adjacent sections more than necessary
  - simplification pass outcomes:
    - `AGENTS.md` was tightened while preserving the repo protocol and repo-local command surface
    - `architecture-governance.md` now describes governing documents without the taxonomy mismatch
    - product specs now point more cleanly to architecture docs for long-lived ownership instead of repeating the same caveat
    - `backtest-mvp.md` now presents synthetic execution path and fill rules in one canonical block
    - `data-ingestion.md` duplicate `source.load() returns BarSeries` wording was removed
    - a temporary repo-check regression caused by over-simplifying the harness-command wording in `AGENTS.md` was corrected before final signoff
  - final review state:
    - reviewer 1 (`Darwin`): `Approved: no material findings.`
    - reviewer 2 (`Ampere`): `Approved: no material findings.`
    - reviewer 3 (`Galileo`): `Approved: no material findings.`
- Verification evidence:
  - first review fan-out:
    - `Darwin` returned 2 medium/low simplification findings with file-level evidence
    - `Ampere` returned 2 medium/low protocol-fit findings with file-level evidence
    - `Galileo` returned `No findings.` for consistency on the first pass
  - second review fan-out after fixes:
    - `Ampere` returned `No material findings.`
    - `Galileo` returned `No material findings.`
    - `Darwin` returned one low duplicate-line finding in `docs/product-specs/data-ingestion.md`
  - final signoff fan-out:
    - `Darwin` returned `Approved: no material findings.`
    - `Ampere` returned `Approved: no material findings.`
    - `Galileo` returned `Approved: no material findings.`
  - `uv run poe repo-check` -> `repository checks passed`
- Final disposition:
  - `accepted`
