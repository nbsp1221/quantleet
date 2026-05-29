import tomllib

from quantleet._repo_tools import collect_poe_task_contract_issues, poe_executor_type
from scripts import check_docs
from tests.support import ROOT

REQUIRED_POE_TASKS = [
    "lint",
    "format",
    "format-check",
    "dead-code",
    "dependency-check",
    "perf-check",
    "check-runtime",
    "typecheck",
    "test",
    "test-unit",
    "test-integration",
    "test-structure",
    "test-smoke",
    "test-live",
    "coverage",
    "coverage-diff",
    "coverage-baseline",
    "coverage-baseline-update",
    "coverage-gates",
    "mutation-trading",
    "build",
    "twine-check",
    "repo-check",
    "notebook-validate",
    "live-smoke",
    "check",
]


def write_minimal_repo_docs(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        (
            "# quantleet\n\n## Installation\n\n"
            "uv run poe check\n"
            "uv run poe perf-check\n"
            "uv run poe check-runtime\n"
            "Quantleet is research and software tooling, not financial advice. "
            "Backtest results do not guarantee future performance. "
            "Users are responsible for data quality, assumptions, execution risk, "
            "and trading decisions.\n"
        ),
        encoding="utf-8",
    )
    (tmp_path / "CONTRIBUTING.md").write_text(
        "uv sync\nuv run poe check\nuv run poe repo-check\ndocs/site\nAI-assisted\nhuman\n",
        encoding="utf-8",
    )
    (tmp_path / "SECURITY.md").write_text(
        (
            "Tier A domains are trading and execution.\n"
            "vulnerability secrets financial public issue 0.1.0b1\n"
        ),
        encoding="utf-8",
    )
    github_dir = tmp_path / ".github"
    github_dir.mkdir()
    (github_dir / "PULL_REQUEST_TEMPLATE.md").write_text(
        "Summary\nChange type\nDocs impact\nVerification\nAI-assisted\nhuman\n",
        encoding="utf-8",
    )
    (tmp_path / "AGENTS.md").write_text(
        (
            "docs/product-specs/index.md\n"
            "docs/design-docs/index.md\n"
            "docs/RELIABILITY.md\n"
            "docs/SECURITY.md\n"
            "uv run poe check\n"
            "uv run poe perf-check\n"
            "uv run poe check-runtime\n"
            "uv run poe coverage\n"
            "uv run poe coverage-diff\n"
            "uv run poe coverage-baseline\n"
            "uv run poe coverage-baseline-update\n"
            "uv run poe coverage-gates\n"
            "uv run poe test-live\n"
            "uv run poe repo-check\n"
            "repo-local harness commands\n"
            "uv run pytest -q\n"
            "uv run python scripts/repo_check.py\n"
            "uv run python scripts/notebook_validate.py\n"
            "uv run python scripts/live_smoke.py\n"
        ),
        encoding="utf-8",
    )
    (tmp_path / "ARCHITECTURE.md").write_text(
        "[architecture](docs/design-docs/quantleet-architecture.md)\n",
        encoding="utf-8",
    )

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    site_dir = docs_dir / "site"
    (site_dir / "getting-started").mkdir(parents=True)
    (site_dir / "guides").mkdir()
    (site_dir / "concepts").mkdir()
    (site_dir / "reference").mkdir()
    public_doc_text = (
        "Quantleet is research and software tooling, not financial advice. "
        "Backtest results do not guarantee future performance. "
        "Users are responsible for data quality, assumptions, execution risk, "
        "and trading decisions.\n"
    )
    for relative_path in [
        "index.md",
        "installation.md",
        "quickstart.md",
        "examples.md",
        "getting-started/index.md",
        "guides/backtesting.md",
        "guides/strategy-authoring.md",
        "guides/data-sources.md",
        "guides/orders-and-sizing.md",
        "guides/parameter-exploration.md",
        "concepts/beta-scope.md",
        "reference/public-api.md",
    ]:
        (site_dir / relative_path).write_text(public_doc_text, encoding="utf-8")
    (docs_dir / "DESIGN.md").write_text(
        (
            "# Design Pointers\n\n"
            "- [design-docs/index.md](design-docs/index.md)\n"
            "- [../ARCHITECTURE.md](../ARCHITECTURE.md)\n"
            "- [design-docs/quantleet-architecture.md]"
            "(design-docs/quantleet-architecture.md)\n"
            "- [design-docs/architecture-governance.md]"
            "(design-docs/architecture-governance.md)\n"
            "- [product-specs/](product-specs/)\n"
            "- [plans/](plans/)\n"
        ),
        encoding="utf-8",
    )
    (docs_dir / "PLANS.md").write_text(
        (
            "# Plan Pointers\n\n"
            "- [plans/](plans/)\n"
            "- [plans/trials/](plans/trials/)\n"
            "- [../AGENTS.md](../AGENTS.md)\n"
            "- [design-docs/](design-docs/)\n"
            "- Durable architecture or contract drafts do not belong in `docs/plans/`\n"
            "- [plans/2026-04-13-ce-workflow-migration-plan.md]"
            "(plans/2026-04-13-ce-workflow-migration-plan.md)\n"
            "- [plans/TEMPLATE.md](plans/TEMPLATE.md)\n"
            "- [plans/trials/TEMPLATE.md](plans/trials/TEMPLATE.md)\n"
        ),
        encoding="utf-8",
    )
    (docs_dir / "RELIABILITY.md").write_text(
        "uv run poe check\nuv run poe check-runtime\nuv build\n",
        encoding="utf-8",
    )
    (docs_dir / "SECURITY.md").write_text(
        "Tier A domains are trading and execution.\n",
        encoding="utf-8",
    )

    plans_dir = docs_dir / "plans"
    plans_dir.mkdir()
    (plans_dir / "TEMPLATE.md").write_text("plan template\n", encoding="utf-8")
    (plans_dir / "2026-04-13-ce-workflow-migration-plan.md").write_text(
        "migration plan\n",
        encoding="utf-8",
    )
    trials_dir = plans_dir / "trials"
    trials_dir.mkdir()
    (trials_dir / "TEMPLATE.md").write_text("trial template\n", encoding="utf-8")

    design_docs_dir = docs_dir / "design-docs"
    design_docs_dir.mkdir()
    (design_docs_dir / "index.md").write_text(
        (
            "# Design Doc Routing Index\n\n"
            "| Task Area | Document | Role | Scope | Read When |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| Repository workflow and operating norms | [`core-beliefs.md`](core-beliefs.md) "
            "| Governing | all agent work | Before changing repository workflow, "
            "harness docs, or operating norms. |\n"
            "| Cleanup and promotion defaults | [`golden-principles.md`](golden-principles.md) "
            "| Governing | repository cleanup and promotion work | Before promoting "
            "repeated review findings into docs or checks. |\n"
            "| Cleanup loops and doc upkeep | [`doc-gardening.md`](doc-gardening.md) "
            "| Governing | harness maintenance | Before changing cleanup loops, "
            "doc upkeep, or quality-tracking expectations. |\n"
            "| Architecture and bounded contexts | "
            "[`quantleet-architecture.md`](quantleet-architecture.md) | Governing "
            "| architecture and bounded-context work | Before changing top-level "
            "contexts, dependency rules, or package ownership. |\n"
            "| Governance for docs versus checks | "
            "[`architecture-governance.md`](architecture-governance.md) | Governing "
            "| harness governance and repo-check changes | Before promoting a "
            "repeated rule from docs into checks or changing system-of-record "
            "policy. |\n"
            "| Shared trading-kernel semantics planning | "
            "[`trading-kernel-contract-draft.md`](trading-kernel-contract-draft.md) "
            "| Draft | future trading-kernel planning | Only when evaluating future "
            "shared trading semantics; read the current implemented product specs "
            "first. |\n"
        ),
        encoding="utf-8",
    )
    (design_docs_dir / "core-beliefs.md").write_text("core beliefs\n", encoding="utf-8")
    (design_docs_dir / "golden-principles.md").write_text(
        "golden principles\n",
        encoding="utf-8",
    )
    (design_docs_dir / "doc-gardening.md").write_text("doc gardening\n", encoding="utf-8")
    (design_docs_dir / "quantleet-architecture.md").write_text(
        "quantleet architecture\n",
        encoding="utf-8",
    )
    (design_docs_dir / "architecture-governance.md").write_text(
        "architecture governance\n",
        encoding="utf-8",
    )
    (design_docs_dir / "trading-kernel-contract-draft.md").write_text(
        "draft trading contract\n",
        encoding="utf-8",
    )

    product_specs_dir = docs_dir / "product-specs"
    product_specs_dir.mkdir()
    (product_specs_dir / "index.md").write_text(
        (
            "# Product Spec Routing Index\n\n"
            "| Task Area | Document | Role | Scope | Read When |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| Existing market-data behavior | [`market-data.md`](market-data.md) "
            "| Governing | current implemented scope | Before changing the existing "
            "market-data codebase or its tests. |\n"
            "| Historical ingestion under `quantleet.data` | "
            "[`data-ingestion.md`](data-ingestion.md) | Governing | current "
            "implemented scope | Before changing the shipped historical ingestion "
            "surface for exchange, CSV, and dataframe-backed backtest workflows. |\n"
            "| Backtest baseline orientation | [`backtest.md`](backtest.md) | "
            "Pointer | current implemented baseline orientation | When scoping "
            "backtest expansion work from the shipped baseline; then read "
            "[`backtest-mvp.md`](backtest-mvp.md). |\n"
            "| Backtest MVP behavior | [`backtest-mvp.md`](backtest-mvp.md) | "
            "Governing | current implemented scope | Before changing the current "
            "backtest MVP behavior, tests, or documented baseline constraints. |\n"
            "| Research ergonomics surface | "
            "[`research-ergonomics.md`](research-ergonomics.md) | Governing | "
            "current implemented scope | Before changing strategy ergonomics, "
            "series contracts, indicators, result reporting, examples, or "
            "quickstart assets for the research layer. |\n"
            "| Explicit percentage-based order sizing | "
            "[`order-sizing.md`](order-sizing.md) | Governing | current "
            "implemented scope | Before changing the shipped `qty_percent` "
            "sizing behavior for strategy order entry and partial exit "
            "semantics; read the current backtest and research specs first. |\n"
            "| Paper-trading planning | [`paper-trading.md`](paper-trading.md) | "
            "Future-only | future planning only | Only when discussing simulated "
            "execution work beyond the current approved slices. |\n"
            "| Live-trading planning | [`live-trading.md`](live-trading.md) | "
            "Future-only | future planning only | Only when discussing Tier A "
            "live-trading scope with explicit human approval. |\n"
        ),
        encoding="utf-8",
    )
    (product_specs_dir / "market-data.md").write_text("market data\n", encoding="utf-8")
    (product_specs_dir / "data-ingestion.md").write_text("data ingestion\n", encoding="utf-8")
    (product_specs_dir / "backtest.md").write_text("backtest pointer\n", encoding="utf-8")
    (product_specs_dir / "backtest-mvp.md").write_text("backtest mvp\n", encoding="utf-8")
    (product_specs_dir / "research-ergonomics.md").write_text(
        "research ergonomics\n",
        encoding="utf-8",
    )
    (product_specs_dir / "order-sizing.md").write_text("order sizing\n", encoding="utf-8")
    (product_specs_dir / "paper-trading.md").write_text("paper trading\n", encoding="utf-8")
    (product_specs_dir / "live-trading.md").write_text("live trading\n", encoding="utf-8")


