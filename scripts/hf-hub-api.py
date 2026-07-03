#!/usr/bin/env python3
"""
Read-only Hugging Face Hub REST helpers for LMA discovery.

Use this for lists, counts, and pagination (collections, org models). Pair with
HF MCP tools (hub_repo_details, hub_repo_search, hf_doc_search) for drill-down —
not hf_hub_query (see integrations/mcp/hf-hub-api.md).

Usage:
  ./scripts/py scripts/hf-hub-api.py health
  ./scripts/py scripts/hf-hub-api.py collections --owner mlx-community
  ./scripts/py scripts/hf-hub-api.py collections --owner mlx-community --recent 10
  ./scripts/py scripts/hf-hub-api.py models --author mlx-community --limit 20
  ./scripts/py scripts/hf-hub-api.py models --search "qwen coder gguf" --limit 10 --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

HF_API = "https://huggingface.co/api"
USER_AGENT = "Local-Model-Assessor/hf-hub-api"


def _request(url: str, *, timeout: float = 30.0) -> tuple[Any, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            link = resp.headers.get("Link")
            body = json.load(resp)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"Hub API error {exc.code}: {exc.reason} — {url}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Hub API unreachable: {exc.reason}") from exc
    next_url = None
    if link:
        match = re.search(r'<([^>]+)>;\s*rel="next"', link)
        if match:
            next_url = match.group(1)
    return body, next_url


def paginate(
    path: str,
    params: dict[str, str | int],
    *,
    max_pages: int | None = None,
) -> list[Any]:
    query = urllib.parse.urlencode(params)
    url = f"{HF_API}{path}?{query}"
    items: list[Any] = []
    pages = 0
    while url:
        batch, url = _request(url)
        if not isinstance(batch, list):
            raise SystemExit(f"Expected list from {path}, got {type(batch).__name__}")
        items.extend(batch)
        pages += 1
        if max_pages is not None and pages >= max_pages:
            break
        if not batch:
            break
    return items


def list_collections(
    owner: str,
    *,
    limit_per_page: int = 100,
    max_pages: int | None = None,
) -> list[dict[str, Any]]:
    return paginate(
        "/collections",
        {"owner": owner, "limit": limit_per_page},
        max_pages=max_pages,
    )


def collection_item_count(collection: dict[str, Any]) -> int | str:
    items = collection.get("items")
    if isinstance(items, list):
        return len(items)
    count = collection.get("itemCount")
    if count is not None:
        return int(count)
    return "?"


def list_models(
    *,
    author: str | None = None,
    search: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    params: dict[str, str | int] = {"limit": min(limit, 100)}
    if author:
        params["author"] = author
    if search:
        params["search"] = search
    batch, _ = _request(f"{HF_API}/models?{urllib.parse.urlencode(params)}")
    if not isinstance(batch, list):
        raise SystemExit("Expected list from /models")
    return batch[:limit]


def cmd_health() -> int:
    _, _ = _request(f"{HF_API}/collections?owner=mlx-community&limit=1", timeout=15.0)
    print("ok huggingface.co/api reachable")
    return 0


def cmd_collections(args: argparse.Namespace) -> int:
    collections = list_collections(
        args.owner,
        limit_per_page=args.page_size,
        max_pages=args.max_pages,
    )
    collections.sort(key=lambda c: c.get("lastUpdated") or "", reverse=True)
    recent = collections[: args.recent] if args.recent else collections

    summary = {
        "owner": args.owner,
        "total": len(collections),
        "recent": [
            {
                "slug": c.get("slug"),
                "title": c.get("title"),
                "lastUpdated": c.get("lastUpdated"),
                "itemCount": collection_item_count(c),
            }
            for c in recent
        ],
    }
    if args.json:
        print(json.dumps(summary, indent=2))
        return 0

    print(f"Collections for {args.owner}: {len(collections)} total")
    if args.recent:
        print(f"\nMost recently updated ({min(args.recent, len(collections))}):")
        for c in recent:
            lu = (c.get("lastUpdated") or "")[:10]
            n = collection_item_count(c)
            title = (c.get("title") or c.get("slug") or "?")[:60]
            print(f"  {lu}  items={str(n):>3}  {title}")
    return 0


def cmd_models(args: argparse.Namespace) -> int:
    models = list_models(author=args.author, search=args.search, limit=args.limit)
    rows = [
        {
            "id": m.get("id") or m.get("modelId"),
            "downloads": m.get("downloads"),
            "likes": m.get("likes"),
            "lastModified": m.get("lastModified"),
        }
        for m in models
    ]
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    label = args.author or args.search or "models"
    print(f"{label}: {len(rows)} result(s)")
    for row in rows:
        lm = (row.get("lastModified") or "")[:10]
        print(f"  {lm}  {row.get('id')}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hugging Face Hub REST helpers for LMA")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("health", help="Quick Hub API reachability check")

    col = sub.add_parser("collections", help="List/count collections for an owner/org")
    col.add_argument("--owner", required=True, help="Hub owner or org (e.g. mlx-community)")
    col.add_argument("--recent", type=int, default=10, help="Show N most recently updated")
    col.add_argument("--page-size", type=int, default=100, help="API page size (max 100)")
    col.add_argument("--max-pages", type=int, default=None, help="Cap pagination pages")
    col.add_argument("--json", action="store_true", help="JSON output")

    mod = sub.add_parser("models", help="List models by author or search")
    mod.add_argument("--author", help="Filter by author/org")
    mod.add_argument("--search", help="Hub model search string")
    mod.add_argument("--limit", type=int, default=20, help="Max models to return")
    mod.add_argument("--json", action="store_true", help="JSON output")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "health":
        return cmd_health()
    if args.command == "collections":
        return cmd_collections(args)
    if args.command == "models":
        if not args.author and not args.search:
            parser.error("models requires --author and/or --search")
        return cmd_models(args)
    parser.error(f"unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
