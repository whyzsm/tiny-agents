# 提示词模板库（Prompt Templates）

本文件供 `screenshot-ui-prompt` 技能在**阶段 4** 调用。按截图分类（组件 / 区块 / 页面）选用对应
模板，把 `{{占位符}}` 替换为从截图识别出的真实内容，并套用阶段 2（功能）与阶段 3（令牌/风格）的约束。
**功能描述（含异常/控制）必须排在视觉段落之前。**

> 关键原则：**功能先于视觉**——先写「功能描述（含异常/控制）」，再写「风格词」等视觉段落；两者都
> 不可省。只写结构或只写视觉的提示词都是弱的。

---

## §1 组件模板（component）

```
请帮我实现一个「{{组件名称}}」组件（参考 {{相似产品，如飞书多维表格 / Airtable}}）。先确认功能与边界，再定视觉。

【组件定位】
{{组件是什么、内嵌于何处（如表格「筛选」浮层）、受控/非受控立场}}

【功能描述（Functional Spec，必填，含异常与控制）】
- 行为：{{受控/非受控；单/多条件；运算符随字段类型动态变化；校验规则}}
- 运算符-字段类型映射：{{text→包含/开头是…；number→大于/介于…；date→早于/晚于…；select→等于/不等于}}
- 值输入随字段类型切换：{{文本 / 数字 / 日期选择器 / 下拉}}
- 【异常 Exception】必须覆盖：
  - 空数据 / 无匹配结果时的展示与文案
  - 输入非法（格式错、越界、超长）的拦截与提示
  - 请求失败 / 超时 / 并发冲突（race）的处理
  - 权限不足 / 越权访问的降级表现
  - 规则数达上限(maxRules)时禁用「新增」
- 【控制 Control】必须覆盖：
  - 禁用态(disabled) / 加载中(loading) / 只读(read-only) 的视觉与行为
  - 受控 vs 非受控：状态归属与初始值来源
  - 节流防抖(debounce/throttle)：输入与 onChange 频率控制
  - 权限门禁：无权限时隐藏/禁用相关操作
  - 防重复提交 / 最大条数限制 / 焦点与键盘可达(a11y)

【入参 Props（受控，必填）】
interface FieldDef { key: string; label: string; type: 'text'|'number'|'date'|'select'; options?: {label:string;value:string}[] }
interface Rule { id: string; field: string; op: string; value: string }
interface FilterGroup { logic: 'AND'|'OR'; rules: Rule[] }
interface {{ComponentName}}Props {
  fields: FieldDef[]                     // 可选字段元数据
  value: FilterGroup                     // 当前规则组（受控）
  onChange: (next: FilterGroup) => void  // 任何增删改回传不可变新值
  maxRules?: number                      // 规则上限
  disabled?: boolean                     // 禁用态
  loading?: boolean                      // 加载态（父组件下发）
  error?: string                         // 错误态文案（父组件下发）
  onError?: (err: Error) => void         // 错误上报钩子
  onTrack?: (event: string, payload?: Record<string, unknown>) => void  // 埋点
}

【输出 / 事件 Output】
- 唯一出口 onChange(next: FilterGroup)：结构化筛选条件，供父组件发起数据查询
- 原子回调（可合成进 onChange）：onAddRule / onUpdateRule(id) / onRemoveRule(id) / onToggleLogic / onClear
- 组件不主动发请求、不直连 API；异常态由父组件通过 props（error/loading）下发驱动

【数据交互 Data Interaction】
- 父组件持有 value 状态；组件只渲染 + 回传不可变新对象，状态归属清晰
- 切换字段时若原 op 不兼容则重置为该类默认 op（内置 字段类型→运算符 映射表）
- 与表格联动：onChange → 防抖 300ms → queryData(value) → 回填列表（AbortController 取消旧请求，防竞态）
- 空组（rules.length === 0）等价于「不过滤」，父组件返回全量数据

【生产级工程要求（高可用，必填）】
- 【可访问性 a11y】语义化标签（button/input/ul/li）；ARIA：role=dialog/listbox/option、aria-expanded、
  aria-selected、aria-invalid、aria-live 播报错误；键盘：Tab 顺序、Enter/Space 触发、Esc 关闭浮层、
  方向键在列表移动、focus-visible 描边；浮层焦点陷阱+关闭归还焦点；图标按钮 sr-only 文案；
  prefers-reduced-motion 降级动画
- 【全状态与错误边界】六态 idle/loading/success/empty/error/disabled 完整；加载用骨架屏/spinner；
  空态文案+操作入口；错误文案+重试按钮，error 经 props(error) 下发或内部捕获，区分网络/校验/权限码；
  超时与竞态用 AbortController；提供 ErrorBoundary 或要求父包裹，兜底 UI 不白屏，onError 上报钩子
- 【类型与组件 API】严格 TS 零 any，Discriminated Union 表达运算符/值形态；优先 Compound Components
  （<Filter.Rule/> 等）或 Slot/as 组合而非巨型 config；受控/非受控双模（value+onChange 或
  defaultValue+ref），useImperativeHandle 暴露 reset/validate；色值走 CSS 变量支持暗色与换肤
- 【测试 + 性能 + 文档】Vitest + RTL 覆盖渲染/交互/异常态，userEvent 交互，vitest-axe 断言无 a11y 违规；
  大数据虚拟列表，输入/查询防抖 300ms，memo/useMemo/useCallback 阻断重渲染；Storybook 覆盖
  default/loading/empty/error/disabled + Props 表 + 用法示例；i18n 文案不硬编码；SSR 安全（useId、不直访 window/document）；
  关键交互 onTrack(event, payload) 埋点

【风格词（必须显式体现）】
- 风格参考：{{风格参考，见 §风格词库}}
- 主色：{{primary_hex}}
- 背景：{{bg_hex}}，面板/卡片用 {{surface_hex}}
- 强调色：{{accent_hex}}（仅用于关键状态/激活态）
- 质感：{{质感要求，如像素级对齐、1px 细线、≤4px 圆角、无阴影}}
- 字体：{{字体族}}；数字用等宽字体保证列对齐
- 气质：{{气质，如高信息密度低视觉噪音、严谨权威}}
- 体验目标：{{可选 UX 目标，如 3 秒找到最大变动数字}}

【布局 / 结构】
{{组件外壳：白底、描边、圆角、有无阴影；内含区域}}

【组件要素】
- {{控件1}}：默认「{{文案}}」，状态：默认 / hover / 聚焦 / 禁用 / 加载 / 错误
- {{控件2}}：下拉项含 {{选项列表}}
- {{控件3}}：输入占位「{{占位文案}}」
- 「···」更多操作：{{操作项}}

【配色 / 设计令牌】
{{精确 hex：背景 / 表面 / 主色 / 文字 / 分隔 / 强调；含 异常态配色（如错误红）与控制态配色（如禁用灰）}}

【字体 / 排版】
{{字体族、字号、等宽数字}}

【交互（视觉层）】
- {{主要交互，如多条件默认 AND 可切 OR、单条件可删、整组可删、空值不触发}}
- 聚焦态描边变主色

【技术栈】
{{React + TS + Tailwind / 指定 UI 库}}，组件名 {{ComponentName}}，纯函数式 + 受控。
```