def test_repo_check_accepts_current_poe_task_contract() -> None:
    assert check_docs.collect_issues(ROOT) == []


def test_pyproject_defines_required_poe_tasks() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert poe_executor_type(pyproject) == "uv"

    task_names = pyproject["tool"]["poe"]["tasks"].keys()
    for task_name in REQUIRED_POE_TASKS:
        assert task_name in task_names
    assert "verify" not in task_names
    assert "verify-runtime" not in task_names
    assert "test-integration-extended" not in task_names


def test_poe_check_sequence_matches_default_local_quality_gate() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    check = pyproject["tool"]["poe"]["tasks"]["check"]

    assert check["sequence"] == [
        "format-check",
        "lint",
        "dead-code",
        "dependency-check",
        "typecheck",
        "coverage-gates",
        "build",
        "twine-check",
        "repo-check",
        "notebook-validate",
    ]


def test_mutation_trading_task_is_manual_and_scoped_to_trading() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    tasks = pyproject["tool"]["poe"]["tasks"]

    assert tasks["mutation-trading"]["sequence"] == [
        {"cmd": "mutmut run --max-children 4"},
        {"cmd": "mutmut results"},
    ]
    assert tasks["mutation-trading"]["help"] == (
        "Run targeted mutation testing for the trading kernel"
    )
    assert "mutation-trading" not in tasks["check"]["sequence"]


