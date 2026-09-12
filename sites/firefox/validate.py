#!/usr/bin/env python3
"""Fail closed on GoreeCloud Firefox Extensions public information drift."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
INVENTORY = ROOT / "assets" / "extension-inventory.json"
EXPECTED_SOURCE_REVISION = "50491e3280545281bc67c31a32819855b265ab92"
EXPECTED = {
    "bookmarks": ("GoreeCloud Bookmarks", "0.1.1", "source-candidate", None),
    "download-manager": ("GoreeCloud Download Manager Extension", "0.2.12", "stable", "0.2.12"),
    "redirector": ("GoreeCloud Redirector", "0.2.1", "canonical-source", "0.2.0"),
    "source-resync": ("GoreeCloud Source Resync", "1.1.2", "canonical-source", None),
    "privacy-shield": ("GoreeCloud Privacy Shield", "0.2.0", "stable", "0.2.0"),
}


def fail(message: str) -> None:
    raise SystemExit(f"Firefox public-site validation failed: {message}")


def main() -> None:
    source = INDEX.read_text(encoding="utf-8")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))

    if inventory.get("source_repository") != "GoreeCloud/goreecloud-firefox-extensions":
        fail("canonical extension repository drifted")
    if inventory.get("source_revision") != EXPECTED_SOURCE_REVISION:
        fail("extension inventory source revision drifted")

    rows = inventory.get("extensions")
    if not isinstance(rows, list) or len(rows) != len(EXPECTED):
        fail("public extension inventory must contain exactly five verified entries")
    by_slug = {row.get("slug"): row for row in rows if isinstance(row, dict)}
    if set(by_slug) != set(EXPECTED):
        fail("public extension inventory slug set drifted")

    for slug, (name, version, state, stable) in EXPECTED.items():
        row = by_slug[slug]
        actual = (row.get("name"), row.get("source_version"), row.get("source_state"), row.get("accepted_stable"))
        if actual != (name, version, state, stable):
            fail(f"verified inventory mismatch for {slug}: {actual!r}")
        for marker in (name, version, f"extensions/{slug}"):
            if marker not in source:
                fail(f"homepage missing verified {slug} marker: {marker}")

    for marker in (
        "https://firefox.goreecloud.com/",
        "5 Firefox extensions",
        "Source candidate",
        "Canonical source",
        "Stable",
        EXPECTED_SOURCE_REVISION[:7],
        "noindex,nofollow",
        "source and release truth stay evidence-scoped",
    ):
        if marker not in source:
            fail(f"homepage missing required truth marker: {marker}")

    for prohibited in (
        "all five extensions are stable",
        "five stable extensions",
        "production-verified",
        "Mozilla Add-ons store approved",
    ):
        if prohibited.lower() in source.lower():
            fail(f"unsupported public claim present: {prohibited}")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Disallow: /" not in robots:
        fail("pre-publication crawler block is missing")

    print("Firefox extension public truth valid: 5 extensions, evidence-scoped release states")


if __name__ == "__main__":
    main()
