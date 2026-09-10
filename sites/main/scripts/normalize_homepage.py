#!/usr/bin/env python3
"""Normalize the GoreeCloud homepage into the current public website hub."""

from __future__ import annotations

import re

HERO_PREFIX = re.compile(r'<div class="hero-labels[^\"]*"[^>]*>.*?(?=\s*<h1>)', re.DOTALL)
HERO_ACTIONS = re.compile(r'<div class="hero-actions">.*?</div>', re.DOTALL)
PORTFOLIO_BLOCK = re.compile(r'\n    <section id="services"[^>]*>.*?(?=\n    <section id="how-it-works")', re.DOTALL)
BAND_BLOCK = re.compile(r'\n    <section class="band" aria-label="Core principles">.*?</section>\n', re.DOTALL)
ROADMAP_BLOCK = re.compile(r'\n    <section id="roadmap" class="section roadmap-section">.*?(?=\n    <section id="about")', re.DOTALL)
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


def canonical_hero_labels() -> str:
    return (
        '<div class="hero-labels hero-context" aria-label="GoreeCloud platform focus">\n'
        '            <span class="eyebrow">Private • Self-hosted • Recoverable</span>\n'
        '          </div>\n\n          '
    )


def website_card(name: str, url: str, domain: str, description: str, status: str, card_class: str, mark: str) -> str:
    return (
        f'<article class="service-card website-card {card_class}">\n'
        '  <div class="website-card-body">\n'
        '    <div class="website-card-head">\n'
        f'      <span class="website-mark" aria-hidden="true">{mark}</span>\n'
        f'      <span class="badge growing">{status}</span>\n'
        '    </div>\n'
        f'    <p class="service-kicker">{domain}</p>\n'
        f'    <h3>{name}</h3>\n'
        f'    <p>{description}</p>\n'
        f'    <a class="website-link" href="{url}" aria-label="Open official destination for {name}">Open destination →</a>\n'
        '  </div>\n'
        '</article>'
    )


def websites_section() -> str:
    common = "Centralized in GoreeCloud/goreecloud-static-websites; exact V1.3 deployment acceptance remains independent."
    cards = [
        website_card("GoreeCloud", "https://www.goreecloud.com/", "goreecloud.com", f"Primary public hub for GoreeCloud. {common}", "V1.3 source candidate", "website-main", "GC"),
        website_card("GoreeCloud Suite", "https://suite.goreecloud.com/", "suite.goreecloud.com", f"Dedicated application and service directory. {common}", "V1.3 source migrated", "website-suite", "SU"),
        website_card("GoreeCloud Projects", "https://projects.goreecloud.com/", "projects.goreecloud.com", f"Public software and project portfolio. {common}", "V1.3 source migrated", "website-projects", "PR"),
        website_card("Glaze UI", "https://design.goreecloud.com/", "design.goreecloud.com", f"Design Center for the current GLAZE UI V1.3 design language. {common}", "V1.3 source migrated", "website-design", "GU"),
        website_card("Privacy Shield", "https://privacy.goreecloud.com/", "privacy.goreecloud.com", f"Privacy Center for GoreeCloud privacy authority and evidence. {common}", "V1.3 source migrated", "website-privacy", "PS"),
        website_card("Wardveil Security", "https://security.goreecloud.com/", "security.goreecloud.com", f"Security Center for evidence-scoped GoreeCloud security state. {common}", "V1.3 source migrated", "website-security", "WS"),
        website_card("Everkeep", "https://everkeep.goreecloud.com/", "everkeep.goreecloud.com", f"Continuity Center for resilience, recovery, preservation, and continuity evidence. {common}", "V1.3 source migrated", "website-everkeep", "EK"),
        website_card("GoreeCloud Roadmap", "https://roadmap.goreecloud.com/", "roadmap.goreecloud.com", f"Public development direction and evidence-scoped priorities. {common}", "V1.3 source migrated", "website-roadmap", "RM"),
        website_card("GoreeCloud Blog", "https://blog.goreecloud.com/", "blog.goreecloud.com", f"Public technical writing and development context. {common}", "V1.3 source migrated", "website-blog", "BL"),
        website_card("GoreeCloud Archive", "https://archive.goreecloud.com/", "archive.goreecloud.com", f"Curated public history and superseded-decision context. {common}", "V1.3 source migrated", "website-archive", "AR"),
        website_card("GoreeCloud Mesh", "https://mesh.goreecloud.com/", "mesh.goreecloud.com", f"Public Mesh coordination and governance information. {common}", "V1.3 source migrated", "website-mesh", "ME"),
        website_card("GoreeCloud Identity", "https://id.goreecloud.com/", "id.goreecloud.com", f"Identity Center for identity, authentication, authorization, devices, sessions, and delegation. {common}", "V1.3 source migrated", "website-identity", "ID"),
        website_card("GoreeCloud Manager", "https://manage.goreecloud.com/", "manage.goreecloud.com", f"Public informational surface for the private-by-default operations console. The authenticated Manager runtime remains separate. {common}", "V1.3 source migrated", "website-manager", "MG"),
    ]
    rendered_cards = "\n          ".join(cards)
    systems = ", ".join(PLATFORM_SYSTEM_LABELS[:-1]) + ", and " + PLATFORM_SYSTEM_LABELS[-1]
    return (
        '\n    <section id="websites" class="section websites-section">\n'
        '      <div class="container">\n'
        '        <div class="section-heading website-heading">\n'
        '          <p class="eyebrow">GoreeCloud websites</p>\n'
        '          <h2>Thirteen official surfaces. One GoreeCloud ecosystem.</h2>\n'
        '          <p>All thirteen authoritative static website packages are centralized in GoreeCloud/goreecloud-static-websites and are being reconciled to the current official Stable GLAZE UI V1.3 contract. Source migration does not establish Cloudflare source cutover, rendered acceptance, or a new production revision. Historical production evidence remains exact-revision scoped.</p>\n'
        f'          <p>The seven Integral Platform Systems are {systems}. Each retains its own authority and evidence boundary; a public website cannot manufacture design, privacy, security, continuity, coordination, identity, or administrative acceptance.</p>\n'
        '        </div>\n'
        '        <div class="service-grid website-grid">\n'
        f'          {rendered_cards}\n'
        '        </div>\n'
        '      </div>\n'
        '    </section>\n'
    )


