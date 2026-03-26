# Data Ingestion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add the first official historical data-ingestion surface under `quantcraft.data` with `CCXTDataSource`, `CSVDataSource`, and `DataFrameDataSource`, all normalizing into the existing backtest-compatible typed OHLCV bar sequence.

**Architecture:** Keep acquisition and normalization in `data`, reuse existing market-data and backtest-compatible OHLCV shapes instead of inventing a second public bar type, and keep the first slice strictly historical-only. Prefer a small public `DataSource -> load() -> typed bars` contract over a larger feed/runtime abstraction.

**Tech Stack:** Python 3.13, `uv`, `pytest`, existing `ccxt` integration in `src/quantcraft/exchange.py`, current `research` backtest path, repository structure checks.

---

### Task 1: Establish the canonical data-domain bar type and public data namespace

**Files:**
- Create: `src/quantcraft/data/domain/bars.py`
- Create: `src/quantcraft/data/domain/sources.py`
- Modify: `src/quantcraft/data/domain/__init__.py`
- Modify: `src/quantcraft/data/__init__.py`
- Test: `tests/unit/data/domain/test_bars.py`
- Test: `tests/unit/data/domain/test_sources.py`

**Step 1: Write the failing tests**

Add tests that pin:
- the canonical normalized OHLCV bar type lives under `quantcraft.data.domain`
- the public namespace exports only the approved source names
- the source protocol remains the minimal `load() -> typed bars` shape

```python
from quantcraft.data import CCXTDataSource, CSVDataSource, DataFrameDataSource
from quantcraft.data.domain import OHLCVBar


def test_data_domain_exports_canonical_ohlcv_bar() -> None:
    bar = OHLCVBar(
        timestamp=1_700_000_000_000,
        open=1.0,
        high=2.0,
        low=0.5,
        close=1.5,
        volume=10.0,
    )
    assert bar.close == 1.5


def test_public_data_namespace_exports_approved_sources() -> None:
    assert CCXTDataSource is not None
    assert CSVDataSource is not None
    assert DataFrameDataSource is not None
```

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/unit/data/domain/test_bars.py tests/unit/data/domain/test_sources.py -q
```

Expected:
- FAIL because the new files and exports do not exist yet

**Step 3: Write the minimal implementation**

Implement:
- a frozen `OHLCVBar` dataclass in `src/quantcraft/data/domain/bars.py`
- a small `HistoricalDataSource` protocol or abstract base in `src/quantcraft/data/domain/sources.py`
- domain exports in `src/quantcraft/data/domain/__init__.py`
- public exports in `src/quantcraft/data/__init__.py`

The public surface should export:
- `OHLCVBar`
- `CCXTDataSource`
- `CSVDataSource`
- `DataFrameDataSource`

Do not add feed, stream, or runtime lifecycle methods.

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/unit/data/domain/test_bars.py tests/unit/data/domain/test_sources.py -q
```

Expected:
- PASS

**Step 5: Commit**

```bash
git add src/quantcraft/data/domain/bars.py src/quantcraft/data/domain/sources.py src/quantcraft/data/domain/__init__.py src/quantcraft/data/__init__.py tests/unit/data/domain/test_bars.py tests/unit/data/domain/test_sources.py
git commit -m "✨ Add data-domain OHLCV bar contract"
```

### Task 2: Implement CCXTDataSource on top of the existing exchange utility

**Files:**
- Create: `src/quantcraft/data/adapters/ccxt_source.py`
- Modify: `src/quantcraft/data/__init__.py`
- Modify: `src/quantcraft/data/adapters/__init__.py`
- Reuse: `src/quantcraft/exchange.py`
- Test: `tests/unit/data/adapters/test_ccxt_source.py`
- Migrate or replace: `tests/unit/market_data/test_exchange_fetch_ohlcv.py`

**Step 1: Write the failing tests**

Add tests that pin:
- `CCXTDataSource(...).load()` returns the canonical `OHLCVBar` sequence
- explicit constructor args are required
- Binance is the documented/tested guarantee, but the implementation stays provider-generic
- non-Binance exchanges are not hard-blocked if the underlying `Exchange` path supports them

