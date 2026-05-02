from __future__ import annotations

from tests.support import ROOT


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_parameter_exploration_docs_route_to_research_public_path() -> None:
    product_spec = _read("docs/product-specs/parameter-exploration.md")

    assert "from quantcraft.research import ParameterStudy, Strategy, ta" in product_spec
    assert "ParameterStudy(...).grid_search(...)" in product_spec


def test_public_docs_do_not_promote_deferred_beta_controls() -> None:
    docs = "\n".join(
        (
            _read("README.md"),
            _read("docs/product-specs/research-ergonomics.md"),
            _read("docs/references/research-ergonomics-quickstart.md"),
        )
    )

    forbidden_fragments = (
        "ParameterStudy(source=",
        "grid_search(source=",
        "n_jobs=",
        "workers=",
        "parallel=",
        "executor=",
        "GridSearchResult.heatmap",
        "resume=",
    )
    for fragment in forbidden_fragments:
        assert fragment not in docs


def test_docs_keep_grid_results_as_research_diagnostics_not_recommendations() -> None:
    product_spec = _read("docs/product-specs/parameter-exploration.md")
    normalized_spec = " ".join(product_spec.split())

    assert "research diagnostics, not trading recommendations" in normalized_spec
