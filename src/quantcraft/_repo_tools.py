from __future__ import annotations

import ast
import json
import re
import subprocess
import tomllib
from datetime import date
from pathlib import Path
from typing import cast

REQUIRED_DOCS = (
    "README.md",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "agent-development-guide-ko.md",
    "docs/DESIGN.md",
    "docs/PLANS.md",
    "docs/QUALITY_SCORE.md",
    "docs/RELIABILITY.md",
    "docs/SECURITY.md",
    "docs/feedback-promotion-log.md",
    "docs/design-docs/golden-principles.md",
    "docs/references/tooling.md",
)

PLACEHOLDER_TOKENS = ("Add your description here",)
SUPPORTED_TEST_DIRS = ("unit", "integration", "structure", "smoke")

TIER_A = {"trading", "execution"}
TIER_B = {"data", "research"}
TIER_C = {"ml"}
SHARED_DOMAINS = {"shared"}
KNOWN_DOMAINS = TIER_A | TIER_B | TIER_C | SHARED_DOMAINS
ALLOWED_CROSS_DOMAIN_DEPENDENCIES = {
    ("research", "data"),
    ("research", "trading"),
    ("execution", "trading"),
}
ALLOWED_ROOT_MODULE_DEPENDENCIES = {
    ("quantcraft", "quantcraft.exchange"),
    ("quantcraft._repo_tools", "quantcraft.exchange"),
}

EXPECTED_QUALITY_AREAS = (
    "data",
    "research",
    "trading",
    "execution",
    "docs_system",
    "verification",
)
REQUIRED_QUALITY_METADATA_FIELDS = (
    "as_of",
    "freshness_window_days",
    "evidence_rule",
    "freshness_rule",
)
QUALITY_CONTRACT_HEADINGS = (
    "## Metadata",
    "## Evidence Expectations",
    "## Score Rubric",
    "## Areas",
)
QUALITY_AREA_COLUMNS = ("Area", "Score", "Evidence", "Notes")
ALLOWED_QUALITY_SCORES = {"A", "B", "C", "D"}
QUALITY_STRONG_GRADES = {"A", "B"}
QUALITY_IMPLEMENTED_GRADES = {"A", "B", "C"}
QUALITY_AREA_RELEVANT_PATHS = {
    "data": (
        "src/quantcraft/data/",
        "src/quantcraft/exchange.py",
        "tests/unit/market_data/",
        "tests/integration/research/fixtures/",
    ),
    "research": (
        "src/quantcraft/research/",
        "tests/unit/research/",
        "tests/integration/research/",
        "docs/product-specs/backtest-mvp.md",
    ),
    "trading": (
        "src/quantcraft/trading/",
        "tests/unit/trading/",
        "docs/product-specs/backtest-mvp.md",
    ),
    "execution": (
        "src/quantcraft/execution/",
        "tests/smoke/live/",
        "docs/design-docs/quantcraft-architecture.md",
    ),
    "docs_system": (
        "docs/",
        "AGENTS.md",
        "ARCHITECTURE.md",
        "README.md",
        "tests/structure/docs/",
        "tests/structure/repo/",
    ),
    "verification": (
        "scripts/",
        "pyproject.toml",
        "tests/structure/repo/",
        "docs/references/tooling.md",
    ),
    "ml": (
        "src/quantcraft/ml/",
        "docs/design-docs/quantcraft-architecture.md",
    ),
}
QUALITY_IMPLEMENTATION_AREAS = {"data", "research", "trading", "execution", "ml"}
QUALITY_IMPLEMENTATION_PATH_PREFIXES = ("src/", "tests/", "scripts/")
QUALITY_HARNESS_PATH_PREFIXES = ("scripts/", "tests/")
INDEX_STATUS_MAP_COLUMNS = (
    "Document",
    "Status",
    "Canonical",
    "Applicability",
    "Read When",
    "Notes",
)
INDEX_STATUS_MAP_REQUIRED_HEADINGS = ("## Metadata", "## Documents")
INDEX_STATUS_MAP_REQUIRED_FIELDS = (
    "status",
    "canonical",
    "applicability",
    "read_when",
    "notes",
)
INDEX_STATUS_MAP_CANONICAL_VALUES = {"yes", "no"}
INDEX_STATUS_MAP_CONFIG = {
    "docs/design-docs/index.md": {
        "index_kind": "design-doc-status-map",
        "directory": "docs/design-docs",
        "label": "design doc",
    },
    "docs/product-specs/index.md": {
        "index_kind": "product-spec-status-map",
        "directory": "docs/product-specs",
        "label": "product spec",
    },
}
REQUIRED_POE_TASKS = (
    "lint",
    "format",
    "perf-check",
    "verify-runtime",
    "typecheck",
    "test",
    "test-unit",
    "test-integration",
    "test-structure",
    "test-smoke",
    "test-live",
    "coverage",
    "build",
    "repo-check",
    "notebook-validate",
    "live-smoke",
    "verify",
)
EXEC_PLAN_ALLOWED_STATUSES = {"active", "completed"}
EXEC_PLAN_INDEX_COLUMNS = ("Plan", "Status", "Note")
EXEC_PLAN_COMPLETE_STATUSES = {"complete", "completed"}
CANONICAL_FEEDBACK_ARTIFACT = "docs/feedback-promotion-log.md"


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


