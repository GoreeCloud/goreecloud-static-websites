#!/usr/bin/env python3
"""Validate GoreeCloud public-site failure resilience and critical-resource hints.

This validator intentionally uses only the Python standard library so it can run in
GitHub Actions without adding dependencies to the static website.
"""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ERROR_PAGE = ROOT / "404.html"
ERROR_STYLES = ROOT / "css" / "error.css"
HEADERS = ROOT / "_headers"
REQUIRED_STYLESHEETS = {
    "/css/style.css",
    "/css/glaze.css",
    "/css/glaze-polish.css",
    "/css/error.css",
}
REQUIRED_SCRIPTS = {"/js/theme-init.js"}
EARLY_HINT = "Link: </css/style.css>; rel=preload; as=style, </css/glaze.css>; rel=preload; as=style"
PRIVATE_PATTERNS = (
    re.compile(r"\b10(?:\.\d{1,3}){3}\b"),
    re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2}\b"),
)
SENSITIVE_TERMS = ("goreecloud-vps-01", ".netbird.selfhosted")
REQUIRED_STATIC_HEADERS = (
    "form-action 'none'",
    "connect-src 'none'",
    "media-src 'none'",
    "worker-src 'none'",
    "X-DNS-Prefetch-Control: off",
)


class ErrorPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang: str | None = None
        self.robots: str | None = None
        self.id_counts: Counter[str] = Counter()
        self.fragment_refs: set[str] = set()
        self.local_refs: set[str] = set()
        self.stylesheet_sources: set[str] = set()
        self.script_sources: set[str] = set()
        self.missing_alt_images: list[str] = []
        self.insecure_external_refs: list[str] = []
        self.external_blank_errors: list[str] = []
        self.inline_script_count = 0
        self.inline_style_count = 0
        self.inline_event_handlers: list[str] = []
        self.h1_count = 0
        self.section_label_targets: list[str] = []
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
        if tag == "section" and attrs.get("aria-labelledby"):
            self.section_label_targets.append(attrs["aria-labelledby"])
        if tag == "meta" and attrs.get("name") == "robots":
            self.robots = attrs.get("content")

        if tag == "script":
            if attrs.get("src"):
                self.script_sources.add(attrs["src"])
            else:
                self.inline_script_count += 1
        if tag == "style":
            self.inline_style_count += 1
        if tag == "link" and "stylesheet" in attrs.get("rel", "").split() and attrs.get("href"):
            self.stylesheet_sources.add(attrs["href"])
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


def validate_error_page(errors: list[str]) -> None:
    if not ERROR_PAGE.exists():
        fail(errors, "Custom Cloudflare Pages not-found document is missing: 404.html")
        return
    if not ERROR_STYLES.exists():
        fail(errors, "Custom not-found stylesheet is missing: css/error.css")
        return

    html = ERROR_PAGE.read_text(encoding="utf-8")
    parser = ErrorPageParser()
    parser.feed(html)

    if parser.html_lang != "en":
        fail(errors, f"404.html root language must be 'en', found {parser.html_lang!r}.")
    if not parser.title:
        fail(errors, "404.html must include a non-empty document title.")
    if parser.robots != "noindex,follow":
        fail(errors, f"404.html robots metadata must be 'noindex,follow', found {parser.robots!r}.")
    if parser.h1_count != 1:
        fail(errors, f"404.html must contain exactly one h1, found {parser.h1_count}.")
    if "main" not in parser.ids:
        fail(errors, "404.html must expose the main content landmark with id='main'.")
    if "main" not in parser.fragment_refs:
        fail(errors, "404.html must include a skip link targeting #main.")

    duplicate_ids = sorted(identifier for identifier, count in parser.id_counts.items() if count > 1)
    for identifier in duplicate_ids:
        fail(errors, f"Duplicate id found in 404.html: {identifier}")

    missing_fragments = sorted(ref for ref in parser.fragment_refs if ref and ref not in parser.ids)
    for fragment in missing_fragments:
        fail(errors, f"404.html references a missing in-page target: #{fragment}")

    for target in parser.section_label_targets:
        if target not in parser.ids:
            fail(errors, f"404.html section aria-labelledby target does not exist: {target}")

    for reference in sorted(parser.local_refs):
        if reference in {"", "/"}:
            continue
        if not reference.startswith("/"):
            fail(
                errors,
                "404.html local references must be origin-rooted so nested missing URLs render correctly: "
                f"{reference}",
            )
        relative = reference.lstrip("/")
        target = (ROOT / relative).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            fail(errors, f"404.html local reference escapes repository root: {reference}")
            continue
        if not target.exists():
            fail(errors, f"404.html references a missing local resource: {reference}")

    for reference in parser.insecure_external_refs:
        fail(errors, f"404.html external web references must use explicit HTTPS: {reference}")
    for href in parser.external_blank_errors:
        fail(errors, f'404.html target="_blank" link must include rel="noopener noreferrer": {href}')
    for image in parser.missing_alt_images:
        fail(errors, f"404.html image must include an alt attribute: {image}")
    if parser.inline_script_count:
        fail(errors, "404.html must not contain inline script blocks.")
    if parser.inline_style_count:
        fail(errors, "404.html must not contain inline style blocks.")
    for handler in parser.inline_event_handlers:
        fail(errors, f"404.html must not contain inline event handlers: {handler}")

    missing_stylesheets = sorted(REQUIRED_STYLESHEETS.difference(parser.stylesheet_sources))
    for stylesheet in missing_stylesheets:
        fail(errors, f"404.html must directly load required stylesheet: {stylesheet}")
    missing_scripts = sorted(REQUIRED_SCRIPTS.difference(parser.script_sources))
    for script in missing_scripts:
        fail(errors, f"404.html must load the early appearance initializer: {script}")
    if "/js/main.js" in parser.script_sources:
        fail(errors, "404.html should remain independently usable without the main interaction script.")

    combined_public_text = html + "\n" + ERROR_STYLES.read_text(encoding="utf-8", errors="replace")
    for pattern in PRIVATE_PATTERNS:
        match = pattern.search(combined_public_text)
        if match:
            fail(errors, f"Private-range IP address found in public error-page resources: {match.group(0)}")
    lower_text = combined_public_text.lower()
    for term in SENSITIVE_TERMS:
        if term.lower() in lower_text:
            fail(errors, f"Private infrastructure identifier found in public error-page resources: {term}")

    css = ERROR_STYLES.read_text(encoding="utf-8", errors="replace")
    if css.count("{") != css.count("}"):
        fail(errors, "Unbalanced CSS braces in css/error.css.")


def validate_headers(errors: list[str]) -> None:
    if not HEADERS.exists():
        fail(errors, "Cloudflare Pages _headers file is missing.")
        return

    headers = HEADERS.read_text(encoding="utf-8")
    root_rule = f"/\n  {EARLY_HINT}"
    if root_rule not in headers:
        fail(errors, "Homepage must declare critical local styles through a root Link preload rule for Cloudflare Pages Early Hints.")

    for marker in REQUIRED_STATIC_HEADERS:
        if marker not in headers:
            fail(errors, f"Static-site security hardening is missing from _headers: {marker}")

    if "Access-Control-Allow-Origin: *" in headers:
        fail(errors, "The public static site must not introduce blanket cross-origin resource access.")


def validate() -> list[str]:
    errors: list[str] = []
    validate_error_page(errors)
    validate_headers(errors)
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Website resilience validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Website resilience validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
