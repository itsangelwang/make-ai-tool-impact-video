#!/usr/bin/env python3
"""Register one combined review and invalidate approval on input drift."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

STATE = ".impact-video-state.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(project: Path) -> dict:
    path = project / STATE
    if not path.exists():
        raise SystemExit("Project not initialized")
    return json.loads(path.read_text(encoding="utf-8"))


def write(project: Path, state: dict) -> None:
    (project / STATE).write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def integrity(state: dict, project: Path) -> tuple[bool, list[str]]:
    changed = []
    for name, item in state.get("review", {}).get("files", {}).items():
        path = project / item["path"]
        if not path.is_file() or digest(path) != item["sha256"]:
            changed.append(name)
    return not changed, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("project", type=Path)
    review = sub.add_parser("review")
    review.add_argument("project", type=Path)
    for flag in ("package", "claims", "story", "sources", "cover", "opening"):
        review.add_argument(f"--{flag}", required=True, type=Path)
    approve = sub.add_parser("approve")
    approve.add_argument("project", type=Path)
    approve.add_argument("--by", required=True)
    status = sub.add_parser("status")
    status.add_argument("project", type=Path)
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
        for name in ("package", "claims", "story", "sources", "cover", "opening"):
            path = getattr(args, name).expanduser().resolve()
            if not path.is_file():
                raise SystemExit(f"Missing review file: {path}")
            try:
                relative = path.relative_to(project)
            except ValueError:
                raise SystemExit(f"Review file must be inside the project directory: {path}") from None
            files[name] = {"path": relative.as_posix(), "sha256": digest(path)}
        state.update({
            "stage": "review-ready",
            "review": {"created_at": datetime.now(timezone.utc).isoformat(), "files": files},
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
        ok, changed = integrity(state, project) if state.get("review") else (True, [])
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
