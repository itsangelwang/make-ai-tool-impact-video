#!/usr/bin/env python3
"""Copy the bundled vertical Remotion project without overwriting work."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    template = Path(__file__).resolve().parent.parent / "assets" / "remotion-template"
    output = args.output_dir.expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty directory: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, output, dirs_exist_ok=True)
    (output / "renders").mkdir(exist_ok=True)
    (output / "qa").mkdir(exist_ok=True)
    if args.install:
        subprocess.run(["npm", "ci"], cwd=output, check=True)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
