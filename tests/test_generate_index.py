import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import generate_index


class GenerateIndexTest(unittest.TestCase):
    def test_generates_from_latest_report_and_excludes_skipped(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            reports = base / "reports"
            reports.mkdir()
            skill_dir = base / "skills" / "demo"
            skill_dir.mkdir(parents=True)
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text(
                f"---\nname: demo\ndescription: Use at {Path.home()}/private\n---\n# Demo\nUse when useful.\n"
            )
            old_report = reports / "scan-2026-07-05.json"
            old_report.write_text(json.dumps(_report("old", [])))
            new_report = reports / "scan-2026-07-06.json"
            new_report.write_text(
                json.dumps(
                    _report(
                        "new",
                        [
                            _item("demo", "skill", "ready", skill_dir, skill_file),
                            _item("dupe", "skill", "skipped", skill_dir, skill_file),
                        ],
                    )
                )
            )

            with patch.object(generate_index, "INDEX_DIR", base / "indexes"), patch.object(
                generate_index, "JSON_INDEX_PATH", base / "indexes" / "agent-skill-index.json"
            ), patch.object(
                generate_index, "MD_INDEX_PATH", base / "indexes" / "agent-skill-index.md"
            ):
                cwd = Path.cwd()
                try:
                    os.chdir(base)
                    exit_code = generate_index.main([])
                finally:
                    os.chdir(cwd)

            data = json.loads((base / "indexes" / "agent-skill-index.json").read_text())

        self.assertEqual(exit_code, 0)
        self.assertEqual(data["source_report"], str(new_report.relative_to(base)))
        self.assertEqual([entry["name"] for entry in data["entries"]], ["demo"])
        self.assertNotIn(str(Path.home()), json.dumps(data))
        self.assertIn("~/private", data["entries"][0]["description"])


def _report(generated_at: str, items: list[dict[str, object]]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "roots": [],
        "items": items,
        "warnings": [],
    }


def _item(
    name: str,
    kind: str,
    status: str,
    source_path: Path,
    entry_path: Path,
    description: str = "standard_skill",
) -> dict[str, object]:
    return {
        "name": name,
        "kind": kind,
        "status": status,
        "source_path": str(source_path),
        "entry_path": str(entry_path),
        "reason": description,
        "files": [str(entry_path)],
        "warnings": [],
        "secret_findings": [],
    }


if __name__ == "__main__":
    unittest.main()
