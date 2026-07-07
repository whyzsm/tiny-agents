# 代码重构专家团

`$tech-code-refactoring` 端到端代码重构工作流入口

## 触发的技能

| 技能 | 能力 |
|---|---|
| `$tech-code-refactoring` | 完整代码重构工作流总入口 |
| `$code-analyzer` | 代码结构、执行流程、数据流、DDD 边界、复杂度和重复逻辑分析 |
| `$agent-git-oracle` | Git 历史热点、技术债务、架构反模式和重构优先级识别 |
| `$uncle-bob` | Clean Code、SOLID、Clean Architecture、命名、职责和依赖方向评审 |
| `$code-refactoring` | 重构模式匹配、遗留代码改造策略和分步操作计划 |
| `$system-architect` | 目标架构、模块边界、接口契约、依赖方向和迁移路径设计 |
| `$simplify` | 不改变行为的代码简化、去重、降复杂度和可读性提升 |

## 我可以帮你做这些

1. 代码结构分析

   调用 `code-analyzer`

   梳理模块职责、调用路径、数据流、复杂度热点、重复逻辑和 DDD 限界上下文。

2. 技术债务定位

   调用 `agent-git-oracle`

   结合 git 历史识别高频修改文件、债务累积区域、架构漂移和重构优先级。

3. Clean Code / SOLID 评审

   调用 `uncle-bob`

   检查单一职责、开闭原则、依赖倒置、接口隔离、命名、内聚和耦合问题。

4. 重构方案设计

   调用 `code-refactoring`

   将代码异味匹配到 Extract Method、Move Field、Replace Conditional 等重构模式，并制定可验证步骤。

5. 目标架构设计

   调用 `system-architect`

   规划模块拆分、接口契约、依赖方向、分层关系、迁移路径和架构图。

6. 行为保持式简化

   调用 `simplify`

   在不改变外部行为的前提下简化条件、去除冗余、改善命名和结构，并补充验证说明。

## 完整交付物通常是

```text
代码结构分析报告

技术债务和热点排序

Clean Code / SOLID 合规报告

分步重构操作计划

目标架构和迁移路径

重构补丁、验证命令和风险说明
```

## 你可以这样用我

```text
$tech-code-refactoring 分析这个模块的复杂度和技术债务，给出重构优先级

$tech-code-refactoring 按 SOLID 和 Clean Architecture 评审这批代码并输出重构计划

$tech-code-refactoring 把这个臃肿服务拆成清晰模块，保留现有行为

$tech-code-refactoring 简化最近改动的代码，运行相关测试并说明验证结果
```
