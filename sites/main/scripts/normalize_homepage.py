#!/usr/bin/env python3
"""Validate and return the source-native GoreeCloud Main homepage."""

from __future__ import annotations

EXPECTED_WEBSITE_DOMAINS = (
    "goreecloud.com",
    "suite.goreecloud.com",
    "projects.goreecloud.com",
    "design.goreecloud.com",
    "privacy.goreecloud.com",
    "security.goreecloud.com",
    "everkeep.goreecloud.com",
    "roadmap.goreecloud.com",
    "blog.goreecloud.com",
    "archive.goreecloud.com",
    "mesh.goreecloud.com",
    "id.goreecloud.com",
    "manage.goreecloud.com",
)

PLATFORM_SYSTEM_LABELS = (
    "Glaze UI",
    "Privacy Shield",
    "Wardveil Security",
    "Everkeep",
    "GoreeCloud Mesh",
    "GoreeCloud Identity",
    "GoreeCloud Manager",
)


def normalize_homepage(source: str) -> str:
    if source.count('id="websites"') != 1:
        raise ValueError("homepage must contain exactly one GoreeCloud websites section")
    for domain in EXPECTED_WEBSITE_DOMAINS:
        if domain not in source:
            raise ValueError(f"homepage missing authoritative website namespace: {domain}")
    for label in PLATFORM_SYSTEM_LABELS:
        if label not in source:
            raise ValueError(f"homepage missing Integral Platform System: {label}")
    for stale in (
        "Glaze UI 2.1",
        "Glaze UI 2.2",
        "current 57-repository portfolio",
        "57 repositories",
        "40 public repositories",
        "17 private repositories",
        "identity.goreecloud.com",
        "Six substantive platform systems",
        "Ten independently deployed public destinations",
        "Eleven official surfaces",
    ):
        if stale in source:
            raise ValueError(f"superseded current-state wording remains on homepage: {stale}")
    if "Thirteen official surfaces" not in source:
        raise ValueError("homepage must identify the authoritative 13-site public surface")
    if "seven Integral Platform Systems" not in source:
        raise ValueError("homepage must identify the seven-system platform model")
    if "source migration does not establish" not in source.lower():
        raise ValueError("homepage must preserve source/deployment acceptance separation")
    return source
