#!/usr/bin/env python3
"""Validate the reviewed GoreeCloud Suite manifest and main-site separation."""

from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import re
import sys

from normalize_homepage import normalize_homepage
from render_repository_portfolio import load_manifest, load_suite_manifest, render_public_file

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
REF = re.compile(r"^[0-9a-f]{40}$|^(?:main|master)$")
STATUS_CLASSES = {"active", "growing", "planned"}
EXPECTED_APPLICATION_COUNT = 38
REQUIRED_NEW_CANONICAL_IDS = {"app-store", "file-manager", "maps", "index"}
REQUIRED_FIELDS = {
    "id", "name", "description", "role", "status", "status_class", "icon",
    "icon_blob", "source_repository", "source_path", "source_ref",
}


def blob_id(raw: bytes) -> str:
    return sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def main() -> int:
    errors: list[str] = []
    manifest = load_suite_manifest(ROOT)
    if manifest.get("schema_version") != 1:
        errors.append("Suite manifest schema_version must be 1.")
    if manifest.get("section_title") != "GoreeCloud Suite":
        errors.append("Suite section title must be 'GoreeCloud Suite'.")
    if not str(manifest.get("section_description", "")).strip():
        errors.append("Suite section description must be non-empty.")

    groups = manifest.get("groups")
    if not isinstance(groups, list) or not groups:
        errors.append("Suite manifest must contain application groups.")
        groups = []

    ids: set[str] = set()
    names: set[str] = set()
    icons: set[str] = set()
    applications: list[dict] = []
    for group in groups:
        if not str(group.get("id", "")).strip() or not str(group.get("label", "")).strip():
            errors.append("Every Suite group must have a non-empty id and label.")
        apps = group.get("applications")
        if not isinstance(apps, list) or not apps:
            errors.append(f"Suite group has no applications: {group.get('id')!r}")
            continue
        applications.extend(apps)

    if len(applications) != EXPECTED_APPLICATION_COUNT:
        errors.append(
            "Suite manifest must contain exactly "
            f"{EXPECTED_APPLICATION_COUNT} current applications/services; found {len(applications)}."
        )

    for app in applications:
        missing = sorted(field for field in REQUIRED_FIELDS if not str(app.get(field, "")).strip())
        if missing:
            errors.append(f"Suite application {app.get('id')!r} is missing fields: {', '.join(missing)}")
            continue
        app_id = app["id"]
        if app_id in ids:
            errors.append(f"Duplicate Suite application id: {app_id}")
        ids.add(app_id)
        if app["name"] in names:
            errors.append(f"Duplicate Suite application name: {app['name']}")
        names.add(app["name"])
        icon = app["icon"]
        if icon in icons:
            errors.append(f"Duplicate Suite icon path: {icon}")
        icons.add(icon)
        if not icon.startswith("assets/suite/") or not icon.endswith(".svg"):
            errors.append(f"Suite icon must use assets/suite/*.svg: {icon}")
        else:
            path = ROOT / icon
            if not path.is_file() or path.is_symlink():
                errors.append(f"Suite icon is missing or invalid: {icon}")
            elif blob_id(path.read_bytes()) != app["icon_blob"]:
                errors.append(f"Suite icon bytes do not match reviewed repository-owned artwork: {icon}")
        if app["status_class"] not in STATUS_CLASSES:
            errors.append(f"Unsupported Suite status class for {app_id}: {app['status_class']}")
        if not app["source_repository"].startswith("GoreeCloud/"):
            errors.append(f"Suite source repository must be first-party GoreeCloud: {app_id}")
        if not REF.fullmatch(app["source_ref"]):
            errors.append(f"Suite source ref must be an immutable commit or reviewed main/master branch: {app_id}")

    missing_new_ids = sorted(REQUIRED_NEW_CANONICAL_IDS - ids)
    if missing_new_ids:
        errors.append(
            "Newly approved canonical Suite identities are missing from the website registry: "
            + ", ".join(missing_new_ids)
        )

    if "quill" in ids or "GoreeCloud Quill" in names:
        errors.append("Quill is a GoreeCloud Keyboard capability family and must not be listed as a standalone Suite application.")

    source = INDEX.read_text(encoding="utf-8")
    rendered = normalize_homepage(render_public_file("index.html", source, load_manifest(ROOT)))
    if 'data-suite-app=' in rendered:
        errors.append("Main homepage must not render GoreeCloud Suite application cards.")
    if '<a href="https://suite.goreecloud.com/">Suite</a>' not in rendered:
        errors.append("Main homepage must link to the dedicated GoreeCloud Suite website.")
    if "suite.goreecloud.com" not in rendered:
        errors.append("Main homepage must identify suite.goreecloud.com as the Suite destination.")

    if errors:
        print("GoreeCloud Suite validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"GoreeCloud Suite manifest validation passed: {len(applications)} applications "
        f"across {len(groups)} groups; newly approved canonical identities present; "
        "main-site separation preserved."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
