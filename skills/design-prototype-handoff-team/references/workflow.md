---
scene: "design"
sub_scene: "prototype-handoff"
skills:
  - "design-to-code-workflows"
  - "accessibility-review"
  - "design-critique"
  - "design-handoff"
  - "design-system"
  - "research-synthesis"
  - "user-research"
  - "ux-copy"
source: "workbuddy-cb-teams-marketplace/design-to-code"
---

# 设计原型交付工作流

你现在要完成一项从设计输入到工程交付的任务。本包从 WorkBuddy design-to-code 团队能力转换而来，请按任务范围选择必要步骤，不要机械输出无关文档。

## 步骤 1：确认设计输入（获取层）

使用 **design-to-code-workflows** 完成：
- 判断输入是 Figma JSON、UI 截图、本地图片路径、设计描述还是自定义布局规格
- 确认目标框架：React、Svelte 或 Vue
- 提取或整理布局结构、组件层级、颜色、字体、间距和响应式要求
- 如果输入不足，要求用户补充 Frame/Component JSON、截图路径或关键状态说明

输出设计输入摘要和待生成组件范围。

## 步骤 2：组件生成和可访问基础（输出层）

使用 **design-to-code-workflows** 完成：
- 从 Figma JSON 或截图解析结果生成组件代码
- 默认包含语义化 HTML、ARIA、键盘导航和基础对比度检查
- 根据框架补充 React hooks、Svelte 单文件组件或 Vue Composition API 结构
- 标出生成代码仍需人工补充的业务逻辑、真实样式和复杂交互

输出生产可继续加工的组件代码。

## 步骤 3：设计评审和无障碍审查（分析层）

使用 **design-critique** 和 **accessibility-review** 完成：
- 审查第一印象、可用性、视觉层级、一致性和信息密度
- 检查 WCAG 2.1 AA 相关项：对比度、触控目标、焦点顺序、表单标签、屏幕阅读器行为
- 按 Critical/Major/Minor 或高/中/低给出优先级
- 给出可执行的设计和实现修改建议

输出设计评审报告和无障碍审查报告。

## 步骤 4：开发交付规格（输出层）

使用 **design-handoff** 完成：
- 说明布局、栅格、断点和响应式行为
- 列出设计令牌、组件 props、变体、状态和交互规则
- 补充空态、错误态、加载态、长文本、缺失数据和慢网络等边界情况
- 描述动效触发、持续时间、easing 和可访问性注意事项

输出开发交付规格。

## 步骤 5：设计系统治理（分析层）

使用 **design-system** 完成：
- 检查颜色、字体、间距、圆角、阴影和 motion token 覆盖
- 检查组件命名、状态、变体、文档和迁移风险
- 为新组件或模式补充使用场景、属性、状态、无障碍和代码示例
- 避免硬编码值和一次性样式进入系统组件

输出设计系统审计或扩展文档。

## 步骤 6：研究和文案打磨（分析/输出层）

使用 **user-research**、**research-synthesis** 和 **ux-copy** 完成：
- 规划访谈、可用性测试、问卷或研究问题
- 将研究记录、问卷、工单或 NPS 综合为主题和机会
- 编写或评审按钮、错误提示、空态、确认弹窗、tooltip 和 onboarding 文案
- 给出文案方案、适用场景、语气和本地化注意事项

输出研究计划/综合报告和 UX 文案建议。

## 最终输出

将以上步骤整合为完整设计原型交付包，通常交付：

1. **设计输入摘要**：来源、框架、组件范围、缺失信息
2. **组件代码**：React/Svelte/Vue 组件和可访问基础结构
3. **设计评审报告**：可用性、视觉层级、一致性和优化优先级
4. **无障碍审查报告**：WCAG 2.1 AA 风险和修复建议
5. **开发交付规格**：布局、tokens、props、状态、断点、边界和动效
6. **设计系统文档**：token、组件、模式、状态和治理建议
7. **研究与文案**：研究综合、用户洞察、UX copy 和本地化注意事项
