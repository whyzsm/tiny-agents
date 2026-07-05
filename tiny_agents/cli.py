from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from .classifier import classify_entries
from .config import DEFAULT_ROOTS
from .discovery import discover_entries
from .importer import import_report
from .report import write_reports
from .secrets import apply_secret_scan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tiny-agents")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan")
    scan_parser.add_argument("--root", action="append", type=Path, dest="roots")
    scan_parser.add_argument("--project-root", type=Path, default=Path.cwd())

    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("report", type=Path)
    import_parser.add_argument("--project-root", type=Path, default=Path.cwd())

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        return _scan(args.roots or DEFAULT_ROOTS, args.project_root)
    if args.command == "import":
        return _import(args.report, args.project_root)
    parser.error("Unknown command")
    return 2


def _scan(roots: list[Path], project_root: Path) -> int:
    entries, warnings = discover_entries(roots)
    report = classify_entries(entries, warnings)
    report.generated_at = _now_for_report()
    apply_secret_scan(report)
    md_path, json_path = write_reports(report, project_root / "reports")
    print(f"Wrote {md_path}")
    print(f"Wrote {json_path}")
    return 0


def _import(report_path: Path, project_root: Path) -> int:
    result = import_report(report_path, project_root)
    for name in result.imported:
        print(f"Imported {name}")
    for name in result.skipped:
        print(f"Skipped {name}")
    for error in result.errors:
        print(f"Error: {error}")
    return 1 if result.errors else 0


def _now_for_report() -> str:
    now = datetime.now(timezone.utc).astimezone()
    return now.isoformat(timespec="seconds")
