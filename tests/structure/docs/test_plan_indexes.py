from tests.support import ROOT


def test_plan_index_links_historical_and_new_exec_plan_locations() -> None:
    plans_doc = (ROOT / "docs/PLANS.md").read_text(encoding="utf-8")

    assert "docs/plans/" in plans_doc
    assert "docs/exec-plans/active/" in plans_doc
    assert "docs/exec-plans/completed/" in plans_doc
    assert "Durable architecture or contract drafts do not belong in `docs/plans/`" in plans_doc


def test_exec_plan_indexes_exist_and_reference_transition() -> None:
    active_index = (ROOT / "docs/exec-plans/active/index.md").read_text(encoding="utf-8")
    completed_index = (ROOT / "docs/exec-plans/completed/index.md").read_text(encoding="utf-8")

    assert "docs/plans/" in active_index
    assert "docs/plans/" in completed_index


def test_plan_index_lists_all_current_historical_plan_files() -> None:
    plans_doc = (ROOT / "docs/PLANS.md").read_text(encoding="utf-8")

    for path in sorted((ROOT / "docs/plans").glob("*.md")):
        relative_path = path.relative_to(ROOT).as_posix()
        assert relative_path in plans_doc
