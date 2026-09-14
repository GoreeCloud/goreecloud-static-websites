#!/usr/bin/env python3
"""Validate and normalize the source-native GoreeCloud Main homepage."""

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

PUBLIC_PROFILES = (
    ("Instagram", "@goreecloud", "https://instagram.com/goreecloud"),
    ("Threads", "@goreecloud", "https://www.threads.com/@goreecloud"),
    ("TikTok", "@goreecloud", "https://www.tiktok.com/@goreecloud"),
    ("X", "@GoreeCloud", "https://x.com/GoreeCloud"),
    ("Reddit", "u/goreecloud", "https://www.reddit.com/user/goreecloud/"),
    ("Pinterest", "@goreecloud", "https://www.pinterest.com/goreecloud/"),
    ("YouTube", "@GoreeCloud", "https://www.youtube.com/@GoreeCloud"),
    ("GitHub", "GoreeCloud", "https://github.com/GoreeCloud"),
)


def _footer_profile_link(name: str, handle: str, href: str) -> str:
    return (
        f'<a class="footer-social-link" href="{href}" target="_blank" rel="me noopener noreferrer" '
        f'aria-label="{name}: {handle}">{name}</a>'
    )


def _render_footer() -> str:
    links = "".join(_footer_profile_link(*profile) for profile in PUBLIC_PROFILES)
    return (
        '<footer class="site-footer"><div class="container footer-grid"><div>'
        '<a class="brand footer-brand" href="#top"><img class="brand-logo" src="assets/goreecloud-logo.svg" alt="" width="36" height="36">'
        '<span class="brand-text">GoreeCloud</span></a>'
        '<p>Privacy • Ownership • Native Software • Recoverability • Interoperability • Long-Term Preservation</p>'
        '<p class="footer-glaze"><strong>Glaze UI</strong> design • <strong>Privacy Shield</strong> privacy • '
        '<strong>Wardveil Security</strong> security • <strong>Everkeep</strong> continuity • <strong>Mesh</strong> coordination.</p></div>'
        '<nav class="footer-links" aria-label="Footer navigation"><a href="#roadmap">Ecosystem</a>'
        '<a href="#platform">Platform</a><a href="#websites">Explore</a><a href="#build">Build</a>'
        '<a href="#about">About</a><a href="privacy.html">Privacy</a><a href="security.html">Security</a></nav>'
        '<nav class="footer-social" aria-label="GoreeCloud public profiles"><strong class="footer-social-label">Follow GoreeCloud</strong>'
        f'<div class="footer-social-links">{links}</div></nav>'
        '<p class="copyright">© <span id="year">2026</span> GoreeCloud</p></div></footer>\n'
    )


def _replace_section(source: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = source.find(start_marker)
    if start < 0:
        raise ValueError(f"homepage missing section marker: {start_marker}")
    end = source.find(end_marker, start)
    if end < 0:
        raise ValueError(f"homepage missing section boundary after: {start_marker}")
    return source[:start] + replacement + source[end:]


def normalize_homepage(source: str) -> str:
    if source.count('id="websites"') != 1:
        raise ValueError("homepage must contain exactly one GoreeCloud websites section")
    if 'id="follow"' in source or 'class="social-grid"' in source:
        raise ValueError("homepage social profiles must appear only in the footer")

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

    has_45_product_model = (
        "45 verified Suite products" in source
        or '<strong>45</strong><span>verified Suite products</span>' in source
        or "45 products across nine functional groups" in source
    )
    has_9_group_model = (
        "9 functional product groups" in source
        or '<strong>9</strong><span>functional product groups</span>' in source
        or "nine functional groups" in source
    )
    if not (has_45_product_model and has_9_group_model):
        raise ValueError("homepage must identify the authoritative 45-product / 9-group Suite model")
    if "seven Integral Platform Systems" not in source:
        raise ValueError("homepage must identify the seven-system platform model")

    for marker in (
        'href="css/homepage-v7.css"',
        'class="ecosystem-panel"',
        'class="ecosystem-metrics"',
        "official public website surfaces",
        'id="platform"',
        'id="build"',
    ):
        if marker not in source:
            raise ValueError(f"homepage missing rebuilt ecosystem presentation marker: {marker}")

    if "source migration does not establish" not in source.lower():
        raise ValueError("homepage must preserve source/deployment acceptance separation")

    # Social profiles are intentionally published in exactly one place: the footer.
    # This keeps public discovery available without duplicating the same account
    # inventory as a full homepage section.
    source = _replace_section(source, '<footer class="site-footer">', '<script src="js/main.js"></script>', _render_footer())
    return source
