#!/usr/bin/env python3
"""Normalize the GoreeCloud homepage into the current public website hub."""

from __future__ import annotations

import re

HERO_PREFIX = re.compile(r'<div class="hero-labels[^\"]*"[^>]*>.*?(?=\s*<h1>)', re.DOTALL)
HERO_ACTIONS = re.compile(r'<div class="hero-actions">.*?</div>', re.DOTALL)
PORTFOLIO_BLOCK = re.compile(r'\n    <section id="services" class="section suite-section">.*?(?=\n    <section id="how-it-works")', re.DOTALL)
BAND_BLOCK = re.compile(r'\n    <section class="band" aria-label="Core principles">.*?</section>\n', re.DOTALL)
ROADMAP_AI_CARD = re.compile(
    r'          <article class="roadmap-card">\s*'
    r'<div class="roadmap-card-head">\s*'
    r'(?:<span class="roadmap-icon roadmap-art"[^>]*>.*?</span>\s*)?'
    r'<span class="roadmap-state">[^<]*</span>\s*'
    r'</div>\s*'
    r'<p class="roadmap-kicker">Local Intelligence</p>\s*'
    r'<h3>(?:Local AI|GoreeCloud AI)</h3>.*?'
    r'          </article>',
    re.DOTALL,
)

WEBSITE_STYLESHEET = '<link rel="stylesheet" href="css/websites.css">'
HOMEPAGE_STYLESHEET = '<link rel="stylesheet" href="css/homepage-v6.css">'

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
    "identity.goreecloud.com",
)

PLATFORM_SYSTEM_LABELS = (
    "Glaze UI",
    "Privacy Shield",
    "Wardveil Security",
    "Everkeep",
    "GoreeCloud Mesh",
    "GoreeCloud Identity",
)


def canonical_hero_labels() -> str:
    """Keep the hero focused; platform-system detail belongs in the ecosystem section."""
    return (
        '<div class="hero-labels hero-context" aria-label="GoreeCloud platform focus">\n'
        '            <span class="eyebrow">Private • Self-hosted • Recoverable</span>\n'
        '          </div>\n\n          '
    )


def website_card(
    name: str,
    url: str,
    domain: str,
    description: str,
    status: str,
    status_class: str,
    card_class: str,
    mark: str,
    link_label: str = "Visit website",
) -> str:
    """Render one concise website card without a simulated browser preview."""
    return (
        f'<article class="service-card website-card {card_class}">\n'
        '  <div class="website-card-body">\n'
        '    <div class="website-card-head">\n'
        f'      <span class="website-mark" aria-hidden="true">{mark}</span>\n'
        f'      <span class="badge {status_class}">{status}</span>\n'
        '    </div>\n'
        f'    <p class="service-kicker">{domain}</p>\n'
        f'    <h3>{name}</h3>\n'
        f'    <p>{description}</p>\n'
        f'    <a class="website-link" href="{url}" aria-label="{link_label} for {name}">{link_label} →</a>\n'
        '  </div>\n'
        '</article>'
    )


