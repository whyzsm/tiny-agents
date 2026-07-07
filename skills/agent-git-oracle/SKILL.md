---
name: agent-git-oracle
description: "Git-history-informed repository analysis for technical debt, hotspot files, architectural anti-patterns, repeated churn, complexity risk, and refactoring priority. Use when the user asks to analyze git history, find code hotspots, identify debt accumulation, rank risky modules, or plan refactoring from repository evolution evidence."
---

# Agent Git Oracle

Analyze repository history and structure to guide safe refactoring. This skill performs deep-scan audits of your local git repositories, identifying areas of high complexity, potential logic leaks, and opportunities for Agent-Native refactoring.

## Features
- **Debt Detection**: Highlights "Dirty Code" that increases cognitive load.
- **Agentic Mapping**: Suggests how to convert traditional modules into autonomous tools.
- **Commit Wisdom**: Summarizes the "Why" behind large architectural shifts in your project.

## Usage
```bash
# Run local git and code analysis commands in the target repository
git log --stat --oneline --decorate --date=short -- .
```


## Codex Notes

Use local repository evidence by default. Do not call external paid services or blockchain/payment endpoints unless the user explicitly requests that integration and confirms credentials, network access, and cost.
