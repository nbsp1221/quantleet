# Design Doc Routing Index

Use this directory to route to the governing long-lived design document for the
task at hand.

Start with the row whose task area and scope match your work. Read rows marked
`Governing` first. Rows marked `Draft` are future-looking and should not be
treated as the current source of truth.

| Task Area | Document | Role | Scope | Read When |
| --- | --- | --- | --- | --- |
| Repository workflow and operating norms | [`core-beliefs.md`](core-beliefs.md) | Governing | all agent work | Before changing repository workflow, entry-contract docs, or operating norms. |
| Agentic quality-gate priorities | [`agentic-quality-gates.md`](agentic-quality-gates.md) | Draft | AI-agent-led test-quality and architecture-fitness gate planning | Before evaluating or promoting new checks for AI-generated test quality, architecture drift, mutation baselines, or agent-specific quality risks. |
| Cleanup and promotion defaults | [`golden-principles.md`](golden-principles.md) | Governing | repository cleanup and promotion work | Before promoting repeated review findings into docs or checks, or deleting workflow bureaucracy. |
| Cleanup loops and doc upkeep | [`doc-gardening.md`](doc-gardening.md) | Governing | harness maintenance | Before changing cleanup loops, doc upkeep, or maintenance triggers. |
| Architecture and bounded contexts | [`quantleet-architecture.md`](quantleet-architecture.md) | Governing | architecture and bounded-context work | Before changing top-level contexts, dependency rules, or package ownership. |
| Package topology and naming | [`package-topology-and-naming.md`](package-topology-and-naming.md) | Governing | package structure, naming, public facades, and product-surface boundaries | Before changing package topology, naming rules, `api.py` facade policy, or the split between `src/quantleet` and `apps/*`. |
| Backtest execution semantics | [`backtest-execution-semantics.md`](backtest-execution-semantics.md) | Governing | backtest path construction, conservative limit handling, and shared-kernel matching boundary | Before changing OHLC backtest execution semantics, synthetic path generation, or matching-boundary rules. |
| Order domain runtime direction | [`order-domain-runtime-design.md`](order-domain-runtime-design.md) | Draft | non-governing future boundary between `OrderIntent` and runtime `Order` | When planning runtime order modeling, stop-order support, or the first Order-domain promotion beyond the current MVP; read current product specs first. |
| Runtime Order object model and responsibility | [`order-runtime-model-design.md`](order-runtime-model-design.md) | Draft | non-governing guidance for runtime `Order` responsibility, lifecycle depth, and event-boundary policy | After reading the Order-domain seam note, when deciding what the runtime `Order` aggregate itself should own and what must remain in matching/runtime/accounting layers. |
| Runtime Order lifecycle and sizing | [`order-lifecycle-and-sizing-design.md`](order-lifecycle-and-sizing-design.md) | Draft | non-governing guidance for the next runtime `Order` lifecycle/FSM depth and sizing-intent contract | After reading the runtime Order responsibility draft, when deciding how stop-family lifecycle and percentage-based sizing should be modeled next. |
| Unified strategy runtime direction | [`unified-strategy-runtime-design.md`](unified-strategy-runtime-design.md) | Draft | future strategy authoring UX, shared runtime model, and backtest-to-live architecture direction | When evaluating long-lived strategy/runtime architecture beyond the current shipped MVP. |
| Governance for docs versus checks | [`architecture-governance.md`](architecture-governance.md) | Governing | harness governance and repo-check changes | Before promoting a repeated rule from docs into checks, retiring a legacy control-plane artifact, or changing discoverability policy. |
| Shared trading-kernel semantics planning | [`trading-kernel-contract-draft.md`](trading-kernel-contract-draft.md) | Draft | future trading-kernel planning | Only when evaluating future shared trading semantics; read the current implemented product specs first. |
