from __future__ import annotations

from pathlib import Path

from scripts import check_architecture
from tests.support import ROOT


def test_strategy_package_is_shared_capability_root() -> None:
    assert (ROOT / "src/quantleet/strategy/__init__.py").exists()


def test_repository_scan_rejects_strategy_importing_research_backtest_or_execution(
    tmp_path: Path,
) -> None:
    src_root = tmp_path / "src" / "quantleet"
    strategy_root = src_root / "strategy"
    research_root = src_root / "research"
    backtest_root = src_root / "backtest"
    execution_root = src_root / "execution"
    integrations_root = src_root / "integrations"
    for path in (strategy_root, research_root, backtest_root, execution_root, integrations_root):
        path.mkdir(parents=True)
        (path / "__init__.py").write_text("from __future__ import annotations\n", encoding="utf-8")

    (strategy_root / "bad_imports.py").write_text(
        "from __future__ import annotations\n"
        "from quantleet.research import Strategy\n"
        "from quantleet.backtest import BacktestEngine\n"
        "from quantleet.execution import runtime\n"
        "from quantleet.integrations import venues\n",
        encoding="utf-8",
    )

    issues = check_architecture.collect_issues(tmp_path)

    assert set(issues) == {
        f"{strategy_root / 'bad_imports.py'}: "
        "Cross-domain dependency violation: strategy cannot depend on backtest",
        f"{strategy_root / 'bad_imports.py'}: "
        "Tier A boundary violation: strategy cannot depend on execution",
        f"{strategy_root / 'bad_imports.py'}: "
        "Cross-domain dependency violation: strategy cannot depend on integrations",
        f"{strategy_root / 'bad_imports.py'}: "
        "Cross-domain dependency violation: strategy cannot depend on research",
    }


def test_repository_scan_allows_strategy_as_shared_runtime_surface(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "quantleet"
    strategy_root = src_root / "strategy"
    trading_root = src_root / "trading"
    research_root = src_root / "research"
    backtest_root = src_root / "backtest"
    execution_root = src_root / "execution"
    for path in (strategy_root, trading_root, research_root, backtest_root, execution_root):
        path.mkdir(parents=True)
        (path / "__init__.py").write_text("from __future__ import annotations\n", encoding="utf-8")

    (strategy_root / "strategy.py").write_text(
        "from __future__ import annotations\nfrom quantleet.trading import order_requests\n",
        encoding="utf-8",
    )
    (research_root / "strategy_use.py").write_text(
        "from __future__ import annotations\nfrom quantleet.strategy import Strategy\n",
        encoding="utf-8",
    )
    (backtest_root / "strategy_use.py").write_text(
        "from __future__ import annotations\nfrom quantleet.strategy import Strategy\n",
        encoding="utf-8",
    )
    (execution_root / "strategy_use.py").write_text(
        "from __future__ import annotations\nfrom quantleet.strategy import Strategy\n",
        encoding="utf-8",
    )

    assert check_architecture.collect_issues(tmp_path) == []
