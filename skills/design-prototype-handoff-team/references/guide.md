# 设计原型专家团

`$design-prototype-handoff-team` 设计原型专家团总入口

## 触发的能力

| 能力模块 | 能力 |
|---|---|
| `design-to-code-workflows` | 将 Figma JSON、UI 截图或自定义布局规格转换为 React/Svelte/Vue 组件 |
| `accessibility-review` | 按 WCAG 2.1 AA 审查色彩对比、键盘导航、触控尺寸、表单标签和屏幕阅读器行为 |
| `design-critique` | 从可用性、视觉层级、一致性和可访问性角度做结构化设计评审 |
| `design-handoff` | 输出布局、设计令牌、组件属性、状态、断点、边界情况和动效交付规格 |
| `design-system` | 审计、文档化或扩展设计系统，包括 tokens、组件、状态和模式 |
| `research-synthesis` | 将访谈、问卷、可用性测试、反馈和 NPS 整理为主题、洞察和建议 |
| `user-research` | 规划访谈、可用性测试、问卷和研究问题，并形成研究计划 |
| `ux-copy` | 编写或评审按钮、错误、空态、确认弹窗、提示和 onboarding 文案 |

## 与已有专家团的边界

| 已有专家团 | 主要覆盖 | 与本团的区别 |
|---|---|---|
| `design-ui-prototype` | 从产品需求到设计系统、线框图和高保真 HTML/Tailwind 原型 | 本团更偏设计输入到工程交付，强调 Figma/截图转组件、handoff、a11y、UX copy 和设计系统治理 |
| `design-interaction-design` | 用户研究、信息架构、交互方案、UX 审计、微交互和无障碍实现 | 本团可做研究和评审，但核心产物是设计交付规格、代码组件和设计系统文档 |
| `design-brand-visual` | 品牌定位、Logo、配色、视觉物料和 SVG 资源 | 本团不负责品牌识别系统，除非品牌规则已经作为设计系统输入提供 |

## 我可以帮你做这些

1. Figma 或截图转代码

   使用 `design-to-code-workflows`

   读取 Figma JSON、截图路径或组件规格，解析布局、色彩、字体和元素结构，生成 React/Svelte/Vue 组件。

2. 无障碍审查

   使用 `accessibility-review`

   检查对比度、语义结构、键盘导航、焦点顺序、触控目标、表单标签和屏幕阅读器行为。

3. 设计质量评审

   使用 `design-critique`

   从第一印象、可用性、视觉层级、一致性和可访问性输出问题表、建议和优先级。

4. 设计交付规格

   使用 `design-handoff`

   生成开发可用的布局规格、设计令牌、组件 props、状态、响应式断点、边界情况和动效说明。

5. 设计系统管理

   使用 `design-system`

   审计 token 覆盖、命名一致性、组件状态和文档完整性，或扩展新的组件/模式。

6. 用户研究和 UX 文案

   使用 `user-research`、`research-synthesis` 和 `ux-copy`

   设计研究计划、综合研究材料，并输出界面微文案、错误提示、空态、CTA 和 onboarding 文案。

## 完整交付物通常是

```text
Figma/截图解析摘要
React/Svelte/Vue 组件代码
设计质量评审报告
WCAG 2.1 AA 无障碍审查报告
开发交付规格
设计系统审计或扩展文档
用户研究综合报告
UX 文案建议
```

## 你可以这样用我

```text
$design-prototype-handoff-team 根据这个 Figma JSON 生成 React 组件，并保留无障碍结构

$design-prototype-handoff-team 审查这张登录页截图，给出设计评审和开发交付规格

$design-prototype-handoff-team 帮我整理这个组件的设计系统文档，包括状态、tokens 和 a11y

$design-prototype-handoff-team 给这个空态和错误提示写三版 UX 文案，并说明适用场景
```
