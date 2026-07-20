#!/usr/bin/env python3
"""Static, evidence-oriented preflight for a HarmonyOS release project.

The checker deliberately reports advisory findings instead of pretending to
know current AppGallery policy. It never writes to the inspected project and
never prints secret values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


TEXT_SUFFIXES = {
    ".c",
    ".cpp",
    ".ets",
    ".h",
    ".html",
    ".json",
    ".json5",
    ".md",
    ".ts",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP_PARTS = {".git", ".hvigor", "build", "node_modules"}
PERMISSION_PATTERN = re.compile(r"ohos\.permission\.[A-Z0-9_]+")
NETWORK_MARKERS = (
    "ohos.permission.INTERNET",
    "@ohos.net",
    "@kit.NetworkKit",
    "@kit.NetConnectionKit",
    "http.createHttp",
    "fetch(",
)
SECRET_MARKERS = (
    "keyPassword",
    "storePassword",
    "privateKey",
    "BEGIN PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
)
SIGNING_FILE_MARKERS = (".p12", ".pfx", ".cer", ".p7b", ".csr")
HOME_PATH_PATTERN = re.compile(r"(?:/Users/|/home/|[A-Za-z]:\\Users\\)")
ARTIFACT_SUFFIXES = {".app", ".hap"}
ARTIFACT_METADATA_NAMES = {"app.json", "module.json", "pack.info", "config.json"}


@dataclass(frozen=True)
class Finding:
    check_id: str
    status: str
    severity: str
    message: str
    evidence: str
    remediation: str


def add(
    findings: list[Finding],
    check_id: str,
    status: str,
    severity: str,
    message: str,
    evidence: str,
    remediation: str,
) -> None:
    findings.append(
        Finding(
            check_id=check_id,
            status=status,
            severity=severity,
            message=message,
            evidence=evidence,
            remediation=remediation,
        )
    )


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def find_module_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("module.json5")
        if not any(part in SKIP_PARTS for part in path.parts)
    )


def extract_string(text: str, key: str) -> str | None:
    match = re.search(
        rf"[\"']{re.escape(key)}[\"']\s*:\s*[\"']([^\"']+)[\"']", text
    )
    return match.group(1) if match else None


def extract_number(text: str, key: str) -> str | None:
    match = re.search(rf"[\"']{re.escape(key)}[\"']\s*:\s*(\d+)", text)
    return match.group(1) if match else None


def relevant_text_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in {".git", ".hvigor", "build", "node_modules"} for part in path.parts):
            continue
        yield path


def tracked_files(root: Path) -> list[Path]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=True,
            capture_output=True,
            text=False,
        )
    except (OSError, subprocess.CalledProcessError):
        return list(relevant_text_files(root))
    paths: list[Path] = []
    for raw in completed.stdout.split(b"\0"):
        if not raw:
            continue
        path = root / os_fs_decode(raw)
        if path.is_file():
            paths.append(path)
    return paths


def os_fs_decode(raw: bytes) -> str:
    return raw.decode(sys.getfilesystemencoding(), errors="surrogateescape")


def check_structure(root: Path, findings: list[Finding]) -> None:
    required = (
        "AppScope/app.json5",
        "build-profile.json5",
        "hvigorfile.ts",
        "oh-package.json5",
    )
    missing = [path for path in required if not (root / path).is_file()]
    if missing:
        add(
            findings,
            "META-2",
            "FAIL",
            "P1",
            "缺少 HarmonyOS 工程入口文件",
            ", ".join(missing),
            "补齐工程入口或说明非标准工程布局后再继续发布检查。",
        )
    else:
        add(
            findings,
            "META-2",
            "PASS",
            "P1",
            "核心工程入口文件存在",
            ", ".join(required),
            "继续核对模块、路由和构建配置。",
        )

    modules = find_module_files(root)
    if not modules:
        add(
            findings,
            "META-2",
            "FAIL",
            "P0",
            "未找到 module.json5，无法确认 Stage 模块",
            str(root),
            "提供可构建的 HarmonyOS Stage 工程。",
        )
        return

    for module in modules:
        relative = module.relative_to(root).as_posix()
        text = read_text(module)
        if '"mainElement"' not in text and "'mainElement'" not in text:
            add(
                findings,
                "META-2",
                "FAIL",
                "P1",
                "模块缺少 mainElement",
                relative,
                "确认 entry ability 或模块入口已注册。",
            )
        if '"pages"' not in text and "'pages'" not in text:
            add(
                findings,
                "META-2",
                "UNVERIFIED",
                "P1",
                "模块未发现 pages 配置，路由注册需人工确认",
                relative,
                "核对 main_pages.json 或项目实际路由注册方式。",
            )


def check_identity(root: Path, findings: list[Finding]) -> None:
    app_path = root / "AppScope/app.json5"
    if not app_path.is_file():
        return
    text = read_text(app_path)
    keys = ("bundleName", "label", "versionCode", "versionName")
    missing = [key for key in keys if extract_string(text, key) is None and extract_number(text, key) is None]
    if missing:
        add(
            findings,
            "META-1",
            "FAIL",
            "P0",
            "应用身份或版本字段缺失",
            f"AppScope/app.json5: {', '.join(missing)}",
            "补齐 bundleName、label、versionCode、versionName，并与 AGC listing 对齐。",
        )
    else:
        add(
            findings,
            "META-1",
            "PASS",
            "P0",
            "应用身份和版本字段存在",
            "AppScope/app.json5",
            "继续核对 AGC listing 和待上传 artifact。",
        )

    build_profile = root / "build-profile.json5"
    if not build_profile.is_file():
        return
    build_text = read_text(build_profile)
    if "targetSdkVersion" not in build_text or "compatibleSdkVersion" not in build_text:
        add(
            findings,
            "META-3",
            "FAIL",
            "P1",
            "未发现 targetSdkVersion 或 compatibleSdkVersion",
            "build-profile.json5",
            "确认目标 API 与 AGC/设备支持范围，并保留版本证据。",
        )
    else:
        add(
            findings,
            "META-3",
            "PASS",
            "P1",
            "构建配置包含目标和兼容 SDK",
            "build-profile.json5",
            "仍需用当前官方资料确认版本支持范围。",
        )
    if "release" not in build_text.lower():
        add(
            findings,
            "SIGN-1",
            "UNVERIFIED",
            "P0",
            "构建配置未显式发现 release 模式",
            "build-profile.json5",
            "用项目 hvigorw 实际构建目标 product 的 release HAP/APP。",
        )
    else:
        add(
            findings,
            "SIGN-1",
            "PASS",
            "P0",
            "构建配置包含 release 模式",
            "build-profile.json5",
            "仍需保留 release 构建日志和 artifact 摘要。",
        )


def check_privacy(root: Path, findings: list[Finding]) -> None:
    candidates = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and ("privacy" in path.name.lower() or "隐私" in path.name)
        and path.suffix.lower() in {".html", ".htm", ".md", ".txt", ".json"}
        and not any(part in {".git", ".hvigor", "build", "node_modules"} for part in path.parts)
    ]
    if not candidates:
        add(
            findings,
            "PRIV-1",
            "FAIL",
            "P1",
            "未找到隐私政策材料",
            "未发现 privacy/隐私 文件",
            "补充可访问的隐私政策，并在 AGC listing 和应用内入口中核对 URL。",
        )
        return
    meaningful = False
    for path in candidates:
        text = read_text(path)
        if re.search(r"隐私|privacy", text, re.IGNORECASE) and re.search(
            r"数据|权限|删除|保存|用途|data|permission|delete|storage", text, re.IGNORECASE
        ):
            meaningful = True
            break
    if meaningful:
        add(
            findings,
            "PRIV-1",
            "PASS",
            "P1",
            "发现包含用途和数据处理说明的隐私政策材料",
            ", ".join(path.relative_to(root).as_posix() for path in candidates),
            "仍需在 AGC 和真实应用入口验证可访问性及内容完整性。",
        )
    else:
        add(
            findings,
            "PRIV-1",
            "UNVERIFIED",
            "P1",
            "隐私材料存在但内容关键词不足，需人工审阅",
            ", ".join(path.relative_to(root).as_posix() for path in candidates),
            "逐项补齐收集范围、用途、存储、删除、联系方式和更新说明。",
        )


def check_permissions(root: Path, findings: list[Finding], forbid_network: bool) -> None:
    files = list(relevant_text_files(root))
    permission_hits: dict[str, str] = {}
    network_hits: list[str] = []
    for path in files:
        text = read_text(path)
        for permission in PERMISSION_PATTERN.findall(text):
            permission_hits.setdefault(permission, path.relative_to(root).as_posix())
        for marker in NETWORK_MARKERS:
            if marker in text:
                network_hits.append(f"{path.relative_to(root).as_posix()} ({marker})")
    if permission_hits:
        add(
            findings,
            "PRIV-2",
            "UNVERIFIED",
            "P1",
            "发现权限声明或权限引用，需要逐项映射到真实功能和隐私说明",
            ", ".join(f"{key} @ {value}" for key, value in sorted(permission_hits.items())),
            "核对 module.json5、运行时申请、拒绝处理、隐私政策和 listing 文案。",
        )
    else:
        add(
            findings,
            "PRIV-2",
            "PASS",
            "P1",
            "未发现 ohos.permission.* 权限引用",
            "项目文本扫描",
            "仍需确认平台隐式能力和 AGC 侧声明。",
        )
    if network_hits and forbid_network:
        add(
            findings,
            "DATA-3",
            "FAIL",
            "P0",
            "检测到 local-first 项目不允许的网络/远程能力",
            ", ".join(sorted(set(network_hits))),
            "移除网络权限和远程依赖，或先明确变更产品范围并更新隐私材料。",
        )
    elif network_hits:
        add(
            findings,
            "DATA-3",
            "UNVERIFIED",
            "P1",
            "检测到网络相关代码，需确认披露和第三方数据流",
            ", ".join(sorted(set(network_hits))),
            "映射数据流、SDK、隐私政策和 AGC listing；本地优先项目应使用 --forbid-network。",
        )
    else:
        add(
            findings,
            "DATA-3",
            "PASS",
            "P1",
            "未检测到网络相关代码标记",
            "项目文本扫描",
            "仍需确认依赖包和构建产物中没有远程能力。",
        )


def check_signing_leaks(root: Path, findings: list[Finding]) -> None:
    leaks: list[str] = []
    for path in tracked_files(root):
        text = read_text(path)
        if not text:
            continue
        marker = next((item for item in SECRET_MARKERS if item in text), None)
        file_marker = next((item for item in SIGNING_FILE_MARKERS if item.lower() in text.lower()), None)
        if marker or file_marker or HOME_PATH_PATTERN.search(text):
            kinds = [item for item in (marker, file_marker, "home path" if HOME_PATH_PATTERN.search(text) else None) if item]
            leaks.append(f"{path.relative_to(root).as_posix()} ({', '.join(kinds)})")
    if leaks:
        add(
            findings,
            "SIGN-3",
            "FAIL",
            "P0",
            "跟踪文件中发现本机签名材料或 home 路径",
            ", ".join(sorted(set(leaks))),
            "停止发布；移除提交内容并改用安全的本地/CI 注入，报告中不要复制值。",
        )
    else:
        add(
            findings,
            "SIGN-3",
            "PASS",
            "P0",
            "跟踪文本未发现明显签名泄露标记",
            "git ls-files 文本扫描",
            "仍需检查暂存区、二进制附件和 CI 密钥配置。",
        )


def check_listing_evidence(root: Path, findings: list[Finding]) -> None:
    screenshots = root / "docs/appgallery/screenshots"
    if not screenshots.is_dir():
        add(
            findings,
            "LIST-1",
            "UNVERIFIED",
            "P1",
            "未发现约定的应用市场截图目录",
            "docs/appgallery/screenshots",
            "提供当前版本的真实截图，并在 AGC 侧确认尺寸、数量和内容要求。",
        )
        return
    images = [
        path
        for path in screenshots.iterdir()
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    ]
    if images:
        add(
            findings,
            "LIST-1",
            "PASS",
            "P1",
            "发现应用市场截图素材",
            ", ".join(path.relative_to(root).as_posix() for path in sorted(images)),
            "人工确认截图来自真实可达状态且不含敏感数据。",
        )
    else:
        add(
            findings,
            "LIST-1",
            "UNVERIFIED",
            "P1",
            "截图目录为空",
            "docs/appgallery/screenshots",
            "补充当前版本截图并在 AGC 侧确认素材要求。",
        )


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def check_artifact(root: Path, artifact: Path | None, findings: list[Finding]) -> None:
    """Validate the selected release archive without uploading or installing it."""
    if artifact is None:
        return

    artifact_path = artifact.expanduser()
    if not artifact_path.is_absolute():
        artifact_path = root / artifact_path
    evidence_path = _display_path(root, artifact_path)

    if not artifact_path.is_file():
        add(
            findings,
            "ARTIFACT-1",
            "FAIL",
            "P0",
            "待检发布包不存在",
            evidence_path,
            "提供实际生成的 release .app 或 .hap，再继续发布检查。",
        )
        return
    if artifact_path.suffix.lower() not in ARTIFACT_SUFFIXES:
        add(
            findings,
            "ARTIFACT-1",
            "FAIL",
            "P0",
            "待检文件不是支持的 HarmonyOS 发布包",
            evidence_path,
            "传入 .app 或 .hap 文件，不要把证书、Profile 或压缩源码当作发布包。",
        )
        return

    digest = hashlib.sha256()
    try:
        with artifact_path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        add(
            findings,
            "ARTIFACT-1",
            "FAIL",
            "P0",
            "无法读取待检发布包",
            f"{evidence_path}: {exc.__class__.__name__}",
            "确认文件权限和路径后重新提供发布包。",
        )
        return

    size_bytes = artifact_path.stat().st_size
    add(
        findings,
        "ARTIFACT-1",
        "PASS",
        "P0",
        "发现待检 release 发布包并生成摘要",
        f"{evidence_path}; size={size_bytes} bytes; sha256={digest.hexdigest()}",
        "将此摘要与上传到 AGC 的同一文件核对；本地摘要不等于 AGC 自检结果。",
    )

    try:
        with zipfile.ZipFile(artifact_path) as archive:
            broken_member = archive.testzip()
            members = archive.namelist()
    except (OSError, zipfile.BadZipFile) as exc:
        add(
            findings,
            "ARTIFACT-2",
            "FAIL",
            "P0",
            "发布包不是可读取的 HarmonyOS 压缩包",
            f"{evidence_path}: {exc.__class__.__name__}",
            "重新生成完整的 release .app/.hap，确认构建未被截断。",
        )
        return

    if broken_member:
        add(
            findings,
            "ARTIFACT-2",
            "FAIL",
            "P0",
            "发布包包含校验失败的成员文件",
            f"{evidence_path}: {broken_member}",
            "重新生成发布包并在上传前复核产物完整性。",
        )
        return

    metadata_members = sorted(
        member for member in members if Path(member).name.lower() in ARTIFACT_METADATA_NAMES
    )
    if metadata_members:
        add(
            findings,
            "ARTIFACT-2",
            "PASS",
            "P0",
            "发布包可解压且包含 HarmonyOS 元数据文件",
            f"{evidence_path}: {', '.join(metadata_members[:8])}",
            "继续核对包名、版本、签名和 AGC 软件包管理行是否一致。",
        )
    else:
        add(
            findings,
            "ARTIFACT-2",
            "UNVERIFIED",
            "P1",
            "发布包可解压但未发现常见元数据文件名",
            evidence_path,
            "确认该产物布局符合当前 DevEco/HarmonyOS 构建格式，再上传 AGC。",
        )


def run(root: Path, forbid_network: bool, artifact: Path | None = None) -> list[Finding]:
    findings: list[Finding] = []
    check_structure(root, findings)
    check_identity(root, findings)
    check_privacy(root, findings)
    check_permissions(root, findings, forbid_network)
    check_signing_leaks(root, findings)
    check_listing_evidence(root, findings)
    check_artifact(root, artifact, findings)
    return findings


def render_text(root: Path, findings: list[Finding]) -> str:
    blocking = [finding for finding in findings if finding.status in {"FAIL", "BLOCKED"}]
    unknown = [finding for finding in findings if finding.status == "UNVERIFIED"]
    overall = "BLOCKED" if blocking else ("UNVERIFIED" if unknown else "READY")
    lines = [
        f"结论: {overall}",
        f"项目: {root}",
        f"检查项: {len(findings)} | 阻断: {len(blocking)} | 未验证: {len(unknown)}",
        "",
        "| ID | 状态 | 严重度 | 发现 | 证据 | 建议 |",
        "|---|---|---|---|---|---|",
    ]
    for finding in findings:
        values = (
            finding.check_id,
            finding.status,
            finding.severity,
            finding.message,
            finding.evidence,
            finding.remediation,
        )
        lines.append("| " + " | ".join(value.replace("|", "\\|") for value in values) + " |")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument(
        "--artifact",
        type=Path,
        help="Optional release .app/.hap to inspect locally; it is never uploaded.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--forbid-network", action="store_true")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.project_root.expanduser().resolve()
    if not root.is_dir():
        print(f"project root is not a directory: {root}", file=sys.stderr)
        return 2
    findings = run(root, args.forbid_network, args.artifact)
    if args.format == "json":
        blocking = any(finding.status in {"FAIL", "BLOCKED"} for finding in findings)
        unknown = any(finding.status == "UNVERIFIED" for finding in findings)
        overall = "BLOCKED" if blocking else ("UNVERIFIED" if unknown else "READY")
        payload = {
            "project_root": str(root),
            "overall": overall,
            "findings": [asdict(finding) for finding in findings],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_text(root, findings), end="")
    if args.strict and any(finding.status in {"FAIL", "BLOCKED"} for finding in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
