#!/usr/bin/env python3
"""Validate GoreeCloud production-readiness governance for the public website.

The website is currently an anonymous static publication surface. The multi-user
baseline is therefore explicitly Not Applicable to the current architecture, while
security readiness and Glaze UI remain mandatory. This validator makes that scope
classification reviewable and fails if the implementation or CI stops carrying the
controls that justify it.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE = ROOT / "docs" / "governance-readiness.md"
BUILD = ROOT / "scripts" / "build_public_site.py"
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"
DEPLOYMENT_VALIDATOR = ROOT / "scripts" / "validate_deployment_contract.py"
ORIGIN_VALIDATOR = ROOT / "scripts" / "validate_browser_origin_integrity.py"
GLAZE_VALIDATOR = ROOT / "scripts" / "validate_glaze_ui.py"
ACCESSIBILITY_VALIDATOR = ROOT / "scripts" / "validate_accessibility.py"
INDEX = ROOT / "index.html"

REQUIRED_GOVERNANCE_MARKERS = (
    "Multi-user readiness: Not applicable to the current static public website",
    "Security readiness: Applicable",
    "Glaze UI compliance: Applicable",
    "If the website adds authentication",
    "this Not Applicable determination expires",
    "issue #5",
    "issue #6",
    "explicit merge and production authorization",
)

REQUIRED_BUILD_MARKERS = (
    "PUBLIC_FILES = (",
    "DIST = ROOT / \"dist\"",
)

PROHIBITED_DYNAMIC_MARKERS = (
    "<form",
    "firebase",
    "supabase",
)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def require_regular_file(errors: list[str], path: Path, label: str) -> str:
    if not path.is_file() or path.is_symlink():
        fail(errors, f"{label} must exist as a regular repository file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    governance = require_regular_file(errors, GOVERNANCE, "Governance readiness record")
    build = require_regular_file(errors, BUILD, "Public artifact builder")
    workflow = require_regular_file(errors, WORKFLOW, "Validation workflow")
    index = require_regular_file(errors, INDEX, "Homepage")

    for validator, label in (
        (DEPLOYMENT_VALIDATOR, "deployment-contract validator"),
        (ORIGIN_VALIDATOR, "browser-origin validator"),
        (GLAZE_VALIDATOR, "Glaze UI validator"),
        (ACCESSIBILITY_VALIDATOR, "accessibility validator"),
    ):
        require_regular_file(errors, validator, label)

    for marker in REQUIRED_GOVERNANCE_MARKERS:
        if marker not in governance:
            fail(errors, f"Governance readiness record is missing required boundary: {marker}")

    for marker in REQUIRED_BUILD_MARKERS:
        if marker not in build:
            fail(errors, f"Static public artifact contract is missing required marker: {marker}")

    lower_index = index.lower()
    for marker in PROHIBITED_DYNAMIC_MARKERS:
        if marker in lower_index:
            fail(
                errors,
                f"Current anonymous-static governance classification must be reviewed before homepage dynamic marker is introduced: {marker}",
            )

    required_workflow_commands = (
        "python scripts/validate_governance_readiness.py",
        "python scripts/validate_repository_hygiene.py",
        "python scripts/validate_repository_history.py",
        "python scripts/validate_security_policy.py",
        "python scripts/validate_privacy_policy.py",
        "python scripts/validate_browser_origin_integrity.py",
        "python scripts/validate_accessibility.py",
        "python scripts/validate_glaze_ui.py",
        "python scripts/validate_deployment_contract.py",
        "python scripts/build_public_site.py",
        "python scripts/validate_build_artifact.py",
    )
    for command in required_workflow_commands:
        if command not in workflow:
            fail(errors, f"Validation workflow must retain governance-supporting gate: {command}")

    if errors:
        print("GoreeCloud governance readiness validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        "GoreeCloud governance readiness validation passed: multi-user N/A for the current anonymous static site; security and Glaze UI gates remain applicable."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
