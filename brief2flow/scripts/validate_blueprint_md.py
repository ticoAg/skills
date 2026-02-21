#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    level: str  # "ERROR" | "WARN"
    message: str


MERMAID_BLOCK_RE = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)
NODE_HEADING_RE = re.compile(r"^###\s+(Node\.\d+(?:\.\d+)?)\b", re.MULTILINE)
ABSTRACT_HEADING_RE = re.compile(r"^##\s+摘要\b", re.MULTILINE)

VAR_BULLET_RE = re.compile(r"^\s*-\s+`(?P<name>[^`]+)`(?P<rest>.*)$")
SECTION_MARK_RE = re.compile(r"^\-\s+\*\*(?P<sec>输入|输出)\*\*", re.MULTILINE)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _split_node_sections(text: str) -> list[tuple[str, str]]:
    matches = list(NODE_HEADING_RE.finditer(text))
    out: list[tuple[str, str]] = []
    for idx, m in enumerate(matches):
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        node_id = m.group(1)
        out.append((node_id, text[start:end]))
    return out


def _extract_section_window(section_text: str, sec_name: str, max_lines: int = 60) -> str | None:
    lines = section_text.splitlines()
    sec_re = re.compile(rf"^\-\s+\*\*{re.escape(sec_name)}\*\*")
    try:
        start_idx = next(i for i, ln in enumerate(lines) if sec_re.search(ln))
    except StopIteration:
        return None

    end_idx = min(len(lines), start_idx + max_lines)
    for j in range(start_idx + 1, end_idx):
        if SECTION_MARK_RE.search(lines[j]):
            end_idx = j
            break
        if re.search(r"^\-\s+\*\*Prompt\b", lines[j]):
            end_idx = j
            break
        if re.search(r"^\-\s+\*\*prompt/代码\b", lines[j]):
            end_idx = j
            break

    return "\n".join(lines[start_idx:end_idx])


def _parse_var_bullet(line: str) -> tuple[str, str | None, str | None]:
    m = VAR_BULLET_RE.match(line)
    if not m:
        return "", None, None

    name = m.group("name").strip()
    rest = m.group("rest")

    type_str: str | None = None
    paren_m = re.match(r"\s*[（(]([^）)]+)[）)]", rest)
    if paren_m:
        inside = paren_m.group(1).strip()
        type_str = re.split(r"[，,]\s*", inside, maxsplit=1)[0].strip() or None

    comment_str: str | None = None
    search_from = 0
    if paren_m:
        search_from = paren_m.end()
    tail = rest[search_from:]
    sep_idx = tail.find("：")
    if sep_idx < 0:
        sep_idx = tail.find(":")
    if sep_idx >= 0:
        comment_str = tail[sep_idx + 1 :].strip() or None

    return name, type_str, comment_str


def _input_has_source(line: str) -> bool:
    if "←" in line:
        return True
    if "来自「" in line:
        return True
    if "来源：" in line:
        return True
    return False


