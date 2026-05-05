from pathlib import Path

from tests.support import ROOT

REQUIRED_PUBLIC_DOCS = [
    "docs/site/index.md",
    "docs/site/installation.md",
    "docs/site/quickstart.md",
    "docs/site/examples.md",
    "docs/site/getting-started/index.md",
    "docs/site/guides/backtesting.md",
    "docs/site/guides/strategy-authoring.md",
    "docs/site/guides/data-sources.md",
    "docs/site/guides/orders-and-sizing.md",
    "docs/site/guides/parameter-exploration.md",
    "docs/site/concepts/beta-scope.md",
    "docs/site/reference/public-api.md",
]

FORBIDDEN_INTERNAL_PUBLIC_LINKS = (
    "AGENTS.md",
    "docs/plans",
    "docs/product-specs",
    "docs/design-docs",
    "docs/research",
    "../plans",
    "../product-specs",
    "../design-docs",
    "../research",
)


def test_public_beta_docs_exist_under_site_boundary() -> None:
    for relative_path in REQUIRED_PUBLIC_DOCS:
        path = ROOT / relative_path
        assert path.exists(), f"missing {relative_path}"
        assert path.read_text(encoding="utf-8").strip(), f"{relative_path} is empty"


def test_public_docs_do_not_link_to_internal_workflow_docs() -> None:
    for path in _public_doc_paths():
        content = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_INTERNAL_PUBLIC_LINKS:
            assert forbidden not in content, f"{path.relative_to(ROOT)} exposes {forbidden}"


def test_public_docs_include_required_financial_disclaimer() -> None:
    for relative_path in ["docs/site/index.md", "docs/site/quickstart.md"]:
        content = (ROOT / relative_path).read_text(encoding="utf-8").lower()
        for marker in [
            "not financial advice",
            "do not guarantee future performance",
            "data quality",
            "assumptions",
            "execution risk",
            "trading decisions",
        ]:
            assert marker in content


def test_public_docs_list_exactly_three_canonical_examples() -> None:
    examples = (ROOT / "docs/site/examples.md").read_text(encoding="utf-8")

    assert examples.count("## Example ") == 3
    for marker in [
        "## Example 1: SMA Crossover Quickstart",
        "## Example 2: Orders And Sizing",
        "## Example 3: Parameter Exploration",
    ]:
        assert marker in examples

    assert "## Example 4" not in examples
    assert "Reporting And Plotting" not in examples


def test_public_docs_describe_unsupported_beta_scope_as_unsupported() -> None:
    beta_scope = (ROOT / "docs/site/concepts/beta-scope.md").read_text(encoding="utf-8").lower()

    for unsupported in [
        "live trading",
        "paper trading",
        "shorting",
        "leverage",
        "multi-symbol",
        "multi-timeframe",
    ]:
        assert unsupported in beta_scope
    assert "unsupported" in beta_scope


def test_public_api_reference_uses_current_public_imports_only() -> None:
    reference = (ROOT / "docs/site/reference/public-api.md").read_text(encoding="utf-8")

    for marker in [
        "quantleet.data.TimeBar",
        "quantleet.data.BarSeries",
        "quantleet.data.DataFrameDataSource",
        "quantleet.data.CSVDataSource",
        "quantleet.data.CCXTDataSource",
        "quantleet.backtest.BacktestEngine",
        "quantleet.backtest.CostConfig",
        "quantleet.backtest.BacktestResult",
        "BacktestResult.report",
        "BacktestResult.plot()",
        "quantleet.research.Strategy",
        "Strategy.buy(...)",
        "Strategy.sell(...)",
        "quantleet.research.ParameterStudy",
        "ParameterStudy.grid_search(...)",
        "quantleet.research.ta",
        "quantleet.research.qc",
    ]:
        assert marker in reference

    for forbidden in [
        "TimeInForce",
        "from quantleet import BacktestEngine",
        "quantleet.Bar",
        "quantleet.trading.domain",
    ]:
        assert forbidden not in reference


def test_public_quickstart_uses_no_live_exchange_or_hidden_files() -> None:
    quickstart = (ROOT / "docs/site/quickstart.md").read_text(encoding="utf-8")

    assert "DataFrameDataSource" in quickstart
    for forbidden in ["CCXTDataSource(", "apiKey", "secret", "read_csv(", "open("]:
        assert forbidden not in quickstart


def _public_doc_paths() -> list[Path]:
    return sorted((ROOT / "docs/site").rglob("*.md"))
