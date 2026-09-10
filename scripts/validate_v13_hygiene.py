#!/usr/bin/env python3
"""Fail closed when superseded Glaze runtime assets return to migrated consumers.

This check is deliberately scoped to consumer packages whose active V1.3 migrations
are complete. Design Center is excluded because it intentionally carries historical
and design-system source material as part of its documentation/source boundary.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OBSOLETE_CONSUMER_ASSETS = (
    "sites/identity/glaze-ui-2.1.0.css",
    "sites/projects/assets/glaze-ui-2.1.0.css",
    "sites/security/website/glaze-ui-v1.1.0.css",
)

for relative in OBSOLETE_CONSUMER_ASSETS:
    path = ROOT / relative
    if path.exists():
        raise SystemExit(f"obsolete Glaze consumer runtime asset must be absent: {relative}")

print("GLAZE UI V1.3 consumer hygiene passed: obsolete Identity, Projects, and Security runtime bundles are absent")
