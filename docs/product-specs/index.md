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
| Historical ingestion under `quantcraft.data` | [`data-ingestion.md`](data-ingestion.md) | Governing | current implemented scope | Before changing the shipped historical ingestion surface for exchange, CSV, and dataframe-backed backtest workflows. |
| Backtest baseline orientation | [`backtest.md`](backtest.md) | Pointer | current implemented baseline orientation | When scoping backtest expansion work from the shipped baseline; then read [`backtest-mvp.md`](backtest-mvp.md). |
| Backtest MVP behavior | [`backtest-mvp.md`](backtest-mvp.md) | Governing | current implemented scope | Before changing the current backtest MVP behavior, tests, or documented baseline constraints. |
| Research ergonomics surface | [`research-ergonomics.md`](research-ergonomics.md) | Governing | current implemented scope | Before changing strategy ergonomics, series contracts, indicators, result reporting, examples, quickstart assets, plotting, parameter exploration, or first-beta UX work for the research layer. |
| Explicit percentage-based order sizing | [`order-sizing.md`](order-sizing.md) | Governing | current implemented scope | Before changing the shipped `qty_percent` sizing behavior for strategy order entry and partial exit semantics; read the current backtest and research specs first. |
| Conservative order reservation policy | [`order-reservation.md`](order-reservation.md) | Governing | current implemented scope | Before changing percent sizing, active-order reservations, dormant stop-family reservation behavior, or trigger-time sizing policy. |
| Stop-limit order behavior | [`stop-limit.md`](stop-limit.md) | Governing | current implemented scope | Before changing `stop_limit` strategy intake, trigger lifecycle, backtest execution semantics, or tests. |
| Paper-trading planning | [`paper-trading.md`](paper-trading.md) | Future-only | future planning only | Only when discussing simulated execution work beyond the current approved slices. |
| Live-trading planning | [`live-trading.md`](live-trading.md) | Future-only | future planning only | Only when discussing Tier A live-trading scope with explicit human approval. |
