# UI Examples

这些示例用于输出方案时快速组织结构，不是固定模板。

## 后台列表页优化输出

```text
方向：Operational Dense
问题诊断：
- 搜索区字段过密，主次不清
- 表格状态色缺少语义区分
- 操作按钮缺少 loading / disabled 态

改进：
- 搜索区按高频字段前置，低频字段收进展开区
- 表格状态使用 success / warning / error 语义色，并保持文字可读
- 批量操作按钮在无选择时 disabled，提交中展示 loading
- 分页、勾选、导出入口保持现有项目写法
```

## Dashboard 优化输出

```text
方向：Data Command
信息层级：
- 第一层：核心 KPI 和异常总数
- 第二层：趋势图和分布图
- 第三层：异常明细和操作入口

视觉建议：
- KPI 使用稳定网格，不做漂浮大卡片
- 预警色只用于异常，不用于普通装饰
- 图表标题说明口径和时间范围
```

## Landing Page 输出

```text
方向：Editorial Landing
首屏：
- 用产品名或明确 offer 做 H1
- 支撑文案说明价值，不把全部信息塞进标题
- 保留下一段内容露出，提示页面可继续阅读

视觉建议：
- 选择一个品牌记忆点，例如真实产品截图、行业场景照片或动态数据画面
- 避免无业务含义的渐变背景和通用插画
```

## 组件重构输出

```text
方向：Trustworthy SaaS
组件状态：
- default
- hover
- focus
- disabled
- loading
- error
- empty

落地建议：
- 保持现有技术栈
- 抽 token，不硬编码散落颜色
- 优先改组件内部状态，不推翻页面结构
```
