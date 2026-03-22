# ccxt Runtime Dependency Design

**Goal:** Add `ccxt` as a runtime dependency for the reset `quantcraft` project using `uv`, without manually editing the lockfile.

**Decision:** `ccxt` belongs in `[project].dependencies`, not in the dev dependency group.

**Reasoning:**
- `quantcraft` is being rebuilt as an OHLCV-fetching library.
- If package code imports and uses `ccxt` at runtime, consumers must get it when they install `quantcraft`.
- Dev dependencies are only for tooling such as `pytest`, `mypy`, and `ruff`.
- The lockfile must be updated by `uv`, not by manual edits.

**Implementation constraints:**
- Use `uv add ccxt`.
- Do not edit `uv.lock` directly.
- Keep the existing dev-tool configuration intact.
- Verify the installed package can be imported through `uv run python`.
