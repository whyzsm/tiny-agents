#!/usr/bin/env python3
"""Resolve local Obsidian installation and candidate vaults.

This script is intentionally read-only. It detects whether Obsidian appears to
be installed, reads platform config when available, searches common document
locations for `.obsidian` directories, and prints JSON for an agent to consume.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
from pathlib import Path
from typing import Any


INSTALL_SOURCE_URL = "https://github.com/obsidianmd/obsidian-releases"
INSTALLER_COMMAND = "python3 scripts/install_obsidian.py --json"


def _home() -> Path:
    return Path.home()


def detect_obsidian() -> dict[str, Any]:
    system = platform.system().lower()
    candidates: list[str] = []

    if system == "darwin":
        candidates = [
            "/Applications/Obsidian.app",
            str(_home() / "Applications" / "Obsidian.app"),
        ]
    elif system == "windows":
        local = os.environ.get("LOCALAPPDATA")
        program_files = os.environ.get("ProgramFiles")
        program_files_x86 = os.environ.get("ProgramFiles(x86)")
        candidates = [
            str(Path(local) / "Obsidian" / "Obsidian.exe") if local else "",
            str(Path(program_files) / "Obsidian" / "Obsidian.exe") if program_files else "",
            str(Path(program_files_x86) / "Obsidian" / "Obsidian.exe") if program_files_x86 else "",
        ]
    else:
        candidates = [
            "/usr/bin/obsidian",
            "/usr/local/bin/obsidian",
            str(_home() / ".local" / "bin" / "obsidian"),
        ]

    found_paths = [path for path in candidates if path and Path(path).exists()]
    path_on_env = shutil.which("obsidian")
    if path_on_env and path_on_env not in found_paths:
        found_paths.append(path_on_env)

    return {
        "installed": bool(found_paths),
        "paths": found_paths,
        "install_required": not bool(found_paths),
        "install_source": INSTALL_SOURCE_URL if not found_paths else None,
        "installer_command": INSTALLER_COMMAND if not found_paths else None,
    }


def config_paths() -> list[Path]:
    system = platform.system().lower()
    home = _home()
    paths: list[Path] = []

    if system == "darwin":
        paths.append(home / "Library" / "Application Support" / "obsidian" / "obsidian.json")
    elif system == "windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            paths.append(Path(appdata) / "obsidian" / "obsidian.json")
    else:
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            paths.append(Path(xdg_config) / "obsidian" / "obsidian.json")
        paths.append(home / ".config" / "obsidian" / "obsidian.json")

    return paths


def read_config_vaults() -> list[dict[str, Any]]:
    vaults: list[dict[str, Any]] = []

    for config_path in config_paths():
        if not config_path.exists():
            continue
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            vaults.append(
                {
                    "path": None,
                    "exists": False,
                    "open": False,
                    "source": "obsidian-config",
                    "config_path": str(config_path),
                    "error": str(exc),
                }
            )
            continue

        raw_vaults = data.get("vaults", {})
        if isinstance(raw_vaults, dict):
            for vault_id, info in raw_vaults.items():
                if not isinstance(info, dict):
                    continue
                raw_path = info.get("path")
                if not raw_path:
                    continue
                path = Path(str(raw_path)).expanduser()
                vaults.append(
                    {
                        "id": vault_id,
                        "path": str(path),
                        "exists": path.exists(),
                        "has_obsidian_dir": (path / ".obsidian").is_dir(),
                        "open": bool(info.get("open")),
                        "timestamp": info.get("ts"),
                        "source": "obsidian-config",
                        "config_path": str(config_path),
                    }
                )

    return vaults


def explicit_vaults(vault_paths: list[str]) -> list[dict[str, Any]]:
    vaults: list[dict[str, Any]] = []

    for raw_path in vault_paths:
        path = Path(raw_path).expanduser()
        vaults.append(
            {
                "path": str(path),
                "exists": path.exists() and path.is_dir(),
                "has_obsidian_dir": (path / ".obsidian").is_dir(),
                "open": False,
                "source": "explicit-user-path",
            }
        )

    return vaults


def likely_search_roots(extra_roots: list[str]) -> list[Path]:
    home = _home()
    roots = [
        home / "Documents",
        home / "Desktop",
        home / "Library" / "Mobile Documents" / "iCloud~md~obsidian" / "Documents",
    ]
    roots.extend(Path(root).expanduser() for root in extra_roots)

    seen: set[str] = set()
    result: list[Path] = []
    for root in roots:
        key = str(root)
        if key in seen:
            continue
        seen.add(key)
        if root.exists() and root.is_dir():
            result.append(root)
    return result


def search_obsidian_dirs(extra_roots: list[str], max_depth: int) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []

    for root in likely_search_roots(extra_roots):
        root_depth = len(root.parts)
        try:
            iterator = root.rglob(".obsidian")
            for obsidian_dir in iterator:
                try:
                    if not obsidian_dir.is_dir():
                        continue
                    depth = len(obsidian_dir.parts) - root_depth
                    if depth > max_depth:
                        continue
                    vault = obsidian_dir.parent
                    found.append(
                        {
                            "path": str(vault),
                            "exists": True,
                            "has_obsidian_dir": True,
                            "open": False,
                            "source": "filesystem-search",
                        }
                    )
                except OSError:
                    continue
        except OSError:
            continue

    return found


def dedupe_vaults(vaults: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_path: dict[str, dict[str, Any]] = {}
    for vault in vaults:
        path = vault.get("path")
        if not path:
            continue
        key = str(Path(str(path)).expanduser())
        existing = by_path.get(key)
        if existing is None:
            by_path[key] = dict(vault)
            by_path[key]["path"] = key
            continue
        existing["open"] = bool(existing.get("open")) or bool(vault.get("open"))
        existing["has_obsidian_dir"] = bool(existing.get("has_obsidian_dir")) or bool(vault.get("has_obsidian_dir"))
        existing_sources = set(str(existing.get("source", "")).split(","))
        existing_sources.add(str(vault.get("source", "")))
        existing["source"] = ",".join(sorted(source for source in existing_sources if source))
    return list(by_path.values())


def choose_vault(vaults: list[dict[str, Any]]) -> tuple[str | None, list[str]]:
    warnings: list[str] = []
    usable = [vault for vault in vaults if vault.get("exists") and vault.get("has_obsidian_dir")]
    explicit_vaults = [vault for vault in usable if "explicit-user-path" in str(vault.get("source", ""))]
    open_vaults = [vault for vault in usable if vault.get("open")]

    if len(explicit_vaults) == 1:
        return str(explicit_vaults[0]["path"]), warnings
    if len(explicit_vaults) > 1:
        warnings.append("Multiple explicit Obsidian vault paths were provided; ask the user to choose one.")
        return None, warnings
    if len(open_vaults) == 1:
        return str(open_vaults[0]["path"]), warnings
    if len(open_vaults) > 1:
        warnings.append("Multiple open Obsidian vaults found; ask the user to choose.")
        return None, warnings
    if len(usable) == 1:
        return str(usable[0]["path"]), warnings
    if len(usable) > 1:
        warnings.append("Multiple candidate Obsidian vaults found; ask the user to choose.")
        return None, warnings

    warnings.append("No usable Obsidian vault found.")
    return None, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve local Obsidian installation and vault candidates.")
    parser.add_argument("--json", action="store_true", help="Print JSON output. This is the default.")
    parser.add_argument("--vault", action="append", default=[], help="Explicit Obsidian vault path. Can be passed multiple times.")
    parser.add_argument("--search", action="store_true", help="Search common directories for .obsidian folders.")
    parser.add_argument("--max-depth", type=int, default=5, help="Maximum relative depth for filesystem search.")
    parser.add_argument("--root", action="append", default=[], help="Extra root directory to search. Can be passed multiple times.")
    args = parser.parse_args()

    obsidian = detect_obsidian()
    user_vaults = explicit_vaults(args.vault)
    config_vaults = read_config_vaults()
    search_vaults = search_obsidian_dirs(args.root, args.max_depth) if args.search else []
    vaults = dedupe_vaults(user_vaults + config_vaults + search_vaults)
    selected_vault, warnings = choose_vault(vaults)

    for vault in user_vaults:
        if not vault["exists"]:
            warnings.append(f"Explicit vault path does not exist or is not a directory: {vault['path']}")
        elif not vault["has_obsidian_dir"]:
            warnings.append(f"Explicit vault path does not contain .obsidian: {vault['path']}")

    if not obsidian["installed"]:
        warnings.append(f"Obsidian was not detected. Install it from {INSTALL_SOURCE_URL} before saving to Obsidian.")

    output = {
        "obsidian_installed": obsidian["installed"],
        "obsidian_paths": obsidian["paths"],
        "install_required": obsidian["install_required"],
        "install_source": obsidian["install_source"],
        "installer_command": obsidian["installer_command"],
        "vaults": vaults,
        "selected_vault": selected_vault,
        "warnings": warnings,
        "next_action": None,
    }

    if not obsidian["installed"]:
        output["next_action"] = f"Run `{INSTALLER_COMMAND}` to install Obsidian from {INSTALL_SOURCE_URL}, then rerun this resolver."
    elif not selected_vault:
        output["next_action"] = "Ask the user to choose a vault path or provide one explicitly."

    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
