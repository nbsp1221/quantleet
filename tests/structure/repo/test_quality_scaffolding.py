from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from quantcraft._repo_tools import collect_quality_issues, quality_report
from scripts import repo_check, update_quality_score
from tests.structure.repo.test_poe_task_contracts import write_minimal_repo_docs
from tests.support import ROOT

FRESHNESS_RULE = (
    "- freshness_rule: Update this file when repository checks or implemented "
    "scope materially change."
)
FRESHNESS_WINDOW_DAYS = "- freshness_window_days: 30"
DATA_ROW = (
    "| data | C | `src/quantcraft/exchange.py` and "
    "`tests/unit/market_data/test_exchange_fetch_ohlcv.py` show the current "
    "exchange-backed path. | Broader bounded-context structure is still being "
    "introduced. |"
)
RESEARCH_ROW = (
    "| research | C | `src/quantcraft/research/application/backtest.py` and "
    "`tests/unit/research/application/test_strategy_surface.py` show the "
    "current backtest orchestration surface. | Research orchestration is still "
    "early and narrow. |"
)
TRADING_ROW = (
    "| trading | C | `src/quantcraft/trading/domain/state.py` and "
    "`tests/unit/trading/test_matching_and_state.py` show the current trading "
    "kernel slice. | Shared trading semantics are still largely "
    "unimplemented. |"
)
EXECUTION_ROW = (
    "| execution | D | `docs/design-docs/quantcraft-architecture.md` keeps "
    "execution as a higher-scrutiny bounded context. | No execution runtime "
    "implementation exists yet. |"
)
DOCS_SYSTEM_ROW = (
    "| docs_system | B | `docs/design-docs/index.md`, "
    "`docs/feedback-promotion-log.md`, and "
    "`tests/structure/docs/test_system_of_record_docs.py` enforce the "
    "system-of-record surface. | Harness status maps are still being tightened "
    "slice-by-slice. |"
)
VERIFICATION_ROW = (
    "| verification | B | `scripts/repo_check.py`, "
    "`tests/structure/repo/test_quality_scaffolding.py`, and `pyproject.toml` "
    "exercise the quality contract. | Quality scoring freshness and lifecycle "
    "checks still depend on this harness slice. |"
)
NO_PATH_DATA_ROW = (
    "| data | B | Exchange-backed data path exists with unit coverage. | "
    "Broader bounded-context structure is still being introduced. |"
)
MISSING_PATH_DATA_ROW = (
    "| data | B | Evidence lives in `src/quantcraft/data/missing.py`. | "
    "Broader bounded-context structure is still being introduced. |"
)
ROOT_LEVEL_DOCS_SYSTEM_ROW = (
    "| docs_system | B | `AGENTS.md`, `ARCHITECTURE.md`, "
    "`docs/feedback-promotion-log.md`, and "
    "`tests/structure/docs/test_system_of_record_docs.py` define the top-level "
    "system-of-record contract. | Harness status maps are still being "
    "tightened slice-by-slice. |"
)
README_AGENTS_VERIFICATION_ROW = (
    "| verification | B | `README.md` and `AGENTS.md` mention repo workflows. | "
    "Verification coverage is improving, but some control-plane checks are "
    "still being promoted from docs into enforcement. |"
)
GENERIC_DATA_B_ROW = (
    "| data | B | `README.md` and `AGENTS.md` mention the repository, but do "
    "not show current data implementation evidence. | Broader bounded-context "
    "structure is still being introduced. |"
)
PLANNED_DATA_C_ROW = (
    "| data | C | `docs/design-docs/quantcraft-architecture.md` documents the "
    "future bounded context direction. | The approved `data` bounded-context "
    "package is scaffolded but not yet the main implementation home. |"
)


