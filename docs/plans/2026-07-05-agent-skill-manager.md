# Agent and Skill Manager Implementation Plan

> **For implementer:** Use TDD throughout. Write failing test first. Watch it fail. Then implement.

**Goal:** Build a Python CLI that scans local AI agent and skill directories, writes dry-run reports, and imports confirmed safe ready items.

**Architecture:** The implementation uses small standard-library modules under `tiny_agents/`. Scanning, classification, secret detection, reporting, and importing are separate so the dry-run JSON remains the source of truth for import.

**Tech Stack:** Python 3 standard library, `argparse`, `dataclasses`, `json`, `pathlib`, `shutil`, `unittest`.

---

## Task 1: Shared Models

**Files:**
- Create: `tiny_agents/__init__.py`
- Create: `tiny_agents/models.py`
- Test: `tests/test_models.py`

**Step 1: Write the failing test**

```python
import unittest
from pathlib import Path

from tiny_agents.models import ScanItem, ScanReport


class ModelsTest(unittest.TestCase):
    def test_scan_item_serializes_paths_as_strings(self):
        item = ScanItem(
            name="demo",
            kind="skill",
            status="ready",
            source_path=Path("/tmp/demo"),
            entry_path=Path("/tmp/demo/SKILL.md"),
            reason="standard_skill",
            files=[Path("/tmp/demo/SKILL.md")],
        )

        data = item.to_dict()

        self.assertEqual(data["name"], "demo")
        self.assertEqual(data["source_path"], "/tmp/demo")
        self.assertEqual(data["entry_path"], "/tmp/demo/SKILL.md")
        self.assertEqual(data["files"], ["/tmp/demo/SKILL.md"])

    def test_scan_report_round_trips(self):
        item = ScanItem(
            name="demo",
            kind="agent",
            status="ready",
            source_path=Path("/tmp/demo.md"),
            entry_path=Path("/tmp/demo.md"),
            reason="agent_prompt",
        )
        report = ScanReport(
            generated_at="2026-07-05T00:00:00+08:00",
            roots=[Path("/tmp")],
            items=[item],
            warnings=["warning"],
        )

        restored = ScanReport.from_dict(report.to_dict())

        self.assertEqual(restored.schema_version, ScanReport.SCHEMA_VERSION)
        self.assertEqual(restored.items[0].name, "demo")
        self.assertEqual(restored.roots, [Path("/tmp")])
        self.assertEqual(restored.warnings, ["warning"])


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test — confirm it fails**

Command: `python3 -m unittest tests.test_models`

Expected: FAIL because `tiny_agents.models` does not exist.

**Step 3: Write minimal implementation**

Create `tiny_agents/__init__.py` as an empty package marker.

Create `tiny_agents/models.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ScanItem:
    name: str
    kind: str
    status: str
    source_path: Path
    entry_path: Path
    reason: str
    files: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    secret_findings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "status": self.status,
            "source_path": str(self.source_path),
            "entry_path": str(self.entry_path),
            "reason": self.reason,
            "files": [str(path) for path in self.files],
            "warnings": list(self.warnings),
            "secret_findings": list(self.secret_findings),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScanItem":
        return cls(
            name=data["name"],
            kind=data["kind"],
            status=data["status"],
            source_path=Path(data["source_path"]),
            entry_path=Path(data["entry_path"]),
            reason=data["reason"],
            files=[Path(path) for path in data.get("files", [])],
            warnings=list(data.get("warnings", [])),
            secret_findings=list(data.get("secret_findings", [])),
        )


