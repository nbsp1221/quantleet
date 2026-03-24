from tests.support import ROOT


def test_repository_entrypoint_docs_exist_and_are_not_empty() -> None:
    for relative_path in ["AGENTS.md", "ARCHITECTURE.md"]:
        path = ROOT / relative_path
        assert path.exists(), f"missing {relative_path}"
        assert path.read_text(encoding="utf-8").strip(), f"{relative_path} is empty"


def test_readme_has_project_description_and_setup_section() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "quantcraft" in readme.lower()
    assert "## setup" in readme.lower()


def test_readme_current_scope_mentions_implemented_backtest_and_research_surfaces() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    setup_start = readme.index("## Setup")
    pre_setup_section = readme[:setup_start]

    assert "Backtest MVP" in pre_setup_section
    assert "`quantcraft.research`" in pre_setup_section
    for marker in ["`Strategy`", "`run_backtest`", "`ta`", "`qc`"]:
        assert marker in pre_setup_section
