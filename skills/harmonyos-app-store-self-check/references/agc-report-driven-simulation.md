# AGC 报告驱动模拟

报告驱动模拟用于回答“当前包按这份 AGC 质检报告的结构和规则检查，可能有哪些
问题”。它不是 AGC 真机测试，也不能把历史报告的“通过”复制到当前包。

UX 页签的本地交叉检查使用
`references/huawei-ux-guidelines-v30.md`。官方 UX 标准是风险和证据参考，不会改变
历史 AGC 报告或当前包的 AGC 结果。

当报告范围包含页面体验时，可额外用
`references/huawei-design-concepts-v6.md` 做方向性复核，输出
`DESIGN-ONE`、`DESIGN-HARMONIOUS`、`DESIGN-UNIVERSE`。这些原则不能从历史 AGC
总体结果推导当前包通过，也不能替代当前设备证据。

## 当前 AGC 报告可见模型

报告页通常包含：

- 报告 ID、测试时间、测试时长、应用名称、应用版本、API Level、应用大小；
- 测试结果：`通过`、`不通过` 或 `执行失败`；
- 五个页签：`兼容性`、`稳定性`、`功耗`、`性能`、`UX`；
- 每个页签的测试总项、不通过项、警告项、通过项；
- 问题维度、问题类型、测试项名称、发生次数、影响机型和说明文档；
- 适配设备与本次实际测试设备的覆盖差异。

例如，报告可以显示总体 `通过`，同时有 1 个 UX `警告`，并提示实际设备没有
覆盖应用声明的全部设备类型。模拟器必须同时保留这三个事实，不能将警告抹掉。

## 已读取的 AGC 样本规则

本 Skill 已根据用户提供的四份 AGC 报告页面建立以下样本基线。四份页面可见内容
一致，均显示同一组测试特征：

- 测试结果为 `通过`，没有不通过项，有 1 个警告项；
- 报告汇总显示 105 个用例，页首显示测试设备 2 台，但分析文案按 1 个设备统计；
- 适配设备为直板机、平板、折叠屏，实际测试为直板机/折叠屏，平板覆盖不完整；
- 兼容性页签显示 0 个测试项、0 个不通过、0 个警告、0 个通过，属于缺少有效
  分类数据，不能解释为“兼容性已完成验证”；
- 稳定性页签显示 6 个测试项、0 个不通过、0 个警告、6 个通过；
- 功耗页签显示 7 个测试项、0 个不通过、0 个警告、7 个通过；
- 性能页签显示 5 个测试项、0 个不通过、0 个警告、5 个通过；
- UX 页签显示 43 个测试项、0 个不通过、1 个警告、42 个通过；
- UX 警告为“应用使用的典型手势时长合理”，问题类型为“人机交互”，影响机型
  为 Mate 60 (6.1.0.115)，发生 1 次，并提供“说明文档”入口。该问题可在本地
  交叉映射到官方标准 `2.1.3.2`，但历史警告不能变成当前包的通过。

这些样本用于模拟器的规则表达和证据质量检查，不是 HarmonyOS 官方完整阈值清单。
页面中的汇总用例数与分类用例数可能不相等；模拟器必须报告这种差异，不能把
`0` 分类项、缺失设备或历史报告直接转化为当前包的通过项。

## 规范化输入

浏览器读取 AGC 页面后，将可见内容整理为以下 JSON。缺失字段写成 `null` 或
空数组，不要自行猜测：

```json
{
  "source": "agc-console",
  "report_id": "<report id>",
  "report_url": "<report url>",
  "test_result": "通过",
  "application": {
    "name": "<app name>",
    "bundle_name": "<bundle name>",
    "version_name": "<version name>",
    "version_code": 0,
    "api_level": 0,
    "declared_device_types": ["phone", "tablet"]
  },
  "summary": {
    "total": 0,
    "failed": 0,
    "warnings": 0,
    "passed": 0,
    "tested_devices": [],
    "tested_device_types": [],
    "coverage_complete": false
  },
  "categories": {
    "兼容性": {"total": 0, "failed": 0, "warnings": 0, "passed": 0},
    "稳定性": {"total": 0, "failed": 0, "warnings": 0, "passed": 0},
    "功耗": {"total": 0, "failed": 0, "warnings": 0, "passed": 0},
    "性能": {"total": 0, "failed": 0, "warnings": 0, "passed": 0},
    "UX": {"total": 0, "failed": 0, "warnings": 0, "passed": 0}
  },
  "issues": [
    {
      "dimension": "UX",
      "type": "<issue type>",
      "name": "<test item name>",
      "count": 1,
      "result": "警告",
      "devices": ["<device>"]
    }
  ]
}
```

## 模拟规则