---

## §2 区块模板（section）

```
请实现一个「{{区块名称}}」区块（用于 {{页面类型}} 的 {{位置，如顶部工具栏 / 左侧栏}}）。先确认功能与边界，再定视觉。

【组件定位】
{{区块职责、在页面中的位置}}

【功能描述（含异常 / 控制）】
- 行为：{{区块做什么、何时更新}}
- 异常：{{空态 / 加载失败 / 无数据 的展示}}
- 控制：{{禁用 / 加载中 / 只读 / 权限门禁}}

【生产级工程要求（高可用，必填）】
- 【可访问性 a11y】语义化标签与 role；aria-current 标注激活项；键盘可达（Tab/Enter/方向键）；
  focus-visible 描边；屏幕阅读器播报计数变化（aria-live）；prefers-reduced-motion 降级
- 【全状态与错误边界】idle/loading/success/empty/error/disabled 六态；加载骨架；错误重试；
  AbortController 防竞态；区块级 ErrorBoundary 兜底不白屏
- 【类型与组件 API】严格 TS 零 any；受控/非受控双模；复合组件或 as/Slot 组合；主题走 CSS 变量
- 【测试 + 性能 + 文档】Vitest+RTL+axe；memo 阻断重渲染；Storybook 覆盖各态；i18n + SSR 安全

【风格词】
- 风格参考：{{风格参考}}
- 主色 {{primary_hex}}；背景 {{bg_hex}}；分隔线 {{divider_hex}}
- 质感：{{质感}}；字体：{{字体}}；气质：{{气质}}

【结构】
- 区块外壳与栅格：{{列数 / 对齐 / 间距}}
- 内含模块：{{模块A}} | {{模块B}} | {{模块C}}，用 {{分隔方式}} 区分
- 激活态：{{哪个模块激活，如何高亮}}

【要素与状态】
- {{模块}}：{{文案 / 图标 / 计数徽标}}，激活态 {{表现}}，禁用/加载态 {{表现}}
- 响应式：{{窄屏如何处理}}

【交互】
{{hover / 点击 / 展开 / 计数变化等}}

【技术栈】
{{技术栈}}，组件名 {{SectionName}}。
```