def roadmap_section() -> str:
    return '''
    <section id="roadmap" class="section roadmap-section">
      <div class="container">
        <div class="section-heading"><p class="eyebrow">Current directions</p><h2>First-party products, replaceable foundations.</h2><p>Public direction is intentionally high level. Planned work is not represented as active or production-accepted until its own implementation and evidence gates pass.</p></div>
        <div class="roadmap-grid" aria-label="Current GoreeCloud product directions">
          <article class="roadmap-card"><div class="roadmap-card-head"><span class="roadmap-icon">GH</span><span class="roadmap-state">Development</span></div><p class="roadmap-kicker">Home</p><h3>GoreeCloud Home</h3><p>First-party home experience and automation direction. Mature home-automation software may remain a bounded implementation foundation without becoming the GoreeCloud product identity.</p><p class="roadmap-current"><strong>Source:</strong> GoreeCloud/goreecloud-home.</p></article>
          <article class="roadmap-card"><div class="roadmap-card-head"><span class="roadmap-icon">HS</span><span class="roadmap-state">Development</span></div><p class="roadmap-kicker">Home Security</p><h3>GoreeCloud Home Security</h3><p>First-party home-security direction for locally controlled safety, cameras, events, and evidence-aware security workflows. Underlying engines remain replaceable implementation details.</p><p class="roadmap-current"><strong>Source:</strong> GoreeCloud/goreecloud-home-security.</p></article>
          <article class="roadmap-card"><div class="roadmap-card-head"><span class="roadmap-icon roadmap-art" aria-hidden="true"><img src="assets/suite/ai.svg" alt="" width="52" height="52"></span><span class="roadmap-state">Active Development</span></div><p class="roadmap-kicker">Local Intelligence</p><h3>GoreeCloud AI</h3><p>First-party conversation, workspace, knowledge, research, file, tool, and orchestration direction with replaceable model runtimes and explicit data/authority boundaries.</p></article>
        </div>
        <p class="roadmap-note"><strong>Status note:</strong> Public direction does not establish deployment, security, privacy, recovery, Stable qualification, or production acceptance.</p>
      </div>
    </section>
'''


def normalize_homepage(source: str) -> str:
    normalized, hero_count = HERO_PREFIX.subn(canonical_hero_labels(), source, count=1)
    if hero_count != 1:
        raise ValueError("homepage hero context could not be normalized")
    normalized, portfolio_count = PORTFOLIO_BLOCK.subn(websites_section(), normalized, count=1)
    if portfolio_count != 1:
        raise ValueError("homepage portfolio block could not be replaced with website hub")
    normalized, band_count = BAND_BLOCK.subn("\n", normalized, count=1)
    if band_count != 1:
        raise ValueError("duplicated homepage principle band could not be removed")
    normalized, roadmap_count = ROADMAP_BLOCK.subn(roadmap_section(), normalized, count=1)
    if roadmap_count != 1:
        raise ValueError("homepage roadmap block could not be normalized")

    normalized = normalized.replace('<a href="#services">Suite</a>', '<a href="#websites">Websites</a>')
    normalized = normalized.replace('<a href="#capabilities">Capabilities</a>', '<a href="https://suite.goreecloud.com/">Suite</a>')
    normalized, action_count = HERO_ACTIONS.subn(
        '<div class="hero-actions">\n            <a class="button primary" href="#websites">Explore GoreeCloud Websites</a>\n            <a class="button secondary" href="https://suite.goreecloud.com/">Explore GoreeCloud Suite</a>\n          </div>',
        normalized,
        count=1,
    )
    if action_count != 1:
        raise ValueError("homepage hero actions could not be normalized")

    for stylesheet in (WEBSITE_STYLESHEET, HOMEPAGE_STYLESHEET):
        if stylesheet not in normalized:
            normalized = normalized.replace("</head>", f"  {stylesheet}\n</head>", 1)

    if normalized.count('id="websites"') != 1:
        raise ValueError("homepage must contain exactly one GoreeCloud websites section")
    for domain in EXPECTED_WEBSITE_DOMAINS:
        if normalized.count(f'<p class="service-kicker">{domain}</p>') != 1:
            raise ValueError(f"homepage website portfolio must show destination domain exactly once: {domain}")
    website_section_match = re.search(r'<section id="websites".*?</section>', normalized, re.DOTALL)
    website_section = website_section_match.group(0) if website_section_match else ""
    if website_section.count('class="service-card website-card ') != len(EXPECTED_WEBSITE_DOMAINS):
        raise ValueError("homepage website portfolio card count must match the authoritative 13-package scope")
    for label in PLATFORM_SYSTEM_LABELS:
        if label not in website_section:
            raise ValueError(f"homepage website ecosystem section must name Integral Platform System: {label}")
    for stale in ("Glaze UI 2.1", "current 57-repository portfolio", "identity.goreecloud.com", "Six substantive platform systems"):
        if stale in normalized:
            raise ValueError(f"superseded current-state wording remains on homepage: {stale}")
    if "source migration does not establish Cloudflare source cutover" not in website_section.lower():
        raise ValueError("homepage must preserve source/deployment acceptance separation")
    return normalized
