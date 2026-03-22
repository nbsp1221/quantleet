from tests.support import ROOT


def test_tier_a_domains_are_named_in_reliability_and_security_docs() -> None:
    reliability = (ROOT / "docs/RELIABILITY.md").read_text(encoding="utf-8")
    security = (ROOT / "docs/SECURITY.md").read_text(encoding="utf-8")

    for domain in ["trading", "execution"]:
        assert domain in reliability
        assert domain in security


def test_product_specs_exist_for_major_financial_domains() -> None:
    for relative_path in [
        "docs/product-specs/market-data.md",
        "docs/product-specs/backtest.md",
        "docs/product-specs/paper-trading.md",
        "docs/product-specs/live-trading.md",
    ]:
        assert (ROOT / relative_path).exists(), f"missing {relative_path}"


def test_live_trading_spec_and_security_docs_require_human_gate() -> None:
    live_trading = (ROOT / "docs/product-specs/live-trading.md").read_text(encoding="utf-8")
    security = (ROOT / "docs/SECURITY.md").read_text(encoding="utf-8")

    assert "human approval" in live_trading.lower()
    assert "human approval" in security.lower()
