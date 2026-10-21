#!/usr/bin/env python3
"""Synthesize an original story-scored music bed and a characterful UI sound set.

Everything is generated from code, so there are no licensing questions.

  sfx   --output DIR                      tick, pop, notify, key-1..3, return,
                                          swish, uhoh, coin, stamp, typing,
                                          callend (.wav); fallback only, prefer
                                          recorded sounds (prepare_sfx.py)
  music --events events.json --output bgm.wav [--bpm 120]

events.json holds seconds on the video timeline: "end" (required) and optional
"drop" (AI handoff starts), "stop" (reveal of the missing/risky detail),
"boom" (tool or result appears), "flip" (outcome changes), "calm" (human
check), "outro" (next action), "brand" (brand card). Duck the bed under speech
in the composition.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import struct
import sys
import wave
from pathlib import Path

SR = 44100
rng = random.Random(4049)


def write(path: Path, samples: list[float], channels: int = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = max(1e-9, max(abs(x) for x in samples))
    gain = min(1.0, 0.89 / peak)
    with wave.open(str(path), "wb") as w:
        w.setparams((channels, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, x * gain)) * 32767)) for x in samples))


def env(t: float, attack: float, decay: float) -> float:
    return min(1.0, t / attack) * math.exp(-t / decay) if t >= 0 else 0.0


def noise() -> float:
    return rng.random() * 2 - 1


def render(seconds: float, fn) -> list[float]:
    return [fn(i / SR) for i in range(int(seconds * SR))]


# ---------------------------------------------------------------- sound effects
def sfx(out: Path) -> None:
    bell = lambda f, t, d: (math.sin(2 * math.pi * f * t) + 0.35 * math.sin(4 * math.pi * f * t)) * env(t, 0.004, d)
    write(out / "tick.wav", render(0.05, lambda t: 0.5 * math.sin(2 * math.pi * 2400 * t) * env(t, 0.001, 0.008)))
    write(out / "pop.wav", render(0.12, lambda t: 0.7 * math.sin(2 * math.pi * (380 * t + 2600 * t * t)) * env(t, 0.003, 0.035)))
    write(out / "notify.wav", render(0.7, lambda t: 0.5 * bell(1318.5, t, 0.18) + 0.5 * bell(1046.5, t - 0.14, 0.3)))
    for name, f in (("key-1", 3100), ("key-2", 2700), ("key-3", 3400)):
        write(out / f"{name}.wav", render(0.05, lambda t, f=f: (0.6 * noise() + 0.5 * math.sin(2 * math.pi * f * t)) * env(t, 0.0008, 0.009)))
    write(out / "return.wav", render(0.12, lambda t: (0.6 * noise() + 0.7 * math.sin(2 * math.pi * 900 * t)) * env(t, 0.001, 0.025)))
    write(out / "swish.wav", render(0.32, lambda t: noise() * math.sin(math.pi * t / 0.32) ** 2 * 0.6))
    write(out / "uhoh.wav", render(0.75, lambda t: 0.5 * (math.sin(2 * math.pi * 392 * (1 + 0.01 * math.sin(30 * t)) * t) * env(t, 0.01, 0.12) if t < 0.28 else math.sin(2 * math.pi * 293.7 * (1 + 0.012 * math.sin(30 * t)) * t) * env(t - 0.28, 0.01, 0.2))))
    write(out / "coin.wav", render(0.6, lambda t: 0.45 * bell(1975.5, t, 0.08) + 0.5 * bell(2637.0, t - 0.07, 0.25)))
    write(out / "stamp.wav", render(0.3, lambda t: 0.9 * math.sin(2 * math.pi * (95 - 40 * t) * t) * env(t, 0.002, 0.06) + 0.4 * noise() * env(t, 0.001, 0.015)))
    # fallback typing bed (3 s of uneven key presses) and a two-tone hang-up
    hits = [0.0]
    while hits[-1] < 2.9:
        hits.append(hits[-1] + 0.07 + 0.09 * abs(noise()))
    write(out / "typing.wav", render(3.0, lambda t: sum((0.5 * noise() + 0.4 * math.sin(2 * math.pi * 2900 * t)) * env(t - h, 0.0008, 0.01) for h in hits if 0 <= t - h < 0.05)))
    write(out / "callend.wav", render(0.6, lambda t: 0.4 * (math.sin(2 * math.pi * 620 * t) * env(t, 0.005, 0.12) if t < 0.25 else math.sin(2 * math.pi * 465 * t) * env(t - 0.25, 0.005, 0.15))))


# ---------------------------------------------------------------------- music
NOTE = lambda n: 440.0 * 2 ** ((n - 69) / 12)
# C - Am - F - G, one chord per bar (MIDI roots and triads)
PROGRESSION = [(48, (60, 64, 67)), (45, (57, 60, 64)), (41, (57, 60, 65)), (43, (55, 59, 62))]


def music(events: dict, output: Path, bpm: float = 120.0) -> None:
    """events (seconds): end (required); drop, stop, boom, flip, calm, outro, brand (optional)."""
    if "end" not in events:
        raise ValueError("events require 'end'")
    total = float(events["end"])
    big = total + 1e9
    ev = {"drop": 0.0, "stop": big, "boom": big, "flip": big, "calm": big, "outro": big, "brand": big, **{k: float(v) for k, v in events.items()}}
    beat = 60 / bpm
    bar = beat * 4

    def section(t: float) -> str:
        if t < ev["drop"]:
            return "tension"
        if t < min(ev["stop"], ev["calm"]):
            return "groove"
        if ev["stop"] < big and t < ev["stop"] + 0.9:
            return "silence"
        if ev["stop"] < big and t < ev["boom"]:
            return "build"
        if t < ev["calm"]:
            return "groove"
        if t < ev["outro"]:
            return "calm"
        if t < ev["brand"]:
            return "groove-light"
        return "brand"

    def riser(t: float, start: float, end: float) -> float:
        if not start <= t < end:
            return 0.0
        p = (t - start) / (end - start)
        return (0.25 * noise() + 0.3 * math.sin(2 * math.pi * (180 + 900 * p * p) * t)) * p ** 2

    def impact(t: float, at: float) -> float:
        d = t - at
        if d < 0 or d > 1.2:
            return 0.0
        return 0.9 * math.sin(2 * math.pi * (70 - 30 * d) * d) * math.exp(-d * 4) + 0.3 * noise() * math.exp(-d * 30)

    samples = []
    for i in range(int(total * SR)):
        t = i / SR
        sec = section(t)
        bar_i = int(t / bar)
        root, triad = PROGRESSION[bar_i % 4]
        bt, et = t % beat, t % (beat / 2)
        beat_i, step16 = int(t / beat) % 4, int(t / (beat / 4))
        s = 0.0
        if sec == "silence":
            samples.append(0.0)
            continue
        # pad: always present, brighter after the drop
        pad_level = {"tension": 0.06, "build": 0.07, "calm": 0.08, "brand": 0.12}.get(sec, 0.09)
        s += pad_level * sum(math.sin(2 * math.pi * NOTE(n) * t + k) for k, n in enumerate(triad)) / 3
        if sec == "tension":
            # clock-like hats and a low pulse on A
            s += 0.05 * noise() * math.exp(-et * 120)
            s += 0.10 * math.sin(2 * math.pi * NOTE(45) * t) * math.exp(-bt * 6)
        if sec in ("groove", "groove-light", "build"):
            kick_gain = 0.0 if sec == "build" else (0.5 if sec == "groove" else 0.32)
            s += kick_gain * math.sin(2 * math.pi * (95 - 55 * min(bt, 0.12) / 0.12) * bt) * math.exp(-bt * 14)
            if beat_i in (1, 3) and sec == "groove":
                s += 0.16 * noise() * math.exp(-bt * 28)  # clap
            s += 0.05 * noise() * math.exp(-et * 90)  # hats
            bass_note = root if (step16 % 8) not in (3, 6) else root + 7
            s += (0.18 if sec == "groove" else 0.1) * math.sin(2 * math.pi * NOTE(bass_note) * t) * math.exp(-(t % (beat / 2)) * 5)
            arp = triad[(step16 * 2) % 3] + (12 if step16 % 4 == 3 else 0)
            s += 0.07 * math.sin(2 * math.pi * NOTE(arp + 12) * t) * math.exp(-(t % (beat / 4)) * 18)
        if sec == "calm":
            s += 0.3 * math.sin(2 * math.pi * (90 - 50 * min(bt, 0.12) / 0.12) * bt) * math.exp(-bt * 12) * (beat_i == 0)
            s += 0.06 * math.sin(2 * math.pi * NOTE(triad[step16 // 2 % 3] + 12) * t) * math.exp(-(t % (beat / 2)) * 8)
        if sec == "brand":
            d = t - ev["brand"]
            for k, n in enumerate((72, 76, 79, 84)):
                s += 0.12 * math.sin(2 * math.pi * NOTE(n) * t) * env(d - k * 0.09, 0.01, 0.9)
            s *= max(0.0, 1 - max(0.0, t - (total - 1.0)))
        if ev["drop"] > 0:
            s += riser(t, ev["drop"] - 1.4, ev["drop"]) + impact(t, ev["drop"]) * 0.7
        if ev["boom"] < big:
            s += riser(t, min(ev["boom"] - 0.5, ev["stop"] + 0.9), ev["boom"]) + impact(t, ev["boom"])
        if ev["flip"] < big:
            s += 0.6 * riser(t, ev["flip"] - 0.9, ev["flip"]) + impact(t, ev["flip"]) * 0.6
        samples.append(s)
    write(output, samples)



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("sfx")
    s.add_argument("--output", type=Path, required=True)
    m = sub.add_parser("music")
    m.add_argument("--events", type=Path, required=True)
    m.add_argument("--output", type=Path, required=True)
    m.add_argument("--bpm", type=float, default=120.0)
    args = parser.parse_args()
    try:
        if args.command == "sfx":
            sfx(args.output)
            print(json.dumps({"ok": True, "output": args.output.name}))
        else:
            music(json.loads(args.events.read_text(encoding="utf-8")), args.output, args.bpm)
            print(json.dumps({"ok": True, "output": args.output.name}))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
