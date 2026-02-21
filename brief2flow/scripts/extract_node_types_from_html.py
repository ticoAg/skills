#!/usr/bin/env python3
"""
Extract Coze node panel entries from a copied HTML snippet.

Input: an HTML file copied from Coze workflow node panel (e.g. temp.html)
Output: a Markdown table with (data_node_type, title_zh).

Notes:
- data_node_type is a UI category id from the node panel; it may not map 1:1 to workspace YAML node.type.
- The same data_node_type may appear with multiple titles (e.g. plugin-related cards). We keep all rows.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import html as _html
import re
import sys
from pathlib import Path


_ENTRY_RE = re.compile(
    r'data-node-type="(?P<type>\d+)"'
    r".*?"
    r"node-title[^>]*>\s*<span>(?P<title>[^<]+)</span>",
    re.DOTALL,
)


def _normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", _html.unescape(s or "")).strip()


def extract_entries(html_text: str) -> list[tuple[int, str]]:
    seen: set[tuple[int, str]] = set()
    entries: list[tuple[int, str]] = []
    for m in _ENTRY_RE.finditer(html_text):
        node_type = int(m.group("type"))
        title = _normalize_text(m.group("title"))
        key = (node_type, title)
        if not title or key in seen:
            continue
        seen.add(key)
        entries.append(key)
    entries.sort(key=lambda x: (x[0], x[1]))
    return entries


def render_markdown(entries: list[tuple[int, str]], source_name: str) -> str:
    now = _dt.datetime.now().astimezone().isoformat(timespec="seconds")
    lines: list[str] = []
    lines.append("# Coze 节点面板类型清单（从 HTML 抽取）")
    lines.append("")
    lines.append("说明：")
    lines.append("- `data_node_type` 来自 Coze 节点面板的 `data-node-type` 数字。它是 UI 分类/卡片类型，不保证与 workspace YAML 的 `node.type` 字段一一对应。")
    lines.append("- 同一个 `data_node_type` 可能对应多张卡片（不同中文名称）；本表保留全部条目。")
    lines.append("")
    lines.append(f"来源：`{source_name}`")
    lines.append(f"抽取时间：`{now}`")
    lines.append("")
    lines.append("| data_node_type | title_zh |")
    lines.append("|---:|---|")
    for node_type, title in entries:
        lines.append(f"| {node_type} | {title} |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("html_path", help="Path to copied HTML (e.g. temp.html)")
    p.add_argument("--out", help="Write output markdown to this file (otherwise stdout)", default="")
    args = p.parse_args(argv[1:])

    html_path = Path(args.html_path).expanduser()
    if not html_path.exists():
        print(f"ERROR: file not found: {html_path}", file=sys.stderr)
        return 2

    html_text = html_path.read_text(encoding="utf-8", errors="ignore")
    entries = extract_entries(html_text)
    if not entries:
        print("ERROR: no entries extracted. The HTML snippet format may have changed.", file=sys.stderr)
        return 1

    md = render_markdown(entries, source_name=str(html_path))

    out = str(args.out or "").strip()
    if out:
        out_path = Path(out).expanduser()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(f"OK: wrote {len(entries)} entries to {out_path}")
        return 0

    sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

