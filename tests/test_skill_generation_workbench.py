import json
import importlib.util
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills/skill-generation-workbench/scripts/scaffold_skill.py"
SPEC = importlib.util.spec_from_file_location("skill_generation_workbench_scaffold", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load {SCRIPT}")
scaffold_skill = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = scaffold_skill
SPEC.loader.exec_module(scaffold_skill)


class ScaffoldSkillTest(unittest.TestCase):
    def test_creates_valid_skeleton_and_sanitized_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            args = Namespace(
                name="Demo Skill",
                path=temp_dir,
                description="Create a demo Skill when a user asks for a demo workflow.",
                display_name="Demo Skill",
                short_description="Create a demo Skill package",
                default_prompt="Use $demo-skill to create a demo Skill.",
                resources="references,scripts",
            )

            skill_dir = scaffold_skill.create_skill(args)

            self.assertEqual(skill_dir.name, "demo-skill")
            self.assertTrue((skill_dir / "SKILL.md").is_file())
            self.assertTrue((skill_dir / "agents/openai.yaml").is_file())
            self.assertTrue((skill_dir / "references").is_dir())
            self.assertTrue((skill_dir / "scripts").is_dir())
            source = json.loads((skill_dir / "source.json").read_text())
            self.assertEqual(source["status"], "draft")
            self.assertEqual(source["source_ref"], "repo-local/generated")
            self.assertNotIn(str(Path(temp_dir).resolve()), json.dumps(source))

            skill_text = (skill_dir / "SKILL.md").read_text()
            self.assertIn("name: demo-skill", skill_text)
            self.assertIn("Create a demo Skill", skill_text)
            self.assertIn("$demo-skill", (skill_dir / "agents/openai.yaml").read_text())

    def test_refuses_to_overwrite_existing_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            existing = Path(temp_dir) / "demo-skill"
            existing.mkdir()
            sentinel = existing / "sentinel.txt"
            sentinel.write_text("keep")
            args = Namespace(
                name="demo-skill",
                path=temp_dir,
                description="Create a demo Skill.",
                display_name="",
                short_description="",
                default_prompt="",
                resources="",
            )

            with self.assertRaises(FileExistsError):
                scaffold_skill.create_skill(args)
            self.assertEqual(sentinel.read_text(), "keep")

    def test_rejects_unknown_resource(self):
        with self.assertRaises(ValueError):
            scaffold_skill.parse_resources("references,unknown")


if __name__ == "__main__":
    unittest.main()
