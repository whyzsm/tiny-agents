# Design Tokens

这些 token 是起点，不是强制品牌规范。落地时优先继承当前项目变量、Ant Design token、Tailwind token 或设计系统 token。

## 基础尺寸

```text
space-2: 2px
space-4: 4px
space-8: 8px
space-12: 12px
space-16: 16px
space-20: 20px
space-24: 24px
space-32: 32px
```

默认建议：

- 表单项间距：`12px` 或当前项目标准
- 卡片内边距：`16px / 20px / 24px`
- 表格页上下区块间距：`12px / 16px`
- 工具栏按钮间距：`8px`

## 圆角

```text
radius-sm: 2px
radius-md: 4px
radius-lg: 8px
radius-xl: 12px
```

默认建议：

- 后台表格、表单、弹窗优先 `4px / 6px / 8px`
- 只有营销页、卡片型展示页才考虑更大圆角
- 不要把所有元素都做成大圆角胶囊

## 字体层级

```text
text-xs: 12px
text-sm: 14px
text-md: 16px
text-lg: 18px
title-sm: 20px
title-md: 24px
title-lg: 32px
```

默认建议：

- 后台正文字号优先 `14px`
- 表格数字列保持等宽或右对齐
- 标题字号根据容器大小收敛，不在小卡片里使用 hero 级标题

## 颜色角色

```text
color-primary
color-success
color-warning
color-error
color-info
color-text-primary
color-text-secondary
color-text-disabled
color-border
color-surface
color-background
```

默认建议：

- 主色只用于关键动作、选中态、焦点态
- 状态色必须保持语义一致
- 次要文字不能低到不可读
- 背景色用于分层，不用于制造无业务意义的氛围

## 阴影与边框

```text
shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.06)
shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08)
border-default: 1px solid color-border
```

默认建议：

- 后台页面优先边框和浅分隔
- 阴影只用于浮层、弹窗、悬浮工具条等层级变化
- 不要用多层阴影制造卡片堆叠感

## 动效

```text
motion-fast: 120ms
motion-base: 180ms
motion-slow: 240ms
ease-standard: cubic-bezier(0.2, 0, 0, 1)
```

默认建议：

- loading、hover、展开收起可使用轻动效
- 数据密集页避免大面积入场动画
- 优先使用 `transform` 和 `opacity`
