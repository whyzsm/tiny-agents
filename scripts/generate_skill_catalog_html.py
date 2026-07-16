from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "indexes" / "skill-catalog.html"

CATEGORY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("技术", ("tech-", "code", "programming", "developer", "frontend", "backend", "api", "devops", "docker", "kubernetes", "github", "git", "mcp", "cloud", "harmony", "arkui")),
    ("腾讯专区", ("tencent", "cloudbase", "wechat", "miniprogram", "微信", "腾讯")),
    ("设计", ("design", "ui-", "ux-", "visual", "brand", "prototype", "wireframe", "poster", "figma", "logo")),
    ("金融", ("finance", "financial", "stock", "quant", "risk", "投资", "财报", "股票", "量化")),
    ("数据智能", ("data", "analytics", "analysis", "research", "dashboard", "sql", "rag", "report")),
    ("游戏空间", ("game", "unity", "游戏")),
    ("营销增长", ("marketing", "growth", "ad-", "campaign", "copywriter", "seo", "social", "funnel")),
    ("销售商务", ("sales", "proposal", "presales", "business-development", "deal", "pipeline")),
    ("法律", ("legal", "contract", "compliance", "law", "litigation", "nda")),
    ("学术", ("academic", "paper", "citation", "literature", "thesis", "论文", "文献")),
    ("教育", ("education", "exam", "teacher", "student", "quiz", "lesson", "training", "gaokao", "study")),
    ("运营人力", ("ops-", "operation", "recruit", "resume", "interview", "hr-", "meeting", "weekly")),
    ("医疗健康", ("medical", "health", "clinic", "emr", "nursing", "病历", "健康")),
    ("电商零售", ("ecommerce", "retail", "1688", "amazon", "shop", "product-selection", "supply")),
    ("内容媒体", ("video", "audio", "image", "media", "ppt", "slides", "document", "writing", "writer")),
    ("项目质量", ("project", "quality", "testing", "test-", "qa-", "workflow")),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="generate_skill_catalog_html",
        description="Generate a static searchable HTML catalog from skill indexes.",
    )
    parser.add_argument("--project-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    project_root = args.project_root.expanduser().resolve()
    output_path = args.output.expanduser()
    if not output_path.is_absolute():
        output_path = project_root / output_path

    registry = _read_json(project_root / "indexes" / "skill-registry.json")
    skill_entries = registry.get("entries", [])
    if not isinstance(skill_entries, list):
        raise ValueError("indexes/skill-registry.json must contain an entries array")

    skill_by_name = {
        str(entry.get("name")): entry
        for entry in skill_entries
        if isinstance(entry, dict) and entry.get("name")
    }
    skill_by_entry = {
        str(entry.get("entry_path")): entry
        for entry in skill_entries
        if isinstance(entry, dict) and entry.get("entry_path")
    }

    teams = _parse_expert_teams(
        project_root / "indexes" / "expert-team-file-list.md",
        skill_by_name=skill_by_name,
        skill_by_entry=skill_by_entry,
    )
    team_entry_paths = {team["entry_path"] for team in teams if team.get("entry_path")}
    child_categories = _categories_by_child_skill(teams, skill_by_name)
    category_order = _category_order(teams)

    skills = [
        _skill_record(entry, child_categories, category_order)
        for entry in skill_entries
        if isinstance(entry, dict) and str(entry.get("entry_path")) not in team_entry_paths
    ]

    payload = {
        "generatedAt": _now(),
        "source": {
            "skillRegistry": "indexes/skill-registry.json",
            "expertTeamList": "indexes/expert-team-file-list.md",
        },
        "stats": {
            "skills": len(skills),
            "expertTeams": len(teams),
            "allRegistryEntries": len(skill_entries),
        },
        "categoryOrder": category_order,
        "skills": skills,
        "teams": teams,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_html(payload), encoding="utf-8")
    print(
        f"Wrote {output_path.relative_to(project_root)} "
        f"({len(skills)} skills, {len(teams)} expert teams)"
    )
    return 0


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_expert_teams(
    path: Path,
    *,
    skill_by_name: dict[str, dict[str, Any]],
    skill_by_entry: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    teams: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| 分类"):
            continue
        cells = _split_markdown_table_row(line)
        if len(cells) < 4:
            continue

        category = _clean_cell(cells[0])
        team_cell = cells[1]
        link_match = re.search(r"\[(`?)([^`\]]+)\1\]\(([^)]+)\)", team_cell)
        if not link_match:
            continue

        slug = link_match.group(2).strip()
        href = link_match.group(3).strip()
        entry_path = _normalize_entry_path(href)
        registry_entry = skill_by_entry.get(entry_path, {})
        child_names = re.findall(r"`([^`]+)`", cells[3])
        children = []
        top_level_count = 0
        for name in child_names:
            skill = skill_by_name.get(name)
            if skill:
                top_level_count += 1
            children.append(
                {
                    "name": name,
                    "isTopLevel": bool(skill),
                    "path": _entry_link(skill.get("entry_path")) if skill else "",
                }
            )

        teams.append(
            {
                "slug": slug,
                "displayName": _clean_cell(cells[2]) or slug,
                "category": category or "其他",
                "primaryCategory": category or "其他",
                "description": _clean_text(str(registry_entry.get("description") or "")),
                "purpose": _clean_text(str(registry_entry.get("purpose") or "")),
                "path": href,
                "entry_path": entry_path,
                "children": children,
                "childCount": len(children),
                "topLevelChildCount": top_level_count,
            }
        )
    return teams


def _split_markdown_table_row(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]

    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in body:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    cells.append("".join(current).strip())
    return cells


def _normalize_entry_path(href: str) -> str:
    return href.replace("../", "").lstrip("./")


def _entry_link(entry_path: Any) -> str:
    if not entry_path:
        return ""
    return "../" + str(entry_path).lstrip("./")


def _categories_by_child_skill(
    teams: list[dict[str, Any]],
    skill_by_name: dict[str, dict[str, Any]],
) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = defaultdict(list)
    for team in teams:
        category = str(team.get("category") or "其他")
        for child in team.get("children", []):
            name = str(child.get("name") or "")
            if name in skill_by_name and category not in mapping[name]:
                mapping[name].append(category)
    return dict(mapping)


def _category_order(teams: list[dict[str, Any]]) -> list[str]:
    order: list[str] = []
    for team in teams:
        category = str(team.get("category") or "其他")
        if category not in order:
            order.append(category)
    for category, _tokens in CATEGORY_RULES:
        if category not in order:
            order.append(category)
    if "其他" not in order:
        order.append("其他")
    return order


def _skill_record(
    entry: dict[str, Any],
    child_categories: dict[str, list[str]],
    category_order: list[str],
) -> dict[str, Any]:
    name = str(entry.get("name") or "")
    categories = child_categories.get(name) or [_infer_category(entry)]
    categories = _sort_categories(_unique(categories), category_order)
    return {
        "name": name,
        "displayName": str(entry.get("display_name") or name),
        "description": _clean_text(str(entry.get("description") or "")),
        "purpose": _clean_text(str(entry.get("purpose") or "")),
        "path": _entry_link(entry.get("entry_path")),
        "packagePath": str(entry.get("package_path") or ""),
        "status": str(entry.get("status") or "ready"),
        "sourceRef": str(entry.get("source_ref") or ""),
        "categories": categories,
        "primaryCategory": categories[0] if categories else "其他",
    }


def _infer_category(entry: dict[str, Any]) -> str:
    blob = " ".join(
        str(entry.get(key) or "")
        for key in ("name", "display_name", "description", "purpose", "source_ref")
    ).lower()
    for category, tokens in CATEGORY_RULES:
        if any(token.lower() in blob for token in tokens):
            return category
    return "其他"


def _sort_categories(categories: list[str], order: list[str]) -> list[str]:
    rank = {category: index for index, category in enumerate(order)}
    return sorted(categories, key=lambda category: (rank.get(category, 10_000), category))


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result or ["其他"]


def _clean_cell(value: str) -> str:
    value = value.replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    return _clean_text(value)


def _clean_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value.replace("\n", " ")).strip()
    return value


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _render_html(payload: dict[str, Any]) -> str:
    data_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )
    html = HTML_TEMPLATE.replace("__CATALOG_DATA__", data_json)
    html = html.replace("__GENERATED_AT__", payload["generatedAt"])
    return html


HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tiny Agents Skill 目录</title>
  <style>
    :root {
      --paper: #f4f7ff;
      --surface: #ffffff;
      --surface-soft: #f8fbff;
      --ink: #102033;
      --muted: #66788f;
      --line: #d9e2f0;
      --line-strong: #c3d1e5;
      --blue: #1764ff;
      --blue-dark: #0052d9;
      --cyan: #00a4ff;
      --green: #15957a;
      --orange: #b76d00;
      --red: #d54941;
      --focus: #1764ff;
      --shadow: 0 12px 30px rgba(23, 79, 168, 0.10);
      --radius: 6px;
    }

    * {
      box-sizing: border-box;
    }

    html {
      color: var(--ink);
      background:
        linear-gradient(180deg, #eef5ff 0, #f7faff 260px, #f5f7fb 100%);
      font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
      line-height: 1.5;
    }

    body {
      margin: 0;
      min-width: 320px;
    }

    a {
      color: inherit;
      text-decoration: none;
    }

    button,
    input {
      font: inherit;
    }

    button:focus-visible,
    input:focus-visible,
    a:focus-visible {
      outline: 3px solid color-mix(in srgb, var(--focus) 32%, transparent);
      outline-offset: 3px;
    }

    .shell {
      width: min(1200px, calc(100% - 32px));
      margin: 0 auto;
      padding: 0 0 42px;
    }

    .cloud-nav {
      display: flex;
      min-height: 56px;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
      color: #31445c;
      font-size: 14px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 800;
      color: #142640;
    }

    .brand-mark {
      display: grid;
      width: 24px;
      height: 24px;
      place-items: center;
      border-radius: 5px;
      background: var(--blue);
      color: #fff;
      font-size: 15px;
      font-weight: 900;
    }

    .nav-links {
      display: flex;
      flex-wrap: wrap;
      gap: 18px;
      justify-content: flex-end;
      color: var(--muted);
    }

    .nav-links span:first-child {
      color: var(--blue-dark);
      font-weight: 700;
    }

    .topbar {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 330px;
      gap: 28px;
      align-items: center;
      min-height: 246px;
      padding: 34px 36px;
      border: 1px solid #cfe0f8;
      border-radius: 10px;
      background:
        linear-gradient(135deg, #ffffff 0%, #f6faff 48%, #e8f3ff 100%);
      box-shadow: var(--shadow);
      overflow: hidden;
      position: relative;
    }

    .topbar::after {
      content: "";
      position: absolute;
      inset: auto 0 0 auto;
      width: 42%;
      height: 100%;
      background:
        linear-gradient(135deg, transparent 18px, rgba(23, 100, 255, 0.12) 18px, rgba(23, 100, 255, 0.12) 20px, transparent 20px),
        linear-gradient(90deg, transparent, rgba(0, 164, 255, 0.10));
      background-size: 46px 46px, auto;
      pointer-events: none;
    }

    .eyebrow {
      margin: 0 0 10px;
      color: var(--blue-dark);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      position: relative;
      z-index: 1;
    }

    h1 {
      margin: 0;
      max-width: 760px;
      font-size: clamp(34px, 4vw, 52px);
      font-weight: 800;
      letter-spacing: 0;
      line-height: 1.12;
      position: relative;
      z-index: 1;
    }

    .hero-text {
      max-width: 720px;
      margin: 16px 0 0;
      color: #4c5f78;
      font-size: 16px;
      position: relative;
      z-index: 1;
    }

    .hero-links {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 22px;
      position: relative;
      z-index: 1;
    }

    .hero-link {
      display: inline-flex;
      align-items: center;
      min-height: 34px;
      padding: 0 12px;
      border: 1px solid #bcd1ef;
      border-radius: var(--radius);
      background: rgba(255, 255, 255, 0.78);
      color: var(--blue-dark);
      font-size: 13px;
      font-weight: 700;
    }

    .statbar {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
      position: relative;
      z-index: 1;
    }

    .stat {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 14px;
      align-items: center;
      min-height: 70px;
      padding: 14px 16px;
      background: rgba(255, 255, 255, 0.88);
      border: 1px solid #d6e5fb;
      border-radius: var(--radius);
    }

    .stat strong {
      display: block;
      color: var(--blue-dark);
      font-size: 28px;
      line-height: 1;
      font-variant-numeric: tabular-nums;
    }

    .stat span {
      display: block;
      color: var(--muted);
      font-size: 12px;
    }

    .practice-strip {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 16px 0 18px;
    }

    .practice-card {
      min-height: 96px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
      box-shadow: 0 6px 18px rgba(28, 78, 140, 0.06);
    }

    .practice-card strong {
      display: block;
      margin-bottom: 6px;
      font-size: 15px;
    }

    .practice-card span {
      display: block;
      color: var(--muted);
      font-size: 13px;
    }

    .control-panel {
      display: grid;
      grid-template-columns: auto minmax(240px, 1fr) auto;
      gap: 14px;
      align-items: center;
      margin: 0 0 18px;
      padding: 12px;
      background: rgba(255, 255, 255, 0.94);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      position: sticky;
      top: 10px;
      z-index: 10;
      backdrop-filter: blur(14px);
    }

    .tabs {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      border: 1px solid var(--line-strong);
      border-radius: var(--radius);
      overflow: hidden;
      background: #eef4ff;
      min-width: 210px;
    }

    .tab {
      min-height: 42px;
      padding: 0 14px;
      border: 0;
      border-right: 1px solid var(--line-strong);
      background: transparent;
      color: var(--muted);
      cursor: pointer;
      font-weight: 760;
    }

    .tab:last-child {
      border-right: 0;
    }

    .tab.is-active {
      background: var(--blue);
      color: white;
    }

    .search-wrap {
      position: relative;
      min-width: 0;
    }

    .search-label {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }

    #searchInput {
      width: 100%;
      min-height: 42px;
      padding: 0 46px 0 14px;
      border: 1px solid var(--line-strong);
      border-radius: var(--radius);
      background: #fbfdff;
      color: var(--ink);
    }

    #searchInput::-webkit-search-cancel-button,
    #searchInput::-webkit-search-decoration {
      appearance: none;
      -webkit-appearance: none;
    }

    #clearSearch {
      position: absolute;
      top: 5px;
      right: 6px;
      width: 32px;
      height: 32px;
      border: 0;
      border-radius: 6px;
      background: transparent;
      color: var(--muted);
      cursor: pointer;
      font-size: 22px;
      line-height: 1;
    }

    #clearSearch:hover {
      background: #eef4ff;
      color: var(--ink);
    }

    .result-meta {
      display: flex;
      min-height: 42px;
      align-items: center;
      justify-content: flex-end;
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }

    .layout {
      display: grid;
      grid-template-columns: 224px minmax(0, 1fr);
      gap: 18px;
      align-items: start;
    }

    .category-panel {
      position: sticky;
      top: 92px;
      padding: 0;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      overflow: hidden;
    }

    .category-panel h2 {
      margin: 0;
      padding: 13px 14px;
      border-bottom: 1px solid var(--line);
      background: var(--surface-soft);
      font-size: 13px;
      color: var(--muted);
    }

    .category-list {
      display: grid;
      gap: 0;
      max-height: calc(100vh - 160px);
      overflow: auto;
      padding: 6px;
    }

    .category-button {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      min-height: 36px;
      width: 100%;
      padding: 0 10px;
      border: 1px solid transparent;
      border-radius: var(--radius);
      background: transparent;
      color: var(--ink);
      cursor: pointer;
      text-align: left;
    }

    .category-button:hover {
      border-color: #d6e5fb;
      background: #f5f9ff;
    }

    .category-button.is-active {
      border-color: #bfd6ff;
      background: #eef5ff;
      color: var(--blue-dark);
    }

    .category-button span:first-child {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-weight: 700;
    }

    .category-button span:last-child {
      color: var(--muted);
      font-variant-numeric: tabular-nums;
      font-size: 12px;
    }

    .results {
      min-width: 0;
    }

    .group {
      margin-bottom: 26px;
    }

    .group-header {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 16px;
      margin: 0 0 12px;
      padding: 14px 2px 10px;
      border-bottom: 1px solid var(--line);
    }

    .group-header h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 800;
    }

    .group-header span {
      color: var(--muted);
      font-size: 13px;
      font-variant-numeric: tabular-nums;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(286px, 1fr));
      gap: 12px;
    }

    .item-card {
      display: flex;
      min-height: 236px;
      flex-direction: column;
      gap: 12px;
      padding: 18px;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
    }

    .item-card:hover {
      transform: translateY(-2px);
      border-color: #a9c9ff;
      box-shadow: 0 14px 28px rgba(23, 79, 168, 0.12);
    }

    .item-top {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: start;
    }

    .item-title {
      min-width: 0;
    }

    .item-title a {
      display: inline;
      color: var(--ink);
      font-weight: 800;
      overflow-wrap: anywhere;
    }

    .item-title a:hover {
      color: var(--blue-dark);
      text-decoration: underline;
      text-decoration-thickness: 1px;
      text-underline-offset: 3px;
    }

    .slug {
      margin-top: 3px;
      color: var(--muted);
      font-family: "SFMono-Regular", Consolas, monospace;
      font-size: 12px;
      overflow-wrap: anywhere;
    }

    .kind-mark {
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      padding: 0 8px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      white-space: nowrap;
    }

    .kind-mark.skill {
      border-color: #bfd6ff;
      color: var(--blue-dark);
      background: #f2f7ff;
    }

    .kind-mark.team {
      border-color: #ffd7b0;
      color: #b76000;
      background: #fff7ed;
    }

    .description {
      margin: 0;
      color: #40536a;
      font-size: 14px;
      display: -webkit-box;
      -webkit-line-clamp: 4;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      margin-top: auto;
    }

    .card-foot {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      min-height: 28px;
      padding-top: 8px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 12px;
    }

    .card-foot span {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .card-foot strong {
      color: var(--ink);
      font-weight: 700;
      white-space: nowrap;
    }

    .chip {
      display: inline-flex;
      align-items: center;
      max-width: 100%;
      min-height: 26px;
      padding: 0 8px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      color: #445b75;
      background: #f8fbff;
      font-size: 12px;
      font-family: "SFMono-Regular", Consolas, monospace;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .chip.category {
      font-family: inherit;
      color: var(--blue-dark);
      background: #f2f7ff;
      border-color: #bfd6ff;
      font-weight: 780;
    }

    .chip.internal {
      color: var(--muted);
      background: #f5f7fb;
      border-style: dashed;
    }

    .chip.link:hover {
      border-color: var(--blue);
      color: var(--blue-dark);
      text-decoration: underline;
      text-underline-offset: 2px;
    }

    .team-meter {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: center;
      padding: 8px 10px;
      background: #f8fbff;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      color: var(--muted);
      font-size: 12px;
    }

    .meter-bar {
      height: 8px;
      border-radius: 5px;
      background: #e6eef9;
      overflow: hidden;
    }

    .meter-bar span {
      display: block;
      height: 100%;
      width: var(--value);
      background: linear-gradient(90deg, var(--blue), var(--cyan));
    }

    .empty-state {
      padding: 36px;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      color: var(--muted);
      text-align: center;
    }

    .footer-note {
      margin-top: 24px;
      color: var(--muted);
      font-size: 12px;
      text-align: right;
    }

    @media (max-width: 980px) {
      .topbar,
      .control-panel,
      .layout {
        grid-template-columns: 1fr;
      }

      .topbar {
        min-height: 0;
        padding: 28px;
      }

      .statbar {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }

      .practice-strip {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .control-panel,
      .category-panel {
        position: static;
      }

      .category-list {
        display: flex;
        max-height: none;
        overflow-x: auto;
        padding: 0 0 3px;
      }

      .category-button {
        width: auto;
        min-width: 122px;
      }

      .result-meta {
        justify-content: flex-start;
      }
    }

    @media (max-width: 640px) {
      .shell {
        width: min(100% - 20px, 1500px);
        padding-top: 12px;
      }

      .cloud-nav {
        align-items: flex-start;
        flex-direction: column;
        gap: 10px;
        padding-bottom: 12px;
      }

      h1 {
        font-size: 32px;
      }

      .statbar {
        grid-template-columns: 1fr;
      }

      .practice-strip {
        grid-template-columns: 1fr;
      }

      .grid {
        grid-template-columns: 1fr;
      }

      .item-card {
        min-height: 0;
      }
    }

    @media (prefers-reduced-motion: reduce) {
      *,
      *::before,
      *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
      }
    }
  </style>
</head>
<body>
  <main class="shell">
    <nav class="cloud-nav" aria-label="项目导航">
      <div class="brand"><span class="brand-mark">T</span><span>Tiny Agents</span></div>
      <div class="nav-links" aria-label="目录来源">
        <span>Skill 广场</span>
        <span>专家团索引</span>
        <span>本地静态目录</span>
      </div>
    </nav>

    <header class="topbar">
      <div>
        <p class="eyebrow">developer skill marketplace</p>
        <h1>Tiny Agents Skill 广场</h1>
        <p class="hero-text">面向 tiny-agents 仓库的本地能力广场。按类型浏览普通 skill 和专家团入口，也可以直接搜索名称、描述、分类或专家团内的子 skill。</p>
        <div class="hero-links" aria-label="快捷入口">
          <a class="hero-link" href="skill-registry.md">Skill Registry</a>
          <a class="hero-link" href="expert-team-file-list.md">专家团列表</a>
          <a class="hero-link" href="../skills/">Skills 文件夹</a>
        </div>
      </div>
      <div class="statbar" aria-label="目录统计">
        <div class="stat"><strong id="skillTotal">0</strong><span>普通 skill</span></div>
        <div class="stat"><strong id="teamTotal">0</strong><span>专家团</span></div>
        <div class="stat"><strong id="registryTotal">0</strong><span>索引条目</span></div>
      </div>
    </header>

    <section class="practice-strip" aria-label="常用查找场景">
      <div class="practice-card"><strong>开发实现</strong><span>按技术栈、调试、测试、云服务快速定位能力。</span></div>
      <div class="practice-card"><strong>设计产品</strong><span>查找 UI、UX、品牌、原型和产品策略专家团。</span></div>
      <div class="practice-card"><strong>业务交付</strong><span>覆盖销售、金融、法务、运营、人力等复合场景。</span></div>
      <div class="practice-card"><strong>能力治理</strong><span>区分普通 skill、专家团入口和内部能力标签。</span></div>
    </section>

    <section class="control-panel" aria-label="目录筛选">
      <div class="tabs" role="tablist" aria-label="页面">
        <button class="tab is-active" type="button" role="tab" aria-selected="true" data-tab="skills">Skill</button>
        <button class="tab" type="button" role="tab" aria-selected="false" data-tab="teams">专家团</button>
      </div>
      <div class="search-wrap">
        <label class="search-label" for="searchInput">搜索</label>
        <input id="searchInput" type="search" autocomplete="off" placeholder="搜索名称、描述、分类或子 skill">
        <button id="clearSearch" type="button" aria-label="清空搜索">×</button>
      </div>
      <div class="result-meta" id="resultMeta">0 条</div>
    </section>

    <section class="layout">
      <aside class="category-panel" aria-label="类型">
        <h2>类型</h2>
        <div class="category-list" id="categoryList"></div>
      </aside>
      <section class="results" id="results" aria-live="polite"></section>
    </section>

    <div class="footer-note">Generated at __GENERATED_AT__</div>
  </main>

  <script type="application/json" id="catalogData">__CATALOG_DATA__</script>
  <script>
    const catalog = JSON.parse(document.getElementById("catalogData").textContent);
    const state = {
      tab: location.hash === "#teams" ? "teams" : "skills",
      category: "全部",
      query: ""
    };

    const els = {
      tabs: Array.from(document.querySelectorAll(".tab")),
      search: document.getElementById("searchInput"),
      clearSearch: document.getElementById("clearSearch"),
      categoryList: document.getElementById("categoryList"),
      results: document.getElementById("results"),
      resultMeta: document.getElementById("resultMeta"),
      skillTotal: document.getElementById("skillTotal"),
      teamTotal: document.getElementById("teamTotal"),
      registryTotal: document.getElementById("registryTotal")
    };

    els.skillTotal.textContent = String(catalog.stats.skills);
    els.teamTotal.textContent = String(catalog.stats.expertTeams);
    els.registryTotal.textContent = String(catalog.stats.allRegistryEntries);

    els.tabs.forEach((button) => {
      button.addEventListener("click", () => {
        state.tab = button.dataset.tab;
        state.category = "全部";
        location.hash = state.tab === "teams" ? "teams" : "skills";
        render();
      });
    });

    els.search.addEventListener("input", () => {
      state.query = els.search.value.trim();
      render();
    });

    els.clearSearch.addEventListener("click", () => {
      els.search.value = "";
      state.query = "";
      els.search.focus();
      render();
    });

    window.addEventListener("hashchange", () => {
      state.tab = location.hash === "#teams" ? "teams" : "skills";
      state.category = "全部";
      render();
    });

    function dataset() {
      return state.tab === "teams" ? catalog.teams : catalog.skills;
    }

    function categoriesFor(item) {
      return state.tab === "teams" ? [item.category] : item.categories;
    }

    function primaryCategory(item) {
      return item.primaryCategory || categoriesFor(item)[0] || "其他";
    }

    function queryBlob(item) {
      const childNames = item.children ? item.children.map((child) => child.name).join(" ") : "";
      const categories = categoriesFor(item).join(" ");
      return [
        item.name,
        item.slug,
        item.displayName,
        item.description,
        item.purpose,
        item.packagePath,
        item.sourceRef,
        categories,
        childNames
      ].filter(Boolean).join(" ").toLowerCase();
    }

    function matchesQuery(item) {
      if (!state.query) return true;
      return queryBlob(item).includes(state.query.toLowerCase());
    }

    function matchesCategory(item) {
      if (state.category === "全部") return true;
      return categoriesFor(item).includes(state.category);
    }

    function filteredByQuery() {
      return dataset().filter(matchesQuery);
    }

    function visibleItems() {
      return filteredByQuery().filter(matchesCategory);
    }

    function orderedCategories(rows) {
      const count = new Map();
      rows.forEach((item) => {
        categoriesFor(item).forEach((category) => {
          count.set(category, (count.get(category) || 0) + 1);
        });
      });
      const known = catalog.categoryOrder.filter((category) => count.has(category));
      const unknown = Array.from(count.keys())
        .filter((category) => !catalog.categoryOrder.includes(category))
        .sort((a, b) => a.localeCompare(b, "zh-Hans-CN"));
      return { ordered: known.concat(unknown), count };
    }

    function renderTabs() {
      els.tabs.forEach((button) => {
        const active = button.dataset.tab === state.tab;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-selected", active ? "true" : "false");
      });
    }

    function renderCategories() {
      const rows = filteredByQuery();
      const { ordered, count } = orderedCategories(rows);
      const buttons = [{ category: "全部", count: rows.length }].concat(
        ordered.map((category) => ({ category, count: count.get(category) || 0 }))
      );
      if (state.category !== "全部" && !count.has(state.category)) {
        state.category = "全部";
      }
      els.categoryList.innerHTML = buttons.map(({ category, count }) => {
        const active = category === state.category ? " is-active" : "";
        return "<button class=\\"category-button" + active + "\\" type=\\"button\\" data-category=\\"" + escapeAttr(category) + "\\">" +
          "<span>" + escapeHTML(category) + "</span><span>" + count + "</span></button>";
      }).join("");

      Array.from(els.categoryList.querySelectorAll("button")).forEach((button) => {
        button.addEventListener("click", () => {
          state.category = button.dataset.category;
          render();
        });
      });
    }

    function renderResults() {
      const rows = visibleItems();
      const label = state.tab === "teams" ? "专家团" : "skill";
      els.resultMeta.textContent = rows.length + " 个" + label;

      if (!rows.length) {
        els.results.innerHTML = "<div class=\\"empty-state\\">没有匹配结果</div>";
        return;
      }

      const grouped = new Map();
      rows.forEach((item) => {
        const category = state.category === "全部" ? primaryCategory(item) : state.category;
        if (!grouped.has(category)) grouped.set(category, []);
        grouped.get(category).push(item);
      });

      const groupNames = Array.from(grouped.keys()).sort((a, b) => {
        const ai = catalog.categoryOrder.indexOf(a);
        const bi = catalog.categoryOrder.indexOf(b);
        if (ai !== -1 || bi !== -1) return (ai === -1 ? 10000 : ai) - (bi === -1 ? 10000 : bi);
        return a.localeCompare(b, "zh-Hans-CN");
      });

      els.results.innerHTML = groupNames.map((category) => {
        const items = grouped.get(category).slice().sort(compareItems);
        return "<section class=\\"group\\">" +
          "<div class=\\"group-header\\"><h2>" + escapeHTML(category) + "</h2><span>" + items.length + " 条</span></div>" +
          "<div class=\\"grid\\">" + items.map((item) => state.tab === "teams" ? teamCard(item) : skillCard(item)).join("") + "</div>" +
        "</section>";
      }).join("");
    }

    function compareItems(a, b) {
      const left = (a.displayName || a.name || a.slug || "").toLowerCase();
      const right = (b.displayName || b.name || b.slug || "").toLowerCase();
      return left.localeCompare(right, "zh-Hans-CN");
    }

    function skillCard(item) {
      const description = item.description || item.purpose || "暂无说明";
      const categoryChips = item.categories.map((category) =>
        "<span class=\\"chip category\\">" + escapeHTML(category) + "</span>"
      ).join("");
      return "<article class=\\"item-card\\">" +
        "<div class=\\"item-top\\"><div class=\\"item-title\\">" +
          "<a href=\\"" + escapeAttr(item.path) + "\\">" + escapeHTML(item.displayName || item.name) + "</a>" +
          "<div class=\\"slug\\">$" + escapeHTML(item.name) + "</div>" +
        "</div><span class=\\"kind-mark skill\\">Skill</span></div>" +
        "<p class=\\"description\\">" + escapeHTML(description) + "</p>" +
        "<div class=\\"chips\\">" + categoryChips + "</div>" +
        "<div class=\\"card-foot\\"><span>" + escapeHTML(item.packagePath || "skills") + "</span><strong>" + escapeHTML(item.status || "ready") + "</strong></div>" +
      "</article>";
    }

    function teamCard(item) {
      const description = item.description || item.purpose || "暂无说明";
      const percent = item.childCount ? Math.round((item.topLevelChildCount / item.childCount) * 100) : 0;
      const childChips = item.children.slice(0, 12).map((child) => {
        if (child.isTopLevel && child.path) {
          return "<a class=\\"chip link\\" href=\\"" + escapeAttr(child.path) + "\\">" + escapeHTML(child.name) + "</a>";
        }
        return "<span class=\\"chip internal\\">" + escapeHTML(child.name) + "</span>";
      }).join("");
      const more = item.children.length > 12 ? "<span class=\\"chip internal\\">+" + (item.children.length - 12) + "</span>" : "";
      return "<article class=\\"item-card\\">" +
        "<div class=\\"item-top\\"><div class=\\"item-title\\">" +
          "<a href=\\"" + escapeAttr(item.path) + "\\">" + escapeHTML(item.displayName || item.slug) + "</a>" +
          "<div class=\\"slug\\">$" + escapeHTML(item.slug) + "</div>" +
        "</div><span class=\\"kind-mark team\\">专家团</span></div>" +
        "<p class=\\"description\\">" + escapeHTML(description) + "</p>" +
        "<div class=\\"team-meter\\"><div class=\\"meter-bar\\" aria-hidden=\\"true\\"><span style=\\"--value:" + percent + "%\\"></span></div>" +
          "<span>" + item.topLevelChildCount + "/" + item.childCount + " 顶层 skill</span></div>" +
        "<div class=\\"chips\\"><span class=\\"chip category\\">" + escapeHTML(item.category) + "</span>" + childChips + more + "</div>" +
        "<div class=\\"card-foot\\"><span>" + escapeHTML(item.entry_path || item.path) + "</span><strong>" + item.childCount + " 子项</strong></div>" +
      "</article>";
    }

    function render() {
      renderTabs();
      renderCategories();
      renderResults();
    }

    function escapeHTML(value) {
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\\"": "&quot;",
        "'": "&#39;"
      })[char]);
    }

    function escapeAttr(value) {
      return escapeHTML(value).replace(/`/g, "&#96;");
    }

    render();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
