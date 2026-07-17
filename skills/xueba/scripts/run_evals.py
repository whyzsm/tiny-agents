#!/usr/bin/env python3
"""Run deterministic checks for the xueba skill package.

This does not call an LLM. It validates the local skill metadata, eval files,
required expert references, and optionally a generated Markdown note.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "VERSION",
    "CHANGELOG.md",
    "docs/runtime-operations.md",
    "docs/release-v2.0.md",
    "docs/model-eval-workflow.md",
    "references/note-template.md",
    "references/tag-taxonomy.md",
    "references/obsidian-workflow.md",
    "references/authenticated-sources.md",
    "references/learning-expert.md",
    "references/expert-personality.md",
    "references/expert-capabilities.md",
    "references/quality-gate.md",
    "references/xueba-agent.md",
    "references/agent-object.md",
    "references/runtime-agent.md",
    "references/upgrade-mode.md",
    "scripts/resolve_obsidian_vault.py",
    "scripts/install_obsidian.py",
    "scripts/classify_learning_path.py",
    "scripts/write_obsidian_note.py",
    "scripts/xueba_runtime.py",
    "scripts/prepare_model_eval_workspace.py",
    "scripts/run_evals.py",
    "evals/cases.json",
    "evals/evals.json",
    "evals/trigger-evals.json",
    "evals/assertions.md",
]

REQUIRED_MAIN_HEADINGS = [
    "## 1. 全景",
    "## 2. 概念",
    "## 3. 正文",
    "## 4. 练习",
    "## 5. 来源",
]

REQUIRED_FRONTMATTER_KEYS = ["title", "tags", "source", "created"]
REQUIRED_TAG_PREFIXES = ["status/", "type/", "domain/", "source/", "access/", "confidence/"]
REQUIRED_AI_YAML_KEYS = ["summary:", "concepts:", "relations:", "keywords:", "qa_pairs:"]
CURRENT_VERSION = "2.0.0"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(read_text(path))


def add_result(results: list[dict[str, Any]], name: str, passed: bool, evidence: str = "") -> None:
    results.append({"name": name, "passed": passed, "evidence": evidence})


def validate_required_files(root: Path, results: list[dict[str, Any]]) -> None:
    for relative in REQUIRED_FILES:
        path = root / relative
        add_result(results, f"required file exists: {relative}", path.is_file(), str(path))


def validate_skill_metadata(root: Path, results: list[dict[str, Any]]) -> None:
    text = read_text(root / "SKILL.md")
    frontmatter_match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    add_result(results, "SKILL.md has YAML frontmatter", bool(frontmatter_match))
    if not frontmatter_match:
        return

    frontmatter = frontmatter_match.group(1)
    add_result(results, "skill name remains xueba", re.search(r"^name:\s*xueba\s*$", frontmatter, flags=re.M) is not None)
    description_match = re.search(r"^description:\s*(.+)$", frontmatter, flags=re.M)
    description = description_match.group(1).strip() if description_match else ""
    add_result(results, "description starts with Use when", description.startswith("Use when"), description[:120])
    add_result(results, "frontmatter is under 1024 characters", len(frontmatter) <= 1024, f"{len(frontmatter)} characters")

    for phrase in [
        "xueba v2.0",
        "Learning Expert Mode",
        "Agent Design Mode",
        "Runtime Harness Mode",
        "references/expert-personality.md",
        "references/expert-capabilities.md",
        "references/learning-expert.md",
        "references/quality-gate.md",
        "references/agent-object.md",
        "references/runtime-agent.md",
        "scripts/xueba_runtime.py",
        "local deterministic runtime harness",
        "Safety Checkpoints",
        "CHECKPOINT",
        "Anti-Patterns And Blacklist",
        "Do not perform these actions",
        "Claim the local runtime harness is an autonomous deployed agent",
    ]:
        add_result(results, f"SKILL.md references {phrase}", phrase in text)


def validate_learning_expert_refs(root: Path, results: list[dict[str, Any]]) -> None:
    text = read_text(root / "references/learning-expert.md")
    for phrase in [
        "xueba v1.2",
        "references/expert-personality.md",
        "references/expert-capabilities.md",
        "references/quality-gate.md",
        "Role Override",
        "Capability Precheck",
        "Expert Workflow",
        "Quality Gate",
        "single-expert",
    ]:
        add_result(results, f"learning expert includes {phrase}", phrase in text)

    personality = read_text(root / "references/expert-personality.md")
    capabilities = read_text(root / "references/expert-capabilities.md")
    for phrase in ["学习架构师", "概念建模者", "知识库工程师", "训练教练"]:
        add_result(results, f"personality covers {phrase}", phrase in personality)
    for phrase in ["资料解析专家", "概念建模专家", "学习路径专家", "练习设计专家", "Obsidian 整理专家", "质量审查专家"]:
        add_result(results, f"capabilities cover {phrase}", phrase in capabilities)
    add_result(results, "capabilities define v1.2 completion criteria", "v1.2 Completion Criteria" in capabilities)


def validate_quality_gate(root: Path, results: list[dict[str, Any]]) -> None:
    text = read_text(root / "references/quality-gate.md")
    for phrase in [
        "Universal Gate",
        "Study Note Gate",
        "Obsidian Save Gate",
        "Upgrade Mode Gate",
        "Learning Expert Gate",
        "Agent Design Gate",
        "Local Eval Gate",
        "88-学习/",
        "/tmp",
        "https://github.com/obsidianmd/obsidian-releases",
    ]:
        add_result(results, f"quality gate includes {phrase}", phrase in text)

    template = read_text(root / "references/note-template.md")
    for phrase in ["references/quality-gate.md", "这门知识解决什么问题", "保存结果位于真实 Obsidian vault 的 `88-学习/`"]:
        add_result(results, f"note template includes {phrase}", phrase in template)


def validate_release_docs(root: Path, results: list[dict[str, Any]]) -> None:
    version = read_text(root / "VERSION").strip()
    add_result(results, "VERSION is 2.0.0", version == CURRENT_VERSION, version)

    changelog = read_text(root / "CHANGELOG.md")
    for phrase in [
        "## 2.0.0",
        "Local Runtime Harness",
        "Agent Object Layer",
        "scripts/xueba_runtime.py",
        "not a deployed autonomous agent",
    ]:
        add_result(results, f"CHANGELOG includes {phrase}", phrase in changelog)

    runtime_ops = read_text(root / "docs/runtime-operations.md")
    for phrase in [
        "Runtime Boundary",
        "Initialize",
        "Create a task",
        "Complete a task",
        "Build memory index",
        "Do not claim autonomous execution",
    ]:
        add_result(results, f"runtime operations includes {phrase}", phrase in runtime_ops)

    model_eval = read_text(root / "docs/model-eval-workflow.md")
    for phrase in [
        "Boundary",
        "Prepare workspace",
        "Grade outputs",
        "Generate benchmark and viewer",
        "Release rule",
    ]:
        add_result(results, f"model eval workflow includes {phrase}", phrase in model_eval)

    release = read_text(root / "docs/release-v2.0.md")
    for phrase in [
        "xueba v2.0",
        "Release Boundary",
        "Verification Commands",
        "258 passed, 0 failed",
        "Known Non-Goals",
    ]:
        add_result(results, f"release doc includes {phrase}", phrase in release)

    model_eval_script = read_text(root / "scripts/prepare_model_eval_workspace.py")
    for phrase in [
        "DEFAULT_EVAL_IDS",
        "build_run_prompt",
        "grading.template.json",
        "run_with_codex.sh",
        "generate_viewer.sh",
    ]:
        add_result(results, f"model eval script includes {phrase}", phrase in model_eval_script)


def validate_agent_runtime_refs(root: Path, results: list[dict[str, Any]]) -> None:
    xueba_agent = read_text(root / "references/xueba-agent.md")
    for phrase in [
        "Local Runtime Harness",
        "references/agent-object.md",
        "references/runtime-agent.md",
        "scripts/xueba_runtime.py",
        "not autonomous learning execution",
        "Not deployed by default",
    ]:
        add_result(results, f"xueba-agent includes {phrase}", phrase in xueba_agent)

    agent_object = read_text(root / "references/agent-object.md")
    for phrase in [
        "Task Schemas",
        "study_note",
        "vault_upgrade",
        "review_plan",
        "expert_spec",
        "State Model",
        "Memory Contract",
        "Tool And Permission Contract",
        "Observability Events",
        "v1.3 Quality Gate",
    ]:
        add_result(results, f"agent object includes {phrase}", phrase in agent_object)

    runtime_agent = read_text(root / "references/runtime-agent.md")
    for phrase in [
        "Local Runtime Harness",
        "Task Lifecycle",
        "Runtime Commands",
        "v2.0 Quality Gate",
        ".xueba-runtime",
        "does not mean there is already a deployed daemon",
        "scripts/xueba_runtime.py",
    ]:
        add_result(results, f"runtime agent includes {phrase}", phrase in runtime_agent)

    runtime_script = read_text(root / "scripts/xueba_runtime.py")
    for phrase in [
        "TASK_TYPES",
        "STATUSES",
        "def create_task",
        "def list_tasks",
        "def update_task",
        "def log_event",
        "def memory_index",
        "does not call an LLM",
    ]:
        add_result(results, f"runtime script includes {phrase}", phrase in runtime_script)


def run_runtime_command(script: Path, runtime: Path, *args: str) -> tuple[bool, dict[str, Any], str]:
    command = [sys.executable, str(script), *args, "--runtime", str(runtime)]
    completed = subprocess.run(command, check=False, text=True, capture_output=True)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {}
    ok = completed.returncode == 0 and payload.get("ok") is True
    evidence = completed.stdout.strip() or completed.stderr.strip()
    return ok, payload, evidence[:500]


def validate_runtime_smoke(root: Path, results: list[dict[str, Any]]) -> None:
    script = root / "scripts/xueba_runtime.py"
    with tempfile.TemporaryDirectory(prefix="xueba-runtime-eval-") as temp_dir:
        temp = Path(temp_dir)
        runtime = temp / ".xueba-runtime"
        vault = temp / "vault"
        note_dir = vault / "88-学习" / "AI" / "skills"
        note_dir.mkdir(parents=True)
        (vault / ".obsidian").mkdir()
        (note_dir / "runtime-test.md").write_text(
            """---
