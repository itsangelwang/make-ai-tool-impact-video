#!/usr/bin/env python3
"""Split one continuous narration take per scene into per-cue clips.

Reading a whole scene in one take sounds more human than synthesizing each
sentence on its own. This cuts the take at the natural pause nearest each
sentence boundary (estimated from character counts) and writes
cue-00.wav, cue-01.wav, ... so the usual per-cue timing still works.

  split_scene_takes.py --timeline video/src/timeline.json \
      --take video/public/audio/takes/s1.mp3 --cues 0,1,2 \
      --out-dir video/public/audio/cues

Each clip keeps the pause that follows it, so placing the clips back to back
reproduces the original take.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess  # nosec B404
import sys
from pathlib import Path

from verify_video import find_tools, tool_env

SILENCE = re.compile(r"silence_(start|end): ([0-9.]+)")


def silences(log: str, duration: float) -> list[tuple[float, float]]:
    """Pair silencedetect start/end lines; an open silence runs to the end."""
    spans, start = [], None
    for kind, value in SILENCE.findall(log):
        if kind == "start":
            start = float(value)
        elif start is not None:
            spans.append((start, float(value)))
            start = None
    if start is not None:
        spans.append((start, duration))
    return spans


def boundaries(spans: list[tuple[float, float]], duration: float, texts: list[str]) -> list[float]:
    """Return len(texts)+1 cut points: speech start, one cut per sentence boundary, speech end."""
    lead = max(0.0, spans[0][1] - 0.03) if spans and spans[0][0] <= 0.001 else 0.0
    tail = min(duration, spans[-1][0] + 0.08) if spans and spans[-1][1] >= duration - 0.05 else duration
    inner = [s for s in spans if s[0] > lead + 0.1 and s[1] < tail - 0.1]
    total = sum(len(t) for t in texts) or 1
    cuts, seen = [], 0
    for text in texts[:-1]:
        seen += len(text)
        expected = lead + (tail - lead) * seen / total
        later = [s for s in inner if not cuts or (s[0] + s[1]) / 2 > cuts[-1]]
        if not later:
            raise ValueError(f"take has too few pauses for {len(texts)} cues")
        # prefer a real sentence pause (>0.15 s) near the expected point
        best = min(later, key=lambda s: abs((s[0] + s[1]) / 2 - expected) + (0 if s[1] - s[0] > 0.15 else 0.4))
        cuts.append((best[0] + best[1]) / 2)
    return [lead, *cuts, tail]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--timeline", required=True, type=Path)
    parser.add_argument("--take", required=True, type=Path)
    parser.add_argument("--cues", required=True, help="comma-separated cue indexes read in this take, in order")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--threshold-db", type=float, default=-42.0)
    args = parser.parse_args()

    ffprobe, ffmpeg, _ = find_tools(args.out_dir)
    if not ffmpeg:
        print(json.dumps({"ok": False, "error": "FFmpeg not found (system or Remotion-bundled)"}))
        return 1
    env = tool_env(ffmpeg)
    ids = [int(x) for x in args.cues.split(",")]
    caps = json.loads(args.timeline.read_text(encoding="utf-8"))["captions"]
    texts = [caps[i]["text"] for i in ids]
    duration = float(subprocess.run(  # nosec B603
        [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(args.take)],
        capture_output=True, text=True, check=True, env=env).stdout)
    log = subprocess.run(  # nosec B603
        [ffmpeg, "-hide_banner", "-i", str(args.take), "-af", f"silencedetect=n={args.threshold_db}dB:d=0.07", "-f", "null", "-"],
        capture_output=True, text=True, env=env).stderr
    try:
        cuts = boundaries(silences(log, duration), duration, texts)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    args.out_dir.mkdir(parents=True, exist_ok=True)
    clips = []
    for n, i in enumerate(ids):
        out = args.out_dir / f"cue-{i:02d}.wav"
        subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{cuts[n]:.3f}", "-to", f"{cuts[n + 1]:.3f}",  # nosec B603
                        "-i", str(args.take), "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(out)], check=True, env=env)
        clips.append({"cue": i, "sec": round(cuts[n + 1] - cuts[n], 2), "text": texts[n]})
    print(json.dumps({"ok": True, "clips": clips}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