def parse_quality_metadata(content: str) -> dict[str, str]:
    return parse_bullet_metadata_section(markdown_section(content, "Metadata"))


def parse_exec_plan_lifecycle_metadata(content: str) -> dict[str, str]:
    return parse_bullet_metadata_section(markdown_section(content, "Lifecycle"))


def parse_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def parse_quality_area_table(content: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    areas_section = markdown_section(content, "Areas")
    if areas_section is None:
        return {}, []

    table_lines = [
        line.strip()
        for line in areas_section.splitlines()
        if line.strip().startswith("|")
    ]
    if len(table_lines) < 2:
        return {}, []

    header = parse_markdown_row(table_lines[0])
    if tuple(header) != QUALITY_AREA_COLUMNS:
        return {}, []

    area_rows: dict[str, dict[str, str]] = {}
    duplicate_areas: list[str] = []
    for line in table_lines[2:]:
        cells = parse_markdown_row(line)
        if len(cells) != len(QUALITY_AREA_COLUMNS):
            continue
        area, score, evidence, notes = cells
        if area in area_rows:
            duplicate_areas.append(area)
            continue
        area_rows[area] = {
            "score": score,
            "evidence": evidence,
            "notes": notes,
        }

    return area_rows, duplicate_areas


def parse_quality_area_rows(content: str) -> dict[str, dict[str, str]]:
    area_rows, _ = parse_quality_area_table(content)
    return area_rows


def parse_exec_plan_index_entries(content: str) -> tuple[list[dict[str, str]], list[str]]:
    plans_section = markdown_section(content, "Plans")
    if plans_section is None:
        return [], []

    table_lines = [
        line.strip()
        for line in plans_section.splitlines()
        if line.strip().startswith("|")
    ]
    if len(table_lines) < 2:
        return [], []

    header = parse_markdown_row(table_lines[0])
    if tuple(header) != EXEC_PLAN_INDEX_COLUMNS:
        return [], []

    entries: list[dict[str, str]] = []
    duplicates: list[str] = []
    seen_targets: set[str] = set()
    for line in table_lines[2:]:
        cells = parse_markdown_row(line)
        if len(cells) != len(EXEC_PLAN_INDEX_COLUMNS):
            continue
        target_cell, status, note = cells
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
                "target": target,
                "status": status.strip(),
                "note": note.strip(),
            }
        )

    return entries, duplicates


