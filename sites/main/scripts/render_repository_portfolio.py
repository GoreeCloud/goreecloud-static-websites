#!/usr/bin/env python3
"""Render reviewed GoreeCloud public portfolio data into deployable HTML."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "repository-portfolio.json"
SUITE_MANIFEST = ROOT / "docs" / "suite-portfolio.json"
CAPABILITY_MANIFEST = ROOT / "docs" / "capability-portfolio.json"

SUMMARY_PATTERNS = {
    "total": re.compile(r"<strong>\d+</strong><span>current repositories</span>"),
    "public": re.compile(r"<strong>\d+</strong><span>public repositories</span>"),
    "private": re.compile(r"<strong>\d+</strong><span>private repositories</span>"),
    "functional_groups": re.compile(r"<strong>\d+</strong><span>functional groups</span>"),
}

DIRECTORY_GROUP_BLOCK = re.compile(
    r'(?P<indent>\s*)<div class="repo-group">.*?(?=\n      </div>\n    </section>)',
    re.DOTALL,
)
DIRECTORY_SUMMARY = re.compile(
    r'<aside class="repo-summary" aria-label="Repository summary">.*?</aside>',
    re.DOTALL,
)
HOMEPAGE_TEASER = re.compile(
    r'<p>GoreeCloud currently maintains \d+ repositories spanning.*?</p>',
    re.DOTALL,
)
SUITE_SECTION = re.compile(
    r'    <section id="services" class="section">.*?(?=\n    <section id="how-it-works")',
    re.DOTALL,
)
PLATFORM_SECTION = re.compile(
    r'\n    <section id="platform" class="section platform-section">.*?(?=\n    <section id="development")',
    re.DOTALL,
)
DEVELOPMENT_SECTION = re.compile(
    r'\n    <section id="development" class="section section-alt">.*?(?=\n    <section id="repositories")',
    re.DOTALL,
)
PLATFORM_NAVIGATION = re.compile(
    r'\s*<a href="(?:index\.html)?#platform">Platform</a>',
)
DEVELOPMENT_NAVIGATION = re.compile(
    r'\s*<a href="(?:index\.html)?#development">Projects</a>',
)
HERO_LABELS = re.compile(
    r'<div class="hero-labels" aria-label="GoreeCloud platform foundations">.*?</div>',
    re.DOTALL,
)
HERO_LEDE = re.compile(
    r'<p class="hero-lede">.*?</p>',
    re.DOTALL,
)
HERO_ACTIONS = re.compile(
    r'<div class="hero-actions">.*?</div>',
    re.DOTALL,
)


def load_manifest(root: Path = ROOT) -> dict:
    return json.loads((root / "docs" / "repository-portfolio.json").read_text(encoding="utf-8"))


def load_suite_manifest(root: Path = ROOT) -> dict:
    return json.loads((root / "docs" / "suite-portfolio.json").read_text(encoding="utf-8"))


def load_capability_manifest(root: Path = ROOT) -> dict:
    return json.loads((root / "docs" / "capability-portfolio.json").read_text(encoding="utf-8"))


def _mark(name: str) -> str:
    if name == "GoreeCloud":
        return "GC"
    base = name.removeprefix("goreecloud-")
    parts = [part for part in re.split(r"[-_]", base) if part]
    if len(parts) == 1:
        return parts[0][:2].upper()
    return "".join(part[0] for part in parts[:3]).upper()


def _card(repository: dict) -> str:
    name = repository["name"]
    visibility = repository["visibility"]
    description = escape(repository["description"])
    role = escape(repository["role"])
    featured = " featured" if name in {"glaze-ui", "goreecloud-manager", "goreecloud-drive"} else ""
    link = (
        f'<a href="https://github.com/GoreeCloud/{escape(name)}" target="_blank" '
        'rel="noopener noreferrer">View repository →</a>'
        if visibility == "public"
        else '<span class="repo-private-note">Private GoreeCloud repository</span>'
    )
    return (
        f'<article class="repo-card{featured}">'
        f'<div class="repo-card-top"><span class="repo-mark">{_mark(name)}</span>'
        f'<span class="repo-visibility {visibility}">{visibility.title()}</span></div>'
        f'<h4>{escape(name)}</h4><p>{description}</p>'
        f'<p class="repo-role"><strong>Role:</strong> {role}</p>{link}</article>'
    )


def _groups(manifest: dict) -> str:
    rendered: list[str] = []
    for number, group in enumerate(manifest["groups"], start=1):
        label = escape(group["label"])
        cards = "\n".join(f"            {_card(repo)}" for repo in group["repositories"])
        rendered.append(
            "        <div class=\"repo-group\">\n"
            f"          <div class=\"repo-group-heading\"><span>{number:02d}</span>"
            f"<div><p class=\"eyebrow\">{label}</p><h3>{label}</h3></div></div>\n"
            "          <div class=\"repo-grid\">\n"
            f"{cards}\n"
            "          </div>\n"
            "        </div>"
        )
    rendered.append(
        '        <div class="repo-footnote glaze-callout"><div>'
        '<span class="glaze-chip">Portfolio principle</span>'
        '<h3>Everything GoreeCloud builds belongs in source control.</h3></div>'
        '<p>Repository visibility does not determine runtime maturity. A public listing does not '
        'by itself establish release, deployment, production acceptance, or Stable status; each '
        "project's specification and release evidence remain authoritative.</p></div>"
    )
    return "\n\n".join(rendered) + "\n"


def _suite_card(application: dict) -> str:
    return (
        f'<article class="service-card suite-card" data-suite-app="{escape(application["id"])}">\n'
        f'  <div class="service-art suite-art" aria-hidden="true"><img src="{escape(application["icon"])}" alt="" width="52" height="52"></div>\n'
        f'  <h3>{escape(application["name"])}</h3>\n'
        f'  <p class="suite-description"><strong>Description:</strong> {escape(application["description"])}</p>\n'
        f'  <p class="suite-role"><strong>Role:</strong> {escape(application["role"])}</p>\n'
        f'  <span class="badge {escape(application["status_class"])}">{escape(application["status"])}</span>\n'
        '</article>'
    )


def _suite_section(manifest: dict) -> str:
    groups: list[str] = []
    for group in manifest["groups"]:
        group_id = f'suite-group-{escape(group["id"])}'
        cards = "\n".join(f"            {_suite_card(app)}" for app in group["applications"])
        groups.append(
            f'        <section class="suite-group" aria-labelledby="{group_id}">\n'
            f'          <div class="suite-group-heading"><p class="eyebrow">{escape(group["label"])}</p><h3 id="{group_id}">{escape(group["label"])}</h3></div>\n'
            '          <div class="service-grid suite-grid">\n'
            f'{cards}\n'
            '          </div>\n'
            '        </section>'
        )

    return (
        '    <section id="services" class="section suite-section">\n'
        '      <div class="container">\n'
        '        <div class="section-heading suite-heading">\n'
        f'          <p class="eyebrow">{escape(manifest["section_title"])}</p>\n'
        '          <h2>First-party applications for the complete GoreeCloud experience.</h2>\n'
        f'          <p>{escape(manifest["section_description"])}</p>\n'
        '        </div>\n\n'
        + "\n\n".join(groups)
        + '\n\n        <p class="status-note suite-note">Status labels describe GoreeCloud lifecycle and acceptance state, not upstream project maturity. A source repository, milestone, beta, or release-candidate label does not imply production approval unless the card explicitly states a Stable or current-service status.</p>\n'
        '      </div>\n'
        '    </section>\n'
    )


def _capability_card(capability: dict) -> str:
    families = " · ".join(escape(item) for item in capability["families"])
    return (
        f'<article class="service-card capability-card" data-capability="{escape(capability["id"])}">\n'
        f'  <div class="service-art suite-art" aria-hidden="true"><img src="{escape(capability["icon"])}" alt="" width="52" height="52"></div>\n'
        f'  <p class="service-kicker">Inside {escape(capability["parent_application"])}</p>\n'
        f'  <h3>{escape(capability["name"])}</h3>\n'
        f'  <p class="suite-description"><strong>What it is:</strong> {escape(capability["description"])}</p>\n'
        f'  <p class="capability-families"><strong>Includes:</strong> {families}</p>\n'
        f'  <p class="suite-role"><strong>Relationship:</strong> {escape(capability["relationship"])}</p>\n'
        f'  <span class="badge {escape(capability["status_class"])}">{escape(capability["status"])}</span>\n'
        '</article>'
    )


def _capability_section(manifest: dict) -> str:
    cards = "\n".join(f"          {_capability_card(item)}" for item in manifest["capabilities"])
    return (
        '    <section id="capabilities" class="section section-alt capability-section">\n'
        '      <div class="container">\n'
        '        <div class="section-heading capability-heading">\n'
        f'          <p class="eyebrow">{escape(manifest["section_title"])}</p>\n'
        '          <h2>The named systems behind GoreeCloud applications.</h2>\n'
        f'          <p>{escape(manifest["section_description"])}</p>\n'
        '        </div>\n'
        '        <div class="service-grid suite-grid capability-grid">\n'
        f'{cards}\n'
        '        </div>\n'
        '        <p class="status-note capability-note">These identities are capability umbrellas, not standalone Suite products. Artwork shown is the approved icon of each parent application; no separate umbrella mark is implied.</p>\n'
        '      </div>\n'
        '    </section>\n'
    )


def _hero_labels() -> str:
    return (
        '<div class="hero-labels" aria-label="GoreeCloud platform systems">\n'
        '            <a class="glaze-chip" href="https://design.goreecloud.com/">Glaze UI</a>\n'
        '            <a class="glaze-chip" href="https://privacy.goreecloud.com/">Privacy Shield</a>\n'
        '            <a class="glaze-chip" href="https://security.goreecloud.com/">Wardveil Security</a>\n'
        '            <span class="glaze-chip">Everkeep</span>\n'
        '            <span class="glaze-chip">GoreeCloud Mesh</span>\n'
        '            <span class="eyebrow">Design • Privacy • Security • Resilience • Coordination</span>\n'
        '          </div>'
    )


def _remove_obsolete_navigation(source: str) -> str:
    source = PLATFORM_NAVIGATION.sub("", source)
    source = DEVELOPMENT_NAVIGATION.sub("", source)
    return source


def render_repository_directory(source: str, manifest: dict) -> str:
    counts = manifest["counts"]
    summary = (
        '<aside class="repo-summary" aria-label="Repository summary">'
        f'<div><strong>{counts["total"]}</strong><span>current repositories</span></div>'
        f'<div><strong>{counts["public"]}</strong><span>public repositories</span></div>'
        f'<div><strong>{counts["private"]}</strong><span>private repositories</span></div>'
        '<p>Historical redirect names are not counted separately.</p></aside>'
    )
    source, summary_replacements = DIRECTORY_SUMMARY.subn(summary, source, count=1)
    if summary_replacements != 1:
        raise ValueError("repository directory summary template could not be resolved")

    source, group_replacements = DIRECTORY_GROUP_BLOCK.subn(_groups(manifest), source, count=1)
    if group_replacements != 1:
        raise ValueError("repository directory group template could not be resolved")
    return _remove_obsolete_navigation(source)


def render_homepage(
    source: str,
    manifest: dict,
    suite_manifest: dict | None = None,
    capability_manifest: dict | None = None,
) -> str:
    counts = manifest["counts"]
    suite_manifest = suite_manifest or load_suite_manifest(ROOT)
    capability_manifest = capability_manifest or load_capability_manifest(ROOT)
    rendered = source

    portfolio_sections = _suite_section(suite_manifest) + "\n" + _capability_section(capability_manifest)
    rendered, suite_replacements = SUITE_SECTION.subn(portfolio_sections, rendered, count=1)
    if suite_replacements != 1:
        raise ValueError("homepage GoreeCloud Suite template could not be resolved")
    rendered = rendered.replace(
        '<a href="#services">Services</a>',
        '<a href="#services">Suite</a>\n        <a href="#capabilities">Capabilities</a>',
    )

    rendered, platform_replacements = PLATFORM_SECTION.subn("", rendered, count=1)
    if platform_replacements != 1:
        raise ValueError("homepage Platform Foundation section could not be resolved")

    rendered, development_replacements = DEVELOPMENT_SECTION.subn("", rendered, count=1)
    if development_replacements != 1:
        raise ValueError("homepage duplicate Software & Development section could not be resolved")

    rendered = _remove_obsolete_navigation(rendered)
    rendered = rendered.replace('  <link rel="stylesheet" href="css/platform.css">\n', '')
    rendered = rendered.replace('  <link rel="stylesheet" href="css/development.css">\n', '')

    rendered, labels_replacements = HERO_LABELS.subn(_hero_labels(), rendered, count=1)
    if labels_replacements != 1:
        raise ValueError("homepage platform-system labels could not be resolved")

    rendered, lede_replacements = HERO_LEDE.subn(
        '<p class="hero-lede">GoreeCloud is a privacy-first, self-hosted personal and family cloud for keeping important data, applications, and digital history under the control of the people they belong to.</p>',
        rendered,
        count=1,
    )
    if lede_replacements != 1:
        raise ValueError("homepage hero description could not be resolved")

    rendered, action_replacements = HERO_ACTIONS.subn(
        '<div class="hero-actions">\n            <a class="button primary" href="#services">Explore GoreeCloud Suite</a>\n            <a class="button secondary" href="repositories.html">Browse Source Repositories</a>\n          </div>',
        rendered,
        count=1,
    )
    if action_replacements != 1:
        raise ValueError("homepage hero actions could not be resolved")

    rendered = re.sub(
        r"all \d+ current repositories",
        f'all {counts["total"]} current repositories',
        rendered,
    )
    rendered = re.sub(
        r"GoreeCloud currently maintains \d+ repositories",
        f'GoreeCloud currently maintains {counts["total"]} repositories',
        rendered,
    )
    current_teaser = (
        f'<p>GoreeCloud currently maintains {counts["total"]} repositories across first-party '
        'applications, maintained forks, shared platform foundations, design, identity, security, '
        'privacy, resilience, networking, storage, media, productivity, developer tooling, and '
        'public-presence work. The dedicated directory explains each repository at a public-safe '
        'level while preserving private source and lifecycle boundaries.</p>'
    )
    rendered, teaser_replacements = HOMEPAGE_TEASER.subn(current_teaser, rendered, count=1)
    if teaser_replacements != 1:
        raise ValueError("homepage repository teaser template could not be resolved")

    labels = {
        "total": "current repositories",
        "public": "public repositories",
        "private": "private repositories",
        "functional_groups": "functional groups",
    }
    for key, pattern in SUMMARY_PATTERNS.items():
        rendered, replacement_count = pattern.subn(
            f'<strong>{counts[key]}</strong><span>{labels[key]}</span>',
            rendered,
            count=1,
        )
        if replacement_count != 1:
            raise ValueError(f"homepage repository summary marker could not be resolved: {key}")
    return rendered


def render_public_file(relative: str, source: str, manifest: dict) -> str:
    if relative == "index.html":
        return render_homepage(source, manifest)
    if relative == "repositories.html":
        return render_repository_directory(source, manifest)
    if relative.endswith(".html"):
        return _remove_obsolete_navigation(source)
    return source
