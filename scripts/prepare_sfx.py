#!/usr/bin/env python3
"""Trim and level downloaded sound effects into the names the template plays.

  prepare_sfx.py --out video/public/audio/sfx \
      swish=sfx-source/swoosh.mp3:0.08:1.12 pop=sfx-source/pop.mp3:0.03:0.45

Each NAME=FILE[:START:END] becomes NAME.wav (48 kHz mono 16-bit), peak-leveled
to -3 dBFS with a short fade-out so no clip ends in a click. Names the template
uses: return, key-2 (mouse clicks), swish, pop, typing, callend, coin, notify,
stamp, tick. See references/sound-library.md for approved sources and cuts.
"""

from __future__ import annotations

import argparse
import array
import json
import subprocess  # nosec B404
import sys
import tempfile
import wave
from pathlib import Path

from verify_video import find_tools, tool_env

SR = 48000


def parse(spec: str) -> tuple[str, Path, float | None, float | None]:
    name, _, rest = spec.partition("=")
    if not name.replace("-", "").isalnum() or not rest:
        raise ValueError(f"expected NAME=FILE[:START:END], got {spec!r}")
    parts = rest.split(":")
    if len(parts) == 3:
        return name, Path(parts[0]), float(parts[1]), float(parts[2])
    return name, Path(rest), None, None


def level(samples: array.array, peak_db: float = -3.0, fade_sec: float = 0.015) -> array.array:
    peak = max((abs(v) for v in samples), default=0)
    if not peak:
        return samples
    gain, fade, n = (10 ** (peak_db / 20) * 32767) / peak, max(1, int(fade_sec * SR)), len(samples)
    return array.array("h", (int(max(-32767, min(32767, samples[k] * gain * min(1.0, (n - k) / fade)))) for k in range(n)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("specs", nargs="+")
    args = parser.parse_args()
    _, ffmpeg, _ = find_tools(args.out)
    if not ffmpeg:
        print(json.dumps({"ok": False, "error": "FFmpeg not found (system or Remotion-bundled)"}))
        return 1
    args.out.mkdir(parents=True, exist_ok=True)
    done = []
    with tempfile.TemporaryDirectory() as tmp:
        for spec in args.specs:
            name, src, start, end = parse(spec)
            raw = Path(tmp) / f"{name}.wav"
            cut = ["-ss", f"{start:.3f}", "-to", f"{end:.3f}"] if start is not None else []
            subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", *cut, "-i", str(src),  # nosec B603
                            "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", str(raw)], check=True, env=tool_env(ffmpeg))
            with wave.open(str(raw)) as w:
                samples = array.array("h", w.readframes(w.getnframes()))
            with wave.open(str(args.out / f"{name}.wav"), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(SR)
                w.writeframes(level(samples).tobytes())
            done.append({"name": name, "sec": round(len(samples) / SR, 2)})
    print(json.dumps({"ok": True, "sounds": done}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
