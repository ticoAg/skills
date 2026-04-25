#!/usr/bin/env python3
"""
Append a structured runtime learning entry to references/runtime-learnings.md.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None


def build_entry(date_text: str, title: str, signal: str, action: str, promote_to: str | None, source: str | None) -> str:
    lines = [
        f"## {date_text} — {title.strip()}",
        "",
        f"- Signal: {signal.strip()}",
        f"- Action: {action.strip()}",
    ]
    if promote_to and promote_to.strip():
        lines.append(f"- Promote to: `{promote_to.strip()}`")
    if source and source.strip():
        lines.append(f"- Source: `{source.strip()}`")
    lines.append("")
    return "\n".join(lines)


def insert_after_intro(existing: str, entry: str) -> str:
    stripped = existing.rstrip()
    if not stripped:
        return entry

    marker = "Prefer `scripts/capture_runtime_learning.py` to append new entries so formatting stays consistent."
    if marker in stripped:
        head, tail = stripped.split(marker, 1)
        return f"{head}{marker}\n\n{entry}{tail.lstrip()}\n"

    return f"{stripped}\n\n{entry}"


class FileLock:
    def __init__(self, lock_path: Path):
        self.lock_path = lock_path
        self.handle = None

    def __enter__(self) -> "FileLock":
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.lock_path.open("w", encoding="utf-8")
        if fcntl is not None:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.handle is None:
            return
        if fcntl is not None:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        self.handle.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a runtime learning entry to the skill log.")
    parser.add_argument("--title", required=True, help="Short title for the learning.")
    parser.add_argument("--signal", required=True, help="What happened or what the user corrected.")
    parser.add_argument("--action", required=True, help="What was changed or should now be default behavior.")
    parser.add_argument("--promote-to", help="Stable target to update or monitor, such as SKILL.md or a reference file.")
    parser.add_argument("--source", help="Optional source marker such as a task id, date, or command path.")
    parser.add_argument("--date", help="Override date in YYYY-MM-DD format. Defaults to today.")
    parser.add_argument("--log-file", help="Override the log file path. Defaults to references/runtime-learnings.md next to this script.")
    parser.add_argument("--dry-run", action="store_true", help="Print the entry without writing.")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    default_log = script_dir.parent / "references" / "runtime-learnings.md"
    log_file = Path(args.log_file).expanduser().resolve() if args.log_file else default_log
    date_text = args.date or datetime.now().strftime("%Y-%m-%d")

    entry = build_entry(date_text, args.title, args.signal, args.action, args.promote_to, args.source)

    if args.dry_run:
        sys.stdout.write(entry)
        if not entry.endswith("\n"):
            sys.stdout.write("\n")
        return 0

    lock_path = log_file.with_name(f"{log_file.name}.lock")
    with FileLock(lock_path):
        existing = log_file.read_text(encoding="utf-8") if log_file.exists() else ""
        updated = insert_after_intro(existing, entry)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.write_text(updated, encoding="utf-8")
    print(f"Appended runtime learning to {log_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
