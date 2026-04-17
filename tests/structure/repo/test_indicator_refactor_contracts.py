from __future__ import annotations

from quantcraft.research import ta
from quantcraft.research.series import SeriesView
from tests.support import ROOT


def test_indicator_refactor_source_layout_exists() -> None:
    expected_paths = [
        ROOT / "src/quantcraft/research/indicators/__init__.py",
        ROOT / "src/quantcraft/research/indicators/pure/__init__.py",
        ROOT / "src/quantcraft/research/indicators/pure/sma.py",
        ROOT / "src/quantcraft/research/indicators/pure/ema.py",
        ROOT / "src/quantcraft/research/indicators/pure/rsi.py",
        ROOT / "src/quantcraft/research/indicators/pure/atr.py",
        ROOT / "src/quantcraft/research/indicators/pure/cci.py",
        ROOT / "src/quantcraft/research/indicators/pure/bb.py",
        ROOT / "src/quantcraft/research/indicators/pure/macd.py",
        ROOT / "src/quantcraft/research/indicators/runtime/__init__.py",
        ROOT / "src/quantcraft/research/indicators/runtime/base.py",
        ROOT / "src/quantcraft/research/indicators/runtime/views.py",
        ROOT / "src/quantcraft/research/indicators/runtime/runtime.py",
        ROOT / "src/quantcraft/research/indicators/runtime/factory.py",
    ]

    for path in expected_paths:
        assert path.exists(), f"missing required indicator refactor path: {path}"


def test_indicator_refactor_test_layout_exists() -> None:
    expected_paths = [
        ROOT / "tests/unit/research/test_indicator_surface.py",
        ROOT / "tests/unit/research/indicators/pure/test_sma.py",
        ROOT / "tests/unit/research/indicators/pure/test_ema.py",
        ROOT / "tests/unit/research/indicators/pure/test_rsi.py",
        ROOT / "tests/unit/research/indicators/pure/test_atr.py",
        ROOT / "tests/unit/research/indicators/pure/test_cci.py",
        ROOT / "tests/unit/research/indicators/pure/test_bb.py",
        ROOT / "tests/unit/research/indicators/pure/test_macd.py",
        ROOT / "tests/unit/research/indicators/runtime/test_runtime.py",
        ROOT / "tests/unit/research/indicators/runtime/test_views.py",
        ROOT / "tests/unit/research/indicators/runtime/test_factory.py",
    ]

    for path in expected_paths:
        assert path.exists(), f"missing required indicator refactor test: {path}"


def test_legacy_indicator_paths_are_absent() -> None:
    legacy_paths = [
        ROOT / "src/quantcraft/research/_indicator_kernels.py",
        ROOT / "src/quantcraft/research/_indicator_runtime.py",
        ROOT / "tests/unit/research/test_indicator_runtime.py",
    ]

    for path in legacy_paths:
        assert not path.exists(), f"legacy indicator path must be removed: {path}"


def test_current_repository_state_has_no_old_bollinger_naming() -> None:
    search_roots = [
        ROOT / "src",
        ROOT / "tests/unit",
        ROOT / "tests/integration",
        ROOT / "docs/product-specs",
        ROOT / "docs/references",
        ROOT / "docs/research",
        ROOT / "docs/RELIABILITY.md",
        ROOT / "README.md",
        ROOT / "AGENTS.md",
    ]

    for root in search_roots:
        if root.is_file():
            contents = root.read_text(encoding="utf-8")
            assert "bollinger_bands" not in contents
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix in {".png", ".jpg", ".jpeg", ".ipynb", ".pyc"}:
                continue
            try:
                contents = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            assert "bollinger_bands" not in contents, f"legacy naming remained in {path}"


def test_indicator_layers_have_no_latest_only_talib_helpers() -> None:
    search_roots = [
        ROOT / "src/quantcraft/research/indicators/pure",
        ROOT / "src/quantcraft/research/ta.py",
    ]

    forbidden_patterns = (
        "def latest_",
        "talib.stream",
        "pure_latest_",
    )

    for root in search_roots:
        if root.is_file():
            contents = root.read_text(encoding="utf-8")
            for pattern in forbidden_patterns:
                assert pattern not in contents, (
                    f"found forbidden latest-only helper pattern {pattern!r} in {root}"
                )
            continue

        for path in root.rglob("*.py"):
            contents = path.read_text(encoding="utf-8")
            for pattern in forbidden_patterns:
                assert pattern not in contents, (
                    f"found forbidden latest-only helper pattern {pattern!r} in {path}"
                )


def test_product_spec_documents_ta_bb_as_canonical_name() -> None:
    spec = (ROOT / "docs/product-specs/research-ergonomics.md").read_text(encoding="utf-8")

    assert "`ta.bb(series, length=20, stddev=2)`" in spec
    assert "`ta.bollinger_bands(series, length=20, stddev=2)`" not in spec


def test_public_ta_bb_contract_is_present_and_alias_absent() -> None:
    bands = ta.bb(SeriesView((1.0, 2.0, 3.0, 4.0, 5.0)), length=3, stddev=2)

    assert hasattr(ta, "bb")
    assert not hasattr(ta, "bollinger_bands")
    assert hasattr(bands, "upper")
    assert hasattr(bands, "middle")
    assert hasattr(bands, "lower")
    assert bands.middle[0] == 4.0
