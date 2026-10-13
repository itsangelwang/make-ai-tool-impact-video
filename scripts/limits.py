"""Shared numeric limits. Edit limits.json, not the individual scripts."""

from __future__ import annotations

import json
from pathlib import Path

LIMITS = json.loads((Path(__file__).with_name("limits.json")).read_text(encoding="utf-8"))


def lang_key(language: str) -> str:
    return "en" if str(language).startswith("en") else "zh"


def max_duration(duration_exception: str | None) -> float:
    key = "extended_max" if duration_exception else "max"
    return LIMITS["duration_sec"][key]
