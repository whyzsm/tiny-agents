#!/usr/bin/env python3
"""Requirement link intake adapter.

This module keeps the existing screenshot/text/link entry types intact while
adding a Python + MCP path for link-based requirement intake.

The adapter is intentionally small:
- connect to a streamable HTTP MCP server
- discover tools/resources
- read the Yuque document content or call a server tool
- normalize the result into a single RequirementBundle

It does not write back to Yuque or any other document store.
"""

from __future__ import annotations

import argparse
import asyncio
import dataclasses
import hashlib
import json
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator
from urllib.parse import unquote, urlparse


YUQUE_GET_DOC_TOOL = "yuque_get_doc"


@dataclasses.dataclass(slots=True)
class YuqueDocLocator:
    host: str
    repo_id: str
    doc_id: str

    def to_tool_arguments(self) -> dict[str, Any]:
        return {
            "repo_id": self.repo_id,
            "doc_id": self.doc_id,
            "format": "markdown",
            "include_lake": True,
        }


@dataclasses.dataclass(slots=True)
class FetchPlan:
    mode: str
    resource_uri: str | None = None
    resource_name: str | None = None
    tool_name: str | None = None
    tool_arguments: dict[str, Any] = dataclasses.field(default_factory=dict)
    evidence: list[dict[str, Any]] = dataclasses.field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(slots=True)
