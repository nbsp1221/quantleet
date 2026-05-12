# Walk-Forward Analysis Readiness Review

## Status

- Status: `draft`
- Class: `product-readiness-analysis`
- Scope: blockers, risks, and prioritization inputs that must be reviewed
  before resuming WFA implementation

Related documents:

- [walk-forward-analysis.md](walk-forward-analysis.md)
- [wfa-prerequisite-roadmap.md](wfa-prerequisite-roadmap.md)
- [direct-backtest-class-config-api.md](direct-backtest-class-config-api.md)
- [research-ergonomics.md](research-ergonomics.md)
- [parameter-exploration.md](parameter-exploration.md)
- [parameter-exploration-test-scenarios.md](parameter-exploration-test-scenarios.md)
- [backtest-mvp.md](backtest-mvp.md)
- [../design-docs/unified-strategy-runtime-design.md](../design-docs/unified-strategy-runtime-design.md)
- [../design-docs/package-topology-and-naming.md](../design-docs/package-topology-and-naming.md)

This document is not a refactoring spec and not an implementation plan. It is
the analysis queue created when WFA planning exposed deeper product-contract
questions. Its job is to list the issues that may block or distort WFA, then
provide a way to prioritize which prerequisite problem should be solved first.

The ordered prerequisite sequence is recorded separately in
[wfa-prerequisite-roadmap.md](wfa-prerequisite-roadmap.md). Read that roadmap
before writing the next product spec so the project does not solve the first
strategy-configuration problem and lose the later `ParameterStudy`, reporting,
and WFA-resume steps.

## Why This Document Exists

The original next feature was walk-forward analysis. During product-spec
discussion, the project reached a stable WFA product position:

- WFA should be a Validation Study.
- The public name should be `WalkForwardStudy`.
- The user-facing product should avoid `WalkForwardOptimizer`.
- MVP output should emphasize `oos_summary`, not `best_params`.
- Advanced splitter/CV toolkit concepts should stay internal or delayed.

The discussion also revealed a deeper concern: WFA depends on a strategy
parameter contract that must not harden ad hoc construction. Stage 2 resolves
the active parameter exploration surface around `strategy=StrategyClass` plus
`StrategyConfig`, which is the contract future WFA work should build on.

Pausing WFA prevents an expedient implementation path from becoming an
accidental long-lived API.

## Current Known Facts

- `Strategy` is already the public strategy authoring base class for the
  research layer.
- `BacktestEngine.run(...)` now receives a `Strategy` class plus optional
  `StrategyConfig` instance after Stage 3.5 alignment.
- `ParameterStudy(...).grid_search(...)` receives a `Strategy` class,
  materializes `StrategyConfig` snapshots, and constructs a fresh strategy
  instance for each admissible candidate.
- `BacktestResult.report` records the framework-owned
  `run.strategy_config` snapshot, not strategy-authored parameter metadata.
- The current beta parameter exploration contract is implemented and
  documented; it is not automatically wrong, but it may be transitional.
- The longer-lived runtime direction aims for one strategy codebase to move
  through research, backtest, paper, and live workflows.

## Blocker Inventory

### B1. Canonical Strategy Configuration Contract

Question:

- What is the long-lived public contract for declaring strategy parameters and
  injecting parameter values into fresh strategy instances?

Why it matters for WFA:

- WFA will instantiate strategies many times across train candidates and test
  folds.
- WFA must not reintroduce the old callable construction path as its primary
  public contract.
- If WFA exposes `strategy=StrategyClass` before the config contract is
  defined, implementation will invent normalization rules under pressure.

Known candidate directions:

- `Strategy` plus explicit `StrategyConfig`.
- Backtrader-style class-level `params`.
- Freqtrade-style parameter descriptors.
- Config-backed `Strategy` plus `StrategyConfig` as the active contract.

Initial assessment:

- Urgency: high
- Impact: high
- Reversibility: medium
- Suggested priority: P0 candidate

### B2. Relationship Between Config Schema And Study Parameters

Question:

- Should `StrategyConfig` only define defaults and valid fields, while
  `parameters={...}` defines the search space for a specific study, or should
  search spaces live inside the strategy/config class?

Why it matters for WFA:

- WFA needs one clear source for candidate values.
- The same strategy may need different search spaces per market, timeframe, or
  experiment.
- Putting search space into config can improve discoverability but can also
  make experiments harder to vary without editing strategy code.

Initial assessment:

- Urgency: high
- Impact: high
- Reversibility: medium
- Suggested priority: P0 candidate

### B3. ParameterStudy Migration Strategy

Question:

