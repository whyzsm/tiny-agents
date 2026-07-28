# 华为 HarmonyOS 人机交互指南 / Huawei HarmonyOS HMI Guidelines

## 来源与边界

本文件整理华为开发者官方“人机交互”文档树，作为
`harmonyos-app-store-self-check` 的 HMI 证据参考。概述页面版本为 `V6`，子页面
版本以 `2026-07-28` 读取结果为准。本文是设计和测试参考，不是 AGC 完整审核规则；
需要操作、观察或测量的内容不能由静态代码扫描直接判定通过。

入口：[人机交互概述](https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-overview-0000001795410269)

| 页面 | 版本 | 官方链接 |
|---|---:|---|
| 人机交互概述 | V6 | [hmi-overview](https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-overview-0000001795410269) |
| 手势 | V10 | [hmi-touchscreen](https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-touchscreen-0000001928273206) |
| 光标交互 | V6 | [hmi-cursor](https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-cursor-0000001795531205) |
| 焦点导航 | V9 | [hmi-focus](https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-focus-0000001748650376) |
| 鼠标 | V5 | [hmi-mouse](https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-mouse-0000001930021626) |
| 键盘 | V6 | [hmi-keyboard](https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-keyboard-0000001928070488) |
| 触控板 | V2 | [hmi-touchpad](https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-touchpad-0000002464444730) |
| 常用交互 | V5 | [hmi-scenes](https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-scenes-0000001748650380) |
| 拖拽 | V12 | [hmi-scenes-drag](https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-scenes-drag-0000001795410277) |
| 框选 | V4 | [hmi-scenes-selection](https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-scenes-selection-0000001957005521) |
| 交互事件归一 | V15 | [hmi-interaction-events](https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-interaction-events-0000001795531217) |

## 总体原则

1. 应用应识别当前输入设备，在触屏、手写笔、鼠标、触控板、键盘、遥控器、表冠、
   车机控件、手柄、隔空手势和语音等输入方式下提供符合用户习惯的响应。
2. 根据用户状态提供当前状态下合适的交互方式，保持不同设备和输入方式之间的
   功能一致性；同一功能不应因为输入设备切换而产生冲突或不可发现。
3. 不适用的输入设备或能力必须根据产品范围记录原因；不能把未实现的输入方式
   写成已适配。

## 交互事件归一 / Interaction Event Normalization

以下映射来自官方“交互事件归一”页面。应用有对应能力时，应验证不同输入方式
是否触发同一业务语义和一致反馈。

| 本地 ID | 交互语义 | 触屏/手写笔 | 鼠标/触控板 | 键盘或其他输入 |
|---|---|---|---|---|
| `HMI-EVENT-1` | 悬浮 | 手写笔靠近屏幕 | 光标移动到对象上 | 指向遥控器移动光标 |
| `HMI-EVENT-2` | 点击 | 单指/笔尖单击 | 左键单击；触控板单指轻点/按压 | 焦点上按 Enter/Space；遥控器 OK |
| `HMI-EVENT-3` | 双击 | 单指/笔尖双击 | 左键快速双击；触控板双击 | 焦点上两次 Enter/Space |
| `HMI-EVENT-4` | 长按/上下文 | 单指长按 | 左键长按；右键打开上下文菜单 | 焦点上长按 Enter/Space；Shift+F10 |
| `HMI-EVENT-5` | 拖拽 | 长按并移动 | 左键按下并移动 | 需要明确的焦点/替代操作 |
| `HMI-EVENT-6` | 滚动/平移 | 单指滑动 | 滚轮或 Shift+滚轮 | 不适用时记录原因 |
| `HMI-EVENT-7` | 轻扫 | 单指快速滑动 | 快速滚轮后停止 | 不适用时记录原因 |
| `HMI-EVENT-8` | 缩放 | 双指捏合/张开 | Ctrl+滚轮；触控板双指捏合 | Ctrl+加号/减号 |
| `HMI-EVENT-9` | 旋转 | 双指旋转 | 通常不适用 | 通常不适用 |

## 手势 / Touch Gestures

手势页面的基础能力包括点击、长按、拖拽、滑动、双击、捏合、旋转和指关节敲击。
测试时至少覆盖：

- 点击激活控件，长按提供额外控制或菜单，滑动用于滚动/平移，双击用于放大/缩小，
  捏合用于缩放，旋转用于旋转选中内容；能力不适用时记录产品原因。
- 不新增与系统边缘返回、桌面、多任务、通知中心、控制中心、指关节、三指/四指
  手势冲突的手势。不要通过二次返回手势挽留用户。
- 游戏、视频等场景重点验证误触；隔空手势不能成为唯一交互方式，应提供可替代的
  触屏、按键或其他输入路径。
- 触屏长按、双击的时间参数还要和 UX 标准 `2.1.3.2` 联合检查：长按
  `400-650 ms`，双击间隔 `70-400 ms`。

本地检查 ID：`HMI-TOUCH-1`（基础手势）、`HMI-TOUCH-2`（系统手势冲突）、
`HMI-TOUCH-3`（反馈、误触和替代路径）。这些 ID 是本 Skill 的映射，不是华为
官方编号。

## 光标交互 / Cursor Interaction

- 箭头用于指向、选择和移动滚动条；I 型光标用于文本框；手形用于链接或可点击
  对象；十字准星用于区域选择。
- 张开/并拢的手表示可拖动与正在拖动；调整类光标表示单向或双向调整；滚动光标
  表示可滚动方向；复制、移动和禁止光标应表达当前拖拽结果。
- 悬浮对象应有清晰的悬浮态样式，光标显示必须清晰，不得模糊、拉伸、压缩或锯齿。

