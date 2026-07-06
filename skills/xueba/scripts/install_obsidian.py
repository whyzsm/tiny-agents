#!/usr/bin/env python3
"""Install Obsidian from the official GitHub releases repository.

The installer is intended for agents to run only after Obsidian detection fails.
It downloads the latest matching asset from:
https://github.com/obsidianmd/obsidian-releases
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import stat
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Any


RELEASE_API_URL = "https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest"
RELEASES_URL = "https://github.com/obsidianmd/obsidian-releases"


def emit(payload: dict[str, Any], code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return code


def system_name() -> str:
    return platform.system().lower()


def normalized_arch() -> str:
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        return "x64"
    if machine in {"arm64", "aarch64"}:
        return "arm64"
    return machine


def fetch_latest_release(timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(RELEASE_API_URL, headers={"User-Agent": "xueba-skill-installer"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def asset_priority(asset_name: str) -> int | None:
    name = asset_name.lower()
    system = system_name()
    arch = normalized_arch()

    if system == "darwin":
        if name.endswith(".dmg"):
            return 100
        return None
    if system == "linux":
        if "appimage" in name:
            if arch == "arm64" and ("arm64" in name or "aarch64" in name):
                return 110
            if arch == "x64" and ("x86_64" in name or "amd64" in name or "appimage" in name):
                return 100
            return 80
        if name.endswith(".deb"):
            return 60
        return None
    if system == "windows":
        if name.endswith(".exe"):
            return 100
        return None
    return None


def select_asset(release: dict[str, Any]) -> dict[str, Any]:
    assets = release.get("assets", [])
    ranked: list[tuple[int, dict[str, Any]]] = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        name = str(asset.get("name") or "")
        url = asset.get("browser_download_url")
        priority = asset_priority(name)
        if priority is not None and url:
            ranked.append((priority, asset))

    if not ranked:
        raise RuntimeError(f"No matching Obsidian installer asset found for {platform.system()} {platform.machine()}.")

    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[0][1]


def download_asset(asset: dict[str, Any], download_dir: Path, timeout: int) -> Path:
    url = str(asset["browser_download_url"])
    filename = str(asset.get("name") or "obsidian-installer")
    target = download_dir / filename
    request = urllib.request.Request(url, headers={"User-Agent": "xueba-skill-installer"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        target.write_bytes(response.read())
    return target


def install_macos_dmg(dmg_path: Path, install_dir: Path, overwrite: bool) -> Path:
    mount_dir = Path(tempfile.mkdtemp(prefix="xueba-obsidian-mount."))
    attached = False
    try:
        subprocess.run(["hdiutil", "attach", str(dmg_path), "-mountpoint", str(mount_dir), "-nobrowse", "-quiet"], check=True)
        attached = True
        apps = list(mount_dir.glob("*.app"))
        if not apps:
            raise RuntimeError("Mounted DMG did not contain an .app bundle.")
        source_app = apps[0]
        install_dir.mkdir(parents=True, exist_ok=True)
        target_app = install_dir / "Obsidian.app"
        if target_app.exists():
            if not overwrite:
                raise RuntimeError(f"Target already exists: {target_app}")
            shutil.rmtree(target_app)
        shutil.copytree(source_app, target_app)
        return target_app
    finally:
        if attached:
            subprocess.run(["hdiutil", "detach", str(mount_dir), "-quiet"], check=False)
        shutil.rmtree(mount_dir, ignore_errors=True)


def install_linux_asset(asset_path: Path, install_dir: Path, overwrite: bool) -> Path:
    name = asset_path.name.lower()
    if "appimage" in name:
        install_dir.mkdir(parents=True, exist_ok=True)
        target = install_dir / "obsidian"
        if target.exists() and not overwrite:
            raise RuntimeError(f"Target already exists: {target}")
        shutil.copy2(asset_path, target)
        mode = target.stat().st_mode
        target.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return target
    if name.endswith(".deb"):
        subprocess.run(["sudo", "dpkg", "-i", str(asset_path)], check=True)
        return Path(shutil.which("obsidian") or "/usr/bin/obsidian")
    raise RuntimeError(f"Unsupported Linux asset: {asset_path.name}")


def install_windows_exe(exe_path: Path, silent: bool) -> Path:
    command = [str(exe_path)]
    if silent:
        command.append("/S")
    subprocess.run(command, check=True)
    return exe_path


def install_asset(asset_path: Path, overwrite: bool, silent: bool, install_dir: str | None) -> Path:
    system = system_name()
    if system == "darwin":
        target_dir = Path(install_dir).expanduser() if install_dir else Path.home() / "Applications"
        return install_macos_dmg(asset_path, target_dir, overwrite)
    if system == "linux":
        target_dir = Path(install_dir).expanduser() if install_dir else Path.home() / ".local" / "bin"
        return install_linux_asset(asset_path, target_dir, overwrite)
    if system == "windows":
        return install_windows_exe(asset_path, silent)
    raise RuntimeError(f"Unsupported operating system: {platform.system()}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Obsidian from official GitHub releases.")
    parser.add_argument("--json", action="store_true", help="Print JSON output. This is the default.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve the installer asset but do not download or install it.")
    parser.add_argument("--download-dir", default=None, help="Directory for downloaded installer assets.")
    parser.add_argument("--install-dir", default=None, help="User-level install directory. Defaults to ~/Applications on macOS and ~/.local/bin on Linux.")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing user-level Obsidian target.")
    parser.add_argument("--silent", action="store_true", help="Use silent install flags when supported.")
    parser.add_argument("--timeout", type=int, default=60, help="Network timeout in seconds.")
    args = parser.parse_args()

    try:
        release = fetch_latest_release(args.timeout)
        asset = select_asset(release)
        result: dict[str, Any] = {
            "ok": True,
            "dry_run": args.dry_run,
            "source": RELEASES_URL,
            "release": release.get("tag_name") or release.get("name"),
            "asset_name": asset.get("name"),
            "asset_url": asset.get("browser_download_url"),
            "installed_path": None,
            "next_action": None,
        }
        if args.dry_run:
            result["next_action"] = "Run without --dry-run to download and install Obsidian, then rerun resolve_obsidian_vault.py."
            return emit(result)

        download_root = Path(args.download_dir).expanduser() if args.download_dir else Path(tempfile.mkdtemp(prefix="xueba-obsidian-install."))
        download_root.mkdir(parents=True, exist_ok=True)
        asset_path = download_asset(asset, download_root, args.timeout)
        installed_path = install_asset(asset_path, args.overwrite, args.silent, args.install_dir)
        result["installed_path"] = str(installed_path)
        result["next_action"] = "Rerun scripts/resolve_obsidian_vault.py --json to verify Obsidian and choose a vault."
        return emit(result)
    except Exception as exc:
        return emit(
            {
                "ok": False,
                "source": RELEASES_URL,
                "error": str(exc),
                "next_action": "Install Obsidian from the official GitHub releases repository, then rerun resolve_obsidian_vault.py.",
            },
            code=1,
        )


if __name__ == "__main__":
    raise SystemExit(main())
