#!/usr/bin/env python3
"""Fit timeline.json caption timing to measured per-cue narration audio.

Expects one audio file per caption cue named cue-00.mp3, cue-01.mp3, ... (any
extension via --ext). Keeps each readable transition after the cue it followed,
records `audio_sec` per cue, and places a spoken brand cue (`"brand": true`)
just after the brand card appears. Scenes in script-package.json are not moved;
re-derive their boundaries from the printed cue starts.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path

from limits import LIMITS, lang_key
from safe_io import atomic_write_json

WORD = re.compile(r"\b[\w]+(?:[’'-][\w]+)*\b")
HAN = re.compile(r"[㐀-鿿]")


def probe_seconds(path: Path) -> float:
    """Audio duration via ffprobe, or afinfo on macOS when FFmpeg is not installed."""
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        out = subprocess.run(  # nosec B603
            [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, check=True,
        ).stdout
        return float(out.strip())
    afinfo = shutil.which("afinfo")
    if afinfo:
        out = subprocess.run([afinfo, str(path)], capture_output=True, text=True, check=True).stdout  # nosec B603
        for line in out.splitlines():
            if "estimated duration" in line:
                return float(line.split()[2])
    raise RuntimeError("ffprobe (FFmpeg) or macOS afinfo is required to measure audio")


def fit(timeline: dict, durations: list[float], gap: float = 0.3, transition_sec: float = 1.4,
        brand_sec: float | None = None) -> dict:
    caps = timeline["captions"]
    if len(durations) != len(caps):
        raise ValueError(f"expected {len(caps)} audio files, got {len(durations)}")
    key = lang_key(timeline.get("language", "en-US"))
    limit = LIMITS["cue_rate_max"][key]
    units = (lambda s: len(WORD.findall(s))) if key == "en" else (lambda s: len(HAN.findall(s)))
    brand_low, brand_high = LIMITS["brand_card_sec"]["min"], LIMITS["brand_card_sec"]["max"]
    brand_sec = brand_low + 0.5 if brand_sec is None else brand_sec

    # remember which cue each transition followed
    after = []
    for tr in timeline.get("transitions", []):
        before = [i for i, c in enumerate(caps) if not c.get("brand") and c["end_sec"] <= tr["start_sec"] + 1e-6]
        after.append(before[-1] if before else -1)

    story = [i for i, c in enumerate(caps) if not c.get("brand")]
    brand = [i for i, c in enumerate(caps) if c.get("brand")]
    if len(brand) > 1 or (brand and brand[0] != len(caps) - 1):
        raise ValueError("only the last cue may be the spoken brand cue")
    cursor = 0.3
    for t_index, a in enumerate(after):
        if a == -1:
            tr = timeline["transitions"][t_index]
            tr["start_sec"], tr["end_sec"] = round(cursor, 2), round(cursor + transition_sec, 2)
            cursor += transition_sec + 0.15
    for i in story:
        c = caps[i]
        c["audio_sec"] = round(durations[i], 2)
        show = max(durations[i] + 0.25, units(c["text"]) / (limit * 0.96) + 0.3)
        c["start_sec"], c["end_sec"] = round(cursor, 2), round(cursor + show, 2)
        cursor = c["end_sec"] + gap
        for t_index, a in enumerate(after):
            if a == i:
                tr = timeline["transitions"][t_index]
                tr["start_sec"] = round(cursor - gap + 0.1, 2)
                tr["end_sec"] = round(tr["start_sec"] + transition_sec, 2)
                cursor = tr["end_sec"] + 0.15
    brand_start = round(cursor + 0.2, 2)
    total = brand_start + brand_sec
    if brand:
        c = caps[brand[0]]
        c["audio_sec"] = round(durations[brand[0]], 2)
        c["start_sec"] = round(brand_start + 0.1, 2)
        spoken = durations[brand[0]]
        hold = max(0.15, min(0.3, brand_high - 0.1 - spoken))
        if 0.1 + spoken + hold > brand_high + 1e-6:
            raise ValueError(f"spoken brand needs {0.1 + spoken + hold:.2f}s; the card allows {brand_high}s — shorten the line")
        c["end_sec"] = round(c["start_sec"] + spoken + hold * 0.8, 2)
        total = min(brand_start + brand_high, max(total, brand_start + 0.1 + spoken + hold))
    timeline["duration_sec"] = round(total, 2)
    timeline["brand"] = {"start_sec": brand_start, "end_sec": round(total, 2)}
    return timeline


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("timeline", type=Path)
    parser.add_argument("--audio-dir", type=Path, required=True)
    parser.add_argument("--ext", default="mp3")
    parser.add_argument("--gap", type=float, default=0.3)
    parser.add_argument("--transition-sec", type=float, default=1.4)
    parser.add_argument("--output", type=Path, help="defaults to overwriting the timeline")
    args = parser.parse_args()
    try:
        timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
        files = [args.audio_dir / f"cue-{i:02d}.{args.ext}" for i in range(len(timeline["captions"]))]
        missing = [f.name for f in files if not f.is_file()]
        if missing:
            raise ValueError(f"missing audio: {', '.join(missing)}")
        fitted = fit(timeline, [probe_seconds(f) for f in files], args.gap, args.transition_sec)
        atomic_write_json(args.output or args.timeline, fitted)
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.CalledProcessError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "duration_sec": fitted["duration_sec"], "brand": fitted["brand"],
                      "cue_starts": [c["start_sec"] for c in fitted["captions"]]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
