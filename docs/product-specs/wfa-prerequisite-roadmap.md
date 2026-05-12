# WFA Prerequisite Roadmap

## Status

- Status: `draft`
- Class: `product-roadmap`
- Scope: ordered prerequisite product-spec sequence before walk-forward analysis
  implementation resumes

Related documents:

- [strategy-configuration-contract.md](strategy-configuration-contract.md)
- [direct-backtest-class-config-api.md](direct-backtest-class-config-api.md)
- [direct-backtest-class-config-api-test-scenarios.md](direct-backtest-class-config-api-test-scenarios.md)
- [walk-forward-analysis.md](walk-forward-analysis.md)
- [walk-forward-analysis-readiness.md](walk-forward-analysis-readiness.md)
- [research-ergonomics.md](research-ergonomics.md)
- [parameter-exploration.md](parameter-exploration.md)
- [backtest-mvp.md](backtest-mvp.md)
- [../design-docs/unified-strategy-runtime-design.md](../design-docs/unified-strategy-runtime-design.md)
- [../design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)

This document is not an implementation plan and not the product spec for
`StrategyConfig`. It records the agreed prerequisite sequence so that the
project can discuss the next product spec without losing the larger path back to
walk-forward analysis.

## Decision

Walk-forward analysis remains paused.

The next product-spec focus is not WFA itself. The next product-spec focus is
the strategy configuration contract that WFA, `ParameterStudy`, reporting, paper
trading, and future live trading should be able to share.

The agreed sequence is:

1. Unified Strategy Configuration Contract
2. ParameterStudy Strategy API Migration
3. Reporting Config Source Of Truth
3.5. Direct Backtest Class+Config API Alignment
4. WFA Resume Spec

This sequence is a product-planning dependency chain, not a commitment to
implement every slice in one batch.

## Why This Roadmap Exists

WFA was paused because implementing it too early would have hardened the old
callable construction research API into a larger public contract. The
actual blocker is not the walk-forward algorithm. The actual blocker is the
absence of a canonical strategy configuration contract shared by backtesting,
research, paper trading, and future live trading.

The risk is easy to miss during the first prerequisite slice. If the project
only focuses on the first `StrategyConfig` discussion, it may forget why that
work was started:

- WFA needs fresh strategy creation for train candidates and selected test runs.
- `ParameterStudy` now teaches `strategy=StrategyClass` plus `StrategyConfig`
  as the canonical public path.
- Stage 3 replaced report-authored `strategy_parameters` with
  `BacktestReport.run.strategy_config`, using the framework-owned execution
  config snapshot.
- Direct `BacktestEngine.run(...)` now uses `strategy=StrategyClass` plus
  `config=StrategyConfig(...)`, matching the construction model WFA will need.
- The long-lived runtime direction wants one strategy codebase to move through
  research, backtest, paper, and live workflows.

This roadmap keeps those dependencies visible while still letting each next
spec stay small.

## Roadmap Stage 1: Unified Strategy Configuration Contract

Governing product spec:

- [strategy-configuration-contract.md](strategy-configuration-contract.md)

Purpose:

- Define the long-lived public contract for declaring strategy configuration and
  creating fresh strategy instances from selected config values.

Primary questions:

- Should Quantleet expose a separate `StrategyConfig` class, class-level
  strategy parameters, descriptor-based parameters, or another minimal contract?
- What is the relationship between `Strategy` and the config object?
- What values are true strategy config values versus runtime dependencies or
  environment settings?
- How does the framework create a fresh strategy instance for one run?
- How should custom construction needs preserve the framework-owned
  `StrategyConfig` contract?

Required product outcome:

- A product spec that defines the canonical user-facing strategy configuration
  model.
- A clear source of truth for default config values and valid config fields.
- A decision on whether study-level search spaces stay separate from strategy
  config schema.
- A clear statement that this stage does not implement WFA.

Non-goals for this stage:

- WFA implementation.
- Full paper/live runner design.
- A general dependency-injection container.
- Objective alias policy.
- OOS summary/report semantics.

