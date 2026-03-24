# Product Specs

Use this directory for scoped product and domain specifications.

## Metadata

- index_kind: product-spec-status-map
- default_read: Start with the row whose applicability matches the task; rows marked `Canonical: yes` define the active contract for that scope.

## Documents

| Document | Status | Canonical | Applicability | Read When | Notes |
| --- | --- | --- | --- | --- | --- |
| [`market-data.md`](market-data.md) | implemented | yes | current implemented scope | Before changing the existing market-data codebase or its tests. | Current implemented-scope English entry for shipped market-data behavior. |
| [`backtest.md`](backtest.md) | implemented | no | current implemented scope orientation | When scoping backtest expansion work from the shipped baseline before opening a narrower slice contract. | English entry that points to the current implemented backtest baseline. |
| [`backtest-mvp.md`](backtest-mvp.md) | implemented | yes | current implemented scope | Before changing the current backtest MVP behavior, tests, or documented baseline constraints. | Canonical current implemented-scope spec for the shipped backtest baseline. |
| [`research-ergonomics.md`](research-ergonomics.md) | implemented | yes | current implemented scope | Before changing strategy ergonomics, series contracts, indicators, result reporting, examples, or quickstart assets for the research layer. | Canonical current implemented-scope spec for the shipped research ergonomics surface on top of the backtest MVP. |
| [`paper-trading.md`](paper-trading.md) | future | no | future planning only | Only when discussing simulated execution work beyond the current approved slices. | Future-facing English domain entry for paper-trading scope. |
| [`live-trading.md`](live-trading.md) | future | no | future planning only | Only when discussing Tier A live-trading scope with explicit human approval. | Future-facing English domain entry with a human gate. |
