# HTML 邮件模板使用说明
# 版本：v3.1

## 模板变量

发送邮件前，以下 Jinja2 变量会被自动填充：

| 变量名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `{{ report_title }}` | String | 报告标题 | "张三技术部 2026年06月08日 日报" |
| `{{ period }}` | String | 报告周期 | "2026年6月8日" 或 "2026年6月1日~6月7日" |
| `{{ author_name }}` | String | 作者姓名 | "张三" |
| `{{ author_dept }}` | String | 作者部门 | "技术部" |
| `{{ greeting }}` | String | 称呼 | "张总，您好：" |
| `{{ summary_html }}` | HTML | 核心摘要（自动生成） | 表格形式展示关键数据和完成情况 |
| `{{ content_html }}` | HTML | 报告正文（Markdown 转 HTML） | 带格式的完整报告内容 |
| `{{ signature }}` | String | 签名档 | "张三 · 技术部 · XX公司" |
| `{{ generate_time }}` | String | 生成时间 | "2026-06-08 18:00:00" |
| `{{ attachments_note }}` | String | 附件说明 | "详见附件：20260608_daily.docx" |

## 样式规范

### 品牌色
- **主色调**：`#1E88E5`（专业蓝）— 用于标题栏、链接、分割线
- **强调色**：`#4CAF50`（成功绿）— 用于完成状态、数据达成
- **警告色**：`#FF9800`（橙色）— 用于待解决问题、风险项
- **文字色**：`#333333`（正文）、`#666666`（次要信息）、`#999999`（辅助文字）

### 响应式断点
- 桌面端：600px 宽度容器（主流邮件客户端标准）
- 移动端：`max-width: 100%` 自适应，字体 14px→15px 微调

### 邮件客户端兼容
- **不支持**：CSS Grid、Flexbox、`position: absolute`、JavaScript、外部CSS文件
- **推荐**：table 布局 + inline style + 内嵌 CSS（`<style>` 在 `<head>` 中，Gmail 会过滤）
- **最佳实践**：关键样式用 inline style，颜色/背景同时声明在 inline 和 `<style>` 中

## 自定义模板

保存自定义 HTML 模板到 `templates/custom/` 目录，命名规则：
- `email_日报.html`
- `email_周报.html`
- `email_月报.html`

AI 会根据报告类型自动选择匹配的模板。
