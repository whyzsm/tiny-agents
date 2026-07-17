#!/usr/bin/env python3
"""Prepare a skill-creator-compatible model eval workspace for xueba.

This script does not run model evals and does not fabricate benchmark results.
It creates the directory structure, prompts, metadata, skill snapshots, and
commands needed to run real model-output comparisons later.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_EVAL_IDS = [2, 4, 6, 7, 9, 10, 11, 13]
DEFAULT_BASELINE_REF = "9b38d23"
IGNORE_NAMES = {
    ".git",
    ".xueba-eval-report",
    ".xueba-runtime",
    "__pycache__",
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slugify(value: str, fallback: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return (slug[:48] or fallback).strip("-")


def parse_eval_ids(raw: str | None) -> list[int]:
    if not raw:
        return DEFAULT_EVAL_IDS
    result: list[int] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        result.append(int(item))
    return result


def ignore_copy(directory: str, names: list[str]) -> set[str]:
    ignored = {name for name in names if name in IGNORE_NAMES or name.endswith(".pyc")}
    return ignored


def copy_current_skill(skill_root: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(skill_root, target, ignore=ignore_copy)


def export_baseline(skill_root: Path, target: Path, baseline_ref: str) -> bool:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(
        ["git", "archive", "--format=tar", baseline_ref],
        cwd=skill_root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if archive.returncode != 0:
        (target / "BASELINE_EXPORT_FAILED.txt").write_text(archive.stderr.decode("utf-8", errors="replace"), encoding="utf-8")
        return False
    extract = subprocess.run(
        ["tar", "-x", "-C", str(target)],
        input=archive.stdout,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if extract.returncode != 0:
        (target / "BASELINE_EXPORT_FAILED.txt").write_text(extract.stderr.decode("utf-8", errors="replace"), encoding="utf-8")
        return False
    return True


def build_run_prompt(
    eval_case: dict[str, Any],
    outputs_dir: Path,
    skill_path: Path | None,
    configuration: str,
) -> str:
    skill_line = f"- Skill path: {skill_path}" if skill_path else "- Skill path: none. Do not read or use xueba skill files."
    files = eval_case.get("files") or []
    file_lines = "\n".join(f"  - {item}" for item in files) if files else "  - none"
    expectations = "\n".join(f"  - {item}" for item in eval_case.get("expectations", []))
    return f"""Execute this xueba evaluation task.

Configuration: {configuration}
{skill_line}

Task:
{eval_case["prompt"]}

Input files:
{file_lines}

Save outputs to:
{outputs_dir}

Required output files:
- `final.md`: final user-facing response.
- If you generate a study note, expert spec, runtime transcript, or upgrade report, save it as a separate Markdown file in the outputs directory.
- If the task asks to save to Obsidian, do not modify the user's real vault during this evaluation. Instead, write the note under the outputs directory and include the intended vault-relative path in `final.md`.

Evaluation expectations:
{expectations}

