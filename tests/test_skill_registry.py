import json
import tempfile
import unittest
from pathlib import Path

from scripts import generate_skill_registry


class SkillRegistryTest(unittest.TestCase):
    def test_generates_canonical_registry_for_repo_skills_only(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            skills_root = base / "skills"
            package = skills_root / "demo-skill"
            package.mkdir(parents=True)
            (package / "SKILL.md").write_text(
                "---\nname: Demo Skill\ndescription: Demo skill description.\n---\n"
                "# Demo Skill\n\n## Overview\nUse when you need a demo workflow.\n",
                encoding="utf-8",
            )

            legacy = skills_root / "legacy-skill"
            legacy.mkdir()
            (legacy / "skill.md").write_text(
                "# Legacy Skill\n\n## Purpose\nUse when you need a legacy workflow.\n",
                encoding="utf-8",
            )
            (legacy / "source.json").write_text(
                json.dumps({"status": "ready", "source_ref": "repo-local/skills/legacy-skill"}),
                encoding="utf-8",
            )

            draft = skills_root / "draft-skill"
            draft.mkdir()
            (draft / "SKILL.md").write_text("# Draft Skill\n", encoding="utf-8")
            (draft / "source.json").write_text(json.dumps({"status": "draft"}), encoding="utf-8")

            agent_root = base / "agents" / "worker"
            agent_root.mkdir(parents=True)
            (agent_root / "worker.md").write_text("You are worker.\n", encoding="utf-8")

            exit_code = generate_skill_registry.main(["--project-root", str(base)])
            data = json.loads((base / "indexes" / "skill-registry.json").read_text())
            markdown = (base / "indexes" / "skill-registry.md").read_text()

        self.assertEqual(exit_code, 0)
        self.assertEqual([entry["name"] for entry in data["entries"]], ["demo-skill", "legacy-skill"])
        self.assertEqual(data["entries"][0]["entry_path"], "skills/demo-skill/SKILL.md")
        self.assertEqual(data["entries"][1]["entry_path"], "skills/legacy-skill/skill.md")
        self.assertNotIn("draft-skill", json.dumps(data))
        self.assertNotIn("worker", json.dumps(data))
        self.assertNotIn(str(Path.home()), json.dumps(data))
        self.assertIn("Demo Skill", markdown)
        self.assertIn("Legacy Skill", markdown)
        self.assertIn("## Omitted", markdown)


if __name__ == "__main__":
    unittest.main()
