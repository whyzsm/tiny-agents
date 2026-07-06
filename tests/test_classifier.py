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

    def test_identical_duplicates_keep_one_ready_item(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            codex = root / ".codex" / "skills" / "same" / "SKILL.md"
            agents = root / ".agents" / "skills" / "same" / "SKILL.md"
            codex.parent.mkdir(parents=True)
            agents.parent.mkdir(parents=True)
            text = "---\nname: same\n---\n# Same\n"
            codex.write_text(text)
            agents.write_text(text)

            report = classify_entries(
                [
                    DiscoveredEntry(codex, codex.parent, root / ".codex", "skill_file"),
                    DiscoveredEntry(agents, agents.parent, root / ".agents", "skill_file"),
                ],
                [],
            )

        statuses = {item.source_path.parts[-3]: item.status for item in report.items}
        reasons = {item.status: item.reason for item in report.items}
        self.assertEqual(statuses[".codex"], "ready")
        self.assertEqual(statuses[".agents"], "skipped")
        self.assertEqual(reasons["skipped"], "duplicate_same_content")


if __name__ == "__main__":
    unittest.main()
