# Trading Kernel Architecture Insights

## Status

- Date: `2026-04-18`
- Status: `research note`
- Authority: `non-governing`
- Purpose:
  Preserve the architectural insights gathered from `quantleet` repository analysis,
  cross-library comparison, and iterative design discussion about a unified
  research-to-live trading engine.

## Why This Note Exists

The project goal discussed in this session is not "just a backtest library."
The intended direction is a personal long-lived quant framework which can:

- support strategy research and alpha search
- backtest with a shared trading meaning
- graduate the same strategy logic into paper trading and live trading
- keep strategy authoring ergonomics as simple as possible
- eventually support both single-asset and multi-asset strategies
- eventually support multiple strategies on one account

This note captures the key insights learned while testing that goal against the
current `quantleet` codebase and against several mature trading libraries.

It does **not** redefine current approved architecture or current shipped API.
Treat it as dated research evidence for later planning or design-doc work, not
as architecture authority by itself.

## Governing Context Consulted

This note was written against these current authority docs:

- [`../../AGENTS.md`](../../AGENTS.md)
- [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`../PLANS.md`](../PLANS.md)
- [`../design-docs/index.md`](../design-docs/index.md)
- [`../design-docs/quantleet-architecture.md`](../design-docs/quantleet-architecture.md)
- [`../design-docs/unified-strategy-runtime-design.md`](../design-docs/unified-strategy-runtime-design.md)
- [`../product-specs/backtest-mvp.md`](../product-specs/backtest-mvp.md)

## Current `quantleet` Truth

The current repository is not yet a full unified trading runtime.

What exists today:

- a `Strategy` authoring surface focused on bar-based research callbacks
- `OrderIntent` as the current strategy output shape
- a deterministic single-symbol long-only backtest runtime
- a shared `trading` path which currently centers on:
  - `OrderIntent`
  - current event contracts consumed in the trading path such as
    `TickEvent`, `BarEvent`, and `FillEvent`
  - `TradingState`
  - fill matching and state application

What does **not** exist yet:

- a rich runtime `Order` aggregate
- `OrderEvent` in the current public slice
- a real `Portfolio` aggregate
- a real account-scoped `RiskEngine`
- paper-trading runtime implementation
- live-trading runtime implementation
- order lifecycle management such as cancel/replace/partial-fill handling

The key implication is:

> `quantleet` currently has a valid shared-kernel *direction*, but its actual
> implementation is still an MVP focused on matching fills and updating one
> spot-like long-only state.

Repository evidence referenced for this section:

- [`../product-specs/backtest-mvp.md`](../product-specs/backtest-mvp.md)
- [`../../src/quantleet/research/strategy.py`](../../src/quantleet/research/strategy.py)
- [`../../src/quantleet/trading/domain/intents.py`](../../src/quantleet/trading/domain/intents.py)
- [`../../src/quantleet/trading/domain/events.py`](../../src/quantleet/trading/domain/events.py)
- [`../../src/quantleet/trading/domain/state.py`](../../src/quantleet/trading/domain/state.py)
- [`../../src/quantleet/backtest/results.py`](../../src/quantleet/backtest/results.py)
- [`../../src/quantleet/backtest/runtime.py`](../../src/quantleet/backtest/runtime.py)

## The Most Important Architectural Insight

The project should not try to force a single object to mean everything.

The current MVP leans too heavily on `OrderIntent`.
That object is useful, but it is too small and too early in the flow to carry
the full runtime semantics of a market-facing order.

The crucial separation is:

- `Strategy` authoring surface
- `Intent` or `Target` decision layer
- runtime `Order` layer
- `Fill` event layer
- `Position` / `Portfolio` / `Ledger` accounting layer

In short:

> `OrderIntent` should describe what a strategy wants.
> `Order` should describe what the runtime is actually managing.

This is the first major place where the session concluded that richer domain
modeling is needed.

## No Universal "Correct" Design Exists

There is no single globally correct trading architecture.

Different libraries optimize for different primary problems:

- strategy authoring UX
- research/backtest productivity
- portfolio/risk framework composition
- execution realism and venue parity
- operational bot management

This means no mature library is "the answer" in full.
However, several of them each contain design choices worth extracting.

The practical conclusion is:

> There is no perfect off-the-shelf answer, but there can be a strong
> `quantleet`-specific local optimum built from the right principles at the
> right layer.

## Cross-Library Takeaways

### NautilusTrader

NautilusTrader was the closest reference for the desired runtime architecture.

Important lessons:

- strategies create orders through an order factory and submit them into a
  pipeline
