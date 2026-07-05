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
