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
    ("Instagram", "@goreecloud", "Visual progress and demonstrations", "https://instagram.com/goreecloud", "assets/social/instagram.ico", "IG"),
    ("Threads", "@goreecloud", "Conversations and community updates", "https://www.threads.com/@goreecloud", None, "TH"),
    ("TikTok", "@goreecloud", "Short-form video and demonstrations", "https://www.tiktok.com/@goreecloud", None, "TT"),
    ("X", "@GoreeCloud", "Concise technical updates and announcements", "https://x.com/GoreeCloud", "assets/social/x.ico", "X"),
    ("Reddit", "u/goreecloud", "Detailed technical discussions", "https://www.reddit.com/user/goreecloud/", None, "RD"),
    ("Pinterest", "@goreecloud", "Evergreen visual discovery and references", "https://www.pinterest.com/goreecloud/", None, "PI"),
    ("YouTube", "@GoreeCloud", "Long-form video and demonstrations", "https://www.youtube.com/@GoreeCloud", "assets/social/youtube.ico", "YT"),
    ("GitHub", "GoreeCloud", "Public source and development history", "https://github.com/GoreeCloud", "assets/social/github.ico", "GH"),
)


def _profile_icon(icon: str | None, monogram: str) -> str:
    if icon:
        return f'<span class="social-icon" aria-hidden="true"><img src="{icon}" alt="" width="52" height="52"></span>'
    return f'<span class="social-icon" aria-hidden="true"><span class="social-monogram">{monogram}</span></span>'


def _profile_card(name: str, handle: str, role: str, href: str, icon: str | None, monogram: str) -> str:
    github_class = " github-card" if name == "GitHub" else ""
    return (
        f'<a class="social-card{github_class}" href="{href}" target="_blank" rel="me noopener noreferrer" '
        f'aria-label="{name}: {handle}">{_profile_icon(icon, monogram)}<strong>{name}</strong>'
        f'<span>{handle}</span><small>{role}</small></a>'
    )


def _footer_profile_link(name: str, handle: str, href: str) -> str:
    return (
        f'<a class="footer-social-link" href="{href}" target="_blank" rel="me noopener noreferrer" '
        f'aria-label="{name}: {handle}">{name}</a>'
    )


def _render_follow_section() -> str:
    cards = "".join(_profile_card(*profile) for profile in PUBLIC_PROFILES)
    return (
        '<section id="follow" class="section section-alt"><div class="container">'
        '<div class="section-heading"><p class="eyebrow">Follow the build</p>'
        '<h2>GoreeCloud is being documented in public.</h2>'
        '<p>Follow product development, demonstrations, design work, release progress, architecture, privacy, security, '
        'infrastructure, and the ongoing move toward first-party GoreeCloud software.</p></div>'
        '<p class="social-scope-note">Six active GoreeCloud social-media accounts are listed here, with YouTube and GitHub '
        'included as additional public destinations.</p>'
        f'<div class="social-grid">{cards}</div></div></section>\n'
    )


def _render_footer() -> str:
    links = "".join(_footer_profile_link(name, handle, href) for name, handle, _role, href, _icon, _monogram in PUBLIC_PROFILES)
    return (
        '<footer class="site-footer"><div class="container footer-grid"><div>'
        '<a class="brand footer-brand" href="#top"><img class="brand-logo" src="assets/goreecloud-logo.svg" alt="" width="36" height="36">'
        '<span class="brand-text">GoreeCloud</span></a>'
        '<p>Privacy • Ownership • Native Software • Recoverability • Interoperability • Long-Term Preservation</p>'
        '<p class="footer-glaze"><strong>Glaze UI</strong> design • <strong>Privacy Shield</strong> privacy • '
        '<strong>Wardveil Security</strong> security • <strong>Everkeep</strong> continuity • <strong>Mesh</strong> coordination.</p></div>'
        '<nav class="footer-links" aria-label="Footer navigation"><a href="#websites">Websites</a>'
        '<a href="https://suite.goreecloud.com/">Suite</a><a href="repositories.html">Repositories</a>'
        '<a href="#roadmap">Portfolio</a><a href="#about">About</a><a href="#follow">Social</a>'
        '<a href="privacy.html">Privacy</a><a href="security.html">Security</a></nav>'
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

    # Build the complete public-profile inventory directly into the published HTML.
    # JavaScript may reconcile/enhance it, but social discovery must not depend on
    # script execution, browser storage, or a fresh cached JavaScript asset.
    source = _replace_section(source, '<section id="follow"', '<section id="contact"', _render_follow_section())
    source = _replace_section(source, '<footer class="site-footer">', '<script src="js/main.js"></script>', _render_footer())
    return source
