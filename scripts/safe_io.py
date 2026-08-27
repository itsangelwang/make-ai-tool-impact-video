"""Small file-safety helpers shared by the command-line scripts."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def atomic_write_text(path: Path, text: str) -> None:
    """Replace a file atomically without following a destination symlink."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def project_file(project: Path, relative: str) -> Path:
    """Resolve an untrusted state-file path while keeping it inside the project."""
    candidate = (project / relative).resolve()
    try:
        candidate.relative_to(project.resolve())
    except ValueError as error:
        raise ValueError("review state contains a path outside the project") from error
    return candidate
