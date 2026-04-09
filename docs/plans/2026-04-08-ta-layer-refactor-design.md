# TA Layer Refactor Design

## Status

- Status: `approved baseline`
- Class: `design`
- Scope: `research` indicator architecture, public contract realignment, and layer ownership

Related documents:

- [../../AGENTS.md](../../AGENTS.md)
- [../../ARCHITECTURE.md](../../ARCHITECTURE.md)
- [../product-specs/research-ergonomics.md](../product-specs/research-ergonomics.md)
- [../RELIABILITY.md](../RELIABILITY.md)
- [../design-docs/architecture-governance.md](../design-docs/architecture-governance.md)
- [../references/openai-harness-engineering.md](../references/openai-harness-engineering.md)
- [../exec-plans/completed/2026-04-08-ta-layer-refactor-implementation.md](../exec-plans/completed/2026-04-08-ta-layer-refactor-implementation.md)

## Goal

Keep the official `quantcraft.research.ta` public namespace, but refactor the
implementation into three layers:

- pure indicator layer
- runtime adapter layer
- public facade layer

This refactor exists to:

- split indicator ownership into small file-level units
- separate indicator math from runtime concerns
- preserve the current `Strategy` + `SeriesView` live causal contract
- split testing into pure correctness and runtime-contract coverage

## Core Decisions

1. `quantcraft.research.ta` remains the official public import surface.
2. `TA-Lib` is the baseline computation backend for the pure indicator layer.
3. `SeriesView`, append/rebuild policy, memoization, and live-view semantics
   belong to the runtime layer.
4. Public `ta.*` functions do not expose pure functions directly; they return
   runtime-adapted views that satisfy the current research ergonomics contract.
5. Indicator implementation and indicator tests must follow source ownership.
6. Internal module naming and canonical public naming follow Pine Script
   built-in naming where appropriate.
7. Compatibility shims are allowed only during intermediate migration and must
   not remain in the final state.
8. If semantic divergence is observed, the agent must not interpret it
   autonomously and must escalate to a human immediately.

## Why This Direction

The current structure concentrates too much indicator responsibility in a few
files:

- `src/quantcraft/research/ta.py`
- `src/quantcraft/research/_indicator_runtime.py`
- `src/quantcraft/research/_indicator_kernels.py`
- `tests/unit/research/test_indicator_surface.py`
- `tests/unit/research/test_indicator_runtime.py`

With that structure, changing one indicator still requires reading large shared
files, and pure-calculation correctness is mixed with runtime synchronization
behavior.

By contrast, `coinfluent`'s `quantleet.utils.ta` has clearer per-indicator file
ownership and per-indicator tests. However, `coinfluent` is mainly an
array-batch wrapper design, while `quantcraft` has a live causal contract where
indicators bound in `Strategy.init()` continue to update as bars arrive. That
means `quantcraft` should adopt the ownership model without dropping the runtime
layer.

## External Evidence

### 1. Clear importable package boundaries

The Python Packaging User Guide explains why `src` layout helps keep importable
code inside explicit package boundaries.

Source:

- https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/

### 2. Test layout should mirror source ownership

`pytest` good practices recommend predictable package and test structure.
Source-aligned tests reduce drift and lower navigation cost.

Source:

- https://docs.pytest.org/en/stable/explanation/goodpractices.html

### 3. TA-Lib availability

The `TA-Lib` Python package currently supports Python 3.13 and NumPy 2 in the
`0.6.x` line.

Sources:

- https://pypi.org/project/TA-Lib/
- https://ta-lib.org/install/

### 4. Pine built-in naming alignment

TradingView Pine v5 documents indicator built-ins under the `ta` namespace,
including `ta.sma()`, `ta.ema()`, `ta.rsi()`, `ta.atr()`, `ta.cci()`,
`ta.macd()`, and `ta.bb()`.

Sources:

- https://www.tradingview.com/pine-script-docs/language/built-ins/
- https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-5

### 5. Self-contained execution authority

OpenAI's ExecPlan guidance says long-running agent work should use self-contained
artifacts with explicit success paths and demonstrably working outcomes. This is
why this document stays as the structure and contract authority while execution
authority is split into a separate implementation artifact.

Source:

- https://developers.openai.com/cookbook/articles/codex_exec_plans

## Non-Goals

This refactor does not aim to:

