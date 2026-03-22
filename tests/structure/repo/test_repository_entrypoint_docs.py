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
