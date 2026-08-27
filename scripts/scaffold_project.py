#!/usr/bin/env python3
"""Copy the bundled vertical Remotion project without overwriting work."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess  # nosec B404
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    template = Path(__file__).resolve().parent.parent / "assets" / "remotion-template"
    requested = args.output_dir.expanduser()
    if requested.is_symlink():
        raise SystemExit("Refusing to use a symbolic link as the output directory")
    output = requested.resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty directory: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, output, dirs_exist_ok=True)
    (output / "renders").mkdir(exist_ok=True)
    (output / "qa").mkdir(exist_ok=True)
    if args.install:
        npm = shutil.which("npm")
        if not npm:
            raise SystemExit("npm is required for --install")
        subprocess.run([npm, "ci"], cwd=output, check=True)  # nosec B603
    print(json.dumps({"ok": True, "output": output.name}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