- remove the `quantcraft.research.ta` namespace
- convert public research ergonomics into a batch-array API
- add plotting, parameter sweeps, or walk-forward tooling
- promote indicator cache behavior into the public contract
- keep maintaining indicator math by hand

## Public Contract Direction

The public namespace stays, but indicator naming aligns with Pine built-ins.

### Approved Target Public Naming

| Current `quantcraft` public name | Target public name | Decision |
| --- | --- | --- |
| `ta.sma` | `ta.sma` | keep |
| `ta.ema` | `ta.ema` | keep |
| `ta.rsi` | `ta.rsi` | keep |
| `ta.atr` | `ta.atr` | keep |
| `ta.cci` | `ta.cci` | keep |
| `ta.macd` | `ta.macd` | keep |
| `ta.bollinger_bands` | `ta.bb` | rename |

Rules:

- the canonical public name is `ta.bb(...)`
- `ta.bollinger_bands(...)` is removed from the documented public contract
- temporary shims are allowed only during intermediate migration
- the final repository state must not contain shims, aliases, or deprecated exports

### `ta.bb` Public Return Contract

`ta.bb(...)` returns a named result object, not a tuple or dict.

Reasons:

- the current `quantcraft` research ergonomics contract already models
  multi-output indicators as named result objects
- in Python, attribute access is more readable and self-describing than
  index-based tuple access
- the goal is Pine-style naming, not blindly copying Pine's tuple-oriented
  interface into a Python public API

Public contract:

- function name: `ta.bb(series, length=20, stddev=2)`
- return type: `BollingerBandsResult`
- approved fields:
  - `middle`
  - `upper`
  - `lower`
- each field is a causal read-only series
- tuple ordering is not part of the public contract
- dict-style access is not part of the public contract

Internal normalization rule:

- even if Pine or TA-Lib exposes order-based multi-output data, the public
  facade must normalize it into a named result object
- public field mapping is fixed:
  - backend middle/basis -> `BollingerBandsResult.middle`
  - backend upper -> `BollingerBandsResult.upper`
  - backend lower -> `BollingerBandsResult.lower`

This slice changes the public function name to `bb` but keeps the more explicit
public result-object type name from the current product contract.

## Semantic Divergence Policy

This refactor aims to make the current `quantcraft` contract, the new pure
`TA-Lib` backend, and Pine-aligned target semantics converge. However,
divergence may still appear in areas such as:

- warmup length
- `NaN` propagation
- EMA seed behavior
- invalid parameter handling
- multi-output ordering

If divergence is observed through canonical fixtures or tests:

1. the agent must not pick a winner autonomously
2. the agent must not normalize to whichever backend is easiest to implement
3. the work must stop and escalate to a human, with mismatch evidence recorded

The default tie-breaker is therefore human escalation, not autonomous inference.

## Product Contract Preservation

This refactor must preserve the following:

1. `from quantcraft.research import ta` remains the public surface
2. existing strategy call style such as `ta.sma(self.data.close, length=...)`
   continues to work
3. indicators bound in `Strategy.init()` continue to behave as live causal views
4. `SeriesView` history semantics remain intact
5. changing names must not change the current strategy ergonomics call style

Exception:

- if preserving the current public contract becomes structurally incompatible
  with the new design, that API change must be documented first, before code is
  changed

## Structure Freeze

Rules:

- implementation agents use the structure below as the default target
- if another structure seems better, do not switch silently; update the design
  document first

Allowed ownership layers:

- `pure`
- `runtime`

Disallowed structures:

- new underscore-prefixed mega files
- re-accumulating indicator math inside `ta.py`
- mixing runtime concerns into pure modules
- regressing to large `test_indicator_*` concentration files
- centralizing unrelated multi-output result types in a shared registry module

## Approved Package Layout

### Public Facade

- `src/quantcraft/research/ta.py`

Responsibilities:

- keep the official import surface
- keep public signatures
- construct runtime adapters only

Forbidden:

- direct pure-calculation implementation
- direct caching implementation
- direct synchronization policy implementation

### Pure Indicator Layer

Paths:

- `src/quantcraft/research/indicators/`
- `src/quantcraft/research/indicators/pure/`

Required files:

- `src/quantcraft/research/indicators/__init__.py`
- `src/quantcraft/research/indicators/pure/__init__.py`
- `src/quantcraft/research/indicators/pure/sma.py`
- `src/quantcraft/research/indicators/pure/ema.py`
- `src/quantcraft/research/indicators/pure/rsi.py`
- `src/quantcraft/research/indicators/pure/atr.py`
- `src/quantcraft/research/indicators/pure/cci.py`
- `src/quantcraft/research/indicators/pure/bb.py`
- `src/quantcraft/research/indicators/pure/macd.py`

