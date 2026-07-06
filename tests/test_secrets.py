import tempfile
import unittest
from pathlib import Path

from tiny_agents.models import ScanItem, ScanReport
from tiny_agents.secrets import apply_secret_scan


class SecretsTest(unittest.TestCase):
    def test_blocks_item_with_suspected_secret(self):
        with tempfile.TemporaryDirectory() as temp:
            secret_file = Path(temp) / "SKILL.md"
            secret_file.write_text('api_key = "sk-12345678901234567890"\n')
            item = ScanItem(
                name="demo",
                kind="skill",
                status="ready",
                source_path=secret_file.parent,
                entry_path=secret_file,
                reason="standard_skill",
                files=[secret_file],
            )
            report = ScanReport("2026-07-05T00:00:00+08:00", [Path(temp)], [item])

            apply_secret_scan(report)

        self.assertEqual(report.items[0].status, "blocked")
        self.assertIn("suspected_secret", report.items[0].reason)
        self.assertEqual(report.items[0].secret_findings, ["api_key_assignment"])

    def test_ordinary_documentation_does_not_block(self):
        with tempfile.TemporaryDirectory() as temp:
            doc = Path(temp) / "SKILL.md"
            doc.write_text("Use when the user asks for help with APIs.\n")
            item = ScanItem(
                name="demo",
                kind="skill",
                status="ready",
                source_path=doc.parent,
                entry_path=doc,
                reason="standard_skill",
                files=[doc],
            )
            report = ScanReport("2026-07-05T00:00:00+08:00", [Path(temp)], [item])

            apply_secret_scan(report)

        self.assertEqual(report.items[0].status, "ready")
        self.assertEqual(report.items[0].secret_findings, [])

    def test_markdown_examples_do_not_block(self):
        with tempfile.TemporaryDirectory() as temp:
            doc = Path(temp) / "SKILL.md"
            doc.write_text(
                "\n".join(
                    [
                        "```js",
                        'const API_KEY = "sk-12345678901234567890"',
                        "```",
                        '| `process.env.API_KEY` | `const API_KEY = "sk-12345678901234567890"` |',
                    ]
                )
            )
            item = ScanItem(
                name="demo",
                kind="skill",
                status="ready",
                source_path=doc.parent,
                entry_path=doc,
                reason="standard_skill",
                files=[doc],
            )
            report = ScanReport("2026-07-05T00:00:00+08:00", [Path(temp)], [item])

            apply_secret_scan(report)

        self.assertEqual(report.items[0].status, "ready")
        self.assertEqual(report.items[0].secret_findings, [])


if __name__ == "__main__":
    unittest.main()
