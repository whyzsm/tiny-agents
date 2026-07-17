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

    def test_catalog_child_entry_modes_are_classified(self):
        catalog = (self.root / "catalog").resolve()
        skills = catalog / "skills"
        index = catalog / "indexes/expert-team-file-list.md"
        for name in ("real-one", "real-two", "hybrid-real"):
            (skills / name).mkdir(parents=True)
            (skills / name / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: test\n---\n# {name}\n",
                encoding="utf-8",
            )
        index.parent.mkdir(parents=True)
        index.write_text(
            "\n".join(
                [
                    "| 分类 | 专家团 | 名称 | 子技能 |",
                    "|---|---|---|---|",
                    "| 技术 | [`all-team`](../skills/all-team/SKILL.md) | All Team | `real-one`<br>`real-two` |",
                    "| 技术 | [`hybrid-team`](../skills/hybrid-team/SKILL.md) | Hybrid Team | `hybrid-real`<br>`internal-label` |",
                    "| 技术 | [`internal-team`](../skills/internal-team/SKILL.md) | Internal Team | `intake`<br>`handoff` |",
                ]
            ),
            encoding="utf-8",
        )

        entries = {entry.team_id: entry for entry in COMPOSE.discover.read_local_index(catalog, index.resolve())}

        self.assertEqual(entries["all-team"].child_entry_mode, "all-top-level-skills")
        self.assertEqual(entries["all-team"].top_level_child_skills, ("real-one", "real-two"))
        self.assertEqual(entries["hybrid-team"].child_entry_mode, "hybrid")
        self.assertEqual(entries["hybrid-team"].top_level_child_skills, ("hybrid-real",))
        self.assertEqual(entries["hybrid-team"].internal_child_labels, ("internal-label",))
        self.assertEqual(entries["internal-team"].child_entry_mode, "internal-router-labels")
        self.assertEqual(entries["internal-team"].internal_child_labels, ("intake", "handoff"))

    def test_hybrid_catalog_candidates_do_not_dispatch_internal_labels(self):
        task = "安全审计和质量 review"
        scan = COMPOSE.scan_project(self.root, task)
        index = REPO_ROOT / "indexes/expert-team-file-list.md"
        entries = [
            entry
            for entry in COMPOSE.discover.read_local_index(REPO_ROOT, index)
            if entry.team_id == "tech-software-workshop"
        ]

        candidates = COMPOSE.build_candidates(entries, task, scan, True)
        review_skills = {candidate["skill"] for candidate in candidates["review"]}
        selected_entry_kinds = {candidate["selected_entry_kind"] for candidate in candidates["review"]}

        self.assertIn("security-audit", review_skills)
        self.assertNotIn("code-review", review_skills)
        self.assertNotIn("qa-testing", review_skills)
        self.assertEqual(selected_entry_kinds, {"top-level-child-skill"})

    def test_local_installed_capabilities_precede_catalog_and_use_name_boundaries(self):
        installed = self.root / "installed-skills"
        (installed / "playwright").mkdir(parents=True)
        (installed / "service-widget").mkdir(parents=True)
        (installed / "ui-audit").mkdir(parents=True)
        (installed / "playwright/SKILL.md").write_text(
            '---\nname: playwright\ndescription: Browser journeys\n---\n# Playwright\n',
            encoding="utf-8",
        )
        (installed / "service-widget/SKILL.md").write_text(
            '---\nname: service-widget\ndescription: Build service widgets\n---\n# Service Widget\n',
            encoding="utf-8",
        )
        (installed / "ui-audit/SKILL.md").write_text(
            '---\nname: ui-audit\ndescription: Review UI accessibility and quality\n---\n# UI Audit\n',
            encoding="utf-8",
        )
        task = "测试页面 API mock 和回归风险"
        scan = COMPOSE.scan_project(self.root, task)
        local, discovery = COMPOSE.discover_local_candidates(
            self.root,
            task,
            scan,
            [(installed, "installed-skill")],
            [],
        )

        self.assertEqual(discovery["skills"], 3)
        self.assertEqual(local["e2e-testing"][0]["skill"], "playwright")
        self.assertEqual(local["review"][0]["skill"], "ui-audit")
        self.assertFalse(any(item["skill"] == "service-widget" for item in local["api-testing"]))

        catalog = {
            key: [{"skill": "remote-skill", "source_kind": "remote-catalog", "score": 1}]
            for key in (slot.key for slot in COMPOSE.SLOTS)
        }
        merged = COMPOSE.merge_candidates(local, catalog)
        self.assertEqual(merged["e2e-testing"][0]["skill"], "playwright")


if __name__ == "__main__":
    unittest.main()
