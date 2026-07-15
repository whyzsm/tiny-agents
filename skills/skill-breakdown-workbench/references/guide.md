# Skill 与 Agent 写作指南 / Skill and Agent Writing Guide

## 核心区别 / Core Distinction

| 组件 / Component | 作用 / Role | 写作重点 / Writing Focus |
|---|---|---|
| Skill | 能力包与工作流 / capability package and workflow | 触发条件、边界、流程、验证 / triggers, boundaries, workflow, validation |
| Agent manifest | UI/调用入口 / entry prompt and config | `display_name`、`short_description`、`default_prompt`、`policy` / UI name, summary, prompt, policy |

## 分析维度 / Analysis Dimensions

### Skill

- `name`：短、清楚、hyphen-case。
- `description`：一句话说清能力和触发场景。
- `Triggers`：写真实自然语言例句，不写抽象标签。
- `Overview`：解释这是什么，不要写人格。
- `Workflow`：按顺序写发现、执行、验证、交付。
- `Guardrails`：说明边界、外部副作用和禁止项。
- `References`：把长知识放到一层引用里。
- `Validation`：说明如何证明结果可靠。

### Agent

- `display_name`：给人看的名字，简短明确。
- `short_description`：一行说明它做什么。
- `default_prompt`：显式调用对应 skill，并保持边界一致。
- `policy`：只写必要策略，不塞进隐藏 persona。

## 怎么写得更好 / How to Write Better

- 写能力，不写人设 / describe capability, not identity.
- 写可触发请求，不写抽象标签 / use natural-language triggers, not labels.
- 写命令式流程，不写散文 / use imperative workflow steps, not prose.
- 写边界，不写模糊承诺 / state boundaries clearly.
- 写验证，不写“应该可以” / make validation observable.
- 写引用，不把长内容塞进主文件 / move long material into references.
- 对齐 Skill 和 Agent 的命名与职责 / keep the Skill and Agent aligned.

## 可复用公式 / Reusable Formula

Use this formula when teaching the user how a Skill is written:

```text
Skill = Trigger + Boundary + Workflow + Decision Rules + References + Output Contract + Validation
```

中文理解：

```text
一个好 Skill =
什么时候触发
+ 能做什么/不能做什么
+ 执行步骤
+ 判断规则
+ 参考资料分层
+ 产出格式
+ 验证方式
```

English version:

```text
A strong Skill =
when to invoke
+ what it can and cannot do
+ execution workflow
+ decision rules
+ layered references
+ output contract
+ validation method
```

### 公式拆解 / Formula Breakdown

| Part | 中文写法 | English Writing Rule |
|---|---|---|
| Trigger | 写用户会真实说出口的触发请求。 | Write real user requests that should invoke the Skill. |
| Boundary | 写清能做什么、不能做什么、哪些动作需要授权。 | Define what it can do, cannot do, and which actions need permission. |
| Workflow | 用编号步骤写发现、执行、验证和交付。 | Use numbered steps for inspect, execute, validate, and deliver. |
| Decision Rules | 把分支判断写成 if/when 规则或表格。 | Express branching as if/when rules or decision tables. |
| References | 把长知识放进一层 `references/`，并说明何时读取。 | Put long knowledge into one-level `references/` files and state when to read them. |
| Output Contract | 固定最终产物的结构、字段和必要证据。 | Fix the structure, fields, and evidence expected in the final output. |
| Validation | 写出可观察的检查命令、测试、审查标准或安全扫描。 | Provide observable checks, tests, review criteria, or safety scans. |

### 一句话原则 / One-Sentence Principle

```text
不要写“我是一个专家”，要写“遇到什么问题时，按什么步骤，读取哪些资料，产出什么结果，并用什么标准验证”。
```

```text
Do not write "I am an expert." Write "When this problem appears, follow these steps, read these references, produce this output, and validate it by these standards."
```

## 可复用回答模板 / Reusable Answer Template

1. 它是做什么的 / What it does.
2. 它是怎么写的 / How it is written.
3. 哪些地方写得好 / What is already strong.
4. 哪些地方可以改 / What to improve.
5. 可复用公式 / A reusable formula.
6. 一个可复用骨架 / A reusable skeleton.

## Markdown 文件输出契约 / Markdown Artifact Contract

Every teardown, writing lesson, formula explanation, or rewrite proposal must be written to a Markdown file before the final response. 每次 Skill 拆解、写作教学、公式说明或改进方案，都必须先写入 Markdown 文件，再发送最终回复。

