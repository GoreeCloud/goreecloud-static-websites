#!/usr/bin/env python3
"""Validate Main's public privacy statement and consent-first PostHog contract."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PRIVACY_PAGE = ROOT / "privacy.html"
HEADERS = ROOT / "_headers"
THEME_INIT_JS = ROOT / "js" / "theme-init.js"
TELEMETRY_JS = ROOT / "js" / "telemetry.js"
TELEMETRY_REVIEW = ROOT / "docs" / "posthog-telemetry-review.md"
PRIVACY_URL = "https://www.goreecloud.com/privacy.html"
POSTHOG_ASSET_ORIGIN = "https://us-assets.i.posthog.com"
POSTHOG_INGEST_ORIGIN = "https://us.i.posthog.com"

PRIVATE_PATTERNS = (
    re.compile(r"\b10(?:\.\d{1,3}){3}\b"),
    re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2}\b"),
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
        if tag == "link" and "canonical" in attrs.get("rel", "").split():
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
                if parsed.scheme == "http":
                    self.insecure_refs.append(value)
                elif parsed.scheme not in {"https", "mailto"}:
                    self.unsupported_schemes.append(value)
                continue
            if value.startswith("//"):
                self.insecure_refs.append(value)
            else:
                self.local_refs.add(parsed.path)


def report(errors: list[str]) -> int:
    if errors:
        print("Privacy and telemetry validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Privacy and telemetry validation passed: consent-first PostHog contract is coherent.")
    return 0


def require(source: str, markers: tuple[str, ...], label: str, errors: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            errors.append(f"{label} is missing required marker: {marker}")


def main() -> int:
    errors: list[str] = []
    for path in (PRIVACY_PAGE, HEADERS, THEME_INIT_JS, TELEMETRY_JS, TELEMETRY_REVIEW):
        if not path.is_file():
            errors.append(f"Required privacy resource is missing: {path.relative_to(ROOT)}")
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
    if parser.inline_scripts:
        errors.append("privacy.html must not contain inline scripts.")
    if parser.inline_styles:
        errors.append("privacy.html must not contain inline styles.")
    if parser.inline_handlers:
        errors.append("privacy.html must not contain inline event handlers.")
    if parser.missing_alt:
        errors.append("Every privacy.html image must include alt text, including an empty decorative alt.")
    if parser.insecure_refs:
        errors.append(f"privacy.html contains insecure references: {parser.insecure_refs}")
    if parser.unsupported_schemes:
        errors.append(f"privacy.html contains unsupported URL schemes: {parser.unsupported_schemes}")
    for identifier, count in sorted(parser.id_counts.items()):
        if count > 1:
            errors.append(f"Duplicate id in privacy.html: {identifier}")

    for reference in sorted(parser.local_refs):
        target = (ROOT / reference).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"privacy.html local reference escapes site root: {reference}")
            continue
        if not target.exists():
            errors.append(f"privacy.html references missing local resource: {reference}")

    normalized = re.sub(r"\s+", " ", html).lower()
    required_privacy_copy = (
        "optional analytics off",
        "posthog us cloud",
        "website opened",
        "discard client ip data",
        "disables geoip enrichment",
        "no person profile",
        "goreecloud-analytics-consent",
        "analytics preferences",
        "12-month event-retention",
        "cloudflare pages",
        "goreecloud-theme",
        "referrer-policy: no-referrer",
        "privacy shield",
    )
    for marker in required_privacy_copy:
        if marker not in normalized:
            errors.append(f"privacy.html does not disclose required behavior: {marker}")

    headers = HEADERS.read_text(encoding="utf-8")
    require(
        headers,
        (
            "Referrer-Policy: no-referrer",
            f"script-src 'self' {POSTHOG_ASSET_ORIGIN}",
            f"connect-src 'self' {POSTHOG_INGEST_ORIGIN}",
        ),
        "_headers",
        errors,
    )
    if "*.posthog.com" in headers:
        errors.append("CSP must not use a wildcard PostHog origin.")
    if headers.count(POSTHOG_ASSET_ORIGIN) != 1:
        errors.append("PostHog asset origin must appear exactly once in the CSP.")
    if headers.count(POSTHOG_INGEST_ORIGIN) != 1:
        errors.append("PostHog ingest origin must appear exactly once in the CSP.")

    telemetry = TELEMETRY_JS.read_text(encoding="utf-8")
    require(
        telemetry,
        (
            "const POSTHOG_ACTIVATION = true;",
            "const CONSENT_STORAGE_KEY = 'goreecloud-analytics-consent';",
            "if (readConsent() !== 'granted') return;",
            "autocapture: false",
            "capture_pageview: false",
            "capture_pageleave: false",
            "capture_dead_clicks: false",
            "capture_exceptions: false",
            "capture_heatmaps: false",
            "capture_performance: false",
            "disable_session_recording: true",
            "disable_external_dependency_loading: true",
            "advanced_disable_flags: true",
            "persistence: 'memory'",
            "cross_subdomain_cookie: false",
            "before_send: scrubEvent",
            "event.event !== WEBSITE_EVENT",
            "$process_person_profile: false",
            "$geoip_disable: true",
            "window.posthog.opt_out_capturing();",
            "Analytics preferences",
        ),
        "telemetry.js",
        errors,
    )
    if "window.posthog.identify(" in telemetry:
        errors.append("Website telemetry must not identify visitors.")
    if "document.cookie" in telemetry:
        errors.append("Website telemetry must not manage a first-party tracking cookie.")
    if telemetry.count(POSTHOG_INGEST_ORIGIN) != 1:
        errors.append("telemetry.js must contain exactly one approved PostHog API host.")

    theme_init = THEME_INIT_JS.read_text(encoding="utf-8")
    require(
        theme_init,
        (
            "const TELEMETRY_MODULE_HREF = '/js/telemetry.js';",
            "ensureTelemetryModule();",
        ),
        "theme-init.js",
        errors,
    )

    review = TELEMETRY_REVIEW.read_text(encoding="utf-8")
    require(
        review,
        (
            "**Status:** Activation candidate / production verification pending",
            "anonymize_ips: true",
            "POSTHOG_ACTIVATION = true",
            "$geoip_disable: true",
            "12-month event-retention",
            "Source activation is not production acceptance",
            "production deployment remains `legacy-source`",
        ),
        "posthog-telemetry-review.md",
        errors,
    )

    for path in (PRIVACY_PAGE, TELEMETRY_JS):
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in PRIVATE_PATTERNS:
            match = pattern.search(text)
            if match:
                errors.append(f"Private-range IP address found in {path.relative_to(ROOT)}: {match.group(0)}")

    return report(errors)


if __name__ == "__main__":
    sys.exit(main())
