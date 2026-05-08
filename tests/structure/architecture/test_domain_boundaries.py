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


def test_strategy_is_a_tier_b_domain() -> None:
    assert "strategy" not in check_architecture.TIER_A


def test_research_dependency_into_backtest_is_permitted() -> None:
    assert check_architecture.validate_domain_dependency("research", "backtest") is None


def test_shared_strategy_dependency_edges_are_permitted() -> None:
    assert check_architecture.validate_domain_dependency("strategy", "trading") is None
    assert check_architecture.validate_domain_dependency("research", "strategy") is None
    assert check_architecture.validate_domain_dependency("backtest", "strategy") is None
    assert check_architecture.validate_domain_dependency("execution", "strategy") is None


def test_strategy_dependency_into_runtime_contexts_is_rejected() -> None:
    assert check_architecture.validate_domain_dependency("strategy", "research") is not None
    assert check_architecture.validate_domain_dependency("strategy", "backtest") is not None
    assert check_architecture.validate_domain_dependency("strategy", "execution") is not None
    assert check_architecture.validate_domain_dependency("strategy", "integrations") is not None


def test_execution_dependency_into_integrations_is_permitted() -> None:
    assert check_architecture.validate_domain_dependency("execution", "integrations") is None


def test_repository_scan_rejects_research_into_execution_even_with_data_allowed(
    tmp_path: Path,
) -> None:
    src_root = tmp_path / "src" / "quantleet"
    research_root = src_root / "research"
    execution_root = src_root / "execution"
    research_root.mkdir(parents=True)
    execution_root.mkdir(parents=True)

    (research_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantleet.execution import runtime\n",
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
    src_root = tmp_path / "src" / "quantleet"
    trading_root = src_root / "trading"
    trading_root.mkdir(parents=True)

    (src_root / "telemetry.py").write_text("from __future__ import annotations\n", encoding="utf-8")
    (src_root / "validation.py").write_text(
        "from __future__ import annotations\n",
        encoding="utf-8",
    )
    (trading_root / "__init__.py").write_text(
        "from __future__ import annotations\n"
        "from quantleet.telemetry import emit_metric\n"
        "from quantleet.validation import validate_order\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == [
        f"{trading_root / '__init__.py'}: "
        "Root-level module dependency violation: trading cannot depend on quantleet.telemetry",
        f"{trading_root / '__init__.py'}: "
        "Root-level module dependency violation: trading cannot depend on quantleet.validation",
    ]


def test_repository_scan_allows_execution_into_integrations_and_integrations_into_shared(
    tmp_path: Path,
) -> None:
    src_root = tmp_path / "src" / "quantleet"
    execution_root = src_root / "execution"
    integrations_root = src_root / "integrations"
    shared_root = src_root / "_shared"
    execution_root.mkdir(parents=True)
    integrations_root.mkdir(parents=True)
    shared_root.mkdir(parents=True)

    (execution_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantleet.integrations import broker\n",
        encoding="utf-8",
    )
    (integrations_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantleet._shared import mapper\n",
        encoding="utf-8",
    )
    (shared_root / "__init__.py").write_text(
        "from __future__ import annotations\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == []


def test_repository_scan_allows_data_into_integrations(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "quantleet"
    data_root = src_root / "data"
    integrations_root = src_root / "integrations"
    data_root.mkdir(parents=True)
    integrations_root.mkdir(parents=True)

    (data_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantleet.integrations import vendor\n",
        encoding="utf-8",
    )
    (integrations_root / "__init__.py").write_text(
        "from __future__ import annotations\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == []


def test_repository_scan_rejects_research_into_integrations(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "quantleet"
    research_root = src_root / "research"
    integrations_root = src_root / "integrations"
    research_root.mkdir(parents=True)
    integrations_root.mkdir(parents=True)

    (research_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantleet.integrations import binance\n",
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
    src_root = tmp_path / "src" / "quantleet"
    trading_root = src_root / "trading"
    trading_root.mkdir(parents=True)

    (src_root / "exchange.py").write_text("from __future__ import annotations\n", encoding="utf-8")
    (trading_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantleet.exchange import Exchange\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == [
        f"{trading_root / '__init__.py'}: "
        "Root-level module dependency violation: trading cannot depend on quantleet.exchange"
    ]


def test_repository_scan_rejects_removed_root_level_allowlist_edges(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "quantleet"
    src_root.mkdir(parents=True)

    (src_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantleet.exchange import Exchange\n",
        encoding="utf-8",
    )
    (src_root / "_repo_tools.py").write_text(
        "from __future__ import annotations\nfrom quantleet.exchange import Exchange\n",
        encoding="utf-8",
    )
    (src_root / "exchange.py").write_text("from __future__ import annotations\n", encoding="utf-8")

    assert check_architecture.collect_issues(tmp_path) == [
        f"{src_root / '__init__.py'}: "
        "Root-level module dependency violation: quantleet cannot depend on quantleet.exchange",
        f"{src_root / '_repo_tools.py'}: "
        "Root-level module dependency violation: "
        "quantleet._repo_tools cannot depend on quantleet.exchange",
    ]


def test_repository_scan_rejects_forbidden_initializer_imports(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "quantleet"
    trading_root = src_root / "trading"
    research_root = src_root / "research"
    trading_root.mkdir(parents=True)
    research_root.mkdir(parents=True)

    (trading_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantleet.research import domain\n",
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
    src_root = tmp_path / "src" / "quantleet"
    trading_root = src_root / "trading"
    research_root = src_root / "research"
    trading_root.mkdir(parents=True)
    research_root.mkdir(parents=True)

    (trading_root / "__init__.py").write_text(
        "from __future__ import annotations\nfrom quantleet import research\n",
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
    src_root = tmp_path / "src" / "quantleet"
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
