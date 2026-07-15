from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SKIP_STATUSES = {"blocked", "candidate", "conflict", "draft", "skipped"}


@dataclass(frozen=True)
class SkillRecord:
    name: str
    display_name: str
    description: str
    purpose: str
    package_path: str
    entry_path: str
    status: str
    source_ref: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="generate_skill_registry")
    parser.add_argument("--project-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--skills-root", type=Path)
    args = parser.parse_args(argv)

    project_root = args.project_root.expanduser()
    skills_root = (
        args.skills_root.expanduser() if args.skills_root else project_root / "skills"
    )
    index_dir = project_root / "indexes"
    md_path = index_dir / "skill-registry.md"
    json_path = index_dir / "skill-registry.json"

    records, omitted = _discover_skill_records(skills_root, project_root)
    index_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": _now(),
        "project_root": _public_path(project_root, project_root),
        "skills_root": _public_path(skills_root, project_root),
        "selection_rule": (
            "Keep top-level skill packages with SKILL.md or skill.md, skip draft/"
            "candidate/blocked/conflict/skipped packages, and use the package path "
            "as the install target."
        ),
        "total": len(records),
        "omitted": len(omitted),
        "entries": [record.to_dict() for record in records],
    }

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(_render_markdown(payload, records, omitted), encoding="utf-8")
    return 0


def _discover_skill_records(
    skills_root: Path, project_root: Path
) -> tuple[list[SkillRecord], list[dict[str, str]]]:
    if not skills_root.exists():
        raise FileNotFoundError(f"Missing skills root: {skills_root}")
    if not skills_root.is_dir():
        raise NotADirectoryError(f"Skills root is not a directory: {skills_root}")

    records: list[SkillRecord] = []
    omitted: list[dict[str, str]] = []

    for package_dir in sorted((path for path in skills_root.iterdir() if path.is_dir()), key=lambda path: path.name.lower()):
        if package_dir.name.startswith("."):
            continue
        entry_path = _entry_file(package_dir)
        if entry_path is None:
            continue

        source_meta = _read_json(package_dir / "source.json")
        status = str(source_meta.get("status", "ready")).strip().lower() or "ready"
        if status in SKIP_STATUSES:
            omitted.append(
                {
                    "name": package_dir.name,
                    "status": status,
                    "path": _public_path(package_dir, project_root),
                }
            )
            continue

        text = _read_text(entry_path)
        frontmatter = _frontmatter(text)
        display_name = _clean_text(
            frontmatter.get("name")
            or str(source_meta.get("display_name") or source_meta.get("name") or "")
            or _first_heading(text)
            or package_dir.name
        )
        description = _clean_text(
            frontmatter.get("description")
            or str(source_meta.get("description") or "")
            or _first_heading(text)
            or display_name
        )
        purpose = _clean_text(_purpose_for(text, frontmatter, description))
        records.append(
            SkillRecord(
                name=package_dir.name,
                display_name=display_name,
                description=description,
                purpose=purpose,
                package_path=_public_path(package_dir, project_root),
                entry_path=_public_path(entry_path, project_root),
                status=status,
                source_ref=_source_ref(package_dir, source_meta, project_root),
            )
        )

    records.sort(key=lambda record: (record.display_name.lower(), record.package_path.lower()))
    omitted.sort(key=lambda item: (item["name"].lower(), item["path"].lower()))
    return records, omitted


def _entry_file(package_dir: Path) -> Path | None:
    entries = {child.name: child for child in package_dir.iterdir() if child.is_file()}
    for filename in ("SKILL.md", "skill.md"):
        candidate = entries.get(filename)
        if candidate is not None:
            return candidate
    return None


def _source_ref(package_dir: Path, source_meta: dict[str, Any], project_root: Path) -> str:
    value = source_meta.get("source_ref") or source_meta.get("source_path")
    if isinstance(value, str) and value.strip():
        cleaned = value.strip().replace(str(Path.home()), "~")
        if not cleaned.startswith("/") and not re.match(r"^[A-Za-z]:\\", cleaned):
            return cleaned
    package_path = _public_path(package_dir, project_root)
    return f"repo-local/{package_path}"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}


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


def _purpose_for(
    text: str,
    frontmatter: dict[str, str],
    description: str,
) -> str:
    return (
        _section_summary(
            text,
            (
                "use when",
                "when to use",
                "overview",
                "purpose",
                "triggers",
                "workflow",
                "task",
                "任务",
                "用途",
                "使用场景",
                "目标",
            ),
        )
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
        relative = path.relative_to(project_root)
    except ValueError:
        return path.name
    return relative.as_posix()


def _render_markdown(
    payload: dict[str, Any], records: list[SkillRecord], omitted: list[dict[str, str]]
) -> str:
    lines = [
        "# Skill Registry",
        "",
        "- Canonical lookup for installable skills in this repository.",
        "- Use `indexes/skill-registry.md` before the local scan inventory in `indexes/agent-skill-index.md`.",
        f"- Project root: `{payload['project_root']}`",
        f"- Skills root: `{payload['skills_root']}`",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Selection rule: {payload['selection_rule']}",
        f"- Total: `{payload['total']}`",
        f"- Omitted: `{payload['omitted']}`",
        "",
        "| Name | Description | Purpose | Path |",
        "|---|---|---|---|",
    ]
    for record in records:
        lines.append(
            "| {name} | {description} | {purpose} | `{path}` |".format(
                name=_format_link(record.display_name, f"../{record.entry_path}"),
                description=_escape_table(record.description),
                purpose=_escape_table(record.purpose),
                path=record.entry_path,
            )
        )

    if omitted:
        lines.extend(["", "## Omitted", "", "| Name | Status | Path |", "|---|---|---|"])
        for item in omitted:
            lines.append(
                "| {name} | {status} | `{path}` |".format(
                    name=_escape_table(item["name"]),
                    status=_escape_table(item["status"]),
                    path=item["path"],
                )
            )

    return "\n".join(lines) + "\n"


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _format_link(label: str, target: str) -> str:
    return f"[{_escape_table(label)}]({target})"


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


if __name__ == "__main__":
    raise SystemExit(main())
