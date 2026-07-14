#!/usr/bin/env python3
"""Compose an executable expert-team plan from a project and a skill index.

The script deliberately keeps project inspection and capability routing separate:
the target project is scanned locally, while the capability catalog is read from
the configured remote or local index. It never installs skills or writes files.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
DISCOVER_PATH = SCRIPT_DIR / "discover_skills.py"
spec = importlib.util.spec_from_file_location("discover_skills", DISCOVER_PATH)
if spec is None or spec.loader is None:  # pragma: no cover - import guard
    raise RuntimeError(f"Cannot load discovery module: {DISCOVER_PATH}")
discover = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = discover
spec.loader.exec_module(discover)


DEFAULT_INDEX_URL = discover.DEFAULT_INDEX_URL
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "target",
    "coverage",
    ".next",
    ".nuxt",
    ".umi",
    ".cache",
    "__pycache__",
    ".venv",
    "venv",
}
MANIFEST_NAMES = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Pipfile",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "Cargo.toml",
    "go.mod",
    "composer.json",
    "Gemfile",
}
TEST_NAME_RE = re.compile(
    r"(^|/)(test|tests|__tests__|spec|e2e|cypress|playwright)(/|$)|"
    r"(^|[._-])(test|spec|e2e)([._-]|$)",
    re.IGNORECASE,
)
ROUTE_NAME_RE = re.compile(r"(^|/)(routes?|router|pages?|views?)(/|$)|route", re.IGNORECASE)
API_RE = re.compile(r"/(?:api|graphql|rpc)/|\b(?:axios|fetch|request|graphql)\b", re.IGNORECASE)
MOCK_RE = re.compile(r"(^|/)(mock|mocks|fixtures?)(/|$)|\bmock\b", re.IGNORECASE)
CI_RE = re.compile(r"(^|/)(\.github/workflows|\.gitlab-ci|jenkins|azure-pipelines)(/|$)", re.IGNORECASE)
LOCAL_SOURCE_PRIORITY = {
    "project-expert-team": 1000,
    "project-agent": 900,
    "project-skill": 850,
    "installed-agent": 800,
    "installed-skill": 800,
}
LOCAL_SOURCE_KINDS = set(LOCAL_SOURCE_PRIORITY)
LOCAL_EXCLUDED_NAMES = {"README.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md"}
LOCAL_NAME_KEYWORDS = {
    "requirements": {"requirement", "requirements", "prd", "acceptance", "需求", "验收"},
    "implementation": {"implement", "implementation", "build", "developer", "frontend", "backend", "code", "开发", "实现"},
    "unit-testing": {"test", "testing", "unit", "integration", "regression", "coverage", "qa", "测试", "回归"},
    "e2e-testing": {"e2e", "browser", "playwright", "cypress", "selenium", "puppeteer", "用户流程"},
    "api-testing": {"api", "http", "graphql", "mock", "contract", "接口"},
    "review": {"review", "audit", "quality", "security", "审查", "审计", "质量"},
    "architecture": {"architecture", "architect", "refactor", "migration", "system", "架构", "重构", "迁移"},
}


@dataclass(frozen=True)
class Slot:
    key: str
    role_en: str
    role_zh: str
    description_en: str
    description_zh: str
    keywords: tuple[str, ...]
    preferred: tuple[str, ...]


SLOTS = (
    Slot(
        "requirements",
        "Requirements analyst",
        "需求分析专家",
        "Turn the request and repository evidence into behavior, scope, and acceptance criteria.",
        "将用户请求和仓库证据转化为行为、范围和验收标准。",
        ("requirement", "requirements", "prd", "scope", "acceptance", "需求", "澄清", "验收"),
        ("requirements-analysis", "requirement-discovery", "product-requirements", "project-requirements"),
    ),
    Slot(
        "implementation",
        "Implementation specialist",
        "实现专家",
        "Identify the smallest implementation plan and own the requested code change when execution is enabled.",
        "确定最小实现方案，并在执行模式下负责请求的代码变更。",
        ("implement", "implementation", "build", "code", "feature", "fix", "实现", "开发", "修复", "新增", "修改"),
        ("parallel-implementation", "frontend-build", "backend-api", "frontend-backend-build", "tech-frontend-engineer-execution"),
    ),
    Slot(
        "unit-testing",
        "Test strategy specialist",
        "测试策略专家",
        "Design and run unit, component, integration, regression, and coverage checks for the affected behavior.",
        "为受影响行为设计并执行单元、组件、集成、回归和覆盖率检查。",
        ("test", "testing", "unit", "integration", "regression", "coverage", "quality", "测试", "回归", "覆盖率", "验证"),
        ("test-patterns", "test-case-generator", "qa-validation", "qa-testing", "quality-gate"),
    ),
    Slot(
        "e2e-testing",
        "End-to-end testing specialist",
        "端到端测试专家",
        "Validate the user journey in a real browser or UI runtime with stable selectors and repeatable evidence.",
        "在真实浏览器或 UI 运行时验证用户流程，提供稳定、可重复的证据。",
        ("e2e", "browser", "playwright", "cypress", "journey", "ui", "页面", "浏览器", "流程"),
        ("e2e-testing-patterns", "browser", "playwright", "cypress", "qa-validation"),
    ),
    Slot(
        "api-testing",
        "API contract specialist",
        "API 契约专家",
        "Check frontend service calls, mock behavior, response shapes, error paths, and executable API evidence.",
        "核对前端服务调用、mock 行为、响应结构、错误路径和可执行接口证据。",
        ("api", "http", "contract", "mock", "service", "接口", "请求", "响应", "mock", "服务"),
        ("qa-api-tester", "api-test-automation", "project-api-testing-execution", "api-dev", "backend-api"),
    ),
    Slot(
        "review",
        "Quality reviewer",
        "质量审查专家",
        "Review the proposed result against the acceptance contract, regressions, security boundaries, and delivery evidence.",
        "依据验收契约、回归风险、安全边界和交付证据审查最终结果。",
        ("review", "audit", "quality", "risk", "审查", "审计", "质量", "风险"),
        ("code-review", "critical-code-reviewer", "quality-gate", "qa-validation", "release-risk"),
    ),
    Slot(
        "architecture",
        "Architecture specialist",
        "架构专家",
        "Assess cross-module impact, data flow, integration boundaries, and migration or design decisions.",
        "评估跨模块影响、数据流、集成边界以及迁移或设计决策。",
        ("architecture", "refactor", "migration", "design", "system", "架构", "重构", "迁移", "设计"),
        ("architecture-design", "architecture-adr", "system-architect", "tech-software-architect-strategy"),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan a project and compose a capability-based expert team."
    )
    parser.add_argument("--project-root", required=True, help="Target project repository")
    parser.add_argument("--task", required=True, help="Requested task and expected deliverable")
    parser.add_argument(
        "--mode",
        choices=("auto-execute", "execute", "blueprint", "package"),
        default="auto-execute",
        help="Execution intent; auto-execute is the default",
    )
    parser.add_argument("--catalog-root", default=str(discover.DEFAULT_CATALOG_ROOT))
    parser.add_argument("--index", help="Local index path; enables offline catalog mode")
    parser.add_argument("--index-url", default=DEFAULT_INDEX_URL)
    parser.add_argument(
        "--skill-root",
        action="append",
        dest="skill_roots",
        help="Additional installed or project Skill root; may be repeated",
    )
    parser.add_argument(
        "--agent-root",
        action="append",
        dest="agent_roots",
        help="Additional installed or project Agent root; may be repeated",
    )
    parser.add_argument(
        "--no-local",
        action="store_true",
        help="Disable local Skill, Agent, and project-team discovery",
    )
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--candidate-limit", type=int, default=40)
    parser.add_argument("--max-members", type=int, default=5)
    parser.add_argument("--skip-verify", action="store_true", help="Do not read selected SKILL.md files")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser.parse_args()


def normalize_mode(value: str) -> str:
    return "auto-execute" if value == "execute" else value


def safe_read(path: Path, limit: int = 12000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def frontmatter_value(text: str, key: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    if end < 0:
        return ""
    frontmatter = text[3:end]
    match = re.search(rf"^{re.escape(key)}:\s*(?:[\"']([^\"']+)[\"']|([^\n]+))", frontmatter, re.MULTILINE)
    if not match:
        return ""
    value = (match.group(1) or match.group(2)).strip()
    if value in {"|", ">"}:
        lines = frontmatter[match.end() :].splitlines()
        block = []
        for line in lines:
            if line and not line[0].isspace():
                break
            if line.strip():
                block.append(line.strip())
        return (" " if value == ">" else "\n").join(block)
    return value


def default_local_roots(project_root: Path) -> tuple[list[tuple[Path, str]], list[tuple[Path, str]]]:
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    skill_roots = [
        (codex_home / "skills", "installed-skill"),
        (Path.home() / ".agents/skills", "installed-skill"),
        (project_root / "skills", "project-skill"),
    ]
    agent_roots = [
        (codex_home / "agents", "installed-agent"),
        (Path.home() / ".agents/agents", "installed-agent"),
        (project_root / "agents", "project-agent"),
    ]
    return dedupe_roots(skill_roots), dedupe_roots(agent_roots)


def dedupe_roots(roots: Iterable[tuple[Path, str]]) -> list[tuple[Path, str]]:
    seen: set[tuple[str, str]] = set()
    result: list[tuple[Path, str]] = []
    for path, source_kind in roots:
        resolved = path.expanduser().resolve()
        key = (str(resolved), source_kind)
        if key not in seen:
            seen.add(key)
            result.append((resolved, source_kind))
    return result


def local_skill_files(root: Path) -> Iterable[tuple[Path, str, str, str]]:
    if not root.is_dir():
        return
    for path in sorted(root.rglob("SKILL.md")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        text = safe_read(path, 24000)
        name = frontmatter_value(text, "name") or path.parent.name
        description = frontmatter_value(text, "description")
        yield path, name, description, text


def local_agent_files(root: Path) -> Iterable[tuple[Path, str, str, str]]:
    if not root.is_dir():
        return
    for path in sorted(root.rglob("*.md")):
        if path.name in LOCAL_EXCLUDED_NAMES or any(part in SKIP_DIRS for part in path.parts):
            continue
        text = safe_read(path, 24000)
        name = frontmatter_value(text, "name") or path.stem
        description = frontmatter_value(text, "description")
        if name and (description or text.startswith("---")):
            yield path, name, description, text


def iter_project_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRS)
        for filename in sorted(files):
            path = Path(current) / filename
            if path.is_file():
                yield path


def relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def extract_package_facts(path: Path) -> dict[str, Any]:
    if path.name != "package.json":
        return {}
    try:
        data = json.loads(safe_read(path, 100000))
    except json.JSONDecodeError:
        return {"parse_error": True}
    dependencies = sorted(
        set((data.get("dependencies") or {}).keys())
        | set((data.get("devDependencies") or {}).keys())
    )
    scripts = data.get("scripts") or {}
    return {
        "name": data.get("name"),
        "dependencies": dependencies[:80],
        "scripts": {key: scripts[key] for key in sorted(scripts) if key in {"test", "test:unit", "test:e2e", "lint", "build", "start", "dev"}},
    }


def scan_project(root: Path, task: str) -> dict[str, Any]:
    files = list(iter_project_files(root))
    rel_files = [relative_path(root, path) for path in files]
    manifests = [name for name in rel_files if Path(name).name in MANIFEST_NAMES]
    instructions = [
        name
        for name in rel_files
        if Path(name).name.upper() in {"AGENTS.MD", "CLAUDE.MD", "CONTRIBUTING.MD"}
    ]
    tests = [name for name in rel_files if TEST_NAME_RE.search(name)]
    route_files = [name for name in rel_files if ROUTE_NAME_RE.search(name)]
    ci_files = [name for name in rel_files if CI_RE.search(name)]
    mock_files = [name for name in rel_files if MOCK_RE.search(name)]
    api_files: list[str] = []
    task_tokens = {token.lower() for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", task)}
    affected_files = []
    package_facts: list[dict[str, Any]] = []
    content_signals = {"api": False, "mock": False, "browser": False, "route": False}

    for path in files:
        rel = relative_path(root, path)
        if Path(rel).name in MANIFEST_NAMES:
            package_fact = extract_package_facts(path)
            if package_fact:
                package_fact["path"] = rel
                package_facts.append(package_fact)
        if any(token in rel.lower() for token in task_tokens):
            affected_files.append(rel)
        if path.suffix.lower() in {".js", ".jsx", ".ts", ".tsx", ".py", ".java", ".go", ".rs"}:
            content = safe_read(path, 20000)
            if API_RE.search(content):
                content_signals["api"] = True
                api_files.append(rel)
            if MOCK_RE.search(content):
                content_signals["mock"] = True
            if re.search(r"\b(?:playwright|cypress|selenium|puppeteer)\b", content, re.IGNORECASE):
                content_signals["browser"] = True
            if ROUTE_NAME_RE.search(rel) or re.search(r"\b(?:routes?|router)\b", content, re.IGNORECASE):
                content_signals["route"] = True

    stack: set[str] = set()
    for package in package_facts:
        for dependency in package.get("dependencies", []):
            lowered = dependency.lower()
            if lowered in {"react", "vue", "angular", "umi", "dva", "antd", "jest", "mocha", "vitest", "cypress", "playwright", "axios"}:
                stack.add(dependency)
    for filename in manifests:
        suffix = Path(filename).name.lower()
        if suffix in {"pyproject.toml", "requirements.txt", "pipfile"}:
            stack.add("Python")
        elif suffix == "pom.xml":
            stack.add("Java/Maven")
        elif suffix in {"cargo.toml"}:
            stack.add("Rust")
        elif suffix == "go.mod":
            stack.add("Go")

    signals = {
        "has_tests": bool(tests),
        "has_ci": bool(ci_files),
        "has_routes": bool(route_files) or content_signals["route"],
        "has_api": bool(api_files) or content_signals["api"],
        "has_mocks": bool(mock_files) or content_signals["mock"],
        "has_browser_tooling": content_signals["browser"] or any(
            name.lower() in {"cypress", "playwright"} for name in stack
        ),
    }
    return {
        "root": str(root),
        "manifests": manifests[:40],
        "instructions": instructions[:20],
        "test_files": tests[:60],
        "route_files": route_files[:60],
        "api_files": api_files[:60],
        "mock_files": mock_files[:60],
        "ci_files": ci_files[:40],
        "affected_files": affected_files[:80],
        "stack": sorted(stack),
        "package_facts": package_facts,
        "signals": signals,
        "file_count": len(files),
    }


def slot_is_required(slot: Slot, task: str, scan: dict[str, Any], mode: str) -> bool:
    normalized = task.lower()
    if slot.key == "requirements":
        return not bool(re.search(r"acceptance|验收标准|明确要求|已确定|spec locked|范围明确", normalized))
    if slot.key == "implementation":
        return mode == "auto-execute" and bool(
            re.search(r"implement|implementation|build|fix|change|add|modify|refactor|实现|开发|修复|新增|修改|重构", normalized)
        )
    if slot.key == "unit-testing":
        explicit_test = bool(re.search(r"test|testing|qa|verify|regression|测试|验证|回归|质量", normalized))
        behavior_change = bool(re.search(r"implement|implementation|build|fix|change|add|modify|refactor|实现|开发|修复|新增|修改|重构", normalized))
        return explicit_test or (mode == "auto-execute" and behavior_change)
    if slot.key == "e2e-testing":
        return bool(
            scan["signals"]["has_browser_tooling"]
            or (
                scan["signals"]["has_routes"]
                and re.search(r"test|testing|verify|测试|验证|页面|列表|导入|删除|表单|用户流程|/", normalized)
            )
            or re.search(r"e2e|browser|playwright|cypress|ui|journey|页面|浏览器|用户流程", normalized)
        )
    if slot.key == "api-testing":
        return bool(scan["signals"]["has_api"] or scan["signals"]["has_mocks"] or re.search(r"api|http|mock|接口|请求|响应|服务", normalized))
    if slot.key == "review":
        return bool(re.search(r"review|audit|quality|risk|审查|审计|质量|风险", normalized))
    if slot.key == "architecture":
        return bool(re.search(r"architecture|refactor|migration|system|架构|重构|迁移|系统", normalized))
    return False


def local_candidate_score(name: str, text: str, slot: Slot, task: str, scan: dict[str, Any], source_kind: str) -> tuple[int, list[str]]:
    lowered_name = name.lower()
    lowered_text = text.lower() if source_kind == "project-expert-team" else lowered_name
    query = f"{task} {' '.join(scan['stack'])} {' '.join(scan['affected_files'])}".lower()
    local_keywords = LOCAL_NAME_KEYWORDS[slot.key] if source_kind != "project-expert-team" else slot.keywords
    direct_terms = {
        keyword
        for keyword in local_keywords
        if discover.contains_term(lowered_name, keyword.lower())
        or (source_kind == "project-expert-team" and keyword.lower() in lowered_text)
    }
    if not direct_terms and name not in slot.preferred:
        return 0, []
    score = LOCAL_SOURCE_PRIORITY[source_kind]
    if name in slot.preferred:
        score += 80 - slot.preferred.index(name) * 5
    score += len(direct_terms) * 18
    score += sum(2 for keyword in slot.keywords if keyword.lower() in query)
    if slot.key == "e2e-testing" and scan["signals"]["has_browser_tooling"]:
        score += 12
    if slot.key == "api-testing" and scan["signals"]["has_api"]:
        score += 12
    return score, sorted(direct_terms)


def discover_local_candidates(
    project_root: Path,
    task: str,
    scan: dict[str, Any],
    skill_roots: list[tuple[Path, str]],
    agent_roots: list[tuple[Path, str]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    candidates: dict[str, list[dict[str, Any]]] = {slot.key: [] for slot in SLOTS}
    discovered = {"skills": 0, "agents": 0, "expert_teams": 0, "roots": []}

    def add_local_item(
        path: Path,
        name: str,
        description: str,
        content: str,
        source_kind: str,
        team_id: str,
        team_name: str,
    ) -> None:
        # Use frontmatter identity for qualification. Full bodies often mention
        # unrelated concepts and would make a PRD or UI Skill look like an API tester.
        searchable = f"{name}\n{description}"
        for slot in SLOTS:
            score, matched_terms = local_candidate_score(name, searchable, slot, task, scan, source_kind)
            if not score:
                continue
            candidates[slot.key].append(
                {
                    "skill": name,
                    "team_id": team_id,
                    "team_name": team_name,
                    "team_path": str(path.parent),
                    "source": str(path),
                    "source_kind": source_kind,
                    "availability": "local-ready",
                    "local_path": str(path),
                    "score": score,
                    "matched_terms": matched_terms,
                    "verification": {
                        "status": "local-ready",
                        "path": str(path),
                        "declared_name": frontmatter_value(content, "name") or name,
                    },
                }
            )

    for root, root_kind in skill_roots:
        if root.is_dir():
            discovered["roots"].append({"kind": root_kind, "path": str(root)})
        for path, name, description, content in local_skill_files(root):
            discovered["skills"] += 1
            team_like = root_kind == "project-skill" and (
                path.parent.name.endswith("-team") or "expert-team" in path.parent.name
            )
            source_kind = "project-expert-team" if team_like else root_kind
            add_local_item(path, name, description, content, source_kind, path.parent.name, path.parent.name)

    for root, root_kind in agent_roots:
        if root.is_dir():
            discovered["roots"].append({"kind": root_kind, "path": str(root)})
        for path, name, description, content in local_agent_files(root):
            discovered["agents"] += 1
            add_local_item(path, name, description, content, root_kind, path.parent.name, path.parent.name)

    for path in iter_project_files(project_root):
        if path.name != "plugin.json":
            continue
        try:
            data = json.loads(safe_read(path, 100000))
        except json.JSONDecodeError:
            continue
        if data.get("expertType") != "team" and not data.get("teamInfo"):
            continue
        discovered["expert_teams"] += 1
        name = data.get("name") or data.get("plugin") or path.parent.name
        display_name = data.get("displayName")
        if isinstance(display_name, dict):
            display_name = " / ".join(str(value) for value in display_name.values())
        team_name = str(display_name or name)
        add_local_item(path, str(name), team_name, json.dumps(data, ensure_ascii=False), "project-expert-team", str(name), team_name)

    for key in candidates:
        candidates[key].sort(key=lambda item: (-item["score"], item["skill"], item["source"]))
    return candidates, discovered


def candidate_score(skill_name: str, team: Any, slot: Slot, task: str, scan: dict[str, Any]) -> int:
    lowered = skill_name.lower()
    query = f"{task} {' '.join(scan['stack'])} {' '.join(scan['affected_files'])}".lower()
    score = team.score
    if skill_name in slot.preferred:
        score += 30 - slot.preferred.index(skill_name) * 3
    if any(keyword.lower() in lowered for keyword in slot.keywords):
        score += 12
    if any(keyword.lower() in query for keyword in slot.keywords):
        score += 2
    if slot.key == "e2e-testing" and scan["signals"]["has_browser_tooling"]:
        score += 8
    if slot.key == "api-testing" and scan["signals"]["has_api"]:
        score += 8
    if slot.key == "api-testing" and scan["signals"]["has_mocks"] and skill_name == "qa-api-tester":
        score += 8
    return score


def build_candidates(entries: list[Any], task: str, scan: dict[str, Any], local_mode: bool) -> dict[str, list[dict[str, Any]]]:
    candidates: dict[str, list[dict[str, Any]]] = {slot.key: [] for slot in SLOTS}
    for team in entries:
        children = team.available_child_skills if local_mode else team.child_skills
        source_by_name = dict(zip(team.child_skills, team.child_skill_sources))
        for child in children:
            for slot in SLOTS:
                child_text = child.lower()
                team_text = f"{team.team_id} {team.router_name} {team.display_name}".lower()
                direct_match = (
                    child in slot.preferred
                    or any(keyword.lower() in child_text for keyword in slot.keywords)
                    or any(keyword.lower() in team_text for keyword in slot.keywords)
                )
                if not direct_match:
                    continue
                score = candidate_score(child, team, slot, task, scan)
                if score <= team.score:
                    continue
                candidates[slot.key].append(
                    {
                        "skill": child,
                        "team_id": team.team_id,
                        "team_name": team.display_name,
                        "team_path": team.path,
                        "source": source_by_name.get(child),
                        "source_kind": "catalog-local" if local_mode else "remote-catalog",
                        "availability": "catalog-local" if local_mode else "remote",
                        "score": score,
                        "matched_terms": list(team.matched_terms),
                    }
                )
    for key in candidates:
        candidates[key].sort(key=lambda item: (-item["score"], item["skill"]))
    return candidates


def merge_candidates(
    local_candidates: dict[str, list[dict[str, Any]]],
    catalog_candidates: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    merged: dict[str, list[dict[str, Any]]] = {}
    for slot in SLOTS:
        key = slot.key
        # Local candidates are intentionally placed first. Their score still
        # orders local options, while remote entries only fill local gaps.
        merged[key] = local_candidates.get(key, []) + catalog_candidates.get(key, [])
    return merged


def verify_skill(source: str | None, expected_name: str, local_mode: bool, timeout: float, catalog_root: Path | None = None) -> dict[str, Any]:
    if not source:
        return {"status": "missing-source", "expected_name": expected_name}
    try:
        if local_mode:
            if catalog_root is None:
                raise OSError("local catalog root is not configured")
            text = (catalog_root / source).read_text(encoding="utf-8")
        else:
            text = discover.fetch_text(source, timeout)
    except (OSError, ValueError) as error:
        return {"status": "unverified", "expected_name": expected_name, "error": str(error)}
    frontmatter = text.split("---", 2)[1] if text.startswith("---") and "---" in text[3:] else ""
    name_match = re.search(r"^name:\s*[\"']?([^\"'\s]+)", frontmatter, re.MULTILINE)
    valid_name = bool(name_match and name_match.group(1) == expected_name)
    return {
        "status": "verified" if valid_name and len(text.strip()) > 80 else "invalid",
        "expected_name": expected_name,
        "declared_name": name_match.group(1) if name_match else None,
        "content_bytes": len(text.encode("utf-8")),
    }


def verify_candidate(
    candidate: dict[str, Any], local_mode: bool, timeout: float, catalog_root: Path
) -> dict[str, Any]:
    if candidate.get("source_kind") in LOCAL_SOURCE_KINDS:
        return candidate.get("verification") or {
            "status": "local-ready",
            "path": candidate.get("local_path") or candidate.get("source"),
        }
    return verify_skill(candidate.get("source"), candidate["skill"], local_mode, timeout, catalog_root)


def choose_roster(
    candidates: dict[str, list[dict[str, Any]]], task: str, scan: dict[str, Any], mode: str, local_mode: bool, catalog_root: Path, timeout: float, max_members: int, verify: bool
) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    for slot in SLOTS:
        if not slot_is_required(slot, task, scan, mode):
            continue
        options = candidates[slot.key]
        if not options:
            continue
        selected = dict(options[0])
        verification = {"status": "skipped"}
        if verify:
            fallback_verification = verify_candidate(options[0], local_mode, timeout, catalog_root)
            verification = fallback_verification
            if fallback_verification["status"] not in {"verified", "local-ready"}:
                for option in options[1:]:
                    candidate_verification = verify_candidate(option, local_mode, timeout, catalog_root)
                    if candidate_verification["status"] in {"verified", "local-ready"}:
                        selected = dict(option)
                        verification = candidate_verification
                        break
        if verify and verification["status"] not in {"verified", "local-ready"}:
            continue
        selected.update(
            {
                "id": f"{slot.key}-specialist",
                "slot": slot.key,
                "role": {"en": slot.role_en, "zh": slot.role_zh},
                "responsibility": {"en": slot.description_en, "zh": slot.description_zh},
                "selection_evidence": {
                    "score": selected.pop("score"),
                    "matched_terms": selected.pop("matched_terms"),
                    "project_signals": [key for key, value in scan["signals"].items() if value],
                },
                "verification": verification,
            }
        )
        chosen.append(selected)

    if not chosen and candidates["unit-testing"]:
        selected = dict(candidates["unit-testing"][0])
        fallback_verification = verify_candidate(selected, local_mode, timeout, catalog_root) if verify else {"status": "skipped"}
        if not verify or fallback_verification["status"] in {"verified", "local-ready"}:
            selected.update({"id": "quality-specialist", "slot": "unit-testing", "role": {"en": "Quality specialist", "zh": "质量专家"}, "responsibility": {"en": "Produce an evidence-based quality assessment.", "zh": "产出基于证据的质量评估。"}, "selection_evidence": {"score": selected.pop("score"), "matched_terms": selected.pop("matched_terms"), "project_signals": []}, "verification": fallback_verification})
            chosen.append(selected)
    return chosen[:max_members]


def prompt_for_member(member: dict[str, Any], project_root: str, task: str, mode: str, scan: dict[str, Any]) -> str:
    evidence = ", ".join(scan["affected_files"][:12]) or "start from repository instructions and manifests"
    return f"""You are {member['role']['en']} ({member['role']['zh']}) in an automatically composed project team.

