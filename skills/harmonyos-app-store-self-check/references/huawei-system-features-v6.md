# 华为 HarmonyOS 系统特性总览 V6 / Huawei HarmonyOS System Features Overview V6

这份参考来自华为开发者官方设计文档《系统特性》。它是系统能力的导航总览，不是
所有子能力的完整验收规则。实际检查时必须打开适用的子文档，以子文档当前内容、
项目实际能力和设备证据为准。

## 来源 / Source

- 文档：系统特性
- 版本：`V6`
- 官方总览：<https://developer.huawei.com/consumer/cn/doc/design-guides/system-features-0000001826860773>
- 获取日期：`2026-07-28`
- 文档更新时间（官方接口字段）：`2025-06-20 00:31:10`

## 官方子文档 / Official Child Guides

| 本地检查 ID | 官方特性 | 官方子文档 | 适用性判断 | 证据要求 |
|---|---|---|---|---|
| `SYS-FEATURE-1` | 导航条 | <https://developer.huawei.com/consumer/cn/doc/design-guides/navigation-0000001957075737> | 应用使用系统底部导航条、沉浸或底部固定交互时适用 | 手机/折叠屏/平板运行记录和截图 |
| `SYS-FEATURE-2` | 通知 | <https://developer.huawei.com/consumer/cn/doc/design-guides/system-features-notification-0000001793074217> | 应用声明或调用通知能力时适用 | 通知内容、通道、触发频率和设备截图 |
| `SYS-FEATURE-3` | 实况窗 | <https://developer.huawei.com/consumer/cn/doc/design-guides/system-features-live-view-0000001955186861> | 应用实现实况窗或持续任务展示时适用 | 能力配置、任务流程、设备记录 |
| `SYS-FEATURE-4` | 多窗口交互 | <https://developer.huawei.com/consumer/cn/doc/design-guides/system-features-multi-window-interaction-0000001795392917> | 应用支持悬浮窗、分屏或窗口尺寸变化时适用 | 适用设备的窗口/分屏操作和截图 |
| `SYS-FEATURE-5` | 服务卡片 | <https://developer.huawei.com/consumer/cn/doc/design-guides/system-features-service-widget-0000002087671904> | 应用提供服务卡片或桌面卡片时适用 | 卡片配置、布局、刷新和设备截图 |
| `SYS-FEATURE-6` | 画中画 | <https://developer.huawei.com/consumer/cn/doc/design-guides/pip-0000001927422624> | 视频、会议、视频通话或直播应用支持画中画时适用 | 进入/退出画中画的设备记录 |
| `SYS-FEATURE-7` | 深色模式 | <https://developer.huawei.com/consumer/cn/doc/design-guides/dark-mode-0000001823255497> | 应用运行在支持深色模式的设备时检查 | 系统切换前后截图和可读性记录 |
| `SYS-FEATURE-8` | 状态栏 | <https://developer.huawei.com/consumer/cn/doc/design-guides/status-bar-0000001776775568> | 应用使用沉浸式布局或显示状态栏区域时适用 | 不同页面/方向的设备截图 |
| `SYS-FEATURE-9` | 播控中心 | <https://developer.huawei.com/consumer/cn/doc/design-guides/broadcasting-control-0000001957017133> | 应用提供音频、视频或媒体播放控制时适用 | 播放、暂停、切换和系统控制中心记录 |

## 使用规则 / Audit Rules

1. 先从 `module.json5`、Ability/页面代码、权限、服务卡片配置、媒体能力和产品
   listing 判断应用是否使用某项系统特性。未使用的能力记为
   `NOT_APPLICABLE`，并写明判断依据；不能把“没有实现”直接写成发布缺陷。
2. 使用某项能力时，报告必须同时记录：`system_feature`、能力入口/配置、适用设备、
   子文档 URL、当前包版本、证据类型和结果。
3. 仅有 API 调用、配置文件或页面截图只能证明“存在实现/审查材料”，不能证明窗口、
   通知、卡片、画中画、深色模式或系统控制中心在设备上行为正确。
4. 父级总览不提供具体阈值时，不自行补充阈值。子文档、当前设备行为和 AGC UX
   报告优先于本地经验基线。
5. 这些本地 `SYS-FEATURE-*` 编号是 Skill 的映射编号，不是华为官方标准编号；
   不得把它们写成 AGC 测试项或 `AGC_READY` 依据。

## 与 UX 标准的关系 / UX Mapping

| 系统特性 | 关联的官方 UX 标准 | 说明 |
|---|---|---|
| 导航条 | `2.2.1` | UX V30 的底部导航条适配标准；子文档规则更具体时以子文档为准。 |
| 通知 | `2.2.2` | UX V30 的通知内容、通道和模板要求。 |
| 实况窗 | `2.2.3` | UX V30 的实况窗模板要求。 |
| 多窗口交互 | `2.2.4.1`、`2.2.4.2` | 分别关注悬浮窗和分屏；适用设备由产品范围决定。 |
| 画中画 | `2.2.4.3` | 只对视频、会议、通话、直播等适用场景检查。 |
| 深色模式 | `2.2.5` | 检查系统切换后所有界面元素是否可识别。 |
| 状态栏 | `2.2.6` | 检查状态栏与页面的一体化和可读性。 |
| 服务卡片、播控中心 | 暂无对应的 UX V30 编号 | 使用本文件的 `SYS-FEATURE-*` 映射和各自官方子文档，不虚构官方编号。 |
