#!/usr/bin/env python3
"""Generate a lightweight, original tech-explainer music bed as a WAV file."""

from __future__ import annotations

import argparse
import math
import random
import struct
import wave
from pathlib import Path


CHORDS = [
    (261.63, 329.63, 392.00, 493.88),  # Cmaj7
    (220.00, 261.63, 329.63, 392.00),  # Am7
    (174.61, 220.00, 261.63, 329.63),  # Fmaj7
    (196.00, 246.94, 293.66, 440.00),  # Gadd9
]


def render(output: Path, duration: float, bpm: float, sample_rate: int = 44100) -> None:
    rng = random.Random(104729)
    total = int(duration * sample_rate)
    beat = 60.0 / bpm
    chord_span = beat * 8
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as wav:
        wav.setparams((2, 2, sample_rate, total, "NONE", "not compressed"))
        block = bytearray()
        for index in range(total):
            t = index / sample_rate
            chord = CHORDS[int(t / chord_span) % len(CHORDS)]
            local_chord = t % chord_span
            chord_env = min(1.0, local_chord / 0.7, (chord_span - local_chord) / 0.9)
            pad = sum(math.sin(2 * math.pi * f * t + i * 0.4) for i, f in enumerate(chord)) / 4
            pad += 0.28 * sum(math.sin(2 * math.pi * (f / 2) * t) for f in chord) / 4
            pad *= max(0.0, chord_env) * 0.16

            eighth = beat / 2
            step = int(t / eighth)
            note_t = t - step * eighth
            note = chord[(step * 3) % len(chord)] * (2 if step % 4 == 3 else 1)
            pluck = math.sin(2 * math.pi * note * note_t) * math.exp(-note_t * 9) * 0.09

            beat_t = t % beat
            kick = math.sin(2 * math.pi * (72 - 32 * beat_t) * beat_t) * math.exp(-beat_t * 18) * 0.16
            half_t = t % eighth
            hat = (rng.random() * 2 - 1) * math.exp(-half_t * 85) * 0.025
            bar_beat = int(t / beat) % 4
            snare = 0.0
            if bar_beat in (1, 3):
                snare = (rng.random() * 2 - 1) * math.exp(-beat_t * 32) * 0.055

            intro = min(1.0, t / 1.2)
            outro = min(1.0, max(0.0, duration - t) / 2.0)
            sample = (pad + pluck + kick + hat + snare) * intro * outro
            left = max(-1.0, min(1.0, sample + pluck * 0.08))
            right = max(-1.0, min(1.0, sample - pluck * 0.08))
            block.extend(struct.pack("<hh", int(left * 32767), int(right * 32767)))
            if len(block) >= 65536:
                wav.writeframesraw(block)
                block.clear()
        if block:
            wav.writeframesraw(block)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--duration", type=float, default=65.0)
    parser.add_argument("--bpm", type=float, default=116.0)
    args = parser.parse_args()
    render(args.output, args.duration, args.bpm)
    print(args.output)


if __name__ == "__main__":
    main()