Rules:

- each indicator file owns only that indicator's pure wrapper
- multi-output return types are owned by their indicator module
- module file names follow Pine built-in naming
- shared calculation helpers should not be introduced unless repeated duplication
  proves the need

Fixed file mapping:

- `sma.py` -> `ta.sma()`
- `ema.py` -> `ta.ema()`
- `rsi.py` -> `ta.rsi()`
- `atr.py` -> `ta.atr()`
- `cci.py` -> `ta.cci()`
- `bb.py` -> `ta.bb()`
- `macd.py` -> `ta.macd()`

### Runtime Adapter Layer

Paths:

- `src/quantcraft/research/indicators/runtime/`

Required files:

- `src/quantcraft/research/indicators/runtime/__init__.py`
- `src/quantcraft/research/indicators/runtime/base.py`
- `src/quantcraft/research/indicators/runtime/views.py`
- `src/quantcraft/research/indicators/runtime/runtime.py`
- `src/quantcraft/research/indicators/runtime/factory.py`

Rules:

- the runtime layer treats pure functions as external utilities
- the runtime layer must not reimplement indicator math

## Approved Test Layout

### Public Surface

- `tests/unit/research/test_indicator_surface.py`

This file must lock:

- `ta.bb` as the canonical public surface
- removal of any legacy alias from the final state
- Pine-aligned public naming
- the documented `BollingerBandsResult` contract

### Pure Indicator Tests

- `tests/unit/research/indicators/pure/test_sma.py`
- `tests/unit/research/indicators/pure/test_ema.py`
- `tests/unit/research/indicators/pure/test_rsi.py`
- `tests/unit/research/indicators/pure/test_atr.py`
- `tests/unit/research/indicators/pure/test_cci.py`
- `tests/unit/research/indicators/pure/test_bb.py`
- `tests/unit/research/indicators/pure/test_macd.py`

Each indicator test must cover at least:

1. signature or wrapper contract
2. small hand-checkable fixtures
3. warmup / `NaN` behavior
4. flat-input behavior
5. insufficient-history behavior
6. invalid-parameter behavior
7. type and shape behavior
8. multi-output ordering or mapping

Additional rules:

- `test_bb.py` also validates the result type owned by `bb.py`
- `test_macd.py` also validates the result type owned by `macd.py`
- do not introduce a central result-type test module

### Runtime Adapter Tests

- `tests/unit/research/indicators/runtime/test_runtime.py`
- `tests/unit/research/indicators/runtime/test_views.py`
- `tests/unit/research/indicators/runtime/test_factory.py`

These tests must cover at least:

1. stable-length memoization
2. monotonic append fast path
3. rebuild on source-shape change
4. multi-source synchronization
5. multi-output view cache sharing
6. live indicator bindings created in `Strategy.init()`
7. facade preservation of the current public runtime contract

## Why These Paths Are Fixed

These paths are fixed because:

1. `src` layout favors clear importable package boundaries
2. `pytest` favors source-aligned test structure
3. this repository already enforces source mirroring and disallows flat root tests

Additional design inference:

- fixing the runtime layer to `base/views/runtime/factory` is not a direct quote
  from an external source; it is a repo-scale judgment about how to keep
  responsibilities clear
- refusing a shared `results.py` follows the same reasoning: with only `bb` and
  `macd` as practical multi-output cases, centralizing unrelated result types
  would reduce ownership locality

## TA-Lib Adoption Policy

This design adopts `TA-Lib` as the baseline pure-computation backend instead of
continuing to maintain indicator math by hand.

Reasons:

- lower maintenance cost for indicator math
- lower correctness risk
- reusable thin-wrapper structure
- clearer per-indicator file ownership

Constraints:

- `TA-Lib` is batch-oriented
- runtime adapters are still required to preserve the current research ergonomics
- adding a pure layer does not imply removing the runtime layer

## Design-Scope Success Conditions

This design document is successful when it makes the following explicit:

1. the canonical public naming table
2. the `ta.bb` public return contract
3. the default human-escalation rule for semantic divergence
4. the rule that no shim, alias, or legacy path may remain in the final state
5. the approved package layout
6. the approved test layout
7. the fact that execution authority lives in the active implementation plan
