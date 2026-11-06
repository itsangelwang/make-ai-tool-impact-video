#!/usr/bin/env python3
"""Split one continuous narration take per scene into per-cue clips.

Reading a whole scene in one take sounds more human than synthesizing each
sentence on its own. This cuts the take at the pause that ends each sentence (pauses are matched
to the punctuation in reading order; long ones to sentence ends) and writes
cue-00.wav, cue-01.wav, ... so the usual per-cue timing still works.

  split_scene_takes.py --timeline video/src/timeline.json \
      --take video/public/audio/takes/s1.mp3 --cues 0,1,2 \
      --out-dir video/public/audio/cues

Pauses inside each clip are shortened to --max-pause (0.2 s by default; the
user found the take's natural pauses sleepy). Use --max-pause 0 to keep them,
so that placing the clips back to back reproduces the original take.
"""

from __future__ import annotations

import argparse
import array
import json
import re
import wave
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
    """Return len(texts)+1 cut points: speech start, one cut per sentence boundary, speech end.

    Pauses are aligned, in reading order, with the punctuation the reader may pause at. Each
    mark gets an expected time from its share of the characters, measured in speaking time
    (pauses removed). Sentence ends that close a cue get the long pauses and commas or colons
    the short ones, so a dramatic pause after "New in ChatGPT:" or "What worked:" is not taken
    for the end of a cue. Leaving a long pause unexplained costs more than leaving a comma
    without a pause."""
    merged: list[tuple[float, float]] = []
    for a, b in spans:  # silencedetect can split one pause into two pieces a few ms apart
        if merged and a - merged[-1][1] < 0.06:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    lead = max(0.0, merged[0][1] - 0.03) if merged and merged[0][0] <= 0.001 else 0.0
    tail = min(duration, merged[-1][0] + 0.08) if merged and merged[-1][1] >= duration - 0.05 else duration
    inner = [s for s in merged if s[0] > lead + 0.1 and s[1] < tail - 0.1]
    if len(inner) < len(texts) - 1:
        raise ValueError(f"take has too few pauses for {len(texts)} cues")
    speech, t = [], lead
    for a, b in inner:
        speech.append((t, a))
        t = b
    speech.append((t, tail))
    talk = sum(b - a for a, b in speech) or 1.0

    def at_talk(x: float) -> float:
        for a, b in speech:
            if x <= b - a:
                return a + x
            x -= b - a
        return tail

    total = len(" ".join(texts)) or 1
    marks, offset = [], 0  # (expected time, closes a cue)
    for i, text in enumerate(texts):
        body = text.rstrip()
        found = [m.end() for m in re.finditer(r"[,:;?!.](?=\s|$)", body)]
        if not found or found[-1] != len(body):
            found.append(len(body))
        for pos in found:
            closes = pos == found[-1]
            if not (closes and i == len(texts) - 1):
                marks.append((at_talk(talk * (offset + pos) / total), closes))
        offset += len(text) + 1
    per = talk / len(texts)
    n_pause, n_mark, inf = len(inner), len(marks), float("inf")
    cost = [[inf] * (n_mark + 1) for _ in range(n_pause + 1)]
    back: dict[tuple[int, int], tuple[int, int, bool]] = {}
    cost[0][0] = 0.0
    for j in range(n_pause + 1):
        for k in range(n_mark + 1):
            c = cost[j][k]
            if c == inf:
                continue
            steps = []
            if j < n_pause:  # a pause with no punctuation (a breath)
                steps.append((j + 1, k, c + 0.2 + 10 * (inner[j][1] - inner[j][0]), False))
            if k < n_mark:  # punctuation read without a pause
                steps.append((j, k + 1, c + (2.5 if marks[k][1] else 0.4), False))
            if j < n_pause and k < n_mark:
                length = inner[j][1] - inner[j][0]
                fit = max(0.0, 0.3 - length) * 4 if marks[k][1] else max(0.0, length - 0.3) * 4
                steps.append((j + 1, k + 1, c + abs(sum(inner[j]) / 2 - marks[k][0]) / per * 0.75 + fit, True))
            for nj, nk, v, matched in steps:
                if v < cost[nj][nk]:
                    cost[nj][nk] = v
                    back[(nj, nk)] = (j, k, matched)
    pairs, j, k = {}, n_pause, n_mark
    while (j, k) != (0, 0):
        pj, pk, matched = back[(j, k)]
        if matched:
            pairs[pk] = pj
        j, k = pj, pk
    cuts: list[float] = []
    for k, (expected, closes) in enumerate(marks):
        if not closes:
            continue
        if k in pairs:
            cuts.append(sum(inner[pairs[k]]) / 2)
        else:
            later = [s for s in inner if not cuts or sum(s) / 2 > cuts[-1]]
            if not later:
                raise ValueError(f"take has too few pauses for {len(texts)} cues")
            cuts.append(sum(min(later, key=lambda s: abs(sum(s) / 2 - expected))) / 2)
    return [lead, *cuts, tail]


def shorten_pauses(samples: array.array, rate: int, max_pause: float = 0.2, threshold: int = 900,
                   lead: float = 0.04, tail: float = 0.14) -> array.array:
    """Keep speech and shorten every quiet run inside it to at most `max_pause` seconds.

    Quiet means no sample above `threshold` (16-bit) in a 10 ms window. The clip keeps
    `lead` seconds before the first word and `tail` seconds after the last one. This removes
    dead air only; the voice itself is never stretched or sped up."""
    win = max(1, rate // 100)
    loud = [max((abs(x) for x in samples[i:i + win]), default=0) > threshold for i in range(0, len(samples), win)]
    if not any(loud):
        return samples
    first = loud.index(True)
    last = len(loud) - 1 - loud[::-1].index(True)
    out = array.array("h", [0] * int(lead * rate))
    keep = max(1, int(max_pause * 100))
    i = first
    while i <= last:
        if loud[i]:
            out.extend(samples[i * win:(i + 1) * win])
            i += 1
        else:
            j = i
            while j <= last and not loud[j]:
                j += 1
            out.extend(samples[i * win:(i + min(j - i, keep)) * win])
            i = j
    out.extend(samples[(last + 1) * win:(last + 1) * win + int(tail * rate)])
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--timeline", required=True, type=Path)
    parser.add_argument("--take", required=True, type=Path)
    parser.add_argument("--cues", required=True, help="comma-separated cue indexes read in this take, in order")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--threshold-db", type=float, default=-42.0)
    parser.add_argument("--max-pause", type=float, default=0.2,
                        help="shorten pauses inside each clip to this many seconds (0 keeps the take's pauses)")
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
        sec = cuts[n + 1] - cuts[n]
        if args.max_pause > 0:
            with wave.open(str(out)) as w:
                rate, raw = w.getframerate(), w.readframes(w.getnframes())
            short = shorten_pauses(array.array("h", raw), rate, args.max_pause)
            with wave.open(str(out), "w") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(short.tobytes())
            sec = len(short) / rate
        clips.append({"cue": i, "sec": round(sec, 2), "text": texts[n]})
    print(json.dumps({"ok": True, "clips": clips}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
