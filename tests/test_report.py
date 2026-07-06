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
                    ScanItem("skipped", "skill", "skipped", Path("/d"), Path("/d/SKILL.md"), "duplicate_same_content"),
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
        self.assertIn("## Skipped", markdown)
        self.assertIn("## Candidates", markdown)
        self.assertIn("## Blocked", markdown)
        self.assertIn("## Conflicts", markdown)
        self.assertIn("## Warnings", markdown)
        self.assertEqual(data["schema_version"], ScanReport.SCHEMA_VERSION)
        self.assertEqual(len(data["items"]), 5)


if __name__ == "__main__":
    unittest.main()
