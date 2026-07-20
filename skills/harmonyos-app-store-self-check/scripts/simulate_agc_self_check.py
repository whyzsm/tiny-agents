#!/usr/bin/env python3
"""Run a conservative, report-shaped local simulation of AGC self-checks."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

from check_harmony_release import (
    Finding,
    extract_number,
    extract_string,
    read_text,
    run,
)


CATEGORIES = ("兼容性", "稳定性", "功耗", "性能", "UX")
COUNTERS = ("total", "failed", "warnings", "passed")


def load_report(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取规范化 AGC 报告: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("规范化 AGC 报告必须是 JSON 对象")
    return value


def validate_report(report: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for key in ("source", "report_id", "test_result", "summary", "categories"):
        if key not in report:
            findings.append(
                Finding(
                    "REPORT-1",
                    "FAIL",
                    "P1",
                    f"AGC 报告缺少字段 {key}",
                    "normalized report",
                    "补齐报告页面可见字段后再模拟。",
                )
            )

    summary = report.get("summary")
    if isinstance(summary, dict):
        _validate_counters(findings, "REPORT-1", "报告汇总", summary)
    else:
        findings.append(
            Finding(
                "REPORT-1",
                "FAIL",
                "P1",
                "AGC 报告 summary 不是对象",
                "summary",
                "按规范化输入格式整理报告汇总。",
            )
        )

    categories = report.get("categories")
    if not isinstance(categories, dict):
        return findings

    category_total = 0
    for category in CATEGORIES:
        values = categories.get(category)
        if not isinstance(values, dict):
            findings.append(
                Finding(
                    "REPORT-2",
                    "FAIL",
                    "P1",
                    f"AGC 报告缺少分类 {category}",
                    f"categories.{category}",
                    "补充该页签的统计；不能用 0 代替缺失数据。",
                )
            )
            continue
        _validate_counters(findings, "REPORT-2", category, values)
        total = values.get("total")
        if isinstance(total, int) and not isinstance(total, bool) and total >= 0:
            category_total += total

    summary_total = summary.get("total") if isinstance(summary, dict) else None
    if (
        isinstance(summary_total, int)
        and not isinstance(summary_total, bool)
        and category_total != summary_total
    ):
        findings.append(
            Finding(
                "REPORT-2",
                "UNVERIFIED",
                "P1",
                "报告汇总用例数与五个分类用例数不一致",
                f"summary.total={summary_total}; categories.total={category_total}",
                "保留原始数据并标记证据差异，不要自行平均或补齐。",
            )
        )

    application = report.get("application")
    if isinstance(application, dict):
        declared = application.get("declared_device_types")
        summary_devices = summary.get("tested_device_types") if isinstance(summary, dict) else None
        if isinstance(declared, list) and isinstance(summary_devices, list):
            missing = sorted(set(str(item) for item in declared) - set(str(item) for item in summary_devices))
            if missing:
                findings.append(
                    Finding(
                        "REPORT-2",
                        "UNVERIFIED",
                        "P1",
                        "报告实际测试设备没有覆盖全部声明设备类型",
                        f"未覆盖: {', '.join(missing)}",
                        "补测缺失设备类型或在模拟结果中保留覆盖不完整。",
                    )
                )
    return findings


def _validate_counters(
    findings: list[Finding], check_id: str, label: str, values: dict[str, Any]
) -> None:
    for counter in COUNTERS:
        value = values.get(counter)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            findings.append(
                Finding(
                    check_id,
                    "FAIL",
                    "P1",
                    f"{label} 的 {counter} 不是非负整数",
                    f"{label}.{counter}",
                    "从 AGC 页签重新读取该统计值。",
                )
            )


def simulate(
    report: dict[str, Any],
    project_root: Path | None,
    artifact: Path | None,
    forbid_network: bool,
) -> dict[str, Any]:
    report_findings = validate_report(report)
    local_findings: list[Finding]
    if project_root is None:
        local_findings = [
            Finding(
                "LOCAL-1",
                "UNVERIFIED",
                "P0",
                "未提供当前 HarmonyOS 工程，无法重跑本地预检",
                "project_root",
                "提供工程根目录后再模拟当前包。",
            )
        ]
    elif not project_root.is_dir():
        local_findings = [
            Finding(
                "LOCAL-1",
                "FAIL",
                "P0",
                "当前 HarmonyOS 工程目录不存在",
                str(project_root),
                "提供可读取的工程根目录。",
            )
        ]
    else:
        local_findings = run(project_root, forbid_network, artifact)
        local_findings.extend(
            compare_identity(report, project_root, artifact)
        )

    local_blocking = any(item.status in {"FAIL", "BLOCKED"} for item in local_findings)
    report_errors = any(item.status == "FAIL" for item in report_findings)
    simulated_status = "SIMULATED_BLOCKED" if local_blocking or report_errors else "SIMULATED_UNVERIFIED"
    categories = [
        {
            "name": category,
            "simulated_status": "UNVERIFIED",
            "reason": "AGC 真机动态证据不能由历史报告复制到当前包。",
            "reference": report.get("categories", {}).get(category),
        }
        for category in CATEGORIES
    ]
    return {
        "mode": "report-driven-local-simulation",
        "simulated_status": simulated_status,
        "official_agc_status": "UNVERIFIED",
        "reference_report": {
            "report_id": report.get("report_id"),
            "report_url": report.get("report_url"),
            "test_result": report.get("test_result"),
            "summary": report.get("summary"),
        },
        "report_findings": [_as_dict(item) for item in report_findings],
        "local_findings": [_as_dict(item) for item in local_findings],
        "categories": categories,
    }


def compare_identity(
    report: dict[str, Any], project_root: Path, artifact: Path | None
) -> list[Finding]:
    expected = report.get("application")
    if not isinstance(expected, dict):
        return [
            Finding(
                "LOCAL-2",
                "UNVERIFIED",
                "P0",
                "报告未提供可比的应用身份字段",
                "application",
                "补充报告中的 bundle name、版本名和版本号。",
            )
        ]

    candidates: list[tuple[str, dict[str, Any]]] = [
        ("project", _project_identity(project_root)),
    ]
    if artifact is not None:
        candidates.append(("artifact", _artifact_identity(project_root, artifact)))

    mismatches: list[str] = []
    unavailable: list[str] = []
    compared: list[str] = []
    for source, actual in candidates:
        for key in ("bundle_name", "version_name", "version_code"):
            expected_value = _identity_value(expected.get(key))
            actual_value = _identity_value(actual.get(key))
            if expected_value is None:
                continue
            if actual_value is None:
                unavailable.append(f"{source}.{key}")
            elif actual_value != expected_value:
                mismatches.append(
                    f"{source}.{key}: expected={expected_value}; actual={actual_value}"
                )
            else:
                compared.append(f"{source}.{key}")

    if mismatches:
        return [
            Finding(
                "LOCAL-2",
                "FAIL",
                "P0",
                "当前工程或发布包与 AGC 报告身份不一致",
                "; ".join(mismatches),
                "停止模拟发布；确认报告对应的 bundle、版本和发布包。",
            )
        ]
    if unavailable:
        return [
            Finding(
                "LOCAL-2",
                "UNVERIFIED",
                "P0",
                "当前工程或发布包缺少与 AGC 报告对比所需的身份字段",
                ", ".join(unavailable),
                "补充可读取的工程配置或发布包元数据。",
            )
        ]
    return [
        Finding(
            "LOCAL-2",
            "PASS",
            "P0",
            "当前工程和发布包身份与 AGC 报告一致",
            ", ".join(compared),
            "继续保留 AGC 真机动态证据为未验证。",
        )
    ]


def _project_identity(root: Path) -> dict[str, Any]:
    text = read_text(root / "AppScope/app.json5")
    return {
        "bundle_name": extract_string(text, "bundleName"),
        "version_name": extract_string(text, "versionName"),
        "version_code": extract_number(text, "versionCode"),
    }


def _artifact_identity(root: Path, artifact: Path) -> dict[str, Any]:
    artifact_path = artifact.expanduser()
    if not artifact_path.is_absolute():
        artifact_path = root / artifact_path
    try:
        with zipfile.ZipFile(artifact_path) as archive:
            pack_name = next(
                name for name in archive.namelist() if Path(name).name == "pack.info"
            )
            pack_info = json.loads(archive.read(pack_name).decode("utf-8"))
    except (OSError, StopIteration, UnicodeDecodeError, json.JSONDecodeError, zipfile.BadZipFile):
        return {}
    app = pack_info.get("summary", {}).get("app", {})
    if not isinstance(app, dict):
        return {}
    version = app.get("version")
    if not isinstance(version, dict):
        version = {}
    return {
        "bundle_name": app.get("bundleName"),
        "version_name": version.get("name"),
        "version_code": version.get("code"),
    }


def _identity_value(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).strip()


def _as_dict(finding: Finding) -> dict[str, str]:
    return {
        "check_id": finding.check_id,
        "status": finding.status,
        "severity": finding.severity,
        "message": finding.message,
        "evidence": finding.evidence,
        "remediation": finding.remediation,
    }


def render_text(result: dict[str, Any]) -> str:
    reference = result["reference_report"]
    lines = [
        f"模拟结论: {result['simulated_status']}",
        f"官方 AGC 结论: {result['official_agc_status']}",
        f"参考报告: {reference.get('report_id')} | 原始结果: {reference.get('test_result')}",
        "",
        "| AGC 分类 | 模拟状态 | 参考统计 | 说明 |",
        "|---|---|---|---|",
    ]
    for category in result["categories"]:
        reference_value = json.dumps(category["reference"], ensure_ascii=False)
        lines.append(
            f"| {category['name']} | {category['simulated_status']} | "
            f"{reference_value} | {category['reason']} |"
        )
    for finding in result["report_findings"] + result["local_findings"]:
        lines.append(
            f"| {finding['check_id']} | {finding['status']} | {finding['severity']} | "
            f"{finding['message']} |"
        )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--forbid-network", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = load_report(args.report.expanduser().resolve())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    project_root = args.project_root.expanduser().resolve() if args.project_root else None
    result = simulate(report, project_root, args.artifact, args.forbid_network)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result), end="")
    if args.strict and result["simulated_status"] == "SIMULATED_BLOCKED":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
