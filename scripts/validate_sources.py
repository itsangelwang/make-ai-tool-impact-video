#!/usr/bin/env python3
"""Validate asset provenance and publication rights."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RIGHTS = {"cleared", "internal-only", "replace", "unknown"}
ROLES = {"product-evidence", "context", "illustration", "user-provided", "code-native"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    data = json.loads(args.ledger.read_text(encoding="utf-8"))
    errors, blockers = [], []
    for index, asset in enumerate(data.get("assets", [])):
        missing = {"path", "origin", "rights", "role", "attribution"} - asset.keys()
        if missing:
            errors.append(f"asset {index} missing: {', '.join(sorted(missing))}")
            continue
        if asset["rights"] not in RIGHTS:
            errors.append(f"asset {index} has invalid rights")
        if asset["role"] not in ROLES:
            errors.append(f"asset {index} has invalid role")
        if asset["rights"] != "cleared":
            blockers.append(asset["path"])
        if asset.get("generated") and asset["role"] == "product-evidence":
            errors.append(f"asset {index}: generated media cannot be product evidence")
    print(json.dumps({"ok": not errors, "errors": errors, "publication_blockers": blockers}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
