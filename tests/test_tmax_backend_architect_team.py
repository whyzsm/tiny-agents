import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = REPO_ROOT / "skills" / "tech-backend-architect-team"
UPGRADED = REPO_ROOT / "skills" / "tech-tmax-backend-architect-team"
DISPATCH_AGENT = REPO_ROOT / "agents" / "tmax-backend-dispatch-agent"
TRACKS = {
    "repo-intake",
    "architecture-design",
    "api-data-contract",
    "implementation-diagnosis",
    "quality-security-review",
    "verification-handoff",
}


class TMaxBackendArchitectTeamTest(unittest.TestCase):
    def test_is_an_independent_copy_with_complete_references(self):
        original_skill = (ORIGINAL / "SKILL.md").read_text(encoding="utf-8")
        upgraded_skill = (UPGRADED / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("name: tech-backend-architect-team", original_skill)
        self.assertIn("name: tech-tmax-backend-architect-team", upgraded_skill)
        self.assertNotEqual(original_skill, upgraded_skill)

        expected_files = {
            "SKILL.md",
            "agents/openai.yaml",
            "references/architecture-method.md",
            "references/dispatch-protocol.md",
            "references/guide.md",
            "references/manifest.json",
            "references/stack-profile.md",
            "references/validation-matrix.md",
            "references/workflow.md",
            "source.json",
        }
        actual_files = {
            path.relative_to(UPGRADED).as_posix()
            for path in UPGRADED.rglob("*")
            if path.is_file()
        }
        self.assertEqual(actual_files, expected_files)

    def test_declares_tracks_and_standalone_source_boundary(self):
        source = json.loads((UPGRADED / "source.json").read_text(encoding="utf-8"))
        manifest = json.loads(
            (UPGRADED / "references" / "manifest.json").read_text(encoding="utf-8")
        )

        self.assertEqual(source["status"], "ready")
        self.assertEqual(source["source_package"], "tech-backend-architect-team")
        self.assertEqual(set(source["internal_tracks"]), TRACKS)
        self.assertTrue(source["repo_only"])
        self.assertFalse(source["installed"])
        self.assertEqual(set(manifest["internalTracks"]), TRACKS)
        self.assertEqual(
            manifest["runtimeArchitecture"]["model"],
            "single-agent-with-rule-package",
        )
        self.assertEqual(
            manifest["runtimeArchitecture"]["dispatcherAgent"],
            "tmax-backend-dispatch-agent",
        )
        self.assertEqual(manifest["runtimeArchitecture"]["concurrency"], 1)
        self.assertEqual(manifest["runtimeArchitecture"]["delegation"], "disabled")
        self.assertTrue(manifest["privacy"]["requiresRepositoryVerification"])
        self.assertFalse(manifest["privacy"]["containsLocalAbsolutePaths"])
        self.assertFalse(manifest["privacy"]["containsCredentials"])
        self.assertFalse(manifest["privacy"]["containsPrivateHosts"])

    def test_is_registered_in_both_expert_team_indexes(self):
        file_list = (REPO_ROOT / "indexes" / "expert-team-file-list.md").read_text(
            encoding="utf-8"
        )
        skill_index = (
            REPO_ROOT / "indexes" / "expert-team-skill-index.md"
        ).read_text(encoding="utf-8")

        link = "../skills/tech-tmax-backend-architect-team/SKILL.md"
        self.assertIn(link, file_list)
        self.assertIn(link, skill_index)
        for track in TRACKS:
            self.assertIn(f"`{track}`", file_list)

    def test_uses_one_dispatch_agent_and_one_rule_package(self):
        agent_prompt = (
            DISPATCH_AGENT / "tmax-backend-dispatch-agent.md"
        ).read_text(encoding="utf-8")
        agent_source = json.loads(
            (DISPATCH_AGENT / "source.json").read_text(encoding="utf-8")
        )
        protocol = (
            UPGRADED / "references" / "dispatch-protocol.md"
        ).read_text(encoding="utf-8")

        self.assertIn("name: tmax-backend-dispatch-agent", agent_prompt)
        self.assertIn("skills/tech-tmax-backend-architect-team/SKILL.md", agent_prompt)
        self.assertEqual(
            agent_source["bound_rule_package"],
            "skills/tech-tmax-backend-architect-team",
        )
        self.assertEqual(agent_source["execution_model"], "single-agent-with-rule-package")
        self.assertEqual(agent_source["concurrency"], 1)
        self.assertEqual(agent_source["delegation"], "disabled")
        self.assertIn("Delegation: disabled", protocol)
        self.assertIn("Do not create or simulate child Agents", protocol)
        self.assertIn("observe -> hypothesize -> plan-one-step -> act -> verify -> decide", protocol)

        unified_index = json.loads(
            (REPO_ROOT / "indexes" / "agent-skill-index.json").read_text(
                encoding="utf-8"
            )
        )
        dispatch_entries = [
            entry
            for entry in unified_index["entries"]
            if entry["kind"] == "agent"
            and entry["name"] == "tmax-backend-dispatch-agent"
        ]
        self.assertEqual(len(dispatch_entries), 1)

    def test_package_contains_no_local_absolute_paths(self):
        markers = ("/" + "Users/", "/" + "var/folders", "/" + "private/var")
        package_text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in UPGRADED.rglob("*")
            if path.is_file()
        )

        for marker in markers:
            self.assertNotIn(marker, package_text)

        agent_text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in DISPATCH_AGENT.rglob("*")
            if path.is_file()
        )
        for marker in markers:
            self.assertNotIn(marker, agent_text)


if __name__ == "__main__":
    unittest.main()
