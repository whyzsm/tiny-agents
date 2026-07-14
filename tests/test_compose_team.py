import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills/assemble-project-expert-team/scripts/compose_team.py"
SPEC = importlib.util.spec_from_file_location("compose_team_test_module", SCRIPT)
COMPOSE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMPOSE
SPEC.loader.exec_module(COMPOSE)


class ComposeTeamTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / ".github/workflows").mkdir(parents=True)
        (self.root / "src/pages/learningVideoPush").mkdir(parents=True)
        (self.root / "mock").mkdir()
        (self.root / "tests").mkdir()
        (self.root / "package.json").write_text(
            json.dumps(
                {
                    "name": "fixture-project",
                    "dependencies": {"react": "18", "umi": "3", "axios": "1"},
                    "scripts": {"test": "umi test", "build": "umi build"},
                }
            ),
            encoding="utf-8",
        )
        (self.root / "src/pages/learningVideoPush/index.js").write_text(
            "export default function Page() { return request('/api/learning-video-push/query'); }\n",
            encoding="utf-8",
        )
        (self.root / "mock/learningVideoPush.js").write_text(
            "export default { 'GET /api/learning-video-push/query': {} };\n",
            encoding="utf-8",
        )
        (self.root / "tests/learningVideoPush.test.js").write_text("test('page', () => {});\n", encoding="utf-8")
        (self.root / ".github/workflows/test.yml").write_text("name: test\n", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_scan_detects_frontend_route_api_mock_test_and_ci(self):
        scan = COMPOSE.scan_project(self.root, "测试 /support/learningVideoPush")

        self.assertEqual(scan["stack"], ["axios", "react", "umi"])
        self.assertTrue(scan["signals"]["has_routes"])
        self.assertTrue(scan["signals"]["has_api"])
        self.assertTrue(scan["signals"]["has_mocks"])
        self.assertTrue(scan["signals"]["has_tests"])
        self.assertTrue(scan["signals"]["has_ci"])
        self.assertIn("src/pages/learningVideoPush/index.js", scan["affected_files"])

    def test_local_catalog_composes_expected_slots_and_dag(self):
        task = "测试 /support/learningVideoPush 的列表、导入和 API mock 回归"
        scan = COMPOSE.scan_project(self.root, task)
        index = REPO_ROOT / "indexes/expert-team-file-list.md"
        entries = COMPOSE.discover.rank(
            COMPOSE.discover.read_local_index(REPO_ROOT, index),
            COMPOSE.build_query(task, scan),
        )
        candidates = COMPOSE.build_candidates(entries, task, scan, True)
        roster = COMPOSE.choose_roster(
            candidates,
            task,
            scan,
            "blueprint",
            True,
            REPO_ROOT,
            5,
            5,
            True,
        )
        slots = {member["slot"] for member in roster}
        skills = {member["skill"] for member in roster}
        self.assertEqual(slots, {"requirements", "unit-testing", "e2e-testing", "api-testing"})
        self.assertTrue({"requirements-analysis", "test-patterns", "e2e-testing-patterns", "qa-api-tester"} <= skills)

        phases = COMPOSE.compose_phases(roster, "blueprint")
        self.assertEqual(phases[0]["id"], "phase-1-contract")
        self.assertEqual(phases[1]["id"], "phase-3-validation")
        self.assertEqual(phases[1]["depends_on"], ["phase-1-contract"])
        self.assertTrue(phases[1]["parallel"])


if __name__ == "__main__":
    unittest.main()
