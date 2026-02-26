#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


BEGIN_MARKER = "<!-- TODO_SYNC:BEGIN -->"
END_MARKER = "<!-- TODO_SYNC:END -->"
ENV_NOTES_DIR = "FEAT_WT_NOTES_DIR"
DEFAULT_VIEW_LINES = 80


@dataclass(frozen=True)
class WorkflowStatus:
    kickoff_done: bool
    vfinal_done: bool
    context_done: bool
    delivery_done: bool


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _has_trailing_newline(text: str) -> bool:
    return bool(text) and text.endswith("\n")


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _split_lines(text: str) -> list[str]:
    text = _normalize_newlines(text)
    return text.split("\n")


def _join_lines(lines: list[str], trailing_newline: bool) -> str:
    content = "\n".join(lines)
    if trailing_newline and not content.endswith("\n"):
        content += "\n"
    if not trailing_newline and content.endswith("\n"):
        content = content[:-1]
    return content


def _workflow_block(status: WorkflowStatus) -> list[str]:
    def box(done: bool) -> str:
        return "[x]" if done else "[ ]"

    return [
        BEGIN_MARKER,
        "## Workflow TODO（自动同步）",
        f"- {box(status.kickoff_done)} Kickoff 已完成（分支/worktree/notes 初始化）",
        f"- {box(status.vfinal_done)} vFinal 已确认（requirements.md 存在 `## vFinal - YYYY-MM-DD`）",
        f"- {box(status.context_done)} Context 已补齐（context.md 无 TODO 且包含 `path:line`）",
        f"- {box(status.delivery_done)} Delivery 已补齐（delivery.md 无 TODO）",
        END_MARKER,
    ]


def _find_block(lines: list[str]) -> tuple[int, int] | None:
    begin_idx = None
    for idx, line in enumerate(lines):
        if line.strip() == BEGIN_MARKER:
            begin_idx = idx
            break
    if begin_idx is None:
        return None

    for idx in range(begin_idx + 1, len(lines)):
        if lines[idx].strip() == END_MARKER:
            return (begin_idx, idx)
    return None


def _insert_after_status_section(lines: list[str], block_lines: list[str]) -> list[str]:
    status_idx = None
    for idx, line in enumerate(lines):
        if line.strip() == "## Status":
            status_idx = idx
            break

    if status_idx is not None:
        insert_at = len(lines)
        for idx in range(status_idx + 1, len(lines)):
            if lines[idx].startswith("## "):
                insert_at = idx
                break
        return lines[:insert_at] + block_lines + lines[insert_at:]

    h1_idx = None
    for idx, line in enumerate(lines):
        if line.startswith("# "):
            h1_idx = idx
            break
    if h1_idx is not None:
        insert_at = h1_idx + 1
        while insert_at < len(lines) and lines[insert_at].strip() != "":
            insert_at += 1
        while insert_at < len(lines) and lines[insert_at].strip() == "":
            insert_at += 1
        return lines[:insert_at] + block_lines + lines[insert_at:]

    return lines + [""] + block_lines


def _upsert_workflow_block(
    requirements_text: str,
    status: WorkflowStatus,
) -> tuple[str, bool]:
    trailing_newline = _has_trailing_newline(requirements_text)
    lines = _split_lines(requirements_text)
    block = _find_block(lines)

    block_lines = _workflow_block(status)
    if block is None:
        new_lines = _insert_after_status_section(lines, block_lines)
        new_lines = _normalize_blank_lines_after_workflow_block(new_lines)
        new_text = _join_lines(new_lines, trailing_newline)
        return new_text, new_text != requirements_text

    begin_idx, end_idx = block
    new_lines = lines[:begin_idx] + block_lines + lines[end_idx + 1 :]
    new_lines = _normalize_blank_lines_after_workflow_block(new_lines)
    new_text = _join_lines(new_lines, trailing_newline)
    return new_text, new_text != requirements_text


def _normalize_blank_lines_after_workflow_block(lines: list[str]) -> list[str]:
    # Ensure there is exactly 1 blank line after END_MARKER.
    end_idx = None
    for idx, line in enumerate(lines):
        if line.strip() == END_MARKER:
            end_idx = idx
            break
    if end_idx is None:
        return lines

    i = end_idx + 1
    blank_count = 0
    while i + blank_count < len(lines) and lines[i + blank_count].strip() == "":
        blank_count += 1

    new_lines = list(lines)
    if blank_count == 0:
        new_lines.insert(i, "")
        return new_lines

    # Remove extra blanks (keep exactly one).
    for _ in range(blank_count - 1):
        del new_lines[i + 1]
    return new_lines


