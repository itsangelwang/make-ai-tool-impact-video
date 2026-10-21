#!/usr/bin/env python3
"""Validate the one-minute story and its evidence ledger."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from limits import LIMITS, lang_key, max_duration

SCENE_TYPES = {
    "pain-hook", "before-workflow", "ai-handoff", "after-workflow",
    "before-after", "human-check", "next-action",
}
READINESS = {"use-now", "try-now", "watch", "future"}
LEVELS = {"observed", "vendor-claim", "inference", "hypothesis"}
SOURCE_TYPES = {"official", "independent", "community", "user-provided"}
COVERAGE_DECISIONS = {"make", "change-angle", "skip"}
REQUIRED = {
    "schema_version", "language", "market", "tool", "audience", "task", "before_steps", "friction",
    "ai_change", "after_steps", "human_check", "readiness", "next_action",
    "narration", "scenes", "coverage",
}


def load(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def han_count(text: str) -> int:
    return len(re.findall(r"[\u3400-\u9fff]", text))


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b", text, flags=re.UNICODE))


def coverage_errors(coverage) -> list[str]:
    if not isinstance(coverage, dict):
        return ["coverage must be an object; see references/topic-check.md"]
    errors = []
    if not coverage.get("checked_at") or not coverage.get("our_angle"):
        errors.append("coverage requires checked_at and our_angle")
    existing = coverage.get("existing")
    if not isinstance(existing, list):
        errors.append("coverage.existing must list the official and creator videos checked")
    else:
        for index, item in enumerate(existing):
            if not isinstance(item, dict) or item.get("by") not in {"official", "creator"} or not item.get("url") or not item.get("shows"):
                errors.append(f"coverage.existing {index} requires by (official or creator), url, and shows")
    decision = coverage.get("decision")
    if decision not in COVERAGE_DECISIONS:
        errors.append(f"coverage.decision must be one of {sorted(COVERAGE_DECISIONS)}")
    elif decision == "skip":
        errors.append("coverage.decision is skip; tell the user why and propose another topic instead of making this video")
    return errors


def validate(package: dict, ledger: dict, duration_exception: str | None = None) -> list[str]:
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
    for field in ("before_steps", "after_steps"):
        low, high = LIMITS[field]["min"], LIMITS[field]["max"]
        if not isinstance(package[field], list) or not low <= len(package[field]) <= high:
            errors.append(f"{field} must contain {low}-{high} steps")
    errors.extend(coverage_errors(package["coverage"]))
    if package["readiness"] not in READINESS:
        errors.append(f"readiness must be one of {sorted(READINESS)}")
    language = package["language"]
    if language not in {"zh-CN", "en-US", "en-GB", "en-AU"}:
        errors.append("language must be zh-CN, en-US, en-GB, or en-AU")
    narration = package["narration"]
    key = lang_key(language)
    bounds = LIMITS["narration"][key]
    count = word_count(narration) if key == "en" else han_count(narration)
    if not bounds["min"] <= count <= bounds["max"]:
        errors.append(f"narration must contain {bounds['min']}-{bounds['max']} {bounds['unit']}; got {count}")
    if re.search(r"[（(](画面|镜头|转场|字幕|特效)|\[(画面|镜头|转场|字幕|特效)", narration):
        errors.append("narration contains stage directions")
    if re.match(r"^.{0,12}(公司|模型|发布了|推出了)", narration):
        errors.append("narration opens with a technical release instead of the task pain")
    if str(language).startswith("en") and re.match(
        r"^\s*(?:today|introducing|[\w.-]+\s+(?:has\s+)?(?:launched|released|announced))\b",
        narration,
        flags=re.IGNORECASE,
    ):
        errors.append("English narration opens with a product release instead of the task pain")

    scenes = package["scenes"]
    if not isinstance(scenes, list) or not LIMITS["scenes"]["min"] <= len(scenes) <= LIMITS["scenes"]["max"]:
        errors.append(f"scenes must contain {LIMITS['scenes']['min']}-{LIMITS['scenes']['max']} entries")
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
    brand = package.get("brand")
    if scenes and brand:
        start, end = float(brand.get("start_sec", -1)), float(brand.get("end_sec", -1))
        low, high = LIMITS["brand_card_sec"]["min"], LIMITS["brand_card_sec"]["max"]
        if not brand.get("name"):
            errors.append("brand requires a name")
        if abs(start - previous_end) > 0.01:
            errors.append("brand card must start where the last scene ends")
        if not low - 0.01 <= end - start <= high + 0.01:
            errors.append(f"brand card must last {low}-{high} seconds")
        previous_end = max(previous_end, end)
    if scenes and scenes[0].get("type") != "pain-hook":
        errors.append("first scene must be pain-hook")
    min_sec, max_sec = LIMITS["duration_sec"]["min"], max_duration(duration_exception)
    if scenes and not min_sec <= previous_end <= max_sec:
        hint = "" if duration_exception else f" (pass --duration-exception to allow up to {LIMITS['duration_sec']['extended_max']})"
        errors.append(f"story duration must be {min_sec}-{max_sec} seconds; got {previous_end:g}{hint}")
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
    parser.add_argument(
        "--duration-exception",
        help="reason the review needs up to 75 seconds; echoed in the result",
    )
    args = parser.parse_args()
    errors = validate(load(args.package), load(args.ledger), args.duration_exception)
    result = {"ok": not errors, "errors": errors, "duration_exception": args.duration_exception}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
