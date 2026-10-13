#!/usr/bin/env python3
"""Build Remotion captions from the canonical narration timeline."""

from __future__ import annotations

import argparse
import json
import math
import sys
import unicodedata
from pathlib import Path

from safe_io import atomic_write_json


def normalize(text: str) -> str:
    """Ignore whitespace and Unicode punctuation, but preserve case and symbols."""
    return "".join(char for char in text if not char.isspace() and not unicodedata.category(char).startswith("P"))


def check_narration(captions: list[dict], narration: str) -> None:
    actual = normalize("".join(cue["text"] for cue in captions))
    expected = normalize(narration)
    if actual == expected:
        return
    index = next((i for i, pair in enumerate(zip(actual, expected)) if pair[0] != pair[1]), min(len(actual), len(expected)))
    got = repr(actual[index]) if index < len(actual) else "<end>"
    wanted = repr(expected[index]) if index < len(expected) else "<end>"
    raise ValueError(f"narration mismatch at normalized character {index + 1}: captions {got}, narration {wanted}")


def build_captions(timeline: dict, script: dict | None = None) -> list[dict]:
    language = timeline.get("language")
    if not isinstance(language, str) or not language.strip():
        raise ValueError("timeline language must be a non-empty string")
    cues = timeline.get("captions")
    if not isinstance(cues, list) or not cues:
        raise ValueError("timeline captions must be a non-empty list")
    result = []
    previous_end = 0
    for index, cue in enumerate(cues, 1):
        if not isinstance(cue, dict) or not isinstance(cue.get("text"), str) or not cue["text"].strip():
            raise ValueError(f"caption {index} requires non-empty text")
        times = [cue.get("start_sec"), cue.get("end_sec")]
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) for value in times):
            raise ValueError(f"caption {index} requires finite numeric start_sec and end_sec")
        start, end = times
        if start < previous_end or end <= start:
            raise ValueError(f"caption {index} has invalid or overlapping bounds")
        # 1000 is the unit conversion factor, not a configurable numeric limit.
        start_ms, end_ms = round(start * 1000), round(end * 1000)
        if end_ms <= start_ms:
            raise ValueError(f"caption {index} collapses after millisecond rounding")
        output = {"startMs": start_ms, "endMs": end_ms, "text": cue["text"], "language": language}
        for key in ("highlightCool", "highlightWarm"):
            if key in cue:
                output[key] = cue[key]
        result.append(output)
        previous_end = end
    if script is not None:
        narration = script.get("narration")
        if not isinstance(narration, str):
            raise ValueError("script narration must be a string")
        check_narration(result, narration)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("timeline", type=Path)
    parser.add_argument("--output", type=Path, help="defaults to captions.json beside the timeline")
    parser.add_argument("--script", type=Path, help="check captions against script-package.json narration")
    args = parser.parse_args()
    try:
        timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
        script = json.loads(args.script.read_text(encoding="utf-8")) if args.script else None
        if not isinstance(timeline, dict) or (args.script and not isinstance(script, dict)):
            raise ValueError("timeline and script must be JSON objects")
        captions = build_captions(timeline, script)
        atomic_write_json(args.output or args.timeline.with_name("captions.json"), captions)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
