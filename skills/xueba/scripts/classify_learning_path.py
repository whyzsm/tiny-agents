#!/usr/bin/env python3
"""Classify a learning note into a simple Obsidian path under 88-学习/.

This script is deterministic and user-agnostic. It never resolves a local vault
and never writes files; it only returns a relative directory and safe filename.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_TITLE = "未命名学习笔记"
LEARNING_ROOT = "88-学习"


RULES: list[dict[str, Any]] = [
    {
        "relative_dir": "88-学习/AI/skills",
        "domain_tag": "domain/ai/skills",
        "keywords": ["agent skills", "agentskills", "skill.md", "skill creator", "技能包", "技能标准"],
    },
    {
        "relative_dir": "88-学习/AI/harness",
        "domain_tag": "domain/ai/harness",
        "keywords": ["agent harness", "harness", "测试框架", "评测框架"],
    },
    {
        "relative_dir": "88-学习/AI/RAG",
        "domain_tag": "domain/ai/rag",
        "keywords": ["rag", "graphrag", "retrieval augmented", "检索增强", "向量检索"],
    },
    {
        "relative_dir": "88-学习/AI/MCP",
        "domain_tag": "domain/ai/mcp",
        "keywords": ["mcp", "model context protocol"],
    },
    {
        "relative_dir": "88-学习/AI/prompting",
        "domain_tag": "domain/ai/prompting",
        "keywords": ["prompt", "prompting", "提示词"],
    },
    {
        "relative_dir": "88-学习/AI/eval",
        "domain_tag": "domain/ai/eval",
        "keywords": ["eval", "evaluation", "评估", "评测"],
    },
    {
        "relative_dir": "88-学习/AI/LLM",
        "domain_tag": "domain/ai/llm",
        "keywords": ["llm", "large language model", "大模型"],
    },
    {
        "relative_dir": "88-学习/AI/智能体",
        "domain_tag": "domain/ai/agent",
        "keywords": ["agent", "智能体", "multi-agent", "多智能体", "agentic"],
    },
    {
        "relative_dir": "88-学习/产品/PRD",
        "domain_tag": "domain/product/prd",
        "keywords": ["prd", "需求文档", "产品需求"],
    },
    {
        "relative_dir": "88-学习/管理/OKR",
        "domain_tag": "domain/management/okr",
        "keywords": ["okr", "kpi", "目标管理"],
    },
    {
        "relative_dir": "88-学习/业务/CRM",
        "domain_tag": "domain/business/crm",
        "keywords": ["crm", "回款", "客户关系"],
    },
    {
        "relative_dir": "88-学习/技术/前端",
        "domain_tag": "domain/tech/frontend",
        "keywords": ["frontend", "react", "vue", "前端"],
    },
    {
        "relative_dir": "88-学习/技术/后端",
        "domain_tag": "domain/tech/backend",
        "keywords": ["backend", "api", "后端", "服务端"],
    },
    {
        "relative_dir": "88-学习/工具/Obsidian",
        "domain_tag": "domain/tools/obsidian",
        "keywords": ["obsidian", "双链", "zettelkasten", "卡片盒"],
    },
]


def load_input(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    try:
        text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        data = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Failed to read input JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("Input JSON must be an object.")
    return data


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def normalize_text(values: list[str]) -> str:
    return " ".join(values).casefold()


def choose_path(title: str, domain_tags: list[str], keywords: list[str], source: str) -> dict[str, Any]:
    haystack = normalize_text([title, source, *domain_tags, *keywords])
    domain_set = {tag.casefold() for tag in domain_tags}
    matches: list[dict[str, Any]] = []

    for rule in RULES:
        score = 0
        reasons: list[str] = []
        domain_tag = str(rule["domain_tag"]).casefold()
        if domain_tag in domain_set:
            score += 100
            reasons.append(f"domain tag matched: {rule['domain_tag']}")
        for keyword in rule["keywords"]:
            if str(keyword).casefold() in haystack:
                score += 10
                reasons.append(f"keyword matched: {keyword}")
        if score:
            matches.append({"rule": rule, "score": score, "reasons": reasons})

    if not matches:
        return {
            "relative_dir": "88-学习/待分类",
            "domain_tag": "domain/unknown",
            "confidence": "low",
            "reasons": ["no domain tag or keyword rule matched"],
        }

    matches.sort(key=lambda item: (item["score"], len(item["rule"]["keywords"])), reverse=True)
    best = matches[0]
    confidence = "high" if best["score"] >= 100 else "medium"
    return {
        "relative_dir": best["rule"]["relative_dir"],
        "domain_tag": best["rule"]["domain_tag"],
        "confidence": confidence,
        "reasons": best["reasons"],
    }


def sanitize_filename(title: str) -> str:
    title = re.sub(r"\s+", " ", title).strip() or DEFAULT_TITLE
    replacements = {
        "/": "／",
        "\\": "-",
        ":": "：",
        "*": "-",
        "?": "？",
        '"': "'",
        "<": "《",
        ">": "》",
        "|": "-",
    }
    for source, replacement in replacements.items():
        title = title.replace(source, replacement)
    title = re.sub(r"[\x00-\x1f]", "", title).strip(" .")
    if not title:
        title = DEFAULT_TITLE
    if len(title) > 90:
        title = title[:90].rstrip()
    return f"{title}.md" if not title.casefold().endswith(".md") else title


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify a learning note path under 88-学习/.")
    parser.add_argument("--input", help="JSON input file, or '-' for stdin.")
    parser.add_argument("--title", help="Note title.")
    parser.add_argument("--domain-tag", action="append", default=[], help="Domain tag. Can be passed multiple times.")
    parser.add_argument("--keyword", action="append", default=[], help="Keyword. Can be passed multiple times.")
    parser.add_argument("--source", default="", help="Source URL or name.")
    parser.add_argument("--json", action="store_true", help="Print JSON output. This is the default.")
    args = parser.parse_args()

    data = load_input(args.input)
    title = args.title or str(data.get("title") or data.get("topic") or DEFAULT_TITLE)
    domain_tags = [*as_list(data.get("domain_tags")), *as_list(data.get("domain_tag")), *args.domain_tag]
    keywords = [*as_list(data.get("keywords")), *args.keyword]
    source = args.source or str(data.get("source") or data.get("source_url") or "")

    result = choose_path(title, domain_tags, keywords, source)
    result["filename"] = sanitize_filename(title)
    result["title"] = title
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