| 模拟项 | 可由本地证据确认 | 必须保持未验证 |
|---|---|---|
| 包身份 | `.app/.hap`、`pack.info`、工程配置与报告的包名/版本对比 | AGC 账号归属和上传记录是否为同一文件，除非页面可核对 |
| 兼容性 | deviceTypes、API、模块入口和包元数据 | 真机机型、系统版本、核心用例通过率 |
| 稳定性 | 工程校验、测试脚本、已提供的运行日志 | AGC 设备上的崩溃、ANR、长时间运行行为 |
| 功耗 | 权限/后台能力的静态风险 | 真实唤醒、耗电和后台行为 |
| 性能 | 包完整性、大小、构建证据；可选的当前包性能证据 JSON 可按 `DELAY-*`、`FPS-*`、`CONTENT-*`、`MEMORY-*`、`CPU-*` 复核 | AGC 设备上的内存曲线、帧率、启动耗时、CPU 峰值和其他设备性能数据 |
| UX | 截图、路由、资源和官方 UX 证据清单 | 真机手势时长、触控体验和设备差异 |

## UX 交叉检查

对报告中的 UX 问题逐项保留以下字段：AGC 问题名称、问题类型、发生次数、影响机型、
报告说明文档和报告 ID。然后在本地报告中增加一个映射字段：

```json
{
  "agc_issue": "应用使用的典型手势时长合理",
  "official_ux_standard": "2.1.3.2",
  "local_evidence_status": "UNVERIFIED",
  "reason": "历史 AGC 设备结果不能证明当前包的手势时长"
}
```

映射只能帮助定位需要复核的官方标准，不能替代当前版本的截图、设备记录或 AGC 实测。

## HMI 交叉检查

当 AGC 的 UX 问题涉及手势、焦点、光标、鼠标、键盘、触控板、拖拽、框选或输入
事件归一时，读取 `references/huawei-hmi-guidelines-v6.md`，并增加本地映射字段：

```json
{
  "agc_issue": "<visible AGC issue>",
  "hmi_standard": "HMI-FOCUS-2",
  "local_evidence_status": "UNVERIFIED",
  "reason": "历史设备结果不能证明当前包在适用输入设备上的行为"
}
```

映射仅用于定位复核范围；没有当前包的输入设备操作记录时，不能生成本地 `PASS`
或 `AGC_READY`。

## 系统特性交叉检查

当 AGC UX 或兼容性问题涉及导航条、通知、实况窗、多窗口、服务卡片、画中画、深色
模式、状态栏或播控中心时，在本地报告中增加 `system_feature` 和
`official_child_document` 字段，并映射到
`references/huawei-system-features-v6.md` 的 `SYS-FEATURE-*` 编号。该编号只是本地
路由标签；具体规则必须回到对应的官方子文档，历史 AGC 结果仍不能复制为当前包通过。

## 元服务交叉检查

当目标包是元服务，或 AGC/报告内容涉及服务卡片、免安装打开、负一屏、元服务胶囊、
静默登录、服务分享或服务状态时，读取 `references/huawei-atomic-service-ux-v4.md`，
并增加本地映射字段：

```json
{
  "atomic_service_check": "ATOMIC-5",
  "official_source": "ux-guidelines-overview-0000001938867005",
  "local_evidence_status": "UNVERIFIED",
  "reason": "历史 AGC 设备结果不能证明当前包的元服务胶囊和服务卡片行为"
}
```

普通应用应记录元服务范围为 `NOT_APPLICABLE`，不能因为报告有 UX 通过项就生成
`ATOMIC_READY`。元服务的发现、无安装打开、分享和系统入口行为必须用当前版本的
设备记录重新验证。

## 性能交叉检查

报告中的 `性能` 页签如果暴露了具体测试项、数值、设备或说明文档，应映射到
`references/huawei-performance-guidelines-v7.md` 的规则 ID。典型映射包括：

- 启动/点击/滑动/折叠/视频起播与 Seek -> `DELAY-1..12`；
- 启动、滑动、转场、视频丢帧/卡顿/音画同步 -> `FPS-1..9`；
- 黑白闪跳、占位符加载、内容完整率 -> `CONTENT-1..3`；
- 后台/前台内存峰值和历史基线 -> `MEMORY-1..3`；
- 后台 CPU 峰值 -> `CPU-1`。

历史报告中的 `通过`、`警告` 和数值只保留为参考证据。除非报告明确对应当前
待测包、设备和测试时间，否则不能复制为当前包的本地 `PASS`；没有当前包测量时
记为 `UNVERIFIED`。

## 状态规则

- `SIMULATED_BLOCKED`：当前工程或包存在本地 P0 阻断项；
- `SIMULATED_UNVERIFIED`：本地没有已知 P0，但至少一个 AGC 动态维度没有
  当前包的真机证据；
- `AGC_READY` 只允许来自 AGC 当前软件包管理页面的“上架自检 = 已达标”，
  模拟器禁止生成这个状态；
- 报告总数与分类总数不一致、报告缺少页签、设备覆盖字段缺失时，增加
  `REPORT-1`/`REPORT-2` 证据问题，不自动修正数据。
