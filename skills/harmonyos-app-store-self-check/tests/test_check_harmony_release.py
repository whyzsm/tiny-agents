from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_harmony_release.py"


def write_fixture(root: Path, *, with_secret: bool = False, with_network: bool = False) -> None:
    (root / "AppScope").mkdir(parents=True)
    (root / "entry/src/main/resources/base/profile").mkdir(parents=True)
    (root / "docs/legal").mkdir(parents=True)
    (root / "docs/appgallery/screenshots").mkdir(parents=True)
    (root / "AppScope/app.json5").write_text(
        '{"app":{"bundleName":"io.example.app","label":"$string:app_name","versionCode":1,"versionName":"1.0.0"}}\n',
        encoding="utf-8",
    )
    (root / "entry/src/main/module.json5").write_text(
        '{"module":{"name":"entry","mainElement":"EntryAbility","pages":"$profile:main_pages"}}\n',
        encoding="utf-8",
    )
    (root / "entry/src/main/resources/base/profile/main_pages.json").write_text(
        '{"src":["pages/Index"]}\n', encoding="utf-8"
    )
    (root / "build-profile.json5").write_text(
        '{"app":{"products":[{"targetSdkVersion":"6.1.0(23)","compatibleSdkVersion":"6.1.0(23)"}]},"buildModeSet":[{"name":"release"}]}\n',
        encoding="utf-8",
    )
    (root / "entry/build-profile.json5").parent.mkdir(parents=True, exist_ok=True)
    (root / "entry/build-profile.json5").write_text('{"targets":[{"name":"default"}]}\n', encoding="utf-8")
    (root / "hvigorfile.ts").write_text("export default {};\n", encoding="utf-8")
    (root / "oh-package.json5").write_text('{"modelVersion":"5.0.0"}\n', encoding="utf-8")
    (root / "docs/legal/privacy-policy.html").write_text(
        "<h1>隐私政策</h1><p>说明照片数据的用途、权限、保存和删除。</p>\n", encoding="utf-8"
    )
    (root / "docs/appgallery/screenshots/home.png").write_bytes(b"fixture")
    if with_secret:
        (root / "build-profile.json5").write_text(
            (root / "build-profile.json5").read_text(encoding="utf-8")
            + '"keyPassword":"redacted","storeFile":"/Users/test/app.p12"\n',
            encoding="utf-8",
        )
    if with_network:
        (root / "entry/src/main/ets").mkdir(parents=True)
        (root / "entry/src/main/ets/Network.ets").write_text(
            "import http from '@ohos.net.http';\n", encoding="utf-8"
        )


class HarmonyReleaseCheckerTests(unittest.TestCase):
    def run_checker(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--project-root", str(root), "--format", "json", *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_clean_fixture_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root)
            result = self.run_checker(root)
            self.assertEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["overall"], "READY")

    def test_secret_is_blocking_in_strict_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, with_secret=True)
            result = self.run_checker(root, "--strict")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["overall"], "BLOCKED")
            self.assertTrue(any(item["check_id"] == "SIGN-3" for item in payload["findings"]))

    def test_local_first_network_check_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, with_network=True)
            result = self.run_checker(root, "--forbid-network", "--strict")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertTrue(any(item["check_id"] == "DATA-3" for item in payload["findings"]))

    def test_release_artifact_is_checked_without_upload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root)
            artifact = root / "build" / "release.app"
            artifact.parent.mkdir()
            with zipfile.ZipFile(artifact, "w") as archive:
                archive.writestr("module.json", '{"module":{"name":"entry"}}')
            result = self.run_checker(root, "--artifact", str(artifact))
            self.assertEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            artifact_findings = {
                item["check_id"]: item for item in payload["findings"] if item["check_id"].startswith("ARTIFACT-")
            }
            self.assertEqual(artifact_findings["ARTIFACT-1"]["status"], "PASS")
            self.assertEqual(artifact_findings["ARTIFACT-2"]["status"], "PASS")

    def test_missing_release_artifact_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root)
            result = self.run_checker(root, "--artifact", "missing.app", "--strict")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertTrue(
                any(
                    item["check_id"] == "ARTIFACT-1" and item["status"] == "FAIL"
                    for item in payload["findings"]
                )
            )


if __name__ == "__main__":
    unittest.main()
