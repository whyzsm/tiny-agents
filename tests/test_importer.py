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
