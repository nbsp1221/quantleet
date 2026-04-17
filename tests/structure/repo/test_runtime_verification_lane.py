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
    assert (
        verify_runtime["help"]
        == "Run the stronger explicit verification lane for runtime-sensitive "
        "backtest or research changes"
    )


def test_runtime_verification_lane_is_documented_with_trigger_paths() -> None:
    reliability = (ROOT / "docs" / "RELIABILITY.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for content in [reliability, agents]:
        assert "uv run poe verify-runtime" in content
        assert "runtime-sensitive backtest or research" in content

    for path in [
        "src/quantcraft/backtest/engine.py",
        "src/quantcraft/backtest/runtime.py",
        "src/quantcraft/backtest/execution_model.py",
        "src/quantcraft/backtest/order_activation.py",
        "src/quantcraft/backtest/strategy_runtime.py",
        "src/quantcraft/research/ta.py",
        "src/quantcraft/research/strategy.py",
        "src/quantcraft/research/indicators/runtime/",
        "src/quantcraft/research/indicators/pure/",
    ]:
        assert path in reliability or path in agents
