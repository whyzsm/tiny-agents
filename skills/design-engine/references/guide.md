# 设计引擎团队

`$design-engine` 是设计原型专家团入口，用于把设计想法、品牌资产、产品需求或已有页面推进到可审查、可交付的高保真设计原型。

## 触发的能力

子项模式：`internal-router-labels`。下表中的成员名是 `$design-engine` 内部路由标签，不是可以单独用 `$成员名` 直接调用的顶层 skill。

| 能力 | 适用场景 |
|---|---|
| `$design-engine` | 设计原型专家团总入口 |
| `discovery-analyst` | 需求发现、五维度问卷、设计场景和约束澄清 |
| `design-system-expert` | 71 套设计系统匹配、5 大视觉方向、品牌提取、设计令牌 |
| `prototype-builder` | HTML/CSS 高保真原型、网页、SaaS、仪表盘、移动端、PPT、文档和邮件模板 |
| `critique-reviewer` | 5 维度质量审查、Anti-Slop 检测、P0/P1/P2 门控 |
| `export-specialist` | HTML、PDF、PPTX、ZIP 导出和交付打包 |

## 子项映射

| 子项 | 类型 | 映射 | 说明 |
|---|---|---|---|
| `discovery-analyst` | `internal-label` | `$design-engine` 内部路由 | 来自源包成员 agent，用于需求发现阶段。 |
| `design-system-expert` | `internal-label` | `$design-engine` 内部路由 | 汇总源包设计系统专家和 `skills/design-systems` 能力。 |
| `prototype-builder` | `internal-label` | `$design-engine` 内部路由 | 汇总源包原型构建成员和 `skills/prototype-templates` 能力。 |
| `critique-reviewer` | `internal-label` | `$design-engine` 内部路由 | 汇总源包质量审查成员和 `skills/quality-review` 能力。 |
| `export-specialist` | `internal-label` | `$design-engine` 内部路由 | 来自源包导出交付成员。 |

## 我可以帮你做这些

1. 需求发现

   调用 `discovery-analyst`

   收集五个维度：场景 Surface、受众 Audience、调性 Tone、品牌上下文 Brand Context、规模 Scale。输出结构化设计需求摘要和推荐方向。

2. 设计系统选择

   调用 `design-system-expert`

   从 AI/LLM、开发工具、生产力、金融科技、电商消费、媒体、汽车、通用系统中筛选候选设计系统，并输出色彩、排版、组件、布局、深度、响应式和注意事项。

3. 品牌提取

   调用 `design-system-expert`

   当用户提供官网、品牌手册、截图或现有样式时，执行 Locate、Download、Grep Hex、Codify、Vocalise 五步协议，生成可消费的品牌规范。

4. 原型构建

   调用 `prototype-builder`

   基于设计令牌和模板生成单文件优先的 HTML/CSS 高保真原型。支持 web-prototype、saas-landing、dashboard、mobile-app、simple-deck、pricing-page、docs-page、blog-post、email-template。

5. 质量审查

   调用 `critique-reviewer`

   从设计哲学、视觉层次、执行质量、特异性、克制五个维度评分，并执行 Anti-Slop 检测。P0 必须修复，P1 累计过多需要修正，P2 作为优化建议。

6. 导出交付

   调用 `export-specialist`

   将审查通过的原型导出为独立 HTML、PDF、PPTX 或 ZIP 包，并说明文件路径、大小、打开方式和格式限制。

## 标准工作流

```text
Phase 1 需求发现
  输入：用户想法、产品资料、目标受众、品牌资产、参考风格
  输出：五维度需求摘要

Phase 2 设计系统选择
  输入：需求摘要、品牌资产、参考品牌
  输出：候选系统、设计令牌、DESIGN.md 结构

Phase 3 原型生成
  输入：需求摘要、设计令牌、模板类型、内容素材
  输出：HTML/CSS 高保真原型

Phase 4 质量审查
  输入：原型文件或代码
  输出：5D 评分、P0/P1/P2 问题、修复建议

Phase 5 导出交付
  输入：审查通过的原型、目标格式
  输出：HTML/PDF/PPTX/ZIP 文件和使用说明
```

## 五维度需求摘要

