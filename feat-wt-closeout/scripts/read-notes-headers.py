#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Tuple


def _repo_root(start: Path) -> Path:
    """Best-effort repo root discovery (works in base repo or worktree)."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            return Path(out)
    except Exception:
        pass
    return start.resolve()


def _select_notes_dir(repo_root: Path, slug: str) -> Tuple[Path, str]:
    # Prefer new layout: .feat/{YYYYMMDD-HHMM}-{slug}/
    feat_root = repo_root / ".feat"
    candidates = sorted([p for p in feat_root.glob(f"*-{slug}") if p.is_dir()])
    if candidates:
        return candidates[-1], "feat"

    # Back-compat: legacy layout
    legacy = repo_root / ".cache" / "codex" / "features" / slug
    if legacy.exists():
        return legacy, "cache"

    raise FileNotFoundError(f"notes dir not found for slug: {slug}")


def _parse_frontmatter(text: str) -> Optional[Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    end = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end = idx
            break
    if end is None:
        return None

    header_text = "\n".join(lines[1:end]).strip()
    if not header_text:
        return {}

    # Prefer PyYAML when available (more robust). Fall back to a minimal parser.
    try:
        import yaml  # type: ignore

        return yaml.safe_load(header_text)
    except Exception:
        pass

    out: dict[str, Any] = {}
    for line in header_text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or ":" not in s:
            continue
        k, v = s.split(":", 1)
        v = v.strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        out[k.strip()] = v
    return out


def _read_text_best_effort(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Read YAML frontmatter headers from all notes docs for a given feature slug."
    )
    parser.add_argument("slug", help="feature slug, e.g. sidebar-wt-branch")
    parser.add_argument(
        "--root",
        help="repo root (default: auto-detect via git); useful when running outside a repo",
        default=None,
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.root).resolve() if args.root else _repo_root(Path.cwd())

    try:
        notes_dir, mode = _select_notes_dir(repo_root, args.slug)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        print(f"        repo_root={repo_root}", file=sys.stderr)
        return 1

    files: list[dict[str, Any]] = []
    for p in sorted(notes_dir.rglob("*")):
        if not p.is_file():
            continue
        header = _parse_frontmatter(_read_text_best_effort(p))

        try:
            rel = p.relative_to(repo_root).as_posix()
        except Exception:
            rel = str(p)

        files.append({"path": rel, "header": header})

    try:
        notes_rel = notes_dir.relative_to(repo_root).as_posix()
    except Exception:
        notes_rel = str(notes_dir)

    payload = {
        "slug": args.slug,
        "notesDir": notes_rel,
        "mode": mode,
        "files": files,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

