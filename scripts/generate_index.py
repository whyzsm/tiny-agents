from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


REPORT_GLOB = "scan-*.json"
INDEX_DIR = Path("indexes")
JSON_INDEX_PATH = INDEX_DIR / "agent-skill-index.json"
MD_INDEX_PATH = INDEX_DIR / "agent-skill-index.md"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    report_path = _resolve_report_path(args)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["source_report"] = str(report_path)
    items = _unique_index_items(report["items"])
    entries = [_index_entry(item) for item in items]

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    JSON_INDEX_PATH.write_text(
        json.dumps(
            {
                "source_report": str(report_path),
                "scan_generated_at": report["generated_at"],
                "selection_rule": "Exclude skipped, blocked, and conflict items, then keep the first item per name.",
                "total": len(entries),
                "entries": entries,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    MD_INDEX_PATH.write_text(_render_markdown(report, entries), encoding="utf-8")
    return 0


def _resolve_report_path(argv: list[str]) -> Path:
    if argv:
        return Path(argv[0])
    reports = sorted(Path("reports").glob(REPORT_GLOB))
    if not reports:
        raise FileNotFoundError(f"No reports matching reports/{REPORT_GLOB}")
    return reports[-1]


def _unique_index_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chosen: dict[str, dict[str, Any]] = {}
    for item in items:
        if item["status"] not in {"ready", "candidate"}:
            continue
        chosen.setdefault(item["name"], item)
    return sorted(chosen.values(), key=lambda item: (item["kind"], item["name"].lower()))


def _index_entry(item: dict[str, Any]) -> dict[str, Any]:
    source_path = Path(item["source_path"])
    entry_path = Path(item["entry_path"])
    text = _read_text(entry_path)
    frontmatter = _frontmatter(text)
    heading = _first_heading(text)

    display_name = frontmatter.get("name") or item["name"]
    description = _description_for(item, text, frontmatter, heading)
    purpose = _purpose_for(item, text, frontmatter, description)

    return {
        "name": item["name"],
        "display_name": display_name,
        "kind": item["kind"],
        "status": item["status"],
        "reason": _clean_text(item["reason"]),
        "description": _clean_text(description),
        "purpose": _clean_text(purpose),
        "source_path": _public_path(source_path),
        "entry_path": _public_path(entry_path),
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


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
    item: dict[str, Any],
    text: str,
    frontmatter: dict[str, str],
    heading: str,
) -> str:
    if item["kind"] == "agent":
        return (
            _section_summary(text, ("职责", "身份", "role", "responsibility"))
            or heading
            or frontmatter.get("description")
            or item["reason"]
        )
    return (
        frontmatter.get("description")
        or _section_summary(text, ("description", "说明", "简介", "skill intent"))
        or heading
        or item["reason"]
    )


def _purpose_for(
    item: dict[str, Any],
    text: str,
    frontmatter: dict[str, str],
    description: str,
) -> str:
    if item["kind"] == "agent":
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


def _public_path(path: Path) -> str:
    try:
        return "~/" + path.relative_to(Path.home()).as_posix()
    except ValueError:
        pass
    return path.name


def _render_markdown(report: dict[str, Any], entries: list[dict[str, Any]]) -> str:
    by_kind: dict[str, list[dict[str, Any]]] = {"agent": [], "skill": [], "candidate": []}
    for entry in entries:
        by_kind.setdefault(entry["kind"], []).append(entry)

    lines = [
        "# Agent And Skill Index",
        "",
        f"- Source report: `{report['source_report']}`",
        f"- Scan generated at: `{report['generated_at']}`",
        "- Selection rule: exclude skipped, blocked, and conflict items, then keep the first item per name.",
        f"- Total: `{len(entries)}`",
        f"- Agents: `{len(by_kind.get('agent', []))}`",
        f"- Skills: `{len(by_kind.get('skill', []))}`",
        f"- Candidates: `{len(by_kind.get('candidate', []))}`",
        "",
    ]

    sections = [
        ("Agents", by_kind.get("agent", [])),
        ("Skills", by_kind.get("skill", [])),
        ("Candidates", by_kind.get("candidate", [])),
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
                    name=_escape_table(entry["display_name"]),
                    description=_escape_table(entry["description"]),
                    purpose=_escape_table(entry["purpose"]),
                    source=entry["source_path"],
                )
            )
        lines.append("")
    return "\n".join(lines)


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
