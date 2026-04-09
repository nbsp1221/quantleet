from tests.support import ROOT


def test_system_of_record_docs_exist() -> None:
    required_paths = [
        "docs/DESIGN.md",
        "docs/PLANS.md",
        "docs/QUALITY_SCORE.md",
        "docs/RELIABILITY.md",
        "docs/SECURITY.md",
        "docs/feedback-promotion-log.md",
        "docs/design-docs/index.md",
        "docs/design-docs/core-beliefs.md",
        "docs/design-docs/golden-principles.md",
        "docs/design-docs/doc-gardening.md",
        "docs/exec-plans/active/index.md",
        "docs/exec-plans/completed/index.md",
        "docs/exec-plans/tech-debt-tracker.md",
        "docs/product-specs/index.md",
        "docs/references/index.md",
        "docs/generated/index.md",
    ]

    for relative_path in required_paths:
        path = ROOT / relative_path
        assert path.exists(), f"missing {relative_path}"
        assert path.read_text(encoding="utf-8").strip(), f"{relative_path} is empty"


def test_current_korean_design_drafts_are_indexed_and_not_misfiled() -> None:
    design_index = (ROOT / "docs/design-docs/index.md").read_text(encoding="utf-8")

    for path in sorted((ROOT / "docs/design-docs").glob("*.md")):
        if path.name == "index.md":
            continue
        assert path.name in design_index

    assert not (ROOT / "docs/plans/2026-03-18-quantcraft-architecture-draft-ko.md").exists()


def test_architecture_doc_points_to_design_docs_not_plans() -> None:
    architecture = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")

    assert "docs/design-docs/" in architecture
    assert "docs/plans/2026-03-18-quantcraft-architecture-draft-ko.md" not in architecture


def test_feedback_promotion_loop_docs_are_discoverable_from_operating_docs() -> None:
    core_beliefs = (ROOT / "docs/design-docs/core-beliefs.md").read_text(encoding="utf-8")
    doc_gardening = (ROOT / "docs/design-docs/doc-gardening.md").read_text(encoding="utf-8")
    quality_score = (ROOT / "docs/QUALITY_SCORE.md").read_text(encoding="utf-8")

    assert "golden-principles.md" in core_beliefs
    assert "feedback-promotion-log.md" in core_beliefs
    assert "golden-principles.md" in doc_gardening
    assert "feedback-promotion-log.md" in doc_gardening
    assert "checks" in doc_gardening.lower()
    assert "docs/feedback-promotion-log.md" in quality_score


def test_governance_and_reliability_docs_define_evaluation_taxonomy() -> None:
    governance = (ROOT / "docs/design-docs/architecture-governance.md").read_text(encoding="utf-8")
    reliability = (ROOT / "docs/RELIABILITY.md").read_text(encoding="utf-8")
    quality_score = (ROOT / "docs/QUALITY_SCORE.md").read_text(encoding="utf-8")

    assert "## Evaluation Taxonomy" in governance
    assert "`mechanical checks`" in governance
    assert "`LLM-assisted critique`" in governance
    assert "`human judgment`" in governance
    assert "## Promotion Ladder" in governance
    for concept in [
        "critique",
        "documented policy",
        "repeated manual use",
        "narrow mechanical enforcement",
    ]:
        assert concept in governance
    assert "## Evaluation Modes" in reliability
    assert "`mechanical checks`" in reliability
    assert "`LLM-assisted critique`" in reliability
    assert "`human judgment`" in reliability
    assert "architecture-governance.md" in reliability
    for concept in [
        "repository-health artifact",
        "user-value meter",
        "approval score",
    ]:
        assert concept in quality_score


def test_metric_admission_rule_is_documented_in_governance_and_promotion_loop() -> None:
    governance = (ROOT / "docs/design-docs/architecture-governance.md").read_text(encoding="utf-8")
    doc_gardening = (ROOT / "docs/design-docs/doc-gardening.md").read_text(encoding="utf-8")
    feedback_log = (ROOT / "docs/feedback-promotion-log.md").read_text(encoding="utf-8")

    assert "## Metric And Check Admission Rule" in governance
    assert "the protected behavior" in governance
    assert "the measured proxy" in governance
    assert "the likely gaming vector" in governance
    assert "the decision the artifact is expected to change" in governance
    assert "the revalidation or removal condition" in governance
    for concept in [
        "protected behavior",
        "measured proxy",
        "likely gaming vector",
        "revalidation or removal condition",
    ]:
        assert concept in doc_gardening
    assert "2026-04-02" in feedback_log
    assert "Proxy metrics and evaluator outputs could become fake rigor" in feedback_log


def test_agents_and_belief_docs_define_findings_first_reviewer_contract() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    core_beliefs = (ROOT / "docs/design-docs/core-beliefs.md").read_text(encoding="utf-8")
    golden_principles = (ROOT / "docs/design-docs/golden-principles.md").read_text(encoding="utf-8")

    for concept in ["evaluator/reviewer agents", "approval", "architecture-governance.md"]:
        assert concept in agents
    for concept in ["architecture-governance.md", "evaluator agents", "failure modes"]:
        assert concept in core_beliefs
    for concept in ["architecture-governance.md", "reviewer output", "failure mode"]:
        assert concept in golden_principles
