#!/usr/bin/env python3
"""Search the repository's expert-team index without external dependencies."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_CATALOG_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INDEX_URL = "https://github.com/whyzsm/tiny-agents/tree/main/indexes"
INDEX_FILENAME = "expert-team-file-list.md"
WORD_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9+.#_-]*|[\u4e00-\u9fff]+")
TEAM_ROW_RE = re.compile(
    r"^\|\s*(?P<category>[^|]+?)\s*"
    r"\|\s*\[`?(?P<team_id>[^]`]+)`?\]\((?P<link>[^)]+)\)\s*"
    r"\|\s*(?P<display_name>[^|]+?)\s*"
    r"\|\s*(?P<children>.*?)\s*\|\s*$"
)

CONCEPT_ALIASES = {
    "requirements": {
        "acceptance",
        "prd",
        "requirement",
        "requirements",
        "scope",
        "spec",
        "验收",
        "澄清",
        "范围",
        "需求",
    },
    "architecture": {
        "adr",
        "architecture",
        "migration",
        "system-design",
        "架构",
        "方案",
        "迁移",
        "系统设计",
    },
    "implementation": {
        "backend",
        "build",
        "code",
        "frontend",
        "implement",
        "implementation",
        "refactor",
        "开发",
        "实现",
        "前端",
        "后端",
        "编码",
        "重构",
    },
    "testing": {
        "api-test",
        "coverage",
        "e2e",
        "integration",
        "qa",
        "quality",
        "regression",
        "test",
        "testing",
        "unit",
        "回归",
        "测试",
        "覆盖率",
        "质量",
        "验证",
        "验收",
    },
    "review": {"audit", "code-review", "critique", "review", "审查", "审计", "评审"},
    "security": {
        "auth",
        "compliance",
        "credential",
        "privacy",
        "secret",
        "security",
        "安全",
        "权限",
        "合规",
        "认证",
        "隐私",
    },
    "debugging": {
        "bug",
        "debug",
        "diagnose",
        "error",
        "fix",
        "troubleshoot",
        "修复",
        "排查",
        "故障",
        "错误",
    },
    "delivery": {
        "ci",
        "cd",
        "deploy",
        "delivery",
        "operations",
        "release",
        "上线",
        "交付",
        "发布",
        "运维",
        "部署",
    },
    "accessibility": {
        "a11y",
        "accessibility",
        "aria",
        "keyboard",
        "screen-reader",
        "wcag",
        "可访问性",
        "无障碍",
        "键盘导航",
    },
    "documentation": {"api-doc", "documentation", "docs", "handoff", "readme", "文档", "说明"},
}

CONCEPT_TARGETS = {
    "requirements": {
        "acceptance",
        "prd",
        "requirement",
        "requirements",
        "验收",
        "澄清",
        "需求",
    },
    "architecture": {"adr", "architecture", "migration", "system-design", "架构", "迁移", "系统设计"},
    "implementation": {
        "backend",
        "frontend",
        "implement",
        "implementation",
        "refactor",
        "开发",
        "实现",
        "前端",
        "后端",
        "重构",
    },
    "testing": {
        "coverage",
        "e2e",
        "integration",
        "qa",
        "regression",
        "test",
        "testing",
        "unit",
        "回归",
        "测试",
        "覆盖率",
        "验证",
    },
    "review": {"audit", "code-review", "review", "审查", "审计", "评审"},
    "security": {"auth", "compliance", "privacy", "security", "安全", "权限", "合规", "认证", "隐私"},
    "debugging": {"bug", "debug", "diagnose", "error", "troubleshoot", "修复", "排查", "故障", "错误"},
    "delivery": {"deploy", "delivery", "operations", "release", "上线", "交付", "发布", "运维", "部署"},
    "accessibility": {"a11y", "accessibility", "aria", "screen-reader", "wcag", "可访问性", "无障碍"},
    "documentation": {"api-doc", "documentation", "docs", "runbook", "文档", "说明"},
}

QUERY_TRANSLATIONS = {
    "需求澄清": {"requirement", "requirements"},
    "需求分析": {"requirement", "requirements"},
    "单元测试": {"test", "unit"},
    "集成测试": {"integration", "test"},
    "端到端测试": {"e2e", "test"},
    "接口测试": {"api", "test"},
    "回归测试": {"regression", "test"},
    "回归验证": {"regression", "verification"},
    "代码审查": {"code-review", "review"},
    "安全审计": {"security", "security-audit"},
    "无障碍": {"accessibility", "wcag"},
}

STOP_TERMS = {
    "a",
    "an",
    "and",
    "for",
    "in",
    "of",
    "on",
    "project",
    "repository",
    "skill",
    "the",
    "to",
    "with",
    "专家",
    "团队",
    "技能",
    "项目",
}


@dataclass(frozen=True)
class TeamEntry:
    category: str
    team_id: str
    router_name: str
    display_name: str
    path: str
    path_exists: bool | None
    child_skills: tuple[str, ...]
    child_entry_mode: str
    top_level_child_skills: tuple[str, ...]
    internal_child_labels: tuple[str, ...]
    available_child_skills: tuple[str, ...]
    unverified_child_skills: tuple[str, ...]
    child_skill_sources: tuple[str, ...]
    score: int = 0
    matched_terms: tuple[str, ...] = ()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search expert teams and child skills declared in expert-team-file-list.md."
    )
    parser.add_argument(
        "--catalog-root",
        default=str(DEFAULT_CATALOG_ROOT),
        help="Capability repository root (default: inferred from this script)",
    )
    parser.add_argument(
        "--index",
        help="Use a local index path instead of the default remote index",
    )
    parser.add_argument(
        "--index-url",
        default=DEFAULT_INDEX_URL,
        help="GitHub tree/blob, raw file, or HTTP(S) directory URL",
    )
    parser.add_argument("--timeout", type=float, default=15.0, help="Remote read timeout in seconds")
    parser.add_argument("--query", default="", help="Target project, task, risks, and deliverable")
    parser.add_argument("--limit", type=int, default=20, help="Maximum teams; use 0 for all")
    parser.add_argument(
        "--format", choices=("json", "markdown"), default="json", help="Output format"
    )
    return parser.parse_args()


def resolve_index(catalog_root: Path, index_arg: str) -> Path:
    index = Path(index_arg).expanduser()
    return index.resolve() if index.is_absolute() else (catalog_root / index).resolve()


def normalize_index_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Index URL must use HTTP(S): {value}")

    parts = [part for part in parsed.path.split("/") if part]
    if parsed.netloc.lower() == "github.com" and len(parts) >= 4:
        owner, repository, marker, branch, *remainder = parts
        if marker in {"tree", "blob"}:
            if not remainder or not remainder[-1].endswith(".md"):
                remainder.append(INDEX_FILENAME)
            raw_path = "/".join([owner, repository, branch, *remainder])
            return f"https://raw.githubusercontent.com/{raw_path}"

    if parsed.path.endswith(".md"):
        return value
    return value.rstrip("/") + f"/{INDEX_FILENAME}"


def fetch_text(url: str, timeout: float) -> str:
    request = Request(url, headers={"User-Agent": "tiny-agents-expert-team-index/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            encoding = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(encoding)
    except (HTTPError, URLError, TimeoutError, UnicodeDecodeError) as error:
        raise ValueError(f"Cannot read remote expert-team index: {url}: {error}") from error


def catalog_path(catalog_root: Path, index: Path, link: str) -> tuple[str, bool]:
    target = (index.parent / link).resolve()
    try:
        relative = target.relative_to(catalog_root)
    except ValueError as error:
        raise ValueError(f"Index link escapes the catalog root: {link}") from error
    return relative.as_posix(), target.is_file()


def classify_child_skills(
    catalog_root: Path, child_skills: tuple[str, ...]
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    available: list[str] = []
    unresolved: list[str] = []
    for name in child_skills:
        if (catalog_root / "skills" / name / "SKILL.md").is_file():
            available.append(name)
        else:
            unresolved.append(name)
    return tuple(available), tuple(unresolved)


def child_entry_mode(top_level: tuple[str, ...], internal_labels: tuple[str, ...]) -> str:
    if top_level and internal_labels:
        return "hybrid"
    if top_level:
        return "all-top-level-skills"
    return "internal-router-labels"


def remote_child_sources(index_url: str, child_skills: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        urljoin(index_url, f"../skills/{quote(name)}/SKILL.md") for name in child_skills
    )


def parse_index(
    lines: list[str],
    catalog_root: Path | None,
    index_path: Path | None,
    index_url: str | None,
) -> list[TeamEntry]:
    entries: list[TeamEntry] = []
    for line in lines:
        match = TEAM_ROW_RE.match(line)
        if not match:
            continue
        child_skills = tuple(re.findall(r"`([^`]+)`", match.group("children")))
        if catalog_root is not None and index_path is not None:
            path, path_exists = catalog_path(
                catalog_root, index_path, match.group("link").strip()
            )
            available, unresolved = classify_child_skills(catalog_root, child_skills)
            mode = child_entry_mode(available, unresolved)
            child_sources = tuple(f"skills/{name}/SKILL.md" for name in child_skills)
        elif index_url is not None:
            path = urljoin(index_url, match.group("link").strip())
            path_exists = None
            mode = "unverified"
            available = ()
            unresolved = child_skills
            child_sources = remote_child_sources(index_url, child_skills)
        else:
            raise ValueError("Index source is not configured")
        entries.append(
            TeamEntry(
                category=match.group("category").strip(),
                team_id=match.group("team_id").strip(),
                router_name=Path(path).parent.name,
                display_name=match.group("display_name").strip(),
                path=path,
                path_exists=path_exists,
                child_skills=child_skills,
                child_entry_mode=mode,
                top_level_child_skills=available,
                internal_child_labels=unresolved if mode != "unverified" else (),
                available_child_skills=available,
                unverified_child_skills=unresolved,
                child_skill_sources=child_sources,
            )
        )

    if not entries:
        raise ValueError("No expert-team rows found in the configured index")
    return entries


def read_local_index(catalog_root: Path, index: Path) -> list[TeamEntry]:
    try:
        lines = index.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise ValueError(f"Cannot read expert-team index: {index}") from error
    return parse_index(lines, catalog_root, index, None)


def read_remote_index(index_url: str, timeout: float) -> list[TeamEntry]:
    text = fetch_text(index_url, timeout)
    return parse_index(text.splitlines(), None, None, index_url)


def query_model(query: str) -> tuple[set[str], set[str]]:
    normalized = query.lower()
    terms = {term.lower() for term in WORD_RE.findall(normalized)}
    for phrase, translations in QUERY_TRANSLATIONS.items():
        if phrase in normalized:
            terms.update(translations)

    concepts: set[str] = set()
    for concept, aliases in CONCEPT_ALIASES.items():
        direct_aliases = {alias for alias in aliases if alias in normalized or alias in terms}
        if direct_aliases:
            concepts.add(concept)
            terms.update(direct_aliases)
    return (
        {term for term in terms if len(term) > 1 and term not in STOP_TERMS},
        concepts,
    )


def contains_term(text: str, term: str) -> bool:
    if term.isascii():
        return bool(
            re.search(
                rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])",
                text,
                flags=re.IGNORECASE,
            )
        )
    return term in text


def rank(entries: list[TeamEntry], query: str) -> list[TeamEntry]:
    if not query.strip():
        return sorted(entries, key=lambda entry: (entry.category, entry.team_id))

    terms, concepts = query_model(query)
    ranked: list[TeamEntry] = []
    normalized_query = " ".join(query.lower().split())
    for entry in entries:
        identity = f"{entry.team_id} {entry.router_name}".lower()
        display = entry.display_name.lower()
        category = entry.category.lower()
        children = " ".join(entry.child_skills).lower()
        combined = f"{identity} {display} {category} {children}"

        identity_matches = {term for term in terms if contains_term(identity, term)}
        display_matches = {term for term in terms if contains_term(display, term)}
        child_matches = {term for term in terms if contains_term(children, term)}
        category_matches = {term for term in terms if contains_term(category, term)}
        concept_matches = {
            concept
            for concept in concepts
            if any(contains_term(combined, target) for target in CONCEPT_TARGETS[concept])
        }
        matched = identity_matches | display_matches | child_matches | category_matches
        score = (
            len(identity_matches) * 5
            + len(display_matches) * 4
            + len(child_matches) * 3
            + len(category_matches)
            + len(concept_matches) * 3
        )
        if normalized_query and normalized_query in combined:
            score += 8
        if score:
            ranked.append(
                TeamEntry(
                    category=entry.category,
                    team_id=entry.team_id,
                    router_name=entry.router_name,
                    display_name=entry.display_name,
                    path=entry.path,
                    path_exists=entry.path_exists,
                    child_skills=entry.child_skills,
                    child_entry_mode=entry.child_entry_mode,
                    top_level_child_skills=entry.top_level_child_skills,
                    internal_child_labels=entry.internal_child_labels,
                    available_child_skills=entry.available_child_skills,
                    unverified_child_skills=entry.unverified_child_skills,
                    child_skill_sources=entry.child_skill_sources,
                    score=score,
                    matched_terms=tuple(
                        sorted(matched | {f"concept:{concept}" for concept in concept_matches})
                    ),
                )
            )
    return sorted(ranked, key=lambda entry: (-entry.score, entry.category, entry.team_id))


def render_markdown(entries: list[TeamEntry], query: str, index_path: str) -> str:
    lines = [
        "# Expert Team Candidates",
        "",
        f"Index: `{index_path}`",
        f"Query: `{query or '(none)'}`",
        "",
        "| Score | Category | Team | Name | Mode | Top-level child skills | Internal labels / Unverified | Path |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for entry in entries:
        available = ", ".join(f"`{skill}`" for skill in entry.top_level_child_skills) or "-"
        internal = entry.internal_child_labels or entry.unverified_child_skills
        unresolved = ", ".join(f"`{skill}`" for skill in internal) or "-"
        if entry.path.startswith(("http://", "https://")):
            source = f"[SKILL.md]({entry.path})"
        else:
            source = f"`{entry.path}`"
        missing = " (missing)" if entry.path_exists is False else ""
        lines.append(
            f"| {entry.score} | {entry.category} | `{entry.router_name}` | "
            f"{entry.display_name} | `{entry.child_entry_mode}` | {available} | {unresolved} | {source}{missing} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    catalog_root = Path(args.catalog_root).expanduser().resolve()
    if args.index and not catalog_root.is_dir():
        raise SystemExit(f"Catalog root does not exist or is not a directory: {args.catalog_root}")
    if args.limit < 0:
        raise SystemExit("--limit must be zero or greater")
    if args.timeout <= 0:
        raise SystemExit("--timeout must be greater than zero")

    try:
        if args.index:
            index = resolve_index(catalog_root, args.index)
            entries = rank(read_local_index(catalog_root, index), args.query)
            index_source = index.relative_to(catalog_root).as_posix()
        else:
            index_source = normalize_index_url(args.index_url)
            entries = rank(read_remote_index(index_source, args.timeout), args.query)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if args.limit:
        entries = entries[: args.limit]

    if args.format == "markdown":
        print(render_markdown(entries, args.query, index_source), end="")
    else:
        print(
            json.dumps(
                {
                    "index": index_source,
                    "query": args.query,
                    "count": len(entries),
                    "teams": [asdict(entry) for entry in entries],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
