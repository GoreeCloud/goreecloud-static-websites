#!/usr/bin/env python3
"""Validate Main's current public content, security, and evidence boundaries."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import re

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "repositories.html", "privacy.html", "security.html", "404.html")
CANONICALS = {
    "index.html": "https://www.goreecloud.com/",
    "repositories.html": "https://www.goreecloud.com/repositories.html",
    "privacy.html": "https://www.goreecloud.com/privacy.html",
    "security.html": "https://www.goreecloud.com/security.html",
}
PRIVATE_PATTERNS = (
    re.compile(r"\b10(?:\.\d{1,3}){3}\b"),
    re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2}\b"),
)


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: Counter[str] = Counter()
        self.refs: list[tuple[str, str]] = []
        self.canonical: str | None = None
        self.robots: str | None = None
        self.h1 = 0
        self.inline_script = 0
        self.inline_style = 0
        self.inline_handlers: list[str] = []
        self.blank_link_errors: list[str] = []
        self.images_without_alt: list[str] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        if attrs.get("id"):
            self.ids[attrs["id"]] += 1
        if tag == "h1":
            self.h1 += 1
        if tag == "link" and "canonical" in attrs.get("rel", "").split():
            self.canonical = attrs.get("href")
        if tag == "meta" and attrs.get("name", "").lower() == "robots":
            self.robots = attrs.get("content")
        if tag == "script" and not attrs.get("src"):
            self.inline_script += 1
        if tag == "style":
            self.inline_style += 1
        if tag == "img" and "alt" not in attrs:
            self.images_without_alt.append(attrs.get("src", "(missing src)"))
        for key in attrs:
            if key.lower().startswith("on"):
                self.inline_handlers.append(f"<{tag} {key}=...>")
        if attrs.get("target") == "_blank":
            rel = set(attrs.get("rel", "").split())
            if not {"noopener", "noreferrer"}.issubset(rel):
                self.blank_link_errors.append(attrs.get("href", "(missing href)"))
        for key in ("href", "src"):
            if attrs.get(key):
                self.refs.append((key, attrs[key]))


def main() -> int:
    errors: list[str] = []
    parsed: dict[str, Parser] = {}

    for name in PAGES:
        path = ROOT / name
        if not path.is_file():
            errors.append(f"missing public page: {name}")
            continue
        text = path.read_text(encoding="utf-8")
        parser = Parser()
        parser.feed(text)
        parsed[name] = parser
        if parser.h1 != 1:
            errors.append(f"{name} must contain exactly one h1; found {parser.h1}")
        for identifier, count in parser.ids.items():
            if count > 1:
                errors.append(f"{name} contains duplicate id: {identifier}")
        if parser.inline_script or parser.inline_style or parser.inline_handlers:
            errors.append(f"{name} violates self-only CSP with inline executable/style content")
        for image in parser.images_without_alt:
            errors.append(f"{name} image missing alt attribute: {image}")
        for href in parser.blank_link_errors:
            errors.append(f"{name} target=_blank link lacks noopener noreferrer: {href}")
        for _, value in parser.refs:
            parsed_url = urlparse(value)
            if parsed_url.scheme == "http" or value.startswith("//"):
                errors.append(f"{name} contains insecure external reference: {value}")
            if parsed_url.scheme in {"https", "mailto"} or value.startswith("#"):
                continue
            local = parsed_url.path.lstrip("/")
            if not local:
                continue
            if local.startswith("assets/glaze-v1/"):
                continue
            candidate = ROOT / local
            if not candidate.exists():
                errors.append(f"{name} references missing local resource: {value}")

    for name, canonical in CANONICALS.items():
        parser = parsed.get(name)
        if parser and parser.canonical != canonical:
            errors.append(f"{name} canonical must be {canonical}; found {parser.canonical!r}")
        if parser and parser.robots and "noindex" in parser.robots.lower():
            errors.append(f"indexable page is marked noindex: {name}")
    error_page = parsed.get("404.html")
    if error_page and (not error_page.robots or "noindex" not in error_page.robots.lower()):
        errors.append("404.html must remain noindex")
    if error_page and error_page.canonical:
        errors.append("404.html must not publish a canonical URL")

    homepage = (ROOT / "index.html").read_text(encoding="utf-8")
    repositories = (ROOT / "repositories.html").read_text(encoding="utf-8")
    for marker in (
        "GoreeCloud Manager", "Glaze UI", "Privacy Shield", "Wardveil Security",
        "Everkeep", "GoreeCloud Mesh", "GoreeCloud Identity",
    ):
        if marker not in homepage:
            errors.append(f"homepage missing Integral Platform System: {marker}")
    for marker in (
        "GoreeCloud Home Security", "GoreeCloud Home", "GoreeCloud AI",
        "GoreeCloud Containers", "GoreeCloud Code", "GoreeCloud Boot",
        "https://github.com/GoreeCloud/goreecloud-boot",
    ):
        if marker not in repositories:
            errors.append(f"repositories page missing six-product focus marker: {marker}")
    for stale in (
        "Five active product lines", "five active product lines", "identity.goreecloud.com",
        "Glaze UI 2.1.0 is the current Stable", "Glaze UI 2.2.0 is the current Stable",
    ):
        if stale in homepage or stale in repositories:
            errors.append(f"superseded current-state wording remains public: {stale}")
    if re.search(r"\b\d+\s+(?:current\s+)?repositories\b", homepage, re.I):
        errors.append("homepage must not publish a hard-coded organization repository count")

    headers = (ROOT / "_headers").read_text(encoding="utf-8")
    for marker in (
        "Content-Security-Policy:", "frame-ancestors 'none'", "Permissions-Policy:",
        "Referrer-Policy: no-referrer", "X-Content-Type-Options: nosniff",
        "Strict-Transport-Security: max-age=31536000",
    ):
        if marker not in headers:
            errors.append(f"required public security header missing: {marker}")

    security = ROOT / ".well-known" / "security.txt"
    if not security.is_file():
        errors.append("missing .well-known/security.txt")
    else:
        fields: dict[str, str] = {}
        for line in security.read_text(encoding="utf-8").splitlines():
            if ":" in line and not line.lstrip().startswith("#"):
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip()
        expected = {
            "Contact": "mailto:security@goreecloud.com",
            "Preferred-Languages": "en",
            "Canonical": "https://www.goreecloud.com/.well-known/security.txt",
        }
        for key, value in expected.items():
            if fields.get(key) != value:
                errors.append(f"security.txt {key} must be {value!r}")
        try:
            expires = datetime.fromisoformat(fields.get("Expires", "").replace("Z", "+00:00"))
            if expires <= datetime.now(timezone.utc):
                errors.append("security.txt Expires is not in the future")
        except ValueError:
            errors.append("security.txt Expires must be valid ISO 8601")

    audited = [ROOT / name for name in PAGES] + [ROOT / "css/site-v1.1.css", ROOT / "js/main.js", ROOT / "js/theme-init.js", ROOT / "_headers"]
    for path in audited:
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in PRIVATE_PATTERNS:
            match = pattern.search(text)
            if match:
                errors.append(f"private-range IP found in {path.relative_to(ROOT)}: {match.group(0)}")
        for forbidden in ("google-analytics", "googletagmanager", "segment.com", "fonts.googleapis.com", "raw.githubusercontent.com"):
            if forbidden in text.lower():
                errors.append(f"forbidden browser/public dependency in {path.relative_to(ROOT)}: {forbidden}")

    if errors:
        print("Main website validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Main public content, security, six-product focus, seven-system model, and source truth boundaries validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
