# 产品战略团队

`$product-strategy-team` 产品战略和产品管理专家团入口。

## 触发的能力

子项模式：`internal-router-labels`。下表中的成员名是 `$product-strategy-team` 内部路由标签，不是可以单独用 `$成员名` 直接调用的顶层 skill。

| 能力 | 适用场景 |
|---|---|
| `$product-strategy-team` | 产品战略专家团工作流总入口 |
| `requirement-analyst` | PRD、功能规格、需求分析、验收标准、范围管理 |
| `user-researcher` | 用户访谈、问卷、可用性测试、工单、NPS 和用户反馈综合 |
| `competitive-analyst` | 竞品研究、功能矩阵、定位分析、市场格局、Battle Card |
| `data-analyst` | 产品指标追踪、KPI 仪表盘、漏斗、留存、异常诊断 |
| `roadmap-planner` | 路线图管理、RICE 优先级、Sprint 规划、利益相关者沟通 |

## 子项映射

| 子项 | 类型 | 映射 | 说明 |
|---|---|---|---|
| `requirement-analyst` | `internal-label` | `$product-strategy-team` 内部路由 | 来自源包需求分析成员，用于 PRD、规格和验收标准。 |
| `user-researcher` | `internal-label` | `$product-strategy-team` 内部路由 | 来自源包用户研究成员，用于访谈、问卷和反馈综合。 |
| `competitive-analyst` | `internal-label` | `$product-strategy-team` 内部路由 | 来自源包竞品分析成员，用于竞品、定位和市场分析。 |
| `data-analyst` | `internal-label` | `$product-strategy-team` 内部路由 | 来自源包数据分析成员，用于产品指标和漏斗诊断。 |
| `roadmap-planner` | `internal-label` | `$product-strategy-team` 内部路由 | 来自源包路线图成员，用于优先级、路线图和 Sprint 规划。 |

## 我可以帮你做这些

1. PRD 和功能规格

   调用 `requirement-analyst`

   输出问题陈述、目标、非目标、目标用户、用户故事、功能需求、验收标准、成功指标、技术和设计考量、里程碑和开放问题。

2. 用户研究综合

   调用 `user-researcher`

   将访谈、问卷、可用性测试、NPS、支持工单、产品评论或行为数据整理为主题、用户分群、证据、洞察、优先级和后续研究建议。

3. 竞品和市场分析

   调用 `competitive-analyst`

   确定分析范围，研究产品页面、定价包装、发布动态、用户评价、招聘信号和社区讨论，输出竞品概览、功能矩阵、定位分析、SWOT 和战略建议。

4. 指标评审和数据洞察

   调用 `data-analyst`

   审查 DAU/WAU/MAU、获取、激活、留存、参与、收入、质量、NPS/CSAT 等指标，识别趋势、分群差异、漏斗流失、异常原因和行动建议。

5. 路线图、优先级和 Sprint 规划

   调用 `roadmap-planner`

   使用 RICE、加权评分、Now/Next/Later 或季度主题规划路线图，拆分 Sprint，标注依赖、风险、容量和 stakeholder 沟通要点。

6. 端到端产品战略交付

   调用 `user-researcher`、`competitive-analyst`、`data-analyst`、`requirement-analyst`、`roadmap-planner`

   先补齐用户、竞品和指标证据，再生成 PRD、优先级、路线图、风险清单和高管/工程/设计沟通稿。

## 标准工作流

### 功能规格书撰写

1. `user-researcher` 综合用户研究和反馈。
2. `competitive-analyst` 调查竞品在该领域的实现。
3. `data-analyst` 整理相关产品指标作为依据。
4. `requirement-analyst` 撰写 PRD 或功能规格。
5. `roadmap-planner` 评估优先级、里程碑和时间线。

### 竞品分析

1. `competitive-analyst` 研究目标竞品、定位、能力、价格和动态。
2. `data-analyst` 补充市场数据、趋势和可量化信号。
3. `user-researcher` 补充用户视角的竞品感知。
4. 汇总为竞品分析报告、功能矩阵、SWOT 和行动建议。

### 路线图规划

1. `data-analyst` 评审当前产品指标表现。
2. `user-researcher` 总结用户反馈和需求趋势。
3. `competitive-analyst` 提供竞品动态和市场方向。
4. `roadmap-planner` 整合为路线图、优先级评分、风险和沟通文档。

### 产品头脑风暴

1. 收集用户需求、业务目标、限制条件和现有假设。
2. 从用户、竞品、数据、需求和路线图五个角度发散方案。
3. 用用户影响、实施难度、差异化和证据强度收敛 Top 2-3 方案。
4. 将最佳想法转为 MVP 概述、关键假设和验证计划。

### 利益相关者更新

1. `data-analyst` 准备关键指标摘要。
2. `roadmap-planner` 更新路线图进度、风险、阻塞和需要的决策。
3. 按高管、工程、设计或客户调整沟通粒度。

## 完整交付物通常是

```text
产品机会、问题空间和假设清单

PRD 或功能规格书

用户研究综合报告

竞品分析简报和功能对比矩阵

产品指标评审和行动建议

RICE / MoSCoW / ICE 优先级评分

Now / Next / Later 或季度路线图

Sprint 计划、依赖和风险清单

高管、工程、设计等分受众沟通稿
```

## 常用输出模板

### PRD / 功能规格

```markdown
# 功能规格: [功能名称]

## 问题陈述
## 目标和非目标
## 目标用户和用户故事
## 方案设计
## 功能需求和验收标准
## 技术考量和设计考量
## 成功指标
## 里程碑
## 开放问题
```

### 竞品分析

```markdown
## 竞品概览
## 功能对比矩阵
## 定位分析
## SWOT
## 差异化机会
## 行动建议
```

### 指标评审

```markdown
## 指标评审: [周期]

| 指标 | 本期 | 上期 | 变化 | 目标 | 状态 |
|---|---:|---:|---:|---:|---|

## 趋势和异常
## 分群或漏斗分析
## 建议行动
```

### 路线图 / Sprint

```markdown
## 路线图更新: [季度/月]

### Now
### Next
### Later
### 优先级评分
### 依赖和风险
### 变更记录
```

## 你可以这样用我

```text
$product-strategy-team 帮我写一份新手引导功能的 PRD，并补齐成功指标和验收标准

$product-strategy-team 对 AI 笔记产品做竞品分析，重点看功能矩阵、定价和差异化机会

$product-strategy-team 根据这些用户访谈和指标，规划下季度产品路线图

$product-strategy-team 帮我把这个产品想法做成 MVP、PRD、路线图和高管汇报稿
```