title: Runtime Test
tags:
  - status/seed
  - type/system-note
---

# Runtime Test

## AI 读取区
summary: runtime smoke test
concepts:
  - C001
relations: []
keywords: [runtime]
qa_pairs: []
""",
            encoding="utf-8",
        )

        ok, payload, evidence = run_runtime_command(script, runtime, "init")
        add_result(results, "runtime init succeeds", ok, evidence)
        add_result(results, "runtime init creates queued directory", (runtime / "tasks" / "queued").is_dir(), str(runtime))

        task_id = "xueba-eval-runtime-task"
        ok, payload, evidence = run_runtime_command(
            script,
            runtime,
            "create",
            "--task-id",
            task_id,
            "--type",
            "study_note",
            "--title",
            "Runtime smoke",
            "--source-kind",
            "web_url",
            "--source-value",
            "https://example.com/runtime",
        )
        add_result(results, "runtime create succeeds", ok, evidence)
        add_result(results, "runtime create writes queued task", (runtime / "tasks" / "queued" / f"{task_id}.json").is_file(), task_id)

        ok, payload, evidence = run_runtime_command(script, runtime, "list")
        listed_ids = [item.get("task_id") for item in payload.get("tasks", [])] if isinstance(payload.get("tasks"), list) else []
        add_result(results, "runtime list includes created task", ok and task_id in listed_ids, evidence)

        ok, payload, evidence = run_runtime_command(script, runtime, "update", "--task-id", task_id, "--status", "running")
        add_result(results, "runtime update to running succeeds", ok and payload.get("task", {}).get("status") == "running", evidence)
        add_result(results, "runtime update moves task file", (runtime / "tasks" / "running" / f"{task_id}.json").is_file(), task_id)

        ok, payload, evidence = run_runtime_command(
            script,
            runtime,
            "update",
            "--task-id",
            task_id,
            "--status",
            "completed",
            "--quality-gate",
            "passed",
            "--final-path",
            "88-学习/AI/skills/runtime-test.md",
        )
        task = payload.get("task", {})
        add_result(results, "runtime update to completed records quality gate", ok and task.get("quality", {}).get("gate") == "passed", evidence)

        ok, payload, evidence = run_runtime_command(
            script,
            runtime,
            "event",
            "--task-id",
            task_id,
            "--type",
            "quality.checked",
            "--message",
            "quality gate passed",
            "--data",
            '{"gate":"passed"}',
        )
        add_result(results, "runtime event append succeeds", ok, evidence)
        events_text = (runtime / "events.jsonl").read_text(encoding="utf-8")
        add_result(results, "runtime events include quality.checked", "quality.checked" in events_text, events_text[-500:])

        command = [sys.executable, str(script), "memory-index", "--runtime", str(runtime), "--vault", str(vault)]
        completed = subprocess.run(command, check=False, text=True, capture_output=True)
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            payload = {}
        ok = completed.returncode == 0 and payload.get("ok") is True
        add_result(results, "runtime memory-index succeeds", ok, completed.stdout.strip()[:500] or completed.stderr.strip()[:500])
        index = json.loads((runtime / "memory-index.json").read_text(encoding="utf-8"))
        add_result(results, "runtime memory-index finds learning note", index.get("notes") and index["notes"][0].get("relative_path") == "88-学习/AI/skills/runtime-test.md")
        add_result(results, "runtime memory-index extracts concept ID", "C001" in index["notes"][0].get("concept_ids", []) if index.get("notes") else False)


def validate_evals(root: Path, results: list[dict[str, Any]]) -> None:
    data = load_json(root / "evals/evals.json")
    cases = load_json(root / "evals/cases.json")
    add_result(results, "evals/cases.json mirrors evals/evals.json", cases == data)
    add_result(results, "evals skill_name is xueba", data.get("skill_name") == "xueba")
    evals = data.get("evals")
    add_result(results, "evals contains at least 13 cases", isinstance(evals, list) and len(evals) >= 13, f"{len(evals) if isinstance(evals, list) else 'not-list'}")
    if not isinstance(evals, list):
        return

    seen_ids: set[Any] = set()
    for item in evals:
        eval_id = item.get("id")
        add_result(results, f"eval {eval_id} has unique id", eval_id not in seen_ids)
        seen_ids.add(eval_id)
        add_result(results, f"eval {eval_id} has prompt", bool(str(item.get("prompt", "")).strip()))
        add_result(results, f"eval {eval_id} has expected_output", bool(str(item.get("expected_output", "")).strip()))
        expectations = item.get("expectations")
        add_result(
            results,
            f"eval {eval_id} has machine-checkable expectations",
            isinstance(expectations, list) and len(expectations) >= 4 and all(str(value).strip() for value in expectations),
            f"{len(expectations) if isinstance(expectations, list) else 'missing'} expectations",
        )


def validate_trigger_evals(root: Path, results: list[dict[str, Any]]) -> None:
    data = load_json(root / "evals/trigger-evals.json")
    add_result(results, "trigger evals skill_name is xueba", data.get("skill_name") == "xueba")
    should_trigger = data.get("should_trigger")
    should_not_trigger = data.get("should_not_trigger")
    add_result(results, "trigger evals has 10 should_trigger prompts", isinstance(should_trigger, list) and len(should_trigger) >= 10)
    add_result(results, "trigger evals has 10 should_not_trigger prompts", isinstance(should_not_trigger, list) and len(should_not_trigger) >= 10)
    total = (len(should_trigger) if isinstance(should_trigger, list) else 0) + (len(should_not_trigger) if isinstance(should_not_trigger, list) else 0)
    add_result(results, "trigger evals covers at least 20 prompts", total >= 20, f"{total} prompts")

    for group_name, group in [("should_trigger", should_trigger), ("should_not_trigger", should_not_trigger)]:
        if not isinstance(group, list):
            continue
        for index, item in enumerate(group, start=1):
            add_result(results, f"{group_name} {index} has prompt", bool(str(item.get("prompt", "")).strip()))
            add_result(results, f"{group_name} {index} has reason", bool(str(item.get("reason", "")).strip()))


def frontmatter_block(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    return match.group(1) if match else ""


def validate_note(note_path: Path, results: list[dict[str, Any]]) -> None:
    text = read_text(note_path)
    fm = frontmatter_block(text)
    add_result(results, "note has YAML frontmatter", bool(fm))
    for key in REQUIRED_FRONTMATTER_KEYS:
        add_result(results, f"note frontmatter has {key}", re.search(rf"^{re.escape(key)}\s*:", fm, flags=re.M) is not None)
    for prefix in REQUIRED_TAG_PREFIXES:
        add_result(results, f"note frontmatter has {prefix} tag", prefix in fm)

    for heading in REQUIRED_MAIN_HEADINGS:
        add_result(results, f"note has heading {heading}", re.search(rf"^{re.escape(heading)}\s*$", text, flags=re.M) is not None)

    for phrase in ["一句话系统本质", "学习目标", "前置知识", "Why", "What", "How", "Limits", "Evidence", "Links"]:
        add_result(results, f"note contains {phrase}", phrase in text)

    add_result(results, "note uses stable concept ID C001", "C001" in text)
    add_result(results, "note states what problem the knowledge solves", "解决什么问题" in text or "核心问题" in text)
    add_result(results, "note separates source and inference labels", all(label in text for label in ["原文依据", "推论", "待补充", "待验证"]))
    add_result(results, "note includes AI 读取区", "AI 读取区" in text)
    for key in REQUIRED_AI_YAML_KEYS:
        add_result(results, f"AI 读取区 has {key}", key in text)
    add_result(results, "note includes quality checklist", "质量检查" in text)
    add_result(results, "note does not expose temporary paths", "/private/tmp" not in text and "/tmp" not in text)
    add_result(results, "note save target is under 88-学习 when path is present", "88-学习/" in str(note_path) or "88-学习/" in text)


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [item for item in results if not item["passed"]]
    return {
        "ok": not failed,
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "results": results,
    }


def write_report(report: dict[str, Any], report_dir: Path, root: Path, note: str | None) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload = {
        "generated_at": generated_at,
        "root": str(root),
        "note": note,
        **report,
    }
    (report_dir / "summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    failed = [item for item in report["results"] if not item["passed"]]
    lines = [
        "# Xueba Eval Report",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Root: `{root}`",
        f"- Status: `{'PASS' if report['ok'] else 'FAIL'}`",
        f"- Passed: `{report['passed']}`",
        f"- Failed: `{report['failed']}`",
    ]
    if note:
        lines.append(f"- Note: `{note}`")
    lines.extend(["", "## Failed Checks"])
    if failed:
        for item in failed:
            evidence = f" Evidence: {item.get('evidence', '')}" if item.get("evidence") else ""
            lines.append(f"- {item['name']}.{evidence}")
    else:
        lines.append("- None.")

    lines.extend(["", "## Check Inventory"])
    for item in report["results"]:
        marker = "PASS" if item["passed"] else "FAIL"
        evidence = f" - {item.get('evidence', '')}" if item.get("evidence") else ""
        lines.append(f"- `{marker}` {item['name']}{evidence}")
    (report_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic xueba skill checks.")
    parser.add_argument("--root", default=None, help="Skill root. Defaults to the parent of this script directory.")
    parser.add_argument("--note", default=None, help="Optional generated Markdown note to validate.")
    parser.add_argument("--report-dir", default=None, help="Optional directory for summary.json and summary.md reports.")
    parser.add_argument("--json", action="store_true", help="Print full JSON result.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve() if args.root else Path(__file__).resolve().parents[1]
    results: list[dict[str, Any]] = []

    try:
        validate_required_files(root, results)
        validate_skill_metadata(root, results)
        validate_release_docs(root, results)
        validate_learning_expert_refs(root, results)
        validate_quality_gate(root, results)
        validate_agent_runtime_refs(root, results)
        validate_evals(root, results)
        validate_trigger_evals(root, results)
        validate_runtime_smoke(root, results)
        if args.note:
            validate_note(Path(args.note).expanduser().resolve(), results)
    except (OSError, json.JSONDecodeError) as exc:
        add_result(results, "runner completed without parser errors", False, str(exc))

    report = summarize(results)
    if args.report_dir:
        write_report(report, Path(args.report_dir).expanduser().resolve(), root, args.note)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if report["ok"] else "FAIL"
        print(f"{status}: {report['passed']} passed, {report['failed']} failed")
        for item in results:
            marker = "ok" if item["passed"] else "FAIL"
            evidence = f" - {item['evidence']}" if item.get("evidence") else ""
            print(f"[{marker}] {item['name']}{evidence}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
