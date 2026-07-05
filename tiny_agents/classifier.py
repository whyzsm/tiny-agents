from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .discovery import DiscoveredEntry
from .models import ScanItem, ScanReport

PERSONA_MARKERS = (
    "you are ",
    "你是",
    "身份",
    "人格",
    "性格",
    "灵魂",
    "persona",
    "personality",
    "mission",
    "role",
)


def classify_entries(entries: list[DiscoveredEntry], warnings: list[str]) -> ScanReport:
    items = [_classify_entry(entry) for entry in entries]
    _mark_conflicts(items)
    roots = sorted({entry.source_root for entry in entries}, key=str)
    return ScanReport(
        generated_at=datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        roots=roots,
        items=items,
        warnings=warnings,
    )


def _classify_entry(entry: DiscoveredEntry) -> ScanItem:
    text = _read_text(entry.entry_path)
    name = _extract_name(text) or _fallback_name(entry)

    if entry.entry_type == "skill_file":
        if _contains_persona(text):
            return ScanItem(
                name=name,
                kind="candidate",
                status="candidate",
                source_path=entry.source_path,
                entry_path=entry.entry_path,
                reason="persona_in_skill",
                files=_core_files(entry.source_path),
            )
        return ScanItem(
            name=name,
            kind="skill",
            status="ready",
            source_path=entry.source_path,
            entry_path=entry.entry_path,
            reason="standard_skill",
            files=_core_files(entry.source_path),
        )

    return ScanItem(
        name=name,
        kind="agent",
        status="ready",
        source_path=entry.source_path,
        entry_path=entry.entry_path,
        reason="agent_prompt",
        files=[entry.entry_path],
    )


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="ignore")


def _extract_name(text: str) -> str | None:
    in_frontmatter = False
    for index, line in enumerate(text.splitlines()):
        stripped = line.strip()
        if index == 0 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter and stripped == "---":
            return None
        if in_frontmatter and stripped.startswith("name:"):
            return stripped.split(":", 1)[1].strip().strip("\"'")
    return None


def _fallback_name(entry: DiscoveredEntry) -> str:
    if entry.entry_type == "skill_file":
        return entry.source_path.name
    if entry.entry_path.name == "AGENTS.md":
        return entry.entry_path.parent.name or "agents"
    return entry.entry_path.stem


def _contains_persona(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in PERSONA_MARKERS)


def _core_files(source_path: Path) -> list[Path]:
    if source_path.is_file():
        return [source_path]
    files: list[Path] = []
    for path in source_path.rglob("*"):
        if path.is_file() and not _should_skip_core_file(path):
            files.append(path)
    return sorted(files, key=str)


def _should_skip_core_file(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    skip_parts = {
        ".git",
        ".tmp",
        "__pycache__",
        "cache",
        "dist",
        "logs",
        "node_modules",
        "tmp",
    }
    return bool(lowered_parts & skip_parts) or path.suffix in {".pyc", ".log"}


def _mark_conflicts(items: list[ScanItem]) -> None:
    by_key: dict[tuple[str, str], list[ScanItem]] = defaultdict(list)
    for item in items:
        if item.status == "ready":
            by_key[(item.kind, item.name)].append(item)

    for duplicates in by_key.values():
        if len(duplicates) < 2:
            continue
        for item in duplicates:
            item.status = "conflict"
            item.reason = "duplicate_name"
