"""Shared numeric limits. Edit limits.json, not the individual scripts."""

from __future__ import annotations

import json
from pathlib import Path

LIMITS = json.loads((Path(__file__).with_name("limits.json")).read_text(encoding="utf-8"))


ENGLISH = ("en-US", "en-GB", "en-AU")


def lang_key(language: str) -> str:
    """Videos are English-only. Chinese titles and post copy live in social-titles.md."""
    if str(language) not in ENGLISH:
        raise ValueError(f"language must be one of {', '.join(ENGLISH)}; videos are English-only (got {language!r})")
    return "en"


def max_duration(duration_exception: str | None) -> float:
    key = "extended_max" if duration_exception else "max"
    return LIMITS["duration_sec"][key]
