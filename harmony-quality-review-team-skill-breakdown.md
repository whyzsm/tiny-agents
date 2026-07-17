# HarmonyOS Quality Review Team Skill 拆解与写作指南 / Skill Breakdown and Writing Guide

## 结论 / Verdict

### 已观察事实 / Observed facts

The visible WorkBuddy expert card defines one lead and three review dimensions: functionality and flow, UI and visual consistency, and interaction and motion. The lead coordinates parallel review, removes duplicate findings, classifies issues as P0/P1/P2, and returns a unified report. The repository's original `harmony-expert-team` routed only to Q&A, implementation, UI generation, and service-widget capabilities.

可见的 WorkBuddy 专家卡片包含一位主理人和三条审查线：功能与流程、UI 与视觉一致性、交互与动效。主理人负责并行调度、去重、按 P0/P1/P2 分级并返回统一报告。仓库原有的 `harmony-expert-team` 只路由到问答、实现、UI 生成和服务卡片能力。

### 本次改动 / Change made

The WorkBuddy workflow has been generalized into the standalone `harmony-quality-review-team`. Product-specific wardrobe rules and local paths are excluded. It is intentionally separate from `harmony-expert-team`, and its four roles remain internal router labels because no standalone child Skills exist for them.

本次将 WorkBuddy 流程通用化为独立的 `harmony-quality-review-team`。衣橱产品专属规则和本机路径均未进入仓库。它有意不接入 `harmony-expert-team`；由于三条审查线没有独立的 `SKILL.md`，四个角色保留为入口内部标签，不伪装成可单独调用的 Skill。

## 结构拆解 / Structure Breakdown

| Visible artifact | Observed responsibility | Generic repository mapping |
|---|---|---|
| WorkBuddy lead prompt | Dispatches tracks and synthesizes findings | `skills/harmony-quality-review-team/SKILL.md` workflow and output contract |
| Function-flow reviewer | Reviews CRUD, navigation, repositories, persistence, and cleanup | `harmony-function-flow-reviewer` internal label |
| UI-visual reviewer | Reviews tokens, layout, states, and accessibility basics | `harmony-ui-visual-reviewer` internal label |
| Interaction-motion reviewer | Reviews targets, loading, transitions, lists, and races | `harmony-interaction-motion-reviewer` internal label |
| WorkBuddy team card metadata | Human-facing entry and trigger | `agents/openai.yaml` and `source.json` |
| Project-specific background and prompts | Domain assumptions and evidence commands | `references/guide.md`, rewritten for generic HarmonyOS projects |

### Capability boundary / 能力边界

**Observed:** the source is a review and orchestration package, not an implementation package. **Recommendation:** keep review-only behavior in the new Skill and hand approved fixes to `$harmony-os-act`. Static evidence must not be presented as runtime proof.

**已观察：**源专家是评审和编排包，不是实现包。**建议：**新 Skill 保持只评审边界，把确认后的修复交给 `$harmony-os-act`；静态证据不能被表述为运行时证明。

## Skill 写作法 / Skill Writing

### Mapping to the reusable formula / 对应可复用公式

`Skill = Trigger + Boundary + Workflow + Decision Rules + References + Output Contract + Validation`

| Formula part | In this package | Writing lesson |
|---|---|---|
| Trigger | `When To Use` and the frontmatter description mention testing, static review, regression, and release quality | Use natural requests users actually make |
| Boundary | Review-only guardrails, no invented child Skills, no unsupported runtime claims | State side effects and evidence limits explicitly |
| Workflow | Project inspection -> three tracks -> evidence -> de-duplication -> severity -> report | Put discovery, execution, and handoff in a numbered order |
| Decision Rules | Routing and review variants; P0/P1/P2 rules | Express branching as `when` rules and severity definitions |
| References | `references/guide.md` contains source mapping, searches, and a report template | Keep long checklists one level below the entry file |
| Output Contract | Scope, health dimensions, P0/P1/P2 findings, roadmap, assumptions, and limits | Require evidence fields rather than vague conclusions |
| Validation | Evidence completeness, duplicate removal, project checks, and explicit unavailable checks | Define what a trustworthy result looks like |

