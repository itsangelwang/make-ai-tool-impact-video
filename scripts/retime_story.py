#!/usr/bin/env python3
"""Move every story beat to follow new narration timing.

After new narration changes cue timing (fit_timeline_to_audio.py), scenes,
transitions, the brand card, and each in-scene beat (`*_sec` inside a scene,
relative to that scene's start) still follow the old timing. This maps old
times to new ones piecewise-linearly through cue starts/ends, transitions, the
brand card and the end, so a beat tied to a word stays tied to it.

  cp video/src/timeline.json timeline.before.json
  fit_timeline_to_audio.py video/src/timeline.json --audio-dir ... --gap 0.05
  retime_story.py video/src/story.json --old timeline.before.json --new video/src/timeline.json
"""

from __future__ import annotations

import argparse
import bisect
import json
import sys
from pathlib import Path

from safe_io import atomic_write_json


def anchors(old: dict, new: dict, story: dict) -> list[tuple[float, float]]:
    oc, nc = old["captions"], new["captions"]
    if len(oc) != len(nc):
        raise ValueError("old and new timelines must have the same cues")
    pairs = [(0.0, 0.0)]
    for a, b in zip(oc, nc):
        pairs += [(a["start_sec"], b["start_sec"]), (a["end_sec"], b["end_sec"])]
    for a, b in zip(story.get("transitions", []), new.get("transitions", [])):
        pairs += [(a["start_sec"], b["start_sec"]), (a["end_sec"], b["end_sec"])]
    if story.get("brand") and new.get("brand"):
        pairs.append((story["brand"]["start_sec"], new["brand"]["start_sec"]))
    pairs.append((story["duration_sec"], new["duration_sec"]))
    pairs = sorted(set(pairs))
    for (x0, y0), (x1, y1) in zip(pairs, pairs[1:]):
        if y1 < y0 - 1e-6:
            raise ValueError(f"new timing reorders events near {x0:.2f}s → {y0:.2f}s")
    return pairs


def warp(pairs: list[tuple[float, float]]):
    xs = [x for x, _ in pairs]

    def at(v: float) -> float:
        k = max(0, min(len(pairs) - 2, bisect.bisect_right(xs, v) - 1))
        (x0, y0), (x1, y1) = pairs[k], pairs[k + 1]
        return y0 if x1 == x0 else y0 + (y1 - y0) * (v - x0) / (x1 - x0)
    return at


def retime(story: dict, old: dict, new: dict) -> dict:
    at = warp(anchors(old, new, story))

    def shift(value, o0: float, n0: float):
        if isinstance(value, list):
            return [shift(v, o0, n0) for v in value]
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return round(max(0.0, at(o0 + value) - n0), 2)
        return value

    def walk(obj, o0: float, n0: float):
        if isinstance(obj, dict):
            return {k: shift(v, o0, n0) if k.endswith("_sec") else walk(v, o0, n0) for k, v in obj.items()}
        if isinstance(obj, list):
            return [walk(v, o0, n0) for v in obj]
        return obj

    scenes = []
    for scene in story["scenes"]:
        o0 = scene["start_sec"]
        n0, n1 = round(at(o0), 2), round(at(scene["end_sec"]), 2)
        inner = walk({k: v for k, v in scene.items() if k not in ("start_sec", "end_sec")}, o0, n0)
        scenes.append({k: (n0 if k == "start_sec" else n1 if k == "end_sec" else inner[k]) for k in scene})
    story["scenes"] = scenes
    for tr, ntr in zip(story.get("transitions", []), new.get("transitions", [])):
        tr["start_sec"], tr["end_sec"] = ntr["start_sec"], ntr["end_sec"]
    if story.get("brand") and new.get("brand"):
        story["brand"]["start_sec"], story["brand"]["end_sec"] = new["brand"]["start_sec"], new["brand"]["end_sec"]
    story["duration_sec"] = new["duration_sec"]
    return story


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("story", type=Path)
    parser.add_argument("--old", required=True, type=Path, help="timeline.json before fitting")
    parser.add_argument("--new", required=True, type=Path, help="timeline.json after fitting")
    args = parser.parse_args()
    load = lambda p: json.loads(p.read_text(encoding="utf-8"))
    try:
        story = retime(load(args.story), load(args.old), load(args.new))
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    atomic_write_json(args.story, story)
    print(json.dumps({"ok": True, "duration_sec": story["duration_sec"],
                      "scenes": [[s["id"], s["start_sec"], s["end_sec"]] for s in story["scenes"]]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
