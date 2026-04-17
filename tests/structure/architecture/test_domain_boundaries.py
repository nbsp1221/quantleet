from pathlib import Path

from scripts import check_architecture  # noqa: E402
from tests.support import ROOT


def test_tier_a_domains_are_defined() -> None:
    assert check_architecture.TIER_A == {"trading", "execution"}


def test_forbidden_crossing_into_tier_a_is_rejected() -> None:
    issue = check_architecture.validate_domain_dependency("data", "execution")

    assert issue is not None
    assert "Tier A" in issue


def test_allowed_dependency_into_trading_kernel_is_permitted() -> None:
    assert check_architecture.validate_domain_dependency("research", "trading") is None
    assert check_architecture.validate_domain_dependency("backtest", "trading") is None
    assert check_architecture.validate_domain_dependency("execution", "trading") is None
    assert check_architecture.validate_domain_dependency("integrations", "trading") is None


def test_allowed_research_dependency_into_data_is_permitted() -> None:
    assert check_architecture.validate_domain_dependency("research", "data") is None
    assert check_architecture.validate_domain_dependency("execution", "data") is None
    assert check_architecture.validate_domain_dependency("integrations", "data") is None


def test_data_dependency_into_integrations_is_permitted() -> None:
    assert check_architecture.validate_domain_dependency("data", "integrations") is None


def test_backtest_is_a_tier_b_domain() -> None:
    assert "backtest" not in check_architecture.TIER_A


def test_research_dependency_into_backtest_is_permitted() -> None:
    assert check_architecture.validate_domain_dependency("research", "backtest") is None


def test_execution_dependency_into_integrations_is_permitted() -> None:
    assert check_architecture.validate_domain_dependency("execution", "integrations") is None


def test_repository_scan_rejects_research_into_execution_even_with_data_allowed(
    tmp_path: Path,
) -> None:
    src_root = tmp_path / "src" / "quantcraft"
    research_root = src_root / "research"
    execution_root = src_root / "execution"
    research_root.mkdir(parents=True)
    execution_root.mkdir(parents=True)

    (research_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantcraft.execution import runtime\n",
        encoding="utf-8",
    )
    (execution_root / "__init__.py").write_text(
        "from __future__ import annotations\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == [
        f"{research_root / '__init__.py'}: "
        "Tier A boundary violation: research cannot depend on execution"
    ]


def test_shared_modules_are_allowed_from_any_domain() -> None:
    assert check_architecture.validate_domain_dependency("data", "_shared") is None


