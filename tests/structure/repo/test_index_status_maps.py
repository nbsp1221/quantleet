from __future__ import annotations

from pathlib import Path

from scripts import check_docs, repo_check
from tests.structure.repo.test_poe_task_contracts import write_minimal_repo_docs
from tests.structure.repo.test_quality_scaffolding import write_valid_quality_fixture
from tests.support import ROOT


def write_status_map_index(
    root: Path,
    *,
    relative_path: str,
    index_kind: str,
    rows: list[str],
) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f"# {path.parent.name.title()}",
                "",
                "## Metadata",
                f"- index_kind: {index_kind}",
                "",
                "## Documents",
                "| Document | Status | Canonical | Applicability | Read When | Notes |",
                "| --- | --- | --- | --- | --- | --- |",
                *rows,
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_current_index_docs_use_explicit_status_map_fields() -> None:
    design_index = (ROOT / "docs/design-docs/index.md").read_text(encoding="utf-8")
    product_index = (ROOT / "docs/product-specs/index.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for content in [design_index, product_index]:
        assert "## Metadata" in content
        assert "## Documents" in content
        assert (
            "| Document | Status | Canonical | Applicability | Read When | Notes |"
            in content
        )

    assert "Status`, `Canonical`, `Applicability`, and `Read When`" in agents
    assert "| [`golden-principles.md`](golden-principles.md) | approved | yes |" in design_index


def test_check_docs_flags_missing_status_map_header_for_design_docs_index(
    tmp_path: Path,
) -> None:
    write_minimal_repo_docs(tmp_path)
    design_index_path = tmp_path / "docs" / "design-docs" / "index.md"
    design_index_path.write_text(
        design_index_path.read_text(encoding="utf-8").replace("## Documents", "## Entries"),
        encoding="utf-8",
    )

    issues = check_docs.collect_issues(tmp_path)

    assert "docs/design-docs/index.md is missing required heading: ## Documents" in issues


def test_check_docs_flags_missing_required_status_map_field_for_product_specs_index(
    tmp_path: Path,
) -> None:
    write_minimal_repo_docs(tmp_path)
    write_status_map_index(
        tmp_path,
        relative_path="docs/product-specs/index.md",
        index_kind="product-spec-status-map",
        rows=[
            "| [`market-data.md`](market-data.md) | implemented | yes | current implemented scope "
            "|  | Current implemented-scope entry. |",
        ],
    )

    issues = check_docs.collect_issues(tmp_path)

    assert (
        "docs/product-specs/index.md has blank Read When field for document: market-data.md"
        in issues
    )


def test_repo_check_surfaces_index_status_map_contract_failures(tmp_path: Path) -> None:
    write_valid_quality_fixture(tmp_path)
    write_status_map_index(
        tmp_path,
        relative_path="docs/design-docs/index.md",
        index_kind="design-doc-status-map",
        rows=[
            "| [`core-beliefs.md`](core-beliefs.md) | approved | maybe | all agents "
            "| Before changing agent workflow docs. | Repository beliefs. |",
        ],
    )
    (tmp_path / "docs" / "design-docs" / "core-beliefs.md").write_text(
        "core beliefs\n",
        encoding="utf-8",
    )
    write_status_map_index(
        tmp_path,
        relative_path="docs/product-specs/index.md",
        index_kind="product-spec-status-map",
        rows=[
            "| [`market-data.md`](market-data.md) | implemented | yes | current implemented scope "
            "| Before changing market-data behavior. | Current implemented-scope entry. |",
        ],
    )
    (tmp_path / "docs" / "product-specs" / "market-data.md").write_text(
        "market data\n",
        encoding="utf-8",
    )

    issues = repo_check.collect_issues(tmp_path)

    assert (
        "docs/design-docs/index.md has invalid Canonical field for document core-beliefs.md: maybe"
        in issues
    )
