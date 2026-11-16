#!/usr/bin/env python3
"""Lower only the audio peaks of a rendered MP4, keeping its loudness and video.

Renders often land near -16 LUFS with a true peak around 0 dBFS. Turning the
whole mix down to fix the peak also drops the loudness below target, so this
runs a look-ahead peak limiter in Python (Remotion's bundled FFmpeg has no
`alimiter`) and remuxes the result with the video stream copied:

  limit_peaks.py video/renders/final.mp4 [--ceiling -2.3] [--output out.mp4]

Without --output the input file is replaced. Measure afterwards with
`-af loudnorm=print_format=json` (input_i about -16, input_tp at or below -1.5).
"""

from __future__ import annotations

import argparse
import array
import math
import subprocess  # nosec B404
import sys
import tempfile
import wave
from collections import deque
from pathlib import Path

from verify_video import find_tools, tool_env


def limit_samples(samples: array.array, channels: int, rate: int, ceiling_db: float,
                  lookahead_sec: float = 0.002, release_sec: float = 0.08) -> array.array:
    """Return int16 samples whose peaks stay under ceiling_db (dBFS)."""
    limit = 32768 * 10 ** (ceiling_db / 20)
    frames = len(samples) // channels
    need = []
    for i in range(frames):
        peak = max(abs(samples[i * channels + c]) for c in range(channels))
        need.append(min(1.0, limit / peak) if peak else 1.0)
    # The gain at each frame is the smallest need within the look-ahead window,
    # so the gain is already down when the peak arrives.
    ahead = max(1, int(lookahead_sec * rate))
    window: deque = deque()
    target = [1.0] * frames
    for i in range(frames - 1, -1, -1):
        while window and window[-1][1] >= need[i]:
            window.pop()
        window.append((i, need[i]))
        while window[0][0] > i + ahead:
            window.popleft()
        target[i] = window[0][1]
    release = math.exp(-1 / (release_sec * rate))
    out = array.array("h", samples)
    gain = 1.0
    for i in range(frames):
        gain = target[i] if target[i] < gain else min(target[i], 1 - (1 - gain) * release)
        for c in range(channels):
            v = samples[i * channels + c] * gain
            out[i * channels + c] = int(max(-32768, min(32767, v)))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", type=Path)
    parser.add_argument("--ceiling", type=float, default=-2.3, help="peak ceiling in dBFS (default -2.3)")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.video.is_file():
        print(f"not found: {args.video}", file=sys.stderr)
        return 1
    _, ffmpeg, _ = find_tools(args.video)
    if not ffmpeg:
        print("FFmpeg not found (system or Remotion-bundled)", file=sys.stderr)
        return 1
    env = tool_env(ffmpeg)
    output = args.output or args.video
    with tempfile.TemporaryDirectory() as tmp:
        raw, limited, muxed = Path(tmp) / "a.wav", Path(tmp) / "b.wav", Path(tmp) / "out.mp4"
        subprocess.run([ffmpeg, "-v", "error", "-y", "-i", str(args.video), "-vn", "-ac", "2", "-ar", "48000",
                        "-c:a", "pcm_s16le", str(raw)], check=True, env=env)  # nosec B603
        with wave.open(str(raw)) as w:
            params = w.getparams()
            samples = array.array("h", w.readframes(w.getnframes()))
        out = limit_samples(samples, params.nchannels, params.framerate, args.ceiling)
        with wave.open(str(limited), "w") as w:
            w.setparams(params)
            w.writeframes(out.tobytes())
        subprocess.run([ffmpeg, "-v", "error", "-y", "-i", str(args.video), "-i", str(limited), "-map", "0:v",
                        "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", str(muxed)],
                       check=True, env=env)  # nosec B603
        muxed.replace(output)
    print(f'{{"ok": true, "output": "{output}", "ceiling_db": {args.ceiling}}}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
