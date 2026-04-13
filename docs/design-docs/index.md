# Design Doc Routing Index

Use this directory to route to the governing long-lived design document for the
task at hand.

Start with the row whose task area and scope match your work. Read rows marked
`Governing` first. Rows marked `Draft` are future-looking and should not be
treated as the current source of truth.

| Task Area | Document | Role | Scope | Read When |
| --- | --- | --- | --- | --- |
| Repository workflow and operating norms | [`core-beliefs.md`](core-beliefs.md) | Governing | all agent work | Before changing repository workflow, entry-contract docs, or operating norms. |
| Cleanup and promotion defaults | [`golden-principles.md`](golden-principles.md) | Governing | repository cleanup and promotion work | Before promoting repeated review findings into docs or checks, or deleting workflow bureaucracy. |
| Cleanup loops and doc upkeep | [`doc-gardening.md`](doc-gardening.md) | Governing | harness maintenance | Before changing cleanup loops, doc upkeep, or maintenance triggers. |
| Architecture and bounded contexts | [`quantcraft-architecture.md`](quantcraft-architecture.md) | Governing | architecture and bounded-context work | Before changing top-level contexts, dependency rules, or package ownership. |
| Governance for docs versus checks | [`architecture-governance.md`](architecture-governance.md) | Governing | harness governance and repo-check changes | Before promoting a repeated rule from docs into checks, retiring a legacy control-plane artifact, or changing discoverability policy. |
| Shared trading-kernel semantics planning | [`trading-kernel-contract-draft-ko.md`](trading-kernel-contract-draft-ko.md) | Draft | future trading-kernel planning | Only when evaluating future shared trading semantics; read the current implemented product specs first. |