```python
def test_ccxt_source_loads_binance_usdm_bars(monkeypatch):
    ...
    source = CCXTDataSource(
        exchange="binance",
        market="usdm",
        symbol="BTC/USDT:USDT",
        timeframe="1h",
        start=1_700_000_000_000,
        end=1_700_000_300_000,
    )
    bars = source.load()
    assert bars[0].timestamp == 1_700_000_000_000


def test_ccxt_source_does_not_hard_block_other_supported_exchanges(monkeypatch):
    ...
```

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/unit/data/adapters/test_ccxt_source.py -q
```

Expected:
- FAIL because `CCXTDataSource` does not exist yet

**Step 3: Write the minimal implementation**

Implement `CCXTDataSource` in `src/quantcraft/data/adapters/ccxt_source.py` by reusing `quantcraft.exchange.Exchange` instead of duplicating `ccxt` rules.

Map:
- `exchange` string -> existing `Exchange(name=...)`
- `market` string -> existing `MarketType`
- `load()` -> `Exchange.fetch_ohlcv(...)`

Keep this slice:
- synchronous
- blocking
- historical-only
- provider-native-string-first

Do not add:
- async
- public session injection
- retries
- credential surfaces

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/unit/data/adapters/test_ccxt_source.py tests/unit/market_data/test_exchange_fetch_ohlcv.py -q
```

Expected:
- PASS

**Step 5: Commit**

```bash
git add src/quantcraft/data/adapters/ccxt_source.py src/quantcraft/data/adapters/__init__.py src/quantcraft/data/__init__.py tests/unit/data/adapters/test_ccxt_source.py tests/unit/market_data/test_exchange_fetch_ohlcv.py
git commit -m "✨ Add CCXT historical data source"
```

### Task 3: Implement CSVDataSource and DataFrameDataSource with the canonical schema

**Files:**
- Create: `src/quantcraft/data/adapters/csv_source.py`
- Create: `src/quantcraft/data/adapters/dataframe_source.py`
- Modify: `src/quantcraft/data/__init__.py`
- Modify: `src/quantcraft/data/adapters/__init__.py`
- Test: `tests/unit/data/adapters/test_csv_source.py`
- Test: `tests/unit/data/adapters/test_dataframe_source.py`

**Step 1: Write the failing tests**

Add tests that pin:
- required columns: `timestamp`, `open`, `high`, `low`, `close`
- optional `volume`
- `symbol` and `timeframe` come from constructor args, not from table metadata
- naive timestamps are rejected
- timestamps normalize to UTC
- missing `volume` normalizes to `0`

```python
def test_csv_source_requires_minimal_schema(tmp_path):
    ...


def test_dataframe_source_rejects_naive_timestamps():
    ...


def test_dataframe_source_normalizes_missing_volume_to_zero():
    ...
```

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/unit/data/adapters/test_csv_source.py tests/unit/data/adapters/test_dataframe_source.py -q
```

Expected:
- FAIL because the sources do not exist yet

**Step 3: Write the minimal implementation**

Implement:
- `CSVDataSource`
- `DataFrameDataSource`

Requirements:
- normalize inputs into the canonical `OHLCVBar`
- enforce the small documented schema
- reject naive timestamps
- normalize timestamps to UTC
- fill missing `volume` with `0`

Do not add:
- schema auto-discovery beyond the documented columns
- caching
- persistence
- hidden metadata inference from CSV/DataFrame columns

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/unit/data/adapters/test_csv_source.py tests/unit/data/adapters/test_dataframe_source.py -q
```

Expected:
- PASS

**Step 5: Commit**

```bash
git add src/quantcraft/data/adapters/csv_source.py src/quantcraft/data/adapters/dataframe_source.py src/quantcraft/data/adapters/__init__.py src/quantcraft/data/__init__.py tests/unit/data/adapters/test_csv_source.py tests/unit/data/adapters/test_dataframe_source.py
git commit -m "✨ Add CSV and dataframe data sources"
```

### Task 4: Integrate the new data-domain bar contract into the current backtest path

**Files:**
- Modify: `src/quantcraft/research/adapters/synthetic_events.py`
- Modify: `src/quantcraft/research/application/backtest.py`
- Modify: `src/quantcraft/research/application/__init__.py`
- Test: `tests/unit/research/adapters/test_synthetic_events.py`
- Test: `tests/integration/research/test_backtest_runner.py`

