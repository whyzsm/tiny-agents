# 代码审查专家团

`$tech-code-review` 端到端代码审查工作流入口

## 触发的技能

| 技能 | 能力 |
|---|---|
| `$tech-code-review` | 完整代码审查工作流总入口 |
| `$pr-reviewer` | GitHub PR 或 git diff 接入、变更文件分析、lint 和初始风险判断 |
| `$critical-code-reviewer` | 严格审查 Bug、边界条件、安全漏洞、性能风险和代码质量问题 |
| `$project-code-standard` | 项目编码规范、格式化、命名、导入顺序和团队约定检查 |
| `$security-audit` | 凭证泄露、依赖漏洞、认证授权、配置和部署安全审计 |
| `$clean-code-review` | Clean Code、代码异味、反模式、职责边界和可维护性评估 |
| `$code-review-assistant` | 汇总审查结果并生成结构化中文 Review 报告 |

## 我可以帮你做这些

1. PR 或 diff 接入

   调用 `pr-reviewer`

   获取 GitHub PR、本地 git diff、变更文件、lint 线索、测试覆盖提示和初始风险范围。

2. 严格质量审查

   调用 `critical-code-reviewer`

   检查潜在 Bug、空值/边界情况、错误处理、类型安全、性能问题、可访问性和维护风险。

3. 编码规范检查

   调用 `project-code-standard`

   校验 lint、格式、命名、导入顺序、文件结构和团队代码规范，并输出可执行修复建议。

4. 安全审计

   调用 `security-audit`

   扫描凭证、密钥、依赖漏洞、认证授权、输入校验、配置权限和部署安全风险。

5. Clean Code 评估

   调用 `clean-code-review`

   基于 KISS、DRY、YAGNI、单一职责、代码异味和反模式评估代码可读性与可维护性。

6. 中文审查报告

   调用 `code-review-assistant`

   将多维度发现汇总为中文 Review 报告，按严重等级给出证据、影响和修复建议。

## 完整交付物通常是

```text
PR 或 diff 范围摘要

按严重等级分组的问题清单

安全审计报告

编码规范合规报告

Clean Code 与重构建议

中文代码审查报告和验证说明
```

## 你可以这样用我

```text
$tech-code-review review 这个 PR，重点看安全、错误处理和测试覆盖

$tech-code-review 严格审查最近的 git diff，按阻塞/必须修/建议分类

$tech-code-review 检查这段 TypeScript 有没有潜在 bug、性能问题和类型安全问题

$tech-code-review 输出中文 Review 报告，包含文件位置、风险等级和修复建议
```
