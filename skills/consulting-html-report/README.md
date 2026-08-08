# consulting-html-report

项目内技能：将零散业务材料、截图和指标整理为咨询风格单文件 HTML 研究报告，并支持按截图反馈持续迭代。

## 目录

```text
consulting-html-report/
├── SKILL.md
├── assets/report-template.html
├── scripts/render_check.cjs
└── evals/evals.json
```

## 常用验证命令

```bash
node 90_项目与工具/skills/consulting-html-report/scripts/render_check.cjs \
  --html /absolute/path/to/report.html \
  --out-dir /absolute/path/to/render-output \
  --chrome "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --must-contain "核心发现"
```