def websites_section() -> str:
    cards = [
        website_card(
            "GoreeCloud",
            "https://www.goreecloud.com/",
            "goreecloud.com",
            "The main public hub for GoreeCloud: platform direction, project story, the current 57-repository portfolio, and links into the wider public web ecosystem.",
            "Primary Website", "active", "website-main", "GC",
        ),
        website_card(
            "GoreeCloud Suite",
            "https://suite.goreecloud.com/",
            "suite.goreecloud.com",
            "The dedicated home for GoreeCloud applications and services, umbrella capabilities, lifecycle status, product identity, and relationships to the six substantive platform systems.",
            "Dedicated Site", "growing", "website-suite", "SU",
        ),
        website_card(
            "GoreeCloud Projects",
            "https://projects.goreecloud.com/",
            "projects.goreecloud.com",
            "The current software portfolio for GoreeCloud AI, Code, Documents, Messenger, Gateway, Mesh, Quill, File Manager, Maps, App Store, and the broader native-suite transition.",
            "Portfolio", "active", "website-projects", "PR",
        ),
        website_card(
            "Glaze UI",
            "https://design.goreecloud.com/",
            "design.goreecloud.com",
            "The GoreeCloud Design Center for Glaze UI 2.1.0 Stable: interaction, material, adaptive form factors, accessibility, motion, visual language, and design-system governance.",
            "Design Center", "active", "website-design", "GU",
        ),
        website_card(
            "Privacy Shield",
            "https://privacy.goreecloud.com/",
            "privacy.goreecloud.com",
            "The GoreeCloud Privacy Center for privacy, consent, data minimization, data governance, user control, adapters, and evidence semantics.",
            "Privacy Center", "active", "website-privacy", "PS",
        ),
        website_card(
            "Wardveil Security",
            "https://security.goreecloud.com/",
            "security.goreecloud.com",
            "The GoreeCloud Security Center for protection, detection, trust, verification, response, evidence-backed security state, and authority boundaries.",
            "Security Center", "active", "website-security", "WS",
        ),
        website_card(
            "Everkeep",
            "https://everkeep.goreecloud.com/",
            "everkeep.goreecloud.com",
            "The GoreeCloud Continuity Center for resilience, backup, recovery, preservation, portability, succession, legacy, and evidence-backed continuity.",
            "Continuity Center", "growing", "website-everkeep", "EK",
        ),
        website_card(
            "GoreeCloud Roadmap",
            "https://roadmap.goreecloud.com/",
            "roadmap.goreecloud.com",
            "The focused public roadmap for native application development, current platform-system work, controlled migrations, and first-party evolution.",
            "Roadmap", "growing", "website-roadmap", "RM",
        ),
        website_card(
            "GoreeCloud Blog",
            "https://blog.goreecloud.com/",
            "blog.goreecloud.com",
            "The public development journal for build notes, architecture decisions, implementation lessons, platform-system updates, and current project milestones.",
            "Publication", "active", "website-blog", "BL",
        ),
        website_card(
            "GoreeCloud Archive",
            "https://archive.goreecloud.com/",
            "archive.goreecloud.com",
            "The curated historical archive preserving selected public records, superseded decisions, identity changes, milestones, and project evolution over time.",
            "Archive", "active", "website-archive", "AR",
        ),
        website_card(
            "GoreeCloud Identity",
            "https://github.com/GoreeCloud/goreecloud-identity",
            "identity.goreecloud.com",
            "The official Identity Center source for GoreeCloud accounts, authentication, authorization, devices, sessions, credentials, service identity, delegation, and recovery. Glaze UI 2.1 source is merged; public-domain publication and exact production acceptance remain separate gates.",
            "Publication Pending", "growing", "website-identity", "ID", "View source",
        ),
    ]
    rendered_cards = "\n          ".join(cards)
    return (
        '\n    <section id="websites" class="section websites-section">\n'
        '      <div class="container">\n'
        '        <div class="section-heading website-heading">\n'
        '          <p class="eyebrow">GoreeCloud websites</p>\n'
        '          <h2>Eleven official surfaces. One GoreeCloud ecosystem.</h2>\n'
        '          <p>Ten independently deployed public destinations are production-accepted on Glaze UI 2.1.0 Stable. Identity Center is the eleventh official first-party surface: its Glaze UI 2.1 source is merged, while public-domain publication and exact production acceptance remain separately gated. Glaze UI, Privacy Shield, Wardveil Security, Everkeep, GoreeCloud Mesh, and GoreeCloud Identity remain six substantive platform systems with distinct design, privacy, security, continuity, coordination, identity, authentication, and authorization responsibilities. Public claims remain tied to actual implementation and applicable evidence.</p>\n'
        '        </div>\n'
        '        <div class="service-grid website-grid">\n'
        f'          {rendered_cards}\n'
        '        </div>\n'
        '      </div>\n'
        '    </section>\n'
    )


def goreecloud_ai_roadmap_card() -> str:
    return (
        '          <article class="roadmap-card" data-roadmap="goreecloud-ai">\n'
        '            <div class="roadmap-card-head">\n'
        '              <span class="roadmap-icon roadmap-art" aria-hidden="true"><img src="assets/suite/ai.svg" alt="" width="52" height="52"></span>\n'
        '              <span class="roadmap-state">Active Development</span>\n'
        '            </div>\n'
        '            <p class="roadmap-kicker">Local Intelligence</p>\n'
        '            <h3>GoreeCloud AI</h3>\n'
        '            <p>First-party private AI experience built around GoreeCloud AI with local-model runtime support, Workspaces, knowledge and RAG, files, tools, orchestration, and controlled current-information research through GoreeCloud Search.</p>\n'
        '            <p class="roadmap-current"><strong>Direction:</strong> Keep model runtimes replaceable while GoreeCloud AI remains the first-party conversation, knowledge, research, and orchestration product.</p>\n'
        '            <ul class="roadmap-details">\n'
        '              <li>Local model runtime support</li>\n'
        '              <li>GoreeCloud AI Workspaces, knowledge, RAG, files, tools, and orchestration</li>\n'
        '              <li>Controlled web research through GoreeCloud Search</li>\n'
        '            </ul>\n'
        '          </article>'
    )


