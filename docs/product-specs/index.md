# Product Spec Routing Index

Use this directory to route to the governing product or domain contract for the
task at hand.

Start with the row whose task area and scope match your work. Read rows marked
`Governing` first. Rows marked `Pointer` route you to the governing spec for
that slice. Rows marked `Future-only` do not define the current implemented
contract.

Historical governance artifacts do not change product authority. Product
behavior is governed by the rows below plus the repo contract in
[`../../AGENTS.md`](../../AGENTS.md).

| Task Area | Document | Role | Scope | Read When |
| --- | --- | --- | --- | --- |
| Existing market-data behavior | [`market-data.md`](market-data.md) | Governing | current implemented scope | Before changing the existing market-data codebase or its tests. |
| Historical ingestion under `quantleet.data` | [`data-ingestion.md`](data-ingestion.md) | Governing | current implemented scope | Before changing the shipped historical ingestion surface for exchange, CSV, and dataframe-backed backtest workflows. |
| Backtest baseline orientation | [`backtest.md`](backtest.md) | Pointer | current implemented baseline orientation | When scoping backtest expansion work from the shipped baseline; then read [`backtest-mvp.md`](backtest-mvp.md). |
| Backtest MVP behavior | [`backtest-mvp.md`](backtest-mvp.md) | Governing | current implemented scope | Before changing the current backtest MVP behavior, tests, or documented baseline constraints. |
| Backtest result plotting | [`backtest-plotting.md`](backtest-plotting.md) | Governing | current implemented first-beta plotting workflow | Before changing the first-beta plot API, plot implementation, plot dependency strategy, or documented result-visualization workflow. |
| Backtest plotting test scenarios | [`backtest-plotting-test-scenarios.md`](backtest-plotting-test-scenarios.md) | Governing | current implemented first-beta plotting test target | Before writing or reviewing tests for the first-beta result plotting workflow. |
| Research ergonomics surface | [`research-ergonomics.md`](research-ergonomics.md) | Governing | current implemented scope | Before changing strategy ergonomics, series contracts, indicators, result reporting, examples, quickstart assets, plotting, parameter exploration, or first-beta UX work for the research layer. |
| Public beta documentation | [`public-beta-documentation.md`](public-beta-documentation.md) | Governing | first public beta documentation planning | Before changing release-facing repository docs, public docs structure, beta quickstarts, public examples, or the boundary between public docs and agent-internal docs. |
| Parameter exploration | [`parameter-exploration.md`](parameter-exploration.md) | Governing | current implemented first-beta scope | Before changing or implementing parameter grids, strategy comparison artifacts, exploration ranking, or selected-run inspection workflows. |
| Parameter exploration test scenarios | [`parameter-exploration-test-scenarios.md`](parameter-exploration-test-scenarios.md) | Governing | current implemented first-beta test target | Before writing or reviewing tests for first-beta parameter grid comparison, ranking, failure, record-output, or selected-run inspection workflows. |
| Strategy configuration contract | [`strategy-configuration-contract.md`](strategy-configuration-contract.md) | Governing | planned shared strategy configuration contract before ParameterStudy migration and WFA resume | Before changing the canonical strategy/config contract, `StrategyConfig`, strategy construction for studies, config materialization, or downstream config-reporting assumptions. |
| Strategy configuration contract test scenarios | [`strategy-configuration-contract-test-scenarios.md`](strategy-configuration-contract-test-scenarios.md) | Governing | planned test target for the shared strategy configuration contract | Before writing or reviewing tests for `StrategyConfig`, canonical `Strategy[Config]` declarations, config materialization, or strategy-config validation behavior. |
| Reporting config source of truth | [`reporting-config-source-of-truth.md`](reporting-config-source-of-truth.md) | Governing | current implemented Stage 3 reporting provenance cleanup before WFA resume | Before replacing report-facing `strategy_parameters`, removing `Strategy.parameters()` from the canonical surface, changing report run metadata, or aligning reports with `StrategyConfig` snapshots. |
| Reporting config source-of-truth test scenarios | [`reporting-config-source-of-truth-test-scenarios.md`](reporting-config-source-of-truth-test-scenarios.md) | Governing | current implemented Stage 3 reporting provenance cleanup test target | Before writing or reviewing tests for `report.run.strategy_config`, removal of `strategy_parameters`, ignored `Strategy.parameters()` hooks, report snapshot provenance, or ParameterStudy/report config alignment. |
| Direct backtest class-plus-config API | [`direct-backtest-class-config-api.md`](direct-backtest-class-config-api.md) | Governing | Stage 3.5 WFA prerequisite contract for aligning direct `BacktestEngine.run(...)` strategy construction with `StrategyConfig` | Before implementing `BacktestEngine.run(strategy=StrategyClass, config=...)`, changing whether strategy instances are accepted, or resuming WFA planning after Stage 3 reporting cleanup. |
| Direct backtest class-plus-config API test scenarios | [`direct-backtest-class-config-api-test-scenarios.md`](direct-backtest-class-config-api-test-scenarios.md) | Governing | Stage 3.5 test target for direct backtest class-plus-config API alignment | Before writing or reviewing tests for `BacktestEngine.run(strategy=StrategyClass, config=...)`, default config materialization, direct-instance rejection, ParameterStudy alignment, or public example cleanup. |
| Walk-forward analysis | [`walk-forward-analysis.md`](walk-forward-analysis.md) | Governing | paused future research-validation workflow | Before changing or implementing walk-forward analysis, out-of-sample fold validation, fold-level selected-parameter reporting, or WFA diagnostics; WFA implementation is paused until readiness blockers are reviewed. |
| Walk-forward analysis readiness | [`walk-forward-analysis-readiness.md`](walk-forward-analysis-readiness.md) | Governing | prerequisite blocker analysis before WFA resumes | Before selecting refactoring work meant to unblock walk-forward analysis, strategy configuration contracts, or research-study parameter construction. |
| WFA prerequisite roadmap | [`wfa-prerequisite-roadmap.md`](wfa-prerequisite-roadmap.md) | Governing | ordered product-spec sequence before WFA resumes | Before writing the Strategy Configuration Contract spec, migrating `ParameterStudy`, changing strategy config reporting metadata, or resuming WFA planning. |
| Explicit percentage-based order sizing | [`order-sizing.md`](order-sizing.md) | Governing | current implemented scope | Before changing the shipped `qty_percent` sizing behavior for strategy order entry and partial exit semantics; read the current backtest and research specs first. |
| Conservative order reservation policy | [`order-reservation.md`](order-reservation.md) | Governing | current implemented scope | Before changing percent sizing, active-order reservations, dormant stop-family reservation behavior, or trigger-time sizing policy. |
| Stop-limit order behavior | [`stop-limit.md`](stop-limit.md) | Governing | current implemented scope | Before changing `stop_limit` strategy intake, trigger lifecycle, backtest execution semantics, or tests. |
| Paper-trading planning | [`paper-trading.md`](paper-trading.md) | Future-only | future planning only | Only when discussing simulated execution work beyond the current approved slices. |
| Live-trading planning | [`live-trading.md`](live-trading.md) | Future-only | future planning only | Only when discussing Tier A live-trading scope with explicit human approval. |
