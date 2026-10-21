#!/usr/bin/env python3
"""Mix narration cues with a music track into one ducked WAV for the composition.

Works with Remotion's bundled FFmpeg, which lacks the mixing filters
(asplit, sidechaincompress, alimiter): FFmpeg only decodes, Python mixes.

  mix_story_audio.py --timeline video/src/timeline.json \
      --cues video/public/audio/cues --music music/track.mp3 \
      --output video/public/audio/mix.wav [--ending-jump 60]

- Each cue-NN.wav/.mp3 starts at its cue's start_sec (no extra trimming).
- Speech is set near -18 dBFS RMS; music sits about 21 dB under it while
  someone speaks and about 11 dB under full scale in gaps; pauses under
  0.4 s count as speech so the music does not pump between sentences.
- --ending-jump N: at the brand card, crossfade to the track N seconds later
  so the music's own ending lands on the card. Pick N as a whole number of
  bars (for example 60 s = 30 bars at 120 BPM) so the beat stays in place.
Set "audio": "audio/mix.wav" in story.json, then render.
"""

from __future__ import annotations

import argparse
import array
import json
import math
import subprocess  # nosec B404
import sys
import tempfile
import wave
from pathlib import Path

from verify_video import find_tools, tool_env

SR = 48000


def read_wav(path: Path) -> list[float]:
    with wave.open(str(path)) as w:
        if w.getsampwidth() != 2:
            raise ValueError(f"{path.name}: expected 16-bit PCM")
        ch, rate = w.getnchannels(), w.getframerate()
        data = array.array("h", w.readframes(w.getnframes()))
    if rate != SR:
        raise ValueError(f"{path.name}: expected {SR} Hz, got {rate}")
    return [v / 32768 for v in data[::ch]]


def load(path: Path, ffmpeg: str | None, tmp: Path) -> list[float]:
    """Read a 48 kHz 16-bit WAV directly; decode anything else with FFmpeg."""
    if path.suffix.lower() == ".wav":
        try:
            return read_wav(path)
        except (ValueError, wave.Error):
            pass
    if not ffmpeg:
        raise RuntimeError(f"FFmpeg is needed to decode {path.name}")
    out = tmp / f"{path.stem}-{abs(hash(str(path)))}.wav"
    subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(path),  # nosec B603
                    "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", str(out)], check=True, env=tool_env(ffmpeg))
    return read_wav(out)


def speech_spans(starts: list[float], lengths: list[float], join: float = 0.4) -> list[tuple[float, float]]:
    spans: list[tuple[float, float]] = []
    for s, n in sorted(zip(starts, lengths)):
        if spans and s - spans[-1][1] < join:
            spans[-1] = (spans[-1][0], max(spans[-1][1], s + n))
        else:
            spans.append((s, s + n))
    return spans


def mix(cues: list[tuple[float, list[float]]], music: list[float], total: float, *, ending_at: float | None = None,
        ending_jump: float = 0.0, speech_db: float = -18.0, under_db: float = -21.0, gap_db: float = -11.0) -> list[float]:
    n = int(total * SR)
    voice = [0.0] * n
    for start, clip in cues:
        o, length, edge = int(start * SR), len(clip), int(0.01 * SR)
        for k in range(length):
            if o + k < n:
                voice[o + k] += clip[k] * min(1.0, (k + 1) / edge, (length - k) / edge)
    spans = speech_spans([s for s, _ in cues], [len(c) / SR for _, c in cues])
    sample = [voice[k] for a, b in spans for k in range(int(a * SR), min(n, int(b * SR)), 7)]
    rms = math.sqrt(sum(v * v for v in sample) / len(sample)) if sample else 0.0
    vgain = 10 ** (speech_db / 20) / rms if rms else 1.0
    under, gap = 10 ** (under_db / 20), 10 ** (gap_db / 20)
    gain = [gap] * n
    for a, b in spans:  # 0.2 s ramp down before speech, 0.4 s back up after
        for k in range(max(0, int((a - 0.2) * SR)), min(n, int((b + 0.4) * SR))):
            t = k / SR
            x = 1.0 if a <= t <= b else (1 - (a - t) / 0.2 if t < a else 1 - (t - b) / 0.4)
            gain[k] = min(gain[k], gap * (under / gap) ** max(0.0, x))
    jump, splice, fade = int(ending_jump * SR), int((ending_at or total + 1) * SR), int(0.25 * SR)
    out = []
    for k in range(n):
        m = music[k] if k < len(music) else 0.0
        if ending_jump and k >= splice - fade:
            w = min(1.0, (k - (splice - fade)) / fade)
            later = music[k + jump] if k + jump < len(music) else 0.0
            m = m * (1 - w) + later * w
        v = voice[k] * vgain + m * gain[k]
        if abs(v) > 0.8:  # soft knee keeps peaks under full scale without a limiter filter
            v = math.copysign(0.8 + 0.19 * math.tanh((abs(v) - 0.8) / 0.19), v)
        out.append(v)
    return out


def write_stereo(path: Path, samples: list[float]) -> None:
    data = array.array("h")
    for v in samples:
        s = int(max(-1.0, min(1.0, v)) * 32767)
        data.append(s)
        data.append(s)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--timeline", required=True, type=Path)
    parser.add_argument("--cues", required=True, type=Path, help="folder with cue-00.wav (or .mp3), cue-01 ...")
    parser.add_argument("--music", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ending-jump", type=float, default=0.0)
    parser.add_argument("--under-db", type=float, default=-21.0)
    parser.add_argument("--gap-db", type=float, default=-11.0)
    args = parser.parse_args()

    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    _, ffmpeg, _ = find_tools(args.output)
    with tempfile.TemporaryDirectory() as tmp:
        cues = []
        for i, cue in enumerate(timeline["captions"]):
            found = [p for ext in (".wav", ".mp3") if (p := args.cues / f"cue-{i:02d}{ext}").is_file()]
            if not found:
                print(json.dumps({"ok": False, "error": f"missing cue-{i:02d}.wav or .mp3"}))
                return 1
            cues.append((cue["start_sec"], load(found[0], ffmpeg, Path(tmp))))
        music = load(args.music, ffmpeg, Path(tmp))
    brand = (timeline.get("brand") or {}).get("start_sec")
    samples = mix(cues, music, timeline["duration_sec"], ending_at=brand, ending_jump=args.ending_jump,
                  under_db=args.under_db, gap_db=args.gap_db)
    write_stereo(args.output, samples)
    peak = max((abs(v) for v in samples), default=0.0)
    print(json.dumps({"ok": True, "output": str(args.output.name), "seconds": timeline["duration_sec"], "peak": round(peak, 3)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
