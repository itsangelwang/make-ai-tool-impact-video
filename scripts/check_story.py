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
BEATS = ("call_end", "toast", "new_feature", "shot", "flow", "scrub", "roles", "checks", "access", "plans", "fix", "replay", "send", "tryit")


def icon_names(icon_file: Path = ICON_FILE) -> set[str]:
    return set(re.findall(r"^\s{2}([a-z]+):\s*<>", icon_file.read_text(encoding="utf-8"), flags=re.MULTILINE))


def words(*texts) -> int:
    return sum(len(re.findall(r"[\w’'%$:-]+", str(t))) for t in texts if t)


def screen_words(scene: dict, story: dict) -> int:
    """Authored words a viewer may read at once in this scene, excluding captions and real UI.
    A pain-hook's opening beats fade out when its new-feature card appears, so only the larger
    of the two groups counts."""
    feature = scene.get("new_feature") or {}
    if scene.get("type") == "pain-hook" and feature:
        card = words(feature.get("date"), feature.get("name"), feature.get("accent"), feature.get("capability"), *[i.get("label") for i in feature.get("items", [])])
        rest = screen_words({**scene, "new_feature": None, "label": None, "headline": None}, story)
        return words(scene.get("label"), scene.get("headline")) + max(card, rest)
    texts = [scene.get("label"), scene.get("headline"), scene.get("new_tag")]
    if scene.get("type") in VISUAL_BOX and not (scene.get("type") == "ai-handoff" and scene.get("shot")):
        texts.append(scene.get("visual"))
    feature = scene.get("new_feature") or {}
    texts += [feature.get("date"), feature.get("name"), feature.get("accent"), feature.get("capability")]
    texts += [item.get("label") for item in feature.get("items", [])]
    shot = scene.get("shot") or {}
    callout = shot.get("callout") or {}
    texts += [callout.get("title"), callout.get("note"), (shot.get("stamp") or {}).get("label"), (shot.get("summary") or {}).get("text")]
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
    toast = scene.get("toast") or {}
    texts += [toast.get("title"), toast.get("note")]
    call = scene.get("call_end") or {}
    texts += ["Call ended"] + [name[:1] for name in call.get("people", [])] if call else []
    replay = scene.get("replay") or {}
    texts += [replay.get("quote"), replay.get("who"), (scene.get("send") or {}).get("label")]
    plans = scene.get("plans") or {}
    texts += [plans.get("title"), plans.get("feature")] + [plan.get("name") for plan in plans.get("plans", [])]
    custom = any(scene.get(key) for key in ("shot", "flow", "scrub", "fix", "replay", "plans", "tryit"))
    if scene.get("type") in {"pain-hook", "before-workflow"} and not custom:
        texts += story.get("before_steps", []) if scene.get("type") == "before-workflow" or not feature else []
    if scene.get("type") == "after-workflow" and not custom:
        texts += story.get("after_steps", [])
    tryit = scene.get("tryit") or {}
    # the two phases replace each other, so only the wordier one is on screen at once
    phase = max(words((tryit.get("consent") or {}).get("ask"), (tryit.get("consent") or {}).get("yes")),
                words((tryit.get("old") or {}).get("file"), "Ask ChatGPT") if tryit.get("old") else 0) if tryit else 0
    return words(*texts) + phase


