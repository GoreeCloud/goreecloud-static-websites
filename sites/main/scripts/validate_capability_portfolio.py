#!/usr/bin/env python3
"""Validate GoreeCloud umbrella capabilities and dedicated-Suite placement."""

from __future__ import annotations

from pathlib import Path
import sys

from normalize_homepage import normalize_homepage
from render_repository_portfolio import (
    load_capability_manifest,
    load_manifest,
    load_suite_manifest,
    render_public_file,
)

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EXPECTED_CAPABILITIES = {
    "quill": "GoreeCloud Quill",
    "waypoint": "GoreeCloud Waypoint",
    "resonance": "GoreeCloud Resonance",
    "courier": "GoreeCloud Courier",
    "beacon": "GoreeCloud Beacon",
}
REQUIRED_FIELDS = {
    "id", "name", "short_name", "parent_app_id", "parent_application", "icon",
    "description", "families", "relationship", "status", "status_class",
}


def main() -> int:
    errors: list[str] = []
    manifest = load_capability_manifest(ROOT)
    suite_manifest = load_suite_manifest(ROOT)

    if manifest.get("schema_version") != 1:
        errors.append("Capability portfolio schema_version must be 1.")
    if manifest.get("section_title") != "Umbrella Capabilities":
        errors.append("Capability portfolio section title must be 'Umbrella Capabilities'.")
    if not str(manifest.get("section_description", "")).strip():
        errors.append("Capability portfolio section description must be non-empty.")

    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, list):
        errors.append("Capability portfolio must contain a capabilities list.")
        capabilities = []

    suite_apps = {
        app["id"]: app
        for group in suite_manifest.get("groups", [])
        for app in group.get("applications", [])
    }

    ids: set[str] = set()
    names: set[str] = set()
    for capability in capabilities:
        if not isinstance(capability, dict):
            errors.append("Each capability portfolio entry must be an object.")
            continue
        missing = sorted(
            field for field in REQUIRED_FIELDS
            if field not in capability or capability[field] is None or capability[field] == ""
        )
        if missing:
            errors.append(f"Capability {capability.get('id')!r} is missing fields: {', '.join(missing)}")
            continue

        capability_id = capability["id"]
        name = capability["name"]
        if capability_id in ids:
            errors.append(f"Duplicate capability id: {capability_id}")
        ids.add(capability_id)
        if name in names:
            errors.append(f"Duplicate capability name: {name}")
        names.add(name)
        if EXPECTED_CAPABILITIES.get(capability_id) != name:
            errors.append(f"Capability identity drifted for {capability_id}.")

        parent = suite_apps.get(capability["parent_app_id"])
        if parent is None:
            errors.append(f"Capability {capability_id} references unknown Suite parent: {capability['parent_app_id']}")
            continue
        if capability["parent_application"] != parent["name"]:
            errors.append(f"Capability {capability_id} parent application name drifted.")
        if capability["icon"] != parent["icon"]:
            errors.append(f"Capability {capability_id} must reuse its parent application's approved Suite icon.")
        if capability["status_class"] != "active":
            errors.append(f"Capability {capability_id} must use the approved active status class.")
        families = capability["families"]
        if not isinstance(families, list) or not families or any(not str(item).strip() for item in families):
            errors.append(f"Capability {capability_id} must list non-empty capability families.")

    if ids != set(EXPECTED_CAPABILITIES):
        missing = sorted(set(EXPECTED_CAPABILITIES).difference(ids))
        extra = sorted(ids.difference(EXPECTED_CAPABILITIES))
        if missing:
            errors.append("Capability portfolio is missing approved identities: " + ", ".join(missing))
        if extra:
            errors.append("Capability portfolio contains unreviewed identities: " + ", ".join(extra))

    source = INDEX.read_text(encoding="utf-8")
    rendered = normalize_homepage(render_public_file("index.html", source, load_manifest(ROOT)))
    if 'data-capability=' in rendered or 'id="capabilities"' in rendered:
        errors.append("Main homepage must not render umbrella capability cards; they belong on suite.goreecloud.com.")
    if "suite.goreecloud.com" not in rendered:
        errors.append("Main homepage must link users to the dedicated Suite website for application capability detail.")

    if errors:
        print("GoreeCloud capability portfolio validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"GoreeCloud capability portfolio validation passed: {len(capabilities)} umbrella identities; main-site separation preserved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
