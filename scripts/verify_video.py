#!/usr/bin/env python3
"""Verify stream presence, 9:16 dimensions, duration, decode, and caption bounds."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess  # nosec B404
from pathlib import Path

from limits import LIMITS, lang_key, max_duration
from safe_io import atomic_write_json


def caption_too_long(cue: dict) -> bool:
    key = lang_key(cue.get("language", "zh-CN"))
    size = len(cue["text"].split()) if key == "en" else len(cue["text"])
    return size > LIMITS["caption_length_max"][key]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("--captions", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument(
        "--duration-exception",
        help="reason a review needs up to 75 seconds; recorded in the QA report",
    )
    args = parser.parse_args()
    errors = []
    min_sec, max_sec = LIMITS["duration_sec"]["min"], max_duration(args.duration_exception)
    ffprobe = shutil.which("ffprobe")
    ffmpeg = shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg:
        errors.append("ffmpeg and ffprobe are required")
        probe = {}
    elif not args.video.is_file():
        errors.append("video file is missing")
        probe = {}
    else:
        result = subprocess.run([  # nosec B603
            ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(args.video)
        ], capture_output=True, text=True, check=True)
        probe = json.loads(result.stdout)
        # ffprobe includes the input filename, which may be an absolute private path.
        probe.get("format", {}).pop("filename", None)
        streams = probe.get("streams", [])
        videos = [s for s in streams if s.get("codec_type") == "video"]
        audios = [s for s in streams if s.get("codec_type") == "audio"]
        if not videos:
            errors.append("missing video stream")
        elif (videos[0].get("width"), videos[0].get("height")) != (1080, 1920):
            errors.append("video must be 1080x1920")
        if not audios:
            errors.append("missing audio stream")
        duration = float(probe.get("format", {}).get("duration", 0))
        if not min_sec <= duration <= max_sec:
            hint = "" if args.duration_exception else f" (pass --duration-exception to allow up to {LIMITS['duration_sec']['extended_max']})"
            errors.append(f"duration must be {min_sec}-{max_sec} seconds; got {duration:.3f}{hint}")
        decode = subprocess.run(  # nosec B603
            [ffmpeg, "-v", "error", "-i", str(args.video), "-f", "null", "-"],
            capture_output=True,
            text=True,
        )
        if decode.returncode:
            errors.append("full decode failed")
    try:
        cues = json.loads(args.captions.read_text(encoding="utf-8"))
        last = 0
        for index, cue in enumerate(cues):
            if cue["startMs"] < last or cue["endMs"] <= cue["startMs"]:
                errors.append(f"invalid caption timing at cue {index}")
            if caption_too_long(cue):
                errors.append(f"caption cue {index} is too long for mobile")
            last = cue["endMs"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"invalid captions: {exc}")
    report = {"ok": not errors, "errors": errors, "duration_exception": args.duration_exception, "probe": probe}
    atomic_write_json(args.report, report)
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
