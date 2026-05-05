# Backtest Engine Design

## Status

- Status: `approved baseline`
- Class: `design`
- Scope: next `research ergonomics` execution-entry slice for backtest usability

Related documents:

- [../../ARCHITECTURE.md](../../ARCHITECTURE.md)
- [../design-docs/quantleet-architecture.md](../design-docs/quantleet-architecture.md)
- [../product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md)
- [../product-specs/research-ergonomics.md](../product-specs/research-ergonomics.md)
- [../references/openai-harness-engineering.md](../references/openai-harness-engineering.md)
- [../research/2026-03-23-python-quant-library-landscape.md](../research/2026-03-23-python-quant-library-landscape.md)
- [../research/libraries/backtesting-py.md](../research/libraries/backtesting-py.md)
- [../research/libraries/backtrader.md](../research/libraries/backtrader.md)
- [../research/libraries/lumibot.md](../research/libraries/lumibot.md)
- [../research/libraries/nautilustrader.md](../research/libraries/nautilustrader.md)
- [../research/libraries/pybroker.md](../research/libraries/pybroker.md)
- [../research/libraries/vectorbt.md](../research/libraries/vectorbt.md)

## Goal

Add a user-facing `BacktestEngine` execution container so users can configure a backtest runtime once and then run strategies through a self-describing bar series dataset rather than a low-level `run_backtest(...)` free-function call.

This slice improves execution ergonomics and clarifies the long-term `backtest / paper / live` runtime family without locking `quantleet` into a source/feed contract that leaks hidden metadata assumptions.

## Why This Slice Exists

Current `quantleet` strategy ergonomics are now credible:

- `Strategy`
- `ta`
- `qc`
- `self.position`

The largest remaining UX friction sits at execution entry.

Today users call:

```python
result = run_backtest(
    symbol="BTC/USDT",
    bar_type="time",
    bar_spec="1h",
    rows=rows,
    strategy=MyStrategy(),
    initial_cash=1_000_000.0,
    costs=costs,
)
```

This is explicit, but it is also engine-facing and repetitive:

- the execution call still exposes low-level metadata
- `rows` are not self-describing
- the public surface does not yet hint at future backtest/paper/live runtime parity

The previous intermediate idea was to let `BacktestEngine.run(source=...)` infer `symbol` and `timeframe` directly from the source object. That turns out to be the wrong abstraction boundary for `quantleet`.

Why it is wrong:

- it couples execution to hidden source-object attributes
- it blurs provider/source concerns with materialized dataset concerns
- it encourages agents to encode ambiguous hybrid contracts

For an agent-first repository, this matters because public execution entry points are long-lived contracts. If the current backtest UX remains a thin free-function wrapper over raw runtime details, or a hybrid source contract with implicit metadata, future agents are more likely to grow paper and live in inconsistent ways.

## External References And Lessons

### backtesting.py

`backtesting.py` centers execution around a `Backtest` runner object and `run()`.

Key lessons:

- users remember object-plus-run surfaces more easily than long free-function calls
- execution consumes materialized market data, not a source/provider object with hidden metadata

Do not copy directly:

- `quantleet` must not become a backtest-only convenience API that hides execution semantics

### Backtrader

Backtrader centers execution around `Cerebro`, which consumes data/feed objects carrying their own identity and timeframe metadata.

Key lessons:

- a named execution container is a familiar mental model
- if runtime entry accepts feed/data objects directly, those objects must be self-describing

Do not copy directly:

- `quantleet` should avoid a broad framework container before the kernel and parity story mature

### PyBroker and vectorbt

Both are useful because they separate acquisition and execution more clearly than the current hybrid `quantleet` attempt.

Key lessons:

- runtime metadata belongs either in:
  - the execution request/config, or
  - the materialized dataset object
- it should not live as a hidden assumption on an abstract provider contract

### Lumibot

Lumibot shows a strategy-centric execution story, but its backtest data path still relies on richer bound data objects and explicit backtest configuration.

Key lesson:

- parity-oriented UX still benefits from a clear distinction between runtime config and data identity

### NautilusTrader

NautilusTrader is the strongest architectural north-star in this comparison set.

Key lessons:

- keep one execution-kernel semantics contract across backtest, paper, and live
- execution should consume metadata-rich runtime-facing data objects
- request/config boundaries should remain explicit

Do not copy directly:

- do not introduce heavyweight platform scope or multi-venue complexity prematurely

## Human-Closed Contract Decisions

These items are explicitly decided and should not be re-opened by implementation agents.

### Public Family Naming

The long-term public runtime family uses `*Engine` naming.

Approved direction:

- `BacktestEngine`
- future: `PaperEngine`
- future: `LiveEngine`

### First Public Execution Container

The next slice adds:

- `BacktestEngine`

### Ownership Model

`BacktestEngine` owns execution configuration, not strategy construction and not provider-specific acquisition logic.

Approved public shape:

```python
engine = BacktestEngine(...)
result = engine.run(...)
```

This means the engine acts as a runtime configuration container and execution entry point.

### Materialized Dataset Contract

This slice introduces a self-describing historical bar-series dataset object.

Approved public names:

- `TimeBar`
- `BarSeries`

`TimeBar` is the single-bar type for this slice.

`BarSeries` is the engine-facing historical dataset type for this slice.

