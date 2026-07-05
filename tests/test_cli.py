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
