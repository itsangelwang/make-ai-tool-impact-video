#!/usr/bin/env python3
"""Check story.json beats (shots, icons, timings) before rendering the template."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ICON_FILE = Path(__file__).resolve().parent.parent / "assets" / "remotion-template" / "src" / "components" / "Icon.jsx"


def icon_names(icon_file: Path = ICON_FILE) -> set[str]:
    return set(re.findall(r"^\s{2}([a-z]+):\s*<>", icon_file.read_text(encoding="utf-8"), flags=re.MULTILINE))


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
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("story", type=Path, help="video/src/story.json")
    args = parser.parse_args()
    story = json.loads(args.story.read_text(encoding="utf-8"))
    errors = check(story, args.story.resolve().parent.parent / "public", icon_names())
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
