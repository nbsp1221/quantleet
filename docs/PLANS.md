# Plan Index

This document is the top-level index for execution plans in `quantcraft`.

## Current Plan Locations

- Historical plans remain in `docs/plans/`
- Active execution plan index lives in `docs/exec-plans/active/`
- Completed execution plan index lives in `docs/exec-plans/completed/`

## Lifecycle Metadata

Execution-plan lifecycle is explicit, not implied by directory names alone.

- Every execution plan under `docs/exec-plans/` must include a `## Lifecycle` section with at least `- status: active|completed`
- The plan file status is the authoritative lifecycle field; its directory and index entry must match it
- If an `active` plan marks every slice complete, it must also include `- status_reason:` explaining why it remains active
- Active and completed indexes use an explicit `Plan / Status / Note` table so lifecycle state stays legible in one scan

## Transition Notes

The repository started with plans written directly under `docs/plans/`.

The new system keeps those historical plans discoverable while shifting new execution work toward indexed locations under `docs/exec-plans/`.

Durable architecture or contract drafts do not belong in `docs/plans/`; they belong in `docs/design-docs/`.

## Historical Plan Set

Current historical plans are stored in:

- `docs/plans/2026-03-11-dev-tools-bootstrap.md`
- `docs/plans/2026-03-13-binance-minimal-hardening.md`
- `docs/plans/2026-03-13-binance-notebook-validation-design.md`
- `docs/plans/2026-03-13-binance-notebook-validation.md`
- `docs/plans/2026-03-13-binance-ohlcv-minimal-design.md`
- `docs/plans/2026-03-13-binance-ohlcv-minimal.md`
- `docs/plans/2026-03-13-ccxt-runtime-dependency-design.md`
- `docs/plans/2026-03-13-ccxt-runtime-dependency.md`
- `docs/plans/2026-03-15-cross-exchange-comparison-notebook-design.md`
- `docs/plans/2026-03-15-cross-exchange-comparison-notebook-implementation.md`
- `docs/plans/2026-03-15-exchange-object-ohlcv-design.md`
- `docs/plans/2026-03-15-exchange-object-ohlcv-implementation.md`
- `docs/plans/2026-03-15-generalized-ccxt-exchange-design.md`
- `docs/plans/2026-03-15-generalized-ccxt-exchange-implementation.md`
- `docs/plans/2026-03-18-agent-first-repository-setup-design.md`
- `docs/plans/2026-03-18-agent-first-repository-setup.md`
- `docs/plans/2026-03-18-test-taxonomy-and-layout-design.md`
- `docs/plans/2026-03-18-test-taxonomy-and-layout.md`
- `docs/plans/2026-03-26-data-ingestion-implementation.md`
- `docs/plans/2026-03-27-ccxt-pagination-implementation.md`
- `docs/plans/2026-03-28-trade-summary-semantics-implementation.md`
- `docs/plans/2026-03-29-strategy-position-view-design.md`
- `docs/plans/2026-03-29-strategy-position-view-implementation.md`
- `docs/plans/2026-03-30-backtest-engine-design.md`
- `docs/plans/2026-03-30-backtest-engine-implementation.md`
- `docs/plans/2026-04-02-agent-harness-anti-gaming-design.md`
- `docs/plans/2026-04-02-backtest-throughput-benchmark-design.md`
- `docs/plans/2026-04-02-backtest-throughput-benchmark-implementation.md`
- `docs/plans/2026-04-03-rsi-performance-gate-design.md`
- `docs/plans/2026-04-03-rsi-performance-gate-implementation.md`
- `docs/plans/2026-04-08-ta-layer-refactor-design.md`
