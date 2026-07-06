#!/usr/bin/env python3
"""Check Obsidian double links in a Markdown draft.

The script reports unresolved `[[...]]` targets so the agent can convert them
to plain text before writing notes that would create empty Obsidian files.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


LINK_RE = re.compile(r"(?<!!)\[\[([^\]\n]+)\]\]")


def fail(message: str, code: int = 2) -> int:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False, indent=2))
    return code


def read_content(content_file: str) -> str:
    if content_file == "-":
        return sys.stdin.read()
    return Path(content_file).read_text(encoding="utf-8")


def normalize_target(raw_target: str) -> str:
    target = raw_target.split("|", 1)[0]
    target = target.split("#", 1)[0]
    target = target.strip()
    if target.casefold().endswith(".md"):
        target = target[:-3]
    return target


def markdown_index(vault: Path) -> set[str]:
    names: set[str] = set()
    for path in vault.rglob("*.md"):
        try:
            relative = path.relative_to(vault)
        except ValueError:
            continue
        without_suffix = relative.with_suffix("")
        names.add(path.stem.casefold())
        names.add(str(without_suffix).casefold())
    return names


def check_links(content: str, vault: Path, created: list[str]) -> dict[str, Any]:
    index = markdown_index(vault)
    for raw_path in created:
        path = Path(raw_path)
        if path.suffix.casefold() == ".md":
            path = path.with_suffix("")
        index.add(path.name.casefold())
        index.add(str(path).casefold())

    links: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in LINK_RE.finditer(content):
        raw = match.group(1).strip()
        target = normalize_target(raw)
        if not target:
            continue
        key = target.casefold()
        if key in seen:
            continue
        seen.add(key)
        resolved = key in index
        links.append(
            {
                "raw": raw,
                "target": target,
                "resolved": resolved,
            }
        )

    unresolved = [link for link in links if not link["resolved"]]
    return {
        "ok": not unresolved,
        "link_count": len(links),
        "unresolved_count": len(unresolved),
        "links": links,
        "unresolved": unresolved,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Obsidian double links in a Markdown draft.")
    parser.add_argument("--vault", required=True, help="Resolved Obsidian vault path.")
    parser.add_argument("--content-file", required=True, help="Markdown content file, or '-' for stdin.")
    parser.add_argument("--created", action="append", default=[], help="Note path that will be created in the same task. Can be passed multiple times.")
    parser.add_argument("--json", action="store_true", help="Print JSON output. This is the default.")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        return fail("Vault path does not exist or is not a directory.")

    try:
        content = read_content(args.content_file)
    except OSError as exc:
        return fail(f"Could not read content file: {exc}")

    result = check_links(content, vault, args.created)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