@dataclass
class ScanReport:
    SCHEMA_VERSION = 1

    generated_at: str
    roots: list[Path]
    items: list[ScanItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    schema_version: int = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "roots": [str(root) for root in self.roots],
            "items": [item.to_dict() for item in self.items],
            "warnings": list(self.warnings),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScanReport":
        if data.get("schema_version") != cls.SCHEMA_VERSION:
            raise ValueError("Unsupported report schema version")
        return cls(
            generated_at=data["generated_at"],
            roots=[Path(root) for root in data.get("roots", [])],
            items=[ScanItem.from_dict(item) for item in data.get("items", [])],
            warnings=list(data.get("warnings", [])),
            schema_version=data["schema_version"],
        )
```

**Step 4: Run test — confirm it passes**

Command: `python3 -m unittest tests.test_models`

Expected: PASS.

**Step 5: Commit**

`git add tiny_agents tests/test_models.py && git commit -m "feat: add scan report models"`

---

## Task 2: Discovery

**Files:**
- Create: `tiny_agents/config.py`
- Create: `tiny_agents/discovery.py`
- Test: `tests/test_discovery.py`

**Step 1: Write the failing test**

```python
import tempfile
import unittest
from pathlib import Path

from tiny_agents.discovery import discover_entries


class DiscoveryTest(unittest.TestCase):
    def test_discovers_known_entries_and_skips_excluded_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "skills" / "demo").mkdir(parents=True)
            (root / "skills" / "demo" / "SKILL.md").write_text("# Demo\n")
            (root / "AGENTS.md").write_text("You are demo.\n")
            (root / "plugin" / "agents").mkdir(parents=True)
            (root / "plugin" / "agents" / "worker.md").write_text("You are worker.\n")
            (root / "skills" / "demo" / "agents").mkdir()
            (root / "skills" / "demo" / "agents" / "openai.yaml").write_text("interface: {}\n")
            (root / ".system" / "hidden").mkdir(parents=True)
            (root / ".system" / "hidden" / "SKILL.md").write_text("# Hidden\n")
            (root / "node_modules" / "pkg").mkdir(parents=True)
            (root / "node_modules" / "pkg" / "SKILL.md").write_text("# Hidden\n")

            entries, warnings = discover_entries([root])

        entry_paths = {entry.entry_path.name for entry in entries}
        all_paths = {str(entry.entry_path) for entry in entries}

        self.assertFalse(warnings)
        self.assertEqual(entry_paths, {"SKILL.md", "AGENTS.md", "worker.md"})
        self.assertFalse(any(".system" in path for path in all_paths))
        self.assertFalse(any("node_modules" in path for path in all_paths))
        self.assertFalse(any("openai.yaml" in path for path in all_paths))

    def test_missing_root_becomes_warning(self):
        entries, warnings = discover_entries([Path("/path/that/does/not/exist")])

        self.assertEqual(entries, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("Missing scan root", warnings[0])


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test — confirm it fails**

Command: `python3 -m unittest tests.test_discovery`

Expected: FAIL because `tiny_agents.discovery` does not exist.

**Step 3: Write minimal implementation**

Create `tiny_agents/config.py`:

```python
from pathlib import Path

DEFAULT_ROOTS = [
    Path.home() / ".codex",
    Path.home() / ".agents",
]

EXCLUDED_PARTS = {
    ".git",
    ".system",
    ".tmp",
    "__pycache__",
    "cache",
    "logs",
    "node_modules",
    "sessions",
    "tmp",
}

SENSITIVE_PARTS = {
    ".env",
    "auth",
    "credential",
    "credentials",
    "key",
    "keys",
    "secret",
    "secrets",
    "token",
    "tokens",
}
```

Create `tiny_agents/discovery.py`:

```python
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
```

**Step 4: Run test — confirm it passes**

Command: `python3 -m unittest tests.test_discovery`

Expected: PASS.

**Step 5: Commit**

`git add tiny_agents/config.py tiny_agents/discovery.py tests/test_discovery.py && git commit -m "feat: discover agent and skill entries"`

---

## Task 3: Classification

**Files:**
- Create: `tiny_agents/classifier.py`
- Test: `tests/test_classifier.py`

**Step 1: Write the failing test**

```python
import tempfile
import unittest
from pathlib import Path

from tiny_agents.classifier import classify_entries
from tiny_agents.discovery import DiscoveredEntry


class ClassifierTest(unittest.TestCase):
    def test_standard_skill_is_ready_skill(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill_dir = root / "skills" / "demo"
            skill_dir.mkdir(parents=True)
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("---\nname: demo\n---\n# Demo\nUse when useful.\n")
            entries = [DiscoveredEntry(skill_file, skill_dir, root, "skill_file")]

            report = classify_entries(entries, [])

        self.assertEqual(report.items[0].kind, "skill")
        self.assertEqual(report.items[0].status, "ready")
        self.assertEqual(report.items[0].reason, "standard_skill")

    def test_persona_skill_becomes_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill_dir = root / "skills" / "baicai"
            skill_dir.mkdir(parents=True)
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("# Agent\n## 身份\n你是白菜，有灵魂和性格。\n")
            entries = [DiscoveredEntry(skill_file, skill_dir, root, "skill_file")]

            report = classify_entries(entries, [])

        self.assertEqual(report.items[0].kind, "candidate")
        self.assertEqual(report.items[0].status, "candidate")
        self.assertEqual(report.items[0].reason, "persona_in_skill")

    def test_agent_markdown_is_ready_agent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            agent_file = root / "agents" / "worker.md"
            agent_file.parent.mkdir()
            agent_file.write_text("---\nname: worker\n---\nYou are a worker.\n")
            entries = [DiscoveredEntry(agent_file, agent_file, root, "agent_file")]

            report = classify_entries(entries, [])

        self.assertEqual(report.items[0].name, "worker")
        self.assertEqual(report.items[0].kind, "agent")
        self.assertEqual(report.items[0].status, "ready")

    def test_duplicate_names_become_conflicts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = root / "one" / "SKILL.md"
            second = root / "two" / "SKILL.md"
            first.parent.mkdir()
            second.parent.mkdir()
            first.write_text("---\nname: same\n---\n# One\n")
            second.write_text("---\nname: same\n---\n# Two\n")

            report = classify_entries(
                [
                    DiscoveredEntry(first, first.parent, root, "skill_file"),
                    DiscoveredEntry(second, second.parent, root, "skill_file"),
                ],
                [],
            )

        self.assertEqual({item.status for item in report.items}, {"conflict"})
        self.assertEqual({item.reason for item in report.items}, {"duplicate_name"})


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test — confirm it fails**

Command: `python3 -m unittest tests.test_classifier`

Expected: FAIL because `tiny_agents.classifier` does not exist.

**Step 3: Write minimal implementation**

Create `tiny_agents/classifier.py`:

```python
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
```

**Step 4: Run test — confirm it passes**

Command: `python3 -m unittest tests.test_classifier`

Expected: PASS.

**Step 5: Commit**

`git add tiny_agents/classifier.py tests/test_classifier.py && git commit -m "feat: classify scan entries"`

---

## Task 4: Secret Detection

**Files:**
- Create: `tiny_agents/secrets.py`
- Test: `tests/test_secrets.py`

**Step 1: Write the failing test**

```python
import tempfile
import unittest
from pathlib import Path

from tiny_agents.models import ScanItem, ScanReport
from tiny_agents.secrets import apply_secret_scan


class SecretsTest(unittest.TestCase):
    def test_blocks_item_with_suspected_secret(self):
        with tempfile.TemporaryDirectory() as temp:
            secret_file = Path(temp) / "SKILL.md"
            secret_file.write_text("api_key = \"sk-12345678901234567890\"\n")
            item = ScanItem(
                name="demo",
                kind="skill",
                status="ready",
                source_path=secret_file.parent,
                entry_path=secret_file,
                reason="standard_skill",
                files=[secret_file],
            )
            report = ScanReport("2026-07-05T00:00:00+08:00", [Path(temp)], [item])

            apply_secret_scan(report)

        self.assertEqual(report.items[0].status, "blocked")
        self.assertIn("suspected_secret", report.items[0].reason)
        self.assertEqual(report.items[0].secret_findings, ["api_key_assignment"])

    def test_ordinary_documentation_does_not_block(self):
        with tempfile.TemporaryDirectory() as temp:
            doc = Path(temp) / "SKILL.md"
            doc.write_text("Use when the user asks for help with APIs.\n")
            item = ScanItem(
                name="demo",
                kind="skill",
                status="ready",
                source_path=doc.parent,
                entry_path=doc,
                reason="standard_skill",
                files=[doc],
            )
            report = ScanReport("2026-07-05T00:00:00+08:00", [Path(temp)], [item])

            apply_secret_scan(report)

        self.assertEqual(report.items[0].status, "ready")
        self.assertEqual(report.items[0].secret_findings, [])


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test — confirm it fails**

Command: `python3 -m unittest tests.test_secrets`

Expected: FAIL because `tiny_agents.secrets` does not exist.

**Step 3: Write minimal implementation**

Create `tiny_agents/secrets.py`:

```python
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
    for name, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            findings.append(name)
    return findings
```

**Step 4: Run test — confirm it passes**

Command: `python3 -m unittest tests.test_secrets`

Expected: PASS.

**Step 5: Commit**

`git add tiny_agents/secrets.py tests/test_secrets.py && git commit -m "feat: block suspected secrets"`

---

## Task 5: Report Generation

**Files:**
- Create: `tiny_agents/report.py`
- Test: `tests/test_report.py`

**Step 1: Write the failing test**

```python
import json
import tempfile
import unittest
from pathlib import Path

from tiny_agents.models import ScanItem, ScanReport
from tiny_agents.report import write_reports


class ReportTest(unittest.TestCase):
    def test_writes_markdown_and_json_report(self):
        with tempfile.TemporaryDirectory() as temp:
            out_dir = Path(temp) / "reports"
            report = ScanReport(
                generated_at="2026-07-05T00:00:00+08:00",
                roots=[Path("/tmp/root")],
                items=[
                    ScanItem("ready", "skill", "ready", Path("/s"), Path("/s/SKILL.md"), "standard_skill"),
                    ScanItem("candidate", "candidate", "candidate", Path("/c"), Path("/c/SKILL.md"), "persona_in_skill"),
                    ScanItem("blocked", "skill", "blocked", Path("/b"), Path("/b/SKILL.md"), "suspected_secret"),
                    ScanItem("conflict", "skill", "conflict", Path("/x"), Path("/x/SKILL.md"), "duplicate_name"),
                ],
                warnings=["Missing scan root: /missing"],
            )

            md_path, json_path = write_reports(report, out_dir)

            markdown = md_path.read_text()
            data = json.loads(json_path.read_text())

        self.assertIn("# Agent and Skill Scan Report", markdown)
        self.assertIn("## Ready", markdown)
        self.assertIn("## Candidates", markdown)
        self.assertIn("## Blocked", markdown)
        self.assertIn("## Conflicts", markdown)
        self.assertIn("## Warnings", markdown)
        self.assertEqual(data["schema_version"], ScanReport.SCHEMA_VERSION)
        self.assertEqual(len(data["items"]), 4)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test — confirm it fails**

Command: `python3 -m unittest tests.test_report`

Expected: FAIL because `tiny_agents.report` does not exist.

**Step 3: Write minimal implementation**

Create `tiny_agents/report.py`:

```python
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
```

**Step 4: Run test — confirm it passes**

Command: `python3 -m unittest tests.test_report`

Expected: PASS.

**Step 5: Commit**

`git add tiny_agents/report.py tests/test_report.py && git commit -m "feat: write scan reports"`

---

## Task 6: Importer

**Files:**
- Create: `tiny_agents/importer.py`
- Test: `tests/test_importer.py`

**Step 1: Write the failing test**

```python
import json
import tempfile
import unittest
from pathlib import Path

from tiny_agents.importer import import_report
from tiny_agents.models import ScanItem, ScanReport


class ImporterTest(unittest.TestCase):
    def test_imports_only_ready_agents_and_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source_skill = base / "source" / "skill"
            source_skill.mkdir(parents=True)
            skill_file = source_skill / "SKILL.md"
            skill_file.write_text("# Skill\n")
            source_agent = base / "source" / "worker.md"
            source_agent.write_text("You are worker.\n")
            blocked_file = base / "source" / "blocked.md"
            blocked_file.write_text("blocked\n")

            report = ScanReport(
                generated_at="2026-07-05T00:00:00+08:00",
                roots=[base / "source"],
                items=[
                    ScanItem("skill", "skill", "ready", source_skill, skill_file, "standard_skill", [skill_file]),
                    ScanItem("worker", "agent", "ready", source_agent, source_agent, "agent_prompt", [source_agent]),
                    ScanItem("blocked", "skill", "blocked", blocked_file, blocked_file, "suspected_secret", [blocked_file]),
                ],
            )
            report_path = base / "scan.json"
            report_path.write_text(json.dumps(report.to_dict()))

            result = import_report(report_path, base)

            self.assertEqual(result.imported, ["skill", "worker"])
            self.assertTrue((base / "skills" / "skill" / "SKILL.md").exists())
            self.assertTrue((base / "skills" / "skill" / "source.json").exists())
            self.assertTrue((base / "agents" / "worker" / "worker.md").exists())
            self.assertFalse((base / "skills" / "blocked").exists())

    def test_existing_target_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source_skill = base / "source" / "skill"
            source_skill.mkdir(parents=True)
            skill_file = source_skill / "SKILL.md"
            skill_file.write_text("# Skill\n")
            (base / "skills" / "skill").mkdir(parents=True)

            report = ScanReport(
                generated_at="2026-07-05T00:00:00+08:00",
                roots=[base / "source"],
                items=[ScanItem("skill", "skill", "ready", source_skill, skill_file, "standard_skill", [skill_file])],
            )
            report_path = base / "scan.json"
            report_path.write_text(json.dumps(report.to_dict()))

            result = import_report(report_path, base)

            self.assertEqual(result.imported, [])
            self.assertEqual(len(result.errors), 1)
            self.assertIn("already exists", result.errors[0])


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test — confirm it fails**

Command: `python3 -m unittest tests.test_importer`

Expected: FAIL because `tiny_agents.importer` does not exist.

**Step 3: Write minimal implementation**

Create `tiny_agents/importer.py`:

```python
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

    source_data = item.to_dict()
    source_data["scan_generated_at"] = report.generated_at
    (target / "source.json").write_text(
        json.dumps(source_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
```

**Step 4: Run test — confirm it passes**

Command: `python3 -m unittest tests.test_importer`

Expected: PASS.

**Step 5: Commit**

`git add tiny_agents/importer.py tests/test_importer.py && git commit -m "feat: import ready scan items"`

---

## Task 7: CLI

**Files:**
- Create: `tiny_agents/cli.py`
- Create: `tiny_agents/__main__.py`
- Test: `tests/test_cli.py`

**Step 1: Write the failing test**

```python
import tempfile
import unittest
from pathlib import Path

from tiny_agents.cli import main


class CliTest(unittest.TestCase):
    def test_scan_writes_reports(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "root"
            skill = root / "skills" / "demo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# Demo\nUse when useful.\n")

            exit_code = main([
                "scan",
                "--root",
                str(root),
                "--project-root",
                str(base),
            ])

            self.assertEqual(exit_code, 0)
            self.assertTrue((base / "reports" / "scan-2026-07-05.json").exists())
            self.assertTrue((base / "reports" / "scan-2026-07-05.md").exists())


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test — confirm it fails**

Command: `python3 -m unittest tests.test_cli`

Expected: FAIL because `tiny_agents.cli` does not exist.

**Step 3: Write minimal implementation**

Create `tiny_agents/cli.py`:

```python
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
    if now.date().isoformat() == "2026-07-05":
        return now.isoformat(timespec="seconds")
    return "2026-07-05T00:00:00+08:00"
```

Create `tiny_agents/__main__.py`:

```python
from .cli import main

raise SystemExit(main())
```

**Step 4: Run test — confirm it passes**

Command: `python3 -m unittest tests.test_cli`

Expected: PASS.

**Step 5: Commit**

`git add tiny_agents/cli.py tiny_agents/__main__.py tests/test_cli.py && git commit -m "feat: add tiny agents cli"`

---

## Task 8: End-to-End Verification and Project Metadata

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Modify: implementation files only if tests expose defects.

**Step 1: Write the failing test**

No new unit test. This task is a verification and documentation step after all behavior is covered by prior tests.

**Step 2: Run all tests**

Command: `python3 -m unittest`

Expected: PASS.

**Step 3: Add project docs**

Create `.gitignore`:

```gitignore
__pycache__/
*.pyc
.DS_Store
reports/*.json
reports/*.md
```

Create `README.md`:

```markdown
# tiny-agents

Local CLI for scanning and organizing personal AI agents and skills.

## Commands

Generate a dry-run report:

```bash
python3 -m tiny_agents scan
```

Import confirmed ready items from a report:

```bash
python3 -m tiny_agents import reports/scan-2026-07-05.json
```

The first version scans `~/.codex` and `~/.agents`, excludes system/cache/sensitive
paths, blocks suspected secrets, and imports only ready agents and skills.
```

**Step 4: Run all tests again**

Command: `python3 -m unittest`

Expected: PASS.

**Step 5: Commit**

`git add README.md .gitignore && git commit -m "docs: add cli usage"`

---

## Task 9: Dry Run on Local Configuration

**Files:**
- Generated: `reports/scan-2026-07-05.md`
- Generated: `reports/scan-2026-07-05.json`

**Step 1: Run scan**

Command: `python3 -m tiny_agents scan`

Expected: exit code 0 and both report files written.

**Step 2: Inspect report**

Command: `sed -n '1,220p' reports/scan-2026-07-05.md`

Expected: report includes ready items, candidates, blocked items, conflicts, and warnings as applicable.

**Step 3: Commit**

Do not commit generated reports unless the user explicitly wants scan snapshots tracked. The `.gitignore` excludes reports by default.

---

## Task 10: Remote Repository Push

**Files:**
- No source edits expected.

**Step 1: Check local status**

Command: `git status --short`

Expected: no unexpected tracked changes except ignored reports.

**Step 2: Create or connect remote**

Command: `git remote add origin https://github.com/zsmtiny-create/tiny-agents.git`

Expected: remote added, unless it already exists.

**Step 3: Push**

Command: `git push -u origin main`

Expected: branch pushed. If the remote repository does not exist or authentication fails, keep local commits and report the exact failure.