def write_quality_repo_docs(tmp_path: Path) -> None:
    write_minimal_repo_docs(tmp_path)
    for relative_path in [
        "docs/feedback-promotion-log.md",
        "scripts/repo_check.py",
        "scripts/update_quality_score.py",
        "tests/structure/repo/test_quality_scaffolding.py",
        "tests/structure/docs/test_system_of_record_docs.py",
        "src/quantcraft/exchange.py",
        "tests/unit/market_data/test_exchange_fetch_ohlcv.py",
        "src/quantcraft/research/application/backtest.py",
        "tests/unit/research/application/test_strategy_surface.py",
        "src/quantcraft/trading/domain/state.py",
        "tests/unit/trading/test_matching_and_state.py",
    ]:
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{relative_path}\n", encoding="utf-8")


def write_valid_quality_fixture(
    tmp_path: Path,
    *,
    metadata_lines: list[str] | None = None,
    area_rows: list[str] | None = None,
) -> None:
    write_quality_repo_docs(tmp_path)
    write_quality_score(
        tmp_path,
        metadata_lines=metadata_lines,
        area_rows=area_rows,
    )


def write_quality_score(
    root: Path,
    *,
    metadata_lines: list[str] | None = None,
    area_rows: list[str] | None = None,
) -> None:
    metadata = metadata_lines or [
        "- as_of: 2026-03-22",
        FRESHNESS_WINDOW_DAYS,
        "- evidence_rule: Scores must cite current repository evidence and stay conservative.",
        FRESHNESS_RULE,
    ]
    rows = area_rows or [
        DATA_ROW,
        RESEARCH_ROW,
        TRADING_ROW,
        EXECUTION_ROW,
        DOCS_SYSTEM_ROW,
        VERIFICATION_ROW,
    ]
    (root / "docs" / "QUALITY_SCORE.md").write_text(
        "\n".join(
            [
                "# Quality Score",
                "",
                "This file tracks the current repository quality state with "
                "explicit freshness and evidence expectations.",
                "",
                "## Metadata",
                *metadata,
                "",
                "## Evidence Expectations",
                "- Keep `docs/feedback-promotion-log.md` linked from this file so "
                "agents can find the promotion loop artifact.",
                "- Each score must cite current repository evidence, not planned intent alone.",
                "- Notes should describe the main limiting gap conservatively.",
                "",
                "## Score Rubric",
                "- `A`: implemented, verified, and aligned with the documented harness contract.",
                "- `B`: working and evidenced, with bounded gaps that do not "
                "undermine current use.",
                "- `C`: partial or uneven coverage; usable but materially incomplete.",
                "- `D`: mostly planned or scaffolded; little verified implementation evidence.",
                "",
                "## Areas",
                "| Area | Score | Evidence | Notes |",
                "| --- | --- | --- | --- |",
                *rows,
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_quality_score_includes_required_metadata_and_contract_sections() -> None:
    quality_score = (ROOT / "docs/QUALITY_SCORE.md").read_text(encoding="utf-8")

    for required_text in [
        "## Metadata",
        "- as_of:",
        "- freshness_window_days:",
        "- evidence_rule:",
        "- freshness_rule:",
        "## Evidence Expectations",
        "## Score Rubric",
        "| Area | Score | Evidence | Notes |",
    ]:
        assert required_text in quality_score


def test_quality_score_tracks_required_areas_as_table_rows() -> None:
    quality_score = (ROOT / "docs/QUALITY_SCORE.md").read_text(encoding="utf-8")

    for area in ["data", "research", "trading", "execution", "docs_system", "verification"]:
        assert f"| {area} |" in quality_score


def test_repo_check_flags_missing_quality_metadata(tmp_path: Path) -> None:
    write_valid_quality_fixture(
        tmp_path,
        metadata_lines=[
            FRESHNESS_WINDOW_DAYS,
            "- evidence_rule: Scores must cite current repository evidence and "
            "stay conservative.",
            FRESHNESS_RULE,
        ],
    )

    issues = collect_quality_issues(tmp_path)

    assert "Missing quality metadata field: as_of" in issues


def test_repo_check_flags_stale_quality_as_of_date(tmp_path: Path) -> None:
    write_valid_quality_fixture(
        tmp_path,
        metadata_lines=[
            "- as_of: 2026-02-01",
            FRESHNESS_WINDOW_DAYS,
            "- evidence_rule: Scores must cite current repository evidence and "
            "stay conservative.",
            FRESHNESS_RULE,
        ],
    )

    issues = collect_quality_issues(tmp_path, today=date(2026, 3, 22))

    assert "Quality metadata field as_of is stale for freshness_window_days: 30" in issues


def test_repo_check_flags_future_quality_as_of_date(tmp_path: Path) -> None:
    write_valid_quality_fixture(
        tmp_path,
        metadata_lines=[
            "- as_of: 9999-01-01",
            FRESHNESS_WINDOW_DAYS,
            "- evidence_rule: Scores must cite current repository evidence and "
            "stay conservative.",
            FRESHNESS_RULE,
        ],
    )

    issues = collect_quality_issues(tmp_path)

    assert "Quality metadata field as_of cannot be in the future" in issues


def test_repo_check_flags_missing_required_quality_area_row(tmp_path: Path) -> None:
    write_valid_quality_fixture(
        tmp_path,
        area_rows=[
            DATA_ROW,
            RESEARCH_ROW,
            TRADING_ROW,
            EXECUTION_ROW,
            DOCS_SYSTEM_ROW,
        ],
    )

    issues = collect_quality_issues(tmp_path)

    assert "Missing quality area row: verification" in issues


def test_repo_check_accepts_root_level_canonical_paths_for_docs_system_evidence(
    tmp_path: Path,
) -> None:
    write_valid_quality_fixture(
        tmp_path,
        area_rows=[
            DATA_ROW,
            RESEARCH_ROW,
            TRADING_ROW,
            EXECUTION_ROW,
            ROOT_LEVEL_DOCS_SYSTEM_ROW,
            VERIFICATION_ROW,
        ],
    )

    issues = collect_quality_issues(tmp_path, today=date(2026, 3, 22))

    assert "Quality evidence for docs_system" not in " ".join(issues)


def test_repo_check_flags_quality_evidence_without_repo_path_reference(tmp_path: Path) -> None:
    write_valid_quality_fixture(
        tmp_path,
        area_rows=[
            NO_PATH_DATA_ROW,
            RESEARCH_ROW,
            TRADING_ROW,
            EXECUTION_ROW,
            DOCS_SYSTEM_ROW,
            VERIFICATION_ROW,
        ],
    )

    issues = collect_quality_issues(tmp_path)

    assert "Quality evidence for data must reference at least one repository path" in issues


def test_repo_check_flags_quality_evidence_with_missing_repo_path(tmp_path: Path) -> None:
    write_valid_quality_fixture(
        tmp_path,
        area_rows=[
            MISSING_PATH_DATA_ROW,
            RESEARCH_ROW,
            TRADING_ROW,
            EXECUTION_ROW,
            DOCS_SYSTEM_ROW,
            VERIFICATION_ROW,
        ],
    )

    issues = collect_quality_issues(tmp_path)

    assert (
        "Quality evidence for data references missing repository path: "
        "src/quantcraft/data/missing.py"
    ) in issues


def test_repo_check_flags_generic_evidence_for_stronger_data_grade(tmp_path: Path) -> None:
    write_valid_quality_fixture(
        tmp_path,
        area_rows=[
            GENERIC_DATA_B_ROW,
            RESEARCH_ROW,
            TRADING_ROW,
            EXECUTION_ROW,
            DOCS_SYSTEM_ROW,
            VERIFICATION_ROW,
        ],
    )

    issues = collect_quality_issues(tmp_path, today=date(2026, 3, 22))

    assert (
        "Quality evidence for data score B must include at least one area-relevant path"
        in issues
    )


def test_repo_check_flags_planned_direction_only_for_data_score_c(tmp_path: Path) -> None:
    write_valid_quality_fixture(
        tmp_path,
        area_rows=[
            PLANNED_DATA_C_ROW,
            RESEARCH_ROW,
            TRADING_ROW,
            EXECUTION_ROW,
            DOCS_SYSTEM_ROW,
            VERIFICATION_ROW,
        ],
    )

    issues = collect_quality_issues(tmp_path, today=date(2026, 3, 22))

    assert (
        "Quality evidence for data score C must include at least one "
        "implementation or test path"
    ) in issues


def test_repo_check_flags_docs_only_verification_score_b(tmp_path: Path) -> None:
    write_valid_quality_fixture(
        tmp_path,
        area_rows=[
            DATA_ROW,
            RESEARCH_ROW,
            TRADING_ROW,
            EXECUTION_ROW,
            DOCS_SYSTEM_ROW,
            README_AGENTS_VERIFICATION_ROW,
        ],
    )

    issues = collect_quality_issues(tmp_path, today=date(2026, 3, 22))

    assert (
        "Quality evidence for verification score B must include at least one "
        "harness-check path"
    ) in issues


def test_update_quality_score_report_marks_docs_only_verification_as_invalid(
    tmp_path: Path,
) -> None:
    write_valid_quality_fixture(
        tmp_path,
        area_rows=[
            DATA_ROW,
            RESEARCH_ROW,
            TRADING_ROW,
            EXECUTION_ROW,
            DOCS_SYSTEM_ROW,
            README_AGENTS_VERIFICATION_ROW,
        ],
    )

    report = update_quality_score.build_quality_score_report(
        tmp_path,
        today=date(2026, 3, 22),
    )

    assert (
        "Quality evidence for verification score B must include at least one "
        "harness-check path"
    ) in report["quality_issues"]
    assert report["quality_validation"]["evidence_status"]["verification"] == "invalid"


def test_repo_check_flags_duplicate_quality_area_rows(tmp_path: Path) -> None:
    write_valid_quality_fixture(
        tmp_path,
        area_rows=[
            DATA_ROW,
            DATA_ROW,
            RESEARCH_ROW,
            TRADING_ROW,
            EXECUTION_ROW,
            DOCS_SYSTEM_ROW,
            VERIFICATION_ROW,
        ],
    )

    issues = collect_quality_issues(tmp_path, today=date(2026, 3, 22))

    assert "Duplicate quality area row: data" in issues


def test_quality_report_exposes_metadata_and_tracked_areas() -> None:
    report = json.loads(quality_report(ROOT))

    assert "quality_score" in report
    assert report["quality_score"]["metadata"]["as_of"]
    assert "verification" in report["quality_score"]["tracked_areas"]


def test_update_quality_score_report_surfaces_validation_status(tmp_path: Path) -> None:
    write_valid_quality_fixture(
        tmp_path,
        metadata_lines=[
            "- as_of: 9999-01-01",
            FRESHNESS_WINDOW_DAYS,
            "- evidence_rule: Scores must cite current repository evidence and "
            "stay conservative.",
            FRESHNESS_RULE,
        ],
        area_rows=[
            MISSING_PATH_DATA_ROW,
            RESEARCH_ROW,
            TRADING_ROW,
            EXECUTION_ROW,
            DOCS_SYSTEM_ROW,
            VERIFICATION_ROW,
        ],
    )

    report = update_quality_score.build_quality_score_report(
        tmp_path,
        today=date(2026, 3, 22),
    )

    assert report["quality_validation"]["issue_count"] >= 2
    assert "Quality metadata field as_of cannot be in the future" in report["quality_issues"]
    assert report["quality_validation"]["evidence_status"]["data"] == "invalid"


def test_repo_check_script_surface_collects_quality_contract_failures(tmp_path: Path) -> None:
    write_valid_quality_fixture(
        tmp_path,
        area_rows=[
            NO_PATH_DATA_ROW,
            RESEARCH_ROW,
            TRADING_ROW,
            EXECUTION_ROW,
            DOCS_SYSTEM_ROW,
            VERIFICATION_ROW,
        ],
    )

    issues = repo_check.collect_issues(tmp_path)

    assert "Quality evidence for data must reference at least one repository path" in issues