- the runtime has an explicit order lifecycle and rich order states
- risk checking is a first-class engine component
- order, position, and portfolio updates flow back through event handlers
- the architecture is explicit about local emulation, venue submission,
  acknowledgements, triggers, partial fills, and terminal states

Why it matters:

- it validates the idea that the runtime should own a rich `Order` model
- it validates `risk -> execution -> events` as a coherent core pipeline
- it shows that stop and trigger orders require order lifecycle, not just
  a larger intent payload

Trade-off:

- authoring UX is more explicit and heavier than Pine-like single-chart tools

Sources:

- https://nautilustrader.io/docs/latest/concepts/orders/
- https://nautilustrader.io/docs/latest/concepts/strategies/
- https://nautilustrader.io/docs/latest/concepts/architecture/

### QuantConnect LEAN

LEAN was the strongest reference for account- and portfolio-level coordination.

Important lessons:

- it has explicit order request, order, ticket, and transaction handling layers
- it elevates target-based portfolio control in the algorithm framework
- risk management is modeled as a layer which transforms or constrains targets
- execution is treated as a separate framework concern

Why it matters:

- it validates a layered `target -> risk -> execution` approach for
  multi-asset systems
- it shows that portfolio-level control often belongs above raw order creation

Trade-off:

- the user-facing model is more symbol- and engine-centric than a Pine-like UX

Sources:

- https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-management/order-tickets
- https://www.quantconnect.com/docs/algorithm-framework/risk-management

### backtrader

backtrader was the strongest reference for strategy authoring ergonomics.

Important lessons:

- `buy()` and `sell()` are easy to use in the common case
- single-asset usage feels natural
- the system still has a concrete order object and status transitions
- stop and stop-limit orders are part of the everyday API

Why it matters:

- it validates a very lightweight single-asset authoring surface
- it shows that rich runtime order semantics do not require exposing that
  full complexity in the first user-facing layer

Trade-off:

- it does not strongly separate intent, risk, execution, and runtime order
  lifecycle as independent layers

Sources:

- https://www.backtrader.com/docu/strategy/
- https://www.backtrader.com/docu/order/
- https://www.backtrader.com/docu/position/

### Zipline

Zipline was useful mainly as a reminder that portfolio APIs and order-lifecycle
APIs are not the same design problem.

Important lessons:

- target-based portfolio APIs are powerful for multi-asset allocation
- target APIs are not a substitute for rich open-order lifecycle handling

Why it matters:

- it reinforces that `Target` is a strong abstraction for portfolio strategies
- it also reinforces that `Order` remains necessary lower in the stack

Sources:

- https://zipline.ml4trading.io/api-reference.html

### Freqtrade

Freqtrade was useful as a reference for operational bot pragmatism.

Important lessons:

- strategy logic can be very lightweight while the bot runtime handles
  order persistence and operational stoploss management
- stoploss orchestration in production has a lot of edge-case handling
- persistent `Trade` and `Order` models are important for real-world bot
  operation

Why it matters:

- it validates the importance of operational runtime logic outside the
  strategy-facing API
- it highlights how much complexity accumulates around stoploss handling,
  retries, and exchange state reconciliation

Trade-off:

- its strategy interface is more signal/bot oriented than a general-purpose
  shared trading kernel

Sources:

- https://www.freqtrade.io/en/stable/strategy-customization/
- https://www.freqtrade.io/en/stable/strategy-callbacks/

## Layered Model Considered During This Session

The discussion converged on a layered model rather than a one-object model.
This section records the candidate layering that emerged from research and
discussion. It is not, by itself, an adopted architecture decision.

### 1. Authoring Layer

This is the strategy UX layer.

Responsibilities:

- provide Pine-like or backtesting.py-like ergonomics
- keep common strategy code easy to read and easy to write
- support simple single-asset strategies without forcing runtime complexity
  into user code

This layer should optimize for:

- usability
- local clarity
- expressive strategy intent

### 2. Decision Layer

This layer should hold what the strategy wants to do.

Candidate abstractions:

- `OrderIntent` for order-shaped intent
- `TargetPosition` or `TargetWeights` for portfolio-shaped intent

Insight:

- `OrderIntent` is useful but should not be the only canonical output forever
- single-asset strategies often map naturally to order-shaped intent
- portfolio strategies often map more naturally to target-shaped intent

### 3. Account Coordination Layer

This is where:

- allocator logic lives
- multi-strategy conflict resolution lives
- account-scoped risk and policy coordination lives

This layer matters as soon as:

