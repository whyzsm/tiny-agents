# Skill Lookup And Install Guide

本文件是本仓库查找、检查、安装和重装 skill 的总入口。仓库内查找时，优先使用本地索引；只有查找仓库外的新 skill 时，才使用 skillhub 或 clawhub。

## 1. 先看哪个索引

普通 skill 查找和安装，从这里开始：

- `indexes/skill-registry.md`
- `indexes/skill-registry.json`

这两个文件只登记本仓库可安装的顶层 skill。判断标准是存在顶层目录：

```text
skills/<name>/SKILL.md
skills/<name>/skill.md
```

需要同时看 agents 和 skills 时，再看：

- `indexes/agent-skill-index.md`
- `indexes/agent-skill-index.json`

需要看专家团入口时，看：

- `indexes/expert-team-file-list.md`: 固定专家团入口
- `indexes/expert-team-skill-index.md`: 专家团路由、转换和 Skill 工作台目录

专家团的“子技能”列不是安装清单。子技能可能是真实顶层 skill，也可能只是 router 内部阶段名、角色名或能力槽位。只有能解析到 `skills/<name>/SKILL.md` 或 `skills/<name>/skill.md` 的名称，才是可单独 `$<name>` 调用和安装的 skill。

## 2. 查找 skill

按关键词查普通 skill：

```bash
rg -n "关键词|keyword" indexes/skill-registry.md
```

按名称查是否存在可安装 skill：

```bash
name="frontend-design"
test -f "skills/$name/SKILL.md" || test -f "skills/$name/skill.md"
```

从 JSON 索引里筛选：

```bash
jq -r '.entries[] | select((.name | test("keyword"; "i")) or (.description | test("keyword"; "i"))) | [.name, .package_path] | @tsv' indexes/skill-registry.json
```

查 agents + skills 总目录：

```bash
rg -n "关键词|keyword" indexes/agent-skill-index.md
```

查专家团入口：

```bash
rg -n "专家团名|skill-name" indexes/expert-team-file-list.md
```

## 3. 检查一个 skill

安装前先读入口文件。安装名以 `skills/<directory>` 的真实目录名为准，不使用展示名或别名。

```bash
name="frontend-design"
entry="skills/$name/SKILL.md"
[ -f "$entry" ] || entry="skills/$name/skill.md"
sed -n '1,220p' "$entry"
```

如果 skill 目录里有这些文件，也要按需检查：

- `references/`: 详细流程、约束、路由说明
- `agents/openai.yaml`: 默认调用提示或 agent 配置
- `scripts/`: 辅助脚本
- `source.json`: 来源、状态和导入元数据
- `_meta.json`: 外部来源或打包元数据

## 4. 安装或重装单个 skill

使用仓库里的原始目录名作为安装名，不做别名映射。安装和重装使用同一条命令；`--delete` 会让已安装目录与仓库版本保持一致。

```bash
name="frontend-design"
target="${CODEX_HOME:-$HOME/.codex}/skills"

test -f "skills/$name/SKILL.md" || test -f "skills/$name/skill.md" || {
  echo "not an installable top-level skill: $name" >&2
  exit 1
}

mkdir -p "$target"
rsync -a --delete "skills/$name/" "$target/$name/"
```

重装时仍然用上面的命令。若你在已安装目录里手动改过文件，`--delete` 可能删除这些本地改动；这种情况先备份或改到仓库内再安装。

## 5. 批量安装 skill

从列表安装：

```bash
target="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$target"

while read -r name; do
  [ -n "$name" ] || continue
  if [ ! -f "skills/$name/SKILL.md" ] && [ ! -f "skills/$name/skill.md" ]; then
    echo "skip non-installable: $name" >&2
    continue
  fi
  rsync -a --delete "skills/$name/" "$target/$name/"
done <<'EOF'
frontend-design
ui-design
accessibility
EOF
```

安装仓库内全部可安装 skill：

```bash
target="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$target"

find skills -mindepth 1 -maxdepth 1 -type d | sort | while read -r path; do
  if [ ! -f "$path/SKILL.md" ] && [ ! -f "$path/skill.md" ]; then
    continue
  fi
  name="$(basename "$path")"
  rsync -a --delete "$path/" "$target/$name/"
done
```

## 6. 专家团怎么用

专家团本身如果有链接到 `skills/<directory>/SKILL.md` 或 `skills/<directory>/skill.md`，它就是一个可安装的顶层 skill。安装方式和普通 skill 相同，安装名用真实目录名 `<directory>`。

专家团子项按三类理解：

- `all-top-level-skills`: 子项全部是真实顶层 skill。
- `hybrid`: 部分子项是真实顶层 skill，部分是内部标签或尚未导入的能力。
- `internal-router-labels`: 子项全部是 router 内部标签、阶段或能力槽位。

不要把 `internal-router-labels` 里的子项当成缺失 skill 逐个安装。真正可安装的是专家团入口本身，以及已经存在于 `skills/<name>/SKILL.md` 或 `skills/<name>/skill.md` 的顶层 skill。

## 7. 导入或改名后刷新索引

扫描外部本机 skill/agent：

```bash
python3 -m tiny_agents scan
```

检查报告里的 `candidate`、`blocked`、`conflict` 和 `ready` 区块，只导入确认过的 ready 项：

```bash
python3 -m tiny_agents import reports/scan-YYYY-MM-DD.json
```

改动 `skills/` 或 `agents/` 后刷新索引：

```bash
python3 scripts/generate_skill_registry.py
python3 scripts/generate_index.py
```

## 8. 仓库外查找

如果本仓库没有需要的 skill，再查外部市场。中文网络优先：

```bash
skillhub search "关键词"
skillhub install <slug>
```

如果 skillhub 不可用或没有结果，再用：

```bash
clawhub search "关键词"
clawhub install <slug>
```

外部安装后，如需纳入本仓库管理，先运行 scan，检查报告，再 import，最后刷新索引。
