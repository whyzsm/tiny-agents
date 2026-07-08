# 工程保障团队

`$tech-engineering-assurance-team` 工程保障团队总入口

## 来源说明

- WorkBuddy 分类：技术工程
- WorkBuddy 卡片：工程保障团队
- 作者/来源：Expert Marketplace
- 卡片摘要：由工程总监领导的5人工程专家团队：代码审查师（安全/性能/正确性）、架构师（系统设计/ADR）、SRE 工程师等协作保障交付。
- 标签：工程保障、代码审查、架构评审
- 提取状态：截图卡片可见团队名、作者、摘要和标签；本地 WorkBuddy marketplace 包未包含完整专家详情 payload。

## 触发的能力

| 能力模块 | 能力 |
|---|---|
| `engineering-director` | 工程目标、风险分级、资源约束和质量闸口 |
| `code-reviewer` | 正确性、安全、性能、可维护性和可测试性审查 |
| `architecture-adr` | 系统设计、架构权衡、ADR 和演进风险 |
| `sre-readiness` | 可观测性、容量、告警、发布、回滚和应急预案 |
| `quality-gate` | 测试覆盖、验收证据、缺陷关闭和发布准入 |
| `release-risk` | 发布风险、依赖、变更影响和回滚策略 |

## 与已有专家团的边界

| 已有专家团 | 主要关系 |
|---|---|
| `tech-code-review` | 负责代码审查专项；本团还覆盖架构 ADR、SRE 和发布准入。 |
| `tech-bug-troubleshooting` | 负责已发生问题的定位修复；本团偏上线前保障和风险预防。 |
| `tech-test-automation` | 负责测试建设；本团把测试证据纳入整体工程质量门禁。 |

## 我可以帮你做这些

1. 工程保障评估

   建立质量目标、风险等级、变更影响和发布准入标准。

2. 代码/架构评审

   同时审查正确性、安全、性能、可维护性、系统设计和 ADR。

3. SRE 准备

   检查日志、指标、告警、容量、降级、回滚和应急流程。

4. 质量闸口

   整理测试证据、缺陷状态、验收结果和发布阻塞项。

5. 发布风险控制

   输出 go/no-go 建议、风险清单、负责人和后续跟踪。

## 完整交付物通常是

```text
工程保障评分
代码审查表
架构 ADR 建议
SRE 准备清单
发布 go/no-go 建议
风险与责任人
```

## 你可以这样用我

```text
$tech-engineering-assurance-team 帮我做上线前工程保障评审
$tech-engineering-assurance-team 从代码、架构、SRE 和发布风险审查这个 PR
```
