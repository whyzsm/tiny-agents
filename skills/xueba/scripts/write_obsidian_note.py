#!/usr/bin/env python3
"""Write a Markdown note into a resolved Obsidian vault.

The script validates that the target stays inside the vault and under 88-学习/.
It defaults to creating a unique filename instead of overwriting existing notes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LEARNING_ROOT = "88-学习"


def fail(message: str, code: int = 2) -> int:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False, indent=2))
    return code


def read_content(content_file: str) -> str:
    if content_file == "-":
        import sys

        return sys.stdin.read()
    return Path(content_file).read_text(encoding="utf-8")


def sanitize_filename(filename: str) -> str:
    filename = filename.strip()
    if not filename:
        filename = "未命名学习笔记.md"
    replacements = {
        "/": "／",
        "\\": "-",
        ":": "：",
        "*": "-",
        "?": "？",
        '"': "'",
        "<": "《",
        ">": "》",
        "|": "-",
    }
    for source, replacement in replacements.items():
        filename = filename.replace(source, replacement)
    filename = filename.strip(" .")
    if not filename.casefold().endswith(".md"):
        filename += ".md"
    return filename


def ensure_inside(parent: Path, child: Path) -> None:
    try:
        child.relative_to(parent)
    except ValueError as exc:
        raise ValueError("Target path escapes the vault.") from exc


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 2
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def cleanup(paths: list[str]) -> dict[str, Any]:
    removed = 0
    failed = 0
    for raw_path in paths:
        try:
            path = Path(raw_path).expanduser()
            if path.is_file():
                path.unlink()
                removed += 1
        except OSError:
            failed += 1
    return {"requested": len(paths), "removed": removed, "failed": failed}


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a Markdown note into an Obsidian vault under 88-学习/.")
    parser.add_argument("--vault", required=True, help="Resolved Obsidian vault path.")
    parser.add_argument("--relative-dir", required=True, help="Target directory relative to vault. Must start with 88-学习.")
    parser.add_argument("--filename", required=True, help="Target Markdown filename.")
    parser.add_argument("--content-file", required=True, help="Markdown content file, or '-' for stdin.")
    parser.add_argument("--if-exists", choices=["uniquify", "fail", "overwrite"], default="uniquify")
    parser.add_argument("--cleanup", action="append", default=[], help="Temporary file to remove after successful write.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and return target path without writing.")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        return fail("Vault path does not exist or is not a directory.")
    if not (vault / ".obsidian").is_dir():
        return fail("Vault path does not contain .obsidian.")

    relative_dir = Path(args.relative_dir)
    if relative_dir.is_absolute() or ".." in relative_dir.parts:
        return fail("Relative directory must be a safe path inside the vault.")
    if not relative_dir.parts or relative_dir.parts[0] != LEARNING_ROOT:
        return fail("Relative directory must start with 88-学习/.")

    filename = sanitize_filename(args.filename)
    if Path(filename).name != filename:
        return fail("Filename must not contain path separators.")

    try:
        content = read_content(args.content_file)
    except OSError as exc:
        return fail(f"Could not read content file: {exc}")

    target_dir = (vault / relative_dir).resolve()
    target_path = (target_dir / filename).resolve()
    try:
        ensure_inside(vault, target_dir)
        ensure_inside(vault, target_path)
    except ValueError as exc:
        return fail(str(exc))

    overwritten = False
    if target_path.exists():
        if args.if_exists == "fail":
            return fail("Target file already exists.")
        if args.if_exists == "uniquify":
            target_path = unique_path(target_path)
        else:
            overwritten = True

    output = {
        "ok": True,
        "dry_run": args.dry_run,
        "saved_path": str(target_path),
        "relative_path": str(target_path.relative_to(vault)),
        "overwritten": overwritten,
        "cleanup": {"requested": len(args.cleanup), "removed": 0, "failed": 0},
    }

    if not args.dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
        output["cleanup"] = cleanup(args.cleanup)

    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
