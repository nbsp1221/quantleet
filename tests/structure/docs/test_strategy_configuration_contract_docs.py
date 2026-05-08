from __future__ import annotations

from tests.support import ROOT


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_product_index_routes_strategy_configuration_and_wfa_prerequisites() -> None:
    index = _read("docs/product-specs/index.md")

    assert "strategy-configuration-contract.md" in index
    assert "strategy-configuration-contract-test-scenarios.md" in index
    assert "walk-forward-analysis-readiness.md" in index
    assert "wfa-prerequisite-roadmap.md" in index
    assert "WFA implementation is paused" in index


def test_strategy_configuration_contract_keeps_stage_boundaries_explicit() -> None:
    spec = _read("docs/product-specs/strategy-configuration-contract.md")

    assert "The chosen package path is `quantleet.strategy`." in spec
    assert "from quantleet.strategy import Strategy, StrategyConfig" in spec
    assert "`Strategy[Config]` is the canonical user-facing declaration" in spec
    assert "Stage 1 does not have to migrate `ParameterStudy`" in spec
    assert "replace report-facing `strategy_parameters` with `strategy_config`" in spec
    assert "WFA remains paused" in spec


def test_strategy_configuration_test_spec_targets_observable_contracts() -> None:
    test_spec = _read("docs/product-specs/strategy-configuration-contract-test-scenarios.md")

    assert "`Strategy` and `StrategyConfig` are canonically imported from" in test_spec
    assert "`quantleet.strategy`" in test_spec
    assert "Tests must validate these contracts as user-visible behavior" in test_spec
    normalized = " ".join(test_spec.split())
    assert "not private helper names or generic-introspection internals" in normalized
    assert "tests/unit/strategy/test_strategy_config_contract.py" in test_spec