```markdown
## 设计需求摘要

| 维度 | 结论 |
|---|---|
| 场景 | Landing Page / SaaS / Dashboard / Mobile App / Deck / Docs / Pricing / Email |
| 受众 | 目标用户画像、技术素养、审美预期 |
| 调性 | Editorial Monocle / Modern Minimal / Tech Utility / Brutalist / Soft Warm |
| 品牌 | 现有品牌资产、参考网站、截图、品牌手册或全新品牌 |
| 规模 | 单页/多页、单屏/多屏、响应式、交互复杂度 |

### 推荐方向
- 设计系统类型：
- 原型模板：
- 特别注意事项：
```

## DESIGN.md 9 段结构

1. Visual Theme：设计哲学、方向、性格、参考。
2. Color Palette：主色、中性色、语义色，优先提供 HEX 和 CSS 变量。
3. Typography：标题、正文、等宽字体栈和字号层级。
4. Component Styles：按钮、卡片、输入框、导航等组件样式。
5. Layout：容器、栅格、间距体系。
6. Depth & Elevation：阴影、层级和 z-index。
7. Cautions：禁止模式和推荐替代方案。
8. Responsive Behavior：断点和适配规则。
9. Agent Prompt Guide：生成时的关键注意事项和 CSS token 摘要。

## 5 大视觉方向

| 方向 | 适用场景 |
|---|---|
| Editorial Monocle | 品牌故事、杂志感、创意机构、时尚和奢侈品 |
| Modern Minimal | SaaS、开发者工具、效率工具、功能优先页面 |
| Tech Utility | 数据密集、开发者平台、DevOps、深色仪表盘 |
| Brutalist | 创意实验、作品集、潮牌、强记忆点页面 |
| Soft Warm | 消费品、教育、健康、生活方式、社交产品 |

## 原型模板

| 模板 | 用途 |
|---|---|
| `web-prototype` | 通用网页、落地页、产品展示 |
| `saas-landing` | SaaS 产品营销、功能展示、转化优化 |
| `dashboard` | 后台管理、数据分析、运营面板 |
| `mobile-app` | iOS/Android 多屏流程 |
| `simple-deck` | 简洁演示、提案、demo |
| `pricing-page` | 方案对比、特性矩阵、价格页 |
| `docs-page` | 技术文档、帮助中心 |
| `blog-post` | 内容营销、技术博客、长文阅读 |
| `email-template` | 营销邮件和通知邮件 |

## Anti-Slop 质量门

P0 必须修复：
- 紫色或彩虹渐变背景。
- 通用 emoji 作为图标。
- 圆角卡片加左侧彩色边框的模板套路。
- 手绘风 SVG 人物插图。
- 编造统计数据、虚假证言或空洞形容词。
- 破碎布局、文本重叠、对比度不达 WCAG AA、无响应式。

P1 建议修复：
- 展示字体过于平庸、段落过宽、行高不足、层级不清。
- 色彩过多、语义色误用、阴影和圆角堆叠。
- CTA 过多、Hero 过载、hover/focus 缺失、动画无 reduced-motion 降级。

通过标准：
- 五个维度每项评分不低于 3/5。
- P0 数量为 0。
- P1 数量不超过 3。

## 完整交付物通常是

```text
设计需求摘要
设计系统推荐和设计令牌
DESIGN.md 或品牌规范摘要
HTML/CSS 高保真原型
5D 质量审查报告
Anti-Slop 问题清单和修复建议
HTML/PDF/PPTX/ZIP 导出文件
交付说明和剩余风险
```

## 你可以这样用我

```text
$design-engine 用 Stripe 风格设计一个 SaaS 落地页

$design-engine 设计一个移动端新手引导流程，并输出高保真 HTML 原型

$design-engine 帮我审查这个 dashboard 原型，按 Anti-Slop 和 5D 标准打分

$design-engine 从这个品牌官网提取视觉规范，再生成一个定价页原型
```

## 来源说明

原始专家包的 README 提到其设计系统规范、Anti-Slop 机制和质量控制框架部分参考 Open Design 项目（Apache-2.0）。本仓库版本只保留可执行的路由和方法摘要，不复制原始头像、插件安装文件或正式团队运行时。