Constraints:
- Do not modify files outside the outputs directory.
- Do not fabricate access to private/authenticated source content.
- Do not claim autonomous runtime behavior.
- Keep enough detail in `final.md` for a grader to evaluate the expectations.
"""


def build_grading_template(expectations: list[str]) -> dict[str, Any]:
    rows = [{"text": item, "passed": False, "evidence": "Not graded yet."} for item in expectations]
    return {
        "expectations": rows,
        "summary": {
            "passed": 0,
            "failed": len(rows),
            "total": len(rows),
            "pass_rate": 0.0,
        },
        "execution_metrics": {
            "total_tool_calls": 0,
            "total_steps": 0,
            "errors_encountered": 0,
            "output_chars": 0,
            "transcript_chars": 0,
        },
        "timing": {
            "total_duration_seconds": 0.0,
        },
        "user_notes_summary": {
            "uncertainties": ["Not graded yet."],
            "needs_review": [],
            "workarounds": [],
        },
    }


def shell_quote(value: Path | str) -> str:
    text = str(value)
    return "'" + text.replace("'", "'\"'\"'") + "'"


def default_skill_creator_root(skill_root: Path) -> Path:
    configured = os.environ.get("SKILL_CREATOR_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()

    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    installed = codex_home / "skills" / ".system" / "skill-creator"
    if installed.exists():
        return installed.resolve()

    repository_copy = skill_root.parent / "skill-creator"
    return repository_copy.resolve()


def create_workspace(args: argparse.Namespace) -> dict[str, Any]:
    skill_root = Path(args.skill_root).expanduser().resolve() if args.skill_root else Path(__file__).resolve().parents[1]
    workspace_root = Path(args.workspace).expanduser().resolve() if args.workspace else skill_root.parent / f"{skill_root.name}-workspace"
    iteration_dir = workspace_root / args.iteration
    eval_ids = parse_eval_ids(args.eval_ids)
    eval_data = read_json(skill_root / "evals" / "evals.json")
    cases_by_id = {int(item["id"]): item for item in eval_data["evals"]}
    selected_cases = [cases_by_id[item] for item in eval_ids]

    skill_snapshot = workspace_root / "skill-current"
    baseline_snapshot = workspace_root / f"skill-baseline-{args.baseline_ref}"
    copy_current_skill(skill_root, skill_snapshot)
    baseline_ok = export_baseline(skill_root, baseline_snapshot, args.baseline_ref)

    iteration_dir.mkdir(parents=True, exist_ok=True)
    commands: list[str] = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "CODEX_BIN=${CODEX_BIN:-/Applications/Codex.app/Contents/Resources/codex}",
        "CODEX_EXEC_ARGS=${CODEX_EXEC_ARGS:---dangerously-bypass-approvals-and-sandbox}",
        "read -r -a CODEX_ARGS <<< \"$CODEX_EXEC_ARGS\"",
        "",
    ]
    run_count = 0

    for eval_case in selected_cases:
        eval_id = int(eval_case["id"])
        eval_name = f"eval-{eval_id:02d}-{slugify(eval_case['prompt'], 'case')}"
        eval_dir = iteration_dir / eval_name
        metadata = {
            "eval_id": eval_id,
            "eval_name": eval_name,
            "prompt": eval_case["prompt"],
            "expected_output": eval_case.get("expected_output", ""),
            "assertions": eval_case.get("expectations", []),
            "created_at": now(),
        }
        write_json(eval_dir / "eval_metadata.json", metadata)

        configs: list[tuple[str, Path | None]] = [("with_skill", skill_snapshot)]
        if args.include_old_skill:
            configs.append(("old_skill", baseline_snapshot if baseline_ok else None))
        if args.include_without_skill:
            configs.append(("without_skill", None))

        for config_name, config_skill in configs:
            run_dir = eval_dir / config_name / "run-1"
            outputs_dir = run_dir / "outputs"
            outputs_dir.mkdir(parents=True, exist_ok=True)
            write_json(run_dir / "eval_metadata.json", metadata)
            (outputs_dir / ".gitkeep").write_text("", encoding="utf-8")
            prompt = build_run_prompt(eval_case, outputs_dir, config_skill, config_name)
            (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")
            write_json(run_dir / "grading.template.json", build_grading_template(eval_case.get("expectations", [])))
            commands.extend(
                [
                    f"echo 'Running {eval_name} / {config_name}'",
                    f"mkdir -p {shell_quote(outputs_dir)}",
                    f"\"$CODEX_BIN\" exec -C {shell_quote(skill_root)} \"${{CODEX_ARGS[@]}}\" --output-last-message {shell_quote(outputs_dir / 'final.md')} < {shell_quote(run_dir / 'prompt.md')}",
                    "",
                ]
            )
            run_count += 1

    skill_creator_root = Path(args.skill_creator_root).expanduser().resolve() if args.skill_creator_root else default_skill_creator_root(skill_root)
    reviewer_commands = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        f"SKILL_CREATOR_ROOT=${{SKILL_CREATOR_ROOT:-{shell_quote(skill_creator_root)}}}",
        f"ITERATION_DIR={shell_quote(iteration_dir)}",
        "PYTHON_BIN=${PYTHON_BIN:-}",
        "if [[ -z \"$PYTHON_BIN\" ]]; then",
        "  for candidate in python3.12 python3.11 python3; do",
        "    if command -v \"$candidate\" >/dev/null 2>&1 && \"$candidate\" - <<'PY' >/dev/null 2>&1",
        "import sys",
        "raise SystemExit(0 if sys.version_info >= (3, 10) else 1)",
        "PY",
        "    then",
        "      PYTHON_BIN=\"$candidate\"",
        "      break",
        "    fi",
        "  done",
        "fi",
        "if [[ -z \"$PYTHON_BIN\" ]]; then",
        "  echo 'Python 3.10+ is required for skill-creator eval viewer.' >&2",
        "  exit 1",
        "fi",
        f"\"$PYTHON_BIN\" \"$SKILL_CREATOR_ROOT/scripts/aggregate_benchmark.py\" \"$ITERATION_DIR\" --skill-name xueba --skill-path {shell_quote(skill_snapshot)}",
        f"\"$PYTHON_BIN\" \"$SKILL_CREATOR_ROOT/eval-viewer/generate_review.py\" \"$ITERATION_DIR\" --skill-name xueba --benchmark \"$ITERATION_DIR/benchmark.json\" --static {shell_quote(iteration_dir / 'review.html')}",
    ]

    (workspace_root / "run_with_codex.sh").write_text("\n".join(commands) + "\n", encoding="utf-8")
    (workspace_root / "generate_viewer.sh").write_text("\n".join(reviewer_commands) + "\n", encoding="utf-8")
    (workspace_root / "MODEL_EVAL_RUNBOOK.md").write_text(build_runbook(workspace_root, iteration_dir, skill_snapshot, baseline_snapshot, eval_ids, baseline_ok), encoding="utf-8")
    for script in [workspace_root / "run_with_codex.sh", workspace_root / "generate_viewer.sh"]:
        script.chmod(0o755)

    return {
        "ok": True,
        "workspace": str(workspace_root),
        "iteration_dir": str(iteration_dir),
        "skill_snapshot": str(skill_snapshot),
        "baseline_snapshot": str(baseline_snapshot),
        "baseline_ok": baseline_ok,
        "eval_ids": eval_ids,
        "run_count": run_count,
        "run_script": str(workspace_root / "run_with_codex.sh"),
        "viewer_script": str(workspace_root / "generate_viewer.sh"),
        "runbook": str(workspace_root / "MODEL_EVAL_RUNBOOK.md"),
    }


def build_runbook(
    workspace_root: Path,
    iteration_dir: Path,
    skill_snapshot: Path,
    baseline_snapshot: Path,
    eval_ids: list[int],
    baseline_ok: bool,
) -> str:
    baseline_line = f"`{baseline_snapshot}`" if baseline_ok else f"`{baseline_snapshot}` export failed; inspect `BASELINE_EXPORT_FAILED.txt`."
    return f"""# Xueba Model Eval Runbook

