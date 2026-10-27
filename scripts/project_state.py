#!/usr/bin/env python3
"""Register one combined review and invalidate approval on input drift.

Approval covers meaning, not timing: in JSON inputs, `*_sec` fields are
ignored, and so are the story's `audio` and `sfx` fields, so fitting the
timeline to measured narration and adding the mix keep the approval. Any
other change, or a different voice, needs a new review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from safe_io import atomic_write_json, project_file

STATE = ".impact-video-state.json"


FILES = ("package", "claims", "story", "sources", "cover", "opening")
# Story fields filled in after approval by the audio steps.
POST_APPROVAL_KEYS = {"story": {"audio", "sfx"}}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_timing(value, drop: set[str]):
    if isinstance(value, dict):
        return {k: strip_timing(v, set()) for k, v in value.items()
                if not k.endswith("_sec") and k not in drop}
    if isinstance(value, list):
        return [strip_timing(v, set()) for v in value]
    return value


def content_digest(name: str, path: Path) -> str:
    """Hash a JSON input without its timing; hash other files byte for byte."""
    if path.suffix.lower() != ".json":
        return digest(path)
    data = strip_timing(json.loads(path.read_text(encoding="utf-8")), POST_APPROVAL_KEYS.get(name, set()))
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def read(project: Path) -> dict:
    path = project / STATE
    if not path.exists():
        raise SystemExit("Project not initialized")
    return json.loads(path.read_text(encoding="utf-8"))


def write(project: Path, state: dict) -> None:
    atomic_write_json(project / STATE, state)


def integrity(state: dict, project: Path, voice: str | None = None) -> tuple[bool, list[str]]:
    changed = []
    for name, item in state.get("review", {}).get("files", {}).items():
        try:
            path = project_file(project, item["path"])
        except (KeyError, TypeError, ValueError):
            changed.append(name)
            continue
        if not path.is_file():
            changed.append(name)
            continue
        try:
            current = content_digest(name, path) if item.get("mode") == "content" else digest(path)
        except (OSError, ValueError):
            changed.append(name)
            continue
        if current != item["sha256"]:
            changed.append(name)
    if voice and voice != state.get("review", {}).get("voice"):
        changed.append("voice")
    return not changed, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("project", type=Path)
    review = sub.add_parser("review")
    review.add_argument("project", type=Path)
    for flag in FILES:
        review.add_argument(f"--{flag}", required=True, type=Path)
    review.add_argument("--voice", required=True, help="voice provider and preset, e.g. fish:en-sawyer")
    approve = sub.add_parser("approve")
    approve.add_argument("project", type=Path)
    approve.add_argument("--by", required=True)
    status = sub.add_parser("status")
    status.add_argument("project", type=Path)
    status.add_argument("--voice", help="the voice about to be used; fails if it is not the reviewed one")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()

    if args.command == "init":
        project.mkdir(parents=True, exist_ok=True)
        write(project, {
            "schema_version": 2,
            "project_root": ".",
            "stage": "draft",
            "review": None,
            "approval": None,
        })
    elif args.command == "review":
        state = read(project)
        files = {}
        for name in FILES:
            path = getattr(args, name).expanduser().resolve()
            if not path.is_file():
                raise SystemExit(f"Missing review file for --{name}")
            try:
                relative = path.relative_to(project)
            except ValueError:
                raise SystemExit(f"Review file for --{name} must be inside the project directory") from None
            try:
                sha = content_digest(name, path)
            except ValueError:
                raise SystemExit(f"Review file for --{name} is not valid JSON") from None
            files[name] = {"path": relative.as_posix(), "sha256": sha, "mode": "content"}
        state.update({
            "stage": "review-ready",
            "review": {"created_at": datetime.now(timezone.utc).isoformat(), "files": files, "voice": args.voice},
            "approval": None,
        })
        write(project, state)
    elif args.command == "approve":
        state = read(project)
        if not state.get("review"):
            raise SystemExit("No combined review registered")
        ok, changed = integrity(state, project)
        if not ok:
            raise SystemExit(f"Review inputs changed: {', '.join(changed)}")
        state["stage"] = "approved"
        state["approval"] = {"by": args.by, "at": datetime.now(timezone.utc).isoformat()}
        write(project, state)
    else:
        state = read(project)
        ok, changed = integrity(state, project, args.voice) if state.get("review") else (True, [])
        if state.get("approval") and not ok:
            state["stage"] = "review-invalidated"
            state["approval"] = None
            write(project, state)
        print(json.dumps({"stage": state["stage"], "integrity_ok": ok, "changed": changed}, ensure_ascii=False, indent=2))
        return 0 if ok else 1
    print(json.dumps({"ok": True, "stage": read(project)["stage"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
