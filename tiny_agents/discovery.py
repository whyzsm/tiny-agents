from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import EXCLUDED_PARTS, SENSITIVE_PARTS


@dataclass(frozen=True)
class DiscoveredEntry:
    entry_path: Path
    source_path: Path
    source_root: Path
    entry_type: str


def discover_entries(roots: list[Path]) -> tuple[list[DiscoveredEntry], list[str]]:
    entries: list[DiscoveredEntry] = []
    warnings: list[str] = []
    seen: set[Path] = set()

    for root in roots:
        root = root.expanduser()
        if not root.exists():
            warnings.append(f"Missing scan root: {root}")
            continue
        if not root.is_dir():
            warnings.append(f"Scan root is not a directory: {root}")
            continue

        for path in root.rglob("*"):
            if not path.is_file() or _is_excluded(path, root):
                continue
            entry = _entry_for_path(path, root)
            if entry and entry.entry_path not in seen:
                entries.append(entry)
                seen.add(entry.entry_path)

    entries.sort(key=lambda entry: str(entry.entry_path))
    return entries, warnings


def _is_excluded(path: Path, root: Path) -> bool:
    parts = set(path.relative_to(root).parts)
    lowered = {part.lower() for part in parts}
    return bool(lowered & EXCLUDED_PARTS) or bool(lowered & SENSITIVE_PARTS)


def _entry_for_path(path: Path, root: Path) -> DiscoveredEntry | None:
    if path.name == "SKILL.md":
        return DiscoveredEntry(
            entry_path=path,
            source_path=path.parent,
            source_root=root,
            entry_type="skill_file",
        )
    if path.name == "AGENTS.md":
        return DiscoveredEntry(
            entry_path=path,
            source_path=path,
            source_root=root,
            entry_type="agent_file",
        )
    if path.suffix.lower() == ".md" and path.parent.name == "agents":
        return DiscoveredEntry(
            entry_path=path,
            source_path=path,
            source_root=root,
            entry_type="agent_file",
        )
    return None
