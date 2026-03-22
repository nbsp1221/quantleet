from __future__ import annotations

from pathlib import Path

from quantcraft._repo_tools import collect_plan_lifecycle_issues
from scripts import repo_check
from tests.structure.repo.test_quality_scaffolding import write_valid_quality_fixture
from tests.support import ROOT


def write_exec_plan_indexes(
    root: Path,
    *,
    active_rows: list[str],
    completed_rows: list[str],
) -> None:
    active_index = root / "docs" / "exec-plans" / "active" / "index.md"
    completed_index = root / "docs" / "exec-plans" / "completed" / "index.md"
    active_index.parent.mkdir(parents=True, exist_ok=True)
    completed_index.parent.mkdir(parents=True, exist_ok=True)

    active_index.write_text(
        "\n".join(
            [
                "# Active Execution Plans",
                "",
                "## Metadata",
                "- index_status: active",
                "",
                "## Plans",
                "| Plan | Status | Note |",
                "| --- | --- | --- |",
                *active_rows,
                "",
            ]
        ),
        encoding="utf-8",
    )
    completed_index.write_text(
        "\n".join(
            [
                "# Completed Execution Plans",
                "",
                "## Metadata",
                "- index_status: completed",
                "",
                "## Plans",
                "| Plan | Status | Note |",
                "| --- | --- | --- |",
                *completed_rows,
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_exec_plan(
    root: Path,
    *,
    relative_path: str,
    status: str,
    status_reason: str | None = None,
    slice_statuses: list[str] | None = None,
) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Sample Execution Plan",
        "",
        "## Lifecycle",
        f"- status: {status}",
    ]
    if status_reason is not None:
        lines.append(f"- status_reason: {status_reason}")
    if slice_statuses is not None:
        lines.extend(["", "## Current Status"])
        for index, slice_status in enumerate(slice_statuses, start=1):
            lines.append(f"- Slice {index}: {slice_status}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_current_exec_plan_docs_use_explicit_lifecycle_metadata() -> None:
    plans_doc = (ROOT / "docs/PLANS.md").read_text(encoding="utf-8")
    active_index = (ROOT / "docs/exec-plans/active/index.md").read_text(encoding="utf-8")
    completed_index = (ROOT / "docs/exec-plans/completed/index.md").read_text(encoding="utf-8")
    completed_harness_plan = (
        ROOT / "docs/exec-plans/completed/2026-03-22-harness-quality-improvement.md"
    ).read_text(encoding="utf-8")
    completed_plan = (
        ROOT / "docs/exec-plans/completed/2026-03-21-backtest-mvp-implementation.md"
    ).read_text(encoding="utf-8")

    assert "## Lifecycle Metadata" in plans_doc
    assert "| Plan | Status | Note |" in active_index
    assert "| Plan | Status | Note |" in completed_index
    assert "_None currently active_" in active_index
    assert "- status: completed" in completed_harness_plan
    assert "Slice 5: complete" in completed_harness_plan
    assert "- status: completed" in completed_plan
    assert "2026-03-21-backtest-mvp-implementation.md" not in active_index
    assert "2026-03-21-backtest-mvp-implementation.md" in completed_index
    assert "2026-03-22-harness-quality-improvement.md" not in active_index
    assert "2026-03-22-harness-quality-improvement.md" in completed_index


def test_collect_plan_lifecycle_issues_flags_status_directory_mismatch(tmp_path: Path) -> None:
    write_exec_plan_indexes(
        tmp_path,
        active_rows=[
            "| [`2026-03-22-sample.md`](2026-03-22-sample.md) | active | Still in progress. |",
        ],
        completed_rows=[],
    )
    write_exec_plan(
        tmp_path,
        relative_path="docs/exec-plans/active/2026-03-22-sample.md",
        status="completed",
    )

    issues = collect_plan_lifecycle_issues(tmp_path)

    assert (
        "Execution plan docs/exec-plans/active/2026-03-22-sample.md is under "
        "docs/exec-plans/active/ but declares status completed"
    ) in issues


def test_collect_plan_lifecycle_issues_flags_fully_complete_active_plan_without_reason(
    tmp_path: Path,
) -> None:
    write_exec_plan_indexes(
        tmp_path,
        active_rows=[
            "| [`2026-03-22-sample.md`](2026-03-22-sample.md) | active | Work in progress. |",
        ],
        completed_rows=[],
    )
    write_exec_plan(
        tmp_path,
        relative_path="docs/exec-plans/active/2026-03-22-sample.md",
        status="active",
        slice_statuses=["complete", "complete"],
    )

    issues = collect_plan_lifecycle_issues(tmp_path)

    assert (
        "Execution plan docs/exec-plans/active/2026-03-22-sample.md marks every "
        "slice complete but remains active without status_reason"
    ) in issues


def test_collect_plan_lifecycle_issues_flags_cross_index_contradiction(
    tmp_path: Path,
) -> None:
    write_exec_plan_indexes(
        tmp_path,
        active_rows=[
            "| [`2026-03-21-backtest-mvp-implementation.md`]"
            "(2026-03-21-backtest-mvp-implementation.md) | active | "
            "Incorrectly still listed here. |",
        ],
        completed_rows=[
            "| [`2026-03-21-backtest-mvp-implementation.md`]"
            "(2026-03-21-backtest-mvp-implementation.md) | completed | Archived. |",
        ],
    )
    write_exec_plan(
        tmp_path,
        relative_path="docs/exec-plans/completed/2026-03-21-backtest-mvp-implementation.md",
        status="completed",
        slice_statuses=["complete"],
    )

    issues = collect_plan_lifecycle_issues(tmp_path)

    assert (
        "Execution plan index docs/exec-plans/active/index.md references missing "
        "plan file: docs/exec-plans/active/2026-03-21-backtest-mvp-implementation.md"
    ) in issues


def test_repo_check_surfaces_plan_lifecycle_issues(tmp_path: Path) -> None:
    write_valid_quality_fixture(tmp_path)
    write_exec_plan_indexes(
        tmp_path,
        active_rows=[
            "| [`2026-03-22-sample.md`](2026-03-22-sample.md) | active | Work in progress. |",
        ],
        completed_rows=[],
    )
    write_exec_plan(
        tmp_path,
        relative_path="docs/exec-plans/active/2026-03-22-sample.md",
        status="active",
        slice_statuses=["complete"],
    )

    issues = repo_check.collect_issues(tmp_path)

    assert (
        "Execution plan docs/exec-plans/active/2026-03-22-sample.md marks every "
        "slice complete but remains active without status_reason"
    ) in issues
