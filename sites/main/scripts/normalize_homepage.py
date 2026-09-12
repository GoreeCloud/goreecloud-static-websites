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
    "labs.goreecloud.com",
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
        "Thirteen official surfaces",
        "Privacy-First Personal & Family Cloud",
        "personal and family cloud",
        "family digital foundation",
        "More than a homelab.",
        "Built deliberately from the beginning.",
        "started in 2026 as a self-hosting plan",
        "want to talk self-hosting",
    ):
        if stale in source:
            raise ValueError(f"superseded current-state wording remains on homepage: {stale}")
    if "Fourteen official surfaces" not in source:
        raise ValueError("homepage must identify the current 14-site public surface including Labs")
    if "GoreeCloud Labs" not in source or "labs.goreecloud.com" not in source:
        raise ValueError("homepage must include the GoreeCloud Labs destination")
    if "45 verified Suite products" not in source or "9 functional product groups" not in source:
        raise ValueError("homepage must identify the authoritative 45-product / 9-group Suite model")
    if "seven Integral Platform Systems" not in source:
        raise ValueError("homepage must identify the seven-system platform model")
    for marker in (
        'href="css/homepage-v7.css"',
        'class="ecosystem-panel"',
        'class="ecosystem-metrics"',
        "official public website surfaces",
    ):
        if marker not in source:
            raise ValueError(f"homepage missing current ecosystem presentation marker: {marker}")
    if "source migration does not establish" not in source.lower():
        raise ValueError("homepage must preserve source/deployment acceptance separation")
    return source
