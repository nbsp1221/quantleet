# Implemented Scope Sync Plan

> **For Codex:** REQUIRED SUB-SKILLS: use `subagent-driven-development` to execute this plan slice-by-slice, and require every worker/reviewer subagent to read `docs/references/openai-harness-engineering.md` plus the slice-relevant architecture/spec docs before touching code.

**Goal:** Sync the repository control plane with the already-implemented Backtest MVP and Research Ergonomics slices so agents read accurate current-scope docs and status maps.

**Architecture:** This batch does not add product behavior. It aligns system-of-record documents with the code that already exists, then adds narrow structure checks so the same drift is harder to reintroduce. The work stays in docs, repo checks, and structure tests.

**Tech Stack:** Markdown docs, `pytest` structure tests, repo-local `scripts/` harness

## Lifecycle

- status: completed
- completed_on: 2026-03-25

## Current Status

- Slice 1: complete
- Slice 2: complete

## Required Reading Before Any Task

- `AGENTS.md`
- `docs/references/openai-harness-engineering.md`
- `docs/design-docs/quantcraft-architecture.md`
- `docs/design-docs/architecture-governance.md`
- `docs/product-specs/backtest-mvp.md`
- `docs/product-specs/research-ergonomics.md`
- `docs/QUALITY_SCORE.md`

## Non-Negotiable Guardrails

- Do not change runtime product behavior in this batch.
- Do not expand product scope beyond what is already implemented.
- Do not mark future or draft work as implemented.
- Keep changes inside docs, repo checks, and structure tests unless a control-plane import surface absolutely requires a tiny code edit.

## Slice Plan

### Slice 1: Promote Current Implemented Scope Docs

**Intent:** Make system-of-record docs describe the current implemented scope instead of the old market-data-only baseline.

**Ownership:**

- `README.md`
- `docs/product-specs/`
- `docs/QUALITY_SCORE.md`

**Acceptance:**

- `README.md` reflects that the repository now includes market-data utilities, the implemented Backtest MVP, and the implemented Research Ergonomics surface.
- `docs/product-specs/backtest-mvp.md` and `docs/product-specs/research-ergonomics.md` declare implemented status, not approved-next-slice status.
- `docs/product-specs/index.md` marks those specs as implemented/current implemented scope.
- `docs/product-specs/backtest.md` describes the current implemented backtest baseline instead of an approved-next-slice orientation.
- `docs/QUALITY_SCORE.md` freshness metadata and area scores/notes are updated to match current repository evidence conservatively.

### Slice 2: Add Drift Guards For Implemented-Scope Control Docs

**Intent:** Add narrow checks so implemented-scope docs do not silently fall behind the code again.

**Ownership:**

- `tests/structure/docs/`
- `tests/structure/repo/`

**Acceptance:**

- A structure test verifies that the current implemented-scope product-spec index includes the implemented backtest and research specs.
- A structure test verifies that `README.md` mentions the implemented backtest and research surfaces in its current-scope section.
- Existing structure tests remain aligned with the new implemented/current-scope wording.