- How should WFA compose the config-backed `ParameterStudy` contract without
  expanding the public API prematurely?

Why it matters for WFA:

- WFA should compose `ParameterStudy` or the same underlying parameter
  exploration primitive.
- If `ParameterStudy` and WFA expose different strategy construction models,
  the research layer will feel incoherent.
- If `ParameterStudy` changes abruptly, existing tests, docs, and examples may
  churn heavily.

Initial assessment:

- Urgency: high
- Impact: high
- Reversibility: low to medium
- Suggested priority: P0 candidate

### B4. Strategy Metadata And Reporting Contract

Question:

- How should selected parameter values be captured, normalized, displayed, and
  exported across backtests, parameter studies, WFA folds, paper runs, and live
  runs?

Why it matters for WFA:

- WFA result records must preserve selected parameters per fold.
- Reporting must distinguish default config values, selected study values, and
  non-optimizable runtime settings.
- Parameter metadata should remain deterministic and portable.

Initial assessment:

- Urgency: medium
- Impact: high
- Reversibility: medium
- Suggested priority: P1 candidate

### B4.5. Direct Backtest Class+Config API Alignment

Question:

- Should direct `BacktestEngine.run(...)` accept and teach
  `strategy=StrategyClass` plus `config=StrategyConfig(...)` before WFA
  planning resumes?

Why it matters for WFA:

- WFA will need fresh configured strategy instances for train candidates and
  selected test runs.
- `ParameterStudy` already uses a strategy class plus materialized
  `StrategyConfig` snapshots.
- Direct backtests now use the same strategy class plus materialized
  `StrategyConfig` model.
- This removes the mismatch that would otherwise force WFA to invent or expose
  separate adapter rules instead of composing a settled public backtest
  contract.

Current planning position:

- Treat this as Stage 3.5, after Stage 3 reporting provenance cleanup and
  before Stage 4 WFA Resume Spec.
- The Stage 3.5 product decision is closed in
  [direct-backtest-class-config-api.md](direct-backtest-class-config-api.md):
  direct backtests use `strategy=StrategyClass` plus optional
  `config=StrategyConfig(...)`, direct strategy instances are removed from the
  current public API, and `ParameterStudy` should use the same direct API.

Initial assessment:

- Urgency: medium-high
- Impact: high
- Reversibility: medium
- Suggested priority: P0/P1 bridge before WFA resume

### B5. Fresh Strategy State And Dependency Injection

Question:

- What must the framework guarantee about fresh strategy instances, config
  immutability, and external dependencies used by a strategy?

Why it matters for WFA:

- WFA magnifies state leakage risks because it runs many train and test
  backtests in sequence.
- A clean config contract can prevent parameter mutation from corrupting later
  folds.
- Advanced strategies may need injected models, feature pipelines, or services.

Initial assessment:

- Urgency: medium
- Impact: high
- Reversibility: medium
- Suggested priority: P1 candidate

### B6. Objective Alias And Metric Registry Policy

Question:

- Should WFA and `ParameterStudy` share one public objective alias registry,
  and how should aliases map to report metric paths and directions?

Why it matters for WFA:

- WFA should be approachable with names such as `"sharpe"`.
- Existing parameter exploration uses canonical metric paths and directions.
- Divergent objective naming between studies will hurt DX and agent usage.

Initial assessment:

- Urgency: medium
- Impact: medium
- Reversibility: high
- Suggested priority: P2 candidate

### B7. OOS Summary Versus OOS Report Semantics

Question:

- When should Quantleet expose `oos_summary` versus `oos_report`, and what
  account-continuity semantics does each name imply?

Why it matters for WFA:

- The MVP should emphasize `oos_summary` because fold tests may be independent.
- A future `oos_report` may be valid if Quantleet defines continuous
  OOS-equity/account semantics.
- Incorrect naming can mislead users into believing WFA output is a live-like
  continuous account simulation.

Initial assessment:

- Urgency: medium
- Impact: medium
- Reversibility: medium
- Suggested priority: P2 candidate

### B8. Splitter And Validation Protocol Boundary

Question:

- Which split protocol concepts are part of the primary public WFA UX, which
  remain internal, and which become advanced API later?

Why it matters for WFA:

- Users should not have to hand-build folds for the primary workflow.
- Internal splitters still need enough structure to support rolling,
  expanding, anchored, purged, or embargoed variants later.
- Exposing splitters too early may shift correctness responsibility to users.

Initial assessment:

- Urgency: low to medium
- Impact: medium
- Reversibility: medium
- Suggested priority: P2 candidate