def normalize_homepage(source: str) -> str:
    normalized, hero_count = HERO_PREFIX.subn(canonical_hero_labels(), source, count=1)
    if hero_count != 1:
        raise ValueError("homepage hero context could not be normalized")

    normalized, portfolio_count = PORTFOLIO_BLOCK.subn(websites_section(), normalized, count=1)
    if portfolio_count != 1:
        raise ValueError("homepage Suite/capability block could not be replaced with website hub")

    normalized, band_count = BAND_BLOCK.subn("\n", normalized, count=1)
    if band_count != 1:
        raise ValueError("duplicated homepage principle band could not be removed")

    # Canonicalize the public navigation independently rather than depending on
    # the two legacy source anchors appearing as one whitespace-identical pair.
    normalized = normalized.replace(
        '<a href="#services">Suite</a>',
        '<a href="#websites">Websites</a>',
    )
    normalized = normalized.replace(
        '<a href="#capabilities">Capabilities</a>',
        '<a href="https://suite.goreecloud.com/">Suite</a>',
    )

    normalized, action_count = HERO_ACTIONS.subn(
        '<div class="hero-actions">\n'
        '            <a class="button primary" href="#websites">Explore GoreeCloud Websites</a>\n'
        '            <a class="button secondary" href="https://suite.goreecloud.com/">Explore GoreeCloud Suite</a>\n'
        '          </div>',
        normalized,
        count=1,
    )
    if action_count != 1:
        raise ValueError("homepage hero actions could not be normalized")

    normalized, ai_count = ROADMAP_AI_CARD.subn(goreecloud_ai_roadmap_card(), normalized, count=1)
    if ai_count != 1:
        raise ValueError("homepage GoreeCloud AI roadmap card could not be normalized")

    for stylesheet in (WEBSITE_STYLESHEET, HOMEPAGE_STYLESHEET):
        if stylesheet not in normalized:
            normalized = normalized.replace("</head>", f"  {stylesheet}\n</head>", 1)

    hero = HERO_PREFIX.search(normalized)
    hero_text = hero.group(0) if hero else ""
    if "Private • Self-hosted • Recoverable" not in hero_text:
        raise ValueError("homepage hero focus label is missing")
    for label in PLATFORM_SYSTEM_LABELS:
        if label in hero_text:
            raise ValueError(f"platform-system detail must not be duplicated in the hero: {label}")

    if 'data-suite-app=' in normalized or 'data-capability=' in normalized:
        raise ValueError("Suite application/capability cards must live on suite.goreecloud.com, not the main homepage")
    if normalized.count('id="websites"') != 1:
        raise ValueError("homepage must contain exactly one GoreeCloud websites section")
    for stale_anchor in ('href="#services"', 'href="#capabilities"'):
        if stale_anchor in normalized:
            raise ValueError(f"homepage contains an orphaned legacy navigation target after normalization: {stale_anchor}")
    for domain in EXPECTED_WEBSITE_DOMAINS:
        if normalized.count(f'<p class="service-kicker">{domain}</p>') != 1:
            raise ValueError(f"homepage website portfolio must show destination domain exactly once: {domain}")
    website_section_match = re.search(r'<section id="websites".*?</section>', normalized, re.DOTALL)
    website_section = website_section_match.group(0) if website_section_match else ""
    if website_section.count('class="service-card website-card ') != len(EXPECTED_WEBSITE_DOMAINS):
        raise ValueError("homepage website portfolio card count must match the website manifest")
    for label in PLATFORM_SYSTEM_LABELS:
        if label not in website_section:
            raise ValueError(f"homepage website ecosystem section must name current platform system: {label}")
    if "Glaze UI 2.1.0 Stable" not in website_section:
        raise ValueError("homepage website ecosystem section must identify the current Stable Glaze UI target")
    if "production-accepted" not in website_section or "Publication Pending" not in website_section:
        raise ValueError("homepage website ecosystem section must preserve production and publication acceptance boundaries")
    if "website-preview" in website_section or "website-preview-browser" in website_section:
        raise ValueError("simulated browser previews must not appear in the website directory")
    if website_section.count('class="website-mark"') != len(EXPECTED_WEBSITE_DOMAINS):
        raise ValueError("each website card must include one compact site identity mark")
    if '<section class="band" aria-label="Core principles">' in normalized:
        raise ValueError("duplicated homepage principle band must not return")
    for stylesheet in (WEBSITE_STYLESHEET, HOMEPAGE_STYLESHEET):
        if normalized.count(stylesheet) != 1:
            raise ValueError(f"homepage must include {stylesheet} exactly once")
    if "Open WebUI" in normalized or "AnythingLLM" in normalized:
        raise ValueError("retired AI front ends remain in the public homepage")
    return normalized
