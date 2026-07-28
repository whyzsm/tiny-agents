# 华为 HarmonyOS 应用性能体验建议 / Huawei HarmonyOS Performance Experience Guidelines

## 来源与边界

本文件是华为开发者文档中心在 `2026-07-28` 读取到的官方页面快照，用作
`harmonyos-app-store-self-check` 的性能证据基线。页面当前显示版本均为 `V7`。
它不是 AGC 完整审核规则清单，也不替代当前 AGC 报告、设备测试或华为页面的
最新版本。正式发布前，如果页面版本发生变化，应重新读取官方页面并更新本文件。

官方入口和页面：

- [应用性能体验建议概述](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/performance-overview-V5)
- [时延](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/performance-delay-V5)
- [帧率](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/performance-frame-rate-V5)
- [内容显示](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/performance-content-display-V5)
- [内存占用](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/performance-memory-usage-V5)
- [CPU 占用](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/performance-cpu-usage-V5)

## 概述与适用范围

华为文档说明，这些建议用于优化 HarmonyOS NEXT 应用性能、寻找应用设计改进点，
适用于应用和元服务的设计、开发及测试。它们是体验性能基线，不代表每个应用都要
执行视频、折叠或 2in1 场景；审计时必须按真实功能和目标设备裁剪规则。

官方页面的“规则”与“建议”必须分开记录：规则不达标是发布前的 P1 性能问题；
建议不达标通常是 P2 优化项，除非它同时造成核心流程不可用。所有数值都必须带
设备、系统/API、包版本、场景、统计方式和可复核证据。

## 证据等级

| 证据 | 可以确认 | 不能确认 |
|---|---|---|
| 设备性能追踪或 AGC 报告 | 该设备、该包、该场景的一次或一组实际测量 | 其他设备、其他包版本、未覆盖的场景 |
| 手工录屏加时间戳 | 用户操作链路的响应/完成时延和视觉问题 | 精确帧率、CPU、内存峰值，除非同时有性能工具数据 |
| 性能分析工具导出 | 帧、卡顿、CPU、内存和音视频同步指标 | 没有包身份和设备信息的孤立数值 |
| 源码、配置、release 构建 | 可能存在的性能风险、测试入口和包身份 | 启动时延、帧率、内存峰值、CPU 峰值已经达标 |

## 规范化测量输入

使用 `scripts/validate_performance_evidence.py` 时，输入 JSON 至少包含包身份、设备
信息、适用规则和测量结果。`required_rule_ids` 由审计者根据真实产品能力填写；例如
不支持视频的应用不应强行执行视频规则，但必须记录不适用原因。

```json
{
  "schema_version": 1,
  "package": {
    "bundle_name": "io.example.app",
    "version_name": "1.0.0",
    "version_code": 1
  },
  "device": {
    "model": "<model>",
    "device_type": "phone",
    "os_version": "<system version>",
    "api_level": 0
  },
  "required_rule_ids": ["DELAY-1", "DELAY-2", "FPS-3"],
  "results": [
    {
      "rule_id": "DELAY-1",
      "status": "measured",
      "value": 80,
      "unit": "ms",
      "input_mode": "touch",
      "statistic": "p95",
      "sample_count": 10,
      "evidence": "docs/qa/performance/startup-trace.json"
    }
  ]
}
```

`status` 只能是 `measured` 或 `not_applicable`。`measured` 必须有数值、单位和证据；
`not_applicable` 必须有原因。没有结果不等于不适用，校验器会报告为
`UNVERIFIED`。同一规则在多个设备上测量时，分别提供证据文件并保留最差结果。

## 时延 / Delay

