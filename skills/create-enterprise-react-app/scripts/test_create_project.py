#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("create_project.py")


class CreateProjectTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_creates_project_and_replaces_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / "ops-console"
            result = self.run_script(str(target), "--title", "Northstar Console")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"name": "ops-console"', (target / "package.json").read_text())
            self.assertIn("Northstar Console", (target / "index.html").read_text())
            self.assertTrue((target / "src" / "main.tsx").is_file())

    def test_refuses_nonempty_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / "existing"
            target.mkdir()
            (target / "keep.txt").write_text("user data", encoding="utf-8")

            result = self.run_script(str(target))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not empty", result.stderr)
            self.assertEqual((target / "keep.txt").read_text(), "user data")

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / "preview"
            result = self.run_script(str(target), "--dry-run")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
