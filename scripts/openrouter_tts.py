#!/usr/bin/env python3
"""Generate narration through OpenRouter TTS without persisting the API key."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import ssl
import subprocess  # nosec B404
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


ENDPOINT = "https://openrouter.ai/api/v1/audio/speech"
OPENROUTER_KEY = re.compile(r"\Ask-or-v1-[A-Za-z0-9_-]{20,}\Z")


def api_key_from_environment() -> str:
    """Read a key without persisting it and reject curl-config control characters."""
    token = os.environ.get("OPENROUTER_API_KEY", "").strip().strip('"').strip("'").strip()
    if not token:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    if not OPENROUTER_KEY.fullmatch(token):
        raise RuntimeError("OPENROUTER_API_KEY has an invalid format")
    return token


def tls_context() -> ssl.SSLContext:
    """Use certifi on Python installs that are not linked to the macOS trust store."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def narration_from_args(args: argparse.Namespace) -> str:
    if args.text:
        return args.text.strip()
    data = json.loads(args.script.read_text(encoding="utf-8"))
    narration = str(data.get("narration", "")).strip()
    if not narration:
        raise ValueError("script JSON requires a non-empty narration field")
    return narration


def synthesize(text: str, output: Path, model: str, voice: str, speed: float) -> None:
    token = api_key_from_environment()
    if not 0.7 <= speed <= 1.3:
        raise ValueError("speed must be between 0.7 and 1.3")
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": "mp3",
        "speed": speed,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    payload_file = None
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as handle:
            payload_file = Path(handle.name)
            json.dump(payload, handle)
        with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as handle:
            temporary = Path(handle.name)
        config = "\n".join([
            f'url = "{ENDPOINT}"',
            'request = "POST"',
            f'header = "Authorization: Bearer {token}"',
            'header = "Content-Type: application/json"',
            'header = "X-Title: make-ai-tool-impact-video"',
            f'data-binary = "@{payload_file}"',
            f'output = "{temporary}"',
            'silent',
            'show-error',
            'fail-with-body',
        ])
        curl = shutil.which("curl")
        if not curl:
            raise RuntimeError("curl is required")
        result = subprocess.run(  # nosec B603
            [curl, "--config", "-"],
            input=config,
            text=True,
            capture_output=True,
            timeout=120,
            check=False,
        )
        if result.returncode:
            detail = temporary.read_text(encoding="utf-8", errors="replace")[:500]
            raise RuntimeError(f"OpenRouter request failed: {detail or result.stderr.strip()}")
        temporary.replace(output)
    finally:
        if payload_file and payload_file.exists():
            payload_file.unlink()
        if temporary and temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--script", type=Path)
    source.add_argument("--text")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="deepgram/flux-tts:free")
    parser.add_argument("--voice", default="flux-hannah-en")
    parser.add_argument("--speed", type=float, default=0.95)
    args = parser.parse_args()
    try:
        text = narration_from_args(args)
        synthesize(text, args.output, args.model, args.voice, args.speed)
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "output": args.output.name, "model": args.model, "voice": args.voice}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
