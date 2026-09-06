#!/usr/bin/env python3
"""Validate the GoreeCloud website source-license and notice boundary.

The Apache-2.0 text is intentionally content-bound to the reviewed Git blob so a
future edit cannot silently change the governing software license. NOTICE and README
are validated separately because GoreeCloud branding and third-party marks are not
made reusable merely by living beside Apache-licensed source code.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LICENSE = ROOT / "LICENSE"
NOTICE = ROOT / "NOTICE"
README = ROOT / "README.md"
EXPECTED_LICENSE_GIT_BLOB = "261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64"
NOTICE_MARKERS = (
    "GoreeCloud Website",
    "Copyright 2026 LaDamian Goree",
    "Apache License, Version 2.0",
    "does not grant permission to use GoreeCloud trade names",
    "Third-party project names, product names, logos, and marks remain the property of their respective owners",
    "docs/public-asset-inventory.md",
)
README_MARKERS = (
    "## Source license and creative-rights boundary",
    "Apache License 2.0",
    "Apache-2.0",
    "top-level `LICENSE` contains the reviewed license text",
    "`NOTICE` records the separate creative-rights boundary",
    "Issue #5 remains open",
)
STALE_README_MARKERS = (
    "source-license/publication decision tracked in issue #5 is unresolved",
)


def git_blob_id(path: Path) -> str:
    result = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def validate() -> list[str]:
    errors: list[str] = []

    if not LICENSE.is_file() or LICENSE.is_symlink():
        errors.append("LICENSE must be a regular repository file.")
    else:
        actual_blob = git_blob_id(LICENSE)
        if actual_blob != EXPECTED_LICENSE_GIT_BLOB:
            errors.append(
                "LICENSE no longer matches the reviewed Apache-2.0 text: "
                f"expected Git blob {EXPECTED_LICENSE_GIT_BLOB}, found {actual_blob}."
            )

    if not NOTICE.is_file() or NOTICE.is_symlink():
        errors.append("NOTICE must be a regular repository file.")
    else:
        notice = NOTICE.read_text(encoding="utf-8")
        for marker in NOTICE_MARKERS:
            if marker not in notice:
                errors.append(f"NOTICE is missing required licensing boundary: {marker}")

    if not README.is_file() or README.is_symlink():
        errors.append("README.md must be a regular repository file.")
    else:
        readme = README.read_text(encoding="utf-8")
        for marker in README_MARKERS:
            if marker not in readme:
                errors.append(f"README.md is missing required license/publication guidance: {marker}")
        for marker in STALE_README_MARKERS:
            if marker in readme:
                errors.append(f"README.md contains obsolete pre-license wording: {marker}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("License validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("License validation passed: Apache-2.0 source terms, NOTICE boundaries, and README guidance are synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
