#!/usr/bin/env python3
"""Validate the one-minute story and its evidence ledger."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCENE_TYPES = {
    "pain-hook", "before-workflow", "ai-handoff", "after-workflow",
    "before-after", "human-check", "next-action",
}
READINESS = {"use-now", "try-now", "watch", "future"}
LEVELS = {"observed", "vendor-claim", "inference", "hypothesis"}
SOURCE_TYPES = {"official", "independent", "community", "user-provided"}
REQUIRED = {
    "schema_version", "tool", "audience", "task", "before_steps", "friction",
    "ai_change", "after_steps", "human_check", "readiness", "next_action",
    "narration", "scenes",
}


def load(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def han_count(text: str) -> int:
    return len(re.findall(r"[\u3400-\u9fff]", text))


def validate(package: dict, ledger: dict) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED - package.keys())
    if missing:
        errors.append(f"package missing: {', '.join(missing)}")
        return errors
    if package["schema_version"] != 1:
        errors.append("schema_version must be 1")
    tool = package["tool"]
    if not isinstance(tool, dict) or not all(tool.get(k) for k in ("name", "url", "one_line_capability")):
        errors.append("tool requires name, url, and one_line_capability")
    if not isinstance(package["before_steps"], list) or not 2 <= len(package["before_steps"]) <= 3:
        errors.append("before_steps must contain 2-3 steps")
    if not isinstance(package["after_steps"], list) or not 2 <= len(package["after_steps"]) <= 4:
        errors.append("after_steps must contain 2-4 steps")
    if package["readiness"] not in READINESS:
        errors.append(f"readiness must be one of {sorted(READINESS)}")
    narration = package["narration"]
    count = han_count(narration)
    if not 150 <= count <= 190:
        errors.append(f"narration must contain 150-190 Han characters; got {count}")
    if re.search(r"[（(](画面|镜头|转场|字幕|特效)|\[(画面|镜头|转场|字幕|特效)", narration):
        errors.append("narration contains stage directions")
    if re.match(r"^.{0,12}(公司|模型|发布了|推出了)", narration):
        errors.append("narration opens with a technical release instead of the task pain")

    scenes = package["scenes"]
    if not isinstance(scenes, list) or not 5 <= len(scenes) <= 7:
        errors.append("scenes must contain 5-7 entries")
        scenes = []
    seen_types, used_claims = set(), set()
    previous_end = 0.0
    for index, scene in enumerate(scenes):
        required = {"id", "type", "purpose", "start_sec", "end_sec", "headline", "visual", "claim_ids"}
        absent = required - scene.keys()
        if absent:
            errors.append(f"scene {index} missing: {', '.join(sorted(absent))}")
            continue
        if scene["type"] not in SCENE_TYPES:
            errors.append(f"scene {index} has unsupported type: {scene['type']}")
        seen_types.add(scene["type"])
        if abs(float(scene["start_sec"]) - previous_end) > 0.01:
            errors.append(f"scene {index} is not contiguous")
        if float(scene["end_sec"]) <= float(scene["start_sec"]):
            errors.append(f"scene {index} has non-positive duration")
        previous_end = float(scene["end_sec"])
        if not scene["purpose"] or not scene["visual"]:
            errors.append(f"scene {index} requires purpose and visual")
        used_claims.update(scene["claim_ids"])
    if scenes and scenes[0].get("type") != "pain-hook":
        errors.append("first scene must be pain-hook")
    if scenes and not 55 <= previous_end <= 65:
        errors.append(f"story duration must be 55-65 seconds; got {previous_end:g}")
    required_types = {"pain-hook", "before-workflow", "ai-handoff", "after-workflow", "human-check", "next-action"}
    if not required_types.issubset(seen_types):
        errors.append(f"missing required scene types: {', '.join(sorted(required_types - seen_types))}")

    claims = ledger.get("claims") if isinstance(ledger, dict) else None
    if not isinstance(claims, list) or not claims:
        errors.append("claim ledger requires a non-empty claims list")
        claims = []
    claim_ids = set()
    for index, claim in enumerate(claims):
        required = {"id", "text", "level", "source_url", "source_type", "accessed_at", "support", "boundary"}
        absent = required - claim.keys()
        if absent:
            errors.append(f"claim {index} missing: {', '.join(sorted(absent))}")
            continue
        claim_ids.add(claim["id"])
        if claim["level"] not in LEVELS:
            errors.append(f"claim {claim['id']} has invalid level")
        if claim["source_type"] not in SOURCE_TYPES:
            errors.append(f"claim {claim['id']} has invalid source_type")
        if claim["level"] in {"observed", "vendor-claim"} and not claim["source_url"]:
            errors.append(f"claim {claim['id']} requires a source URL")
    unknown = used_claims - claim_ids
    if unknown:
        errors.append(f"scenes reference unknown claims: {', '.join(sorted(unknown))}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    errors = validate(load(args.package), load(args.ledger))
    result = {"ok": not errors, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
