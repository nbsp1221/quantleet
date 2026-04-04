import tomllib

from tests.support import ROOT


def test_pyproject_defines_required_poe_tasks() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    poe_tasks = pyproject["tool"]["poe"]["tasks"]

    for task_name in [
        "lint",
        "format",
        "perf-check",
        "verify-runtime",
        "typecheck",
        "test",
        "test-unit",
        "test-integration",
        "test-structure",
        "test-smoke",
        "test-live",
        "coverage",
        "build",
        "repo-check",
        "notebook-validate",
        "live-smoke",
        "verify",
    ]:
        assert task_name in poe_tasks


def test_agenda_docs_reference_poe_task_layer_and_keep_entrypoints() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "uv run poe verify" in readme
    assert "uv run poe verify-runtime" in readme
    assert "uv run poe coverage" in readme
    assert "uv run poe format" in readme
    assert "repo-local harness commands" in agents
    assert "uv run poe coverage" in agents
    assert "uv run poe verify" in agents
    assert "uv run poe verify-runtime" in agents
