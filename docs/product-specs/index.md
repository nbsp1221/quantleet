# Product Specs

Use this directory for scoped product and domain specifications.

## Metadata

- index_kind: product-spec-status-map
- default_read: Start with the row whose applicability matches the task; rows marked `Canonical: yes` define the active contract for that scope.

## Documents

| Document | Status | Canonical | Applicability | Read When | Notes |
| --- | --- | --- | --- | --- | --- |
| [`market-data.md`](market-data.md) | implemented | yes | current implemented scope | Before changing the existing market-data codebase or its tests. | Current implemented-scope English entry for shipped market-data behavior. |
| [`backtest.md`](backtest.md) | approved | no | approved next-slice orientation | When scoping backtest expansion work before opening the slice-level contract. | English entry that points to the active backtest MVP spec. |
| [`backtest-mvp.md`](backtest-mvp.md) | approved | yes | current approved backtest slice | Before changing the current backtest MVP behavior, tests, or slice boundaries. | Canonical MVP spec for the first backtest implementation slice. |
| [`paper-trading.md`](paper-trading.md) | future | no | future planning only | Only when discussing simulated execution work beyond the current approved slices. | Future-facing English domain entry for paper-trading scope. |
| [`live-trading.md`](live-trading.md) | future | no | future planning only | Only when discussing Tier A live-trading scope with explicit human approval. | Future-facing English domain entry with a human gate. |
