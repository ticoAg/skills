#!/usr/bin/env python3
"""
Archive stale feature notes under .feat/.

We treat a notes directory as "stale" when its most recently modified file is older than
the threshold (default: 12 hours). Stale directories are moved to:
  .feat/_archive/<original-dir-name>/

This keeps the active .feat/ directory tidy without deleting anything.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import time
from pathlib import Path


_TS_PREFIX_RE = re.compile(r"^\d{8}-\d{4}-")


def _newest_mtime(path: Path) -> float:
    newest = path.stat().st_mtime
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                newest = max(newest, (Path(root) / name).stat().st_mtime)
            except FileNotFoundError:
                # File disappeared mid-walk; ignore and continue.
                continue
    return newest


def _iter_note_dirs(feat_dir: Path) -> list[Path]:
    if not feat_dir.exists():
        return []
    if not feat_dir.is_dir():
        return []
    out: list[Path] = []
    for child in feat_dir.iterdir():
        if child.name == "_archive":
            continue
        if not child.is_dir():
            continue
        # Only archive directories created by our convention.
        if not _TS_PREFIX_RE.match(child.name):
            continue
        out.append(child)
    return sorted(out, key=lambda p: p.name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive stale .feat note directories.")
    parser.add_argument("--feat-dir", required=True, help="Path to .feat directory")
    parser.add_argument(
        "--threshold-hours",
        type=float,
        default=12.0,
        help="Archive dirs older than this many hours since last modification (default: 12)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without moving")
    args = parser.parse_args()

    feat_dir = Path(args.feat_dir).expanduser().resolve()
    archive_dir = feat_dir / "_archive"
    threshold_s = float(args.threshold_hours) * 3600.0
    now = time.time()

    note_dirs = _iter_note_dirs(feat_dir)
    if not note_dirs:
        return 0

    moved = 0
    skipped = 0
    for d in note_dirs:
        try:
            newest = _newest_mtime(d)
        except FileNotFoundError:
            skipped += 1
            continue

        age_s = now - newest
        if age_s <= threshold_s:
            continue

        dest = archive_dir / d.name
        if dest.exists():
            print(f"[SKIP] 已存在归档目录：{dest}")
            skipped += 1
            continue

        if args.dry_run:
            print(f"[DRY] mv {d} -> {dest}")
        else:
            archive_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(d), str(dest))
            print(f"[OK] 已归档：{d} -> {dest}")
        moved += 1

    if moved > 0:
        print(
            f"[OK] 自动归档完成：moved={moved} skipped={skipped} threshold={args.threshold_hours}h"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        sys.stderr.write("\n[ERROR] Interrupted.\n")
        raise SystemExit(130)

