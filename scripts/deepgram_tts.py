#!/usr/bin/env python3
"""Generate narration with Deepgram Flux TTS without persisting the API key."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


FLUX_SPEEDS = {0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15}


def build_url(model: str, speed: float, expressivity: int, encoding: str) -> str:
    if not model.startswith("flux-") or not model.endswith("-en"):
        raise ValueError("Flux model must look like flux-hannah-en")
    if speed not in FLUX_SPEEDS:
        raise ValueError(f"speed must be one of {sorted(FLUX_SPEEDS)}")
    if expressivity not in {-2, -1, 0, 1, 2}:
        raise ValueError("expressivity must be an integer from -2 to 2")
    if encoding not in {"mp3", "opus", "flac", "aac"}:
        raise ValueError("encoding must be mp3, opus, flac, or aac")
    query = urllib.parse.urlencode({
        "model": model,
        "speed": str(speed),
        "expressivity": str(expressivity),
        "encoding": encoding,
    })
    return f"https://api.deepgram.com/v2/speak?{query}"


def narration_from_args(args: argparse.Namespace) -> str:
    if args.text:
        return args.text.strip()
    data = json.loads(args.script.read_text(encoding="utf-8"))
    narration = str(data.get("narration", "")).strip()
    if not narration:
        raise ValueError("script JSON requires a non-empty narration field")
    return narration


def synthesize(text: str, output: Path, model: str, speed: float, expressivity: int, encoding: str) -> None:
    token = os.environ.get("DEEPGRAM_API_KEY")
    if not token:
        raise RuntimeError("DEEPGRAM_API_KEY is not set")
    request = urllib.request.Request(
        build_url(model, speed, expressivity, encoding),
        data=json.dumps({"text": text}).encode("utf-8"),
        headers={"Authorization": f"Token {token}", "Content-Type": "application/json"},
        method="POST",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(response.read())
        temporary.replace(output)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Deepgram returned HTTP {error.code}: {detail}") from error
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--script", type=Path)
    source.add_argument("--text")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="flux-hannah-en")
    parser.add_argument("--speed", type=float, default=0.95)
    parser.add_argument("--expressivity", type=int, default=1)
    parser.add_argument("--encoding", default="mp3")
    args = parser.parse_args()
    try:
        text = narration_from_args(args)
        synthesize(text, args.output, args.model, args.speed, args.expressivity, args.encoding)
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "output": str(args.output), "model": args.model}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