## Roadmap Stage 2: ParameterStudy Strategy API Migration

Purpose:

- Align `ParameterStudy` with the canonical strategy configuration contract so
  WFA and existing parameter exploration do not teach different strategy
  construction models.

Primary questions:

- Should `ParameterStudy(..., strategy=StrategyClass)` become the canonical
  public path?
- Stage 2 resolved this as a breaking migration: the old callable construction
  keyword is not supported in active public API.
- How should error messages guide users from old factory examples to the new
  canonical path?
- What tests and public docs must change to keep the first-beta research story
  coherent?

Required product outcome:

- A migration product spec that defines the new `ParameterStudy` public input
  surface.
- A clear breaking-migration policy for old callable construction examples.
- A decision that the migration is breaking before public beta release.
- A clear preservation rule for fresh strategy instance guarantees.

Non-goals for this stage:

- New optimization algorithms.
- WFA fold generation.
- Paper/live execution.
- Changing backtest matching or trading semantics.

## Roadmap Stage 3: Reporting Config Source Of Truth

Purpose:

- Ensure report metadata records the actual config used for a run rather than
  relying on strategy-authored metadata that may drift from execution inputs.

Primary questions:

- Stage 3 resolved that reports expose the framework-owned config snapshot as
  `report.run.strategy_config`.
- Stage 3 resolved that `Strategy.parameters()` is removed from the canonical
  strategy surface and ignored by reporting.
- Stage 3 resolved that selected study values, defaults, and report metadata
  line up through the full materialized `StrategyConfig` snapshot.
- Fold-level WFA selected parameters should line up with per-run reports through
  the same `strategy_config` snapshot vocabulary.
- Report config snapshots remain JSON-scalar mappings in the first-beta scope.

Required product outcome:

- A reporting product spec that defines config snapshot ownership.
- A rule that selected parameters and report metadata cannot silently disagree.
- A breaking pre-beta compatibility position: `Strategy.parameters()` is not a
  report metadata fallback and is no longer part of the canonical strategy
  surface.
- A record/export expectation that future WFA fold results can reuse.

Non-goals for this stage:

- Full WFA result model.
- Continuous OOS account semantics.
- New report metrics unrelated to config provenance.

## Roadmap Stage 3.5: Direct Backtest Class+Config API Alignment

Governing product spec:

- [direct-backtest-class-config-api.md](direct-backtest-class-config-api.md)
- [direct-backtest-class-config-api-test-scenarios.md](direct-backtest-class-config-api-test-scenarios.md)

Purpose:

- Track the Stage 3.5 decision that direct `BacktestEngine.run(...)` accepts a
  strategy class and optional `StrategyConfig` before WFA resumes.
- Align normal direct backtests with the strategy-construction model already
  used by `ParameterStudy`.
- Prevent WFA from becoming the first public surface that must bridge direct
  strategy instances and framework-created configured strategy instances.

Plain-language summary:

- Direct backtests receive a strategy class and optional config.
- `ParameterStudy` already receives a strategy class and creates fresh
  configured strategy instances for each run.
- WFA will need the same fresh-instance behavior many times across folds.
- Stage 3.5 makes direct backtests teach `strategy=StrategyClass` plus
  `config=...`.

Resolved product decisions:

- `BacktestEngine.run(strategy=StrategyClass, config=...)` is the primary
  direct-backtest API.
- Direct strategy instances are removed from the current public API rather than
  preserved as a compatibility path.
- `config` accepts `StrategyConfig` instances only; plain dict config input is
  rejected.
- Omitted `config` means the engine materializes `StrategyClass.config_type()`.
- `ParameterStudy` should call the direct class-plus-config API instead of
  constructing strategy instances internally.

Required product outcome:

- A product spec that closes the direct-backtest class-plus-config API decision.
- A separate test-scenarios spec that defines the verification target before
  implementation planning.
- A clear documentation policy for the primary direct-backtest example style.
- A test-scenario target for strategy class, config, instance, report snapshot,
  and error-message behavior.
- Confirmation that WFA can rely on one framework-owned fresh strategy
  construction model.