### What is strong / 写得好的地方

- The trigger surface is concrete and aligned with the actual use case.
- The three dimensions reduce review blind spots without pretending that every reviewer is a separate installable package.
- The lead's de-duplication and severity rules make the output actionable.
- The guardrails preserve repository safety and distinguish static inspection from runtime verification.

这些设计的优点是：触发语句贴近真实请求；三条维度能减少漏检；主理人的去重和严重级规则能把发现转成行动清单；边界明确保护仓库安全，也区分了静态检查和运行时验证。

### Improvement rules / 可继续改进的规则

- Add project-specific references only when the target project provides them; do not bake one application's design system into the generic router.
- If the runtime supports formal team primitives, encode the lead/member handoff there. Otherwise describe coordinated capability execution.
- Add executable project checks only when their commands are discovered from the target project; do not claim a generic Harmony build command.
- Keep the report baseline-aware for regression work so findings can be labeled new, fixed, persistent, or unverifiable.

## Agent 写作法 / Agent Writing

The `agents/openai.yaml` file is intentionally small. It exposes a display name, a concise capability summary, and a default invocation that points to the actual Skill. It does not repeat the workflow or invent a separate persona.

`agents/openai.yaml` 保持短小：只提供展示名、能力摘要和指向真实 Skill 的默认调用，不重复工作流，也不另造人格。

Use this pattern:

```yaml
interface:
  display_name: "Human-facing team name"
  short_description: "One concise capability summary"
  default_prompt: "Use $skill-name to ..."
policy:
  allow_implicit_invocation: true
```

The Skill owns triggers, boundaries, routing, output, and validation. The Agent manifest owns the UI and entry behavior.

Skill 负责触发、边界、路由、产出和验证；Agent manifest 负责 UI 展示和入口调用行为。

## 可复用公式 / Reusable Formula

```text
Skill = Trigger + Boundary + Workflow + Decision Rules + References + Output Contract + Validation
```

中文可记为：

```text
一个好 Skill = 触发条件 + 能力边界 + 执行工作流 + 判断规则 + 分层引用 + 产出契约 + 可观察验证
```

For a review team, a useful additional formula is:

```text
Quality Review Team = Scope Intake + Independent Tracks + Evidence Contract + Lead Synthesis + Severity Gate + Remediation Handoff
```

对于评审专家团，可以再使用：

```text
质量评审专家团 = 范围接收 + 独立审查线 + 证据契约 + 主理人汇编 + 严重级门禁 + 修复交接
```

## 可复用模板 / Reusable Template

```markdown
---
name: example-quality-review-team
description: Use when the user asks to review <platform/project> quality across <dimensions>.
metadata:
  child_entry_mode: internal-router-labels
---

# <Platform> Quality Review Team

## When To Use
- <natural request>

## Internal Review Roles
- `<lead-label>`: <synthesis responsibility>
- `<track-a-label>`: <owned evidence>
- `<track-b-label>`: <owned evidence>

## Workflow
1. Inspect project shape and establish evidence limits.
2. Run independent tracks in parallel when complete coverage is requested.
3. Require file/line, behavior, impact, and fix evidence.
4. De-duplicate findings and classify severity.
5. Return the report and hand approved fixes to the implementation Skill.

## Output Contract
- Scope and verification limits
- Health summary
- Severity-grouped findings
- Remediation roadmap
- Open questions and regression checks

## Guardrails
- Do not edit during review.
- Do not claim unavailable runtime evidence.
- Do not imply internal labels are standalone Skills.

## Validation
- Verify evidence completeness, routing, severity, duplicate removal, and project checks.
```

## 验证结果 / Validation

The implementation is checked with the repository's structural validator, generated indexes, unit tests, diff checks, and the repository's local-path scan. The final handoff should link this Markdown artifact and distinguish completed checks from checks unavailable in the current environment.

本次实现已使用仓库结构校验器、索引生成、单元测试、差异检查和本机路径扫描进行验证。最终交付会链接本 Markdown 文件，并区分已完成的校验和当前环境无法执行的检查。
