from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

from tests.support import ROOT


def test_backtest_plotting_does_not_depend_on_reporting_or_outer_capabilities() -> None:
    imports = _imports(ROOT / "src" / "quantcraft" / "backtest" / "plotting.py")

    assert "quantcraft.backtest.reporting" not in imports
    assert "quantcraft.research" not in imports
    assert "quantcraft.execution" not in imports
    assert "quantcraft.integrations" not in imports


def test_backtest_plotting_is_not_promoted_as_a_public_module_api() -> None:
    init_path = ROOT / "src" / "quantcraft" / "backtest" / "__init__.py"
    init_imports = _imports(init_path)
    init_source = init_path.read_text(encoding="utf-8")

    assert "quantcraft.backtest.plotting" not in init_imports
    assert '"plot_backtest_result"' not in init_source


def test_importing_backtest_result_surface_does_not_import_matplotlib() -> None:
    command = (
        "import quantcraft.backtest, quantcraft.backtest.results, sys; "
        "assert 'matplotlib' not in sys.modules"
    )

    subprocess.run([sys.executable, "-c", command], cwd=ROOT, check=True)


def test_importing_plotting_module_does_not_import_matplotlib() -> None:
    command = "import quantcraft.backtest.plotting, sys; assert 'matplotlib' not in sys.modules"

    subprocess.run([sys.executable, "-c", command], cwd=ROOT, check=True)


def test_backtest_plotting_runtime_imports_do_not_depend_on_results_or_reporting() -> None:
    imports = _runtime_imports(ROOT / "src" / "quantcraft" / "backtest" / "plotting.py")

    assert "quantcraft.backtest.results" not in imports
    assert "quantcraft.backtest.reporting" not in imports


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)

    return imports


def _runtime_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    runtime_nodes = [
        node
        for node in tree.body
        if not (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Name)
            and node.test.id == "TYPE_CHECKING"
        )
    ]
    imports: set[str] = set()

    for node in ast.walk(ast.Module(body=runtime_nodes, type_ignores=[])):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)

    return imports
