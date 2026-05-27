#!/usr/bin/env python3
"""Fail if any source file exceeds a line limit (default 800).

Enforces the project rule that files stay small and modular. Pure standard
library so it runs anywhere: Windows, WSL2, the Pi, or CI.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_LIMIT = 800
SOURCE_SUFFIXES = {".py", ".cpp", ".hpp", ".cc", ".c", ".h"}
SKIP_DIRS = {"build", "install", "log", "__pycache__", ".git", ".pytest_cache"}


def iter_source_files(root: Path) -> list[Path]:
    """Return source files under ``root``, skipping build and VCS directories."""
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix in SOURCE_SUFFIXES:
            files.append(path)
    return files


def count_lines(path: Path) -> int:
    """Return the number of lines in ``path``."""
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for _ in handle)


def find_violations(root: Path, limit: int) -> list[tuple[Path, int]]:
    """Return ``(path, line_count)`` for every file exceeding ``limit``."""
    violations: list[tuple[Path, int]] = []
    for path in iter_source_files(root):
        line_count = count_lines(path)
        if line_count > limit:
            violations.append((path, line_count))
    return violations


def main(argv: list[str] | None = None) -> int:
    """Print any violations and return non-zero if at least one is found."""
    parser = argparse.ArgumentParser(
        description="Check that source files stay under a line limit."
    )
    parser.add_argument("root", nargs="?", default=".", help="Directory to scan.")
    parser.add_argument(
        "--limit", type=int, default=DEFAULT_LIMIT, help="Maximum lines per file."
    )
    args = parser.parse_args(argv)

    violations = find_violations(Path(args.root), args.limit)
    if violations:
        print(f"FAIL: {len(violations)} file(s) exceed {args.limit} lines:")
        for path, line_count in violations:
            print(f"  {path} ({line_count} lines)")
        return 1
    print(f"OK: all source files are within {args.limit} lines.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