def parse_index_status_map_entries(content: str) -> tuple[list[dict[str, str]], list[str]]:
    documents_section = markdown_section(content, "Documents")
    if documents_section is None:
        return [], []

    table_lines = [
        line.strip()
        for line in documents_section.splitlines()
        if line.strip().startswith("|")
    ]
    if len(table_lines) < 2:
        return [], []

    header = parse_markdown_row(table_lines[0])
    if tuple(header) != INDEX_STATUS_MAP_COLUMNS:
        return [], []

    entries: list[dict[str, str]] = []
    duplicates: list[str] = []
    seen_targets: set[str] = set()
    for line in table_lines[2:]:
        cells = parse_markdown_row(line)
        if len(cells) != len(INDEX_STATUS_MAP_COLUMNS):
            continue
        target_cell, status, canonical, applicability, read_when, notes = cells
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
                "target": target,
                "status": status.strip(),
                "canonical": canonical.strip(),
                "applicability": applicability.strip(),
                "read_when": read_when.strip(),
                "notes": notes.strip(),
            }
        )

    return entries, duplicates


def parse_exec_plan_slice_statuses(content: str) -> list[str]:
    current_status_section = markdown_section(content, "Current Status")
    if current_status_section is None:
        return []

    statuses: list[str] = []
    for line in current_status_section.splitlines():
        match = re.match(r"^\s*[-*]\s*Slice\s+\d+:\s*(.+?)\s*$", line)
        if match is None:
            continue
        statuses.append(match.group(1).strip().lower())

    return statuses


def resolve_exec_plan_index_target(
    root: Path, *, index_path: Path, target: str
) -> str | None:
    relative_base = index_path.parent.relative_to(root)
    relative_path = (relative_base / target).as_posix()
    if relative_path.startswith("../"):
        return None
    return relative_path


def resolve_index_status_map_target(
    root: Path, *, index_path: Path, target: str
) -> str | None:
    relative_base = index_path.parent.relative_to(root)
    relative_path = (relative_base / target).as_posix()
    if relative_path.startswith("../"):
        return None
    return relative_path


def quality_score_snapshot(root: Path) -> dict[str, object]:
    return quality_score_snapshot_for_date(root, today=date.today())


def parse_iso_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def parse_positive_int(value: str) -> int | None:
    try:
        parsed = int(value)
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def is_area_relevant_path(area: str, path: str) -> bool:
    for candidate in QUALITY_AREA_RELEVANT_PATHS.get(area, ()):
        if path == candidate or path.startswith(candidate):
            return True
    return False


def is_implementation_path(path: str) -> bool:
    return path.startswith(QUALITY_IMPLEMENTATION_PATH_PREFIXES)


def is_harness_check_path(path: str) -> bool:
    return path == "pyproject.toml" or path.startswith(QUALITY_HARNESS_PATH_PREFIXES)


def evaluate_quality_area_evidence(
    root: Path,
    *,
    area: str,
    score: str,
    evidence: str,
) -> tuple[list[str], str]:
    issues: list[str] = []
    evidence_paths = sorted(referenced_repo_paths(evidence))
    if not evidence_paths:
        issues.append(f"Quality evidence for {area} must reference at least one repository path")
        return issues, "missing_paths"

    valid_evidence_paths: list[str] = []
    for evidence_path in evidence_paths:
        if not (root / evidence_path).exists():
            issues.append(
                f"Quality evidence for {area} references missing repository path: "
                f"{evidence_path}"
            )
            continue
        valid_evidence_paths.append(evidence_path)

    if score in QUALITY_STRONG_GRADES:
        if len(valid_evidence_paths) < 2:
            issues.append(
                f"Quality evidence for {area} score {score} must reference at least "
                "two valid repository paths"
            )
        relevant_paths = [
            path for path in valid_evidence_paths if is_area_relevant_path(area, path)
        ]
        if not relevant_paths:
            issues.append(
                f"Quality evidence for {area} score {score} must include at least one "
                "area-relevant path"
            )
        if area == "verification" and not any(
            is_harness_check_path(path) for path in valid_evidence_paths
        ):
            issues.append(
                f"Quality evidence for {area} score {score} must include at least one "
                "harness-check path"
            )

    if area in QUALITY_IMPLEMENTATION_AREAS and score in QUALITY_IMPLEMENTED_GRADES:
        if not any(
            is_area_relevant_path(area, path) and is_implementation_path(path)
            for path in valid_evidence_paths
        ):
            issues.append(
                f"Quality evidence for {area} score {score} must include at least one "
                "implementation or test path"
            )

    return issues, "invalid" if issues else "valid"


