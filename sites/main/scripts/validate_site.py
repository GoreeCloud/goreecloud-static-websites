#!/usr/bin/env python3
"""Validate the source-native GoreeCloud Main website and public truth boundaries."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

from normalize_homepage import normalize_homepage
from render_repository_portfolio import load_manifest, render_public_file

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
SECURITY_TXT = ROOT / ".well-known" / "security.txt"
CANONICAL = "https://www.goreecloud.com/"

PRIVATE_PATTERNS = (
    re.compile(r"\b10(?:\.\d{1,3}){3}\b"),
    re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2}\b"),
)

REQUIRED_MARKERS = (
    "Thirteen official surfaces. One GoreeCloud ecosystem.",
    "45 verified Suite products",
    "9 functional product groups",
    "seven Integral Platform Systems",
    "Glaze UI",
    "Privacy Shield",
    "Wardveil Security",
    "Everkeep",
    "GoreeCloud Mesh",
    "GoreeCloud Identity",
    "GoreeCloud Manager",
    "mesh.goreecloud.com",
    "id.goreecloud.com",
    "manage.goreecloud.com",
    "source migration does not establish Cloudflare source cutover",
    "GoreeCloud Home",
    "GoreeCloud Home Security",
    "GoreeCloud Health",
    "Reader",
    "GoreeCloud Router OS",
    "GoreeCloud AI",
    "this website does not publish a fragile “current repository count.”",
    "Ownership should be understandable and repeatable.",
    "From services to a first-party ecosystem.",
    '<section id="follow"',
    '<section id="contact"',
    "https://www.youtube.com/@GoreeCloud",
)
STALE = (
    "current 57-repository portfolio",
    "57 repositories",
    "40 public repositories",
    "17 private repositories",
    "identity.goreecloud.com",
    "Glaze UI 2.1",
    "Glaze UI 2.2",
    "Six substantive platform systems",
    "Ten independently deployed public destinations",
    "Eleven official surfaces",
    "Privacy-First Personal & Family Cloud",
    "personal and family cloud",
    "family digital foundation",
    "More than a homelab.",
    "Built deliberately from the beginning.",
    "started in 2026 as a self-hosting plan",
    "want to talk self-hosting",
    "<h3>Home Assistant</h3>",
    "<h3>Frigate</h3>",
    "assets/roadmap/home-assistant.png",
    "assets/roadmap/frigate.svg",
)


class Audit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = Counter()
        self.canonical = None
        self.og_url = None
        self.description = None
        self.h1 = 0
        self.title_parts = []
        self._title = False
        self.scripts = []
        self.styles = []
        self.external_blank_errors = []
        self.inline_scripts = 0
        self.inline_styles = 0
        self.missing_alt = []

    def handle_starttag(self, tag, attrs_list):
        attrs = {k: v or "" for k, v in attrs_list}
        if attrs.get("id"): self.ids[attrs["id"]] += 1
        if tag == "h1": self.h1 += 1
        if tag == "title": self._title = True
        if tag == "link":
            rel = set(attrs.get("rel", "").split())
            if "canonical" in rel: self.canonical = attrs.get("href")
            if "stylesheet" in rel and attrs.get("href"): self.styles.append(attrs["href"])
        if tag == "meta":
            if attrs.get("property") == "og:url": self.og_url = attrs.get("content")
            if attrs.get("name") == "description": self.description = attrs.get("content")
        if tag == "script":
            if attrs.get("src"): self.scripts.append(attrs["src"])
            else: self.inline_scripts += 1
        if tag == "style": self.inline_styles += 1
        if tag == "img" and "alt" not in attrs: self.missing_alt.append(attrs.get("src", ""))
        if attrs.get("target") == "_blank":
            rel = set(attrs.get("rel", "").split())
            if not {"noopener", "noreferrer"}.issubset(rel): self.external_blank_errors.append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag == "title": self._title = False

    def handle_data(self, data):
        if self._title: self.title_parts.append(data)


def rendered_homepage() -> str:
    manifest = load_manifest(ROOT)
    text = render_public_file("index.html", INDEX.read_text(encoding="utf-8"), manifest)
    return normalize_homepage(text)


def main() -> int:
    errors: list[str] = []
    try:
        html = rendered_homepage()
    except (OSError, ValueError) as exc:
        print(f"Website validation failed: {exc}")
        return 1

    audit = Audit(); audit.feed(html)
    if audit.canonical != CANONICAL: errors.append(f"homepage canonical must be {CANONICAL}")
    if audit.og_url != CANONICAL: errors.append("homepage Open Graph URL mismatch")
    if not audit.description: errors.append("homepage description missing")
    if audit.h1 != 1: errors.append(f"homepage must contain one h1, found {audit.h1}")
    if not "".join(audit.title_parts).strip(): errors.append("homepage title missing")
    if audit.inline_scripts or audit.inline_styles: errors.append("inline script/style violates self-only CSP")
    if audit.missing_alt: errors.append("all homepage images require alt attributes")
    if audit.external_blank_errors: errors.append("target=_blank links require noopener noreferrer")
    for identifier, count in audit.ids.items():
        if count > 1: errors.append(f"duplicate homepage id: {identifier}")

    if "js/theme-init.js" not in audit.scripts or "js/main.js" not in audit.scripts:
        errors.append("required appearance/navigation scripts missing")
    for required_css in (
        "css/style.css",
        "css/glaze.css",
        "css/glaze-v1.3.0.css",
        "css/glaze-polish.css",
        "css/homepage-v7.css",
    ):
        if required_css not in audit.styles: errors.append(f"required stylesheet missing: {required_css}")
    if html.index('<script src="js/theme-init.js"></script>') > html.index('<link rel="stylesheet"'):
        errors.append("theme-init must run before first stylesheet")
    if 'class="theme-toggle" type="button"' not in html or 'title="Switch theme" hidden' not in html:
        errors.append("progressive appearance control markup missing")
    if '<span id="year">2026</span>' not in html:
        errors.append("copyright fallback year missing")

    for marker in REQUIRED_MARKERS:
        if marker not in html: errors.append(f"required current public marker missing: {marker}")
    for stale in STALE:
        if stale in html: errors.append(f"superseded current-state copy remains: {stale}")

    repo = (ROOT / "repositories.html").read_text(encoding="utf-8")
    for marker in ("GitHub organization", "authoritative for current inventory", "goreecloud-static-websites", "goreecloud-health", "goreecloud-reader", "goreecloud-router-os", "goreecloud-os-desktop", "goreecloud-os-tv"):
        if marker not in repo: errors.append(f"repository guide missing current role marker: {marker}")
    for stale in ("57", "40 public", "17 private", "current repository portfolio"):
        if stale in repo: errors.append(f"repository guide still presents obsolete snapshot wording: {stale}")

    main_js = (ROOT / "js/main.js").read_text(encoding="utf-8")
    theme_js = (ROOT / "js/theme-init.js").read_text(encoding="utf-8")
    polish = (ROOT / "css/glaze-polish.css").read_text(encoding="utf-8")
    if "'system', 'light', 'dark'" not in main_js: errors.append("System/Light/Dark appearance modes missing")
    if "root.dataset.js = 'true'" not in main_js: errors.append("progressive JavaScript state marker missing")
    if "localStorage.getItem(THEME_STORAGE_KEY)" not in theme_js: errors.append("appearance preference restoration missing")
    for marker in ("prefers-reduced-motion", "prefers-reduced-transparency", "prefers-contrast: more", "forced-colors: active", "@media print"):
        if marker not in polish: errors.append(f"consumer accessibility fallback missing: {marker}")

    headers = (ROOT / "_headers").read_text(encoding="utf-8")
    for marker in ("Content-Security-Policy:", "Referrer-Policy: no-referrer", "Origin-Agent-Cluster: ?1"):
        if marker not in headers: errors.append(f"required public header missing: {marker}")

    if not SECURITY_TXT.is_file():
        errors.append(".well-known/security.txt missing")
    else:
        security = SECURITY_TXT.read_text(encoding="utf-8")
        for marker in ("Contact: mailto:security@goreecloud.com", "Preferred-Languages: en", "Canonical: https://www.goreecloud.com/.well-known/security.txt"):
            if marker not in security: errors.append(f"security.txt marker missing: {marker}")
        match = re.search(r"^Expires:\s*(.+)$", security, re.MULTILINE)
        if not match:
            errors.append("security.txt Expires missing")
        else:
            try:
                expires = datetime.fromisoformat(match.group(1).strip().replace("Z", "+00:00"))
                if expires <= datetime.now(timezone.utc): errors.append("security.txt is expired")
            except ValueError:
                errors.append("security.txt Expires invalid")

    for path in [INDEX, ROOT / "repositories.html", ROOT / "privacy.html", ROOT / "security.html", ROOT / "README.md", ROOT / "_headers", SECURITY_TXT]:
        if not path.is_file(): continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text): errors.append(f"private-range IP found in {path.relative_to(ROOT)}")

    if errors:
        print("Website validation failed:")
        for error in errors: print(f"  - {error}")
        return 1
    print("Website validation passed: current source-native V1.3 public truth boundary is coherent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