本地检查 ID：`HMI-CURSOR-1`（语义样式）、`HMI-CURSOR-2`（悬浮反馈）、
`HMI-CURSOR-3`（清晰度和可辨识性）。

## 焦点导航 / Focus Navigation

- 提供焦点初始位置；焦点可遍历所有可交互控件，并且焦点位置、显示和触发行为
  在需要时保持记忆。
- 对复杂页面配置焦点组；优先按区域快速移动，或定义明确的绝对/相对走焦顺序。
- 可交互控件可获焦，非交互文本、分割器、空白和纯装饰元素不应进入焦点链。
- 键盘/平板常用映射：Tab 下一个、Shift+Tab 上一个、方向键移动、Home/End 到
  区域首尾、Space 激活、Enter 进入、Esc 取消、Shift+F10 打开上下文菜单。
- 电视遥控器、车机旋钮、表冠、方向键/摇杆/手柄要使用符合设备习惯的移动、确认
  和返回操作；不应只在触屏下可用。

本地检查 ID：`HMI-FOCUS-1`（初始焦点）、`HMI-FOCUS-2`（遍历和焦点组）、
`HMI-FOCUS-3`（可交互边界）、`HMI-FOCUS-4`（焦点可见/位置记忆）。

## 鼠标 / Mouse

| 操作 | 预期语义 |
|---|---|
| 移动 | 移动光标，并在元素上显示悬浮态 |
| 悬浮 | 预览更多信息或功能 |
| 左键点击 | 选择或启动主功能 |
| 右键点击 | 打开上下文菜单，对应触屏长按 |
| 滚轮 | 上下或左右滚动页面内容 |
| 左键按下并移动 | 拖拽对象或框选对象 |
| Ctrl+滚轮 | 以光标位置为中心缩放对象 |

本地检查 ID：`HMI-MOUSE-1`（主/次按钮语义）、`HMI-MOUSE-2`（滚轮和缩放）、
`HMI-MOUSE-3`（悬浮和拖拽反馈）。

## 键盘 / Keyboard

- 优先沿用传统电脑的用户习惯；快捷键组合最多 3 个键，常用功能才分配快捷键。
- 不得占用含 Logo 键的系统快捷键；应用自定义快捷键应使用易理解的英文首字母
  组合，并支持行动不便用户一次抬手只按一个键的操作方式。
- 保持焦点导航快捷键：Tab、Shift+Tab、方向键、Home、End、Space、Enter、Esc、
  Shift+F10；编辑和常用功能保持 Ctrl+C/V/X/Z/Y/S/A/F、Delete、Page Up/Down 等
  传统语义。

本地检查 ID：`HMI-KEYBOARD-1`（系统快捷键不冲突）、`HMI-KEYBOARD-2`（焦点导航）、
`HMI-KEYBOARD-3`（编辑和常用快捷键）。

## 触控板 / Touchpad

- 基础手势包括单指移动光标、单击、双击、双指呼出菜单、拖拽、双指轻扫、双指滚动
  /平移、双指捏合缩放和双指旋转。
- 自然滚动时，双指上滑显示页面下方内容，双指下滑显示页面上方内容；离手后应
  根据速度继续减速滚动直到停止。
- 验证系统手势和边缘手势不会被应用手势覆盖：三指上滑回桌面/进入多任务，四指
  横滑切换空间，边缘滑动返回等属于系统行为。

本地检查 ID：`HMI-TOUCHPAD-1`（基础手势）、`HMI-TOUCHPAD-2`（系统/边缘手势）、
`HMI-TOUCHPAD-3`（自然滚动和离手反馈）。

## 拖拽与框选 / Drag And Selection

- 拖拽生命周期为“发起拖拽、拖拽中、释放拖拽”；文本通常先选中，内容对象可长按
  直接选中并发起拖拽，长按浮起应有预览和反馈。
- 区分移动与复制：Ctrl 拖拽可切换为复制；跨窗口通常为复制，但应用要根据业务
  明确处理。原对象、拖拽数量、目标是否接收以及失败/归位结果都要有反馈。
- 支持同应用不同页面、分屏/悬浮窗、跨应用或跨设备的产品场景时，验证拖拽目标
  格式、可见范围、释放后的落点和不可接收时的恢复行为。
- 框选应明确加选、减选、间序选择、连续选择和焦点选择的视觉状态，鼠标框选底板
  不应遮挡或混淆被选内容。

本地检查 ID：`HMI-DRAG-1`（生命周期）、`HMI-DRAG-2`（移动/复制语义）、
`HMI-DRAG-3`（目标接收和失败反馈）、`HMI-SELECT-1`（加减选和视觉状态）。

## 自检证据规则

| 检查类型 | 最低证据 | 不能替代的证据 |
|---|---|---|
| 输入设备适配 | 目标设备上的触屏/鼠标/键盘/触控板操作记录 | 单纯源码存在某个事件回调 |
| 焦点导航 | 键盘、遥控器或旋钮录屏，包含焦点移动路径 | 仅设置 `focusable` 的代码截图 |
| 光标/悬浮 | 当前版本桌面或平板截图/录屏 | 手机触屏截图 |
| 拖拽/框选 | 当前包在目标窗口和设备上的完整操作记录 | 单元测试通过 |
| 事件归一 | 同一功能在两种以上输入方式下的对照记录 | 历史包或另一设备结果 |

没有对应设备、输入方式或功能时，记录 `NOT_APPLICABLE` 和原因；缺少应该执行的
操作证据时记录 `UNVERIFIED`。本地 HMI 通过不等于 AGC `AGC_READY`。
