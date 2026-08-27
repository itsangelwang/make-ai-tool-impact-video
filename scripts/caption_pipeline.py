#!/usr/bin/env python3
"""Create phrase-level caption cues from final narration and measured duration."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from safe_io import atomic_write_json


def phrases(text: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"(?<=[，。！？；：,.!?;:])", text) if p.strip()]
    return parts or [text.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, type=Path)
    parser.add_argument("--duration-ms", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.duration_ms <= 0:
        raise SystemExit("duration-ms must be positive")
    package = json.loads(args.script.read_text(encoding="utf-8"))
    language = str(package.get("language", "zh-CN"))
    chunks = phrases(package["narration"])
    if language.startswith("en"):
        weights = [max(1, len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b", chunk))) for chunk in chunks]
    else:
        weights = [max(1, len(re.findall(r"[\u3400-\u9fffA-Za-z0-9]", chunk))) for chunk in chunks]
    total = sum(weights)
    cues, cursor = [], 0
    for index, (chunk, weight) in enumerate(zip(chunks, weights)):
        end = args.duration_ms if index == len(chunks) - 1 else round(cursor + args.duration_ms * weight / total)
        cues.append({"text": chunk, "startMs": cursor, "endMs": end, "language": language})
        cursor = end
    atomic_write_json(args.output, cues)
    print(json.dumps({"ok": True, "cues": len(cues), "duration_ms": args.duration_ms}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
