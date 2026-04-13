from quantcraft._repo_tools import parse_routing_index_entries
from tests.support import ROOT


def test_core_guardrail_and_routing_docs_exist() -> None:
    required_paths = [
        "README.md",
        "AGENTS.md",
        "ARCHITECTURE.md",
        "docs/DESIGN.md",
        "docs/PLANS.md",
        "docs/RELIABILITY.md",
        "docs/SECURITY.md",
        "docs/design-docs/index.md",
        "docs/design-docs/quantcraft-architecture.md",
        "docs/design-docs/architecture-governance.md",
        "docs/product-specs/index.md",
        "docs/product-specs/backtest-mvp.md",
        "docs/product-specs/research-ergonomics.md",
    ]

    for relative_path in required_paths:
        path = ROOT / relative_path
        assert path.exists(), f"missing {relative_path}"
        assert path.read_text(encoding="utf-8").strip(), f"{relative_path} is empty"


def test_design_docs_are_discoverable_from_routing_index() -> None:
    design_index = (ROOT / "docs/design-docs/index.md").read_text(encoding="utf-8")
    entries, duplicates = parse_routing_index_entries(design_index)
    indexed_targets = {entry["target"] for entry in entries}

    assert duplicates == []
    for path in sorted((ROOT / "docs/design-docs").glob("*.md")):
        if path.name == "index.md":
            continue
        assert path.name in indexed_targets

    assert not (ROOT / "docs/plans/2026-03-18-quantcraft-architecture-draft-ko.md").exists()


def test_product_specs_are_discoverable_from_routing_index() -> None:
    product_index = (ROOT / "docs/product-specs/index.md").read_text(encoding="utf-8")
    entries, duplicates = parse_routing_index_entries(product_index)
    entries_by_target = {entry["target"]: entry for entry in entries}

    assert duplicates == []
    assert entries_by_target["backtest-mvp.md"]["role"] == "Governing"
    assert entries_by_target["backtest-mvp.md"]["scope"] == "current implemented scope"
    assert entries_by_target["research-ergonomics.md"]["role"] == "Governing"
    assert entries_by_target["research-ergonomics.md"]["scope"] == "current implemented scope"


def test_architecture_doc_points_to_design_docs_not_plans() -> None:
    architecture = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")

    assert "docs/design-docs/" in architecture
    assert "docs/plans/2026-03-18-quantcraft-architecture-draft-ko.md" not in architecture


def test_agents_routes_to_governing_docs_and_repo_checks() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for reference in [
        "docs/product-specs/index.md",
        "docs/design-docs/index.md",
        "docs/RELIABILITY.md",
        "docs/SECURITY.md",
        "uv run poe verify",
        "uv run poe repo-check",
        "uv run poe verify-runtime",
    ]:
        assert reference in agents

    assert "Compound Engineering" in agents
    assert "Tier A domains are `trading` and `execution`" in agents