Generated at: `{now()}`

## Scope

- Eval IDs: `{",".join(str(item) for item in eval_ids)}`
- Current skill snapshot: `{skill_snapshot}`
- Baseline snapshot: {baseline_line}
- Iteration directory: `{iteration_dir}`

This workspace prepares real model-output review. It does not contain completed benchmark results until the run and grading steps are executed.

## 1. Run model outputs

```bash
{workspace_root / "run_with_codex.sh"}
```

Each run writes `final.md` under its `outputs/` directory.

The run script defaults to `CODEX_EXEC_ARGS=--dangerously-bypass-approvals-and-sandbox` because current Codex CLI non-interactive mode does not expose an `--ask-for-approval never` flag. Override `CODEX_EXEC_ARGS` if your local CLI has a safer non-interactive profile.

## 2. Grade outputs

For each `run-1`, create `grading.json` from `grading.template.json` after reviewing the generated outputs. The viewer and benchmark aggregator require `grading.json` fields:

- `expectations[].text`
- `expectations[].passed`
- `expectations[].evidence`
- `summary.passed`
- `summary.failed`
- `summary.total`
- `summary.pass_rate`

Do not rename `grading.template.json` without actually grading the output.

## 3. Generate benchmark and static viewer

```bash
{workspace_root / "generate_viewer.sh"}
```

Expected outputs after grading:

- `{iteration_dir / "benchmark.json"}`
- `{iteration_dir / "benchmark.md"}`
- `{iteration_dir / "review.html"}`

The viewer script requires Python 3.10+ because `skill-creator/eval-viewer/generate_review.py` uses modern type syntax. Set `PYTHON_BIN=/path/to/python3.11` if auto-detection fails.

## 4. Review

Open `review.html`, inspect outputs and grades, then save feedback as `feedback.json` in the workspace if further iteration is needed.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare xueba model eval workspace.")
    parser.add_argument("--skill-root", default=None)
    parser.add_argument("--workspace", default=None)
    parser.add_argument("--iteration", default="iteration-1")
    parser.add_argument("--eval-ids", default=None, help="Comma-separated eval ids. Defaults to core 8.")
    parser.add_argument("--baseline-ref", default=DEFAULT_BASELINE_REF)
    parser.add_argument("--skill-creator-root", default=None)
    parser.add_argument("--include-old-skill", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--include-without-skill", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    result = create_workspace(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
