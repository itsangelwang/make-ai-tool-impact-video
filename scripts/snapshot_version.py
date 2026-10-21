#!/usr/bin/env python3
"""Save the current editable project files as versions/vN before a revision."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

# Small editable inputs only; renders, audio, and node_modules stay out.
FILES = ("script-package.json", "claim-ledger.json", "source-ledger.json", "audio-events.json", "social-titles.md")
VIDEO_SRC_SUFFIXES = {".json", ".jsx", ".js", ".ts", ".tsx", ".css"}


def next_version(versions: Path) -> int:
    numbers = [int(m.group(1)) for p in versions.glob("v*") if (m := re.fullmatch(r"v(\d+)", p.name))]
    return max(numbers, default=0) + 1


def snapshot(project: Path, note: str | None = None) -> tuple[Path, list[str]]:
    project = project.expanduser().resolve()
    versions = project / "versions"
    if versions.is_symlink():
        raise SystemExit("Refusing to use a symbolic link as the versions directory")
    target = versions / f"v{next_version(versions)}"
    target.mkdir(parents=True)
    copied = []
    for name in FILES:
        source = project / name
        if source.is_file() and not source.is_symlink():
            shutil.copy2(source, target / name)
            copied.append(name)
    src = project / "video" / "src"
    if src.is_dir():
        for source in sorted(src.rglob("*")):
            if source.is_file() and not source.is_symlink() and source.suffix in VIDEO_SRC_SUFFIXES:
                relative = source.relative_to(project)
                (target / relative).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target / relative)
                copied.append(str(relative))
    if note:
        (target / "NOTE.txt").write_text(note.strip() + "\n", encoding="utf-8")
    return target, copied


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--note", help="one line on what this version was, e.g. 'v3 review: user asked for slower opening'")
    args = parser.parse_args()
    target, copied = snapshot(args.project, args.note)
    print(json.dumps({"ok": True, "version": target.name, "files": len(copied)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