def change_times(scene: dict) -> list[float]:
    """Seconds (from scene start) at which something new appears on screen."""
    times = [0.0]
    for key in ("new_feature", "roles", "access", "fix", "scrub", "toast", "call_end"):
        item = scene.get(key)
        if isinstance(item, dict) and isinstance(item.get("at_sec"), (int, float)):
            times.append(item["at_sec"])
    scrub = scene.get("scrub") or {}
    if isinstance(scrub.get("at_sec"), (int, float)):
        # The playhead keeps jumping for six moves of 22 frames each.
        times += [scrub["at_sec"] + (8 + 22 * n) / 30 for n in range(1, 7)]
    if isinstance(scrub.get("ask_at_sec"), (int, float)):
        times.append(scrub["ask_at_sec"])
    call = scene.get("call_end") or {}
    if isinstance(call.get("end_at_sec"), (int, float)):
        times += [call["end_at_sec"], call["end_at_sec"] + 16 / 30]
    fix = scene.get("fix") or {}
    if isinstance(fix.get("at_sec"), (int, float)):
        times.append(fix["at_sec"] + 24 / 30)  # the right value pops in
    shot = scene.get("shot") or {}
    for key in ("click", "reveal", "stamp", "callout", "summary", "zoom", "drag", "type", "wait"):
        if isinstance((shot.get(key) or {}).get("at_sec"), (int, float)):
            times.append(shot[key]["at_sec"])
    for key in ("drag", "type", "wait", "zoom"):  # these keep moving until they finish
        item = shot.get(key) or {}
        if isinstance(item.get("at_sec"), (int, float)):
            times.append(item["at_sec"] + item.get("frames", 30) / 30)
    times += [band["at_sec"] for band in shot.get("focus", []) if isinstance(band.get("at_sec"), (int, float))]
    times += [item["at_sec"] for item in scene.get("flow", []) if isinstance(item.get("at_sec"), (int, float))]
    times += [t for t in scene.get("steps_at_sec", []) if isinstance(t, (int, float))]
    if isinstance(scene.get("checks_at_sec"), (int, float)):
        times.append(scene["checks_at_sec"])
    num = lambda v: isinstance(v, (int, float))
    replay = scene.get("replay") or {}
    times += [replay[k] for k in ("at_sec", "jump_sec", "replay_sec") if num(replay.get(k))]
    if num(replay.get("jump_sec")):
        times.append(replay["jump_sec"] + 8 / 30)  # the quote pops in
    send = scene.get("send") or {}
    if num(send.get("at_sec")):
        times += [max(0.0, send["at_sec"] - 1), send["at_sec"]]
    plans = scene.get("plans") or {}
    if num(plans.get("at_sec")):
        times += [plans["at_sec"] + (6 + 5 * i) / 30 for i in range(len(plans.get("plans", [])))]
    tryit = scene.get("tryit") or {}
    consent, old = tryit.get("consent") or {}, tryit.get("old") or {}
    if num(consent.get("at_sec")):
        times += [consent["at_sec"] + f / 30 for f in (0, 4, 14, 22)]
    if num(old.get("at_sec")):
        times += [old["at_sec"] + f / 30 for f in (2, 4, 26)]
    return sorted(times)


