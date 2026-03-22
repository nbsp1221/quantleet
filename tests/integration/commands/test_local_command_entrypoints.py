from tests.support import ROOT


def test_local_command_wrappers_exist() -> None:
    for relative_path in [
        "scripts/repo_check.py",
        "scripts/notebook_validate.py",
        "scripts/live_smoke.py",
        ]:
        assert (ROOT / relative_path).exists(), f"missing {relative_path}"


def test_pyproject_does_not_expose_repository_entrypoints_as_package_scripts() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert "[project.scripts]" not in pyproject


def test_agents_doc_references_repo_local_harness_commands() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for command in [
        "uv run python scripts/repo_check.py",
        "uv run python scripts/notebook_validate.py",
        "uv run python scripts/live_smoke.py",
    ]:
        assert command in agents
