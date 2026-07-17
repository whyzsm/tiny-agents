#!/usr/bin/env python3
"""Local deterministic runtime harness for xueba tasks.

This script manages task records, status transitions, event logs, and a simple
memory-index scaffold. It does not call an LLM and does not execute learning
tasks autonomously.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUSES = ["queued", "running", "blocked", "completed", "failed", "cancelled"]
TASK_TYPES = ["study_note", "vault_upgrade", "review_plan", "expert_spec"]
MODE_BY_TYPE = {
    "study_note": "study",
    "vault_upgrade": "vault_upgrade",
    "review_plan": "study",
    "expert_spec": "learning_expert",
}
DEFAULT_RUNTIME = ".xueba-runtime"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = value.strip("-")
    return value[:48] or "task"


def runtime_root(raw: str | None) -> Path:
    return Path(raw or DEFAULT_RUNTIME).expanduser().resolve()


def task_dirs(root: Path) -> list[Path]:
    return [root / "tasks" / status for status in STATUSES]


def init_runtime(root: Path) -> dict[str, Any]:
    for directory in task_dirs(root):
        directory.mkdir(parents=True, exist_ok=True)
    events = root / "events.jsonl"
    if not events.exists():
        events.write_text("", encoding="utf-8")
    memory_index = root / "memory-index.json"
    if not memory_index.exists():
        memory_index.write_text(json.dumps({"version": 1, "notes": []}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "runtime": str(root)}


def event_path(root: Path) -> Path:
    return root / "events.jsonl"


def append_event(root: Path, task_id: str, event_type: str, message: str = "", data: dict[str, Any] | None = None) -> None:
    init_runtime(root)
    event = {
        "time": now(),
        "task_id": task_id,
        "type": event_type,
        "message": message,
        "data": data or {},
    }
    with event_path(root).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def task_path(root: Path, status: str, task_id: str) -> Path:
    return root / "tasks" / status / f"{task_id}.json"


def find_task(root: Path, task_id: str) -> tuple[Path, dict[str, Any]]:
    for status in STATUSES:
        path = task_path(root, status, task_id)
        if path.exists():
            return path, json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"Task not found: {task_id}")


def save_task(root: Path, task: dict[str, Any]) -> Path:
    status = task["status"]
    path = task_path(root, status, task["task_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def create_task(args: argparse.Namespace) -> dict[str, Any]:
    root = runtime_root(args.runtime)
    init_runtime(root)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    task_type = args.type
    task_id = args.task_id or f"xueba-{timestamp}-{slugify(args.title or task_type)}"
    if task_type not in TASK_TYPES:
        raise ValueError(f"Unsupported task type: {task_type}")
    task = {
        "task_id": task_id,
        "type": task_type,
        "mode": args.mode or MODE_BY_TYPE[task_type],
        "status": "queued",
        "title": args.title or task_type,
        "source": {
            "kind": args.source_kind,
            "value": args.source_value,
            "access": args.source_access,
        },
        "output": {
            "target_root": args.target_root,
            "format": args.output_format,
            "final_paths": [],
        },
        "quality": {
            "gate": "pending",
            "checks": [],
        },
        "created_at": now(),
        "updated_at": now(),
    }
    path = save_task(root, task)
    append_event(root, task_id, "task.created", f"Created {task_type} task", {"path": str(path)})
    return {"ok": True, "runtime": str(root), "task": task, "path": str(path)}


def list_tasks(args: argparse.Namespace) -> dict[str, Any]:
    root = runtime_root(args.runtime)
    init_runtime(root)
    tasks: list[dict[str, Any]] = []
    for status in STATUSES:
        for path in sorted((root / "tasks" / status).glob("*.json")):
            task = json.loads(path.read_text(encoding="utf-8"))
            if args.status and task.get("status") != args.status:
                continue
            tasks.append(
                {
                    "task_id": task.get("task_id"),
                    "type": task.get("type"),
                    "mode": task.get("mode"),
                    "status": task.get("status"),
                    "title": task.get("title"),
                    "updated_at": task.get("updated_at"),
                    "path": str(path),
                }
            )
    return {"ok": True, "runtime": str(root), "tasks": tasks}


def update_task(args: argparse.Namespace) -> dict[str, Any]:
    root = runtime_root(args.runtime)
    init_runtime(root)
    if args.status not in STATUSES:
        raise ValueError(f"Unsupported status: {args.status}")
    old_path, task = find_task(root, args.task_id)
    old_status = task["status"]
    task["status"] = args.status
    task["updated_at"] = now()
    if args.quality_gate:
        task.setdefault("quality", {})["gate"] = args.quality_gate
    if args.final_path:
        task.setdefault("output", {}).setdefault("final_paths", []).append(args.final_path)
    new_path = save_task(root, task)
    if old_path != new_path and old_path.exists():
        old_path.unlink()
    append_event(
        root,
        args.task_id,
        f"task.{args.status}",
        args.message or f"Status changed from {old_status} to {args.status}",
        {"from": old_status, "to": args.status, "path": str(new_path)},
    )
    return {"ok": True, "runtime": str(root), "task": task, "path": str(new_path)}


def log_event(args: argparse.Namespace) -> dict[str, Any]:
    root = runtime_root(args.runtime)
    init_runtime(root)
    data = json.loads(args.data) if args.data else {}
    append_event(root, args.task_id, args.type, args.message or "", data)
    return {"ok": True, "runtime": str(root), "event": {"task_id": args.task_id, "type": args.type, "message": args.message or "", "data": data}}


def extract_frontmatter(text: str) -> dict[str, Any]:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    if not match:
        return {}
    result: dict[str, Any] = {}
    current_key: str | None = None
    for line in match.group(1).splitlines():
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:", line):
            key, value = line.split(":", 1)
            current_key = key.strip()
            result[current_key] = value.strip().strip('"')
        elif current_key and line.strip().startswith("- "):
            result.setdefault(current_key, [])
            if not isinstance(result[current_key], list):
                result[current_key] = []
            result[current_key].append(line.strip()[2:].strip().strip('"'))
    return result


def memory_index(args: argparse.Namespace) -> dict[str, Any]:
    root = runtime_root(args.runtime)
    init_runtime(root)
    vault = Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        raise FileNotFoundError(f"Vault does not exist: {vault}")
    learning_root = vault / "88-学习"
    notes: list[dict[str, Any]] = []
    if learning_root.is_dir():
        for path in sorted(learning_root.rglob("*.md")):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            fm = extract_frontmatter(text)
            notes.append(
                {
                    "path": str(path),
                    "relative_path": str(path.relative_to(vault)),
                    "title": fm.get("title") or path.stem,
                    "tags": fm.get("tags", []),
                    "aliases": fm.get("aliases", []),
                    "has_ai_readable_yaml": "AI 读取区" in text,
                    "concept_ids": sorted(set(re.findall(r"\bC\d{3}\b", text))),
                }
            )
    payload = {
        "version": 1,
        "generated_at": now(),
        "vault": str(vault),
        "learning_root": str(learning_root),
        "notes": notes,
    }
    target = root / "memory-index.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    append_event(root, "runtime", "memory.indexed", f"Indexed {len(notes)} notes", {"vault": str(vault)})
    return {"ok": True, "runtime": str(root), "path": str(target), "note_count": len(notes)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage local xueba runtime task state.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize runtime directories.")
    init_parser.add_argument("--runtime", default=DEFAULT_RUNTIME)

    create_parser = subparsers.add_parser("create", help="Create a queued xueba task.")
    create_parser.add_argument("--runtime", default=DEFAULT_RUNTIME)
    create_parser.add_argument("--task-id", default=None)
    create_parser.add_argument("--type", choices=TASK_TYPES, required=True)
    create_parser.add_argument("--mode", default=None)
    create_parser.add_argument("--title", default="")
    create_parser.add_argument("--source-kind", default="unknown")
    create_parser.add_argument("--source-value", default="")
    create_parser.add_argument("--source-access", default="unknown")
    create_parser.add_argument("--target-root", default="88-学习/")
    create_parser.add_argument("--output-format", choices=["single_note", "asset_package", "report", "spec"], default="single_note")

    list_parser = subparsers.add_parser("list", help="List tasks.")
    list_parser.add_argument("--runtime", default=DEFAULT_RUNTIME)
    list_parser.add_argument("--status", choices=STATUSES, default=None)

    update_parser = subparsers.add_parser("update", help="Update task status and metadata.")
    update_parser.add_argument("--runtime", default=DEFAULT_RUNTIME)
    update_parser.add_argument("--task-id", required=True)
    update_parser.add_argument("--status", choices=STATUSES, required=True)
    update_parser.add_argument("--message", default="")
    update_parser.add_argument("--quality-gate", choices=["pending", "passed", "failed"], default=None)
    update_parser.add_argument("--final-path", default=None)

    event_parser = subparsers.add_parser("event", help="Append an event.")
    event_parser.add_argument("--runtime", default=DEFAULT_RUNTIME)
    event_parser.add_argument("--task-id", required=True)
    event_parser.add_argument("--type", required=True)
    event_parser.add_argument("--message", default="")
    event_parser.add_argument("--data", default="")

    memory_parser = subparsers.add_parser("memory-index", help="Build a memory-index scaffold from an Obsidian vault.")
    memory_parser.add_argument("--runtime", default=DEFAULT_RUNTIME)
    memory_parser.add_argument("--vault", required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "init":
            result = init_runtime(runtime_root(args.runtime))
        elif args.command == "create":
            result = create_task(args)
        elif args.command == "list":
            result = list_tasks(args)
        elif args.command == "update":
            result = update_task(args)
        elif args.command == "event":
            result = log_event(args)
        elif args.command == "memory-index":
            result = memory_index(args)
        else:
            raise ValueError(f"Unsupported command: {args.command}")
    except Exception as exc:  # noqa: BLE001 - command-line tool should return JSON errors.
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
