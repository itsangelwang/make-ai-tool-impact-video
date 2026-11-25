#!/usr/bin/env python3
"""Check story.json before rendering: beats (shots, icons, timings), reading load per
screen, how long a screen stays unchanged, and variety between neighboring scenes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from limits import LIMITS

VIDEO_EXT = (".mov", ".mp4", ".webm")
ICON_FILE = Path(__file__).resolve().parent.parent / "assets" / "remotion-template" / "src" / "components" / "Icon.jsx"
# Scene types whose `visual` text the template shows in a box (an empty visual hides the box).
VISUAL_BOX = {"human-check", "next-action", "ai-handoff"}
BEATS = ("call_end", "toast", "new_feature", "stoplist", "shot", "compare", "flow", "scrub", "roles", "checks", "access", "plans", "fix", "replay", "send", "tryit", "strips")


def icon_names(icon_file: Path = ICON_FILE) -> set[str]:
    return set(re.findall(r"^\s{2}([a-z]+):\s*<>", icon_file.read_text(encoding="utf-8"), flags=re.MULTILINE))


def words(*texts) -> int:
    return sum(len(re.findall(r"[\w’'%$:-]+", str(t))) for t in texts if t)


def is_video(src) -> bool:
    return str(src or "").lower().endswith(VIDEO_EXT)


def board_texts(board: dict) -> list:
    texts = [board.get("title"), board.get("note")]
    for row in board.get("rows", []):
        texts += [row.get("name"), row.get("sub"), row.get("tally"), row.get("tally_note")]
    return texts


def stoplist_texts(stoplist: dict) -> list:
    texts = [stoplist.get("title"), stoplist.get("subtitle"), stoplist.get("badge"), (stoplist.get("extra") or {}).get("label")]
    return texts + [row.get("label") for row in stoplist.get("rows", [])]


def compare_texts(compare: dict) -> list:
    texts = [(compare.get("note") or {}).get("text"), (compare.get("stamp") or {}).get("label")]
    for row in compare.get("rows", []):
        texts += [row.get("input"), row.get("result")]
    return texts


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
    texts += [(shot.get("stamp") or {}).get("label"), (shot.get("summary") or {}).get("text")]
    # shot.board slides over the whole screenshot, hiding the callout inside it
    texts += board_texts(shot["board"]) if shot.get("board") else []
    texts += [callout.get("title"), callout.get("note")] if not shot.get("board") or words(callout.get("title"), callout.get("note")) > words(*board_texts(shot["board"])) else []
    texts += stoplist_texts(scene["stoplist"]) if scene.get("stoplist") else []
    texts += compare_texts(scene["compare"]) if scene.get("compare") else []
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
    for strip in scene.get("strips") or []:
        texts.append(strip.get("label"))
        texts += [f"{s.get('label')} {s.get('sec')} s" for s in strip.get("segments", []) if s.get("label")]
    plans = scene.get("plans") or {}
    texts += [plans.get("title"), plans.get("feature")] + [plan.get("name") for plan in plans.get("plans", [])]
    custom = any(scene.get(key) for key in ("stoplist", "compare", "shot", "flow", "scrub", "fix", "replay", "plans", "tryit", "asset", "strips", "call_end", "toast"))
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
    num = lambda v: isinstance(v, (int, float))
    # A playing recording keeps changing: count every second it plays (still before
    # hold_start_sec, still after freeze_at_sec), and the alt clip from its switch onward.
    end = 60.0
    if is_video(shot.get("src")):
        start = shot.get("hold_start_sec", 0) if num(shot.get("hold_start_sec")) else 0
        stop = shot["freeze_at_sec"] if num(shot.get("freeze_at_sec")) else end
        times += [start + n for n in range(int(max(0, stop - start)) + 1)] + ([stop] if stop < end else [])
    alt = shot.get("alt") or {}
    if num(alt.get("at_sec")):
        times += [alt["at_sec"]] + ([alt["at_sec"] + n for n in range(1, int(end))] if is_video(alt.get("src")) else [])
    for mask in shot.get("masks", []):
        times += [mask[k] for k in ("from_sec", "until_sec") if num(mask.get(k))]
    board = shot.get("board") or {}
    if num(board.get("at_sec")):
        times.append(board["at_sec"])
        for row in board.get("rows", []):
            times += [t for t in row.get("mark_at_sec", []) if num(t)] + ([row["tally_at_sec"]] if num(row.get("tally_at_sec")) else [])
    stoplist = scene.get("stoplist") or {}
    if stoplist:
        times.append(stoplist.get("avatar_at_sec", 0.2) if stoplist.get("avatar") else 0)
        times += [row["at_sec"] for row in stoplist.get("rows", []) if num(row.get("at_sec"))]
        if num((stoplist.get("extra") or {}).get("at_sec")):
            times.append(stoplist["extra"]["at_sec"])
        if num(stoplist.get("shuffle_at_sec")):
            times += [stoplist["shuffle_at_sec"], stoplist["shuffle_at_sec"] + 4 / 30]  # rows hop, "?" pops
    compare = scene.get("compare") or {}
    for row in compare.get("rows", []):
        if num(row.get("at_sec")):
            times += [row["at_sec"], row["at_sec"] + 18 / 30]  # the input, then where its pin landed
    for key in ("note", "stamp"):
        if num((compare.get(key) or {}).get("at_sec")):
            times.append(compare[key]["at_sec"])
    frames, frame_sec = shot.get("frames") or [], shot.get("frame_sec")
    if len(frames) > 1 and isinstance(frame_sec, (int, float)) and frame_sec > 0:
        # a looping GIF keeps moving: count the start of every loop as a visible change
        loop = len(frames) * frame_sec
        times += [n * loop for n in range(1, int(60 / loop) + 1)]
    times += [s["at_sec"] for s in scene.get("strips") or [] if isinstance(s.get("at_sec"), (int, float))]
    times += [band["at_sec"] for band in shot.get("focus", []) if isinstance(band.get("at_sec"), (int, float))]
    times += [item["at_sec"] for item in scene.get("flow", []) if isinstance(item.get("at_sec"), (int, float))]
    times += [t for t in scene.get("steps_at_sec", []) if isinstance(t, (int, float))]
    if isinstance(scene.get("checks_at_sec"), (int, float)):
        times.append(scene["checks_at_sec"])
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
            parts = [sub for sub in ("frames", "zoom", "drag", "type", "click", "focus", "callout", "stamp", "board", "alt") if key == "shot" and scene["shot"].get(sub)]
            present.append(f"{key}({','.join(parts)})" if parts else key)
    return "+".join(present) or scene.get("type", "?")


def shot_errors(sid: str, shot: dict, crop: dict, length: float, public_dir: Path, errors: list, timed) -> None:
    """Recording playback, the alt switch, masks, the full-bleed width and the tally board."""
    num = lambda v: isinstance(v, (int, float))
    if not num(shot.get("width", 936)) or not 600 <= shot.get("width", 936) <= 1080:
        errors.append(f"{sid}.shot.width must be 600-1080 frame pixels (1080 = full bleed)")
    video_keys = [k for k in ("from_sec", "rate", "hold_start_sec", "freeze_at_sec") if k in shot]
    if video_keys and not is_video(shot.get("src")):
        errors.append(f"{sid}.shot.{video_keys[0]} needs a .mov/.mp4/.webm src")
    if "from_sec" in shot and (not num(shot["from_sec"]) or shot["from_sec"] < 0):
        errors.append(f"{sid}.shot.from_sec must be seconds into the recording")
    if "rate" in shot and (not num(shot["rate"]) or not 0.25 <= shot["rate"] <= 4):
        errors.append(f"{sid}.shot.rate must be 0.25-4")
    for key in ("hold_start_sec", "freeze_at_sec"):
        if key in shot:
            timed(f"{sid}.shot", shot, length, keys=(key,))
    if num(shot.get("hold_start_sec")) and num(shot.get("freeze_at_sec")) and shot["freeze_at_sec"] <= shot["hold_start_sec"]:
        errors.append(f"{sid}.shot.freeze_at_sec must come after hold_start_sec")
    alt = shot.get("alt")
    if alt is not None:
        timed(f"{sid}.shot.alt", alt, length)
        ac = (alt or {}).get("crop") or {}
        if not alt.get("src") or not num(alt.get("source_width")):
            errors.append(f"{sid}.shot.alt requires src and source_width")
        elif not (public_dir / alt["src"]).is_file():
            errors.append(f"{sid}.shot.alt.src not found under public/: {alt['src']}")
        if not all(num(ac.get(k)) for k in "xywh") or ac.get("w", 0) <= 0 or ac.get("h", 0) <= 0:
            errors.append(f"{sid}.shot.alt.crop requires numeric x, y, and positive w, h")
        elif crop.get("h") and abs(ac["w"] / ac["h"] - crop["w"] / crop["h"]) > 0.03 * crop["w"] / crop["h"]:
            errors.append(f"{sid}.shot.alt.crop must have the same aspect ratio as shot.crop")
    for index, mask in enumerate(shot.get("masks", [])):
        where = f"{sid}.shot.masks[{index}]"
        if not all(num(mask.get(k)) for k in "xywh") or mask.get("w", 0) <= 0 or mask.get("h", 0) <= 0:
            errors.append(f"{where} requires x, y and positive w, h in source pixels")
        if mask.get("style", "blur") not in ("tile", "bar", "blur"):
            errors.append(f"{where}.style must be tile, bar or blur")
        for key in ("from_sec", "until_sec"):
            if key in mask and (not num(mask[key]) or not 0 <= mask[key] <= length):
                errors.append(f"{where}.{key} must be seconds inside the scene")
    board = shot.get("board")
    if board is not None:
        timed(f"{sid}.shot.board", board, length)
        rows = (board or {}).get("rows") or []
        if not board.get("title") or not 1 <= len(rows) <= 3:
            errors.append(f"{sid}.shot.board requires title and 1-3 rows")
        for index, row in enumerate(rows):
            where = f"{sid}.shot.board.rows[{index}]"
            marks, mark_at = str(row.get("marks", "")), row.get("mark_at_sec") or []
            if not row.get("name") or not marks or set(marks) - set("xv-"):
                errors.append(f"{where} requires name and marks made of x (wrong), v (right) and - (blank)")
            if len(mark_at) != len(marks) or not all(num(t) and 0 <= t < length for t in mark_at):
                errors.append(f"{where}.mark_at_sec needs one time inside the scene per mark")
            timed(where, row, length, keys=("tally_at_sec",))


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
            if "frames" in shot:
                frames = shot.get("frames")
                if not isinstance(frames, list) or len(frames) < 2:
                    errors.append(f"{sid}.shot.frames needs at least two images (the real GIF frames)")
                else:
                    for src in frames:
                        if not (public_dir / str(src)).is_file():
                            errors.append(f"{sid}.shot.frames image not found under public/: {src}")
                if not isinstance(shot.get("frame_sec"), (int, float)) or shot.get("frame_sec", 0) <= 0:
                    errors.append(f"{sid}.shot.frame_sec must be the GIF's own seconds per frame")
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
            shot_errors(sid, shot, crop, length, public_dir, errors, timed)
        stoplist = scene.get("stoplist")
        if stoplist is not None:
            rows = (stoplist or {}).get("rows") or []
            if not stoplist.get("title") or not 1 <= len(rows) <= 6:
                errors.append(f"{sid}.stoplist requires title and 1-6 rows")
            for index, row in enumerate(rows):
                timed(f"{sid}.stoplist.rows[{index}]", row, length)
                if not row.get("label"):
                    errors.append(f"{sid}.stoplist.rows[{index}] requires label")
                if row.get("icon") is not None:
                    icon(f"{sid}.stoplist.rows[{index}]", row["icon"])
            if stoplist.get("avatar") and not (public_dir / stoplist["avatar"]).is_file():
                errors.append(f"{sid}.stoplist.avatar not found under public/: {stoplist['avatar']}")
            if stoplist.get("extra") is not None:
                timed(f"{sid}.stoplist.extra", stoplist["extra"], length)
                if stoplist["extra"].get("icon") is not None:
                    icon(f"{sid}.stoplist.extra", stoplist["extra"]["icon"])
            for key in ("avatar_at_sec", "shuffle_at_sec"):
                if key in stoplist:
                    timed(f"{sid}.stoplist", stoplist, length, keys=(key,))
        compare = scene.get("compare")
        if compare is not None:
            rows = (compare or {}).get("rows") or []
            if not compare.get("img") or not isinstance(compare.get("img_width"), (int, float)):
                errors.append(f"{sid}.compare requires img and img_width")
            elif not (public_dir / compare["img"]).is_file():
                errors.append(f"{sid}.compare.img not found under public/: {compare['img']}")
            if not 1 <= len(rows) <= 3:
                errors.append(f"{sid}.compare needs 1-3 rows")
            for index, row in enumerate(rows):
                timed(f"{sid}.compare.rows[{index}]", row, length)
                rc, pin = row.get("crop") or {}, row.get("pin") or {}
                if not row.get("input") or not row.get("result") or not isinstance(row.get("ok"), bool):
                    errors.append(f"{sid}.compare.rows[{index}] requires input, result and ok (true/false)")
                if not all(isinstance(rc.get(k), (int, float)) for k in "xyw") or rc.get("w", 0) <= 0 or not all(isinstance(pin.get(k), (int, float)) for k in "xy"):
                    errors.append(f"{sid}.compare.rows[{index}] requires crop {{x, y, w}} and pin {{x, y}} in img pixels")
            for key in ("note", "stamp"):
                if compare.get(key) is not None:
                    timed(f"{sid}.compare.{key}", compare[key], length)
        strips = scene.get("strips")
        if strips is not None:
            if not isinstance(strips, list) or not 1 <= len(strips) <= 2:
                errors.append(f"{sid}.strips needs 1-2 strips")
            else:
                for index, strip in enumerate(strips):
                    timed(f"{sid}.strips[{index}]", strip, length)
                    segments = strip.get("segments") or []
                    if len(segments) < 2 or not all(isinstance(s.get("sec"), (int, float)) and s["sec"] > 0 for s in segments):
                        errors.append(f"{sid}.strips[{index}] needs 2+ segments, each with sec > 0")
        flow = scene.get("flow")
        if flow is not None and scene.get("type") == "next-action":
            errors.append(f"{sid}: no flow in the next-action scene; the user rejected boxed icon cards for next steps. Animate a concrete moment (tryit, plans, real UI) or leave it to the narration")
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


def cover_errors(story: dict, public_dir: Path) -> list[str]:
    """The designed cover (story.cover) needs a headline, a moment inside the video and a crop
    inside the 1080x1920 frame. Without story.cover the template falls back to a frame grab."""
    cover = story.get("cover")
    if cover is None:
        return []
    if not isinstance(cover, dict):
        return ["cover must be an object"]
    errors = []
    if not str(cover.get("headline", "")).strip():
        errors.append("cover.headline is required: the one promise the cover makes")
    duration = float(story.get("duration_sec", 0) or 0)
    at = cover.get("frame_sec", 2)
    if not isinstance(at, (int, float)) or not 0 <= at < duration:
        errors.append("cover.frame_sec must be a moment inside the video")
    crop = cover.get("crop")
    if crop is not None:
        if not all(isinstance(crop.get(k), (int, float)) for k in ("x", "y", "w", "h")) or crop["w"] <= 0 or crop["h"] <= 0:
            errors.append("cover.crop requires numeric x, y and positive w, h")
        elif crop["x"] < 0 or crop["y"] < 0 or crop["x"] + crop["w"] > 1080 or crop["y"] + crop["h"] > 1920:
            errors.append("cover.crop must stay inside the 1080x1920 frame")
    if cover.get("logo") and not (public_dir / cover["logo"]).is_file():
        errors.append(f"cover.logo not found under public/: {cover['logo']}")
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
    public = args.story.resolve().parent.parent / "public"
    errors = check(story, public, icon_names()) + transition_errors(story) + cover_errors(story, public)
    report = {"ok": not errors, "errors": errors, "variety": variety_notes(story),
              "screen_words": {s.get("id"): screen_words(s, story) for s in story.get("scenes", [])}}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
