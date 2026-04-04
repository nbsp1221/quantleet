from __future__ import annotations

import tomllib

from tests.support import ROOT


def _pyproject() -> dict[str, object]:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_pyproject_defines_runtime_verification_task() -> None:
    tasks = _pyproject()["tool"]["poe"]["tasks"]

    assert "verify-runtime" in tasks
    verify_runtime = tasks["verify-runtime"]
    assert verify_runtime["sequence"] == ["verify", "perf-check"]


def test_runtime_verification_lane_is_documented_with_trigger_paths() -> None:
    reliability = (ROOT / "docs" / "RELIABILITY.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    developer_tasks = (ROOT / "docs" / "references" / "developer-tasks.md").read_text(
        encoding="utf-8"
    )
    tooling = (ROOT / "docs" / "references" / "tooling.md").read_text(encoding="utf-8")

    for content in [reliability, agents, developer_tasks, tooling]:
        assert "uv run poe verify-runtime" in content

    for path in [
        "src/quantcraft/research/_indicator_runtime.py",
        "src/quantcraft/research/_indicator_kernels.py",
        "src/quantcraft/research/ta.py",
        "src/quantcraft/research/application/backtest.py",
    ]:
        assert path in reliability or path in agents
        assert path not in developer_tasks
        assert path not in tooling
