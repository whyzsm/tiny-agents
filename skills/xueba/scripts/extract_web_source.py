#!/usr/bin/env python3
"""Extract readable public content from ordinary and CMS-style web pages.

The script is intentionally credential-free. It reads HTML, meta tags, visible
text, links, and common encoded JSON/script-state payloads so Study Mode can
avoid treating a JavaScript shell as an empty source.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import OrderedDict
from html.parser import HTMLParser
from typing import Any


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.7",
}


class TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.meta: dict[str, str] = {}
        self.links: list[dict[str, str]] = []
        self.texts: list[str] = []
        self._skip_stack: list[str] = []
        self._current_link: dict[str, str] | None = None
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.casefold(): value or "" for key, value in attrs}
        tag = tag.casefold()
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_stack.append(tag)
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            key = attrs_dict.get("name") or attrs_dict.get("property")
            content = attrs_dict.get("content")
            if key and content:
                self.meta[key] = clean_text(content)
        if tag == "a":
            self._current_link = {"href": attrs_dict.get("href", ""), "text": ""}

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if self._skip_stack and self._skip_stack[-1] == tag:
            self._skip_stack.pop()
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._current_link:
            self._current_link["text"] = clean_text(self._current_link["text"])
            if self._current_link["href"] or self._current_link["text"]:
                self.links.append(self._current_link)
            self._current_link = None

    def handle_data(self, data: str) -> None:
        if self._skip_stack:
            return
        text = clean_text(data)
        if not text:
            return
        if self._in_title:
            self.title = clean_text(f"{self.title} {text}")
            return
        if self._current_link is not None:
            self._current_link["text"] = clean_text(f"{self._current_link['text']} {text}")
        self.texts.append(text)


def clean_text(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def dedupe_strings(values: list[str], max_items: int = 300) -> list[str]:
    result: OrderedDict[str, str] = OrderedDict()
    for value in values:
        text = clean_text(value)
        if len(text) < 2:
            continue
        result.setdefault(text, text)
        if len(result) >= max_items:
            break
    return list(result.values())


def fetch_html(url: str, timeout: int) -> tuple[str, str, int | None]:
    request = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        final_url = response.geturl()
        status = getattr(response, "status", None)
    return raw.decode(charset, "replace"), final_url, status


def parse_html(source: str) -> dict[str, Any]:
    parser = TextHTMLParser()
    parser.feed(source)
    return {
        "title": parser.title,
        "meta": parser.meta,
        "visible_text": dedupe_strings(parser.texts),
        "links": dedupe_links(parser.links),
    }


def dedupe_links(links: list[dict[str, str]], max_items: int = 120) -> list[dict[str, str]]:
    result: OrderedDict[tuple[str, str], dict[str, str]] = OrderedDict()
    for link in links:
        href = clean_text(link.get("href"))
        text = clean_text(link.get("text"))
        if not href and not text:
            continue
        key = (text, href)
        result.setdefault(key, {"text": text, "href": href})
        if len(result) >= max_items:
            break
    return list(result.values())


def extract_json_texts(data: Any) -> tuple[list[str], list[dict[str, str]]]:
    texts: list[str] = []
    links: list[dict[str, str]] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            item_type = value.get("_type")
            if item_type == "TextItem" and "value" in value:
                texts.append(clean_text(value.get("value")))
            elif item_type == "AlinkItem":
                href = clean_text(value.get("href"))
                label = ""
                text_obj = value.get("text")
                if isinstance(text_obj, dict):
                    label = clean_text(text_obj.get("value"))
                if href or label:
                    links.append({"text": label, "href": href})
            else:
                for key in ("title", "name", "description", "summary", "content", "text", "value"):
                    raw = value.get(key)
                    if isinstance(raw, str):
                        texts.append(clean_text(raw))
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(data)
    return dedupe_strings(texts), dedupe_links(links)


def extract_encoded_json(source: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    patterns = [
        r"JSON\.parse\(decodeURIComponent\(\"(.*?)\"\)\)",
        r"decodeURIComponent\(\"(%7B.*?%7D)\"\)",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, source, flags=re.S):
            encoded = match.group(1)
            try:
                decoded = urllib.parse.unquote(encoded)
                data = json.loads(decoded)
            except (json.JSONDecodeError, ValueError):
                continue
            texts, links = extract_json_texts(data)
            if texts or links:
                results.append(
                    {
                        "kind": "encoded_json",
                        "text_count": len(texts),
                        "texts": texts,
                        "links": links,
                    }
                )
    return results


def extract_next_data(source: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    match = re.search(r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>', source, flags=re.S)
    if not match:
        return results
    try:
        data = json.loads(html.unescape(match.group(1)))
    except json.JSONDecodeError:
        return results
    texts, links = extract_json_texts(data)
    if texts or links:
        results.append({"kind": "next_data", "text_count": len(texts), "texts": texts, "links": links})
    return results


def detect_shell(parsed: dict[str, Any], source: str) -> bool:
    visible_count = len(parsed.get("visible_text") or [])
    shell_markers = ["<app-root", "__NEXT_DATA__", "id=\"root\"", "id=\"app\"", "data-reactroot"]
    has_shell_marker = any(marker in source for marker in shell_markers)
    return visible_count < 10 and has_shell_marker


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract readable public content from a web page.")
    parser.add_argument("--url", required=True, help="Public URL to fetch.")
    parser.add_argument("--timeout", type=int, default=25, help="Request timeout in seconds.")
    parser.add_argument("--json", action="store_true", help="Print JSON output. This is the default.")
    args = parser.parse_args()

    try:
        source, final_url, status = fetch_html(args.url, args.timeout)
    except Exception as exc:  # noqa: BLE001 - CLI should report any fetch failure as JSON.
        print(json.dumps({"ok": False, "error": str(exc), "url": args.url}, ensure_ascii=False, indent=2))
        return 2

    parsed = parse_html(source)
    encoded = [*extract_encoded_json(source), *extract_next_data(source)]
    output = {
        "ok": True,
        "url": args.url,
        "final_url": final_url,
        "status": status,
        "html_chars": len(source),
        "title": parsed["title"],
        "meta": parsed["meta"],
        "visible_text_count": len(parsed["visible_text"]),
        "visible_text": parsed["visible_text"],
        "links": parsed["links"],
        "encoded_sources": encoded,
        "encoded_text_count": sum(item.get("text_count", 0) for item in encoded),
        "spa_shell": detect_shell(parsed, source),
        "source_access": "public",
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
