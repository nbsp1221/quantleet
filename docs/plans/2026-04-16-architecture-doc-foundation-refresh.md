# Active Plan

- Date: `2026-04-16`
- Task: `Refresh governing architecture and terminology docs for the capability-first v0 architecture`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - replace the current layer-first architecture story with the approved capability-first v0 architecture
  - define the repository's canonical contexts, product surfaces, terminology, and doc roles before any code migration work begins
  - keep this slice documentation-only so later codebase migration can be planned against stable governing docs
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/core-beliefs.md`
  - `docs/design-docs/quantcraft-architecture.md`
  - `docs/design-docs/architecture-governance.md`
  - `docs/product-specs/index.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `Python 아키텍처 구현 질문.md`
- Why these are governing:
  - they define the current repo contract, long-lived architecture authority, document-role rules, and the user-approved external-architecture conclusion that this slice must promote into repo truth
- In-repo scope:
  - rewrite or add governing docs that define:
    - top-level capability contexts
    - product surfaces versus engine package boundaries
    - terminology and naming rules
    - document roles for architecture versus implementation plans
    - initial import-boundary intent for future mechanical enforcement
  - update routing indexes so agents can discover the new authority quickly
- Out-of-repo scope:
  - code moves
  - package renames
  - `.importlinter` implementation
  - detailed migration sequencing for source files
- Tier A progression requested: `no`
- Approval record, if required:
  - not required for this documentation-only architecture slice
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - the governing docs state the capability-first v0 architecture clearly and without contradiction
  - `backtest` is documented as a peer runtime context rather than a `research` sub-layer target
  - product surfaces such as `apps/api` are distinguished from `src/quantcraft` engine/package boundaries
  - terminology guidance covers `integrations`, `_shared`, asset-neutral naming, and facade/public API intent
  - design-doc indexes route readers to the new authority
  - repo/document checks pass
- Out of scope:
  - proving the codebase already matches the new docs
  - file-by-file migration decisions

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - done means the repository's governing docs consistently describe the same capability-first v0 architecture and document-role model, with no remaining top-level contradiction that would misroute later code migration work
- Acceptance artifact location:
  - `docs/plans/2026-04-16-architecture-doc-foundation-refresh.md`
- How the generator and evaluator agreed on done before execution:
  - this plan fixes the slice as documentation-only, names the target authorities, and constrains verification to repo/document checks before edits begin
- Checks the evaluator will use:
  - diff review against the current architecture docs
  - cross-document consistency review
  - `uv run poe repo-check`
- Auto-fail conditions:
  - the updated docs still present both layer-first and capability-first structures as simultaneous authorities
  - the docs imply code has already migrated when it has not
  - verification is skipped or failing

## Generator Work Log

- Planned slice order:
  - identify the minimum governing docs to rewrite
  - promote the capability-first v0 architecture into the architecture docs
  - add a durable terminology/naming reference if needed
  - update routing/index docs
  - run repo/document verification
- Notes:
  - this slice intentionally stops before implementation planning for code migration
- Blockers or scope changes:
  - cross-document consistency required narrow supporting edits in `docs/design-docs/backtest-execution-semantics.md` and the current backtest/research-facing product specs so the new long-lived architecture would not contradict current slice docs

## Evaluator Review

- Findings:
  - `AGENTS.md` now explicitly treats itself as a map and routes package-topology questions to long-lived design docs instead of duplicating architecture detail
  - `ARCHITECTURE.md` and `docs/design-docs/quantcraft-architecture.md` now agree on the same capability-first v0 baseline:
    - `data`
    - `trading`
    - `research`
    - `backtest`
    - `execution`
    - `integrations`
    - `_shared`
  - a new governing doc, `docs/design-docs/package-topology-and-naming.md`, fixes package topology, naming, `api.py` facade policy, `_shared` policy, and `integrations` policy
  - design-doc routing and governance docs were updated so agents can discover the new authority without treating old layer-first guidance as equal authority
  - current implemented-scope product specs now explicitly state the transition:
    - public `BacktestEngine` entry still lives under `research`
    - long-lived runtime ownership belongs to the peer `backtest` context
  - the docs do not claim that the current source tree has already migrated; they consistently mark the codebase as transitional
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
- Final disposition:
  - `accepted`
