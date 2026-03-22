# Quality Score

This file tracks the current repository quality state with explicit freshness and evidence expectations.

## Metadata

- as_of: 2026-03-22
- freshness_window_days: 30
- evidence_rule: Scores must cite current repository evidence and stay conservative when code, tests, and docs do not all align.
- freshness_rule: Update this file when implemented scope, verification coverage, or repository control-plane checks materially change.

## Evidence Expectations

- Keep `docs/feedback-promotion-log.md` linked from this file so agents can find the current promotion-loop artifact.
- A score must be backed by repository-visible evidence such as current code, tests, or enforced docs.
- `as_of` becomes invalid once it is older than `freshness_window_days`.
- Each tracked area may appear only once in the table.
- Planned direction alone is not enough to score above `D`.
- `A` and `B` scores must cite at least two valid repository paths.
- `A` and `B` scores must include at least one area-relevant path.
- `verification` scores of `A` or `B` must include at least one harness-check path such as `scripts/`, `tests/`, or `pyproject.toml`; repo docs alone are not enough.
- For implementation areas (`data`, `research`, `trading`, `execution`, `ml`), any score above `D` must include at least one implementation or test path, not docs alone.
- Notes should identify the main limitation that keeps the area from the next grade.

## Score Rubric

- `A`: implemented, verified, and aligned with the documented harness contract.
- `B`: working and evidenced, with bounded gaps that do not undermine current use.
- `C`: partial or uneven coverage; usable but materially incomplete.
- `D`: mostly planned or scaffolded; little verified implementation evidence.

## Areas

| Area | Score | Evidence | Notes |
| --- | --- | --- | --- |
| data | C | Exchange-backed market-data code exists in `src/quantcraft/exchange.py` and has unit coverage in `tests/unit/market_data/test_exchange_fetch_ohlcv.py`. | The approved `data` bounded-context package is scaffolded but not yet the main implementation home. |
| research | C | Backtest orchestration and strategy surface exist in `src/quantcraft/research/application/`, with unit and integration coverage under `tests/unit/research/` and `tests/integration/research/`. | The research surface is still narrow and tied to the current MVP slice. |
| trading | C | Trading domain modules exist in `src/quantcraft/trading/domain/` with contract and state tests under `tests/unit/trading/`. | The shared trading kernel direction is only partially implemented and not yet proven across multiple environments. |
| execution | D | `docs/design-docs/quantcraft-architecture.md` keeps `execution` as a higher-scrutiny bounded context. | No `src/quantcraft/execution/` implementation or execution-specific tests exist yet. |
| docs_system | B | `docs/design-docs/index.md`, `docs/design-docs/golden-principles.md`, `docs/feedback-promotion-log.md`, and `tests/structure/docs/test_system_of_record_docs.py` define and verify the system-of-record surface. | The promotion loop is now explicit, but adding new rows to the feedback log is still a maintenance action rather than an automated capture. |
| verification | B | `scripts/repo_check.py`, `scripts/update_quality_score.py`, and `tests/structure/repo/test_quality_scaffolding.py` exercise the quality-score contract. | Verification coverage is improving, but some control-plane checks are still being promoted from docs into enforcement. |
| ml | D | `docs/design-docs/quantcraft-architecture.md` keeps `ml` deferred until the core four contexts stabilize. | There is no implemented `ml` package or verification surface yet. |
