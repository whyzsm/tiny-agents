from __future__ import annotations

import re
from pathlib import Path

from .models import ScanReport

SECRET_PATTERNS = [
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    (
        "api_key_assignment",
        re.compile(r"(?i)\b(api[_-]?key|secret|token|credential|password)\b\s*[:=]\s*[\"'][^\"']{12,}[\"']"),
    ),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")),
]


def apply_secret_scan(report: ScanReport) -> None:
    for item in report.items:
        if item.status not in {"ready", "candidate"}:
            continue
        findings: list[str] = []
        for file_path in item.files or [item.entry_path]:
            findings.extend(_scan_file(file_path))
        item.secret_findings = sorted(set(findings))
        if item.secret_findings:
            item.status = "blocked"
            item.reason = f"{item.reason}:suspected_secret"


def _scan_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    findings: list[str] = []
    lines = _scannable_lines(path, text)
    scannable_text = "\n".join(lines)
    for name, pattern in SECRET_PATTERNS:
        if pattern.search(scannable_text):
            findings.append(name)
    if "api_key_assignment" in findings and "openai_key" in findings:
        findings.remove("openai_key")
    return findings


def _scannable_lines(path: Path, text: str) -> list[str]:
    if path.suffix.lower() not in {".md", ".markdown"}:
        return text.splitlines()

    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence or _looks_like_markdown_table_row(stripped):
            continue
        lines.append(line)
    return lines


def _looks_like_markdown_table_row(stripped: str) -> bool:
    return stripped.startswith("|") and stripped.endswith("|")
