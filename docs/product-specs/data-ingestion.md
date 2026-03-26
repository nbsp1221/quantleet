# Data Ingestion

## Status

- Status: `implemented`
- Class: `product-spec`
- Scope: the current implemented historical data-ingestion surface for research workflows

Related documents:

- [market-data.md](market-data.md)
- [backtest-mvp.md](backtest-mvp.md)
- [research-ergonomics.md](research-ergonomics.md)
- [../design-docs/quantcraft-architecture.md](../design-docs/quantcraft-architecture.md)
- [../design-docs/architecture-governance.md](../design-docs/architecture-governance.md)

This document is the canonical current implemented-scope contract for the shipped historical ingestion surface under `quantcraft.data`.

## Goal

Provide the current official historical data-ingestion surface that:

- is easy for users to understand
- belongs clearly to the `data` bounded context
- feeds the current backtest path directly
- stays small enough that agents do not grow it into a larger data platform

## Why This Slice Exists

`quantcraft` already has:

- implemented market-data utilities
- an implemented Backtest MVP
- an implemented `quantcraft.research` ergonomics surface

What is still weak is the user-facing ingestion path that connects external historical data to the current backtest workflow.

Compared with other quant and backtesting libraries, users still do not have a clear, canonical way to:

- fetch historical bars from an exchange-backed provider
- load historical bars from CSV
- pass dataframe-like research data into the same backtest path

This implemented slice closes that gap without introducing storage, scheduling, or live-feed infrastructure.

## In Scope

This implemented slice includes:

- public historical `DataSource` objects under `quantcraft.data`
- normalization into the same typed OHLCV bar sequence already accepted by the current backtest path
- the ingestion path that feeds those bars into the current backtest workflow

## Out Of Scope

This implemented slice does not include:

- caching systems
- persistence or storage systems
- scheduled collection or sync jobs
- background data services
- generalized live or streaming feed infrastructure
- a broader data platform beyond research ingestion

## Public Namespace

The official public ingestion namespace for this slice is:

```python
from quantcraft.data import CCXTDataSource, CSVDataSource, DataFrameDataSource
```

Acquisition and normalization belong to `data`.

Strategy authoring and backtest orchestration remain in `research`.

## Public Contract

The long-lived public concept is `DataSource`, not `OHLCVSource`.

The minimal public contract for this slice is intentionally small:

1. create a source object
2. call `load()`
3. receive the typed OHLCV bar sequence

This slice does not require or expose a broader lifecycle such as:

- `connect()`
- `stream()`
- `subscribe()`
- background runtime ownership
- async loading
- public session or client injection
- retry or rate-limit policy knobs
- credential management surfaces

Those belong to later feed or execution work, not to this historical-ingestion slice.

## Official Source Baseline

The first approved baseline includes:

- `CCXTDataSource`
- `CSVDataSource`
- `DataFrameDataSource`

This gives `quantcraft` three practical first-run paths:

1. fetch historical bars from an exchange-backed provider
2. load historical bars from a local CSV file
3. pass already-prepared research data from a dataframe-like workflow

## Typed Bar Reuse And Ownership

All official sources must return the same typed OHLCV bar sequence that the current backtest path already accepts.

Agents must treat this as a reuse requirement:

- do not invent a second public historical bar type for ingestion
- normalize all supported sources into the existing backtest-compatible typed OHLCV bar shape

Ownership rule:

- the canonical normalized OHLCV bar type for this slice belongs to `data.domain`
- `research` consumes that type
- `shared` must not be used as a shortcut location for this business shape

## Historical-Only Scope

This slice is historical-only.

It is not the place to unify historical ingestion and future live or streaming feeds under one abstraction.

Future live or streaming feed abstractions can be designed later as separate slices.

## CCXTDataSource

`CCXTDataSource` is the first approved exchange-backed historical source for this slice.

The public naming follows the provider boundary rather than a venue-specific or overly generic name.

It should use explicit constructor arguments rather than a separate public request object.

Illustrative direction:

```python
source = CCXTDataSource(
    exchange="binance",
    market="usdm",
    symbol="BTC/USDT:USDT",
    timeframe="1h",
    start=start,
    end=end,
)
bars = source.load()
```

The first public path should be provider-native-string-first:

- `exchange="binance"`
- `market="usdm"`
- `symbol="BTC/USDT:USDT"`
- `timeframe="1h"`

### First-Slice Support Boundary

The first documented and tested guarantee is Binance via `ccxt`.

However:

- the implementation should still be written as a provider-generic `CCXTDataSource`
- other `ccxt` venues must not be explicitly hard-blocked in this slice
- other venues may work or fail depending on venue-specific behavior

This keeps the support boundary realistic without destroying the value of using `ccxt`.

## CSVDataSource And DataFrameDataSource

The first public CSV/DataFrame ingestion contract uses a small canonical input schema.

Required input columns:

- `timestamp`
- `open`
- `high`
- `low`
- `close`

Optional input columns:

- `volume`

Metadata fields are not inferred from the table by default in this slice.

Instead:

- `symbol` is supplied as a constructor argument
- `timeframe` is supplied as a constructor argument

### Time Rules

Internal canonical time handling uses UTC.

CSV/DataFrame ingestion must receive timezone-aware timestamps, or explicitly parseable timestamps that can be normalized to UTC without guessing.

Naive timestamps must be rejected.

### Volume Rule

`volume` may be omitted and normalized to `0`.

## Canonical User Experience Target

The target mental model is:

1. create a `DataSource`
2. call `load()`
3. receive typed OHLCV bars
4. pass those bars into the current backtest path

Illustrative direction:

```python
from datetime import UTC, datetime, timedelta

from quantcraft.data import CCXTDataSource
from quantcraft.research import Strategy, run_backtest, ta, qc


class RsiStrategy(Strategy):
    def init(self):
        self.rsi = ta.rsi(self.data.close, length=14)

    def on_bar(self, bar):
        if qc.is_na(self.rsi[0]):
            return

        if self.rsi[0] < 30:
            self.buy(symbol=bar.symbol, quantity=1, tag="rsi-entry")
        elif self.rsi[0] > 70:
            self.sell(symbol=bar.symbol, quantity=1, tag="rsi-exit")


end = datetime.now(UTC)
start = end - timedelta(days=365)

bars = CCXTDataSource(
    exchange="binance",
    market="usdm",
    symbol="BTC/USDT:USDT",
    timeframe="1h",
    start=start,
    end=end,
).load()

result = run_backtest(
    strategy_cls=RsiStrategy,
    bars=bars,
    initial_cash=10_000,
    fee_rate=0.0004,
    tick_size=0.1,
    slippage_ticks=1,
)
```

This example is a target API illustration for the next slice, not the current implemented quickstart.

## Success Criteria

This slice is complete when:

1. users can import `CCXTDataSource`, `CSVDataSource`, and `DataFrameDataSource` from `quantcraft.data`
2. all three sources load historical inputs into the existing backtest-compatible typed OHLCV bar sequence
3. the current backtest path can consume those bars without introducing a second ingestion-only bar type
4. the first documented and tested exchange-backed path works for Binance via `ccxt`
5. CSV/DataFrame ingestion enforces the documented schema and UTC timestamp rules
6. canonical docs and quickstart materials reflect the shipped behavior clearly

## Agent Constraints

Agents implementing this slice must not:

- invent new top-level ingestion namespaces outside `quantcraft.data`
- expose raw provider payloads as the public return type
- collapse source-specific logic into `research`
- expand this slice into caching, persistence, scheduling, or live-feed infrastructure
- rename the public contract around the current OHLCV-only support shape
- invent a second public historical bar type for this slice