Non-goals for this stage:

- WFA implementation.
- Fold generation, OOS summary, or WFA result-model decisions.
- Paper/live execution design.
- Changes to trading or execution semantics.

## Roadmap Stage 4: WFA Resume Spec

Purpose:

- Resume walk-forward analysis product planning on top of the resolved strategy
  configuration, reporting, and direct-backtest construction contracts.

Primary questions:

- What exact public constructor does `WalkForwardStudy` use after the strategy
  config migration?
- How does each fold create train candidate strategies and selected test
  strategies?
- How does WFA compose the Stage 3.5 direct-backtest API without teaching a
  separate construction model?
- Which output concepts are first-slice required: `oos_summary`, fold records,
  selected parameters by fold, parameter stability, diagnostics?
- Which WFA readiness blockers remain after the prior stages?
- Which deferred items remain outside the first WFA implementation slice?

Required product outcome:

- An updated WFA product spec or resume addendum.
- Confirmation that WFA no longer hardens a transitional strategy construction
  API.
- A technical implementation plan can then be written from the resumed product
  spec.

Non-goals for this stage:

- Reopening the decision that WFA is a Validation Study.
- Centering the result UX on `best_params`.
- Treating `oos_report` as continuous-account output unless those semantics are
  explicitly designed.

## Dependency Rules

- Stage 1 must happen before Stage 2.
- Stage 2 must happen before WFA implementation resumes.
- Stage 3 may be specified after Stage 2 or in parallel with late Stage 2
  planning, but WFA cannot depend on ambiguous report metadata.
- Stage 3.5 must happen after Stage 3 and before Stage 4 unless a human
  decision explicitly records why direct-backtest class-plus-config API
  alignment no longer blocks WFA planning.
- Stage 4 must not start until the project has either completed the relevant
  prior specs or explicitly records why a prior stage no longer blocks WFA.

The roadmap allows later human decisions to reorder or merge stages, but only
through an explicit update to this document or a superseding product spec. Silent
scope drift is not acceptable.

## Current Priority Read

| Stage | Urgency | Impact | Delay Cost | Current Priority |
| --- | --- | --- | --- | --- |
| Unified Strategy Configuration Contract | high | high | high | P0 |
| ParameterStudy Strategy API Migration | high | high | high | P0 |
| Reporting Config Source Of Truth | medium | high | medium-high | Completed |
| Direct Backtest Class+Config API Alignment | medium-high | high | high | Spec decisions closed; implementation planning next |
| WFA Resume Spec | medium | high | high after prerequisites | Blocked on Stage 3.5 completion |

## Guardrails

- Do not treat this roadmap as permission to implement WFA.
- Do not use this roadmap to skip the dedicated product spec for Stage 1.
- Do not solve Stage 1 by preserving the current legacy callable construction API path merely
  because it is already implemented.
- Do not solve Stage 1 by overbuilding paper/live infrastructure before the
  strategy config contract is clear.
- Do not let `StrategyConfig` absorb study-specific search spaces unless the
  Stage 1 product spec deliberately chooses that model.
- Do not let report metadata continue to rely on user-authored duplication if a
  framework-owned config snapshot exists.

## Success Conditions

This roadmap is successful when:

- future work on `StrategyConfig` can point to the larger WFA-unblocking
  sequence
- the project can discuss Stage 1 without forgetting Stages 2 through 4
- the WFA pause reason remains explicit
- product-spec routing sends WFA-unblocking work through this roadmap
- implementation plans for any stage can cite which stage they are executing and
  which later stages remain unresolved

## Open Questions

- Should Stage 1 use the title `Unified Strategy Configuration Contract` or
  `Strategy Configuration Contract`?
- Stage 2 resolved that the old callable construction path is removed from
  active code, tests, examples, and public docs.
- Stage 3 resolved that report metadata records
  `BacktestReport.run.strategy_config`.
- Stage 3.5 resolves that direct backtests use strategy classes plus optional
  `StrategyConfig` objects.
- WFA can safely resume product planning after Stage 3.5 is implemented or
  explicitly deferred by a human decision.
