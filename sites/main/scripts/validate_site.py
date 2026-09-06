#!/usr/bin/env python3
"""Validate the dependency-free GoreeCloud public website.

The checks intentionally use only the Python standard library so GitHub Actions can
validate the repository without downloading third-party packages. Homepage checks
run through the same deterministic composition path used by publication so source
placeholders are not mistaken for the deployed public surface.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import re
import sys

from glaze_ui_2 import apply_glaze_ui_2
from normalize_homepage import normalize_homepage
from render_repository_portfolio import load_manifest, render_public_file

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
SECURITY = ROOT / ".well-known" / "security.txt"
CANONICAL = "https://www.goreecloud.com/"
SECURITY_CANONICAL = f"{CANONICAL}.well-known/security.txt"
PRIVATE_PATTERNS = (
    re.compile(r"\b10(?:\.\d{1,3}){3}\b"),
    re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2}\b"),
)
SENSITIVE_TERMS = ("goreecloud-vps-01", ".netbird.selfhosted")
REQUIRED_STYLESHEETS = {
    "css/style.css",
    "css/glaze.css",
    "css/glaze-polish.css",
}
REQUIRED_SCRIPTS = {
    "js/theme-init.js",
    "js/main.js",
}
REQUIRED_PUBLIC_MARKERS = {
    "current repository portfolio": "current 57-repository portfolio",
    "official website directory": '<section id="websites"',
    "Suite public destination": "suite.goreecloud.com",
    "Projects public destination": "projects.goreecloud.com",
    "Design Center public destination": "design.goreecloud.com",
    "Privacy Center public destination": "privacy.goreecloud.com",
    "Security Center public destination": "security.goreecloud.com",
    "Continuity Center public destination": "everkeep.goreecloud.com",
    "Roadmap public destination": "roadmap.goreecloud.com",
    "Blog public destination": "blog.goreecloud.com",
    "Archive public destination": "archive.goreecloud.com",
    "Identity publication boundary": "identity.goreecloud.com",
    "current Glaze UI target": "Glaze UI 2.1.0 Stable",
    "production/publication boundary": "Publication Pending",
    "public ownership purpose": "Ownership should be understandable and repeatable.",
    "public Follow the build section": '<section id="follow"',
    "public GoreeCloud YouTube channel": "https://www.youtube.com/@GoreeCloud",
    "public contact section": '<section id="contact"',
}
STALE_PUBLIC_COPY = (
    "56-repository portfolio",
    "56 repositories spanning",
    "A GoreeCloud-maintained Memos fork for fast private note capture",
    "Memos RC remains a protected transitional migration source",
    "transitional services remain protected until migration gates are satisfied",
    "https://github.com/GoreeCloud/linkding",
    "https://github.com/GoreeCloud/memos",
    '<span class="badge growing">Quick Capture</span>',
    '<span class="badge growing">Stabilizing</span>',
    "has replaced ntfy",
    "GoreeCloud Notify replaces ntfy",
)
REQUIRED_SECURITY_FIELDS = {
    "Contact": "mailto:security@goreecloud.com",
    "Preferred-Languages": "en",
    "Canonical": SECURITY_CANONICAL,
}
REQUIRED_HEADERS = (
    "Referrer-Policy: no-referrer",
    "Origin-Agent-Cluster: ?1",
)


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.id_counts: Counter[str] = Counter()
        self.local_refs: set[str] = set()
        self.fragment_refs: set[str] = set()
        self.external_blank_errors: list[str] = []
        self.insecure_external_refs: list[str] = []
        self.missing_alt_images: list[str] = []
        self.inline_script_count = 0
        self.inline_style_count = 0
        self.inline_event_handlers: list[str] = []
        self.canonical: str | None = None
        self.og_url: str | None = None
        self.description: str | None = None
        self.script_sources: list[str] = []
        self.stylesheet_sources: list[str] = []
        self.html_lang: str | None = None
        self.h1_count = 0
        self._in_title = False
        self.title_parts: list[str] = []

    @property
    def ids(self) -> set[str]:
        return set(self.id_counts)

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}

        if tag == "html":
            self.html_lang = attrs.get("lang")
        if tag == "title":
            self._in_title = True
        if tag == "h1":
            self.h1_count += 1
        if attrs.get("id"):
            self.id_counts[attrs["id"]] += 1

        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "meta" and attrs.get("property") == "og:url":
            self.og_url = attrs.get("content")
        if tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content")

        if tag == "script":
            if attrs.get("src"):
                self.script_sources.append(attrs["src"])
            else:
                self.inline_script_count += 1
        if tag == "style":
            self.inline_style_count += 1
        if tag == "link" and "stylesheet" in attrs.get("rel", "").split() and attrs.get("href"):
            self.stylesheet_sources.append(attrs["href"])
        if tag == "img" and "alt" not in attrs:
            self.missing_alt_images.append(attrs.get("src", "(missing src)"))

        for attr_name in attrs:
            if attr_name.lower().startswith("on"):
                self.inline_event_handlers.append(f"<{tag} {attr_name}=...>")

        for attr in ("href", "src"):
            value = attrs.get(attr, "")
            if not value:
                continue
            if value.startswith("#"):
                self.fragment_refs.add(value[1:])
                continue
            parsed = urlparse(value)
            if parsed.scheme:
                if parsed.scheme.lower() == "http":
                    self.insecure_external_refs.append(value)
                continue
            if value.startswith("//"):
                self.insecure_external_refs.append(value)
                continue
            self.local_refs.add(parsed.path)

        if attrs.get("target") == "_blank":
            rel = set(attrs.get("rel", "").split())
            if not {"noopener", "noreferrer"}.issubset(rel):
                self.external_blank_errors.append(attrs.get("href", "(missing href)"))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_css(errors: list[str]) -> None:
    for path in sorted((ROOT / "css").glob("*.css")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if text.count("{") != text.count("}"):
            fail(errors, f"Unbalanced CSS braces in {path.relative_to(ROOT)}.")


def validate_security_contact(errors: list[str]) -> None:
    if not SECURITY.exists():
        fail(errors, "Standardized public security contact is missing: .well-known/security.txt")
        return

    text = SECURITY.read_text(encoding="utf-8")
    fields: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()

    for field, expected in REQUIRED_SECURITY_FIELDS.items():
        if fields.get(field) != expected:
            fail(errors, f"security.txt field {field!r} must be {expected!r}, found {fields.get(field)!r}.")

    expires_raw = fields.get("Expires")
    if not expires_raw:
        fail(errors, "security.txt must include an Expires field.")
        return

    try:
        expires = datetime.fromisoformat(expires_raw.replace("Z", "+00:00"))
    except ValueError:
        fail(errors, f"security.txt Expires value is not valid ISO 8601: {expires_raw!r}.")
        return

    if expires.tzinfo is None:
        fail(errors, "security.txt Expires value must include a timezone.")
        return

    if expires <= datetime.now(timezone.utc):
        fail(errors, f"security.txt has expired: {expires_raw}.")


def render_homepage() -> str:
    manifest = load_manifest()
    source = INDEX.read_text(encoding="utf-8")
    rendered = render_public_file("index.html", source, manifest)
    rendered = normalize_homepage(rendered)
    return apply_glaze_ui_2(rendered)


def validate() -> list[str]:
    errors: list[str] = []
    html = render_homepage()
    parser = SiteParser()
    parser.feed(html)

    if parser.html_lang != "en":
        fail(errors, f"Root html language must be 'en', found {parser.html_lang!r}.")
    if not parser.title:
        fail(errors, "Document title must not be empty.")
    if not parser.description:
        fail(errors, "Meta description must not be empty.")
    if parser.h1_count != 1:
        fail(errors, f"Homepage must contain exactly one h1, found {parser.h1_count}.")

    duplicate_ids = sorted(identifier for identifier, count in parser.id_counts.items() if count > 1)
    for identifier in duplicate_ids:
        fail(errors, f"Duplicate id found in rendered index.html: {identifier}")

    if parser.canonical != CANONICAL:
        fail(errors, f"Canonical URL must be {CANONICAL!r}, found {parser.canonical!r}.")
    if parser.og_url != CANONICAL:
        fail(errors, f"Open Graph URL must be {CANONICAL!r}, found {parser.og_url!r}.")

    missing_fragments = sorted(ref for ref in parser.fragment_refs if ref and ref not in parser.ids)
    for fragment in missing_fragments:
        fail(errors, f"Missing in-page target for #{fragment}.")

    for reference in sorted(parser.local_refs):
        local_path = reference.lstrip("/") if reference.startswith("/") else reference
        target = (ROOT / local_path).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            fail(errors, f"Local reference escapes repository root: {reference}")
            continue
        if not target.exists():
            fail(errors, f"Missing local asset referenced by rendered index.html: {reference}")

    for href in parser.external_blank_errors:
        fail(errors, f'target="_blank" link must include rel="noopener noreferrer": {href}')
    for reference in parser.insecure_external_refs:
        fail(errors, f"External web references must use explicit HTTPS: {reference}")
    for image in parser.missing_alt_images:
        fail(errors, f"Image must include an alt attribute, even when decorative: {image}")
    if parser.inline_script_count:
        fail(errors, "Inline script blocks are not allowed by the self-only Content Security Policy.")
    if parser.inline_style_count:
        fail(errors, "Inline style blocks are not allowed by the self-only Content Security Policy.")
    for handler in parser.inline_event_handlers:
        fail(errors, f"Inline event handlers are not allowed by the self-only Content Security Policy: {handler}")

    for src in parser.script_sources + parser.stylesheet_sources:
        if urlparse(src).scheme or src.startswith("//"):
            fail(errors, f"Browser code dependency must be self-hosted, found external resource: {src}")

    missing_stylesheets = sorted(REQUIRED_STYLESHEETS.difference(parser.stylesheet_sources))
    for stylesheet in missing_stylesheets:
        fail(errors, f"Required stylesheet is not linked from the rendered index.html: {stylesheet}")

    missing_scripts = sorted(REQUIRED_SCRIPTS.difference(parser.script_sources))
    for script in missing_scripts:
        fail(errors, f"Required script is not loaded from the rendered index.html: {script}")

    theme_init_markup = '<script src="js/theme-init.js"></script>'
    first_stylesheet_markup = '<link rel="stylesheet"'
    if theme_init_markup not in html:
        fail(errors, "Early appearance initialization script is missing from rendered index.html.")
    elif first_stylesheet_markup in html and html.index(theme_init_markup) > html.index(first_stylesheet_markup):
        fail(errors, "js/theme-init.js must load before stylesheets so stored appearance is applied before first paint.")

    if 'class="theme-toggle"' not in html or 'class="theme-toggle" type="button"' not in html:
        fail(errors, "Appearance control markup is missing or malformed.")
    if 'title="Switch theme" hidden' not in html:
        fail(errors, "Appearance control must remain hidden until the interaction script is active.")
    if '<span id="year">2026</span>' not in html:
        fail(errors, "Footer must include a no-JavaScript copyright-year fallback.")

    for label, marker in REQUIRED_PUBLIC_MARKERS.items():
        if marker not in html:
            fail(errors, f"Required current-state public marker is missing: {label}.")
    for stale_copy in STALE_PUBLIC_COPY:
        if stale_copy in html:
            fail(errors, f"Obsolete public project wording must not return: {stale_copy}")

    public_text_files = [
        INDEX,
        ROOT / "README.md",
        ROOT / "robots.txt",
        ROOT / "sitemap.xml",
        ROOT / "_headers",
        SECURITY,
    ]
    public_text_files.extend((ROOT / "css").glob("*.css"))
    public_text_files.extend((ROOT / "js").glob("*.js"))

    for path in public_text_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in PRIVATE_PATTERNS:
            match = pattern.search(text)
            if match:
                fail(errors, f"Private-range IP address found in {path.relative_to(ROOT)}: {match.group(0)}")
        lower_text = text.lower()
        for term in SENSITIVE_TERMS:
            if term.lower() in lower_text:
                fail(errors, f"Private infrastructure identifier found in {path.relative_to(ROOT)}: {term}")

    main_js = (ROOT / "js" / "main.js").read_text(encoding="utf-8")
    theme_init_js = (ROOT / "js" / "theme-init.js").read_text(encoding="utf-8")
    polish_css = (ROOT / "css" / "glaze-polish.css").read_text(encoding="utf-8")

    if "'system', 'light', 'dark'" not in main_js:
        fail(errors, "Appearance control must preserve System, Light, and Dark modes.")
    if "root.dataset.js = 'true'" not in main_js:
        fail(errors, "Interaction script must identify the enhanced JavaScript state for progressive navigation behavior.")
    if "themeToggle.hidden = false" not in main_js:
        fail(errors, "Interaction script must reveal the appearance control only after JavaScript is active.")
    if "updateNavigationControl(open)" not in main_js or "'Close navigation'" not in main_js or "'Open navigation'" not in main_js:
        fail(errors, "Mobile navigation must update its accessible control label for open and closed states.")
    if "localStorage.getItem(THEME_STORAGE_KEY)" not in theme_init_js:
        fail(errors, "Early appearance initialization must restore an explicit local browser preference when present.")
    if 'html:not([data-js="true"]) .site-nav' not in polish_css:
        fail(errors, "Mobile navigation must retain a visible no-JavaScript fallback.")
    if "@media (prefers-contrast: more)" not in polish_css:
        fail(errors, "Glaze UI must include an increased-contrast fallback.")
    if "@media (forced-colors: active)" not in polish_css:
        fail(errors, "Glaze UI must include a forced-colors fallback.")
    if "@media print" not in polish_css:
        fail(errors, "Glaze UI must include a print/readable-paper fallback.")

    validate_css(errors)
    validate_security_contact(errors)

    headers = (ROOT / "_headers").read_text(encoding="utf-8")
    for required_header in REQUIRED_HEADERS:
        if required_header not in headers:
            fail(errors, f"Required security/privacy header is missing: {required_header}")
    if "/.well-known/security.txt" not in headers or "Cache-Control: public, max-age=3600" not in headers:
        fail(errors, "security.txt must have an explicit one-hour cache policy in _headers.")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {CANONICAL}sitemap.xml" not in robots:
        fail(errors, "robots.txt sitemap URL does not match the canonical www hostname.")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    if f"<loc>{CANONICAL}</loc>" not in sitemap:
        fail(errors, "sitemap.xml does not contain the canonical www homepage URL.")
    if not re.search(r"<lastmod>\d{4}-\d{2}-\d{2}</lastmod>", sitemap):
        fail(errors, "sitemap.xml must include a YYYY-MM-DD lastmod value for the homepage.")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Website validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Website validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
