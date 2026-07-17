# HarmonyOS 质量评审指南 / HarmonyOS Quality Review Guide

## Source Mapping / 来源映射

The source WorkBuddy card is visible as a team with one lead and three review dimensions. The visible members are generalized here as router-local labels:

| Source capability | Generic HarmonyOS route | Owned output |
|---|---|---|
| Function flow review | `harmony-function-flow-reviewer` | Feature reachability, CRUD, navigation, data and architecture evidence |
| UI visual review | `harmony-ui-visual-reviewer` | Token, layout, component-state, and accessibility evidence |
| Interaction motion review | `harmony-interaction-motion-reviewer` | Hit targets, feedback, transitions, async race, and performance evidence |
| Lead orchestration | `harmony-quality-review-lead` | De-duplicated P0/P1/P2 decision and remediation roadmap |

These labels are internal to the standalone `$harmony-quality-review-team`. They do not imply that standalone child `SKILL.md` files exist or that this team is a child route of `$harmony-expert-team`.

## Routing Table / 路由表

| User request | Route | Execution |
|---|---|---|
| "完整测一下 Harmony 项目" / full project review | All three tracks | Parallel evidence collection, then lead synthesis |
| "只查功能流程" / function-flow only | Function track | Focused report; do not claim UI or interaction coverage |
| "检查 UI 和交互" / UI and interaction | UI + interaction tracks | Parallel two-track report, then synthesis |
| "对比上次质量" / regression review | Relevant tracks plus baseline | Label each finding new, fixed, persistent, or unverifiable |
| "上线前验收" / release readiness | All tracks plus available checks | Separate static findings from build, test, preview, or device evidence |

## Evidence Checklist / 证据清单

### Project Shape / 项目结构

Inspect the files that exist in the target project, typically:

- `module.json5`, `app.json5`, `build-profile.json5`, `hvigorfile.ts`, `oh-package.json5`, and `main_pages.json`.
- `entry/src/main/ets/pages/`, `components/`, `domain/`, `data/`, `media/`, `utils/`, and `theme/` or their project equivalents.
- Tests, fixtures, build scripts, CI configuration, design specifications, and architecture notes.

### Function And Flow / 功能与流程

Use repository-relative searches such as:

```text
delete|Delete|remove|repository|migration|ALTER TABLE|search|index|cleanup|copy|URI|route|Navigation
```

Trace UI event -> domain/repository -> persistence/media/index and verify both the success and failure paths.

### UI And Visual / UI 与视觉

Use the project's token and design files as the baseline, then search for:

```text
#|Color|BackgroundColor|shadow|borderRadius|fontSize|padding|margin|placeholder|accessibility|contentDescription
```

Do not apply a generic palette or spacing rule when the project has an explicit design system. Flag the missing baseline as an assumption.

### Interaction And Motion / 交互与动效

Search for the platform or project equivalents of:

```text
onClick|gesture|onTouch|Loading|isSaving|disabled|transition|animate|bindSheet|LazyForEach|refresh|error|retry
```

Static evidence can show that an animation or state path is declared or missing. It cannot prove timing, frame smoothness, hit testing, or device behavior without runtime verification.

## Severity Rules / 严重级规则

- **P0**: a core workflow is blocked, data can be lost or falsified, or an accessibility or interaction defect prevents normal use.
- **P1**: an important correctness, consistency, architecture, feedback, or performance risk is likely to affect release quality.
- **P2**: a lower-risk visual, motion, robustness, or maintainability problem.

If severity is uncertain, state the uncertainty and explain what evidence would resolve it. Do not inflate a style issue into P0.

## Report Template / 报告模板

```markdown
# HarmonyOS 质量评审报告

## 范围与证据边界
- 项目范围：
- 检查维度：
- 已执行检查：
- 未执行或无法证明：

## 总览
- 功能与流程健康度：
- UI 与视觉健康度：
- 交互与动效健康度：
- 结论：

## P0
| 维度 | 文件:行号 | 证据 | 影响 | 修复建议 |
|---|---|---|---|---|

## P1
| 维度 | 文件:行号 | 证据 | 影响 | 修复建议 |
|---|---|---|---|---|

## P2
| 维度 | 文件:行号 | 证据 | 影响 | 修复建议 |
|---|---|---|---|---|

## 修复路线图
1. <按严重级和依赖排序的第一项>
2. <按严重级和依赖排序的下一项>

## 假设、开放问题与回归检查
- <需要确认的假设、开放问题或回归检查>
```

## Handoff Rules / 交接规则

The lead receives the three track reports, removes duplicates, preserves the strongest file/line evidence, and records which track found each issue. A follow-up implementation must be handed to `$harmony-os-act` with the report and the selected P0/P1/P2 items as input.
