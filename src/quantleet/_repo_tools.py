from __future__ import annotations

import ast
import re
import subprocess
import tomllib
from pathlib import Path
from typing import cast

REQUIRED_DOCS = (
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "docs/DESIGN.md",
    "docs/PLANS.md",
    "docs/RELIABILITY.md",
    "docs/SECURITY.md",
    "docs/design-docs/index.md",
    "docs/product-specs/index.md",
)

REQUIRED_PUBLIC_DOCS = (
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
)
FORBIDDEN_PUBLIC_DOC_LINKS = (
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
FINANCIAL_DISCLAIMER_MARKERS = (
    "not financial advice",
    "do not guarantee future performance",
    "data quality",
    "assumptions",
    "execution risk",
    "trading decisions",
)
PLACEHOLDER_TOKENS = ("Add your description here",)
SUPPORTED_TEST_DIRS = ("unit", "integration", "structure", "smoke")

TIER_A = {"trading", "execution"}
TIER_B = {"data", "research", "backtest", "strategy"}
TIER_C = {"ml"}
INTEGRATION_DOMAINS = {"integrations"}
SHARED_DOMAINS = {"_shared"}
KNOWN_DOMAINS = TIER_A | TIER_B | TIER_C | INTEGRATION_DOMAINS | SHARED_DOMAINS
ALLOWED_CROSS_DOMAIN_DEPENDENCIES = {
    ("backtest", "data"),
    ("backtest", "trading"),
    ("data", "integrations"),
    ("execution", "data"),
    ("execution", "integrations"),
    ("research", "data"),
    ("research", "trading"),
    ("research", "backtest"),
    ("research", "strategy"),
    ("backtest", "strategy"),
    ("execution", "trading"),
    ("execution", "strategy"),
    ("integrations", "data"),
    ("integrations", "trading"),
    ("strategy", "trading"),
}
ALLOWED_ROOT_MODULE_DEPENDENCIES: set[tuple[str, str]] = set()

ROUTING_INDEX_COLUMNS = ("Task Area", "Document", "Role", "Scope", "Read When")
ROUTING_INDEX_REQUIRED_FIELDS = ("task_area", "role", "scope", "read_when")
ROUTING_INDEX_CONFIG = {
    "docs/design-docs/index.md": {
        "directory": "docs/design-docs",
        "label": "design doc",
        "allowed_roles": {"Governing", "Draft"},
    },
    "docs/product-specs/index.md": {
        "directory": "docs/product-specs",
        "label": "product spec",
        "allowed_roles": {"Governing", "Pointer", "Future-only"},
    },
}
REQUIRED_POE_TASKS = (
    "lint",
    "format",
    "format-check",
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
    "build",
    "twine-check",
    "repo-check",
    "notebook-validate",
    "live-smoke",
    "check",
)
FORBIDDEN_POE_TASKS = (
    "verify",
    "verify-runtime",
)
EXPECTED_COVERAGE_BASELINE_CMD = (
    "uv run python scripts/coverage_baseline.py check "
    "--baseline .coverage-baseline.json "
    "--allowed-drop 0.25 "
    "--current-json coverage-baseline-current.json"
)
EXPECTED_COVERAGE_BASELINE_UPDATE_CMD = (
    "uv run python scripts/coverage_baseline.py update "
    "--baseline .coverage-baseline.json "
    "--current-json coverage-baseline-current.json"
)
EXPECTED_DIFF_COVER_CMD = (
    "diff-cover coverage.xml --compare-branch HEAD --include-untracked --fail-under 80"
)


def git_has_head(root: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def git_untracked_paths(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return set()
    return {line for line in result.stdout.splitlines() if line}


def referenced_repo_paths(content: str) -> set[str]:
    pattern = re.compile(
        r"(docs/[^\s`)\]]+|notebooks/[^\s`)\]]+|tests/[^\s`)\]]+|src/[^\s`)\]]+|scripts/[^\s`)\]]+|AGENTS\.md|ARCHITECTURE\.md|README\.md|agent-development-guide-ko\.md|pyproject\.toml)"
    )
    return {match.group(1) for match in pattern.finditer(content)}


def missing_markdown_link_targets(doc_path: Path) -> list[str]:
    content = doc_path.read_text(encoding="utf-8")
    pattern = re.compile(r"\[[^\]]+\]\(([^)#]+)\)")
    missing: list[str] = []

    for match in pattern.finditer(content):
        target = match.group(1).strip()
        if not target or "://" in target:
            continue
        resolved = (doc_path.parent / target).resolve()
        if not resolved.exists():
            missing.append(target)

    return missing


def poe_executor_type(pyproject: dict[str, object]) -> str | None:
    tool_config = pyproject.get("tool")
    if not isinstance(tool_config, dict):
        return None

    poe_config = tool_config.get("poe")
    if not isinstance(poe_config, dict):
        return None

    executor = poe_config.get("executor")
    if isinstance(executor, str):
        return executor
    if isinstance(executor, dict):
        executor_type = executor.get("type")
        return executor_type if isinstance(executor_type, str) else None

    return None


def normalize_command(command: str) -> str:
    return " ".join(command.split())


def poe_task_command(task: object) -> str | None:
    if isinstance(task, str):
        return normalize_command(task)
    if isinstance(task, dict):
        command = task.get("cmd")
        if isinstance(command, str):
            return normalize_command(command)
    return None


def poe_task_sequence(task: object) -> list[str]:
    if isinstance(task, list):
        sequence = task
    elif isinstance(task, dict):
        raw_sequence = task.get("sequence")
        sequence = raw_sequence if isinstance(raw_sequence, list) else []
    else:
        sequence = []

    commands: list[str] = []
    for item in sequence:
        if isinstance(item, str):
            commands.append(normalize_command(item))
        elif isinstance(item, dict):
            command = item.get("cmd")
            if isinstance(command, str):
                commands.append(normalize_command(command))
    return commands


def collect_poe_task_contract_issues(poe_tasks: object) -> list[str]:
    if not isinstance(poe_tasks, dict):
        return ["pyproject.toml is missing Poe task configuration"]

    issues: list[str] = []
    coverage_baseline = poe_task_command(poe_tasks.get("coverage-baseline"))
    if coverage_baseline != EXPECTED_COVERAGE_BASELINE_CMD:
        issues.append("Poe task coverage-baseline does not match the approved command")

    coverage_baseline_update = poe_task_command(poe_tasks.get("coverage-baseline-update"))
    if coverage_baseline_update != EXPECTED_COVERAGE_BASELINE_UPDATE_CMD:
        issues.append("Poe task coverage-baseline-update does not match the approved command")

    coverage_gates = poe_task_sequence(poe_tasks.get("coverage-gates"))
    if coverage_gates.count("coverage run -m pytest -q") != 1:
        issues.append("Poe task coverage-gates must run pytest under coverage exactly once")
    if EXPECTED_DIFF_COVER_CMD not in coverage_gates:
        issues.append("Poe task coverage-gates is missing the changed-lines coverage gate")
    if coverage_gates[-1:] != ["coverage-baseline"]:
        issues.append("Poe task coverage-gates must end with coverage-baseline")

    return issues


def markdown_section(content: str, title: str) -> str | None:
    pattern = re.compile(
        rf"^## {re.escape(title)}\s*$\n(?P<body>.*?)(?=^##\s+\S|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(content)
    if match is None:
        return None
    return match.group("body").strip()


def parse_bullet_metadata_section(section: str | None) -> dict[str, str]:
    if section is None:
        return {}
    metadata: dict[str, str] = {}
    for line in section.splitlines():
        match = re.match(r"^\s*[-*]\s*([a-z_]+):\s*(.+?)\s*$", line)
        if match is None:
            continue
        key, value = match.groups()
        metadata[key] = value.strip()

    return metadata


def parse_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def find_markdown_table_lines(content: str, header_columns: tuple[str, ...]) -> list[str]:
    lines = [line.strip() for line in content.splitlines()]
    for index, line in enumerate(lines):
        if tuple(parse_markdown_row(line)) != header_columns:
            continue

        table_lines = [line]
        cursor = index + 1
        while cursor < len(lines):
            candidate = lines[cursor]
            if not candidate.startswith("|"):
                break
            table_lines.append(candidate)
            cursor += 1
        return table_lines

    return []


def parse_routing_index_entries(
    content: str,
    *,
    allowed_roles: set[str] | None = None,
) -> tuple[list[dict[str, str]], list[str]]:
    table_lines = find_markdown_table_lines(content, ROUTING_INDEX_COLUMNS)
    if len(table_lines) >= 2:
        entries: list[dict[str, str]] = []
        duplicates: list[str] = []
        seen_targets: set[str] = set()
        for line in table_lines[2:]:
            cells = parse_markdown_row(line)
            if len(cells) != len(ROUTING_INDEX_COLUMNS):
                continue
            task_area, target_cell, role, scope, read_when = cells
            match = re.search(r"\(([^)#]+\.md)\)", target_cell)
            if match is None:
                stripped = target_cell.strip().strip("`")
                if stripped.endswith(".md"):
                    target = stripped
                else:
                    continue
            else:
                target = match.group(1).strip()
            if target in seen_targets:
                duplicates.append(target)
                continue
            seen_targets.add(target)
            entries.append(
                {
                    "task_area": task_area.strip(),
                    "target": target,
                    "role": role.strip(),
                    "scope": scope.strip(),
                    "read_when": read_when.strip(),
                    "schema": "routing_index",
                }
            )
        return entries, duplicates

    return [], []


def resolve_routing_index_target(root: Path, *, index_path: Path, target: str) -> str | None:
    relative_base = index_path.parent.relative_to(root)
    relative_path = (relative_base / target).as_posix()
    if relative_path.startswith("../"):
        return None
    return relative_path


def collect_doc_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for relative_path in REQUIRED_DOCS:
        path = root / relative_path
        if not path.exists():
            issues.append(f"Missing required document: {relative_path}")
            continue

        content = path.read_text(encoding="utf-8").strip()
        if not content:
            issues.append(f"Required document is empty: {relative_path}")
            continue

        for token in PLACEHOLDER_TOKENS:
            if token in content:
                issues.append(f"Found placeholder content in {relative_path}: {token}")

    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    if "## Setup" not in readme and "## Installation" not in readme:
        issues.append("README.md is missing the setup or installation section")
    if "uv run poe" not in readme:
        issues.append("README.md is missing uv run poe guidance")
    for marker in FINANCIAL_DISCLAIMER_MARKERS:
        if marker not in readme.lower():
            issues.append(f"README.md is missing financial disclaimer marker: {marker}")

    for relative_path in REQUIRED_PUBLIC_DOCS:
        path = root / relative_path
        if not path.exists():
            issues.append(f"Missing public documentation page: {relative_path}")
            continue

        content = path.read_text(encoding="utf-8")
        if not content.strip():
            issues.append(f"Public documentation page is empty: {relative_path}")
            continue

        for forbidden in FORBIDDEN_PUBLIC_DOC_LINKS:
            if forbidden in content:
                issues.append(
                    f"{relative_path} exposes internal workflow document reference: {forbidden}"
                )

    for relative_path in ("docs/site/index.md", "docs/site/quickstart.md"):
        path = root / relative_path
        content = path.read_text(encoding="utf-8").lower() if path.exists() else ""
        for marker in FINANCIAL_DISCLAIMER_MARKERS:
            if marker not in content:
                issues.append(f"{relative_path} is missing financial disclaimer marker: {marker}")

    plans_doc_path = root / "docs/PLANS.md"
    plans_doc = plans_doc_path.read_text(encoding="utf-8") if plans_doc_path.exists() else ""
    required_plan_references = ("plans/", "plans/trials/")
    for required_reference in required_plan_references:
        if required_reference not in plans_doc:
            issues.append(f"docs/PLANS.md is missing plan reference: {required_reference}")
    if "Durable architecture or contract drafts do not belong in `docs/plans/`" not in plans_doc:
        issues.append("docs/PLANS.md is missing design-docs versus plans guidance")

    agents_path = root / "AGENTS.md"
    agents = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    if "uv run poe" not in agents:
        issues.append("AGENTS.md is missing uv run poe guidance")
    if "repo-local harness commands" not in agents:
        issues.append("AGENTS.md is missing repo-local harness command guidance")

    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.exists():
        issues.append("Missing pyproject.toml for Poe task checks")
    else:
        pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        dev_dependencies = pyproject.get("dependency-groups", {}).get("dev", [])
        if not any(dependency.startswith("poethepoet") for dependency in dev_dependencies):
            issues.append("pyproject.toml is missing poethepoet in dependency-groups.dev")

        executor_type = poe_executor_type(pyproject)
        if executor_type != "uv":
            issues.append('pyproject.toml is missing Poe executor = "uv" configuration')

        poe_tasks = pyproject.get("tool", {}).get("poe", {}).get("tasks", {})
        for task_name in REQUIRED_POE_TASKS:
            if task_name not in poe_tasks:
                issues.append(f"Missing required Poe task: {task_name}")
        for task_name in FORBIDDEN_POE_TASKS:
            if task_name in poe_tasks:
                issues.append(f"Forbidden Poe task alias: {task_name}")
        issues.extend(collect_poe_task_contract_issues(poe_tasks))

    indexed_doc_dirs = (
        (
            "design-docs",
            (root / "docs" / "design-docs" / "index.md").read_text(encoding="utf-8")
            if (root / "docs" / "design-docs" / "index.md").exists()
            else "",
            "design doc",
        ),
        (
            "references",
            (root / "docs" / "references" / "index.md").read_text(encoding="utf-8")
            if (root / "docs" / "references" / "index.md").exists()
            else "",
            "reference doc",
        ),
        (
            "product-specs",
            (root / "docs" / "product-specs" / "index.md").read_text(encoding="utf-8")
            if (root / "docs" / "product-specs" / "index.md").exists()
            else "",
            "product spec",
        ),
        (
            "generated",
            (root / "docs" / "generated" / "index.md").read_text(encoding="utf-8")
            if (root / "docs" / "generated" / "index.md").exists()
            else "",
            "generated artifact",
        ),
    )
    for index_relative_path, config in ROUTING_INDEX_CONFIG.items():
        index_path = root / index_relative_path
        if not index_path.exists():
            continue

        content = index_path.read_text(encoding="utf-8")
        entries, duplicates = parse_routing_index_entries(
            content,
            allowed_roles=cast(set[str], config["allowed_roles"]),
        )
        if not entries:
            issues.append(f"{index_relative_path} is missing routing index table")

        for duplicate in duplicates:
            issues.append(f"{index_relative_path} has duplicate document row: {duplicate}")

        indexed_targets: set[str] = set()
        for entry in entries:
            target = entry["target"]
            resolved_target = resolve_routing_index_target(
                root,
                index_path=index_path,
                target=target,
            )
            if resolved_target is None:
                issues.append(
                    f"{index_relative_path} references document outside its directory: {target}"
                )
                continue
            if not (root / resolved_target).exists():
                issues.append(
                    f"{index_relative_path} references missing document: {resolved_target}"
                )
                continue

            indexed_targets.add(Path(resolved_target).name)
            if entry["role"] not in config["allowed_roles"]:
                issues.append(
                    f"{index_relative_path} has invalid Role field for document "
                    f"{Path(target).name}: {entry['role']}"
                )
            for field in ROUTING_INDEX_REQUIRED_FIELDS:
                if entry[field]:
                    continue
                label = field.replace("_", " ").title()
                issues.append(
                    f"{index_relative_path} has blank {label} field for document: "
                    f"{Path(target).name}"
                )

        directory = root / cast(str, config["directory"])
        if directory.exists():
            for path in sorted(directory.glob("*.md")):
                if path.name == "index.md":
                    continue
                if path.name not in indexed_targets:
                    issues.append(
                        f"{index_relative_path} is missing {cast(str, config['label'])}: "
                        f"{path.name}"
                    )

    for directory_name, index_content, label in indexed_doc_dirs:
        directory = root / "docs" / directory_name
        if not directory.exists():
            continue
        if f"docs/{directory_name}/index.md" in ROUTING_INDEX_CONFIG:
            continue
        for path in sorted(directory.glob("*.md")):
            if path.name == "index.md":
                continue
            if path.name not in index_content:
                issues.append(f"docs/{directory_name}/index.md is missing {label}: {path.name}")

    architecture_doc_path = root / "ARCHITECTURE.md"
    architecture_doc = (
        architecture_doc_path.read_text(encoding="utf-8") if architecture_doc_path.exists() else ""
    )
    if "docs/design-docs/" not in architecture_doc:
        issues.append("ARCHITECTURE.md is missing a design-docs architecture reference")
    if "docs/plans/2026-03-18-quantleet-architecture-draft-ko.md" in architecture_doc:
        issues.append("ARCHITECTURE.md still references the old plan-path architecture draft")

    old_architecture_draft = (
        root / "docs" / "plans" / "2026-03-18-quantleet-architecture-draft-ko.md"
    )
    if old_architecture_draft.exists():
        issues.append("Old plan-path Korean architecture draft should not exist")

    linked_index_docs = (
        root / "ARCHITECTURE.md",
        root / "docs" / "DESIGN.md",
        root / "docs" / "PLANS.md",
        root / "docs" / "design-docs" / "index.md",
        root / "docs" / "references" / "index.md",
        root / "docs" / "product-specs" / "index.md",
        root / "docs" / "generated" / "index.md",
    )
    for doc_path in linked_index_docs:
        if not doc_path.exists():
            continue
        for target in missing_markdown_link_targets(doc_path):
            issues.append(f"{doc_path.relative_to(root)} points to missing target: {target}")

    tests_dir = root / "tests"
    if tests_dir.exists():
        for supported_dir in SUPPORTED_TEST_DIRS:
            if not (tests_dir / supported_dir).exists():
                issues.append(f"Missing test taxonomy directory: tests/{supported_dir}")

        for path in sorted(tests_dir.glob("test_*.py")):
            issues.append(
                f"Found flat root-level test file outside taxonomy: tests/{path.name}",
            )

    return issues


def collect_doc_advisories(root: Path) -> list[str]:
    if not git_has_head(root):
        return []

    advisories: list[str] = []
    architecture_path = root / "ARCHITECTURE.md"
    plans_path = root / "docs" / "PLANS.md"
    architecture_doc = (
        architecture_path.read_text(encoding="utf-8") if architecture_path.exists() else ""
    )
    plans_doc = plans_path.read_text(encoding="utf-8") if plans_path.exists() else ""
    indexed_doc_dir_names = ("design-docs", "references", "product-specs", "generated")

    referenced_paths: set[str] = set()
    for content in (architecture_doc, plans_doc):
        referenced_paths.update(referenced_repo_paths(content))

    for directory_name in indexed_doc_dir_names:
        directory = root / "docs" / directory_name
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            if path.name == "index.md":
                continue
            referenced_paths.add(path.relative_to(root).as_posix())

    untracked_paths = git_untracked_paths(root)
    for relative_path in sorted(referenced_paths):
        if relative_path in untracked_paths and (root / relative_path).exists():
            advisories.append(f"Indexed artifact is untracked: {relative_path}")

    return advisories


def domain_for_module_parts(parts: tuple[str, ...]) -> str | None:
    if len(parts) < 2 or parts[0] != "quantleet":
        return None

    candidate = parts[1]
    return candidate if candidate in KNOWN_DOMAINS else None


def module_name_for_parts(parts: tuple[str, ...]) -> str | None:
    if not parts:
        return None

    normalized_parts = parts[:-1] if parts[-1] == "__init__" else parts
    if not normalized_parts:
        return None

    return ".".join(normalized_parts)


def root_non_domain_module_for_parts(parts: tuple[str, ...]) -> str | None:
    if len(parts) < 2 or parts[0] != "quantleet":
        return None

    if parts[1] in KNOWN_DOMAINS:
        return None

    return ".".join(parts[:2])


def validate_domain_dependency(source_domain: str | None, target_domain: str | None) -> str | None:
    if source_domain is None or target_domain is None:
        return None

    if source_domain == target_domain or target_domain in SHARED_DOMAINS:
        return None

    if (source_domain, target_domain) in ALLOWED_CROSS_DOMAIN_DEPENDENCIES:
        return None

    if target_domain in TIER_A and source_domain not in TIER_A:
        return f"Tier A boundary violation: {source_domain} cannot depend on {target_domain}"

    return f"Cross-domain dependency violation: {source_domain} cannot depend on {target_domain}"


def validate_root_module_dependency(
    source_module_parts: tuple[str, ...],
    source_domain: str | None,
    target_parts: tuple[str, ...],
) -> str | None:
    source_module = module_name_for_parts(source_module_parts)
    target_root_module = root_non_domain_module_for_parts(target_parts)

    if source_module is None or target_root_module is None:
        return None

    if source_module == target_root_module or source_module.startswith(f"{target_root_module}."):
        return None

    if (source_module, target_root_module) in ALLOWED_ROOT_MODULE_DEPENDENCIES:
        return None

    source_label = source_domain or source_module
    return (
        "Root-level module dependency violation: "
        f"{source_label} cannot depend on {target_root_module}"
    )


def resolve_import_from_module_parts(
    source_module_parts: tuple[str, ...], node: ast.ImportFrom
) -> tuple[str, ...] | None:
    if node.level == 0:
        return tuple(node.module.split(".")) if node.module is not None else None

    current_package_parts = source_module_parts[:-1]
    levels_up = node.level - 1
    if levels_up > len(current_package_parts):
        return None

    base_parts = current_package_parts[: len(current_package_parts) - levels_up]
    if node.module is None:
        return base_parts

    return base_parts + tuple(node.module.split("."))


def import_targets_for_node(
    source_module_parts: tuple[str, ...], node: ast.ImportFrom
) -> tuple[tuple[str, ...], ...]:
    base_parts = resolve_import_from_module_parts(source_module_parts, node)
    if base_parts is None:
        return ()

    if domain_for_module_parts(base_parts) is not None:
        return (base_parts,)

    targets = []
    for alias in node.names:
        if alias.name == "*":
            targets.append(base_parts)
            continue
        targets.append(base_parts + tuple(alias.name.split(".")))
    return tuple(targets)


def collect_architecture_issues(root: Path) -> list[str]:
    src_root = root / "src" / "quantleet"
    if not src_root.exists():
        return ["Missing src/quantleet package root"]

    issues: list[str] = []

    for path in src_root.rglob("*.py"):
        module_parts = ("quantleet",) + path.relative_to(src_root).with_suffix("").parts
        source_domain = domain_for_module_parts(module_parts)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

        for node in ast.walk(tree):
            target_parts: tuple[str, ...] | None = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target_parts = tuple(alias.name.split("."))
                    issue = validate_domain_dependency(
                        source_domain,
                        domain_for_module_parts(target_parts),
                    )
                    if issue is not None:
                        issues.append(f"{path}: {issue}")
                    issue = validate_root_module_dependency(
                        module_parts,
                        source_domain,
                        target_parts,
                    )
                    if issue is not None:
                        issues.append(f"{path}: {issue}")
            elif isinstance(node, ast.ImportFrom):
                for target_parts in import_targets_for_node(module_parts, node):
                    issue = validate_domain_dependency(
                        source_domain,
                        domain_for_module_parts(target_parts),
                    )
                    if issue is not None:
                        issues.append(f"{path}: {issue}")
                    issue = validate_root_module_dependency(
                        module_parts,
                        source_domain,
                        target_parts,
                    )
                    if issue is not None:
                        issues.append(f"{path}: {issue}")

    return sorted(set(issues))


def run_live_smoke() -> list[str]:
    from quantleet.integrations.venues.ccxt import Exchange, MarketType

    cases = [
        ("binance", MarketType.SPOT, "BTC/USDT"),
        ("binance", MarketType.USDM, "BTC/USDT:USDT"),
        ("bybit", MarketType.SPOT, "BTC/USDT"),
        ("bitget", MarketType.SPOT, "BTC/USDT"),
    ]

    results: list[str] = []
    for name, market_type, symbol in cases:
        rows = Exchange(name=name, market_type=market_type).fetch_ohlcv(
            symbol=symbol,
            timeframe="1h",
            limit=3,
        )
        if not rows:
            raise RuntimeError(f"Live smoke returned no rows for {name} {market_type}")
        results.append(f"{name}:{market_type}:{len(rows)}")

    return results
