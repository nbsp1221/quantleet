# Design Docs

Use this directory for long-lived design rationale and repository operating principles.

## Metadata

- index_kind: design-doc-status-map
- default_read: Start with rows marked `Canonical: yes` whose applicability matches the task.

## Documents

| Document | Status | Canonical | Applicability | Read When | Notes |
| --- | --- | --- | --- | --- | --- |
| [`core-beliefs.md`](core-beliefs.md) | approved | yes | all agent work | Before changing repository workflow, harness docs, or operating norms. | Repository-wide agent-first beliefs. |
| [`golden-principles.md`](golden-principles.md) | approved | yes | repository cleanup and promotion work | Before promoting repeated review findings into docs or checks. | Canonical cleanup invariants and promotion defaults. |
| [`doc-gardening.md`](doc-gardening.md) | approved | yes | harness maintenance | Before changing cleanup loops, doc upkeep, or quality-tracking expectations. | Recurring cleanup and repository gardening guidance. |
| [`quantcraft-architecture.md`](quantcraft-architecture.md) | approved | yes | architecture and bounded-context work | Before changing top-level contexts, dependency rules, or package ownership. | Canonical long-lived architecture for contexts, layers, and dependency rules. |
| [`trading-kernel-contract-draft-ko.md`](trading-kernel-contract-draft-ko.md) | draft | no | trading-kernel planning | Only when evaluating future shared trading semantics that are still draft. | Draft only; do not treat it as the current implemented contract. |
| [`architecture-governance.md`](architecture-governance.md) | approved | yes | harness governance and repo-check changes | Before promoting a repeated rule from docs into checks or changing system-of-record policy. | Canonical governance for mechanical enforcement versus prompt guidance. |