def test_mutmut_configuration_targets_trading_unit_tests() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    mutmut = pyproject["tool"]["mutmut"]

    assert mutmut["paths_to_mutate"] == ["src/quantleet/trading"]
    assert mutmut["pytest_add_cli_args_test_selection"] == ["tests/unit/trading"]
    assert mutmut["mutate_only_covered_lines"] is True


def test_default_test_tasks_use_plain_pytest_commands() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    tasks = pyproject["tool"]["poe"]["tasks"]

    assert tasks["test"]["cmd"] == "pytest -q"
    assert tasks["test-integration"]["cmd"] == "pytest tests/integration -q"


def test_dead_code_task_uses_vulture_pyproject_configuration() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    tasks = pyproject["tool"]["poe"]["tasks"]
    vulture = pyproject["tool"]["vulture"]

    assert tasks["dead-code"]["cmd"] == "vulture"
    assert vulture["paths"] == ["src", "tests", "scripts"]
    assert vulture["min_confidence"] == 80
    assert vulture["sort_by_size"] is True


def test_dependency_check_task_uses_deptry_pyproject_configuration() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    tasks = pyproject["tool"]["poe"]["tasks"]
    deptry = pyproject["tool"]["deptry"]

    assert tasks["dependency-check"]["cmd"] == "deptry src"
    assert deptry["known_first_party"] == ["quantleet"]
    assert deptry["ignore_notebooks"] is True
    assert deptry["package_module_name_map"] == {"ta-lib": "talib"}


