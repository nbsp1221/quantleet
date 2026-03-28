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


def test_readme_current_scope_mentions_implemented_backtest_research_and_data_surfaces() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    setup_start = readme.index("## Setup")
    pre_setup_section = readme[:setup_start]

    assert "Backtest MVP" in pre_setup_section
    assert "`quantcraft.research`" in pre_setup_section
    assert "`quantcraft.data`" in pre_setup_section
    for marker in ["`CCXTDataSource`", "`CSVDataSource`", "`DataFrameDataSource`"]:
        assert marker in pre_setup_section
    for marker in ["`Strategy`", "`run_backtest`", "`ta`", "`qc`"]:
        assert marker in pre_setup_section
    assert "automatic historical pagination" in pre_setup_section


def test_current_docs_describe_closed_trade_and_fill_count_summary_terms() -> None:
    research_spec = (ROOT / "docs" / "product-specs" / "research-ergonomics.md").read_text(
        encoding="utf-8"
    )
    backtest_spec = (ROOT / "docs" / "product-specs" / "backtest-mvp.md").read_text(
        encoding="utf-8"
    )
    quickstart = (ROOT / "docs" / "references" / "research-ergonomics-quickstart.md").read_text(
        encoding="utf-8"
    )

    assert "`total_trades` means closed trades" in research_spec
    assert "`total_fills` means the raw fill count" in research_spec
    assert "trade-count metrics should be interpreted as closed trades" in backtest_spec
    assert "`result.summary.total_trades` = closed trades" in quickstart
    assert "`sell()` while flat is treated as a no-op" in research_spec
    assert "a `sell` intent while flat is treated as an exit-only no-op" in backtest_spec
    assert "repeated `sell()` calls while flat are treated as exit-only no-ops" in quickstart