---

## §3 页面模板（page）

```
请实现「{{页面名称}}」完整页面（{{产品类型，如金融数据后台 / SaaS 控制台}}）。先确认功能与边界，再定视觉。

【组件定位】
{{页面解决什么问题、主要用户、内嵌/独立形态}}

【功能描述（Functional Spec，必填，含异常与控制）】
- 核心能力：{{页面主要用户动作与流程}}
- 【异常 Exception】必须覆盖：空数据 / 无匹配 / 输入非法 / 请求失败·超时 / 越界·分页越界 / 权限不足 / 并发冲突
- 【控制 Control】必须覆盖：禁用 / 加载中 / 只读 / 受控-非受控 / 节流防抖 / 权限门禁 / 防重复提交 / 最大限制 / 焦点键盘(a11y)

【整体布局】
- 顶栏：{{logo / 导航 / 全局操作}}
- 左/右侧栏：{{导航或筛选}}
- 主区栅格：{{列定义、卡片/表格}}
- 页脚（如有）：{{内容}}

【核心模块】
1. {{模块名}}：{{作用与关键元素}}
2. {{模块名}}：{{表格/图表/列表}}
3. {{筛选/工具条}}：{{参考组件模板}}

【数据契约 / 入参 / 输出】
- 页面入参：{{路由参数 / query 状态 / 全局 store 字段}}
- 数据获取（完整契约）：
  - 请求形状：GET {{/api/resource}}?filter={{FilterGroup}}&page={{n}}&pageSize={{m}}&sort={{field,dir}}
  - 响应形状：{ code: 0|ErrorCode; data: T[]; total: number; page: number; hasMore: boolean }
  - 错误码枚举：{{NetworkTimeout | InvalidParam | Forbidden | NotFound | RateLimited}}
  - 全状态：加载骨架 → 成功渲染 / 空态文案+操作 / 错误文案+重试；分页越界回退首页
  - 竞态：组件卸载或参数变更时用 AbortController 取消在途请求，防旧响应覆盖新状态
- 向上输出事件：{{onSelectRow / onSubmit / onFilterChange}}
- 状态归属：{{服务端为主 / 全局 store / 本地 useState}}，明确页面不直连 API 的边界

【生产级工程要求（高可用，必填）】
- 【可访问性 a11y】landmark 语义（header/nav/main/aside/footer）；跳转链接(skip-link)；
  表格 th scope、列表 ul/li；ARIA：aria-current 导航、aria-selected 选中、aria-live 播报加载/错误/
  计数变化；全键盘可达（Tab/Enter/Esc/方向键）；可见焦点环；图标按钮 sr-only 文案；prefers-reduced-motion
- 【全状态与错误边界】六态完整（idle/loading/success/empty/error/disabled）；路由级 ErrorBoundary
  兜底不白屏；非关键模块失败降级（如日历挂了仍能筛选）；错误上报 onError；AbortController 防竞态
- 【类型与组件 API】严格 TS 零 any；页面拆为受控子组件；复合组件 / Slot 组合；主题 CSS 变量支持暗色；
  命令式句柄（如表格 ref.scrollToRow）按需
- 【测试 + 性能 + 文档】Vitest+RTL 覆盖渲染/交互/异常态，vitest-axe 无违规；大数据虚拟列表
  （react-window）；防抖 300ms、memo 阻断重渲染、代码分割（路由懒加载）；Storybook 覆盖各态 + Props 表；
  i18n（useTranslation）文案不硬编码；SSR 安全（useId、useEffect 内访问 window/document）；关键交互 onTrack 埋点

【风格词】
- 风格参考：{{风格参考}}
- 主色 {{primary_hex}}；背景 {{bg_hex}}；表面 {{surface_hex}}；文字 {{text_hex}}
- 强调色 {{accent_hex}}（涨/跌或关键指标）
- 质感：{{像素级对齐、严格栅格、高密低噪}}
- 字体：{{字体}}；数字等宽 {{等宽字体}}
- 气质：{{严谨、权威、可信赖}}
- 体验目标：{{观看者 3 秒找到最大变动数字；30 秒理解整体结构}}

【配色 / 设计令牌】
{{精确 hex 表：背景 / 表面 / 主色 / 文字 / 分隔 / 强调；含异常态与控制态配色}}

【字体 / 排版】
{{字体族、字号、等宽数字}}

【交互（视觉层）】
- 默认视图与重载；筛选/排序/分组如何联动主区
- 关键数字 hover 高亮 / 对比上期

【技术栈】
{{React + TS + Tailwind / 指定框架}}，路由/状态方案 {{方案}}，组件拆分 {{拆分}}。
```

