# xueba

Current version target: **xueba v2.0 - 本地 runtime harness 版**.

This package is a Codex Skill plus Learning Expert Mode, Agent Object Layer, and deterministic local runtime harness. It is not yet a deployed autonomous daemon or cloud service.

“学霸”是一个面向深度学习、Obsidian TAG 流沉淀和已有知识升级的 Codex Skill 技能包。

## 适用场景

- 给一个网站、论文、PDF、视频转写或粘贴资料，让智能体系统学习。
- 给一个需要登录/授权的飞书、Notion、语雀、钉钉、私有 Wiki 或内部文档，让智能体通过合规授权路径读取后学习。
- 把资料整理成 Obsidian 可长期复用的学习资产。
- 生成 MOC、系统化笔记、原子概念卡、费曼自测、练习题和复习计划。
- 使用轻文件夹、重标签、强检索的 TAG 流知识管理方式。
- 扫描已有 Obsidian vault 或文件夹，找出可升级、可合并、可拆分、可补来源、可优化标签和双链的笔记。

## 五种模式

### 学习模式

用于处理新资料，默认生成一篇完整 Markdown，把一个主题讲清楚。只有用户明确要求概念卡、MOC 或完整知识资产包时，才拆成多文件。

### 升级模式

用于检查已有 Obsidian 知识库，输出知识库升级报告。默认只生成报告，不直接改旧笔记；只有用户明确要求“应用修改”时，才逐篇升级。

### 学习专家模式

用于把学霸本身生成或解释为一个产品化学习专家。它包含专家人格、核心使命、能力预检、专家工作流、交付契约、质量门禁和最终交接规则。普通学习任务仍走单专家学习模式，不默认模拟多 Agent 专家团。

v1.2 的专家化产物包括：

- `references/expert-personality.md`：专家人格、口吻、边界和反模式。
- `references/expert-capabilities.md`：资料解析、概念建模、学习路径、练习设计、Obsidian 整理、质量审查 6 个能力模块。
- `references/learning-expert.md`：学习专家执行协议。
- `references/quality-gate.md`：可检查的质量门禁。

### 智能体对象层模式

用于回答或设计“学霸到底是技能还是智能体”。v1.3 已补 Agent 对象层：身份、任务 schema、状态模型、记忆契约、工具权限、事件观测和质量门禁。它仍不等于已部署的独立 Agent。

### 本地运行时模式

v2.0 新增本地 deterministic runtime harness：`scripts/xueba_runtime.py`。它能创建任务记录、维护队列状态、追加事件日志、生成 Obsidian 学习资产的 memory-index 脚手架。它不调用模型、不后台常驻、不绕过权限，也不代表已经有云端部署或自动调度服务。

## 核心输出

学习模式默认生成一个单文件系统化专题笔记，并保存到 Obsidian 当前真实 vault 下的 `88-学习/`，而不是只放到 Codex 工作区、某台机器的个人目录或生成输出区。

```text
88-学习/[大学科]/[章节或知识要点]/[主题].md
```

写入前应先动态解析 Obsidian 环境：

- 先检查本机是否安装 Obsidian。
- 如果未检测到 Obsidian，先说明官方 GitHub releases 来源并请求用户或宿主批准：https://github.com/obsidianmd/obsidian-releases
- 获得批准后再运行安装脚本；未获批准时可以生成草稿，但不能声称已经保存到 Obsidian。
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
- `全景`：学习目标、前置知识、核心脉络和 Why / What / How / Limits
- `概念`：核心概念、概念 ID、别名、关系、双链和可拆卡候选
- `正文`：问题、机制、应用、边界、依据、推论、待补充/待验证和关联
- `练习`：费曼自测、闭卷回忆、迁移任务、复习节奏
- `来源`：来源与可信度、AI 读取区、质量检查

可选资产包模式才生成，并保存到真实 vault 的 `88-学习/` 下：

