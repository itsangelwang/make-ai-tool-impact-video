#!/usr/bin/env python3
"""Check story.json before rendering: beats (shots, icons, timings), reading load per
screen, how long a screen stays unchanged, and variety between neighboring scenes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from limits import LIMITS

ICON_FILE = Path(__file__).resolve().parent.parent / "assets" / "remotion-template" / "src" / "components" / "Icon.jsx"
# Scene types whose `visual` text the template shows in a box (an empty visual hides the box).
VISUAL_BOX = {"human-check", "next-action", "ai-handoff"}
BEATS = ("new_feature", "shot", "flow", "scrub", "roles", "checks", "access", "fix")


def icon_names(icon_file: Path = ICON_FILE) -> set[str]:
    return set(re.findall(r"^\s{2}([a-z]+):\s*<>", icon_file.read_text(encoding="utf-8"), flags=re.MULTILINE))


def words(*texts) -> int:
    return sum(len(re.findall(r"[\w’'%$:-]+", str(t))) for t in texts if t)


def screen_words(scene: dict, story: dict) -> int:
    """Authored words a viewer may read on this scene, excluding captions and real UI."""
    texts = [scene.get("label"), scene.get("headline"), scene.get("new_tag")]
    if scene.get("type") in VISUAL_BOX and not (scene.get("type") == "ai-handoff" and scene.get("shot")):
        texts.append(scene.get("visual"))
    feature = scene.get("new_feature") or {}
    texts += [feature.get("date"), feature.get("name"), feature.get("accent"), feature.get("capability")]
    texts += [item.get("label") for item in feature.get("items", [])]
    shot = scene.get("shot") or {}
    callout = shot.get("callout") or {}
    texts += [callout.get("title"), callout.get("note"), (shot.get("stamp") or {}).get("label")]
    texts += [item.get("label") for item in scene.get("flow", [])]
    roles = scene.get("roles") or {}
    texts += [(roles.get("you") or {}).get("label"), (roles.get("ai") or {}).get("name")]
    texts += [out.get("label") for out in (roles.get("ai") or {}).get("outputs", [])]
    texts += [item.get("label") for item in scene.get("checks", [])]
    access = scene.get("access") or {}
    texts += [access.get("label")] + [plan.get("name") for plan in access.get("plans", [])]
    fix = scene.get("fix") or {}
    texts += [fix.get("label"), fix.get("wrong"), fix.get("right")]
    texts.append((scene.get("scrub") or {}).get("ask"))
    if scene.get("type") in {"pain-hook", "before-workflow"} and not scene.get("flow") and not scene.get("shot"):
        texts += story.get("before_steps", []) if scene.get("type") == "before-workflow" or not feature else []
    if scene.get("type") == "after-workflow" and not scene.get("flow") and not scene.get("shot"):
        texts += story.get("after_steps", [])
    return words(*texts)


def change_times(scene: dict) -> list[float]:
    """Seconds (from scene start) at which something new appears on screen."""
    times = [0.0]
    for key in ("new_feature", "roles", "access", "fix", "scrub"):
        item = scene.get(key)
        if isinstance(item, dict) and isinstance(item.get("at_sec"), (int, float)):
            times.append(item["at_sec"])
    if isinstance((scene.get("scrub") or {}).get("ask_at_sec"), (int, float)):
        times.append(scene["scrub"]["ask_at_sec"])
    shot = scene.get("shot") or {}
    for key in ("click", "reveal", "stamp", "callout"):
        if isinstance((shot.get(key) or {}).get("at_sec"), (int, float)):
            times.append(shot[key]["at_sec"])
    times += [band["at_sec"] for band in shot.get("focus", []) if isinstance(band.get("at_sec"), (int, float))]
    times += [item["at_sec"] for item in scene.get("flow", []) if isinstance(item.get("at_sec"), (int, float))]
    times += [t for t in scene.get("steps_at_sec", []) if isinstance(t, (int, float))]
    if isinstance(scene.get("checks_at_sec"), (int, float)):
        times.append(scene["checks_at_sec"])
    return sorted(times)


def main_form(scene: dict) -> str:
    present = [key for key in BEATS if scene.get(key)]
    return "+".join(present) or scene.get("type", "?")


def check(story: dict, public_dir: Path, icons: set[str]) -> list[str]:
    errors: list[str] = []

    def icon(where: str, name) -> None:
        if name not in icons:
            errors.append(f"{where}: unknown icon {name!r}; use one of {sorted(icons)}")

    def timed(where: str, item, scene_len: float, keys=("at_sec",)) -> None:
        if not isinstance(item, dict):
            errors.append(f"{where} must be an object")
            return
        for key in keys:
            value = item.get(key)
            if not isinstance(value, (int, float)) or not 0 <= value < scene_len:
                errors.append(f"{where}.{key} must be seconds from the scene start, inside the scene")

    for scene in story.get("scenes", []):
        sid = scene.get("id", "?")
        length = float(scene.get("end_sec", 0)) - float(scene.get("start_sec", 0))
        feature = scene.get("new_feature")
        if feature is not None:
            timed(f"{sid}.new_feature", feature, length)
            if isinstance(feature, dict):
                if not feature.get("name"):
                    errors.append(f"{sid}.new_feature requires name")
                for item in feature.get("items", []):
                    icon(f"{sid}.new_feature.items", item.get("icon"))
        shot = scene.get("shot")
        if shot is not None:
            crop = shot.get("crop") or {}
            if not shot.get("src") or not isinstance(shot.get("source_width"), (int, float)):
                errors.append(f"{sid}.shot requires src and source_width")
            elif not (public_dir / shot["src"]).is_file():
                errors.append(f"{sid}.shot.src not found under public/: {shot['src']}")
            if not all(isinstance(crop.get(k), (int, float)) for k in "xywh") or crop.get("w", 0) <= 0 or crop.get("h", 0) <= 0:
                errors.append(f"{sid}.shot.crop requires numeric x, y, and positive w, h")
            elif isinstance(shot.get("source_width"), (int, float)) and crop["x"] + crop["w"] > shot["source_width"]:
                errors.append(f"{sid}.shot.crop extends past source_width")
            for beat in ("click", "reveal", "stamp", "callout"):
                if beat in shot:
                    timed(f"{sid}.shot.{beat}", shot[beat], length)
            for index, band in enumerate(shot.get("focus", [])):
                timed(f"{sid}.shot.focus[{index}]", band, length)
                if not isinstance(band.get("y"), (int, float)) or not isinstance(band.get("h"), (int, float)) or band.get("h", 0) <= 0:
                    errors.append(f"{sid}.shot.focus[{index}] requires source y and positive h")
        flow = scene.get("flow")
        if flow is not None:
            if not isinstance(flow, list) or not 2 <= len(flow) <= 4:
                errors.append(f"{sid}.flow needs 2-4 items")
            else:
                for index, item in enumerate(flow):
                    timed(f"{sid}.flow[{index}]", item, length)
                    icon(f"{sid}.flow", item.get("icon"))
                    if words(item.get("label")) > 2:
                        errors.append(f"{sid}.flow[{index}].label should be 1-2 words")
        scrub = scene.get("scrub")
        if scrub is not None:
            timed(f"{sid}.scrub", scrub, length)
            if "ask_at_sec" in scrub:
                timed(f"{sid}.scrub", scrub, length, keys=("ask_at_sec",))
        fix = scene.get("fix")
        if fix is not None:
            timed(f"{sid}.fix", fix, length)
            if not fix.get("wrong") or not fix.get("right"):
                errors.append(f"{sid}.fix requires wrong and right")
        roles = scene.get("roles")
        if roles is not None:
            timed(f"{sid}.roles", roles, length)
            icon(f"{sid}.roles.you", (roles.get("you") or {}).get("icon"))
            for out in (roles.get("ai") or {}).get("outputs", []):
                icon(f"{sid}.roles.ai.outputs", out.get("icon"))
        if "checks" in scene:
            timed(sid, scene, length, keys=("checks_at_sec",))
            for item in scene["checks"]:
                icon(f"{sid}.checks", item.get("icon"))
            if len(scene["checks"]) > 3:
                errors.append(f"{sid}.checks shows at most three items")
        access = scene.get("access")
        if access is not None:
            timed(f"{sid}.access", access, length)
            if not access.get("plans"):
                errors.append(f"{sid}.access requires plans")
        if "steps_at_sec" in scene:
            for value in scene["steps_at_sec"]:
                if not isinstance(value, (int, float)) or not 0 <= value < length:
                    errors.append(f"{sid}.steps_at_sec values must be inside the scene")

        count = screen_words(scene, story)
        if count > LIMITS["screen_words_max"]:
            errors.append(f"{sid}: {count} words on screen (max {LIMITS['screen_words_max']}); cut text or split it into beats")
        times = change_times(scene) + [length]
        gaps = [later - earlier for earlier, later in zip(times, times[1:])]
        if gaps and max(gaps) > LIMITS["static_hold_max_sec"] + 0.01:
            errors.append(f"{sid}: screen stays unchanged for {max(gaps):.1f}s (max {LIMITS['static_hold_max_sec']}); add a beat or shorten the scene")
    return errors


def variety_notes(story: dict) -> list[str]:
    scenes = story.get("scenes", [])
    return [
        f"{a.get('id')} and {b.get('id')} use the same form ({main_form(a)}); vary the visual"
        for a, b in zip(scenes, scenes[1:]) if main_form(a) == main_form(b)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("story", type=Path, help="video/src/story.json")
    args = parser.parse_args()
    story = json.loads(args.story.read_text(encoding="utf-8"))
    errors = check(story, args.story.resolve().parent.parent / "public", icon_names())
    report = {"ok": not errors, "errors": errors, "variety": variety_notes(story),
              "screen_words": {s.get("id"): screen_words(s, story) for s in story.get("scenes", [])}}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
