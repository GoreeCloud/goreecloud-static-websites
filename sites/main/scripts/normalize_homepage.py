#!/usr/bin/env python3
"""Normalize and validate the current GoreeCloud Main homepage public directory."""

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

LABS_CARD = """<article class=\"service-card website-card website-labs\"><div class=\"website-card-body\"><div class=\"website-card-head\"><span class=\"website-mark\" aria-hidden=\"true\">LB</span><span class=\"badge growing\">Product center</span></div><p class=\"service-kicker\">labs.goreecloud.com</p><h3>GoreeCloud Labs</h3><p>Public development center for GoreeCloud Home Security, Home, AI, Containers, Code, and Boot, with lifecycle claims kept evidence-scoped.</p><a class=\"website-link\" href=\"https://labs.goreecloud.com/\">Open destination →</a></div></article>"""


def _sync_public_directory(source: str) -> str:
    """Compile the current public-surface directory without weakening source truth gates."""
    if "labs.goreecloud.com" not in source:
        marker = '\n</div><p class="status-note">Central source migration does not establish'
        if source.count(marker) != 1:
            raise ValueError("homepage website directory insertion boundary is ambiguous")
        source = source.replace(marker, f"\n{LABS_CARD}{marker}", 1)

    replacements = (
        ("<strong>13</strong><span>official public website surfaces</span>", "<strong>14</strong><span>official public website surfaces</span>"),
        ("Thirteen official surfaces. One GoreeCloud ecosystem.", "Fourteen official surfaces. One GoreeCloud ecosystem."),
        ("thirteen public website surfaces", "fourteen public website surfaces"),
    )
    for old, new in replacements:
        source = source.replace(old, new)
    return source


def normalize_homepage(source: str) -> str:
    source = _sync_public_directory(source)

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
        raise ValueError("homepage must identify the current 14-surface public directory")
    if "45 verified Suite products" not in source or "9 functional product groups" not in source:
        raise ValueError("homepage must identify the authoritative 45-product / 9-group Suite model")
    if "seven Integral Platform Systems" not in source:
        raise ValueError("homepage must identify the seven-system platform model")
    for marker in (
        'href="css/homepage-v7.css"',
        'class="ecosystem-panel"',
        'class="ecosystem-metrics"',
        "official public website surfaces",
        "GoreeCloud Labs",
        "GoreeCloud Boot",
    ):
        if marker not in source:
            raise ValueError(f"homepage missing current ecosystem presentation marker: {marker}")
    if "source migration does not establish" not in source.lower():
        raise ValueError("homepage must preserve source/deployment acceptance separation")
    return source
