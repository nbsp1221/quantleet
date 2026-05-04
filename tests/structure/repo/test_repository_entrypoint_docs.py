from tests.support import ROOT


def test_repository_entrypoint_docs_exist_and_are_not_empty() -> None:
    for relative_path in ["AGENTS.md", "ARCHITECTURE.md"]:
        path = ROOT / relative_path
        assert path.exists(), f"missing {relative_path}"
        assert path.read_text(encoding="utf-8").strip(), f"{relative_path} is empty"


def test_release_facing_repository_docs_exist_and_are_not_empty() -> None:
    for relative_path in [
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CHANGELOG.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
    ]:
        path = ROOT / relative_path
        assert path.exists(), f"missing {relative_path}"
        assert path.read_text(encoding="utf-8").strip(), f"{relative_path} is empty"


def test_release_facing_repository_docs_cover_public_beta_workflow() -> None:
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    pr_template = (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")

    for marker in [
        "uv sync",
        "uv run poe verify",
        "uv run poe repo-check",
        "docs/site",
        "AI-assisted",
        "human",
    ]:
        assert marker in contributing

    for marker in [
        "vulnerability",
        "secrets",
        "financial",
        "public issue",
        "0.1.0b1",
    ]:
        assert marker.lower() in security.lower()

    assert "## Unreleased" in changelog
    assert "## 0.1.0b1" in changelog

    for marker in [
        "Summary",
        "Change type",
        "Docs impact",
        "Verification",
        "Changelog",
        "AI-assisted",
        "human",
    ]:
        assert marker in pr_template


def test_readme_has_project_description_and_installation_section() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "quantcraft" in readme.lower()
    assert "## installation" in readme.lower()


def test_readme_presents_public_beta_docs_surface() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for marker in [
        "single-symbol",
        "Python 3.13",
        "from quantcraft.backtest import BacktestEngine, CostConfig",
        "from quantcraft.data import DataFrameDataSource",
        "from quantcraft.research import Strategy, qc, ta",
        "result.report",
        "result.plot()",
        "SMA crossover quickstart",
        "Orders and sizing",
        "Parameter exploration",
        "docs/site",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "MIT",
    ]:
        assert marker in readme

    for disclaimer_marker in [
        "not financial advice",
        "do not guarantee future performance",
        "data quality",
        "execution risk",
        "trading decisions",
    ]:
        assert disclaimer_marker in readme.lower()

    for forbidden in [
        "docs/plans",
        "docs/product-specs",
        "docs/design-docs",
        "docs/research",
        "from quantcraft import BacktestEngine",
        "from quantcraft.trading.domain.costs import CostConfig",
        "TimeInForce",
    ]:
        assert forbidden not in readme


def test_current_docs_describe_summary_terms_and_engine_surface() -> None:
    research_spec = (ROOT / "docs" / "product-specs" / "research-ergonomics.md").read_text(
        encoding="utf-8"
    )
    backtest_spec = (ROOT / "docs" / "product-specs" / "backtest-mvp.md").read_text(
        encoding="utf-8"
    )
    order_sizing_spec = (ROOT / "docs" / "product-specs" / "order-sizing.md").read_text(
        encoding="utf-8"
    )
    data_ingestion_spec = (ROOT / "docs" / "product-specs" / "data-ingestion.md").read_text(
        encoding="utf-8"
    )
    quickstart = (ROOT / "docs" / "references" / "research-ergonomics-quickstart.md").read_text(
        encoding="utf-8"
    )
    reliability = (ROOT / "docs" / "RELIABILITY.md").read_text(encoding="utf-8")

    assert "`total_trades` means closed trades" in research_spec
    assert "`total_fills` means the raw fill count" in research_spec
    assert "trade-count metrics should be interpreted as closed trades" in backtest_spec
    assert "`result.summary.total_trades` = closed trades" in quickstart
    assert "`sell()` while flat is treated as a no-op" in research_spec
    assert "`qty_percent`" in research_spec
    assert "a `sell` intent while flat is treated as an exit-only no-op" in backtest_spec
    assert "pending order request" in backtest_spec
    assert (
        "runtime\n  `OrderIntent` at activation" in backtest_spec
        or "runtime `OrderIntent`" in backtest_spec
    )
    assert "- Status: `implemented`" in order_sizing_spec
    assert "carry trigger facts for shipped `stop_market`" in order_sizing_spec
    assert "runtime `Order` remains quantity-based" in order_sizing_spec
    assert "repeated `sell()` calls while flat are treated as exit-only no-ops" in quickstart
    assert "`self.position`" in research_spec
    assert "`self.position.is_open`" in research_spec
    assert "`self.position.quantity`" in research_spec
    assert "`self.position.average_entry_price`" in research_spec
    assert "may\n  omit `symbol`" in research_spec or "may omit `symbol`" in research_spec
    assert "should match the active series symbol" in research_spec
    assert "self.position.is_open" in quickstart
    assert "may omit `symbol`" in quickstart
    assert "should still match the active series" in quickstart
    assert "`BacktestEngine`" in research_spec
    assert "`BacktestEngine(...).run(bars=..., strategy=...)`" in research_spec
    assert "`BacktestEngine(...).run(source=..., strategy=...)`" in research_spec
    assert "### Initial Canonical User Journeys" in research_spec
    for journey_marker in [
        "Clean Install To Public Imports",
        "DataFrame-Like Quickstart To First Backtest",
        "Materialized `BarSeries`",
        "Exchange-Backed Historical Research Flow",
    ]:
        assert journey_marker in research_spec
    assert "superficially passing but still bad" in research_spec
    assert "`BacktestEngine(...).run(bars=..., strategy=...)`" in backtest_spec
    assert "`BacktestEngine(...).run(source=..., strategy=...)`" in backtest_spec
    assert "`quantcraft.data.TimeBar`" in research_spec
    assert "`quantcraft.data.BarSeries`" in research_spec
    assert "`quantcraft.data.TimeBar`" in backtest_spec
    assert "`quantcraft.data.BarSeries`" in backtest_spec
    assert "`run_backtest(...)` remains available as a compatibility surface" not in research_spec
    assert "`run_backtest(...)` remains available as a compatibility surface" not in backtest_spec
    assert "source.load() returns `BarSeries`" in data_ingestion_spec
    assert "`CCXTDataSource.load()` returns `BarSeries`" in data_ingestion_spec
    assert "`CSVDataSource.load()` returns `BarSeries`" in data_ingestion_spec
    assert "`DataFrameDataSource.load()` returns `BarSeries`" in data_ingestion_spec
    assert "`BarSeries.rows` is `tuple[TimeBar, ...]`" in data_ingestion_spec
    assert '`BarSeries.bar_type` is fixed to `"time"`' in data_ingestion_spec
    assert 'self.buy(quantity=1, tag="rsi-entry")' in data_ingestion_spec
    assert 'self.sell(quantity=1, tag="rsi-exit")' in data_ingestion_spec
    assert "from quantcraft.backtest import BacktestEngine" in quickstart
    assert "from quantcraft.research import ParameterStudy, Strategy, ta, qc" in quickstart
    assert (
        "from quantcraft.research import BacktestEngine, Strategy, ta, qc, run_backtest"
        not in quickstart
    )
    assert "from quantcraft.data import BarSeries, DataFrameDataSource, TimeBar" in quickstart
    assert "run(bars=" in quickstart
    assert "run(source=" in quickstart
    assert "canonical strategy pair" in reliability
    assert "RSI 30/70 mean reversion" in reliability
    assert "EMA crossover" in reliability
    assert "BTC-fixture-backed `qty_percent`" in reliability
    assert "test-integration-extended" not in reliability