```text
88-学习/[大学科]/[章节或知识要点]/[主题]/
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
88-学习/工具/Obsidian/知识库升级报告/YYYY-MM-DD-知识库升级报告.md
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
- 原文观点、AI 转述、推理扩展、待补充和待验证内容需要区分。
- 练习题必须包含答案或评分标准。
- 复习计划必须有间隔和具体任务。
- 概念较多时应使用 `C001` 这类稳定 ID，并在 AI 读取区输出关键词、概念关系和问答对。
- 升级已有笔记时必须先报告后修改，避免污染知识库。
- 学习新资料时默认一篇 Markdown 讲清楚，不要过早拆成多个零散文件。
- 默认输出应像一篇完整的“系统化专题”，而不是多个卡片、摘录、问答的拼接。
- 正式学习笔记应进入 Obsidian vault 下的 `88-学习/` 并按内容智能分类；生成输出区只作为草稿、测试或失败报告区。

## 默认单文件模板

默认五段式模板已移到 `references/note-template.md`，作为单文件学习笔记的唯一模板来源。主标题固定保持简洁：`全景`、`概念`、`正文`、`练习`、`来源`。

质量门禁保存在 `references/quality-gate.md`。学习笔记完成前必须检查来源边界、五段结构、概念 ID、练习答案、AI 读取区、真实 vault 保存路径和临时路径泄漏风险。

学习专家模式的产品化专家定义保存在 `references/learning-expert.md`。专家人格保存在 `references/expert-personality.md`，专家能力模块保存在 `references/expert-capabilities.md`。当用户要求“生成学习专家”“学霸专家模式”“学习专家提示词”或“把学习流程产品化成专家”时使用。

智能体对象层定义保存在 `references/xueba-agent.md` 和 `references/agent-object.md`。本地 runtime harness 边界保存在 `references/runtime-agent.md`。当用户问“学霸是技能还是智能体”、要求“智能体化学霸”、设计“Xueba Agent 对象/运行时/长期记忆/任务队列”时使用。

## 脚本

技能内置通用脚本，用于减少跨用户路径错误、提供本地质量检查，并支持本地 runtime harness：

```bash
python3 scripts/resolve_obsidian_vault.py --json
python3 scripts/install_obsidian.py --json
python3 scripts/classify_learning_path.py --title "Agent Skills 开放技能标准与工程实践" --domain-tag domain/ai/skills
python3 scripts/write_obsidian_note.py --vault "/path/to/vault" --relative-dir "88-学习/AI/skills" --filename "Agent Skills：开放技能标准与工程实践.md" --content-file note.md
python3 scripts/run_evals.py
python3 scripts/run_evals.py --report-dir .xueba-eval-report
python3 scripts/run_evals.py --note "/path/to/generated-note.md"
python3 scripts/prepare_model_eval_workspace.py
python3 scripts/xueba_runtime.py init --runtime .xueba-runtime
python3 scripts/xueba_runtime.py create --runtime .xueba-runtime --type study_note --title "Agent memory" --source-kind web_url --source-value https://example.com/agent-memory
python3 scripts/xueba_runtime.py list --runtime .xueba-runtime
```

- `resolve_obsidian_vault.py`：只读检测 Obsidian 安装和候选 vault。
- `install_obsidian.py`：未检测到 Obsidian 且获得批准后，从 `obsidianmd/obsidian-releases` 获取最新安装包并安装。
- `classify_learning_path.py`：输出 `88-学习/[大学科]/[章节]/` 这类简洁相对目录和安全文件名。
- `write_obsidian_note.py`：校验目标 vault、确保路径在 `88-学习/` 下、创建目录、防止默认覆盖同名笔记。
- `run_evals.py`：本地静态检查技能结构、专家引用、质量门禁、eval expectations、20 条触发边界，并可检查生成的单文件笔记或输出发布报告。
- `prepare_model_eval_workspace.py`：生成 skill-creator 兼容的模型输出评估工作区、执行提示、grading 模板和 reviewer 命令，不伪造模型结果。
- `xueba_runtime.py`：本地 deterministic runtime harness，管理任务队列、状态迁移、事件日志和 memory-index 脚手架。

## 测试提示

测试用例保存在 `evals/evals.json`，兼容入口保存在 `evals/cases.json`，触发边界保存在 `evals/trigger-evals.json`，断言说明保存在 `evals/assertions.md`。先运行 `python3 scripts/run_evals.py` 做确定性结构检查；需要模型输出对比时，再按 `skill-creator` 流程运行评估。