### B9. Failure Policy Across Nested Studies

Question:

- Should WFA continue by default when a fold, candidate, selected train row, or
  test run fails, and where should fail-fast controls live?

Why it matters for WFA:

- `ParameterStudy` already records failed and rejected candidate rows.
- WFA adds another layer of failure: fold generation, train search, selection,
  and OOS backtest.
- Inconsistent failure policy will make notebooks and agents hard to reason
  about.

Initial assessment:

- Urgency: medium
- Impact: medium
- Reversibility: high
- Suggested priority: P2 candidate

### B10. Backtest To Paper/Live Strategy Portability

Question:

- Which parts of the strategy authoring and configuration contract must be
  shared before WFA is implemented, and which can remain future runtime design?

Why it matters for WFA:

- The project goal is not only a research notebook API; it is a stable path
  from research to paper and live execution.
- WFA should not introduce a research-only strategy construction model that
  later paper/live systems cannot reuse.

Initial assessment:

- Urgency: medium
- Impact: high
- Reversibility: low
- Suggested priority: P1 candidate

## Prioritization Criteria

Future refactoring candidates should be ranked with these criteria before a
new product spec is written:

- User-facing contract risk: Will this decision appear in examples, notebooks,
  public imports, or result records?
- Cross-workflow leverage: Does this help backtest, `ParameterStudy`, WFA,
  paper, and live rather than only one feature?
- Refactoring cost if delayed: How much implemented code, docs, and examples
  would need to be rewritten if the decision is postponed?
- Conceptual clarity: Does solving this make the system easier for users and
  agents to understand?
- Implementation containment: Can the slice be solved without expanding Tier A
  runtime scope?
- Reversibility: If the first version is wrong, can the project migrate
  without breaking most user code?
- Verification tractability: Can the behavior be tested through clear product
  and contract tests?

## Initial Priority Read

This is not a final scope decision. It is the starting triage produced by the
WFA pause.

| Candidate | Urgency | Impact | Delay Cost | Initial Priority |
| --- | --- | --- | --- | --- |
| Canonical strategy configuration contract | high | high | high | P0 |
| Config schema vs study search-space ownership | high | high | high | P0 |
| `ParameterStudy` migration strategy | high | high | high | P0 |
| Backtest/paper/live strategy portability boundary | medium | high | high | P1 |
| Strategy metadata and reporting contract | medium | high | medium | P1 |
| Fresh strategy state and dependency injection | medium | high | medium | P1 |
| Objective alias and metric registry policy | medium | medium | low | P2 |
| OOS summary/report semantics | medium | medium | medium | P2 |
| Splitter and validation protocol boundary | low-medium | medium | medium | P2 |
| Nested-study failure policy | medium | medium | low | P2 |

## Recommended Next Analysis Sequence

1. Analyze the canonical strategy configuration contract.
2. Decide whether config schema and experiment search space are separate
   product concepts.
3. Analyze how `ParameterStudy` can migrate or adapt without breaking the
   implemented beta surface unnecessarily.
4. Close the reporting config source-of-truth stage.
5. Decide the direct backtest class-plus-config API alignment slice.
6. Revisit WFA only after Stage 3.5 is completed or explicitly deferred by a
   human decision.

The next document should be a product spec for the first roadmap stage:
`Unified Strategy Configuration Contract`. That spec should stay focused on the
strategy configuration contract itself while preserving the later roadmap stages:

1. `ParameterStudy` Strategy API Migration.
2. Reporting Config Source Of Truth.
3. Direct Backtest Class+Config API Alignment.
4. WFA Resume Spec.

This readiness document should not be used to skip the dedicated roadmap or the
dedicated product spec for the selected prerequisite.

## Open Questions For Later Review

- Should `StrategyConfig` exist as a separate class, class-level `params`, or
  descriptor-based parameter declarations?
- Should the first config contract use plain dataclasses, a custom base class,
  or another validation approach?
- WFA must not preserve or reintroduce the old callable construction path.
- Which strategy settings are true optimizable parameters versus environment,
  dependency, or runtime settings?
- How should selected config values be reflected in `BacktestResult.report`?
- How should examples teach strategy parameters without making users write
  lambda factories for common cases?

Resolved since this readiness review was first written:

- Stage 1 selected the explicit `StrategyConfig` model.
- Stage 2 resolved that `ParameterStudy` uses `strategy=StrategyClass` only.
- Stage 3 resolved that reports expose the framework-owned
  `run.strategy_config` snapshot.
- Stage 3.5 resolves that direct backtests teach strategy classes plus optional
  explicit configs before WFA resumes.
