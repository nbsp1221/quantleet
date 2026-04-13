from tests.support import ROOT


def test_plan_index_links_active_plan_locations() -> None:
    plans_doc = (ROOT / "docs/PLANS.md").read_text(encoding="utf-8")

    assert "plans/" in plans_doc
    assert "plans/trials/" in plans_doc
    assert "Durable architecture or contract drafts do not belong in `docs/plans/`" in plans_doc


def test_plan_index_points_to_migration_plan_and_trial_template() -> None:
    plans_doc = (ROOT / "docs/PLANS.md").read_text(encoding="utf-8")

    assert "2026-04-13-ce-workflow-migration-plan.md" in plans_doc
    assert "plans/trials/TEMPLATE.md" in plans_doc