def test_poe_task_surface_is_documented() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for command in [
        "uv run poe check",
        "uv run poe perf-check",
        "uv run poe check-runtime",
        "uv run poe coverage",
        "uv run poe coverage-diff",
        "uv run poe coverage-baseline",
        "uv run poe coverage-baseline-update",
        "uv run poe coverage-gates",
        "uv run poe dead-code",
        "uv run poe dependency-check",
        "uv run poe format",
        "uv run poe test-live",
    ]:
        assert command in agents
    assert "project.scripts" not in agents
    for command in [
        "uv run python scripts/repo_check.py",
        "uv run python scripts/notebook_validate.py",
        "uv run python scripts/live_smoke.py",
    ]:
        assert command in agents


def test_repo_check_flags_missing_required_poe_task(tmp_path) -> None:
    write_minimal_repo_docs(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "quantleet"
version = "0.1.0"

[dependency-groups]
dev = ["poethepoet>=0.42.1"]

[tool.poe]
executor = "uv"

[tool.poe.tasks]
lint = "ruff check ."
""".strip(),
        encoding="utf-8",
    )

    issues = check_docs.collect_issues(tmp_path)

    assert any("Missing required Poe task: check" in issue for issue in issues)


def test_repo_check_flags_forbidden_verify_aliases(tmp_path) -> None:
    write_minimal_repo_docs(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "quantleet"
version = "0.1.0"

[dependency-groups]
dev = ["poethepoet>=0.42.1"]

[tool.poe]
executor = "uv"

[tool.poe.tasks]
lint = "ruff check ."
format = "ruff format ."
format-check = "ruff format --check ."
dead-code = "vulture"
dependency-check = "deptry src"
perf-check = "pytest tests/perf -q"
check-runtime = ["check", "perf-check"]
typecheck = "mypy src"
test = "pytest -q"
test-unit = "pytest tests/unit -q"
test-integration = "pytest tests/integration -q"
test-structure = "pytest tests/structure -q"
test-smoke = "pytest tests/smoke -q"
test-live = "pytest tests/live -q"
coverage = "coverage run -m pytest -q"
coverage-diff = "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80"
coverage-baseline = { cmd = '''
uv run python scripts/coverage_baseline.py check
--baseline .coverage-baseline.json
--allowed-drop 0.25
--current-json coverage-baseline-current.json
''' }
coverage-baseline-update = { cmd = '''
uv run python scripts/coverage_baseline.py update
--baseline .coverage-baseline.json
--current-json coverage-baseline-current.json
''' }
coverage-gates = [
    "coverage erase",
    "coverage run -m pytest -q",
    "coverage report -m",
    "coverage xml -o coverage.xml --fail-under=0",
    "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80",
    "coverage-baseline",
]
build = "uv build"
twine-check = "uvx twine check --strict dist/*.whl dist/*.tar.gz"
repo-check = "uv run python scripts/repo_check.py"
notebook-validate = "uv run python scripts/notebook_validate.py"
live-smoke = "uv run python scripts/live_smoke.py"
check = [
    "format-check",
    "lint",
    "dead-code",
    "dependency-check",
    "typecheck",
    "coverage-gates",
    "build",
    "twine-check",
    "repo-check",
    "notebook-validate",
]
verify = ["check"]
verify-runtime = ["check-runtime"]
""".strip(),
        encoding="utf-8",
    )

    issues = check_docs.collect_issues(tmp_path)

    assert any("Forbidden Poe task alias: verify" in issue for issue in issues)
    assert any("Forbidden Poe task alias: verify-runtime" in issue for issue in issues)


