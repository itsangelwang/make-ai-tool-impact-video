#!/usr/bin/env python3
"""Audit silent/voiced caption pace and readable transition timing."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from limits import LIMITS, lang_key, max_duration


def han_count(text: str) -> int:
    return len(re.findall(r"[\u3400-\u9fff]", text))


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b", text, flags=re.UNICODE))


def validate(data: dict, duration_exception: str | None = None) -> list[str]:
    errors: list[str] = []
    duration = float(data.get("duration_sec", 0))
    key = lang_key(data.get("language", "en-US"))
    english = key == "en"
    min_sec, max_sec = LIMITS["duration_sec"]["min"], max_duration(duration_exception)
    if not min_sec <= duration <= max_sec:
        hint = "" if duration_exception else f" (pass --duration-exception to allow up to {LIMITS['duration_sec']['extended_max']})"
        errors.append(f"duration_sec must be {min_sec}-{max_sec}; got {duration:g}{hint}")

    captions = data.get("captions")
    if not isinstance(captions, list) or not captions:
        errors.append("captions must be a non-empty list")
        captions = []
    previous_end = 0.0
    total_units = 0
    spoken_seconds = 0.0
    for index, cue in enumerate(captions):
        if not all(key in cue for key in ("start_sec", "end_sec", "text")):
            errors.append(f"caption {index} requires start_sec, end_sec, and text")
            continue
        start, end = float(cue["start_sec"]), float(cue["end_sec"])
        if start < previous_end - 0.001:
            errors.append(f"caption {index} overlaps the previous caption")
        if start < 0 or end <= start or end > duration + 0.001:
            errors.append(f"caption {index} has invalid bounds")
            continue
        cue_duration = end - start
        count = word_count(str(cue["text"])) if english else han_count(str(cue["text"]))
        rate = count / cue_duration
        limit = LIMITS["cue_rate_max"][key]
        unit = "words/s" if english else "Han/s"
        if rate > limit:
            errors.append(f"caption {index} is too fast: {rate:.2f} {unit}")
        if cue_duration < count / limit + 0.2:
            errors.append(f"caption {index} lacks a spoken pause")
        previous_end = end
        total_units += count
        spoken_seconds += cue_duration

    bounds = LIMITS["narration"][key]
    if total_units and not bounds["min"] <= total_units <= bounds["max"]:
        errors.append(f"caption narration should contain {bounds['min']}-{bounds['max']} {bounds['unit']}; got {total_units}")
    average_limit = LIMITS["average_rate_max"][key]
    if spoken_seconds and total_units / spoken_seconds > average_limit:
        unit = "words/s" if english else "Han/s"
        errors.append(f"average caption pace is too fast: {total_units / spoken_seconds:.2f} {unit}")

    transitions = data.get("transitions", [])
    if not isinstance(transitions, list):
        errors.append("transitions must be a list")
        transitions = []
    for index, transition in enumerate(transitions):
        if not all(key in transition for key in ("start_sec", "end_sec")):
            errors.append(f"transition {index} requires start_sec and end_sec")
            continue
        start, end = float(transition["start_sec"]), float(transition["end_sec"])
        if start < 0 or end <= start or end > duration + 0.001:
            errors.append(f"transition {index} has invalid bounds")
            continue
        minimum = LIMITS["readable_transition_min_sec"]
        if transition.get("readable", True) and end - start < minimum:
            errors.append(f"readable transition {index} must last at least {minimum:g} seconds")
        for cue_index, cue in enumerate(captions):
            cue_start, cue_end = float(cue.get("start_sec", 0)), float(cue.get("end_sec", 0))
            if max(start, cue_start) < min(end, cue_end) - 0.001:
                errors.append(f"transition {index} overlaps caption {cue_index}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("timeline", type=Path)
    parser.add_argument(
        "--duration-exception",
        help="reason the review needs up to 75 seconds",
    )
    args = parser.parse_args()
    data = json.loads(args.timeline.read_text(encoding="utf-8"))
    errors = validate(data, args.duration_exception)
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