def _doc_is_filled(path: Path) -> bool:
    if not path.exists():
        return False
    text = _read_text(path)
    if re.search(r"\bTODO\b", text):
        return False
    return True


def _context_has_evidence(path: Path) -> bool:
    if not path.exists():
        return False
    text = _read_text(path)
    for line in _normalize_newlines(text).split("\n"):
        if "http://" in line or "https://" in line:
            continue
        # Accept evidence inside backticks or parentheses too (not only whitespace-delimited).
        if re.search(r"(?:\./)?[\w./-]+:\d+(?::\d+)?\b", line):
            return True
    return False


def _detect_workflow_status(notes_dir: Path) -> WorkflowStatus:
    requirements_path = notes_dir / "requirements.md"
    context_path = notes_dir / "context.md"
    delivery_path = notes_dir / "delivery.md"

    kickoff_done = notes_dir.is_dir() and requirements_path.exists()
    vfinal_done = False
    if requirements_path.exists():
        req_text = _read_text(requirements_path)
        vfinal_done = (
            re.search(r"(?m)^##\s+vFinal\s+-\s+\d{4}-\d{2}-\d{2}\b", req_text) is not None
        )

    context_done = _doc_is_filled(context_path) and _context_has_evidence(context_path)
    delivery_done = _doc_is_filled(delivery_path)

    return WorkflowStatus(
        kickoff_done=kickoff_done,
        vfinal_done=vfinal_done,
        context_done=context_done,
        delivery_done=delivery_done,
    )


