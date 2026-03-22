from pathlib import Path

from scripts import check_docs
from tests.support import ROOT


def test_repository_has_no_flat_test_modules() -> None:
    flat_test_files = sorted(path.name for path in ROOT.glob("tests/test_*.py"))
    assert flat_test_files == []


def test_doc_checks_flag_new_flat_root_test_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# quantcraft\n\n## Setup\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    (tmp_path / "ARCHITECTURE.md").write_text("architecture", encoding="utf-8")
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    for relative_path in [
        "DESIGN.md",
        "PLANS.md",
        "QUALITY_SCORE.md",
        "RELIABILITY.md",
        "SECURITY.md",
    ]:
        (docs_dir / relative_path).write_text("ok", encoding="utf-8")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_flat_example.py").write_text("def test_example(): pass\n", encoding="utf-8")

    issues = check_docs.collect_issues(tmp_path)

    assert any("flat root-level test file" in issue.lower() for issue in issues)
