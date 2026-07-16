import json
import tempfile
import unittest
from pathlib import Path

from scripts import generate_index


class GenerateIndexTest(unittest.TestCase):
    def test_generates_project_agent_and_skill_index(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            skill_dir = base / "skills" / "demo"
            skill_dir.mkdir(parents=True)
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text(
                f"---\nname: legacy-demo\ndescription: Use at {Path.home()}/private\n---\n# Demo\nUse when useful.\n"
            )

            skipped_skill = base / "skills" / "skipped"
            skipped_skill.mkdir()
            (skipped_skill / "SKILL.md").write_text("# Skipped\n", encoding="utf-8")
            (skipped_skill / "source.json").write_text(
                json.dumps({"status": "skipped"}), encoding="utf-8"
            )

            agent_dir = base / "agents" / "worker"
            agent_dir.mkdir(parents=True)
            (agent_dir / "worker.md").write_text(
                "---\nname: Worker Agent\n---\n# Worker\n\n## Task\nDo worker tasks.\n",
                encoding="utf-8",
            )

            exit_code = generate_index.main(["--project-root", str(base)])

            data = json.loads((base / "indexes" / "agent-skill-index.json").read_text())
            markdown = (base / "indexes" / "agent-skill-index.md").read_text()

        self.assertEqual(exit_code, 0)
        self.assertEqual(data["project_root"], ".")
        self.assertEqual(data["agents_root"], "agents")
        self.assertEqual(data["skills_root"], "skills")
        self.assertEqual(data["total"], 2)
        self.assertEqual([entry["name"] for entry in data["entries"]], ["worker", "demo"])
        self.assertEqual(data["entries"][0]["display_name"], "Worker Agent")
        self.assertEqual(data["entries"][1]["display_name"], "demo")
        self.assertEqual(data["entries"][0]["source_path"], "agents/worker")
        self.assertEqual(data["entries"][1]["entry_path"], "skills/demo/SKILL.md")
        self.assertNotIn(str(Path.home()), json.dumps(data))
        self.assertNotIn("skipped", json.dumps(data["entries"]))
        self.assertIn("~/private", data["entries"][1]["description"])
        self.assertIn("# Agent And Skill Index", markdown)


if __name__ == "__main__":
    unittest.main()
