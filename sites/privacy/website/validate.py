#!/usr/bin/env python3
"""Fail-closed validation for the canonical Privacy Center Glaze V1.3 source boundary.

This validator proves only repository source/build invariants. It cannot establish
rendered visual acceptance, accessibility device/browser acceptance, Privacy Shield
runtime acceptance, deployment acceptance, or production approval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parents[1]
SOURCE = SITE_ROOT / "website"
DIST = SOURCE / "dist"
ICON = SITE_ROOT / "branding" / "privacy-shield" / "privacy-shield-icon.svg"
README = SITE_ROOT / "README.md"
PROVENANCE = SITE_ROOT / "SOURCE-PROVENANCE.md"

EXPECTED_LOCK = {
    "schema": "goreecloud.glaze.consumer-lock.v1",
    "version": "1.3.0",
    "lifecycle": "Stable",
    "repository": "GoreeCloud/goreecloud-glaze-ui",
    "stable_commit": "8354308445da9ac35ced2b37a7f503a08a0aaf72",
    "entrypoint": "glaze-v1.3.0.css",
    "entrypoint_blob": "4c3ad293ba9196e2e5a32700b530ec67fd01cef6",
    "consumer_state": "source-migrated-rendered-acceptance-pending",
}

REQUIRED_SOURCE_FILES = (
    "index.html",
    "404.html",
    "_headers",
    "build.py",
    "glaze.lock.json",
    "site.css",
    "site-polish.css",
    "site.js",
    "v1.3-site.css",
)

HTML_MARKERS = (
    'data-glaze-version="1.3.0"',
    'name="goreecloud-glaze-ui" content="1.3.0"',
    'name="goreecloud-glaze-source-revision" content="8354308445da9ac35ced2b37a7f503a08a0aaf72"',
    'name="goreecloud-glaze-consumer-state" content="source-migrated-rendered-acceptance-pending"',
    'href="/assets/glaze-v1.3.0.css"',
    'href="/assets/v1.3-site.css"',
)

STALE_RUNTIME_MARKERS = (
    'glaze-ui-2.1.0.css',
    'data-glaze-ui="2.1.0"',
    'name="goreecloud-glaze-ui" content="2.1.0"',
)

ACCESSIBILITY_MARKERS = (
    "--privacy-v13-control:48px",
    "--privacy-v13-control-assisted:56px",
    "focus-visible",
    "prefers-reduced-motion:reduce",
    "prefers-reduced-transparency:reduce",
    "prefers-contrast:more",
    "forced-colors:active",
)

SECURITY_HEADER_MARKERS = (
    "X-Content-Type-Options: nosniff",
    "Referrer-Policy: strict-origin-when-cross-origin",
    "X-Frame-Options: DENY",
    "Content-Security-Policy:",
    "frame-ancestors 'none'",
    "connect-src 'none'",
)

BUILD_MARKERS = (
    'EXPECTED_VERSION = "1.3.0"',
    'EXPECTED_COMMIT = "8354308445da9ac35ced2b37a7f503a08a0aaf72"',
    'EXPECTED_ENTRYPOINT = "glaze-v1.3.0.css"',
    'EXPECTED_ENTRYPOINT_BLOB = "4c3ad293ba9196e2e5a32700b530ec67fd01cef6"',
    'GLAZE_UI_SOURCE',
    'consumer_state',
)

COPIED_ASSETS = (
    "site.css",
    "site-polish.css",
    "v1.3-site.css",
    "site.js",
)


def fail(message: str) -> None:
    raise SystemExit(f"Privacy Center V1.3 validation failed: {message}")


def require_regular_file(path: Path, label: str) -> Path:
    if not path.is_file() or path.is_symlink():
        fail(f"missing or unsafe {label}: {path}")
    return path


def git_blob_sha(data: bytes) -> str:
    prefix = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


def load_lock() -> dict[str, object]:
    path = require_regular_file(SOURCE / "glaze.lock.json", "Glaze lock")
    try:
        lock = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"invalid Glaze lock JSON: {exc}")
    if lock != EXPECTED_LOCK:
        fail("Glaze lock drifted from the exact approved V1.3 source boundary")
    return lock


def validate_html(path: Path) -> None:
    text = require_regular_file(path, "HTML source").read_text(encoding="utf-8")
    for marker in HTML_MARKERS:
        if marker not in text:
            fail(f"{path.relative_to(SITE_ROOT)} missing V1.3 marker: {marker}")
    for stale in STALE_RUNTIME_MARKERS:
        if stale in text:
            fail(f"{path.relative_to(SITE_ROOT)} contains superseded active Glaze marker: {stale}")


def validate_source() -> None:
    for name in REQUIRED_SOURCE_FILES:
        require_regular_file(SOURCE / name, "Privacy Center source")
    require_regular_file(ICON, "Privacy Shield public icon")
    require_regular_file(README, "Privacy Center README")
    require_regular_file(PROVENANCE, "Privacy Center source provenance")

    load_lock()
    validate_html(SOURCE / "index.html")
    validate_html(SOURCE / "404.html")

    adaptation = (SOURCE / "v1.3-site.css").read_text(encoding="utf-8")
    for marker in ACCESSIBILITY_MARKERS:
        if marker not in adaptation:
            fail(f"V1.3 consumer adaptation missing accessibility marker: {marker}")

    headers = (SOURCE / "_headers").read_text(encoding="utf-8")
    for marker in SECURITY_HEADER_MARKERS:
        if marker not in headers:
            fail(f"Privacy Center security headers missing marker: {marker}")

    build = (SOURCE / "build.py").read_text(encoding="utf-8")
    for marker in BUILD_MARKERS:
        if marker not in build:
            fail(f"deterministic V1.3 build contract missing marker: {marker}")

    readme = README.read_text(encoding="utf-8")
    for marker in (
        "Current Glaze UI source target: `1.3.0` Stable",
        "`8354308445da9ac35ced2b37a7f503a08a0aaf72`",
        "`source-migrated-rendered-acceptance-pending`",
        "source migration is not rendered acceptance",
    ):
        if marker not in readme:
            fail(f"Privacy Center README missing governance marker: {marker}")

    provenance = PROVENANCE.read_text(encoding="utf-8")
    for marker in (
        "df503451fcb508a84c35c0d7e95dc726372af749",
        "5f63af9fe0438858cb6e3f8f5f9debd53282e403",
        "source-migrated-rendered-acceptance-pending",
        "2.1.0 package remains historical provenance only",
    ):
        if marker not in provenance:
            fail(f"Privacy Center provenance missing migration marker: {marker}")

    obsolete = SOURCE / "glaze-ui-2.1.0.css"
    if obsolete.exists():
        fail("superseded Glaze UI 2.1.0 runtime asset must be absent from canonical source")


def validate_dist() -> None:
    if not DIST.is_dir() or DIST.is_symlink():
        fail("website/dist must be a real directory before --dist validation")

    for name in ("index.html", "404.html", "_headers"):
        source = require_regular_file(SOURCE / name, "source artifact")
        built = require_regular_file(DIST / name, "built artifact")
        if source.read_bytes() != built.read_bytes():
            fail(f"built {name} differs from canonical source")
        if name.endswith(".html"):
            validate_html(built)

    for name in COPIED_ASSETS:
        source = require_regular_file(SOURCE / name, "source asset")
        built = require_regular_file(DIST / "assets" / name, "built asset")
        if source.read_bytes() != built.read_bytes():
            fail(f"built asset differs from canonical source: {name}")

    built_icon = require_regular_file(DIST / "assets" / "privacy-shield-icon.svg", "built Privacy Shield icon")
    if ICON.read_bytes() != built_icon.read_bytes():
        fail("built Privacy Shield icon differs from canonical approved icon")

    entrypoint = require_regular_file(DIST / "assets" / EXPECTED_LOCK["entrypoint"], "built Glaze V1.3 entrypoint")
    if git_blob_sha(entrypoint.read_bytes()) != EXPECTED_LOCK["entrypoint_blob"]:
        fail("built Glaze V1.3 entrypoint does not match the pinned Git blob")

    text = entrypoint.read_text(encoding="utf-8")
    imports = re.findall(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', text, flags=re.IGNORECASE)
    for dependency in imports:
        require_regular_file(DIST / "assets" / dependency, f"built Glaze dependency {dependency}")

    if (DIST / "assets" / "glaze-ui-2.1.0.css").exists():
        fail("superseded Glaze UI 2.1.0 runtime asset must be absent from built artifact")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", action="store_true", help="also validate the exact built artifact")
    args = parser.parse_args()

    validate_source()
    if args.dist:
        validate_dist()

    scope = "source + exact built artifact" if args.dist else "source"
    print(
        f"Privacy Center GLAZE UI V1.3 {scope} boundary validated at "
        f"{EXPECTED_LOCK['stable_commit']}; rendered/runtime/deployment/production acceptance remains separate"
    )


if __name__ == "__main__":
    main()