def main_form(scene: dict) -> str:
    present = []
    for key in BEATS:
        if scene.get(key):
            parts = [sub for sub in ("zoom", "drag", "type", "click", "focus", "callout", "stamp") if key == "shot" and scene["shot"].get(sub)]
            present.append(f"{key}({','.join(parts)})" if parts else key)
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
            for beat in ("click", "reveal", "stamp", "callout", "summary", "zoom", "drag", "type", "wait"):
                if beat in shot:
                    timed(f"{sid}.shot.{beat}", shot[beat], length)
            zoom = shot.get("zoom") or {}
            start_crop = zoom.get("from") or {}
            if zoom and crop.get("h") and start_crop.get("h") and abs(start_crop.get("w", 0) / start_crop["h"] - crop["w"] / crop["h"]) > 0.03 * crop["w"] / crop["h"]:
                errors.append(f"{sid}.shot.zoom.from must have the same aspect ratio as shot.crop")
            for beat in ("drag", "type"):
                region = (shot.get(beat) or {}).get("region")
                if beat in shot and region is not None and not all(isinstance(region.get(k), (int, float)) for k in "xywh"):
                    errors.append(f"{sid}.shot.{beat}.region requires x, y, w, h in source pixels")
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
        call = scene.get("call_end")
        if call is not None:
            timed(f"{sid}.call_end", call, length, keys=("at_sec", "end_at_sec"))
            if not call.get("file") or len(call.get("people", [])) != 2:
                errors.append(f"{sid}.call_end requires file and two people")
        toast = scene.get("toast")
        if toast is not None:
            timed(f"{sid}.toast", toast, length)
            icon(f"{sid}.toast", toast.get("icon"))
            if not toast.get("title"):
                errors.append(f"{sid}.toast requires title")
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
        plans = scene.get("plans")
        if plans is not None:
            timed(f"{sid}.plans", plans, length)
            if not plans.get("title") or not plans.get("feature") or not plans.get("plans"):
                errors.append(f"{sid}.plans requires title (whose plans, e.g. 'ChatGPT plans'), feature and plans")
            icon(f"{sid}.plans", plans.get("icon", "mic"))
        replay = scene.get("replay")
        if replay is not None:
            timed(f"{sid}.replay", replay, length, keys=("at_sec", "jump_sec") + (("replay_sec",) if "replay_sec" in replay else ()))
            if not replay.get("file") or not replay.get("quote"):
                errors.append(f"{sid}.replay requires file and quote")
        send = scene.get("send")
        if send is not None:
            timed(f"{sid}.send", send, length)
        tryit = scene.get("tryit")
        if tryit is not None:
            consent, old = (tryit or {}).get("consent"), (tryit or {}).get("old")
            if not consent or not old:
                errors.append(f"{sid}.tryit requires consent and old")
            else:
                timed(f"{sid}.tryit.consent", consent, length)
                timed(f"{sid}.tryit.old", old, length)
                if len(consent.get("people", [])) != 2 or not consent.get("ask") or not consent.get("yes"):
                    errors.append(f"{sid}.tryit.consent requires two people, ask and yes")
                if not old.get("file"):
                    errors.append(f"{sid}.tryit.old requires file (use a placeholder name such as old-call-xxx.mp3)")
                elif isinstance(old.get("at_sec"), (int, float)) and isinstance(consent.get("at_sec"), (int, float)) and old["at_sec"] - consent["at_sec"] < 1.0:
                    errors.append(f"{sid}.tryit.old must start at least 1 s after consent")
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
        start = float(scene.get("start_sec", 0))
        cards = [float(t["start_sec"]) - start for t in story.get("transitions", []) if 0 < float(t.get("start_sec", -1)) - start < length]
        times = sorted(change_times(scene) + cards) + [length]
        gaps = [later - earlier for earlier, later in zip(times, times[1:])]
        if gaps and max(gaps) > LIMITS["static_hold_max_sec"] + 0.01:
            errors.append(f"{sid}: screen stays unchanged for {max(gaps):.1f}s (max {LIMITS['static_hold_max_sec']}); add a beat or shorten the scene")
    return errors


CHAPTER_CHANGES = {("before-workflow", "ai-handoff"), ("before-workflow", "after-workflow"), ("after-workflow", "human-check"), ("ai-handoff", "human-check")}


def transition_errors(story: dict) -> list[str]:
    """Before -> after needs a readable chapter transition at the boundary; two chapter
    cards in a row must not look the same."""
    errors, scenes, cards = [], story.get("scenes", []), story.get("transitions", [])
    for a, b in zip(scenes, scenes[1:]):
        if a.get("type") == "before-workflow" and b.get("type") in {"ai-handoff", "after-workflow"}:
            boundary = float(b.get("start_sec", 0))
            if not any(float(t.get("start_sec", -9)) - 0.01 <= boundary <= float(t.get("end_sec", -9)) + 0.01 for t in cards):
                errors.append(f"{a.get('id')} -> {b.get('id')}: add a readable chapter transition that ends at {boundary:g}s (before -> after)")
    for a, b in zip(cards, cards[1:]):
        if a.get("label") == b.get("label") or (a.get("color") == b.get("color") and a.get("symbol") == b.get("symbol")):
            errors.append(f"transitions at {a.get('start_sec')}s and {b.get('start_sec')}s look the same; change color, symbol, or wording")
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
    errors = check(story, args.story.resolve().parent.parent / "public", icon_names()) + transition_errors(story)
    report = {"ok": not errors, "errors": errors, "variety": variety_notes(story),
              "screen_words": {s.get("id"): screen_words(s, story) for s in story.get("scenes", [])}}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
