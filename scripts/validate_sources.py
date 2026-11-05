#!/usr/bin/env python3
"""Validate asset provenance and publication rights.

Preview (default): an asset whose rights are not "cleared" is listed under
publication_blockers as a warning, and the check still passes so a review can go ahead.
--delivery: the same blockers fail the check. Use it before delivering the final video.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RIGHTS = {"cleared", "internal-only", "replace", "unknown"}
ROLES = {"product-evidence", "context", "illustration", "user-provided", "code-native"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--delivery", action="store_true", help="fail when any asset is not cleared for publication")
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
    if args.delivery:
        errors.extend(f"not cleared for publication: {path}" for path in blockers)
    mode = "delivery" if args.delivery else "preview"
    report = {"ok": not errors, "mode": mode, "errors": errors, "publication_blockers": blockers}
    if blockers and not args.delivery:
        report["warning"] = "preview only: these assets block delivery until their rights are cleared"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
