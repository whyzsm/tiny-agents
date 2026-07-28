from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_performance_evidence.py"
sys.path.insert(0, str(SCRIPT.parent))
from validate_performance_evidence import validate  # noqa: E402


def evidence(*results: dict) -> dict:
    return {
        "schema_version": 1,
        "package": {
            "bundle_name": "io.example.app",
            "version_name": "1.0.0",
            "version_code": 1,
        },
        "device": {
            "model": "Fixture Phone",
            "device_type": "phone",
            "os_version": "5.0.0",
            "api_level": 12,
        },
        "required_rule_ids": [item["rule_id"] for item in results],
        "results": list(results),
    }


class PerformanceEvidenceTests(unittest.TestCase):
    def test_measured_rules_can_be_ready(self) -> None:
        result = validate(
            evidence(
                {
                    "rule_id": "DELAY-1",
                    "status": "measured",
                    "value": 80,
                    "unit": "ms",
                    "input_mode": "touch",
                    "statistic": "p95",
                    "sample_count": 10,
                    "evidence": "trace/startup.json",
                },
                {
                    "rule_id": "FPS-3",
                    "status": "measured",
                    "value": 0,
                    "unit": "frames",
                    "evidence": "trace/scroll.json",
                },
                {
                    "rule_id": "CPU-1",
                    "status": "measured",
                    "value": 1.5,
                    "unit": "%",
                    "evidence": "trace/background-cpu.json",
                },
            )
        )
        self.assertEqual(result["overall"], "READY")
        self.assertTrue(all(item["status"] == "PASS" for item in result["findings"]))

    def test_threshold_failure_is_blocked(self) -> None:
        result = validate(
            evidence(
                {
                    "rule_id": "DELAY-4",
                    "status": "measured",
                    "value": 101,
                    "unit": "ms",
                    "evidence": "trace/click.json",
                }
            )
        )
        self.assertEqual(result["overall"], "BLOCKED")
        self.assertEqual(result["findings"][-1]["status"], "FAIL")

    def test_not_applicable_requires_reason(self) -> None:
        result = validate(
            evidence(
                {
                    "rule_id": "DELAY-7",
                    "status": "not_applicable",
                    "reason": "目标产品不支持折叠屏设备",
                }
            )
        )
        self.assertEqual(result["overall"], "READY")
        self.assertEqual(result["findings"][-1]["status"], "NOT_APPLICABLE")

    def test_missing_measurement_is_unverified_in_strict_mode(self) -> None:
        payload = evidence(
            {
                "rule_id": "DELAY-1",
                "status": "measured",
                "value": 80,
                "unit": "ms",
                "evidence": "trace/startup.json",
            },
            {
                "rule_id": "DELAY-2",
                "status": "measured",
                "value": 1100,
                "unit": "ms",
                "evidence": "trace/load.json",
            },
        )
        payload["required_rule_ids"].append("FPS-3")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "performance.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--evidence",
                    str(path),
                    "--strict",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["overall"], "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
