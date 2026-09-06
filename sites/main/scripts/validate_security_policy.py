#!/usr/bin/env python3
"""Validate GoreeCloud public security-reporting metadata and Wardveil policy surfaces."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SECURITY_TXT = ROOT / ".well-known" / "security.txt"
SECURITY_PAGE = ROOT / "security.html"
SECURITY_MD = ROOT / "SECURITY.md"
SITEMAP = ROOT / "sitemap.xml"
POLICY_URL = "https://www.goreecloud.com/security.html"
CANONICAL_SECURITY_TXT = "https://www.goreecloud.com/.well-known/security.txt"
PRIMARY_CONTACT = "mailto:security@goreecloud.com"
WARDVEIL_IDENTITY = "Wardveil Security by GoreeCloud"
EXPIRY_RENEWAL_BUFFER = timedelta(days=30)
MAX_EXPIRY_HORIZON = timedelta(days=365)
PRIVATE_PATTERNS = (
    re.compile(r"\b10(?:\.\d{1,3}){3}\b"),
    re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2}\b"),
)
SENSITIVE_TERMS = ("goreecloud-vps-01", ".netbird.selfhosted")
REQUIRED_COPY = (
    "Responsible security reporting",
    WARDVEIL_IDENTITY,
    "platform-wide first-party security system and shared security plane",
    "Foundation 0.9",
    "Sentinel Fold",
    "Six complementary platform systems",
    "GoreeCloud Identity",
    "production ClamAV scanner runtime is deployed and accepted at the scanner-evidence layer",
    "does not establish end-to-end Wardveil Scan application acceptance",
    "security@goreecloud.com",
    "/.well-known/security.txt",
    "does not currently offer a bug bounty",
    "does not authorize testing of private family infrastructure",
)
REQUIRED_REPOSITORY_POLICY_COPY = (
    "Do **not** open a public GitHub issue",
    WARDVEIL_IDENTITY,
    "platform-wide first-party security system and shared security plane",
    "Foundation 0.9",
    "Sentinel Fold",
    "production ClamAV scanner runtime is deployed and accepted at the scanner-evidence layer",
    "does not establish end-to-end Wardveil Scan application acceptance",
    "security@goreecloud.com",
    POLICY_URL,
    CANONICAL_SECURITY_TXT,
    "does not authorize testing of private family infrastructure",
    "does not currently offer a bug bounty",
)
STALE_WARDVEIL_COPY = (
    "security identity and presentation layer",
    "Three complementary GoreeCloud foundations",
    "Five complementary platform systems",
    "production ClamAV runtime remains unaccepted",
)


class PolicyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.id_counts: Counter[str] = Counter()
        self.local_refs: set[str] = set()
        self.external_refs: list[str] = []
        self.insecure_refs: list[str] = []
        self.inline_scripts = 0
        self.inline_styles = 0
        self.inline_handlers: list[str] = []
        self.missing_alt: list[str] = []
        self.canonical: str | None = None
        self.robots: str | None = None
        self.lang: str | None = None
        self.h1_count = 0
        self.security_identity: str | None = None

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
        if tag == "meta" and attrs.get("name") == "goreecloud-security-identity":
            self.security_identity = attrs.get("content")
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
                if parsed.scheme.lower() == "http":
                    self.insecure_refs.append(value)
                elif parsed.scheme.lower() not in {"https", "mailto"}:
                    self.external_refs.append(value)
                continue
            if value.startswith("//"):
                self.insecure_refs.append(value)
                continue
            self.local_refs.add(parsed.path)


def parse_security_txt(errors: list[str]) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}
    for line_number, raw_line in enumerate(SECURITY_TXT.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"security.txt line {line_number} is not a field-name/value pair.")
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if not key or not value:
            errors.append(f"security.txt line {line_number} has an empty field name or value.")
            continue
        fields.setdefault(key, []).append(value)
    return fields


def parse_rfc3339(value: str) -> datetime | None:
    normalized = value[:-1] + "+00:00" if value.endswith(("Z", "z")) else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def validate_security_txt(errors: list[str], fields: dict[str, list[str]]) -> None:
    contacts = fields.get("contact", [])
    if not contacts:
        errors.append("security.txt must contain at least one Contact field.")
    elif contacts[0] != PRIMARY_CONTACT:
        errors.append(f"security.txt preferred Contact must remain {PRIMARY_CONTACT!r}, found {contacts[0]!r}.")
    for contact in contacts:
        parsed = urlparse(contact)
        if parsed.scheme not in {"mailto", "https", "tel"}:
            errors.append(f"security.txt Contact uses an unsupported URI scheme: {contact}")
        if parsed.scheme == "https" and not parsed.netloc:
            errors.append(f"security.txt Contact HTTPS URI is malformed: {contact}")

    expires_values = fields.get("expires", [])
    if len(expires_values) != 1:
        errors.append(f"security.txt must contain exactly one Expires field, found {len(expires_values)}.")
    else:
        expires = parse_rfc3339(expires_values[0])
        if expires is None:
            errors.append("security.txt Expires must be an RFC3339 timestamp with an explicit timezone.")
        else:
            remaining = expires - datetime.now(timezone.utc)
            if remaining <= EXPIRY_RENEWAL_BUFFER:
                errors.append("security.txt Expires must stay more than 30 days in the future so CI provides a renewal window.")
            if remaining >= MAX_EXPIRY_HORIZON:
                errors.append("security.txt Expires must remain less than 365 days in the future to avoid stale disclosure metadata.")

    preferred_languages = fields.get("preferred-languages", [])
    if len(preferred_languages) > 1:
        errors.append("security.txt Preferred-Languages must not appear more than once.")
    elif preferred_languages:
        languages = [value.strip().lower() for value in preferred_languages[0].split(",") if value.strip()]
        if not languages or "en" not in languages:
            errors.append("security.txt Preferred-Languages must continue to include English ('en').")

    canonical_values = fields.get("canonical", [])
    if CANONICAL_SECURITY_TXT not in canonical_values:
        errors.append(f"security.txt must publish its canonical URI: {CANONICAL_SECURITY_TXT}")
    for canonical in canonical_values:
        parsed = urlparse(canonical)
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"security.txt Canonical web URI must use explicit HTTPS: {canonical}")

    policy_values = fields.get("policy", [])
    if POLICY_URL not in policy_values:
        errors.append(f"security.txt Policy must include {POLICY_URL!r}.")
    for policy in policy_values:
        parsed = urlparse(policy)
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"security.txt Policy web URI must use explicit HTTPS: {policy}")


def main() -> int:
    errors: list[str] = []

    for path in (SECURITY_TXT, SECURITY_PAGE, SECURITY_MD, SITEMAP):
        if not path.exists():
            errors.append(f"Required security-reporting file is missing: {path.relative_to(ROOT)}")
    if errors:
        return report(errors)

    fields = parse_security_txt(errors)
    validate_security_txt(errors, fields)

    sitemap = SITEMAP.read_text(encoding="utf-8")
    if f"<loc>{POLICY_URL}</loc>" not in sitemap:
        errors.append("sitemap.xml must publish the canonical security policy URL.")
    policy_entry = re.search(
        rf"<url>\s*<loc>{re.escape(POLICY_URL)}</loc>\s*<lastmod>(\d{{4}}-\d{{2}}-\d{{2}})</lastmod>\s*</url>",
        sitemap,
        re.DOTALL,
    )
    if not policy_entry:
        errors.append("The security policy sitemap entry must include a YYYY-MM-DD lastmod value.")

    html = SECURITY_PAGE.read_text(encoding="utf-8")
    parser = PolicyParser()
    parser.feed(html)

    if parser.lang != "en":
        errors.append(f"security.html language must be 'en', found {parser.lang!r}.")
    if parser.h1_count != 1:
        errors.append(f"security.html must contain exactly one h1, found {parser.h1_count}.")
    if parser.canonical != POLICY_URL:
        errors.append(f"security.html canonical must be {POLICY_URL!r}, found {parser.canonical!r}.")
    if not parser.robots or "noindex" in parser.robots.lower():
        errors.append("security.html must remain indexable public guidance.")
    if parser.security_identity != WARDVEIL_IDENTITY:
        errors.append(
            f"security.html must declare the canonical Wardveil identity metadata {WARDVEIL_IDENTITY!r}, found {parser.security_identity!r}."
        )

    for identifier, count in sorted(parser.id_counts.items()):
        if count > 1:
            errors.append(f"Duplicate id in security.html: {identifier}")
    if parser.inline_scripts:
        errors.append("security.html must not contain inline script blocks.")
    if parser.inline_styles:
        errors.append("security.html must not contain inline style blocks.")
    for handler in parser.inline_handlers:
        errors.append(f"security.html must not contain inline event handlers: {handler}")
    for image in parser.missing_alt:
        errors.append(f"Image in security.html must include alt text, even when decorative: {image}")
    for reference in parser.insecure_refs:
        errors.append(f"security.html external web references must use explicit HTTPS: {reference}")
    for reference in parser.external_refs:
        errors.append(f"security.html uses an unsupported external scheme: {reference}")

    for reference in sorted(parser.local_refs):
        target = (ROOT / reference).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"security.html local reference escapes repository root: {reference}")
            continue
        if not target.exists():
            errors.append(f"security.html references missing local resource: {reference}")

    for marker in REQUIRED_COPY:
        if marker.casefold() not in html.casefold():
            errors.append(f"security.html required reporting guidance is missing: {marker}")

    repository_policy = SECURITY_MD.read_text(encoding="utf-8")
    for marker in REQUIRED_REPOSITORY_POLICY_COPY:
        if marker.casefold() not in repository_policy.casefold():
            errors.append(f"SECURITY.md required reporting guidance is missing: {marker}")

    for stale in STALE_WARDVEIL_COPY:
        if stale.casefold() in html.casefold() or stale.casefold() in repository_policy.casefold():
            errors.append(f"Superseded Wardveil reporting model remains published: {stale}")

    for path in (SECURITY_TXT, SECURITY_PAGE, SECURITY_MD):
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


def report(errors: list[str]) -> int:
    if errors:
        print("Security reporting validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Security reporting validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
