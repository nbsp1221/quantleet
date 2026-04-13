from __future__ import annotations

from pathlib import Path

from quantcraft._repo_tools import parse_routing_index_entries
from scripts import check_docs, repo_check
from tests.structure.repo.test_poe_task_contracts import write_minimal_repo_docs
from tests.support import ROOT


def write_routing_index(
    root: Path,
    *,
    relative_path: str,
    title: str,
    rows: list[str],
) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                "Use this directory to route to the governing document for the task at hand.",
                "",
                "| Task Area | Document | Role | Scope | Read When |",
                "| --- | --- | --- | --- | --- |",
                *rows,
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_current_index_docs_use_routing_fields() -> None:
    design_index = (ROOT / "docs/design-docs/index.md").read_text(encoding="utf-8")
    product_index = (ROOT / "docs/product-specs/index.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for content in [design_index, product_index]:
        assert "| Task Area | Document | Role | Scope | Read When |" in content

    assert "docs/product-specs/index.md" in agents
    assert "docs/design-docs/index.md" in agents
    assert (
        "| Cleanup and promotion defaults | "
        "[`golden-principles.md`](golden-principles.md) | Governing |"
    ) in design_index


def test_product_spec_routing_index_lists_governing_current_scope_specs() -> None:
    product_index = (ROOT / "docs/product-specs/index.md").read_text(encoding="utf-8")
    entries, duplicates = parse_routing_index_entries(product_index)
    entries_by_target = {entry["target"]: entry for entry in entries}

    assert duplicates == []
    assert entries_by_target["data-ingestion.md"]["role"] == "Governing"
    assert entries_by_target["data-ingestion.md"]["scope"] == "current implemented scope"
    assert entries_by_target["backtest-mvp.md"]["role"] == "Governing"
    assert entries_by_target["backtest-mvp.md"]["scope"] == "current implemented scope"
    assert entries_by_target["research-ergonomics.md"]["role"] == "Governing"
    assert entries_by_target["research-ergonomics.md"]["scope"] == "current implemented scope"
    assert entries_by_target["backtest.md"]["role"] == "Pointer"


def test_check_docs_flags_missing_routing_index_table_for_design_docs_index(
    tmp_path: Path,
) -> None:
    write_minimal_repo_docs(tmp_path)
    design_index_path = tmp_path / "docs" / "design-docs" / "index.md"
    design_index_path.write_text(
        "# Design Doc Routing Index\n\nNo routing table yet.\n",
        encoding="utf-8",
    )

    issues = check_docs.collect_issues(tmp_path)

    assert "docs/design-docs/index.md is missing routing index table" in issues


def test_check_docs_flags_blank_scope_for_product_specs_index(
    tmp_path: Path,
) -> None:
    write_minimal_repo_docs(tmp_path)
    write_routing_index(
        tmp_path,
        relative_path="docs/product-specs/index.md",
        title="Product Spec Routing Index",
        rows=[
            "| Existing market-data behavior | [`market-data.md`](market-data.md) "
            "| Governing |  | Before changing the existing market-data codebase "
            "or its tests. |",
        ],
    )

    issues = check_docs.collect_issues(tmp_path)

    assert (
        "docs/product-specs/index.md has blank Scope field for document: market-data.md"
        in issues
    )


def test_repo_check_surfaces_invalid_routing_role(tmp_path: Path) -> None:
    write_minimal_repo_docs(tmp_path)
    write_routing_index(
        tmp_path,
        relative_path="docs/design-docs/index.md",
        title="Design Doc Routing Index",
        rows=[
            "| Repository workflow and operating norms | "
            "[`core-beliefs.md`](core-beliefs.md) | Maybe | all agent work | "
            "Before changing agent workflow docs. |",
        ],
    )
    (tmp_path / "docs" / "design-docs" / "core-beliefs.md").write_text(
        "core beliefs\n",
        encoding="utf-8",
    )
    write_routing_index(
        tmp_path,
        relative_path="docs/product-specs/index.md",
        title="Product Spec Routing Index",
        rows=[
            "| Existing market-data behavior | [`market-data.md`](market-data.md) "
            "| Governing | current implemented scope | Before changing "
            "market-data behavior. |",
        ],
    )
    (tmp_path / "docs" / "product-specs" / "market-data.md").write_text(
        "market data\n",
        encoding="utf-8",
    )

    issues = repo_check.collect_issues(tmp_path)

    assert (
        "docs/design-docs/index.md has invalid Role field for document "
        "core-beliefs.md: Maybe" in issues
    )


def test_check_docs_normalizes_legacy_design_index_rows_to_allowed_roles(tmp_path: Path) -> None:
    write_minimal_repo_docs(tmp_path)
    design_index_path = tmp_path / "docs" / "design-docs" / "index.md"
    design_index_path.write_text(
        "\n".join(
            [
                "# Design Doc Status Map",
                "",
                "| Document | Status | Canonical | Applicability | Read When | Notes |",
                "| --- | --- | --- | --- | --- | --- |",
                (
                    "| [`core-beliefs.md`](core-beliefs.md) | implemented | yes | "
                    "all agent work | Before changing repository workflow docs. | "
                    "repository workflow and operating norms |"
                ),
                (
                    "| [`trading-kernel-contract-draft-ko.md`]"
                    "(trading-kernel-contract-draft-ko.md) | implemented | no | "
                    "future trading-kernel planning | Only when evaluating future "
                    "shared trading semantics. | shared trading-kernel semantics "
                    "planning |"
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )

    issues = check_docs.collect_issues(tmp_path)

    assert (
        "docs/design-docs/index.md has invalid Role field for document "
        "trading-kernel-contract-draft-ko.md: Pointer"
    ) not in issues