- multiple strategies share one account
- multiple symbols share one account
- target expressions need reconciliation into account-level actions

This note does not claim that all risk semantics move out of `trading`.
Per the approved architecture, core cross-environment risk semantics still
belong in the shared trading kernel, while account-scoped coordination and
runtime policy sit above strategy outputs.

### 4. Runtime Order Layer

This layer should own the real market-facing order semantics.

This is where `Order` belongs.

It should be responsible for:

- order status
- trigger state
- submission lifecycle
- partial fills
- cancel / modify / reject / expire handling
- local order-state transitions driven by accepted commands and translated
  runtime events

This was one of the clearest conclusions of the session:

> rich order state belongs here, not in `OrderIntent`.

This does not mean the runtime order layer should absorb venue protocol code.
Execution and integration layers should still own broker or exchange sessions
and translate external messages into internal order and fill events.

### 5. Fill And Accounting Layer

This layer should use fill facts to drive state updates.

Recommended chain:

- `FillEvent`
- `Position` update
- `Portfolio` / `Account` update
- `Ledger` / reporting update

This keeps accounting driven by execution facts rather than by assumptions in
the strategy or order-intent layer.

### 6. Runtime Adapter Layer

This layer differentiates:

- backtest
- paper
- live

The goal is not that all three are identical.
The goal is that they share the same internal trading meaning and differ
mainly in event source, adapter behavior, and capability constraints.

## Implications Considered For Future `quantleet` Work

The session did not conclude that `quantleet` should immediately implement all
of this.

The more realistic conclusion was:

- keep the current user-facing `Strategy` simple
- treat current `Strategy` as the single-symbol authoring DSL for now
- do not force a premature public split solely for naming reasons
- preserve internal symbol-bearing generality beneath that surface
- evolve the engine by introducing the missing runtime objects in the core
  trading path

This means:

- current `Strategy` may remain the canonical public authoring class for the
  current slice
- future multi-asset strategy models can be added later without forcing an
  early public abstraction split
- the core engine should still move toward `Intent != Order != Fill != State`

## What To Watch Carefully During Implementation

The discussion identified several areas where elegant architecture matters more
than API surface cosmetics.

### Event Ordering And Causality

Questions like these must be explicitly defined:

- when is a new order active
- when does a stop become triggered
- whether same-bar child or tail evaluation is allowed
- how acknowledgements and fills are ordered
- how partial fills and later cancels interact

Without this, backtest and live drift semantically even if they share names.

### Deterministic Core

The runtime core should be replayable and deterministic whenever possible.

Async I/O is still necessary at the boundaries, but:

- the core trading loop should ideally consume ordered commands and events
- side effects should be pushed to adapters
- event replay should reproduce state transitions

### Capability Boundaries

A unified API cannot honestly pretend every runtime or venue supports every
order behavior.

The engine should eventually model capabilities explicitly, for example:

- local stop emulation available
- native stop-limit available
- trailing-stop update supported or unsupported

The system should fail clearly instead of silently degrading.

### Persistent Runtime State

Paper/live systems need more than transient in-memory strategy state.

Important persistent or reconstructible entities include:

- open orders
- order history
- fills
- positions
- portfolio snapshots or ledger state

This is especially important for restart and reconciliation behavior.

### Keeping Logic Local To Its Owner

The session repeatedly reinforced this principle:

- strategy DSL should not own runtime order truth
- backtest should not become the owner of trading semantics
- trading should not absorb venue protocol code
- integrations should not absorb core trading meaning

This aligns with the approved `quantleet` architecture and should remain a
design guardrail.

## The Key "Near-Answer"

There is no universal perfect architecture to copy.

The strongest answer found in this session was instead:

> extract the best idea from each library **at the correct layer**.

That means:

- learn single-asset UX from backtrader-like surfaces
- learn runtime order lifecycle from NautilusTrader
- learn portfolio target/risk layering from LEAN
- learn operational stoploss and bot supervision lessons from Freqtrade

The "correct" architecture for `quantleet` is therefore not a clone of any
one system.
It is a layered synthesis tuned to the project's specific goal:

- simple authoring
- shared trading meaning
- research-to-live portability
- future support for multi-asset and multi-strategy execution

## Practical Summary

If future engine work has to prioritize only a few architectural upgrades, the
highest-leverage ones are likely:

1. separate `OrderIntent` from runtime `Order`
2. introduce explicit order lifecycle events
3. drive state updates from fills into richer state models
4. keep a deterministic event-driven kernel below all runtimes
5. place allocator/risk/account coordination above raw order execution

These five points summarize the most reusable insight from the session.