Project: {project_root}
Task: {task}
Mode: {mode}
Assigned capability: {member['skill']}
Responsibility: {member['responsibility']['en']} {member['responsibility']['zh']}

Inspect the repository before making claims. Begin with AGENTS.md or equivalent instructions, then inspect these likely affected paths: {evidence}.
Return a concise structured result with: confirmed facts, assumptions, findings, files or commands inspected, recommendation or changes, verification evidence, blockers, and a handoff for the lead.
In auto-execute mode, change only files required by your assignment and report every changed path. In blueprint or package mode, do not modify the target project.
Send the result to the coordinator through the runtime's member-to-lead message primitive (SendMessage, or the Codex equivalent); do not claim a message was sent when that primitive is unavailable."""


def compose_phases(roster: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    by_slot = {member["slot"]: member["id"] for member in roster}
    phases: list[dict[str, Any]] = []
    if "requirements" in by_slot:
        phases.append({"id": "phase-1-contract", "name": {"en": "Contract and acceptance", "zh": "需求契约与验收"}, "members": [by_slot["requirements"]], "depends_on": [], "parallel": False, "input": "user task and project scan", "output": "behavior, scope, acceptance criteria, open questions", "gate": "No downstream work starts until the acceptance contract is explicit."})
    foundation = [by_slot[key] for key in ("architecture", "implementation") if key in by_slot]
    if foundation:
        phases.append({"id": "phase-2-foundation", "name": {"en": "Design and implementation plan", "zh": "设计与实现方案"}, "members": foundation, "depends_on": ["phase-1-contract"] if phases else [], "parallel": len(foundation) > 1, "input": "acceptance contract and project evidence", "output": "impact analysis, implementation plan, risks", "gate": "Plan must name affected files, rollback or containment, and verification approach."})
    validation = [by_slot[key] for key in ("unit-testing", "api-testing", "e2e-testing") if key in by_slot]
    if validation:
        phases.append({"id": "phase-3-validation", "name": {"en": "Validation and evidence", "zh": "验证与证据"}, "members": validation, "depends_on": [phase["id"] for phase in phases[-2:]], "parallel": len(validation) > 1, "input": "contract, implementation/design result, and affected paths", "output": "test plan or results, API/UI evidence, blockers", "gate": "Each failure is classified as product bug, test defect, environment blocker, or data issue."})
    if "review" in by_slot:
        phases.append({"id": "phase-4-review", "name": {"en": "Quality decision and handoff", "zh": "质量裁决与交付"}, "members": [by_slot["review"]], "depends_on": [phase["id"] for phase in phases], "parallel": False, "input": "all member reports and verification evidence", "output": "accept/rework decision, residual risks, final handoff", "gate": "Lead integrates only after the quality decision is recorded."})
    return phases


def build_query(task: str, scan: dict[str, Any]) -> str:
    signal_terms = [key for key, value in scan["signals"].items() if value]
    routing_terms = []
    if not re.search(r"acceptance|验收标准|明确要求|已确定|spec locked|范围明确", task.lower()):
        routing_terms.append("requirements")
    if scan["signals"]["has_api"] or scan["signals"]["has_mocks"]:
        routing_terms.append("api testing")
    if scan["signals"]["has_routes"]:
        routing_terms.append("user journey")
    if re.search(r"review|audit|quality|risk|审查|审计|质量|风险", task.lower()):
        routing_terms.append("code review")
    # A long list of repository paths can dominate index ranking with unrelated
    # words from filenames. The selected member prompt already carries paths.
    return " ".join([task, " ".join(scan["stack"]), " ".join(signal_terms), " ".join(routing_terms)])


def compose(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.project_root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Project root does not exist or is not a directory: {args.project_root}")
    if args.max_members < 1 or args.max_members > 8:
        raise ValueError("--max-members must be between 1 and 8")
    if args.candidate_limit < 1:
        raise ValueError("--candidate-limit must be greater than zero")
    mode = normalize_mode(args.mode)
    scan = scan_project(root, args.task)
    catalog_root = Path(args.catalog_root).expanduser().resolve()
    default_skill_roots, default_agent_roots = default_local_roots(root)
    skill_roots = default_skill_roots + [
        (Path(value).expanduser(), "installed-skill") for value in (args.skill_roots or [])
    ]
    agent_roots = default_agent_roots + [
        (Path(value).expanduser(), "installed-agent") for value in (args.agent_roots or [])
    ]
    if args.no_local:
        skill_roots = []
        agent_roots = []
    else:
        skill_roots = dedupe_roots(skill_roots)
        agent_roots = dedupe_roots(agent_roots)
    local_candidates, local_discovery = discover_local_candidates(
        root, args.task, scan, skill_roots, agent_roots
    )
    if args.index:
        index_path = discover.resolve_index(catalog_root, args.index)
        entries = discover.rank(discover.read_local_index(catalog_root, index_path), build_query(args.task, scan))
        index_source = index_path.relative_to(catalog_root).as_posix()
        local_mode = True
    else:
        index_source = discover.normalize_index_url(args.index_url)
        entries = discover.rank(discover.read_remote_index(index_source, args.timeout), build_query(args.task, scan))
        local_mode = False
    candidate_entries = entries[: args.candidate_limit]
    catalog_candidates = build_candidates(candidate_entries, args.task, scan, local_mode)
    required_slots = {
        slot.key for slot in SLOTS if slot_is_required(slot, args.task, scan, mode)
    }
    if any(not catalog_candidates[key] for key in required_slots):
        # Keep normal routing focused, but search the complete index when a
        # required capability was absent from the top-ranked teams.
        all_candidates = build_candidates(entries, args.task, scan, local_mode)
        for key in required_slots:
            if not catalog_candidates[key]:
                catalog_candidates[key] = all_candidates[key]
    candidates = merge_candidates(local_candidates, catalog_candidates)
    roster = choose_roster(candidates, args.task, scan, mode, local_mode, catalog_root, args.timeout, args.max_members, not args.skip_verify)
    for member in roster:
        member["prompt"] = prompt_for_member(member, str(root), args.task, mode, scan)

    phases = compose_phases(roster, mode)
    selected_skills = {member["skill"] for member in roster}
    rejected = []
    for slot in SLOTS:
        if slot_is_required(slot, args.task, scan, mode) and slot.key not in {member["slot"] for member in roster}:
            rejected.append({"slot": slot.key, "reason": "no indexed candidate or max-members limit"})
    remote_selected = [member["skill"] for member in roster if member.get("source_kind") == "remote-catalog"]
    local_selected = [member["skill"] for member in roster if member.get("source_kind") in LOCAL_SOURCE_KINDS]
    prerequisites = []
    if remote_selected:
        prerequisites.append("remote access to selected SKILL.md sources")
    if local_selected:
        prerequisites.append("local Skill or Agent files are readable")
    prerequisites.append("project-specific credentials, services, test data, and browser runner when required")
    return {
        "schema": "expert-team-composition.v1",
        "project": {"root": str(root), "task": args.task, "mode": mode},
        "catalog": {
            "index": index_source,
            "local": local_mode,
            "selection_policy": "project expert team > project/local Skill or Agent > verified catalog capability",
            "local_discovery": local_discovery,
            "local_selected": local_selected,
            "remote_selected": remote_selected,
        },
        "scan": scan,
        "query": build_query(args.task, scan),
        "roster": roster,
        "phases": phases,
        "handoff": {"lead": "coordinator", "member_report_format": ["facts", "assumptions", "findings", "evidence", "changes", "verification", "blockers", "handoff"], "integration_rule": "The coordinator owns cross-member synthesis and final acceptance."},
        "runtime": {"formal_team": "Use TeamCreate once, then spawn Agent members and collect SendMessage reports by phase when those primitives exist.", "codex_fallback": "Use spawn_agent, send_input, wait_agent, and resume_agent equivalents when available; otherwise execute the same prompts as one coordinator and label the result as coordinated capability execution.", "installation": "never install or copy selected skills into the target project", "avatars": "omitted by design"},
        "selected_skills": sorted(selected_skills),
        "rejected_or_missing_slots": rejected,
        "prerequisites": prerequisites,
    }


def render_markdown(result: dict[str, Any]) -> str:
    project = result["project"]
    lines = [
        "# 自动专家团编排结果 / Automatic Expert-Team Composition",
        "",
        f"- Project / 项目: `{project['root']}`",
        f"- Task / 任务: {project['task']}",
        f"- Mode / 模式: `{project['mode']}`",
        f"- Catalog / 能力目录: `{result['catalog']['index']}`",
        "",
        "## Roster / 成员",
        "",
        "| ID | Role / 角色 | Skill | Source kind / 来源 | Source / 地址 | Verification / 校验 |",
        "|---|---|---|---|---|---|",
    ]
    for member in result["roster"]:
        lines.append(f"| `{member['id']}` | {member['role']['en']} / {member['role']['zh']} | `{member['skill']}` | `{member.get('source_kind', 'unknown')}` | `{member['source']}` | `{member['verification']['status']}` |")
    lines.extend(["", "## Phases / 阶段", ""])
    for phase in result["phases"]:
        lines.append(f"- **{phase['id']}** {phase['name']['en']} / {phase['name']['zh']}: `{', '.join(phase['members'])}`; depends on `{', '.join(phase['depends_on']) or 'none'}`; gate: {phase['gate']}")
    lines.extend(["", "## Runtime / 运行时", "", result["runtime"]["formal_team"], result["runtime"]["codex_fallback"], "", "Avatars are omitted by design. / 按要求不生成头像资源。", ""])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        result = compose(args)
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from error
    if args.format == "markdown":
        print(render_markdown(result), end="\n")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
