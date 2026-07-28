#!/usr/bin/env python3
"""Validate measured HarmonyOS performance evidence against Huawei's V7 guidance."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SOURCE_URL = (
    "https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/"
    "performance-delay-V5"
)


@dataclass(frozen=True)
class Rule:
    rule_id: str
    label: str
    kind: str
    unit: str
    severity: str
    source: str


@dataclass(frozen=True)
class Finding:
    check_id: str
    status: str
    severity: str
    message: str
    evidence: str
    remediation: str


RULES = {
    **{
        f"DELAY-{index}": Rule(
            f"DELAY-{index}",
            label,
            kind,
            unit,
            "P2" if index == 3 else "P1",
            "performance-delay-V5",
        )
        for index, label, kind, unit in (
            (1, "启动响应", "startup_response", "ms"),
            (2, "启动加载完成", "max", "ms"),
            (3, "冷启动进度提示", "cold_start_progress", "ms"),
            (4, "点击操作响应", "max", "ms"),
            (5, "点击操作完成", "max", "ms"),
            (6, "滑动操作响应", "scroll_response", "ms"),
            (7, "折叠操作接续", "max", "ms"),
            (8, "展开操作接续", "max", "ms"),
            (9, "长视频起播", "max", "ms"),
            (10, "长视频 Seek 起播", "max", "ms"),
            (11, "短视频切换起播", "max", "ms"),
            (12, "短视频 Seek 起播", "max", "ms"),
        )
    },
    **{
        f"FPS-{index}": Rule(
            f"FPS-{index}", label, kind, unit, "P1", "performance-frame-rate-V5"
        )
        for index, label, kind, unit in (
            (1, "启动丢帧", "startup_frames", "frames"),
            (2, "启动卡顿率", "zero", "ms/s"),
            (3, "滑动丢帧", "zero", "frames"),
            (4, "滑动卡顿率", "max", "ms/s"),
            (5, "转场丢帧", "zero", "frames"),
            (6, "转场卡顿率", "zero", "ms/s"),
            (7, "弹幕滚动丢帧", "zero", "frames"),
            (8, "视频卡顿", "video_stutter", "mixed"),
            (9, "音画同步", "av_sync", "ms_and_subjective"),
        )
    },
    **{
        f"CONTENT-{index}": Rule(
            f"CONTENT-{index}", label, kind, unit, "P1", "performance-content-display-V5"
        )
        for index, label, kind, unit in (
            (1, "启动黑白闪跳", "max", "ms"),
            (2, "滑动占位符加载", "max", "ms"),
            (3, "滑动内容完整率", "exact", "%"),
        )
    },
    **{
        f"MEMORY-{index}": Rule(
            f"MEMORY-{index}", label, kind, unit, "P2", "performance-memory-usage-V5"
        )
        for index, label, kind, unit in (
            (1, "后台内存峰值", "max", "MB"),
            (2, "前台内存峰值", "max", "MB"),
            (3, "历史基线", "baseline", "any"),
        )
    },
    "CPU-1": Rule(
        "CPU-1",
        "后台 CPU 峰值",
        "strict_max",
        "%",
        "P1",
        "performance-cpu-usage-V5",
    ),
}


def add(
    findings: list[Finding],
    check_id: str,
    status: str,
    severity: str,
    message: str,
    evidence: str,
    remediation: str,
) -> None:
    findings.append(Finding(check_id, status, severity, message, evidence, remediation))


def load_evidence(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取性能证据 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("性能证据必须是 JSON 对象")
    return value


def _has_values(value: Any, keys: tuple[str, ...]) -> bool:
    return isinstance(value, dict) and all(key in value for key in keys)


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _validate_metadata(data: dict[str, Any], findings: list[Finding]) -> None:
    package = data.get("package")
    device = data.get("device")
    package_keys = ("bundle_name", "version_name", "version_code")
    device_keys = ("model", "device_type", "os_version", "api_level")
    if not isinstance(package, dict) or any(not str(package.get(key, "")).strip() for key in package_keys):
        add(
            findings,
            "EVIDENCE-1",
            "UNVERIFIED",
            "P1",
            "性能证据缺少完整的包身份",
            "package.bundle_name/version_name/version_code",
            "补充与待测 release 包一致的 bundle、版本名和版本号。",
        )
    if not isinstance(device, dict) or any(not str(device.get(key, "")).strip() for key in device_keys):
        add(
            findings,
            "EVIDENCE-1",
            "UNVERIFIED",
            "P1",
            "性能证据缺少完整的设备和系统信息",
            "device.model/device_type/os_version/api_level",
            "补充实际测量设备、设备类型、系统版本和 API Level。",
        )


def _validate_result_shape(rule: Rule, result: dict[str, Any], findings: list[Finding]) -> bool:
    status = result.get("status")
    evidence = result.get("evidence")
    if status == "not_applicable":
        if not str(result.get("reason", "")).strip():
            add(
                findings,
                f"PERF-{rule.rule_id}",
                "FAIL",
                rule.severity,
                f"{rule.label}标记为不适用但没有原因",
                rule.rule_id,
                "说明产品能力或目标设备为何不适用该官方性能规则。",
            )
            return False
        return True
    if status != "measured":
        add(
            findings,
            f"PERF-{rule.rule_id}",
            "FAIL",
            rule.severity,
            f"{rule.label}的 status 必须是 measured 或 not_applicable",
            rule.rule_id,
            "使用真实设备/AGC 测量结果，或明确记录不适用原因。",
        )
        return False
    if not str(evidence or "").strip():
        add(
            findings,
            f"PERF-{rule.rule_id}",
            "UNVERIFIED",
            rule.severity,
            f"{rule.label}缺少可复核证据路径或报告引用",
            rule.rule_id,
            "补充性能工具导出、AGC 报告或带时间戳的测试记录。",
        )
        return False
    if rule.kind == "startup_response" and result.get("input_mode") not in {"touch", "mouse"}:
        add(
            findings,
            f"PERF-{rule.rule_id}",
            "UNVERIFIED",
            rule.severity,
            "启动响应缺少 touch 或 mouse 场景",
            rule.rule_id,
            "记录输入方式后按对应的 85 ms 或 100 ms 阈值复测。",
        )
        return False
    if rule.kind == "scroll_response" and result.get("gesture") not in {"fling", "drag"}:
        add(
            findings,
            f"PERF-{rule.rule_id}",
            "UNVERIFIED",
            rule.severity,
            "滑动响应缺少 fling 或 drag 场景",
            rule.rule_id,
            "记录滑动类型后按抛滑 80 ms 或拖滑 60 ms 阈值复测。",
        )
        return False
    if rule.kind == "startup_frames" and not _has_values(
        result.get("values"), ("animation_max_consecutive", "loading_max_consecutive")
    ):
        add(
            findings,
            f"PERF-{rule.rule_id}",
            "FAIL",
            rule.severity,
            "启动丢帧证据缺少 animation_max_consecutive 或 loading_max_consecutive",
            rule.rule_id,
            "从帧率工具分别记录启动动效和加载环节的最大连续丢帧。",
        )
        return False
    if rule.kind == "startup_frames" and any(
        _number(result["values"].get(key)) is None
        for key in ("animation_max_consecutive", "loading_max_consecutive")
    ):
        add(
            findings,
            f"PERF-{rule.rule_id}",
            "FAIL",
            rule.severity,
            "启动丢帧证据包含非数值字段",
            rule.rule_id,
            "使用帧率工具导出的非负连续丢帧数。",
        )
        return False
    if rule.kind == "video_stutter" and not _has_values(
        result.get("values"), ("max_stutter_ms", "stutter_count")
    ):
        add(
            findings,
            f"PERF-{rule.rule_id}",
            "FAIL",
            rule.severity,
            "视频卡顿证据缺少 max_stutter_ms 或 stutter_count",
            rule.rule_id,
            "同时记录最大卡顿时长和卡顿次数。",
        )
        return False
    if rule.kind == "video_stutter" and any(
        _number(result["values"].get(key)) is None
        for key in ("max_stutter_ms", "stutter_count")
    ):
        add(
            findings,
            f"PERF-{rule.rule_id}",
            "FAIL",
            rule.severity,
            "视频卡顿证据包含非数值字段",
            rule.rule_id,
            "同时提供最大卡顿毫秒数和非负卡顿次数。",
        )
        return False
    if rule.kind == "av_sync" and not _has_values(
        result.get("values"), ("av_sync_ms", "subjective_ok")
    ):
        add(
            findings,
            f"PERF-{rule.rule_id}",
            "FAIL",
            rule.severity,
            "音画同步证据缺少 av_sync_ms 或 subjective_ok",
            rule.rule_id,
            "同时记录音画时间差和主观同步感受。",
        )
        return False
    if rule.kind == "av_sync" and (
        _number(result["values"].get("av_sync_ms")) is None
        or not isinstance(result["values"].get("subjective_ok"), bool)
    ):
        add(
            findings,
            f"PERF-{rule.rule_id}",
            "FAIL",
            rule.severity,
            "音画同步证据包含无效数值或主观结果",
            rule.rule_id,
            "提供数值音画时差和明确的 true/false 主观同步结果。",
        )
        return False
    if rule.kind == "cold_start_progress" and _number(result.get("value")) is not None:
        if _number(result["value"]) > 3000 and "progress_hint" not in result:
            add(
                findings,
                f"PERF-{rule.rule_id}",
                "UNVERIFIED",
                rule.severity,
                "冷启动超过 3 s，但未记录是否提供进度提示",
                rule.rule_id,
                "补充 progress_hint 以及对应的启动录屏或实现证据。",
            )
            return False
    if rule.kind == "baseline" and _number(result.get("baseline")) is None:
        add(
            findings,
            f"PERF-{rule.rule_id}",
            "UNVERIFIED",
            rule.severity,
            "历史基线规则缺少 baseline 数值",
            rule.rule_id,
            "补充同类设备/场景的历史基线和当前测量值。",
        )
        return False
    if rule.kind not in {"startup_frames", "video_stutter", "av_sync"} and _number(result.get("value")) is None:
        add(
            findings,
            f"PERF-{rule.rule_id}",
            "FAIL",
            rule.severity,
            f"{rule.label}缺少数值 value",
            rule.rule_id,
            "提供带正确单位的数值测量结果。",
        )
        return False
    unit = result.get("unit")
    if rule.unit != "any" and unit != rule.unit:
        add(
            findings,
            f"PERF-{rule.rule_id}",
            "FAIL",
            rule.severity,
            f"{rule.label}的单位不正确，应为 {rule.unit}",
            f"{rule.rule_id}: unit={unit!r}",
            f"按官方单位 {rule.unit} 重新记录，避免跨单位比较。",
        )
        return False
    return True


def _evaluate(rule: Rule, result: dict[str, Any], findings: list[Finding]) -> None:
    evidence = str(result.get("evidence"))
    values = result.get("values")
    value = _number(result.get("value"))
    passed = True
    message = f"{rule.label}测量值符合华为 {rule.source} 标准"
    remediation = "保留该设备和包版本的原始性能证据。"

    if rule.kind == "startup_response":
        limit = 100 if result.get("input_mode") == "mouse" else 85
        passed = value is not None and 0 <= value <= limit
        message = f"启动响应 {value:g} ms，阈值 <= {limit} ms"
    elif rule.kind == "scroll_response":
        limit = 60 if result.get("gesture") == "drag" else 80
        passed = value is not None and 0 <= value <= limit
        message = f"滑动响应 {value:g} ms，阈值 <= {limit} ms"
    elif rule.kind == "max":
        limits = {
            "DELAY-2": 1100,
            "DELAY-4": 100,
            "DELAY-5": 900,
            "DELAY-7": 800,
            "DELAY-8": 700,
            "DELAY-9": 800,
            "DELAY-10": 800,
            "DELAY-11": 230,
            "DELAY-12": 100,
            "FPS-4": 5,
            "CONTENT-1": 40,
            "CONTENT-2": 40,
            "MEMORY-1": 1000,
            "MEMORY-2": 1500,
        }
        limit = limits[rule.rule_id]
        passed = value is not None and 0 <= value <= limit
        message = f"{rule.label} {value:g} {rule.unit}，阈值 <= {limit} {rule.unit}"
    elif rule.kind == "cold_start_progress":
        if value is None or value < 0:
            passed = False
        elif value <= 3000:
            passed = True
        else:
            passed = result.get("progress_hint") is True
            if not passed:
                message = "冷启动动画/视频超过 3 s 但未提供进度提示"
                remediation = "增加进度提示，或提交说明该场景不需要进度提示的证据。"
    elif rule.kind == "zero":
        passed = value is not None and 0 <= value == 0
        message = f"{rule.label} {value:g} {rule.unit}，官方要求为 0"
    elif rule.kind == "exact":
        passed = value == 100
        message = f"{rule.label} {value:g}{rule.unit}，官方要求 100%"
    elif rule.kind == "strict_max":
        passed = value is not None and 0 <= value < 2
        message = f"后台 CPU 峰值 {value:g}%，官方要求 < 2%"
    elif rule.kind == "startup_frames":
        animation = _number(values.get("animation_max_consecutive")) if isinstance(values, dict) else None
        loading = _number(values.get("loading_max_consecutive")) if isinstance(values, dict) else None
        passed = animation is not None and loading is not None and animation == 0 and 0 <= loading <= 6
        message = f"启动动效连续丢帧 {animation:g}，加载连续丢帧 {loading:g}，阈值为 0/<=6"
    elif rule.kind == "video_stutter":
        maximum = _number(values.get("max_stutter_ms")) if isinstance(values, dict) else None
        count = _number(values.get("stutter_count")) if isinstance(values, dict) else None
        passed = maximum is not None and count is not None and 0 <= maximum <= 100 and count == 0
        message = f"视频最大卡顿 {maximum:g} ms、次数 {count:g}，阈值 <=100 ms/0 次"
    elif rule.kind == "av_sync":
        sync = _number(values.get("av_sync_ms")) if isinstance(values, dict) else None
        subjective = values.get("subjective_ok") if isinstance(values, dict) else None
        passed = sync is not None and -80 <= sync <= 25 and subjective is True
        message = f"音画时间差 {sync:g} ms，范围 -80..25 ms，主观结果={subjective}"
    elif rule.kind == "baseline":
        baseline = _number(result.get("baseline"))
        passed = value is not None and baseline is not None and value <= baseline
        message = f"当前值 {value:g} {result.get('unit')}，历史基线 {baseline:g} {result.get('unit')}"
        if not passed:
            remediation = "高于历史基线时补充性能澄清和优化说明，不要静默忽略。"

    add(
        findings,
        f"PERF-{rule.rule_id}",
        "PASS" if passed else "FAIL",
        rule.severity,
        message,
        evidence,
        remediation,
    )


def validate(data: dict[str, Any]) -> dict[str, Any]:
    findings: list[Finding] = []
    _validate_metadata(data, findings)

    required = data.get("required_rule_ids")
    if not isinstance(required, list) or not required:
        add(
            findings,
            "EVIDENCE-2",
            "UNVERIFIED",
            "P1",
            "没有声明当前产品适用的华为性能规则",
            "required_rule_ids",
            "按产品能力和目标设备填写适用规则；不适用规则要有原因。",
        )
        required = []

    unknown = [str(item) for item in required if str(item) not in RULES]
    if unknown:
        add(
            findings,
            "EVIDENCE-2",
            "FAIL",
            "P1",
            "required_rule_ids 含未知规则 ID",
            ", ".join(unknown),
            "使用 references/huawei-performance-guidelines-v7.md 中的规则 ID。",
        )

    results = data.get("results")
    if not isinstance(results, list):
        add(
            findings,
            "EVIDENCE-3",
            "FAIL",
            "P1",
            "results 必须是数组",
            "results",
            "按规范化性能证据格式提供测量结果。",
        )
        results = []
    by_id: dict[str, dict[str, Any]] = {}
    for result in results:
        if not isinstance(result, dict):
            add(findings, "EVIDENCE-3", "FAIL", "P1", "性能结果必须是对象", "results", "修正 JSON 结构。")
            continue
        rule_id = str(result.get("rule_id", ""))
        if rule_id not in RULES:
            add(findings, "EVIDENCE-3", "FAIL", "P1", "性能结果含未知 rule_id", rule_id or "<empty>", "使用官方矩阵中的规则 ID。")
            continue
        if rule_id in by_id:
            add(findings, "EVIDENCE-3", "FAIL", "P1", "同一 rule_id 有重复结果", rule_id, "同一设备保留一条最差测量结果，跨设备使用不同证据文件。")
            continue
        by_id[rule_id] = result

    for rule_id in required:
        if rule_id not in RULES:
            continue
        rule = RULES[rule_id]
        result = by_id.get(rule_id)
        if result is None:
            add(
                findings,
                f"PERF-{rule_id}",
                "UNVERIFIED",
                rule.severity,
                f"缺少{rule.label}的实际测量结果",
                rule_id,
                "补充设备性能追踪、AGC 报告或带时间戳的手工测量。",
            )
            continue
        if not _validate_result_shape(rule, result, findings):
            continue
        if result.get("status") == "not_applicable":
            add(
                findings,
                f"PERF-{rule_id}",
                "NOT_APPLICABLE",
                rule.severity,
                f"{rule.label}记录为不适用",
                str(result.get("reason")),
                "保留不适用原因，并确保与产品能力和目标设备一致。",
            )
            continue
        _evaluate(rule, result, findings)

    blocking = [item for item in findings if item.status == "FAIL"]
    unknown_findings = [item for item in findings if item.status in {"UNVERIFIED", "BLOCKED"}]
    overall = "BLOCKED" if blocking else ("UNVERIFIED" if unknown_findings else "READY")
    return {
        "overall": overall,
        "source": SOURCE_URL,
        "rule_count": len(required),
        "findings": [item.__dict__ for item in findings],
    }


def render_text(result: dict[str, Any]) -> str:
    lines = [
        f"结论: {result['overall']}",
        f"官方来源: {result['source']}",
        f"适用规则数: {result['rule_count']}",
        "",
        "| ID | 状态 | 严重度 | 发现 | 证据 | 建议 |",
        "|---|---|---|---|---|---|",
    ]
    for item in result["findings"]:
        lines.append(
            f"| {item['check_id']} | {item['status']} | {item['severity']} | "
            f"{item['message']} | {item['evidence']} | {item['remediation']} |"
        )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--strict", action="store_true", help="对未验证和失败项都返回非零")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = load_evidence(args.evidence.expanduser().resolve())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    result = validate(data)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result), end="")
    if args.strict and result["overall"] != "READY":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
