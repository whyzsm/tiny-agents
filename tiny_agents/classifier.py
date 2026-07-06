from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .config import LOCAL_ONLY_FILES
from .discovery import DiscoveredEntry
from .models import ScanItem, ScanReport

PERSONA_PATTERNS = (
    re.compile(r"(?i)^\s*(persona|personality|identity)\s*:"),
    re.compile(r"(?i)^\s*#+\s*(persona|personality|identity)\b"),
    re.compile(r"(?i)\byou are (an?|the) [^.。\n]{1,80}"),
    re.compile(r"你是[^。\n]{1,80}"),
    re.compile(r"^\s*#+\s*(身份|人格|性格|灵魂)\b"),
    re.compile(r"(人格|性格|灵魂)"),
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
    return any(_line_contains_persona(line) for line in text.splitlines())


def _line_contains_persona(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("|"):
        return False
    if _is_instructional_you_are(stripped):
        return False
    return any(pattern.search(stripped) for pattern in PERSONA_PATTERNS)


def _is_instructional_you_are(stripped: str) -> bool:
    lowered = stripped.lower()
    return lowered.startswith(("if you are ", "when you are ", "- if you are ", "- when you are "))


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
    if path.name in LOCAL_ONLY_FILES:
        return True
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
        representatives: list[ScanItem] = []
        by_digest: dict[str, list[ScanItem]] = defaultdict(list)
        for item in duplicates:
            by_digest[_content_digest(item)].append(item)

        for same_content_items in by_digest.values():
            winner = min(same_content_items, key=_source_priority_key)
            representatives.append(winner)
            for item in same_content_items:
                if item is winner:
                    continue
                item.status = "skipped"
                item.reason = "duplicate_same_content"

        if len(representatives) < 2:
            continue
        for item in representatives:
            item.status = "conflict"
            item.reason = "duplicate_name"


def _content_digest(item: ScanItem) -> str:
    digest = hashlib.sha256()
    for file_path in item.files or [item.entry_path]:
        digest.update(_relative_digest_path(item, file_path).encode("utf-8"))
        digest.update(b"\0")
        try:
            digest.update(file_path.read_bytes())
        except OSError:
            digest.update(b"<unreadable>")
        digest.update(b"\0")
    return digest.hexdigest()


def _relative_digest_path(item: ScanItem, file_path: Path) -> str:
    if item.source_path.is_dir():
        try:
            return file_path.relative_to(item.source_path).as_posix()
        except ValueError:
            pass
    return file_path.name


def _source_priority_key(item: ScanItem) -> tuple[int, int, str]:
    parts = set(item.source_path.parts)
    if ".codex" in parts and "skills" in parts:
        priority = 0
    elif ".agents" in parts and "skills" in parts:
        priority = 1
    elif "understand-anything" in parts:
        priority = 2
    else:
        priority = 10
    return (priority, len(item.source_path.parts), str(item.source_path))