def quality_score_snapshot_for_date(root: Path, *, today: date) -> dict[str, object]:
    relative_path = "docs/QUALITY_SCORE.md"
    quality_score_path = root / relative_path
    snapshot: dict[str, object] = {
        "path": relative_path,
        "metadata": {},
        "tracked_areas": {},
        "missing_metadata": list(REQUIRED_QUALITY_METADATA_FIELDS),
        "missing_areas": list(EXPECTED_QUALITY_AREAS),
        "validation": {
            "today": today.isoformat(),
            "as_of_status": "missing",
            "evidence_status": {},
            "issue_count": 0,
        },
    }
    if not quality_score_path.exists():
        return snapshot

    content = quality_score_path.read_text(encoding="utf-8")
    metadata = parse_quality_metadata(content)
    tracked_areas, duplicate_areas = parse_quality_area_table(content)
    snapshot["metadata"] = metadata
    snapshot["tracked_areas"] = tracked_areas
    snapshot["duplicate_areas"] = duplicate_areas
    snapshot["missing_metadata"] = [
        field for field in REQUIRED_QUALITY_METADATA_FIELDS if not metadata.get(field)
    ]
    snapshot["missing_areas"] = [
        area for area in EXPECTED_QUALITY_AREAS if area not in tracked_areas
    ]
    validation = cast(dict[str, object], snapshot["validation"])
    as_of = metadata.get("as_of")
    freshness_window_days = parse_positive_int(metadata.get("freshness_window_days", ""))
    if as_of:
        as_of_date = parse_iso_date(as_of)
        if as_of_date is None:
            validation["as_of_status"] = "invalid"
        elif as_of_date > today:
            validation["as_of_status"] = "future"
        elif (
            freshness_window_days is not None
            and (today - as_of_date).days > freshness_window_days
        ):
            validation["as_of_status"] = "stale"
        else:
            validation["as_of_status"] = "valid"

    evidence_status: dict[str, str] = {}
    for area, row in tracked_areas.items():
        _, status = evaluate_quality_area_evidence(
            root,
            area=area,
            score=row.get("score", ""),
            evidence=row.get("evidence", ""),
        )
        evidence_status[area] = status

    validation["evidence_status"] = evidence_status
    return snapshot


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
    if "## Setup" not in readme:
        issues.append("README.md is missing the setup section")
    if "uv run poe" not in readme:
        issues.append("README.md is missing uv run poe guidance")

    plans_doc_path = root / "docs/PLANS.md"
    plans_doc = plans_doc_path.read_text(encoding="utf-8") if plans_doc_path.exists() else ""
    required_plan_references = (
        "docs/plans/",
        "docs/exec-plans/active/",
        "docs/exec-plans/completed/",
    )
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

    local_guide_path = root / "agent-development-guide-ko.md"
    local_guide = (
        local_guide_path.read_text(encoding="utf-8") if local_guide_path.exists() else ""
    )
    if "project.scripts" in local_guide:
        issues.append("agent-development-guide-ko.md still references project.scripts")

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

    tooling_path = root / "docs" / "references" / "tooling.md"
    tooling = tooling_path.read_text(encoding="utf-8") if tooling_path.exists() else ""
    for command in (
        "uv run poe verify",
        "uv run poe coverage",
        "uv run poe format",
        "uv run poe test-live",
        "uv run python scripts/coverage_check.py",
        "uv run python scripts/repo_check.py",
        "uv run python scripts/notebook_validate.py",
        "uv run python scripts/live_smoke.py",
    ):
        if command not in tooling:
            issues.append(f"docs/references/tooling.md is missing command: {command}")

    quality_score_path = root / "docs" / "QUALITY_SCORE.md"
    quality_score = (
        quality_score_path.read_text(encoding="utf-8") if quality_score_path.exists() else ""
    )
    if quality_score and CANONICAL_FEEDBACK_ARTIFACT not in quality_score:
        issues.append(
            "docs/QUALITY_SCORE.md is missing canonical feedback artifact reference: "
            f"{CANONICAL_FEEDBACK_ARTIFACT}"
        )

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
    for index_relative_path, config in INDEX_STATUS_MAP_CONFIG.items():
        index_path = root / index_relative_path
        if not index_path.exists():
            continue

        content = index_path.read_text(encoding="utf-8")
        for heading in INDEX_STATUS_MAP_REQUIRED_HEADINGS:
            if heading not in content:
                issues.append(f"{index_relative_path} is missing required heading: {heading}")

        metadata = parse_bullet_metadata_section(markdown_section(content, "Metadata"))
        if metadata.get("index_kind") != config["index_kind"]:
            issues.append(
                f"{index_relative_path} must declare index_kind: {config['index_kind']}"
            )

        header = "| " + " | ".join(INDEX_STATUS_MAP_COLUMNS) + " |"
        if header not in content:
            issues.append(
                f"{index_relative_path} is missing table header: {header}"
            )

        entries, duplicates = parse_index_status_map_entries(content)
        for duplicate in duplicates:
            issues.append(f"{index_relative_path} has duplicate document row: {duplicate}")

        indexed_targets: set[str] = set()
        for entry in entries:
            target = entry["target"]
            resolved_target = resolve_index_status_map_target(
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
            if entry["canonical"].lower() not in INDEX_STATUS_MAP_CANONICAL_VALUES:
                issues.append(
                    f"{index_relative_path} has invalid Canonical field for document "
                    f"{Path(target).name}: {entry['canonical']}"
                )
            for field in INDEX_STATUS_MAP_REQUIRED_FIELDS:
                if entry[field]:
                    continue
                label = field.replace("_", " ").title()
                issues.append(
                    f"{index_relative_path} has blank {label} field for document: "
                    f"{Path(target).name}"
                )

        directory = root / config["directory"]
        if directory.exists():
            for path in sorted(directory.glob("*.md")):
                if path.name == "index.md":
                    continue
                if path.name not in indexed_targets:
                    issues.append(
                        f"{index_relative_path} is missing {config['label']}: {path.name}"
                    )

    for directory_name, index_content, label in indexed_doc_dirs:
        directory = root / "docs" / directory_name
        if not directory.exists():
            continue
        if f"docs/{directory_name}/index.md" in INDEX_STATUS_MAP_CONFIG:
            continue
        for path in sorted(directory.glob("*.md")):
            if path.name == "index.md":
                continue
            if path.name not in index_content:
                issues.append(f"docs/{directory_name}/index.md is missing {label}: {path.name}")

    architecture_doc_path = root / "ARCHITECTURE.md"
    architecture_doc = (
        architecture_doc_path.read_text(encoding="utf-8")
        if architecture_doc_path.exists()
        else ""
    )
    if "docs/design-docs/" not in architecture_doc:
        issues.append("ARCHITECTURE.md is missing a design-docs architecture reference")
    if "docs/plans/2026-03-18-quantcraft-architecture-draft-ko.md" in architecture_doc:
        issues.append("ARCHITECTURE.md still references the old plan-path architecture draft")

    old_architecture_draft = (
        root / "docs" / "plans" / "2026-03-18-quantcraft-architecture-draft-ko.md"
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

    plans_dir = root / "docs" / "plans"
    if plans_dir.exists():
        for path in sorted(plans_dir.glob("*.md")):
            relative_path = path.relative_to(root).as_posix()
            if relative_path not in plans_doc:
                issues.append(f"docs/PLANS.md is missing historical plan entry: {relative_path}")

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
    if len(parts) < 2 or parts[0] != "quantcraft":
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
    if len(parts) < 2 or parts[0] != "quantcraft":
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
    src_root = root / "src" / "quantcraft"
    if not src_root.exists():
        return ["Missing src/quantcraft package root"]

    issues: list[str] = []

    for path in src_root.rglob("*.py"):
        module_parts = ("quantcraft",) + path.relative_to(src_root).with_suffix("").parts
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
    from quantcraft.exchange import Exchange, MarketType

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


def collect_quality_issues(root: Path, *, today: date | None = None) -> list[str]:
    quality_score = root / "docs" / "QUALITY_SCORE.md"
    if not quality_score.exists():
        return ["Missing docs/QUALITY_SCORE.md"]

    effective_today = today or date.today()
    content = quality_score.read_text(encoding="utf-8")
    issues: list[str] = []

    for heading in QUALITY_CONTRACT_HEADINGS:
        if heading not in content:
            issues.append(f"Missing quality contract section: {heading}")

    metadata = parse_quality_metadata(content)
    for field in REQUIRED_QUALITY_METADATA_FIELDS:
        if not metadata.get(field):
            issues.append(f"Missing quality metadata field: {field}")

    as_of = metadata.get("as_of")
    freshness_window_days = parse_positive_int(metadata.get("freshness_window_days", ""))
    if metadata.get("freshness_window_days") and freshness_window_days is None:
        issues.append("Quality metadata field freshness_window_days must be a positive integer")
    if as_of:
        as_of_date = parse_iso_date(as_of)
        if as_of_date is None:
            issues.append("Quality metadata field as_of must use YYYY-MM-DD")
        elif as_of_date > effective_today:
            issues.append("Quality metadata field as_of cannot be in the future")
        elif freshness_window_days is not None:
            age_days = (effective_today - as_of_date).days
            if age_days > freshness_window_days:
                issues.append(
                    "Quality metadata field as_of is stale for freshness_window_days: "
                    f"{freshness_window_days}"
                )

    tracked_areas, duplicate_areas = parse_quality_area_table(content)
    if "| Area | Score | Evidence | Notes |" not in content:
        issues.append("Missing quality areas table header: | Area | Score | Evidence | Notes |")
    for area in duplicate_areas:
        issues.append(f"Duplicate quality area row: {area}")

    for area in EXPECTED_QUALITY_AREAS:
        if area not in tracked_areas:
            issues.append(f"Missing quality area row: {area}")

    for area, row in tracked_areas.items():
        score = row.get("score", "")
        if score not in ALLOWED_QUALITY_SCORES:
            issues.append(f"Invalid quality score for {area}: {score}")
        evidence = row.get("evidence", "").strip()
        if not evidence:
            issues.append(f"Missing evidence text for quality area: {area}")
        else:
            area_issues, _ = evaluate_quality_area_evidence(
                root,
                area=area,
                score=score,
                evidence=evidence,
            )
            issues.extend(area_issues)
        if not row.get("notes", "").strip():
            issues.append(f"Missing notes text for quality area: {area}")

    return issues


def collect_plan_lifecycle_issues(root: Path) -> list[str]:
    issues: list[str] = []
    exec_plans_root = root / "docs" / "exec-plans"
    directories = {
        "active": exec_plans_root / "active",
        "completed": exec_plans_root / "completed",
    }
    indexed_paths: dict[str, dict[str, dict[str, str]]] = {}
    indexed_names: dict[str, set[str]] = {}

    for directory_status, directory in directories.items():
        index_path = directory / "index.md"
        relative_index_path = index_path.relative_to(root).as_posix()
        if not index_path.exists():
            issues.append(f"Missing execution-plan index: {relative_index_path}")
            indexed_paths[directory_status] = {}
            indexed_names[directory_status] = set()
            continue

        content = index_path.read_text(encoding="utf-8")
        metadata = parse_bullet_metadata_section(markdown_section(content, "Metadata"))
        if metadata.get("index_status") != directory_status:
            issues.append(
                f"Execution plan index {relative_index_path} must declare "
                f"index_status: {directory_status}"
            )
        if "| Plan | Status | Note |" not in content:
            issues.append(
                f"Execution plan index {relative_index_path} is missing table header: "
                "| Plan | Status | Note |"
            )

        entries, duplicates = parse_exec_plan_index_entries(content)
        resolved_entries: dict[str, dict[str, str]] = {}
        indexed_names[directory_status] = set()
        for duplicate in duplicates:
            issues.append(
                f"Execution plan index {relative_index_path} has duplicate entry target: "
                f"{duplicate}"
            )

        for entry in entries:
            target = entry["target"]
            resolved_target = resolve_exec_plan_index_target(
                root,
                index_path=index_path,
                target=target,
            )
            if resolved_target is None:
                issues.append(
                    f"Execution plan index {relative_index_path} references out-of-scope "
                    f"target: {target}"
                )
                continue

            resolved_entries[resolved_target] = entry
            indexed_names[directory_status].add(Path(resolved_target).name)
            if entry["status"] != directory_status:
                issues.append(
                    f"Execution plan index {relative_index_path} must list {resolved_target} "
                    f"with status {directory_status}, not {entry['status']}"
                )
            if not entry["note"]:
                issues.append(
                    f"Execution plan index {relative_index_path} is missing a note for "
                    f"{resolved_target}"
                )
            if not (root / resolved_target).exists():
                issues.append(
                    f"Execution plan index {relative_index_path} references missing plan file: "
                    f"{resolved_target}"
                )

        indexed_paths[directory_status] = resolved_entries

    seen_names: dict[str, str] = {}
    for directory_status, directory in directories.items():
        if not directory.exists():
            issues.append(
                "Missing execution-plan directory: "
                f"{directory.relative_to(root).as_posix()}"
            )
            continue

        for path in sorted(directory.glob("*.md")):
            if path.name == "index.md":
                continue
            relative_path = path.relative_to(root).as_posix()
            declared_name_owner = seen_names.get(path.name)
            if declared_name_owner is not None:
                issues.append(
                    f"Execution plan filename appears in multiple lifecycle directories: "
                    f"{path.name}"
                )
            else:
                seen_names[path.name] = relative_path

            content = path.read_text(encoding="utf-8")
            metadata = parse_exec_plan_lifecycle_metadata(content)
            status = metadata.get("status")
            if not status:
                issues.append(
                    f"Execution plan {relative_path} is missing lifecycle metadata field: "
                    "status"
                )
                continue
            if status not in EXEC_PLAN_ALLOWED_STATUSES:
                issues.append(
                    f"Execution plan {relative_path} has invalid status: {status}"
                )
                continue
            if status != directory_status:
                issues.append(
                    f"Execution plan {relative_path} is under docs/exec-plans/{directory_status}/ "
                    f"but declares status {status}"
                )

            slice_statuses = parse_exec_plan_slice_statuses(content)
            if (
                status == "active"
                and slice_statuses
                and all(
                    slice_status in EXEC_PLAN_COMPLETE_STATUSES
                    for slice_status in slice_statuses
                )
                and not metadata.get("status_reason")
            ):
                issues.append(
                    f"Execution plan {relative_path} marks every slice complete but remains "
                    "active without status_reason"
                )
            if (
                status == "completed"
                and slice_statuses
                and any(
                    slice_status not in EXEC_PLAN_COMPLETE_STATUSES
                    for slice_status in slice_statuses
                )
            ):
                issues.append(
                    f"Execution plan {relative_path} declares completed status but has "
                    "non-complete slice states"
                )

            indexed_entry = indexed_paths.get(directory_status, {}).get(relative_path)
            if indexed_entry is None:
                issues.append(
                    f"Execution plan index docs/exec-plans/{directory_status}/index.md is "
                    f"missing plan entry: {relative_path}"
                )
            elif indexed_entry["status"] != status:
                issues.append(
                    f"Execution plan index docs/exec-plans/{directory_status}/index.md lists "
                    f"{relative_path} with status {indexed_entry['status']}, but the plan file "
                    f"declares {status}"
                )

            other_status = "completed" if directory_status == "active" else "active"
            if path.name in indexed_names.get(other_status, set()):
                issues.append(
                    f"Execution plan {path.name} is indexed in both active and completed "
                    "execution-plan indexes"
                )

    return sorted(set(issues))


def quality_report(root: Path) -> str:
    quality_score = quality_score_snapshot(root)
    report = {
        "doc_issues": collect_doc_issues(root),
        "architecture_issues": collect_architecture_issues(root),
        "quality_issues": collect_quality_issues(root),
        "plan_lifecycle_issues": collect_plan_lifecycle_issues(root),
        "quality_score": quality_score,
    }
    validation = cast(dict[str, object], quality_score["validation"])
    validation["issue_count"] = len(report["quality_issues"])
    return json.dumps(report, indent=2, sort_keys=True)
