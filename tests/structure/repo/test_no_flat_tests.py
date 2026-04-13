from pathlib import Path

from scripts import check_docs
from tests.structure.repo.test_poe_task_contracts import write_minimal_repo_docs
from tests.support import ROOT


def test_repository_has_no_flat_test_modules() -> None:
    flat_test_files = sorted(path.name for path in ROOT.glob("tests/test_*.py"))
    assert flat_test_files == []


def test_doc_checks_flag_new_flat_root_test_files(tmp_path: Path) -> None:
    write_minimal_repo_docs(tmp_path)

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_flat_example.py").write_text("def test_example(): pass\n", encoding="utf-8")

    issues = check_docs.collect_issues(tmp_path)

    assert any("flat root-level test file" in issue.lower() for issue in issues)
