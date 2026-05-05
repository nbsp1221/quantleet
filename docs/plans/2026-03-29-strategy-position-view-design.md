# Strategy Position View Design

## Status

- Status: `approved baseline`
- Class: `design`
- Scope: next `research ergonomics` UX slice for strategy position state

Related documents:

- [../../ARCHITECTURE.md](../../ARCHITECTURE.md)
- [../design-docs/quantleet-architecture.md](../design-docs/quantleet-architecture.md)
- [../product-specs/research-ergonomics.md](../product-specs/research-ergonomics.md)
- [../product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md)
- [../references/openai-harness-engineering.md](../references/openai-harness-engineering.md)
- [../research/2026-03-23-python-quant-library-landscape.md](../research/2026-03-23-python-quant-library-landscape.md)

## Goal

Add a small read-only `self.position` surface to `quantleet.research.Strategy` so users can write conventional one-position strategies without maintaining ad-hoc local booleans such as `self.in_position`.

This slice improves research UX without changing the underlying long-only shared trading kernel.

## Why This Slice Exists

The current backtest and research surface is already usable, but the largest day-to-day UX gap is strategy state visibility.

Today:

- `buy()` means long entry or long increase
- `sell()` means long exit and is a no-op while flat in the current long-only backtest path
- one-position strategies must currently maintain local state such as `self.in_position`

That pattern is more cumbersome than mainstream quant libraries and weaker than the product goal of a clear, agent-legible strategy contract.

## External References And Lessons

### Pine Script

Pine strategies expose position state directly through `strategy.position_size`.

Key lesson:

- basic strategies should not require users to shadow engine state with local booleans

Do not copy directly:

- Pine hides more engine detail than `quantleet` should hide

### backtesting.py

`backtesting.py` exposes `self.position` as a first-class strategy surface.

Key lessons:

- strategy code becomes materially simpler when position state is directly readable
- `self.position` is a natural public name for the strategy-layer contract

### Backtrader

Backtrader exposes `self.position` and `getposition()`.

Key lesson:

- even heavier frameworks keep the strategy-layer position view directly available

### PyBroker

PyBroker strategy and execution contexts expose position state directly.

Key lesson:

- practical research frameworks do not force users to reconstruct current position state by hand

## Human-Closed Contract Decisions

These items are explicitly decided and should not be re-opened by implementation agents.

### Public Name

The public strategy-layer name is:

- `self.position`

### Contract Shape

`self.position` is a small read-only runtime view.

Approved public fields:

- `self.position.is_open`
- `self.position.quantity`
- `self.position.average_entry_price`

Do not add in this slice:

- `unrealized_pnl`
- `market_value`
- `cash`
- `equity`
- account or portfolio objects

### Read Timing

`self.position` is officially meaningful in `on_bar()`.

Rules:

- treat it as the current evaluation-step runtime view
- do not document it as a decision surface for `init()`

### Flat-State Semantics

When the strategy is flat:

- `self.position.is_open == False`
- `self.position.quantity == 0.0`
- `self.position.average_entry_price == 0.0`

This slice deliberately uses numeric zero defaults instead of `None` to keep strategy code lightweight.

## Architecture Direction

This slice should remain a `research`-layer read-only view over already-existing trading state.

That means:

- no new independent position model in `research`
- no duplication of accounting state
- no widening of the `trading` kernel contract just to satisfy convenience concerns

Recommended direction:

- keep canonical mutable state in `trading.domain.state.TradingState`
- derive a small read-only `PositionView` in the `research` runtime layer
- bind it onto `Strategy` as `self.position`

## Responsibilities

### Human Responsibilities

Humans closed:

- the public name
- the public field set
- the read timing contract
- the flat-state semantics

### Agent Responsibilities

Implementation agents should decide:

- file placement for the read-only wrapper type
- runtime binding details
- test decomposition
- doc updates
- whether internal helpers are needed to keep code simple

provided they preserve the approved public contract above.

## Included Scope

- add `self.position` to the `Strategy` runtime surface
- wire it from current backtest state
- update quickstart and examples to remove unnecessary local position booleans where possible
- add tests that prove the view updates correctly across flat, entry, increase, partial exit, and full exit paths

## Out Of Scope

- short support
- leverage or margin
- account or portfolio read models
- new order primitives
- changing current `buy()` / `sell()` semantics
- paper/live runtime parity work beyond preserving future compatibility

## Testing Requirements

The slice should prove:

- `self.position` exists during `on_bar()`
- flat state returns the approved zero-based values
- position state reflects current quantity and average entry price after fills
- long increases update `quantity` and `average_entry_price` correctly
- partial exits preserve `is_open == True` and reduce quantity
- full exit returns to flat semantics
- quickstart and docs no longer require `self.in_position` for simple one-position examples if `self.position` is sufficient

## Success Criteria

The slice is done when:

1. a user can write a one-position RSI or SMA strategy using `self.position.is_open`
2. no extra local boolean is needed for the canonical one-position example
3. the backtest runtime exposes correct position state without duplicating kernel state
4. docs and tests describe the same public contract
5. the repository verification surface passes

## Design Summary

The correct next move is a small read-only `self.position` surface, not a broader account model.

This preserves the shared-kernel direction while closing the most visible research UX gap.