### 默认文件 / Default File

- If the user provides an output path, use that path only when it ends with `.md`. 用户提供输出路径时，仅在路径以 `.md` 结尾时使用。
- Otherwise create `<target-name>-skill-breakdown.md` in the current workspace. 未提供路径时，在当前工作区生成 `<target-name>-skill-breakdown.md`。
- Normalize `<target-name>` to lowercase kebab-case and avoid local absolute paths in the document body. 将 `<target-name>` 规范化为小写 kebab-case，并避免在文件正文写入本机绝对路径。
- Return the generated file as a clickable local file link. 在最终回复中返回可点击的本地文件链接。

### 必需章节 / Required Sections

```markdown
# <Target> Skill 拆解与写作指南 / Skill Breakdown and Writing Guide

## 结论 / Verdict
## 结构拆解 / Structure Breakdown
## Skill 写作法 / Skill Writing
## Agent 写作法 / Agent Writing
## 可复用公式 / Reusable Formula
## 可复用模板 / Reusable Template
## 验证结果 / Validation
```

The document must separate observed facts, recommendations, and assumptions. 文件必须区分已观察事实、改进建议和假设，不得把推测写成事实。

### 交付前校验 / Handoff Checks

1. The path ends in `.md` and the file exists. 路径以 `.md` 结尾且文件存在。
2. The file contains all required bilingual headings. 文件包含全部必需的双语标题。
3. Claims point to visible source files or are explicitly labeled as recommendations. 结论能指向可见源文件，或明确标记为建议。
4. The final response links to the artifact and briefly summarizes its contents. 最终回复链接到文件，并简要说明文件内容。

## 常见错误 / Common Mistakes

- 把 Skill 写成角色扮演 / turning a Skill into role-play.
- 把 Agent 写成另一个 Skill / turning the Agent into a duplicate Skill.
- 忽略验证和副作用 / omitting validation and side effects.
- 默认假设隐藏 prompt / assuming hidden prompts or private files.
- 中英文不对齐 / letting the Chinese and English sections drift apart.

## 推荐输出顺序 / Recommended Output Order

1. 结论 / Verdict
2. 结构拆解 / Structure Breakdown
3. Skill 写作建议 / Skill Writing Advice
4. Agent 写作建议 / Agent Writing Advice
5. 可复用公式 / Reusable Formula
6. 可直接复用模板 / Reusable Template

## 通用 SKILL.md 格式 / Reusable SKILL.md Format

### Skill / SKILL.md

```markdown
---
name: example-skill
description: "Do X. Use when the user needs ..., asks for ..., or provides ..., especially when ..."
---

# Title

## Purpose
Explain what capability this Skill provides and what outcome it should produce.

## When to Use
- Use when ...
- Use when ...
- Do not use when ...

## Triggers
- "Natural-language request example"
- "Another realistic user request"

## Workflow
1. Identify the user's goal and input.
2. Read the required reference file.
3. Choose the right path based on decision rules.
4. Produce the output in the required format.
5. Validate the result before delivery.

## Decision Rules
- If the task is simple, use ...
- If the task is complex, read ...
- If implementation is requested, ...
- If review is requested, ...

## References
- `references/guide.md`: main routing guide
- `references/checklist.md`: validation checklist
- `references/patterns.md`: reusable patterns

## Output Contract
When answering, include:
1. ...
2. ...
3. ...

## Guardrails
- ...

## Validation
- ...
```

## Agent Manifest 公式 / Agent Formula

```text
Agent = Display Identity + Short Capability + Default Invocation + Policy
```

### Agent manifest / agents/openai.yaml

```yaml
interface:
  display_name: "Example Skill"
  short_description: "One-line summary"
  default_prompt: "Use $example-skill to ..."
policy:
  allow_implicit_invocation: true
```

## 套公式示例 / Formula Mapping Example

When analyzing a target Skill, map visible files into this shape:

```text
Trigger:
What user requests or frontmatter description activate the Skill?

Boundary:
What does the Skill explicitly allow, forbid, or require permission for?

Workflow:
What ordered steps does it require?

Decision Rules:
What if/when branches, matrices, checklists, or routing rules does it use?

References:
Which reference files are loaded, and under what conditions?

Output Contract:
What final structure or artifacts must the Skill produce?

Validation:
How does it check correctness, safety, or completeness?
```
