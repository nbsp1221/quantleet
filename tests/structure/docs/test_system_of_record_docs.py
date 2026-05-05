from quantleet._repo_tools import parse_routing_index_entries
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
        "docs/design-docs/quantleet-architecture.md",
        "docs/design-docs/architecture-governance.md",
        "docs/product-specs/index.md",
        "docs/product-specs/backtest-mvp.md",
        "docs/product-specs/research-ergonomics.md",
        "docs/product-specs/order-sizing.md",
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

    assert not (ROOT / "docs/plans/2026-03-18-quantleet-architecture-draft-ko.md").exists()


def test_product_specs_are_discoverable_from_routing_index() -> None:
    product_index = (ROOT / "docs/product-specs/index.md").read_text(encoding="utf-8")
    entries, duplicates = parse_routing_index_entries(product_index)
    entries_by_target = {entry["target"]: entry for entry in entries}

    assert duplicates == []
    assert entries_by_target["backtest-mvp.md"]["role"] == "Governing"
    assert entries_by_target["backtest-mvp.md"]["scope"] == "current implemented scope"
    assert entries_by_target["research-ergonomics.md"]["role"] == "Governing"
    assert entries_by_target["research-ergonomics.md"]["scope"] == "current implemented scope"
    assert entries_by_target["order-sizing.md"]["role"] == "Governing"
    assert entries_by_target["order-sizing.md"]["scope"] == "current implemented scope"


def test_architecture_doc_points_to_design_docs_not_plans() -> None:
    architecture = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")

    assert "docs/design-docs/" in architecture
    assert "docs/plans/2026-03-18-quantleet-architecture-draft-ko.md" not in architecture


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


def test_current_order_and_kernel_doc_routing_prefers_english_canonical_paths() -> None:
    design_index = (ROOT / "docs/design-docs/index.md").read_text(encoding="utf-8")
    backtest_mvp = (ROOT / "docs/product-specs/backtest-mvp.md").read_text(encoding="utf-8")
    architecture_governance = (ROOT / "docs/design-docs/architecture-governance.md").read_text(
        encoding="utf-8"
    )
    research_index = (ROOT / "docs/research/index.md").read_text(encoding="utf-8")

    assert "[`order-runtime-model-design.md`](order-runtime-model-design.md)" in design_index
    assert (
        "| Runtime Order object model and responsibility | "
        "[`order-runtime-model-design.md`](order-runtime-model-design.md) |"
    ) in design_index
    assert "order-runtime-model-design-ko.md" not in design_index
    assert "[`trading-kernel-contract-draft.md`](trading-kernel-contract-draft.md)" in design_index
    assert (
        "| Shared trading-kernel semantics planning | "
        "[`trading-kernel-contract-draft.md`](trading-kernel-contract-draft.md) |"
    ) in design_index
    assert "trading-kernel-contract-draft-ko.md" not in design_index
    assert (
        "[`2026-04-20-order-runtime-model-comparison.md`]"
        "(2026-04-20-order-runtime-model-comparison.md)"
    ) in research_index
    assert "2026-04-20-order-runtime-model-comparison-ko.md" not in research_index
    assert "../design-docs/trading-kernel-contract-draft.md" in backtest_mvp
    assert (
        "[trading-kernel-contract-draft.md](trading-kernel-contract-draft.md)"
    ) in architecture_governance


def test_legacy_ko_doc_paths_are_removed() -> None:
    compatibility_paths = [
        ROOT / "docs/design-docs/order-runtime-model-design-ko.md",
        ROOT / "docs/design-docs/trading-kernel-contract-draft-ko.md",
        ROOT / "docs/research/2026-04-20-order-runtime-model-comparison-ko.md",
    ]

    for path in compatibility_paths:
        assert not path.exists()


def test_completed_archives_keep_historical_ko_filename_references() -> None:
    archive_paths = [
        ROOT / "docs/exec-plans/completed/2026-03-21-backtest-mvp-implementation.md",
        ROOT / "docs/exec-plans/completed/2026-03-22-harness-quality-improvement.md",
        ROOT / "docs/exec-plans/completed/2026-03-24-research-ergonomics-implementation.md",
    ]

    for path in archive_paths:
        contents = path.read_text(encoding="utf-8")
        assert "trading-kernel-contract-draft-ko.md" in contents
        assert "trading-kernel-contract-draft.md" not in contents