---

## §风格词库（Style-Word Library）

直接复用下面的「风格词」段落，或让用户自定义。每个都含：参考、主色、背景、质感、气质、体验目标。

### A. 金融终端极简（Goldman Sachs / Bloomberg Terminal）
- 风格参考：高盛企业视觉 + 彭博终端极简主义
- 主色：深蓝 #0A2540（权威、严谨）
- 背景：灰白 #F5F6F8，面板纯白 #FFFFFF，避免纯黑
- 强调色：克制红 #C0392B（跌）/ 绿 #1E8449（涨），仅用于关键数字
- 质感：像素级对齐、严格栅格、1px 细线分隔、圆角 ≤4px、无阴影去装饰
- 字体：Inter / Helvetica Neue；数字等宽 Roboto Mono / SF Mono
- 气质：高信息密度但低视觉噪音，严谨权威可信赖
- 体验目标：观看者 3 秒找到最大变动数字，30 秒理解整体财务表单结构

### B. Apple HIG / 现代简洁
- 风格参考：Apple Human Interface Guidelines
- 主色：系统蓝 #007AFF
- 背景：#FFFFFF / 深色模式 #000000
- 质感：大圆角（10–16px）、充足留白、微妙阴影、清晰层级
- 字体：SF Pro
- 气质：干净、友好、以人为本

### C. Ant Design / 企业后台
- 风格参考：Ant Design 5
- 主色：#1677FF
- 背景：#F5F5F5，容器 #FFFFFF
- 质感：4–8px 圆角、1px #D9D9D9 描边、轻阴影
- 字体：PingFang SC / -apple-system
- 气质：专业、规范、企业级

### D. Linear / 暗色科技
- 风格参考：Linear 暗色风
- 主色：#5E6AD2（靛紫）
- 背景：#0D0E12 / 表面 #1A1B23
- 质感：小圆角、细描边、微弱发光、高对比
- 字体：Inter
- 气质：极客、高效、未来感

> 用户自定义：直接把用户给出的风格描述（含主色 hex、背景、质感、气质、体验目标）填入「风格词」段落。
