#!/usr/bin/env python3
"""Create a new project from the bundled enterprise React template."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


TOKEN_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
TEXT_SUFFIXES = {
    "",
    ".css",
    ".example",
    ".html",
    ".js",
    ".json",
    ".md",
    ".ts",
    ".tsx",
}


def normalize_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9._-]+", "-", value.strip().lower())
    return re.sub(r"-{2,}", "-", normalized).strip("-._")


def display_title(package_name: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[-_.]+", package_name))


def validate_destination(target: Path) -> None:
    if target.exists() and not target.is_dir():
        raise ValueError(f"target exists and is not a directory: {target}")
    if target.exists() and any(target.iterdir()):
        raise ValueError(f"target directory is not empty: {target}")


def replace_tokens(target: Path, values: dict[str, str]) -> None:
    for path in sorted(target.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        content = path.read_text(encoding="utf-8")
        updated = content
        for token, value in values.items():
            updated = updated.replace(token, value)
        if updated != content:
            path.write_text(updated, encoding="utf-8")


def create_project(target: Path, package_name: str, title: str, dry_run: bool) -> None:
    template = Path(__file__).resolve().parent.parent / "assets" / "template"
    if not (template / "package.json").is_file() or not (template / "src").is_dir():
        raise ValueError(f"bundled template is incomplete: {template}")

    validate_destination(target)
    if dry_run:
        print(f"[DRY RUN] Would create {package_name} at {target}")
        return

    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, target, dirs_exist_ok=True)
    replace_tokens(
        target,
        {
            "__PROJECT_NAME__": package_name,
            "__PROJECT_TITLE__": title,
            "__PROJECT_INITIAL__": title[:1].upper(),
        },
    )
    print(f"[OK] Created {package_name} at {target}")
    print("[NEXT] Install dependencies with pnpm install, then run pnpm check")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="New or empty destination directory")
    parser.add_argument("--name", default="", help="npm package name")
    parser.add_argument("--title", default="", help="Display title")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    target = Path(args.target).expanduser().resolve()
    package_name = normalize_name(args.name or target.name)
    if not package_name or not TOKEN_PATTERN.fullmatch(package_name):
        print(f"[ERROR] invalid npm package name: {package_name!r}", file=sys.stderr)
        return 1
    title = args.title.strip() or display_title(package_name)

    try:
        create_project(target, package_name, title, args.dry_run)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