def validate(text: str) -> list[Finding]:
    findings: list[Finding] = []

    if ABSTRACT_HEADING_RE.search(text) is None:
        findings.append(Finding("WARN", "Missing abstract-style summary section: expected heading '## 摘要' near the top"))

    mermaid_blocks = MERMAID_BLOCK_RE.findall(text)
    if not mermaid_blocks:
        findings.append(Finding("ERROR", "Missing mermaid block fenced by ```mermaid ... ```"))
    else:
        for i, block in enumerate(mermaid_blocks, 1):
            if "flowchart TD" not in block:
                findings.append(Finding("WARN", f"Mermaid block #{i}: expected 'flowchart TD' for maximum compatibility"))
            if "(" in block or ")" in block:
                findings.append(Finding("ERROR", f"Mermaid block #{i}: contains '(' or ')', which often breaks parsers"))
            if "<br/>" in block or "<br />" in block:
                findings.append(Finding("ERROR", f"Mermaid block #{i}: contains '<br/>' which often breaks parsers"))
            if "Node." not in block:
                findings.append(Finding("WARN", f"Mermaid block #{i}: no 'Node.' labels found (ok if intentional)"))

    sections = _split_node_sections(text)
    if not sections:
        findings.append(Finding("ERROR", "No node sections found. Expected headings like: ### Node.1 ..."))
        return findings

    for node_id, section in sections:
        if f"：{node_id} " not in section and f"：{node_id}\n" not in section:
            findings.append(Finding("WARN", f"{node_id}: missing '- **名称（带序号）**：{node_id} ...' line"))

        if re.search(r"^\-\s+\*\*功能\*\*：", section, flags=re.MULTILINE) is None:
            findings.append(Finding("WARN", f"{node_id}: missing '- **功能**：...' line"))

        type_line_match = re.search(r"^\-\s+\*\*类型\*\*：(.+)$", section, flags=re.MULTILINE)
        is_start_node = False
        is_end_node = False
        if not type_line_match:
            findings.append(Finding("WARN", f"{node_id}: missing '- **类型**：`...`' line"))
        else:
            type_value = type_line_match.group(1).strip()
            if "`" not in type_value:
                findings.append(Finding("ERROR", f"{node_id}: type value should be wrapped in backticks, got: {type_value}"))
            is_start_node = "开始" in type_value
            is_end_node = "结束" in type_value

        for sec_name in ("输入", "输出"):
            window = _extract_section_window(section, sec_name)
            if is_start_node and sec_name == "输出":
                if window is not None:
                    findings.append(
                        Finding(
                            "WARN",
                            f"{node_id}: start node should only declare '**输入**' variables (remove '**输出**' section)",
                        )
                    )
                continue
            if is_end_node and sec_name == "输入":
                if window is not None:
                    findings.append(
                        Finding(
                            "WARN",
                            f"{node_id}: end node should only declare '**输出**' variables (remove '**输入**' section)",
                        )
                    )
                continue
            if window is None:
                findings.append(
                    Finding("WARN", f"{node_id}: missing '**{sec_name}**' section (allowing suffixes like 输入（...）)")
                )
                continue

            bullet_lines = [ln for ln in window.splitlines() if VAR_BULLET_RE.match(ln)]
            if not bullet_lines:
                if "`" in window:
                    findings.append(
                        Finding(
                            "ERROR",
                            f"{node_id}: '{sec_name}' section must use variable bullet lines like: - `var`（type ...）：comment",
                        )
                    )
                else:
                    findings.append(Finding("WARN", f"{node_id}: '{sec_name}' section has no variable bullets like - `var`（...）：..."))
                continue

            for ln in bullet_lines:
                var_name, type_str, comment_str = _parse_var_bullet(ln)
                if not var_name:
                    continue
                if var_name == "none":
                    continue

                if type_str is None:
                    findings.append(Finding("ERROR", f"{node_id}: `{var_name}` in '{sec_name}' is missing a type in parentheses"))
                if comment_str is None:
                    findings.append(
                        Finding("ERROR", f"{node_id}: `{var_name}` in '{sec_name}' is missing a comment after ':' / '：'")
                    )

                if sec_name == "输入":
                    if not _input_has_source(ln):
                        findings.append(
                            Finding(
                                "ERROR",
                                f"{node_id}: `{var_name}` input is missing source (require '← 来自…' or '来源：…')",
                            )
                        )

        if re.search(r"\*\*Prompt", section):
            if "```markdown" not in section:
                findings.append(Finding("ERROR", f"{node_id}: prompt section exists but no ```markdown fenced block found"))

    return findings


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] in {"-h", "--help"}:
        print("Usage: validate_blueprint_md.py <path-to-workflow.blueprint.md>", file=sys.stderr)
        return 2

    path = Path(argv[1]).expanduser()
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    text = _read_text(path)
    findings = validate(text)

    errors = [f for f in findings if f.level == "ERROR"]
    warns = [f for f in findings if f.level == "WARN"]

    for f in errors + warns:
        print(f"{f.level}: {f.message}")

    if errors:
        print(f"\nFAIL: {len(errors)} error(s), {len(warns)} warning(s)")
        return 1

    print(f"OK: {len(warns)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
