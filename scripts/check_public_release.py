#!/usr/bin/env python3
"""Fail when a release tree contains common private-project identifiers."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".toml", ".txt", ".html", ".js", ".ts"}
DENY_PATTERNS = {
    "macOS user path": re.compile(r"/Users/[^/\s'\"]+"),
    "Linux user path": re.compile(r"/home/[^/\s'\"]+"),
    "private service domain": re.compile(r"(?i)\.internal\b|\.corp\b"),
}


def findings(root: Path, deny_terms: tuple[str, ...] = ()) -> list[str]:
    issues: list[str] = []
    patterns = dict(DENY_PATTERNS)
    for index, term in enumerate(deny_terms, start=1):
        patterns[f"custom deny term {index}"] = re.compile(re.escape(term), re.IGNORECASE)
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if (
            not path.is_file()
            or ".git" in relative.parts
            or "tests" in relative.parts
            or relative == Path("scripts/check_public_release.py")
            or path.suffix.lower() not in TEXT_SUFFIXES
        ):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in patterns.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                issues.append(f"{relative}:{line}: {label}: {match.group(0)}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--deny", action="append", default=[], help="Additional private term to reject")
    args = parser.parse_args()
    issues = findings(args.root.resolve(), tuple(args.deny))
    if issues:
        print("public release check failed:", file=sys.stderr)
        print("\n".join(f"- {issue}" for issue in issues), file=sys.stderr)
        return 1
    print("public release check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