def test_repo_check_flags_wrong_coverage_baseline_command() -> None:
    issues = collect_poe_task_contract_issues(
        {
            "coverage-baseline": {"cmd": "coverage baseline"},
            "coverage-baseline-update": {"cmd": "coverage baseline update"},
            "coverage-gates": [
                {"cmd": "coverage erase"},
                {"cmd": "coverage run -m pytest -q"},
                {
                    "cmd": (
                        "diff-cover coverage.xml --compare-branch HEAD "
                        "--include-untracked --fail-under 80"
                    ),
                },
                "coverage-baseline",
            ],
        },
    )

    assert "Poe task coverage-baseline does not match the approved command" in issues
    assert "Poe task coverage-baseline-update does not match the approved command" in issues


def test_repo_check_flags_invalid_coverage_gates_contract() -> None:
    valid_task_commands = {
        "coverage-baseline": {
            "cmd": (
                "uv run python scripts/coverage_baseline.py check "
                "--baseline .coverage-baseline.json "
                "--allowed-drop 0.25 "
                "--current-json coverage-baseline-current.json"
            ),
        },
        "coverage-baseline-update": {
            "cmd": (
                "uv run python scripts/coverage_baseline.py update "
                "--baseline .coverage-baseline.json "
                "--current-json coverage-baseline-current.json"
            ),
        },
    }

    issues = collect_poe_task_contract_issues(
        {
            **valid_task_commands,
            "coverage-gates": [
                {"cmd": "coverage erase"},
                {"cmd": "coverage run -m pytest -q"},
                {"cmd": "coverage run -m pytest -q"},
                "coverage-baseline",
            ],
        },
    )
    assert "Poe task coverage-gates must run pytest under coverage exactly once" in issues
    assert "Poe task coverage-gates is missing the changed-lines coverage gate" in issues

    issues = collect_poe_task_contract_issues(
        {
            **valid_task_commands,
            "coverage-gates": [
                {"cmd": "coverage erase"},
                {"cmd": "coverage run -m pytest -q"},
                {
                    "cmd": (
                        "diff-cover coverage.xml --compare-branch HEAD "
                        "--include-untracked --fail-under 80"
                    ),
                },
            ],
        },
    )
    assert "Poe task coverage-gates must end with coverage-baseline" in issues


def test_repo_check_accepts_table_form_poe_executor(tmp_path) -> None:
    write_minimal_repo_docs(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "quantleet"
version = "0.1.0"

[dependency-groups]
dev = ["poethepoet>=0.42.1"]

[tool.poe.executor]
type = "uv"

[tool.poe.tasks]
lint = "ruff check ."
format = "ruff format ."
format-check = "ruff format --check ."
dead-code = "vulture"
dependency-check = "deptry src"
perf-check = "pytest tests/perf -q"
check-runtime = ["check", "perf-check"]
typecheck = "mypy src"
test = "pytest -q"
test-unit = "pytest tests/unit -q"
test-integration = "pytest tests/integration -q"
test-structure = "pytest tests/structure -q"
test-smoke = "pytest tests/smoke/local -q"
test-live = "pytest tests/smoke/live -q"
coverage = [{ cmd = "coverage run -m pytest -q" }, { cmd = "coverage report -m" }]
coverage-diff = [
    { cmd = "coverage erase" },
    { cmd = "coverage run -m pytest -q" },
    { cmd = "coverage xml -o coverage.xml --fail-under=0" },
    { cmd = "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80" },
]
coverage-baseline = { cmd = '''
uv run python scripts/coverage_baseline.py check
--baseline .coverage-baseline.json
--allowed-drop 0.25
--current-json coverage-baseline-current.json
''' }
coverage-baseline-update = { cmd = '''
uv run python scripts/coverage_baseline.py update
--baseline .coverage-baseline.json
--current-json coverage-baseline-current.json
''' }
coverage-gates = [
    { cmd = "coverage erase" },
    { cmd = "coverage run -m pytest -q" },
    { cmd = "coverage report -m" },
    { cmd = "coverage xml -o coverage.xml --fail-under=0" },
    { cmd = "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80" },
    "coverage-baseline",
]
build = "uv build"
twine-check = "uvx twine check --strict dist/*.whl dist/*.tar.gz"
repo-check = "uv run python scripts/repo_check.py"
notebook-validate = "uv run python scripts/notebook_validate.py"
live-smoke = "uv run python scripts/live_smoke.py"
check = [
    "format-check",
    "lint",
    "dead-code",
    "dependency-check",
    "typecheck",
    "coverage-gates",
    "build",
    "twine-check",
    "repo-check",
    "notebook-validate",
]
""".strip(),
        encoding="utf-8",
    )

    assert check_docs.collect_issues(tmp_path) == []
