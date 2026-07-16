from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SKIP_STATUSES = {"blocked", "conflict", "draft", "skipped"}


@dataclass(frozen=True)
class IndexEntry:
    name: str
    display_name: str
    kind: str
    status: str
    reason: str
    description: str
    purpose: str
    source_path: str
    entry_path: str


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="generate_index")
    parser.add_argument("--project-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    project_root = args.project_root.expanduser()
    entries = _discover_entries(project_root)
    index_dir = project_root / "indexes"
    json_path = index_dir / "agent-skill-index.json"
    md_path = index_dir / "agent-skill-index.md"

    payload = {
        "generated_at": _now(),
        "project_root": _public_path(project_root, project_root),
        "agents_root": _public_path(project_root / "agents", project_root),
        "skills_root": _public_path(project_root / "skills", project_root),
        "selection_rule": (
            "Scan project agents/ and skills/, exclude blocked/conflict/draft/skipped "
            "packages, and keep repository-relative paths."
        ),
        "total": len(entries),
        "entries": [entry.__dict__ for entry in entries],
    }

    index_dir.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    md_path.write_text(_render_markdown(payload, entries), encoding="utf-8")
    return 0


def _discover_entries(project_root: Path) -> list[IndexEntry]:
    entries = _discover_agents(project_root) + _discover_skills(project_root)
    return sorted(entries, key=lambda entry: (entry.kind, entry.name.lower(), entry.entry_path))


def _discover_agents(project_root: Path) -> list[IndexEntry]:
    agents_root = project_root / "agents"
    if not agents_root.is_dir():
        return []

    entries: list[IndexEntry] = []
    for package_dir in sorted(
        (path for path in agents_root.iterdir() if path.is_dir()),
        key=lambda path: path.name.lower(),
    ):
        entry_path = _agent_entry_file(package_dir)
        if entry_path is None:
            continue
        source_meta = _read_json(package_dir / "source.json")
        status = _status(source_meta)
        if status in SKIP_STATUSES:
            continue
        entries.append(
            _index_entry(
                package_dir=package_dir,
                entry_path=entry_path,
                kind="agent",
                status=status,
                reason=str(source_meta.get("reason") or "repo-agent"),
                project_root=project_root,
            )
        )
    return entries


def _discover_skills(project_root: Path) -> list[IndexEntry]:
    skills_root = project_root / "skills"
    if not skills_root.is_dir():
        return []

    entries: list[IndexEntry] = []
    for package_dir in sorted(
        (path for path in skills_root.iterdir() if path.is_dir()),
        key=lambda path: path.name.lower(),
    ):
        entry_path = _skill_entry_file(package_dir)
        if entry_path is None:
            continue
        source_meta = _read_json(package_dir / "source.json")
        status = _status(source_meta)
        if status in SKIP_STATUSES:
            continue
        entries.append(
            _index_entry(
                package_dir=package_dir,
                entry_path=entry_path,
                kind="skill",
                status=status,
                reason=str(source_meta.get("reason") or "repo-skill"),
                project_root=project_root,
            )
        )
    return entries


def _index_entry(
    package_dir: Path,
    entry_path: Path,
    kind: str,
    status: str,
    reason: str,
    project_root: Path,
) -> IndexEntry:
    text = _read_text(entry_path)
    frontmatter = _frontmatter(text)
    heading = _first_heading(text)

    name = package_dir.name
    display_name = _display_name_for(name, kind, frontmatter)
    description = _description_for(kind, reason, text, frontmatter, heading)
    purpose = _purpose_for(kind, text, frontmatter, description)

    return IndexEntry(
        name=name,
        display_name=display_name,
        kind=kind,
        status=status,
        reason=_clean_text(reason),
        description=_clean_text(description),
        purpose=_clean_text(purpose),
        source_path=_public_path(package_dir, project_root),
        entry_path=_public_path(entry_path, project_root),
    )


def _skill_entry_file(package_dir: Path) -> Path | None:
    for filename in ("SKILL.md", "skill.md"):
        candidate = package_dir / filename
        if candidate.is_file():
            return candidate
    return None


def _agent_entry_file(package_dir: Path) -> Path | None:
    preferred = (
        package_dir / f"{package_dir.name}.md",
        package_dir / "AGENTS.md",
        package_dir / "agent.md",
        package_dir / "prompt.md",
    )
    for candidate in preferred:
        if candidate.is_file():
            return candidate
    candidates = sorted(
        path
        for path in package_dir.iterdir()
        if path.is_file() and path.name != "source.json" and path.suffix in {".md", ".yaml", ".yml"}
    )
    return candidates[0] if candidates else None


def _status(source_meta: dict[str, Any]) -> str:
    return str(source_meta.get("status", "ready")).strip().lower() or "ready"


def _display_name_for(canonical_name: str, kind: str, frontmatter: dict[str, str]) -> str:
    raw_display = frontmatter.get("name") or canonical_name
    if kind == "skill" and _slug(raw_display) != canonical_name:
        return canonical_name
    return raw_display


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-+", "-", slug)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    key: str | None = None
    value_lines: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            if key:
                data[key] = _clean_text(" ".join(value_lines))
            break
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            if key:
                data[key] = _clean_text(" ".join(value_lines))
            key = match.group(1)
            raw_value = match.group(2).strip().strip("\"'")
            value_lines = [raw_value] if raw_value not in {"|", ">"} else []
        elif key and (line.startswith(" ") or line.startswith("\t")):
            stripped = line.strip()
            if stripped and not stripped.startswith("- "):
                value_lines.append(stripped)
    return data


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def _description_for(
    kind: str,
    reason: str,
    text: str,
    frontmatter: dict[str, str],
    heading: str,
) -> str:
    if kind == "agent":
        return (
            _section_summary(text, ("职责", "身份", "role", "responsibility"))
            or heading
            or frontmatter.get("description")
            or reason
        )
    return (
        frontmatter.get("description")
        or _section_summary(text, ("description", "说明", "简介", "skill intent"))
        or heading
        or reason
    )


def _purpose_for(
    kind: str,
    text: str,
    frontmatter: dict[str, str],
    description: str,
) -> str:
    if kind == "agent":
        return (
            _section_summary(text, ("启动", "工作流", "task", "任务", "接单"))
            or description
        )
    return (
        _section_summary(text, ("task", "任务", "use when", "skill intent", "purpose", "用途", "使用场景", "目标"))
        or frontmatter.get("description")
        or description
    )


def _section_summary(text: str, headings: tuple[str, ...]) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        normalized = line.strip().lower().strip("#:： ")
        if not normalized:
            continue
        if any(marker in normalized for marker in headings):
            collected: list[str] = []
            for next_line in lines[index + 1 :]:
                stripped = next_line.strip()
                if not stripped:
                    if collected:
                        break
                    continue
                if stripped.startswith("#"):
                    break
                if stripped.startswith("---"):
                    continue
                collected.append(stripped.lstrip("- ").strip())
                if len(" ".join(collected)) > 240:
                    break
            if collected:
                return " ".join(collected)
    return ""


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", _public_text(value)).strip()


def _public_text(value: str) -> str:
    return value.replace(str(Path.home()), "~")


def _public_path(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix() or "."
    except ValueError:
        pass
    return _public_text(str(path))


def _render_markdown(payload: dict[str, Any], entries: list[IndexEntry]) -> str:
    by_kind: dict[str, list[IndexEntry]] = {"agent": [], "skill": []}
    for entry in entries:
        by_kind.setdefault(entry.kind, []).append(entry)

    lines = [
        "# Agent And Skill Index",
        "",
        "- Scope: project agents and skills in this repository.",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Project root: `{payload['project_root']}`",
        f"- Agents root: `{payload['agents_root']}`",
        f"- Skills root: `{payload['skills_root']}`",
        f"- Selection rule: {payload['selection_rule']}",
        f"- Total: `{len(entries)}`",
        f"- Agents: `{len(by_kind.get('agent', []))}`",
        f"- Skills: `{len(by_kind.get('skill', []))}`",
        "",
    ]

    sections = [
        ("Agents", by_kind.get("agent", [])),
        ("Skills", by_kind.get("skill", [])),
    ]
    for title, section_entries in sections:
        lines.extend([f"## {title}", ""])
        if not section_entries:
            lines.extend(["None.", ""])
            continue
        lines.append("| Name | Description | Purpose | Source |")
        lines.append("|---|---|---|---|")
        for entry in section_entries:
            lines.append(
                "| {name} | {description} | {purpose} | `{source}` |".format(
                    name=_escape_table(entry.display_name),
                    description=_escape_table(entry.description),
                    purpose=_escape_table(entry.purpose),
                    source=entry.source_path,
                )
            )
        lines.append("")
    return "\n".join(lines)


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


if __name__ == "__main__":
    raise SystemExit(main())
