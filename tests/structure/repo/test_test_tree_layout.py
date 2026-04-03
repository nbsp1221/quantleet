from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_top_level_test_taxonomy_directories_exist() -> None:
    for relative_path in [
        "tests/unit",
        "tests/integration",
        "tests/perf",
        "tests/structure",
        "tests/smoke",
    ]:
        assert (ROOT / relative_path).is_dir(), f"missing directory: {relative_path}"