| ID | 官方标准 | 类型 | 适用设备 |
|---|---|---|---|
| `DELAY-1` | 启动响应：触屏 `<=85 ms`；键鼠 `<=100 ms` | 规则 | 手机、折叠屏、平板、2in1 |
| `DELAY-2` | 启动加载完成 `<=1100 ms` | 规则 | 手机、折叠屏、平板、2in1 |
| `DELAY-3` | 冷启动动画/视频超过 `3 s` 时建议增加进度提示 | 建议 | 手机、折叠屏、平板、2in1 |
| `DELAY-4` | 点击操作响应 `<=100 ms` | 规则 | 手机、折叠屏、平板、2in1 |
| `DELAY-5` | 点击操作完成 `<=900 ms` | 规则 | 手机、折叠屏、平板、2in1 |
| `DELAY-6` | 抛滑（速度大于 `300 mm/s`）触屏响应 `<=80 ms`；拖滑（速度小于 `100 mm/s`）`<=60 ms` | 规则 | 手机、折叠屏、平板、2in1 |
| `DELAY-7` | 折叠操作响应 `<=800 ms` | 规则 | 折叠屏 |
| `DELAY-8` | 展开操作响应 `<=700 ms` | 规则 | 折叠屏 |
| `DELAY-9` | 在线长视频起播 `<=800 ms` | 规则 | 手机、折叠屏、平板、2in1 |
| `DELAY-10` | 长视频拖动进度条 `40%~60%` 后起播 `<=800 ms` | 规则 | 手机、折叠屏、平板、2in1 |
| `DELAY-11` | 滑动短视频后新视频起播 `<=230 ms` | 规则 | 手机、折叠屏、平板、2in1 |
| `DELAY-12` | 短视频拖动进度条 `40%~60%` 后起播 `<=100 ms` | 规则 | 手机、折叠屏、平板、2in1 |

## 帧率 / Frame Rate

| ID | 官方标准 | 类型 |
|---|---|---|
| `FPS-1` | 冷启动动效最大连续丢帧 `0`，加载环节最大连续丢帧 `<=6` | 规则 |
| `FPS-2` | 启动过程平均卡顿率 `0 ms/s` | 规则 |
| `FPS-3` | 滑动过程最大连续丢帧 `0` | 规则 |
| `FPS-4` | 滑动过程卡顿率 `<=5 ms/s` | 规则 |
| `FPS-5` | 应用内转场最大连续丢帧 `0` | 规则 |
| `FPS-6` | 应用内转场卡顿率 `0 ms/s` | 规则 |
| `FPS-7` | 视频弹幕滚动最大连续丢帧 `0` | 规则 |
| `FPS-8` | 视频最大卡顿时长 `<=100 ms`，卡顿次数 `0` | 规则 |
| `FPS-9` | 音画时间差 `-80 ms <= delay <= 25 ms`，且主观观感无不适 | 规则 |

## 内容显示 / Content Display

| ID | 官方标准 | 类型 |
|---|---|---|
| `CONTENT-1` | 启动过程无黑白闪跳时延 `<=40 ms` | 规则 |
| `CONTENT-2` | 滑动页面占位符加载完成时延 `<=40 ms` | 规则 |
| `CONTENT-3` | 已加载内容滑动完整率 `100%` | 规则 |

## 内存与 CPU / Memory And CPU

| ID | 官方标准 | 类型 | 适用设备 |
|---|---|---|---|
| `MEMORY-1` | 操作完成后后台内存峰值建议 `<=1000 MB` | 建议 | 手机、折叠屏、平板 |
| `MEMORY-2` | 前台亮屏使用过程内存峰值建议 `<=1500 MB` | 建议 | 手机、折叠屏、平板 |
| `MEMORY-3` | 冷启动时延类指标建议不高于历史基线；高于时需单独澄清 | 建议 | 手机、折叠屏、平板 |
| `CPU-1` | 后台 CPU 占用峰值 `<2%` | 规则 | 手机、折叠屏、平板 |

## 审计要求

1. 先根据产品能力和声明设备确定 `required_rule_ids`，把视频、折叠屏、2in1 等
   条件规则与实际产品边界对齐。
2. 对每个适用规则给出测量设备、系统版本/API、包身份、场景、采样次数、统计值、
   单位和证据。没有这些字段时最多是 `UNVERIFIED`。
3. 记录最差设备/场景，而不是只记录平均值。历史包的通过结果不能复制到新包。
4. 将规则失败与建议优化分开；不要因为源码看起来简单、debug 构建成功或截图正常，
   推断性能指标通过。
5. 与 AGC 报告关联时，把本地性能证据作为辅助证据；只有 AGC 当前包的“上架自检”
   明确 `已达标` 才能产生 `AGC_READY`。
