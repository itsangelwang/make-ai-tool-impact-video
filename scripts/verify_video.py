#!/usr/bin/env python3
"""Verify stream presence, 9:16 dimensions, duration, decode, and caption bounds."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("--captions", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    errors = []
    if not shutil.which("ffprobe") or not shutil.which("ffmpeg"):
        errors.append("ffmpeg and ffprobe are required")
        probe = {}
    elif not args.video.is_file():
        errors.append("video file is missing")
        probe = {}
    else:
        result = subprocess.run([
            "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(args.video)
        ], capture_output=True, text=True, check=True)
        probe = json.loads(result.stdout)
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
        if not 55 <= duration <= 65:
            errors.append(f"duration must be 55-65 seconds; got {duration:.3f}")
        decode = subprocess.run(["ffmpeg", "-v", "error", "-i", str(args.video), "-f", "null", "-"], capture_output=True, text=True)
        if decode.returncode:
            errors.append("full decode failed")
    try:
        cues = json.loads(args.captions.read_text(encoding="utf-8"))
        last = 0
        for index, cue in enumerate(cues):
            if cue["startMs"] < last or cue["endMs"] <= cue["startMs"]:
                errors.append(f"invalid caption timing at cue {index}")
            if len(cue["text"]) > 34:
                errors.append(f"caption cue {index} is too long for mobile")
            last = cue["endMs"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"invalid captions: {exc}")
    report = {"ok": not errors, "errors": errors, "probe": probe}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
