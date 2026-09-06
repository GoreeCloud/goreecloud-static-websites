#!/usr/bin/env python3
"""Validate the public GoreeCloud privacy statement against site behavior."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PRIVACY_PAGE = ROOT / "privacy.html"
SITEMAP = ROOT / "sitemap.xml"
HEADERS = ROOT / "_headers"
MAIN_JS = ROOT / "js" / "main.js"
THEME_INIT_JS = ROOT / "js" / "theme-init.js"
PRIVACY_URL = "https://www.goreecloud.com/privacy.html"
PRIVATE_PATTERNS = (
    re.compile(r"\b10(?:\.\d{1,3}){3}\b"),
    re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2}\b"),
)
SENSITIVE_TERMS = ("goreecloud-vps-01", ".netbird.selfhosted")
REQUIRED_COPY = (
    "Privacy at GoreeCloud",
    "No behavioral tracking.",
    "third-party browser resources",
    "Browser-loaded site resources are kept on the GoreeCloud origin",
    "goreecloud-theme",
    "localStorage",
    "System mode requires no stored preference",
    "Cloudflare Pages",
    "Referrer-Policy: no-referrer",
    "external links",
    "mailto:",
    "goreecloud@gmail.com",
    "security-reporting policy",
)
TRACKING_MARKERS = (
    "google-analytics",
    "googletagmanager",
    "gtag(",
    "plausible",
    "umami",
    "matomo",
    "mixpanel",
    "hotjar",
    "facebook.com/tr",
    "document.cookie",
)


class PrivacyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.id_counts: Counter[str] = Counter()
        self.local_refs: set[str] = set()
        self.insecure_refs: list[str] = []
        self.unsupported_schemes: list[str] = []
        self.inline_scripts = 0
        self.inline_styles = 0
        self.inline_handlers: list[str] = []
        self.missing_alt: list[str] = []
        self.canonical: str | None = None
        self.robots: str | None = None
        self.lang: str | None = None
        self.h1_count = 0

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "h1":
            self.h1_count += 1
        if attrs.get("id"):
            self.id_counts[attrs["id"]] += 1
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "meta" and attrs.get("name") == "robots":
            self.robots = attrs.get("content")
        if tag == "script" and not attrs.get("src"):
            self.inline_scripts += 1
        if tag == "style":
            self.inline_styles += 1
        if tag == "img" and "alt" not in attrs:
            self.missing_alt.append(attrs.get("src", "(missing src)"))
        for name in attrs:
            if name.lower().startswith("on"):
                self.inline_handlers.append(f"<{tag} {name}=...>")

        for attr in ("href", "src"):
            value = attrs.get(attr, "")
            if not value or value.startswith("#"):
                continue
            parsed = urlparse(value)
            if parsed.scheme:
                scheme = parsed.scheme.lower()
                if scheme == "http":
                    self.insecure_refs.append(value)
                elif scheme not in {"https", "mailto"}:
                    self.unsupported_schemes.append(value)
                continue
            if value.startswith("//"):
                self.insecure_refs.append(value)
                continue
            self.local_refs.add(parsed.path)


def report(errors: list[str]) -> int:
    if errors:
        print("Privacy statement validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Privacy statement validation passed.")
    return 0


def main() -> int:
    errors: list[str] = []
    required_paths = (PRIVACY_PAGE, SITEMAP, HEADERS, MAIN_JS, THEME_INIT_JS)
    for path in required_paths:
        if not path.exists():
            errors.append(f"Required privacy-validation resource is missing: {path.relative_to(ROOT)}")
    if errors:
        return report(errors)

    html = PRIVACY_PAGE.read_text(encoding="utf-8")
    parser = PrivacyParser()
    parser.feed(html)

    if parser.lang != "en":
        errors.append(f"privacy.html language must be 'en', found {parser.lang!r}.")
    if parser.h1_count != 1:
        errors.append(f"privacy.html must contain exactly one h1, found {parser.h1_count}.")
    if parser.canonical != PRIVACY_URL:
        errors.append(f"privacy.html canonical must be {PRIVACY_URL!r}, found {parser.canonical!r}.")
    if not parser.robots or "noindex" in parser.robots.lower():
        errors.append("privacy.html must remain indexable public guidance.")

    for identifier, count in sorted(parser.id_counts.items()):
        if count > 1:
            errors.append(f"Duplicate id in privacy.html: {identifier}")
    if parser.inline_scripts:
        errors.append("privacy.html must not contain inline script blocks.")
    if parser.inline_styles:
        errors.append("privacy.html must not contain inline style blocks.")
    for handler in parser.inline_handlers:
        errors.append(f"privacy.html must not contain inline event handlers: {handler}")
    for image in parser.missing_alt:
        errors.append(f"Image in privacy.html must include an alt attribute: {image}")
    for reference in parser.insecure_refs:
        errors.append(f"privacy.html web references must use explicit HTTPS: {reference}")
    for reference in parser.unsupported_schemes:
        errors.append(f"privacy.html uses an unsupported external scheme: {reference}")

    for reference in sorted(parser.local_refs):
        target = (ROOT / reference).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"privacy.html local reference escapes repository root: {reference}")
            continue
        if not target.exists():
            errors.append(f"privacy.html references missing local resource: {reference}")

    normalized_html = re.sub(r"\s+", " ", html).lower()
    for marker in REQUIRED_COPY:
        normalized_marker = re.sub(r"\s+", " ", marker).lower()
        if normalized_marker not in normalized_html:
            errors.append(f"privacy.html required statement is missing: {marker}")

    sitemap = SITEMAP.read_text(encoding="utf-8")
    if f"<loc>{PRIVACY_URL}</loc>" not in sitemap:
        errors.append("sitemap.xml must publish the canonical privacy statement URL.")
    if not re.search(
        rf"<url>\s*<loc>{re.escape(PRIVACY_URL)}</loc>\s*<lastmod>\d{{4}}-\d{{2}}-\d{{2}}</lastmod>\s*</url>",
        sitemap,
        re.DOTALL,
    ):
        errors.append("The privacy statement sitemap entry must include a YYYY-MM-DD lastmod value.")

    headers = HEADERS.read_text(encoding="utf-8")
    for marker in (
        "Referrer-Policy: no-referrer",
        "script-src 'self'",
    ):
        if marker not in headers:
            errors.append(f"Privacy statement depends on missing public-site header control: {marker}")
    if "connect-src 'none'" not in headers and "connect-src 'self'" not in headers:
        errors.append(
            "Privacy statement depends on a restrictive connect-src policy; expected 'none' or 'self'."
        )

    main_js = MAIN_JS.read_text(encoding="utf-8")
    theme_init = THEME_INIT_JS.read_text(encoding="utf-8")
    storage_requirements = (
        (main_js, "localStorage.setItem(THEME_STORAGE_KEY, mode)", "explicit theme persistence"),
        (main_js, "localStorage.removeItem(THEME_STORAGE_KEY)", "System-mode storage removal"),
        (theme_init, "localStorage.getItem(THEME_STORAGE_KEY)", "early stored-theme restoration"),
        (main_js, "const THEME_STORAGE_KEY = 'goreecloud-theme'", "theme storage key"),
    )
    for source, marker, label in storage_requirements:
        if marker not in source:
            errors.append(f"Privacy statement no longer matches website {label} behavior.")

    browser_code = "\n".join(
        path.read_text(encoding="utf-8", errors="replace").lower()
        for path in sorted((ROOT / "js").glob("*.js"))
    )
    for marker in TRACKING_MARKERS:
        if marker.lower() in browser_code:
            errors.append(f"Tracking-related browser-code marker conflicts with privacy statement: {marker}")

    for path in (PRIVACY_PAGE,):
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in PRIVATE_PATTERNS:
            match = pattern.search(text)
            if match:
                errors.append(f"Private-range IP address found in {path.relative_to(ROOT)}: {match.group(0)}")
        lower = text.lower()
        for term in SENSITIVE_TERMS:
            if term.lower() in lower:
                errors.append(f"Private infrastructure identifier found in {path.relative_to(ROOT)}: {term}")

    return report(errors)


if __name__ == "__main__":
    sys.exit(main())