**Step 1: Write the failing tests**

Add or adjust tests so the current backtest path consumes the `data.domain.OHLCVBar` contract directly, rather than a second ingestion-only type.

```python
def test_backtest_path_accepts_data_domain_ohlcv_bars():
    ...
```

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/unit/research/adapters/test_synthetic_events.py tests/integration/research/test_backtest_runner.py -q
```

Expected:
- FAIL due to type mismatch or old `research`-local bar assumptions

**Step 3: Write the minimal implementation**

Refactor the research/backtest path so that:
- `convert_ohlcv_to_backtest_events(...)` accepts the canonical `data.domain.OHLCVBar`
- `run_backtest(...)` can be fed by the new ingestion sources without inventing a second public historical bar type

Keep the current backtest semantics unchanged.

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/unit/research/adapters/test_synthetic_events.py tests/integration/research/test_backtest_runner.py -q
```

Expected:
- PASS

**Step 5: Commit**

```bash
git add src/quantcraft/research/adapters/synthetic_events.py src/quantcraft/research/application/backtest.py src/quantcraft/research/application/__init__.py tests/unit/research/adapters/test_synthetic_events.py tests/integration/research/test_backtest_runner.py
git commit -m "♻️ Reuse data-domain OHLCV bars in backtest path"
```

### Task 5: Update docs, quickstart materials, and structure checks for the shipped slice

**Files:**
- Modify: `README.md`
- Modify: `docs/product-specs/market-data.md`
- Modify: `docs/product-specs/data-ingestion.md`
- Modify: `docs/product-specs/index.md`
- Modify: `docs/references/research-ergonomics-quickstart.md`
- Modify: `notebooks/research-ergonomics-quickstart.ipynb`
- Modify: `tests/structure/docs/test_system_of_record_docs.py`
- Modify: `tests/structure/repo/test_index_status_maps.py`
- Modify: `tests/structure/repo/test_repository_entrypoint_docs.py`

**Step 1: Write the failing tests**

Add or update tests that pin:
- the new slice status after implementation
- the docs point to the correct spec
- quickstart/examples show the shipped ingestion surface clearly

```python
def test_product_spec_index_includes_data_ingestion_status():
    ...


def test_repository_entry_docs_reference_shipped_data_ingestion_surface():
    ...
```

**Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/structure/docs tests/structure/repo -q
```

Expected:
- FAIL because docs and status maps still describe this slice as only approved

**Step 3: Write the minimal implementation**

Promote docs from approved-next-slice to implemented-current-scope only after the code is actually shipped and verified.

Update:
- status maps
- quickstart materials
- repository entry docs

Do not promote the slice early.

**Step 4: Run tests to verify they pass**

Run:

```bash
uv run pytest tests/structure/docs tests/structure/repo -q
```

Expected:
- PASS

**Step 5: Commit**

```bash
git add README.md docs/product-specs/market-data.md docs/product-specs/data-ingestion.md docs/product-specs/index.md docs/references/research-ergonomics-quickstart.md notebooks/research-ergonomics-quickstart.ipynb tests/structure/docs/test_system_of_record_docs.py tests/structure/repo/test_index_status_maps.py tests/structure/repo/test_repository_entrypoint_docs.py
git commit -m "📝 Promote shipped data ingestion docs"
```

### Task 6: Run final repository verification

**Files:**
- No new files expected

**Step 1: Run the full verification lane**

Run:

```bash
uv run ruff check .
uv run mypy src
uv run pytest -q
uv run python scripts/repo_check.py
uv run python scripts/notebook_validate.py
uv build
```

Expected:
- all commands pass

**Step 2: Review against the spec**

Check the finished code and docs against:
- `docs/product-specs/data-ingestion.md`
- `docs/product-specs/market-data.md`
- `docs/product-specs/backtest-mvp.md`
- `docs/product-specs/research-ergonomics.md`

Confirm:
- no second public historical bar type was introduced
- ingestion stayed in `quantcraft.data`
- the slice remained historical-only
- Binance is the first documented/tested exchange-backed guarantee

**Step 3: Commit any final verification-only doc fixes**

```bash
git add .
git commit -m "🧑‍💻 Finalize data ingestion slice verification"
```