`BarSeries` owns:

- `symbol`
- `timeframe`
- `bar_type`
- `rows`

In this slice:

- `rows` is a tuple of `TimeBar`
- `bar_type` must be `"time"`

This is the core contract change that resolves the current hybrid mismatch without pretending that non-time bars are already supported.

### Run Inputs

`BacktestEngine.run(...)` officially supports either:

- `bars=...`
- `source=...`

This is deliberate:

- `bars=...` is the self-describing materialized dataset path
- `source=...` remains convenient for `quantleet.data`
- the source path must materialize into `BarSeries` before execution

### Source Contract Direction

`HistoricalDataSource` should remain an acquisition boundary, not a hidden runtime-metadata carrier.

The engine must not depend on undeclared source attributes such as:

- `source.symbol`
- `source.timeframe`

Instead:

- `source.load()` should return `BarSeries`

### Public Import Surface

To avoid future agent ambiguity, the new public data types are imported from `quantleet.data`.

Approved public import paths:

- `quantleet.data.TimeBar`
- `quantleet.data.BarSeries`

### Strategy Passing

`BacktestEngine.run(...)` accepts a strategy instance, not a strategy class.

Approved pattern:

```python
engine.run(source=source, strategy=MyStrategy())
engine.run(bars=bars, strategy=MyStrategy())
```

This preserves the current `quantleet` strategy mental model and avoids opening constructor or optimizer contracts in this slice.

## Architecture Direction

This slice should improve execution ergonomics without moving mutable simulation state out of the current backtest kernel.

That means:

- keep canonical execution semantics in the existing backtest pipeline
- treat `BacktestEngine` as a user-facing orchestration layer
- keep the current kernel path as the implementation core
- do not introduce a public generic `Engine` base in this slice

Recommended direction:

- add a narrow `BacktestEngine` under the `research` public surface
- add a self-describing `BarSeries` contract at the `data` boundary
- implement `BacktestEngine.run(...)` as a thin orchestration layer over the current backtest path
- remove the public `run_backtest(...)` free-function entry in the same slice so one canonical execution path remains

## Responsibilities

### Human Responsibilities

Humans closed:

- the runtime family naming
- the first public container name
- the ownership model
- the `bars` or `source` dual-input contract
- the dataset contract direction
- the public names `TimeBar` and `BarSeries`
- the public import surface `quantleet.data`
- the rule that this slice supports `time` bars only
- the rule that source metadata must not remain implicit
- the strategy-instance contract

### Agent Responsibilities

Implementation agents should decide:

- exact internal file placement for `TimeBar` and `BarSeries`
- how the existing kernel path is reused internally without leaving multiple public entry points behind
- input validation details
- test decomposition
- doc and quickstart updates

provided they preserve the approved public contract above.

## Included Scope

- add `BacktestEngine` as the user-facing execution container for backtests
- let the engine own execution configuration such as initial cash and costs
- add `TimeBar` as the canonical single-bar type for the current historical backtest slice
- add `BarSeries` as the self-describing engine-facing dataset object
- support `engine.run(bars=..., strategy=...)`
- support `engine.run(source=..., strategy=...)`
- remove the public `run_backtest(...)` free-function surface in this slice
- update docs and examples to show `BacktestEngine` plus the dataset-based execution path as the preferred public entry point

## Out Of Scope

- `PaperEngine`
- `LiveEngine`
- a public generic `Engine` base
- optimizer or parameter-sweep contracts
- portfolio objects
- multi-symbol support
- `DollarBar`, `TickBar`, `VolumeBar`, or other non-time bar types
- strategy-class execution contracts
- a generalized request object for every future data workflow

## Testing Requirements

The slice should prove:

- `BarSeries` is self-describing and validates its required metadata
- `BarSeries.rows` contains `TimeBar`
- `BarSeries.bar_type` only accepts `"time"` in this slice
- `BacktestEngine.run(bars=..., strategy=...)` produces the same result shape as the current backtest path
- `BacktestEngine.run(source=..., strategy=...)` materializes through the existing data-ingestion path into the dataset contract before execution
- mixed or invalid input combinations fail clearly
- `run_backtest(...)` is removed from the public `quantleet.research` execution story in code, docs, and tests
- quickstart and docs use the new preferred execution surface consistently

## Success Criteria

The slice is done when:

1. a user can configure `BacktestEngine` once and execute a strategy with either a materialized bars dataset or a data source
2. the preferred public backtest entry point is more legible than the current raw free-function call
3. the data boundary is clearer than the current hybrid source-metadata assumption
4. the implementation preserves the existing kernel semantics and result structure
5. the runtime family direction for future paper/live work is now visible in the public surface
6. docs, tests, and repository verification all agree on the contract
7. there is only one canonical public backtest execution entry, so future agents do not have to choose between competing surfaces

## Design Summary

The correct next move is not a giant framework container and not a full generic runtime hierarchy.

The correct next move is:

- a narrow public `BacktestEngine`
- a canonical `TimeBar` single-bar type for the current slice
- a self-describing `BarSeries` dataset contract
- an explicit `DataSource -> BarSeries -> BacktestEngine` shape

This is small enough for agents to maintain safely, but principled enough to avoid amplifying the current hybrid contract mismatch.
