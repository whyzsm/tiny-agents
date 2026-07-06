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
            (root / "vendor_imports" / "skills" / "cached").mkdir(parents=True)
            (root / "vendor_imports" / "skills" / "cached" / "SKILL.md").write_text("# Cached\n")
            (root / "backups" / "old").mkdir(parents=True)
            (root / "backups" / "old" / "SKILL.md").write_text("# Backup\n")
            (root / "skill-backups" / "old").mkdir(parents=True)
            (root / "skill-backups" / "old" / "SKILL.md").write_text("# Backup\n")
            (root / "skill-update-backups" / "old").mkdir(parents=True)
            (root / "skill-update-backups" / "old" / "SKILL.md").write_text("# Backup\n")

            entries, warnings = discover_entries([root])

        entry_paths = {entry.entry_path.name for entry in entries}
        all_paths = {str(entry.entry_path) for entry in entries}

        self.assertFalse(warnings)
        self.assertEqual(entry_paths, {"SKILL.md", "AGENTS.md", "worker.md"})
        self.assertFalse(any(".system" in path for path in all_paths))
        self.assertFalse(any("node_modules" in path for path in all_paths))
        self.assertFalse(any("vendor_imports" in path for path in all_paths))
        self.assertFalse(any("backups" in path for path in all_paths))
        self.assertFalse(any("skill-backups" in path for path in all_paths))
        self.assertFalse(any("skill-update-backups" in path for path in all_paths))
        self.assertFalse(any("openai.yaml" in path for path in all_paths))

    def test_missing_root_becomes_warning(self):
        entries, warnings = discover_entries([Path("/path/that/does/not/exist")])

        self.assertEqual(entries, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("Missing scan root", warnings[0])


if __name__ == "__main__":
    unittest.main()
