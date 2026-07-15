#!/usr/bin/env python3
"""Create a safe, minimal Codex Skill package skeleton.

The generator is intentionally limited to scaffolding. It never overwrites an
existing directory and it does not install, commit, push, or publish anything.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ALLOWED_RESOURCES = {"scripts", "references", "assets"}
MAX_NAME_LENGTH = 64


def normalize_name(raw_name: str) -> str:
    name = raw_name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = re.sub(r"-{2,}", "-", name).strip("-")
    return name


def title_for(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def yaml_string(value: str) -> str:
    """Use JSON quoting, which is also valid YAML for scalar strings."""

    return json.dumps(value, ensure_ascii=False)


def parse_resources(raw_resources: str) -> list[str]:
    resources = [item.strip() for item in raw_resources.split(",") if item.strip()]
    invalid = sorted(set(resources) - ALLOWED_RESOURCES)
    if invalid:
        choices = ", ".join(sorted(ALLOWED_RESOURCES))
        raise ValueError(f"unknown resource(s): {', '.join(invalid)}; choose from {choices}")
    return list(dict.fromkeys(resources))


def build_skill_md(name: str, description: str, display_name: str) -> str:
    return f"""---
name: {name}
description: {yaml_string(description)}
---

# {display_name}

## Overview

Describe the capability, its target user, and the boundary of this Skill.

## Triggers

- Add a concrete natural-language request that should activate this Skill.
- Add a second request covering a meaningful variation.

## Workflow

1. Inspect the provided context and identify missing blocking information.
2. Execute the smallest valid workflow for the request.
3. Validate the output with the checks named below.
4. Report files, evidence, assumptions, and remaining risks.

## Guardrails

- Ask before destructive, external, installation, publication, commit, or push actions.
- Do not use secrets, local absolute paths, or undocumented private interfaces.

## Validation

- Run the relevant structural and behavioral checks for this Skill.
- Replace this placeholder with concrete commands before delivery.
"""


def build_openai_yaml(
    name: str,
    display_name: str,
    short_description: str,
    default_prompt: str,
) -> str:
    return f"""interface:
  display_name: {yaml_string(display_name)}
  short_description: {yaml_string(short_description)}
  default_prompt: {yaml_string(default_prompt)}
policy:
  allow_implicit_invocation: true
"""


def build_source_json(name: str, resources: list[str], files: list[str]) -> str:
    source = {
        "name": name,
        "kind": "skill",
        "status": "draft",
        "source_kind": "repo-authored",
        "source_ref": "repo-local/generated",
        "converted_for": "codex-skills",
        "resources": resources,
        "files": files,
        "repo_only": True,
    }
    return json.dumps(source, ensure_ascii=False, indent=2) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Skill name; normalized to lowercase hyphen-case")
    parser.add_argument("--path", required=True, help="Parent directory for the new Skill")
    parser.add_argument("--description", required=True, help="Trigger-aware Skill description")
    parser.add_argument("--display-name", default="", help="Optional UI-facing name")
    parser.add_argument("--short-description", default="", help="Optional UI-facing summary")
    parser.add_argument("--default-prompt", default="", help="Optional invocation prompt")
    parser.add_argument(
        "--resources",
        default="",
        help="Comma-separated resource directories: scripts,references,assets",
    )
    return parser


def create_skill(args: argparse.Namespace) -> Path:
    name = normalize_name(args.name)
    if not name:
        raise ValueError("name must contain at least one letter or digit")
    if len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"name is too long ({len(name)}); maximum is {MAX_NAME_LENGTH}")

    description = args.description.strip()
    if not description:
        raise ValueError("description cannot be empty")
    if len(description) > 1024:
        raise ValueError("description cannot exceed 1024 characters")
    if "<" in description or ">" in description:
        raise ValueError("description cannot contain angle brackets")

    resources = parse_resources(args.resources)
    display_name = args.display_name.strip() or title_for(name)
    short_description = (
        args.short_description.strip() or "Create and validate generated Skill packages"
    )
    if len(short_description) > 64:
        raise ValueError("short-description cannot exceed 64 characters")
    default_prompt = (
        args.default_prompt.strip()
        or f"Use ${name} to design and generate a Skill package."
    )

    skill_dir = Path(args.path).expanduser().resolve() / name
    if skill_dir.exists():
        raise FileExistsError(f"Skill directory already exists: {skill_dir}")

    files = ["SKILL.md", "agents/openai.yaml", "source.json"]
    skill_dir.mkdir(parents=True)
    (skill_dir / "agents").mkdir()
    for resource in resources:
        (skill_dir / resource).mkdir()

    (skill_dir / "SKILL.md").write_text(
        build_skill_md(name, description, display_name), encoding="utf-8"
    )
    (skill_dir / "agents/openai.yaml").write_text(
        build_openai_yaml(name, display_name, short_description, default_prompt),
        encoding="utf-8",
    )
    (skill_dir / "source.json").write_text(
        build_source_json(name, resources, files), encoding="utf-8"
    )
    return skill_dir


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        skill_dir = create_skill(args)
    except (FileExistsError, ValueError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 1

    print(f"[OK] Created Skill skeleton at {skill_dir}")
    print("[NEXT] Complete SKILL.md, remove unused resource directories, then validate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