def test_repository_scan_rejects_removed_shared_domain_aliases(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "quantcraft"
    trading_root = src_root / "trading"
    trading_root.mkdir(parents=True)

    (src_root / "telemetry.py").write_text("from __future__ import annotations\n", encoding="utf-8")
    (src_root / "validation.py").write_text(
        "from __future__ import annotations\n",
        encoding="utf-8",
    )
    (trading_root / "__init__.py").write_text(
        "from __future__ import annotations\n"
        "from quantcraft.telemetry import emit_metric\n"
        "from quantcraft.validation import validate_order\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == [
        f"{trading_root / '__init__.py'}: "
        "Root-level module dependency violation: trading cannot depend on quantcraft.telemetry",
        f"{trading_root / '__init__.py'}: "
        "Root-level module dependency violation: trading cannot depend on quantcraft.validation",
    ]


def test_repository_scan_allows_execution_into_integrations_and_integrations_into_shared(
    tmp_path: Path,
) -> None:
    src_root = tmp_path / "src" / "quantcraft"
    execution_root = src_root / "execution"
    integrations_root = src_root / "integrations"
    shared_root = src_root / "_shared"
    execution_root.mkdir(parents=True)
    integrations_root.mkdir(parents=True)
    shared_root.mkdir(parents=True)

    (execution_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantcraft.integrations import broker\n",
        encoding="utf-8",
    )
    (integrations_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantcraft._shared import mapper\n",
        encoding="utf-8",
    )
    (shared_root / "__init__.py").write_text(
        "from __future__ import annotations\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == []


def test_repository_scan_allows_data_into_integrations(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "quantcraft"
    data_root = src_root / "data"
    integrations_root = src_root / "integrations"
    data_root.mkdir(parents=True)
    integrations_root.mkdir(parents=True)

    (data_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantcraft.integrations import vendor\n",
        encoding="utf-8",
    )
    (integrations_root / "__init__.py").write_text(
        "from __future__ import annotations\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == []


def test_repository_scan_rejects_research_into_integrations(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "quantcraft"
    research_root = src_root / "research"
    integrations_root = src_root / "integrations"
    research_root.mkdir(parents=True)
    integrations_root.mkdir(parents=True)

    (research_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantcraft.integrations import binance\n",
        encoding="utf-8",
    )
    (integrations_root / "__init__.py").write_text(
        "from __future__ import annotations\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == [
        f"{research_root / '__init__.py'}: "
        "Cross-domain dependency violation: research cannot depend on integrations"
    ]


def test_repository_scan_allows_current_capability_first_codebase() -> None:
    assert check_architecture.collect_issues(ROOT) == []


def test_repository_scan_rejects_root_level_non_domain_module_imports(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "quantcraft"
    trading_root = src_root / "trading"
    trading_root.mkdir(parents=True)

    (src_root / "exchange.py").write_text("from __future__ import annotations\n", encoding="utf-8")
    (trading_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantcraft.exchange import Exchange\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == [
        f"{trading_root / '__init__.py'}: "
        "Root-level module dependency violation: trading cannot depend on quantcraft.exchange"
    ]


def test_repository_scan_rejects_removed_root_level_allowlist_edges(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "quantcraft"
    src_root.mkdir(parents=True)

    (src_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantcraft.exchange import Exchange\n",
        encoding="utf-8",
    )
    (src_root / "_repo_tools.py").write_text(
        "from __future__ import annotations\nfrom quantcraft.exchange import Exchange\n",
        encoding="utf-8",
    )
    (src_root / "exchange.py").write_text("from __future__ import annotations\n", encoding="utf-8")

    assert check_architecture.collect_issues(tmp_path) == [
        f"{src_root / '__init__.py'}: "
        "Root-level module dependency violation: quantcraft cannot depend on quantcraft.exchange",
        f"{src_root / '_repo_tools.py'}: "
        "Root-level module dependency violation: "
        "quantcraft._repo_tools cannot depend on quantcraft.exchange",
    ]


def test_repository_scan_rejects_forbidden_initializer_imports(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "quantcraft"
    trading_root = src_root / "trading"
    research_root = src_root / "research"
    trading_root.mkdir(parents=True)
    research_root.mkdir(parents=True)

    (trading_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantcraft.research import domain\n",
        encoding="utf-8",
    )
    (research_root / "__init__.py").write_text(
        "from __future__ import annotations\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == [
        f"{trading_root / '__init__.py'}: "
        "Cross-domain dependency violation: trading cannot depend on research"
    ]


def test_repository_scan_rejects_absolute_package_alias_imports(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "quantcraft"
    trading_root = src_root / "trading"
    research_root = src_root / "research"
    trading_root.mkdir(parents=True)
    research_root.mkdir(parents=True)

    (trading_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantcraft import research\n",
        encoding="utf-8",
    )
    (research_root / "__init__.py").write_text(
        "from __future__ import annotations\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == [
        f"{trading_root / '__init__.py'}: "
        "Cross-domain dependency violation: trading cannot depend on research"
    ]


def test_repository_scan_rejects_relative_cross_domain_imports(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "quantcraft"
    trading_root = src_root / "trading"
    research_root = src_root / "research"
    trading_root.mkdir(parents=True)
    research_root.mkdir(parents=True)

    (trading_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom ..research import domain\n",
        encoding="utf-8",
    )
    (research_root / "__init__.py").write_text(
        "from __future__ import annotations\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == [
        f"{trading_root / '__init__.py'}: "
        "Cross-domain dependency violation: trading cannot depend on research"
    ]
