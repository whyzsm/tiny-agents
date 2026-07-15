# Repository Agent Guide

This repository collects, organizes, and manages personal AI agents and skills.

本仓库用于收集、整理和管理个人 AI agents 与 skills。

## Working Rules / 工作规则

Treat `skills/` as capability packages, not personas. Skills describe when to use
a capability, how to execute it, and what output it should produce.

将 `skills/` 视为能力包，而不是人格主体。Skill 只描述何时使用、如何执行、产出什么。

Treat `agents/` as role-bearing prompts or manifests. Agents may define identity,
responsibilities, communication style, constraints, and task boundaries.

将 `agents/` 视为带角色的提示词或 manifest。Agent 可以定义身份、职责、沟通风格、约束和任务边界。

Do not commit local absolute paths, secrets, tokens, credentials, runtime caches,
or generated reports intended only for local review.

不要提交本机绝对路径、密钥、token、凭据、运行时缓存，或仅供本地查看的生成报告。

When importing new content, run the scan first, inspect candidate, blocked, and
conflict sections, then import only confirmed ready items.

导入新内容时，先运行扫描，检查 candidate、blocked 和 conflict 区块，再只导入确认过的 ready 项。

For repository skill lookup, use `indexes/skill-registry.md` and
`indexes/skill-registry.json` first. Treat `indexes/agent-skill-index.md` and
`indexes/agent-skill-index.json` as the local scan inventory, and keep
`indexes/skill-team-router-index.md` plus `indexes/expert-team-file-list.md`
as specialized catalogs.

仓库内查找 skill 时，优先使用 `indexes/skill-registry.md` 和
`indexes/skill-registry.json`。将 `indexes/agent-skill-index.md` 和
`indexes/agent-skill-index.json` 视为本地扫描库存，并把
`indexes/skill-team-router-index.md` 与 `indexes/expert-team-file-list.md`
视为专项目录。

## Verification / 验证

Run the unit test suite before committing changes to the CLI or import logic.

修改 CLI 或导入逻辑后，提交前运行单元测试。

```bash
python3 -m unittest
```

Check for accidental local absolute paths before publishing.

发布前检查是否误提交本机绝对路径。

```bash
python3 - <<'PY'
from pathlib import Path

markers = ("/" + "Users/", "/" + "var/folders", "/" + "private/var")
ignored_parts = {"reports", "__pycache__", ".git"}

for path in Path(".").rglob("*"):
    if not path.is_file() or any(part in ignored_parts for part in path.parts):
        continue
    if path.suffix == ".pyc":
        continue
    text = path.read_text(errors="ignore")
    for marker in markers:
        if marker in text:
            print(f"{path}: contains {marker}")
PY
```
