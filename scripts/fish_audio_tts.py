#!/usr/bin/env python3
"""Generate Fish Audio speech without logging or persisting credentials."""

from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


ENDPOINT = "https://api.fish.audio/v1/tts"
SAFE_SECRET = re.compile(r"\A[^\s\x00-\x1f\x7f]{20,512}\Z")
SAFE_REFERENCE_ID = re.compile(r"\A[A-Za-z0-9_-]{8,128}\Z")
DEFAULT_ENV_FILE = Path("~/.config/make-ai-tool-impact-video/.env")
MODELS = {"s1", "s2-pro", "s2.1-pro", "s2.1-pro-free", "drama-3"}
# Approved voice presets; explicit flags override any preset field.
PRESETS = {
    "en-sawyer": {
        "reference_id": "fa4c9eb3dccc4806b382b40d61c6b10a",  # Fish Official "Sawyer", US male
        "model": "drama-3",
        "temperature": 0.85,
        "speed": 1.08,
    },
}
DEFAULTS = {"model": "s2.1-pro", "temperature": 0.7, "speed": 1.0}


def load_env(path: Path) -> None:
    """Load simple KEY=VALUE entries without overriding the caller environment."""
    path = path.expanduser()
    if not path.is_file():
        return
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"invalid .env entry on line {number}")
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            raise ValueError(f"invalid .env key on line {number}")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def secret_from_environment() -> str:
    token = os.environ.get("FISH_AUDIO_API_KEY", "").strip()
    if not token:
        raise RuntimeError("FISH_AUDIO_API_KEY is not set")
    if not SAFE_SECRET.fullmatch(token):
        raise RuntimeError("FISH_AUDIO_API_KEY has an invalid format")
    return token


def reference_id(value: str | None) -> str:
    selected = (value or os.environ.get("FISH_AUDIO_REFERENCE_ID", "")).strip()
    if not selected:
        raise RuntimeError("Fish Audio requires --reference-id or FISH_AUDIO_REFERENCE_ID")
    if not SAFE_REFERENCE_ID.fullmatch(selected):
        raise RuntimeError("Fish Audio reference ID has an invalid format")
    return selected


def tls_context() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def narration(args: argparse.Namespace) -> str:
    if args.text:
        result = args.text.strip()
    else:
        data = json.loads(args.script.read_text(encoding="utf-8"))
        result = str(data.get("narration", "")).strip()
    if not result:
        raise ValueError("narration must not be empty")
    return result


def synthesize(
    text: str,
    output: Path,
    token: str,
    voice_id: str,
    model: str,
    speed: float,
    temperature: float,
) -> None:
    payload = json.dumps({
        "text": text,
        "reference_id": voice_id,
        "temperature": temperature,
        "top_p": 0.7,
        "prosody": {"speed": speed, "volume": 0, "normalize_loudness": True},
        "normalize": True,
        "format": "mp3",
        "sample_rate": 44100,
        "mp3_bitrate": 128,
        "latency": "normal",
        "condition_on_previous_chunks": True,
    }).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "model": model,
        },
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with urllib.request.urlopen(request, context=tls_context(), timeout=180) as response:
            with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as handle:
                temporary = Path(handle.name)
                while chunk := response.read(65536):
                    handle.write(chunk)
        temporary.replace(output)
    except urllib.error.HTTPError as error:
        # Provider responses can echo submitted text or sensitive request data.
        raise RuntimeError(f"Fish Audio returned HTTP {error.code}") from None
    except urllib.error.URLError as error:
        raise RuntimeError("Fish Audio request failed; check connectivity and TLS configuration") from None
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text")
    source.add_argument("--script", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument("--preset", choices=sorted(PRESETS))
    parser.add_argument("--reference-id")
    parser.add_argument("--model", choices=sorted(MODELS))
    parser.add_argument("--speed", type=float)
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    preset = PRESETS.get(args.preset, {})
    for key, value in DEFAULTS.items():
        if getattr(args, key) is None:
            setattr(args, key, preset.get(key, value))
    if args.reference_id is None:
        args.reference_id = preset.get("reference_id")
    try:
        load_env(args.env_file)
        text = narration(args)
        voice_id = reference_id(args.reference_id)
        if not 0.8 <= args.speed <= 1.2:
            raise ValueError("speed must be between 0.8 and 1.2")
        if not 0 <= args.temperature <= 1:
            raise ValueError("temperature must be between 0 and 1")
        if args.dry_run:
            print(json.dumps({
                "ok": True,
                "dry_run": True,
                "model": args.model,
                "reference_id_present": bool(voice_id),
                "characters": len(text),
                "output": str(args.output),
            }))
            return 0
        token = secret_from_environment()
        synthesize(text, args.output, token, voice_id, args.model, args.speed, args.temperature)
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "output": str(args.output), "model": args.model}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
