from __future__ import annotations

import json
from pathlib import Path

from .models import ScanItem, ScanReport


def write_reports(report: ScanReport, reports_dir: Path) -> tuple[Path, Path]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    date = report.generated_at[:10]
    md_path = reports_dir / f"scan-{date}.md"
    json_path = reports_dir / f"scan-{date}.json"

    md_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return md_path, json_path


def render_markdown(report: ScanReport) -> str:
    lines = [
        "# Agent and Skill Scan Report",
        "",
        f"- Generated: `{report.generated_at}`",
        f"- Schema version: `{report.schema_version}`",
        "",
        "## Roots",
        "",
    ]
    lines.extend(f"- `{root}`" for root in report.roots)
    lines.append("")

    sections = [
        ("Ready", lambda item: item.status == "ready"),
        ("Candidates", lambda item: item.status == "candidate"),
        ("Blocked", lambda item: item.status == "blocked"),
        ("Conflicts", lambda item: item.status == "conflict"),
    ]
    for title, predicate in sections:
        lines.extend([f"## {title}", ""])
        matching = [item for item in report.items if predicate(item)]
        if matching:
            lines.extend(_render_item(item) for item in matching)
        else:
            lines.append("- None")
        lines.append("")

    lines.extend(["## Warnings", ""])
    if report.warnings:
        lines.extend(f"- {warning}" for warning in report.warnings)
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def _render_item(item: ScanItem) -> str:
    details = f"{item.kind} / {item.reason}"
    if item.secret_findings:
        details += f" / secrets: {', '.join(item.secret_findings)}"
    return f"- `{item.name}` ({details}) from `{item.source_path}`"
