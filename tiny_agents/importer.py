from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .models import ScanItem, ScanReport


@dataclass
class ImportResult:
    imported: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def import_report(report_path: Path, project_root: Path) -> ImportResult:
    report = ScanReport.from_dict(json.loads(report_path.read_text(encoding="utf-8")))
    result = ImportResult()
    for item in report.items:
        if item.status != "ready" or item.kind not in {"agent", "skill"}:
            result.skipped.append(item.name)
            continue
        target = _target_dir(project_root, item)
        if target.exists():
            result.errors.append(f"Target already exists for {item.name}: {target}")
            continue
        try:
            _copy_item(item, target, report)
        except OSError as exc:
            result.errors.append(f"Failed to import {item.name}: {exc}")
            continue
        result.imported.append(item.name)
    return result


def _target_dir(project_root: Path, item: ScanItem) -> Path:
    parent = "agents" if item.kind == "agent" else "skills"
    return project_root / parent / item.name


def _copy_item(item: ScanItem, target: Path, report: ScanReport) -> None:
    target.mkdir(parents=True)
    if item.source_path.is_dir():
        for file_path in item.files:
            relative = file_path.relative_to(item.source_path)
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, destination)
    else:
        destination = target / item.entry_path.name
        shutil.copy2(item.entry_path, destination)

    source_data = _public_source_data(item, report)
    source_data["scan_generated_at"] = report.generated_at
    (target / "source.json").write_text(
        json.dumps(source_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _public_source_data(item: ScanItem, report: ScanReport) -> dict[str, object]:
    source_root = _matching_source_root(item, report)
    data = item.to_dict()
    data["source_path"] = _public_path(item.source_path, source_root)
    data["entry_path"] = _public_path(item.entry_path, source_root)
    data["files"] = [_public_path(path, source_root) for path in item.files]
    data["source_root"] = _public_path(source_root, source_root) if source_root else None
    return data


def _matching_source_root(item: ScanItem, report: ScanReport) -> Path | None:
    candidates = sorted(report.roots, key=lambda path: len(path.parts), reverse=True)
    for root in candidates:
        try:
            item.source_path.relative_to(root)
        except ValueError:
            continue
        return root
    return None


def _public_path(path: Path, source_root: Path | None) -> str:
    if source_root is not None:
        try:
            relative = path.relative_to(source_root)
        except ValueError:
            pass
        else:
            root_label = _source_root_label(source_root)
            if str(relative) == ".":
                return root_label
            return f"{root_label}/{relative.as_posix()}"
    return path.name


def _source_root_label(source_root: Path) -> str:
    if source_root.name in {".codex", ".agents"}:
        return f"~/{source_root.name}"
    return source_root.name