def _run_git(repo_root: Path | None, args: list[str]) -> str:
    cmd = ["git", *args]
    try:
        p = subprocess.run(
            cmd,
            cwd=str(repo_root) if repo_root else None,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as e:
        raise RuntimeError("未找到 git；请先安装 git。") from e
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        raise RuntimeError(f"git 命令失败：{' '.join(cmd)}\n{stderr}") from e
    return (p.stdout or "").strip()


def _get_repo_root() -> Path:
    out = _run_git(None, ["rev-parse", "--show-toplevel"])
    return Path(out).expanduser().resolve()


def _get_current_branch(repo_root: Path) -> str:
    return _run_git(repo_root, ["branch", "--show-current"])


def _fmt_mtime(ts: float) -> str:
    t = dt.datetime.fromtimestamp(ts)
    return t.strftime("%Y-%m-%d %H:%M")


def _list_notes_dirs(repo_root: Path) -> list[Path]:
    feat_dir = repo_root / ".feat"
    if not feat_dir.exists():
        return []
    out: list[Path] = []
    for child in feat_dir.iterdir():
        if not child.is_dir():
            continue
        if child.name == "_archive":
            continue
        out.append(child)
    out.sort(key=lambda p: p.name)
    return out


def _extract_slug_from_branch(branch: str) -> str | None:
    m = re.fullmatch(r"feat/([a-z0-9]+(?:[a-z0-9-]*[a-z0-9])?)", branch.strip())
    return m.group(1) if m else None


def _select_notes_for_slug(notes_dirs: list[Path], slug: str) -> Path | None:
    pat = re.compile(rf"^\d{{8}}-\d{{4}}-{re.escape(slug)}$")
    matches = [p for p in notes_dirs if pat.match(p.name)]
    if not matches:
        return None
    matches.sort(key=lambda p: p.name)
    return matches[-1]


def _resolve_notes_dir(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()

    env_value = os.environ.get(ENV_NOTES_DIR, "").strip()
    if env_value:
        return Path(env_value).expanduser().resolve()

    repo_root = _get_repo_root()
    notes_dirs = _list_notes_dirs(repo_root)
    branch = _get_current_branch(repo_root)
    slug = _extract_slug_from_branch(branch)
    if slug:
        selected = _select_notes_for_slug(notes_dirs, slug)
        if selected:
            return selected.resolve()

    if len(notes_dirs) == 1:
        return notes_dirs[0].resolve()

    raise RuntimeError(
        "无法唯一定位 notes 目录；请先运行 `feat-wt notes list`，"
        f"或通过环境变量指定：export {ENV_NOTES_DIR}=\".../.feat/<notes>\"，"
        "或在命令中显式传入 --notes-dir。",
    )


def _ensure_notes_dir(notes_dir: Path) -> None:
    if not notes_dir.exists() or not notes_dir.is_dir():
        raise RuntimeError(f"notes 目录不存在：{notes_dir}")


def _get_requirements_path(notes_dir: Path, file: str | None) -> Path:
    return Path(file).expanduser().resolve() if file else (notes_dir / "requirements.md")


def cmd_todo_sync(args: argparse.Namespace) -> int:
    try:
        notes_dir = _resolve_notes_dir(args.notes_dir)
        _ensure_notes_dir(notes_dir)
        requirements_path = _get_requirements_path(notes_dir, args.file)
        if not requirements_path.exists():
            raise RuntimeError(f"未找到 requirements.md：{requirements_path}")
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2

    status = _detect_workflow_status(notes_dir)
    original = _read_text(requirements_path)
    updated, changed = _upsert_workflow_block(original, status)

    if changed and args.dry_run:
        if not args.quiet:
            print(f"[DRY-RUN] 将更新：{requirements_path}")
        return 0
    if changed:
        _write_text(requirements_path, updated)
        if not args.quiet:
            print(f"[OK] 已同步 TODO：{requirements_path}")
    else:
        if not args.quiet:
            print(f"[OK] TODO 已是最新：{requirements_path}")
    return 0


def _update_checklist_line(line: str, done: bool) -> str:
    m = re.match(r"^(\s*-\s*\[)([ xX])(\]\s+)(.*)$", line)
    if not m:
        return line
    prefix, _, mid, rest = m.groups()
    return f"{prefix}{'x' if done else ' '}{mid}{rest}"


def _resolve_target_file_for_todo(notes_dir: Path, file: str | None) -> Path:
    if file:
        return Path(file).expanduser().resolve()
    return notes_dir / "requirements.md"


def _sync_workflow_todo_if_requirements(notes_dir: Path, *, path: Path, quiet: bool) -> None:
    """
    当目标文件为 notes_dir/requirements.md 时，自动同步 Workflow TODO 区块。

    设计目标：
    - 用户完成/取消某条 checklist 后，不用再额外手动执行 `feat-wt todo sync`；
    - 同步是 best-effort：失败仅提示，不影响 checklist 更新结果。
    """

    requirements_path = (notes_dir / "requirements.md").resolve()
    if path.resolve() != requirements_path:
        return

    try:
        status = _detect_workflow_status(notes_dir)
        original = _read_text(requirements_path)
        updated, changed = _upsert_workflow_block(original, status)
        if changed:
            _write_text(requirements_path, updated)
            if not quiet:
                print(f"[OK] 已同步 Workflow TODO：{requirements_path}")
    except Exception as exc:  # noqa: BLE001
        if not quiet:
            print(f"[WARN] Workflow TODO 同步失败（已忽略）：{exc}", file=sys.stderr)


def cmd_todo_set(args: argparse.Namespace) -> int:
    try:
        if not (args.done ^ args.undone):
            raise RuntimeError("需要二选一：--done 或 --undone")
        if not args.contains:
            raise RuntimeError("必须传入 --contains 用于匹配 checklist 条目文本")
        notes_dir = _resolve_notes_dir(args.notes_dir)
        _ensure_notes_dir(notes_dir)
        path = _resolve_target_file_for_todo(notes_dir, args.file)
        if not path.exists():
            raise RuntimeError(f"未找到文件：{path}")
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2

    needle = str(args.contains)
    original = _read_text(path)
    trailing_newline = _has_trailing_newline(original)
    lines = _split_lines(original)

    matched_indices: list[int] = []
    for idx, line in enumerate(lines):
        if re.match(r"^\s*-\s*\[[ xX]\]\s+", line) and needle in line:
            matched_indices.append(idx)

    if not matched_indices:
        print(f"[ERROR] 未匹配到 checklist：contains={args.contains}", file=sys.stderr)
        return 3

    if len(matched_indices) > 1 and not args.all:
        print(
            f"[ERROR] 命中多条（{len(matched_indices)}）；请更精确 contains，或加 --all 批量更新。",
            file=sys.stderr,
        )
        return 4

    target_indices = matched_indices if args.all else [matched_indices[0]]
    new_lines = list(lines)
    for idx in target_indices:
        new_lines[idx] = _update_checklist_line(new_lines[idx], done=args.done)

    updated = _join_lines(new_lines, trailing_newline)
    changed = updated != original

    if changed and args.dry_run:
        print(f"[DRY-RUN] 将更新：{path}")
        return 0
    if changed:
        _write_text(path, updated)
        print(f"[OK] 已更新 checklist：{path}")
        _sync_workflow_todo_if_requirements(notes_dir, path=path, quiet=False)
    else:
        print(f"[OK] checklist 无需更新：{path}")
    return 0


def _find_workflow_range(lines: list[str]) -> tuple[int, int] | None:
    begin = None
    end = None
    for idx, line in enumerate(lines):
        if line.strip() == BEGIN_MARKER:
            begin = idx
            continue
        if begin is not None and line.strip() == END_MARKER:
            end = idx
            break
    if begin is None or end is None:
        return None
    return (begin, end)


def _line_no_in_range(line_no: int, r: tuple[int, int] | None) -> bool:
    if r is None:
        return False
    begin, end = r
    idx = line_no - 1
    return begin <= idx <= end


def cmd_todo_list(args: argparse.Namespace) -> int:
    try:
        notes_dir = _resolve_notes_dir(args.notes_dir)
        _ensure_notes_dir(notes_dir)
        req_path = notes_dir / "requirements.md"
        if not req_path.exists():
            raise RuntimeError(f"未找到 requirements.md：{req_path}")
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2

    lines = _split_lines(_read_text(req_path))
    workflow_range = _find_workflow_range(lines)

    for idx, line in enumerate(lines):
        line_no = idx + 1
        if (not args.include_workflow) and _line_no_in_range(line_no, workflow_range):
            continue
        m = re.match(r"^\s*-\s*\[([ xX])\]\s+(.*)$", line)
        if not m:
            continue
        checked = m.group(1).lower() == "x"
        text = m.group(2).strip()
        if (not args.all) and checked:
            continue
        box = "[x]" if checked else "[ ]"
        print(f"{line_no}\t{box}\t{text}")
    return 0


def _toggle_done_by_line_no(
    req_path: Path,
    line_no: int,
    done: bool,
    *,
    allow_workflow: bool,
) -> bool:
    original = _read_text(req_path)
    trailing_newline = _has_trailing_newline(original)
    lines = _split_lines(original)

    if line_no < 1 or line_no > len(lines):
        raise RuntimeError(f"行号超出范围：{line_no}（文件共 {len(lines)} 行）")

    workflow_range = _find_workflow_range(lines)
    if (not allow_workflow) and _line_no_in_range(line_no, workflow_range):
        raise RuntimeError("目标行位于自动同步区块；默认禁止手工修改。需要时请加 --allow-workflow。")

    idx = line_no - 1
    before = lines[idx]
    if not re.match(r"^\s*-\s*\[[ xX]\]\s+", before):
        raise RuntimeError(f"目标行不是 checklist（- [ ] / - [x]）：{line_no}")

    lines[idx] = _update_checklist_line(before, done=done)
    updated = _join_lines(lines, trailing_newline)
    if updated == original:
        return False
    _write_text(req_path, updated)
    return True


def cmd_todo_done(args: argparse.Namespace) -> int:
    try:
        notes_dir = _resolve_notes_dir(args.notes_dir)
        _ensure_notes_dir(notes_dir)
        req_path = notes_dir / "requirements.md"
        if not req_path.exists():
            raise RuntimeError(f"未找到 requirements.md：{req_path}")
        changed = _toggle_done_by_line_no(
            req_path,
            int(args.line_no),
            done=True,
            allow_workflow=bool(args.allow_workflow),
        )
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2
    print(f"[OK] 已标记完成：{req_path}:{args.line_no}" if changed else f"[OK] 无需更新：{req_path}:{args.line_no}")
    _sync_workflow_todo_if_requirements(notes_dir, path=req_path, quiet=True)
    return 0


def cmd_todo_undone(args: argparse.Namespace) -> int:
    try:
        notes_dir = _resolve_notes_dir(args.notes_dir)
        _ensure_notes_dir(notes_dir)
        req_path = notes_dir / "requirements.md"
        if not req_path.exists():
            raise RuntimeError(f"未找到 requirements.md：{req_path}")
        changed = _toggle_done_by_line_no(
            req_path,
            int(args.line_no),
            done=False,
            allow_workflow=bool(args.allow_workflow),
        )
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2
    print(f"[OK] 已取消完成：{req_path}:{args.line_no}" if changed else f"[OK] 无需更新：{req_path}:{args.line_no}")
    _sync_workflow_todo_if_requirements(notes_dir, path=req_path, quiet=True)
    return 0


def cmd_notes_list(args: argparse.Namespace) -> int:
    try:
        repo_root = _get_repo_root()
        notes_dirs = _list_notes_dirs(repo_root)
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2

    resolved: Path | None = None
    try:
        resolved = _resolve_notes_dir(None)
    except Exception:
        resolved = None

    for idx, p in enumerate(notes_dirs, start=1):
        slug = ""
        m = re.match(r"^\d{8}-\d{4}-(.+)$", p.name)
        if m:
            slug = m.group(1)
        mark = "*" if resolved and p.resolve() == resolved else " "
        print(f"{mark}{idx}\t{p.name}\t{_fmt_mtime(p.stat().st_mtime)}\t{slug}")
    if not notes_dirs:
        print("[INFO] 未找到任何 notes：当前 repo 下没有 .feat/<timestamp>-<slug> 目录。", file=sys.stderr)
    return 0


def cmd_notes_show(args: argparse.Namespace) -> int:
    try:
        notes_dir = _resolve_notes_dir(args.notes_dir)
        _ensure_notes_dir(notes_dir)
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2
    print(str(notes_dir))
    return 0


def cmd_notes_pick(args: argparse.Namespace) -> int:
    try:
        repo_root = _get_repo_root()
        notes_dirs = _list_notes_dirs(repo_root)
        if not notes_dirs:
            raise RuntimeError("当前 repo 下未找到任何 notes（.feat/<timestamp>-<slug>）。")
        idx = int(args.idx)
        if idx < 1 or idx > len(notes_dirs):
            raise RuntimeError(f"idx 超出范围：{idx}（可选 1..{len(notes_dirs)}）")
        picked = notes_dirs[idx - 1].resolve()
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2
    print(f"export {ENV_NOTES_DIR}=\"{picked}\"")
    print(f"# 已选择 notes：{picked.name}", file=sys.stdout)
    return 0


def _print_preview(path: Path, lines: int | None, full: bool) -> None:
    print(f"[INFO] 文件：{path}")
    text = _read_text(path)
    if full:
        print(text, end="" if text.endswith("\n") else "\n")
        return
    n = lines if lines is not None else DEFAULT_VIEW_LINES
    out_lines = _split_lines(text)[:n]
    print("\n".join(out_lines))


def cmd_doc_view(args: argparse.Namespace) -> int:
    try:
        notes_dir = _resolve_notes_dir(args.notes_dir)
        _ensure_notes_dir(notes_dir)
        path = notes_dir / args.filename
        if not path.exists():
            raise RuntimeError(f"未找到文件：{path}")
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2
    _print_preview(path, lines=args.lines, full=bool(args.full))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="feat-wt",
        description="feat-wt：本地 feature notes（.feat/...）的检查与 TODO 更新工具（严格模式：<资源> <行为>）。",
    )
    resources = parser.add_subparsers(dest="resource", required=True)

    # notes
    p_notes = resources.add_parser("notes", help="notes 目录操作（列出/选择/显示）")
    notes_actions = p_notes.add_subparsers(dest="action", required=True)

    p_notes_list = notes_actions.add_parser("list", help="列出当前 repo 下所有 notes（.feat/<timestamp>-<slug>）")
    p_notes_list.set_defaults(func=cmd_notes_list)

    p_notes_show = notes_actions.add_parser("show", help="显示当前选择/自动定位到的 notes 目录")
    p_notes_show.add_argument("--notes-dir", help="显式指定 notes 目录（可选）。")
    p_notes_show.set_defaults(func=cmd_notes_show)

    p_notes_pick = notes_actions.add_parser("pick", help=f"选择一个 notes（输出 export {ENV_NOTES_DIR}=...）")
    p_notes_pick.add_argument("idx", help="notes 索引（来自 `feat-wt notes list` 的 idx）。")
    p_notes_pick.set_defaults(func=cmd_notes_pick)

    # todo
    p_todo = resources.add_parser("todo", help="requirements.md 的 TODO/checklist 操作")
    todo_actions = p_todo.add_subparsers(dest="action", required=True)

    p_todo_list = todo_actions.add_parser("list", help="列出 checklist（默认只列未完成项）")
    p_todo_list.add_argument("--notes-dir", help="显式指定 notes 目录（可选）。")
    p_todo_list.add_argument("--all", action="store_true", help="包含已完成项（[x]）。")
    p_todo_list.add_argument("--include-workflow", action="store_true", help="包含自动同步区块（默认不包含）。")
    p_todo_list.set_defaults(func=cmd_todo_list)

    p_todo_done = todo_actions.add_parser("done", help="按行号标记完成（[x]）")
    p_todo_done.add_argument("--notes-dir", help="显式指定 notes 目录（可选）。")
    p_todo_done.add_argument("line_no", help="requirements.md 行号（来自 `feat-wt todo list` 输出）。")
    p_todo_done.add_argument("--allow-workflow", action="store_true", help="允许修改自动同步区块内的 checklist。")
    p_todo_done.set_defaults(func=cmd_todo_done)

    p_todo_complete = todo_actions.add_parser("complete", help="按行号标记完成（[x]）（同 done）")
    p_todo_complete.add_argument("--notes-dir", help="显式指定 notes 目录（可选）。")
    p_todo_complete.add_argument("line_no", help="requirements.md 行号（来自 `feat-wt todo list` 输出）。")
    p_todo_complete.add_argument("--allow-workflow", action="store_true", help="允许修改自动同步区块内的 checklist。")
    p_todo_complete.set_defaults(func=cmd_todo_done)

    p_todo_undone = todo_actions.add_parser("undone", help="按行号取消完成（[ ]）")
    p_todo_undone.add_argument("--notes-dir", help="显式指定 notes 目录（可选）。")
    p_todo_undone.add_argument("line_no", help="requirements.md 行号（来自 `feat-wt todo list` 输出）。")
    p_todo_undone.add_argument("--allow-workflow", action="store_true", help="允许修改自动同步区块内的 checklist。")
    p_todo_undone.set_defaults(func=cmd_todo_undone)

    p_todo_uncomplete = todo_actions.add_parser("uncomplete", help="按行号取消完成（[ ]）（同 undone）")
    p_todo_uncomplete.add_argument("--notes-dir", help="显式指定 notes 目录（可选）。")
    p_todo_uncomplete.add_argument("line_no", help="requirements.md 行号（来自 `feat-wt todo list` 输出）。")
    p_todo_uncomplete.add_argument("--allow-workflow", action="store_true", help="允许修改自动同步区块内的 checklist。")
    p_todo_uncomplete.set_defaults(func=cmd_todo_undone)

    p_todo_sync = todo_actions.add_parser("sync", help="同步 Workflow TODO（自动同步区块）")
    p_todo_sync.add_argument("--notes-dir", help="显式指定 notes 目录（可选）。")
    p_todo_sync.add_argument("--file", help="直接指定 requirements.md 路径（高级用法）。")
    p_todo_sync.add_argument("--dry-run", action="store_true", help="只输出将要变更，不写入。")
    p_todo_sync.add_argument("--quiet", action="store_true", help="减少输出（适合脚本调用）。")
    p_todo_sync.set_defaults(func=cmd_todo_sync)

    p_todo_set = todo_actions.add_parser("set", help="按文本匹配勾选/取消勾选 checklist（高级）")
    p_todo_set.add_argument("--notes-dir", help="显式指定 notes 目录（可选）。")
    p_todo_set.add_argument("--file", help="要更新的 Markdown 文件路径（默认 requirements.md）。")
    p_todo_set.add_argument("--contains", required=True, help="要匹配的 checklist 行子串。")
    p_todo_set.add_argument("--done", action="store_true", help="标记为已完成（[x]）。")
    p_todo_set.add_argument("--undone", action="store_true", help="标记为未完成（[ ]）。")
    p_todo_set.add_argument("--all", action="store_true", help="批量更新所有命中的项（默认只更新第一条）。")
    p_todo_set.add_argument("--dry-run", action="store_true", help="只输出将要变更，不写入。")
    p_todo_set.set_defaults(func=cmd_todo_set)

    # docs: req/ctx/del/dis view
    def add_doc_resource(name: str, filename: str, help_text: str) -> None:
        p = resources.add_parser(name, help=help_text)
        actions = p.add_subparsers(dest="action", required=True)
        v = actions.add_parser("view", help="查看文档（默认仅展示前 80 行）")
        v.add_argument("--notes-dir", help="显式指定 notes 目录（可选）。")
        g = v.add_mutually_exclusive_group()
        g.add_argument("--lines", type=int, default=DEFAULT_VIEW_LINES, help="展示前 N 行（默认 80）。")
        g.add_argument("--full", action="store_true", help="展示全部内容。")
        v.set_defaults(func=cmd_doc_view, filename=filename)

    add_doc_resource("req", "requirements.md", "requirements.md 文档操作")
    add_doc_resource("ctx", "context.md", "context.md 文档操作")
    add_doc_resource("del", "delivery.md", "delivery.md 文档操作")
    add_doc_resource("dis", "disagreements.md", "disagreements.md 文档操作")

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
