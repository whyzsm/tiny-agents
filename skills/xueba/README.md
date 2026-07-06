# xueba

“学霸”是一个面向深度学习、Obsidian TAG 流沉淀和已有知识升级的智能体技能。

## 适用场景

- 给一个网站、论文、PDF、视频转写或粘贴资料，让智能体系统学习。
- 给一个需要登录/授权的飞书、Notion、语雀、钉钉、私有 Wiki 或内部文档，让智能体通过合规授权路径读取后学习。
- 把资料整理成 Obsidian 可长期复用的学习资产。
- 生成 MOC、系统化笔记、原子概念卡、费曼自测、练习题和复习计划。
- 使用轻文件夹、重标签、强检索的 TAG 流知识管理方式。
- 扫描已有 Obsidian vault 或文件夹，找出可升级、可合并、可拆分、可补来源、可优化标签和双链的笔记。

## 两种模式

### 学习模式

用于处理新资料，默认生成一篇完整 Markdown，把一个主题讲清楚。只有用户明确要求概念卡、MOC 或完整知识资产包时，才拆成多文件。

### 升级模式

用于检查已有 Obsidian 知识库，输出知识库升级报告。默认只生成报告，不直接改旧笔记；只有用户明确要求“应用修改”时，才逐篇升级。

## 核心输出

学习模式默认生成一个单文件系统化专题笔记，并保存到 Obsidian 当前真实 vault 下的 `88-学习/`，而不是只放到 Codex 工作区、某台机器的个人目录或生成输出区。

```text
88-学习/[大学科]/[章节或知识要点]/[主题].md
```

写入前应先动态解析 Obsidian 环境：

- 先检查本机是否安装 Obsidian。
- 如果未检测到 Obsidian，直接从官方 GitHub releases 安装：https://github.com/obsidianmd/obsidian-releases
- 再通过 Obsidian 本地配置、`.obsidian` 目录搜索或用户显式路径定位 vault。
- 不写死任何本机绝对 vault 路径。
- 不把 `obsidian://` 深链当作保存目标；保存目标必须是真实 vault 文件夹。
- 只有在已确认 Obsidian 安装且已解析出 vault 名称和文件相对路径后，才动态构造打开链接或使用系统打开器。

解析到 vault 后，统一使用 `88-学习/` 作为学习沉淀根目录：

```text
88-学习/
  AI/
    智能体/
      Agent 与 Agent Harness：核心架构.md
    skills/
      学霸技能设计与评估.md
  管理/
    OKR/
      OKR 与 KPI：目标管理机制.md
  产品/
    PRD/
      高质量 PRD 的结构化写法.md
```

如果 vault 中没有 `88-学习/`，创建它；如果已经存在，直接复用。目录保持简洁直接：`大学科` 放第一层，例如 `AI`、`产品`、`管理`、`技术`、`业务`；章节或知识要点放第二层，例如 `AI/智能体`、`AI/skills`、`AI/RAG`、`产品/PRD`。分类信心不足时，保存到 `88-学习/待分类/`，并用保守标签标记。

单文件内包含：

- 一句话系统本质
- `全景`：核心脉络和 Why / What / How / Limits
- `概念`：核心概念、双链和可拆卡候选
- `正文`：问题、机制、应用、边界、关联
- `练习`：费曼自测、闭卷回忆、迁移任务、复习节奏
- `来源`：来源与可信度、质量检查

可选资产包模式才生成：

```text
学霸/[主题]/
  index.md
  overview.md
  notes.md
  concepts/
  questions/
  exercises/
  review-plan.md
  sources.md
  qa.md
```

升级模式默认生成：

```text
学霸/知识库升级报告/YYYY-MM-DD-知识库升级报告.md
```

## TAG 规范

Frontmatter 中使用受控嵌套标签，不带 `#`：

```yaml
tags:
  - status/seed
  - type/system-note
  - domain/ai/agent
  - source/web
  - access/public
  - confidence/medium
```

## 登录/授权资料处理

遇到飞书、Notion、语雀、钉钉、私有 Wiki、内部文档等需要登录的资料时，“学霸”不应直接放弃，也不能绕过权限。默认按以下顺序处理：

1. 先尝试公开 URL 读取，确认返回的是正文而不是登录页。
2. 如果有官方导出、API、MCP 或 CLI，并且用户已授权，优先导出 Markdown / PDF / DOCX / HTML。
3. 如果有可用的已登录浏览器工具，征得用户许可后只读取页面可见正文，不读取 cookies、localStorage、密码或 token。
4. 如果无法直接授权读取，请用户粘贴正文或提供导出文件。
5. 仍无法取得正文时，生成结构化失败说明，不伪造学习笔记。

访问方式用 `access/*` 标签标记：

```yaml
tags:
  - access/public
  - access/authenticated
  - access/exported
  - access/pasted
  - access/blocked
```

## 质量要求

- 双链只用于长期可复用概念。
- 关键论断必须有来源锚点。
- 原文观点、AI 转述、推理扩展需要区分。
- 练习题必须包含答案或评分标准。
- 复习计划必须有间隔和具体任务。
- 升级已有笔记时必须先报告后修改，避免污染知识库。
- 学习新资料时默认一篇 Markdown 讲清楚，不要过早拆成多个零散文件。
- 默认输出应像一篇完整的“系统化专题”，而不是多个卡片、摘录、问答的拼接。
- 正式学习笔记应进入 Obsidian vault 下的 `88-学习/` 并按内容智能分类；生成输出区只作为草稿、测试或失败报告区。

## 默认单文件模板

默认五段式模板已移到 `references/note-template.md`，作为单文件学习笔记的唯一模板来源。主标题固定保持简洁：`全景`、`概念`、`正文`、`练习`、`来源`。

## 脚本

技能内置 3 个通用脚本，用于减少跨用户路径错误：

```bash
python scripts/resolve_obsidian_vault.py --json
python scripts/install_obsidian.py --json
python scripts/classify_learning_path.py --title "Agent Skills 开放技能标准与工程实践" --domain-tag domain/ai/skills
python scripts/write_obsidian_note.py --vault "/path/to/vault" --relative-dir "88-学习/AI/skills" --filename "Agent Skills：开放技能标准与工程实践.md" --content-file note.md
```

- `resolve_obsidian_vault.py`：只读检测 Obsidian 安装和候选 vault。
- `install_obsidian.py`：未检测到 Obsidian 时，从 `obsidianmd/obsidian-releases` 获取最新安装包并安装。
- `classify_learning_path.py`：输出 `88-学习/[大学科]/[章节]/` 这类简洁相对目录和安全文件名。
- `write_obsidian_note.py`：校验目标 vault、确保路径在 `88-学习/` 下、创建目录、防止默认覆盖同名笔记。

## 测试提示

测试用例保存在 `evals/evals.json`，触发边界保存在 `evals/trigger-evals.json`，断言说明保存在 `evals/assertions.md`。后续可按 `skill-creator` 流程运行评估。
