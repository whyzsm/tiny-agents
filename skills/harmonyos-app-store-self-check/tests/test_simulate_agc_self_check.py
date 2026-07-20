from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "simulate_agc_self_check.py"
sys.path.insert(0, str(SCRIPT.parent))
from simulate_agc_self_check import compare_identity  # noqa: E402


def report(*, inconsistent: bool = False) -> dict:
    totals = {
        "兼容性": {"total": 0, "failed": 0, "warnings": 0, "passed": 0},
        "稳定性": {"total": 6, "failed": 0, "warnings": 0, "passed": 6},
        "功耗": {"total": 7, "failed": 0, "warnings": 0, "passed": 7},
        "性能": {"total": 5, "failed": 0, "warnings": 0, "passed": 5},
        "UX": {"total": 43, "failed": 0, "warnings": 1, "passed": 42},
    }
    return {
        "source": "agc-console",
        "report_id": "fixture-report",
        "test_result": "通过",
        "application": {
            "name": "Fixture",
            "bundle_name": "io.example.app",
            "version_name": "1.0.0",
            "version_code": 1,
            "api_level": 23,
            "declared_device_types": ["phone", "tablet"],
        },
        "summary": {
            "total": 105 if inconsistent else 61,
            "failed": 0,
            "warnings": 1,
            "passed": 104 if inconsistent else 60,
            "tested_devices": ["Mate 60"],
            "tested_device_types": ["phone"],
            "coverage_complete": False,
        },
        "categories": totals,
    }


class SimulateAgcSelfCheckTests(unittest.TestCase):
    def run_script(self, payload: dict, *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "report.json"
            report_path.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), "--report", str(report_path), "--format", "json", *args],
                check=False,
                capture_output=True,
                text=True,
            )

    def test_historical_pass_never_becomes_official_pass(self) -> None:
        result = self.run_script(report())
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["reference_report"]["test_result"], "通过")
        self.assertEqual(payload["official_agc_status"], "UNVERIFIED")
        self.assertEqual(payload["simulated_status"], "SIMULATED_UNVERIFIED")

    def test_inconsistent_report_is_retained_as_evidence_issue(self) -> None:
        result = self.run_script(report(inconsistent=True))
        payload = json.loads(result.stdout)
        self.assertTrue(
            any(item["check_id"] == "REPORT-2" for item in payload["report_findings"])
        )

    def test_missing_required_category_is_blocking_in_strict_mode(self) -> None:
        payload = report()
        del payload["categories"]["UX"]
        result = self.run_script(payload, "--strict")
        self.assertEqual(result.returncode, 1)
        output = json.loads(result.stdout)
        self.assertEqual(output["simulated_status"], "SIMULATED_BLOCKED")

    def test_project_and_artifact_identity_are_compared(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AppScope").mkdir()
            (root / "AppScope/app.json5").write_text(
                '{"app":{"bundleName":"io.example.app","versionCode":1,"versionName":"1.0.0"}}',
                encoding="utf-8",
            )
            artifact = root / "release.app"
            with zipfile.ZipFile(artifact, "w") as archive:
                archive.writestr(
                    "pack.info",
                    json.dumps(
                        {
                            "summary": {
                                "app": {
                                    "bundleName": "io.example.app",
                                    "version": {"code": 1, "name": "1.0.0"},
                                }
                            }
                        }
                    ),
                )
            matching = compare_identity(report(), root, artifact)
            self.assertEqual(matching[0].status, "PASS")
            mismatched = report()
            mismatched["application"]["bundle_name"] = "io.other.app"
            mismatch = compare_identity(mismatched, root, artifact)
            self.assertEqual(mismatch[0].status, "FAIL")


if __name__ == "__main__":
    unittest.main()