class RequirementBundle:
    source_type: str
    source_uri: str
    title: str | None
    raw_text: str
    comments: list[str]
    updated_at: str | None
    content_hash: str
    normalized_sections: list[dict[str, Any]]
    confidence: float
    evidence: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def build_content_hash(*parts: str | None) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update((part or "").encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def normalize_text(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    compact: list[str] = []
    blank = False
    for line in lines:
        if line.strip():
            compact.append(line)
            blank = False
        elif not blank:
            compact.append("")
            blank = True
    return "\n".join(compact).strip()


def infer_sections(raw_text: str, comments: list[str]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    if raw_text.strip():
        sections.append({"kind": "body", "text": normalize_text(raw_text)})
    for index, comment in enumerate(comments, start=1):
        text = normalize_text(comment)
        if text:
            sections.append({"kind": "comment", "index": index, "text": text})
    return sections


def parse_yuque_doc_uri(source_uri: str) -> YuqueDocLocator | None:
    parsed = urlparse(source_uri)
    if parsed.scheme not in {"http", "https"}:
        return None

    host = parsed.hostname or ""
    host = host.lower()
    if host != "yuque.com" and not host.endswith(".yuque.com"):
        return None

    segments = [unquote(segment) for segment in parsed.path.split("/") if segment]
    if len(segments) < 3:
        return None

    return YuqueDocLocator(
        host=host,
        repo_id=f"{segments[0]}/{segments[1]}",
        doc_id=segments[2],
    )


def get_discovered_tool_names(discovery: Any) -> set[str]:
    return {
        name
        for tool in getattr(discovery, "tools", [])
        if isinstance(name := getattr(tool, "name", None), str)
    }


def parse_json_object(text: str) -> dict[str, Any] | None:
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def extract_structured_text(text_blocks: list[str], structured: Any) -> tuple[str, dict[str, Any] | None]:
    text = "\n\n".join(text_blocks).strip()
    payload = structured if isinstance(structured, dict) else parse_json_object(text)
    if not isinstance(payload, dict):
        return text, None

    for key in ("body", "rawText", "raw_text", "markdown", "text"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value, payload
    return text, payload


def resolve_fetch_plan(
    *,
    source_uri: str,
    resource_uri: str | None = None,
    resource_name: str | None = None,
    tool_name: str | None = None,
    tool_arguments: dict[str, Any] | None = None,
    discovery: Any | None = None,
) -> FetchPlan:
    if resource_uri:
        return FetchPlan(
            mode="resource",
            resource_uri=resource_uri,
            resource_name=resource_name,
            evidence=[{"kind": "fetch_plan", "mode": "resource"}],
        )

    if tool_name:
        return FetchPlan(
            mode="tool",
            tool_name=tool_name,
            tool_arguments=tool_arguments or {},
            evidence=[{"kind": "fetch_plan", "mode": "explicit_tool", "tool_name": tool_name}],
        )

    yuque_locator = parse_yuque_doc_uri(source_uri)
    if yuque_locator:
        if discovery is not None and YUQUE_GET_DOC_TOOL not in get_discovered_tool_names(discovery):
            raise RuntimeError(
                f"Yuque URL detected, but the MCP server does not expose '{YUQUE_GET_DOC_TOOL}'. "
                "Pass --tool-name/--tool-arguments explicitly or expose the Yuque document reader."
            )
        return FetchPlan(
            mode="tool",
            tool_name=YUQUE_GET_DOC_TOOL,
            tool_arguments=yuque_locator.to_tool_arguments(),
            evidence=[
                {
                    "kind": "source_provider",
                    "provider": "yuque",
                    "host": yuque_locator.host,
                    "repo_id": yuque_locator.repo_id,
                    "doc_id": yuque_locator.doc_id,
                },
                {"kind": "fetch_plan", "mode": "auto_yuque_doc", "tool_name": YUQUE_GET_DOC_TOOL},
            ],
        )

    raise ValueError(
        "No MCP fetch target could be resolved. Provide --resource-uri/--tool-name, "
        "or pass a supported Yuque document URL."
    )


@asynccontextmanager
async def connect_to_mcp_server(url: str) -> AsyncIterator[Any]:
    try:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client
    except Exception as exc:  # pragma: no cover - dependency guard
        raise RuntimeError(
            "The 'mcp' Python package is required. Install the Model Context Protocol Python SDK first."
        ) from exc

    async with streamable_http_client(url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


async def fetch_from_resource_or_tool(
    session: Any,
    *,
    resource_uri: str | None = None,
    resource_name: str | None = None,
    tool_name: str | None = None,
    tool_arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if resource_uri:
        result = await session.read_resource(resource_uri)
        contents = getattr(result, "contents", [])
        text_blocks: list[str] = []
        for item in contents:
            text = getattr(item, "text", None)
            if text:
                text_blocks.append(text)
        return {
            "mode": "resource",
            "resource_uri": resource_uri,
            "resource_name": resource_name,
            "text": "\n\n".join(text_blocks).strip(),
            "raw": result.model_dump() if hasattr(result, "model_dump") else result,
        }

    if tool_name:
        result = await session.call_tool(tool_name, tool_arguments or {})
        text_blocks: list[str] = []
        for item in getattr(result, "content", []):
            text = getattr(item, "text", None)
            if text:
                text_blocks.append(text)
        structured = getattr(result, "structured_content", None) or getattr(result, "structuredContent", None)
        text, payload = extract_structured_text(text_blocks, structured)
        return {
            "mode": "tool",
            "tool_name": tool_name,
            "text": text,
            "structured": payload,
            "raw": result.model_dump() if hasattr(result, "model_dump") else result,
        }

    raise ValueError("Either resource_uri or tool_name must be provided.")


async def build_requirement_bundle(
    *,
    mcp_url: str,
    source_uri: str,
    resource_uri: str | None = None,
    tool_name: str | None = None,
    tool_arguments: dict[str, Any] | None = None,
    source_type: str = "link",
) -> RequirementBundle:
    async with connect_to_mcp_server(mcp_url) as session:
        discovery = await session.list_tools()
        resources = await session.list_resources()
        fetch_plan = resolve_fetch_plan(
            source_uri=source_uri,
            resource_uri=resource_uri,
            tool_name=tool_name,
            tool_arguments=tool_arguments,
            discovery=discovery,
        )
        fetched = await fetch_from_resource_or_tool(
            session,
            resource_uri=fetch_plan.resource_uri,
            resource_name=fetch_plan.resource_name,
            tool_name=fetch_plan.tool_name,
            tool_arguments=fetch_plan.tool_arguments,
        )

    raw_text = fetched.get("text", "")
    comments: list[str] = []
    if isinstance(fetched.get("structured"), dict):
        structured = fetched["structured"]
        maybe_comments = structured.get("comments")
        if isinstance(maybe_comments, list):
            comments = [str(item) for item in maybe_comments if item is not None]

    title = None
    updated_at = None
    if isinstance(fetched.get("structured"), dict):
        title = fetched["structured"].get("title") or fetched["structured"].get("name")
        updated_at = fetched["structured"].get("updatedAt") or fetched["structured"].get("updated_at")

    normalized_sections = infer_sections(raw_text, comments)
    content_hash = build_content_hash(
        source_uri,
        title,
        updated_at,
        raw_text,
        json.dumps(normalized_sections, ensure_ascii=False, sort_keys=True),
    )
    evidence = [
        {"kind": "mcp_server", "url": mcp_url},
        {"kind": "tool_count", "value": len(getattr(discovery, "tools", []))},
        {"kind": "resource_count", "value": len(getattr(resources, "resources", []))},
        *fetch_plan.evidence,
    ]

    return RequirementBundle(
        source_type=source_type,
        source_uri=source_uri,
        title=title,
        raw_text=normalize_text(raw_text),
        comments=comments,
        updated_at=updated_at,
        content_hash=content_hash,
        normalized_sections=normalized_sections,
        confidence=0.75 if normalized_sections else 0.35,
        evidence=evidence,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read a requirement link through an MCP server and normalize it.")
    parser.add_argument("--mcp-url", default=os.environ.get("MCP_URL", ""), help="Streamable HTTP MCP server URL")
    parser.add_argument("--source-uri", required=True, help="Original requirement link")
    parser.add_argument("--resource-uri", help="Raw MCP resource URI, if the server exposes resources")
    parser.add_argument("--tool-name", help="MCP tool name, if the server exposes a fetch tool")
    parser.add_argument("--tool-arguments", default="{}", help="JSON object passed to the MCP tool")
    parser.add_argument("--print-fetch-plan", action="store_true", help="Print the resolved MCP fetch plan without connecting")
    parser.add_argument("--source-type", default="link", choices=["screenshot", "link", "text"], help="User-facing source type")
    return parser.parse_args()


async def amain() -> int:
    args = parse_args()
    try:
        tool_arguments = json.loads(args.tool_arguments)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid --tool-arguments JSON: {exc}") from exc
    if not isinstance(tool_arguments, dict):
        raise SystemExit("--tool-arguments must decode to a JSON object")

    if args.print_fetch_plan:
        fetch_plan = resolve_fetch_plan(
            source_uri=args.source_uri,
            resource_uri=args.resource_uri,
            tool_name=args.tool_name,
            tool_arguments=tool_arguments,
        )
        print(json.dumps(fetch_plan.to_dict(), ensure_ascii=False, indent=2))
        return 0

    if not args.mcp_url:
        raise SystemExit("--mcp-url or MCP_URL is required")

    try:
        bundle = await build_requirement_bundle(
            mcp_url=args.mcp_url,
            source_uri=args.source_uri,
            resource_uri=args.resource_uri,
            tool_name=args.tool_name,
            tool_arguments=tool_arguments,
            source_type=args.source_type,
        )
    except Exception as exc:
        pending, reasons = [exc], []
        while pending:
            err = pending.pop(0)
            subs = getattr(err, "exceptions", None) or []
            if subs:
                pending.extend(subs)
            else:
                reasons.append(str(err).strip() or repr(err))
        summary = "; ".join(dict.fromkeys(item for item in reasons if item)) or type(exc).__name__
        raise SystemExit(
            f"MCP fetch failed for {args.source_uri}: {summary}. "
            "Keep the original link and record the gap; do not treat the requirement as complete."
        ) from exc
    print(json.dumps(bundle.to_dict(), ensure_ascii=False, indent=2))
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(amain()))


if __name__ == "__main__":
    main()
