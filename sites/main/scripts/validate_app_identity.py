#!/usr/bin/env python3
"""Validate GoreeCloud browser application identity and manifest integration."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "site.webmanifest"
THEME_INIT = ROOT / "js" / "theme-init.js"
HEADERS = ROOT / "_headers"
PUBLIC_PAGES = (
    ROOT / "index.html",
    ROOT / "repositories.html",
    ROOT / "privacy.html",
    ROOT / "security.html",
    ROOT / "404.html",
)
EXPECTED_THEME = "#07111f"
CANONICAL_LOGO = "/assets/goreecloud-logo.svg"


class IdentityParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta_names: dict[str, str] = {}
        self.links: list[dict[str, str]] = []
        self.scripts: list[str] = []
        self.main_attrs: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        if tag == "meta" and attrs.get("name"):
            self.meta_names[attrs["name"]] = attrs.get("content", "")
        elif tag == "link":
            self.links.append(attrs)
        elif tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])
        elif tag == "main" and attrs.get("id") == "main":
            self.main_attrs = attrs


def main() -> int:
    errors: list[str] = []

    for path in (MANIFEST, THEME_INIT, HEADERS, *PUBLIC_PAGES):
        if not path.exists():
            errors.append(f"Required application-identity resource is missing: {path.relative_to(ROOT)}")
    if errors:
        return report(errors)

    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"site.webmanifest is not valid JSON: {exc}")
        return report(errors)

    expected = {
        "id": "/",
        "name": "GoreeCloud",
        "short_name": "GoreeCloud",
        "lang": "en",
        "dir": "ltr",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "theme_color": EXPECTED_THEME,
        "background_color": EXPECTED_THEME,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            errors.append(f"site.webmanifest {key!r} must be {value!r}, found {manifest.get(key)!r}.")

    description = manifest.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("site.webmanifest must include a non-empty description.")

    icons = manifest.get("icons")
    if not isinstance(icons, list) or not icons:
        errors.append("site.webmanifest must contain the canonical GoreeCloud SVG identity icon.")
        icons = []

    icon_by_src = {
        icon.get("src"): icon
        for icon in icons
        if isinstance(icon, dict) and isinstance(icon.get("src"), str)
    }
    svg_icon = icon_by_src.get(CANONICAL_LOGO)
    if not svg_icon:
        errors.append(f"site.webmanifest must include {CANONICAL_LOGO}.")
    else:
        if svg_icon.get("sizes") != "any":
            errors.append("The scalable manifest SVG icon must use sizes='any'.")
        if svg_icon.get("type") != "image/svg+xml":
            errors.append("The scalable manifest SVG icon must use type='image/svg+xml'.")
        if svg_icon.get("purpose") != "any":
            errors.append("The scalable manifest SVG icon must use purpose='any'.")

    if set(icon_by_src) != {CANONICAL_LOGO}:
        errors.append(
            "site.webmanifest identity icon set must use only the canonical GoreeCloud SVG; "
            f"found {sorted(icon_by_src)!r}."
        )

    for src in icon_by_src:
        parsed = urlparse(src)
        if parsed.scheme or parsed.netloc:
            errors.append(f"Manifest icon must remain same-origin: {src}")
            continue
        target = ROOT / parsed.path.lstrip("/")
        if not target.exists():
            errors.append(f"Manifest icon resource is missing: {src}")

    theme_init = THEME_INIT.read_text(encoding="utf-8")
    required_manifest_markers = (
        "const MANIFEST_HREF = '/site.webmanifest';",
        "document.querySelector('link[rel~=\"manifest\"]')",
        "document.createElement('link')",
        "manifest.rel = 'manifest';",
        "manifest.href = MANIFEST_HREF;",
        "document.head.append(manifest);",
        "ensureManifestLink();",
    )
    for marker in required_manifest_markers:
        if marker not in theme_init:
            errors.append(f"theme-init.js is missing manifest discovery behavior: {marker}")

    if "serviceWorker" in theme_init or "navigator.serviceWorker" in theme_init:
        errors.append("Application identity initialization must not introduce a service worker implicitly.")

    headers = HEADERS.read_text(encoding="utf-8")
    if "manifest-src 'self'" not in headers:
        errors.append("The site CSP must keep manifest-src restricted to self.")

    for page in PUBLIC_PAGES:
        parser = IdentityParser()
        parser.feed(page.read_text(encoding="utf-8"))
        relative = page.relative_to(ROOT)
        is_error_page = page.name == "404.html"
        theme_init_src = "/js/theme-init.js" if is_error_page else "js/theme-init.js"
        apple_icon_href = CANONICAL_LOGO if is_error_page else CANONICAL_LOGO.lstrip("/")

        if parser.meta_names.get("application-name") != "GoreeCloud":
            errors.append(f"{relative} must publish application-name=GoreeCloud.")
        if parser.meta_names.get("author") != "GoreeCloud":
            errors.append(f"{relative} must publish author=GoreeCloud.")
        if theme_init_src not in parser.scripts:
            errors.append(f"{relative} must load {theme_init_src} for early theme and manifest discovery.")

        apple_icons = [
            link for link in parser.links
            if "apple-touch-icon" in link.get("rel", "").split()
        ]
        if not apple_icons or apple_icons[0].get("href") != apple_icon_href:
            errors.append(f"{relative} must publish the canonical GoreeCloud apple-touch-icon at {apple_icon_href}.")
        elif apple_icons[0].get("type") != "image/svg+xml":
            errors.append(f"{relative} canonical GoreeCloud apple-touch-icon must declare image/svg+xml.")

        if parser.main_attrs is None:
            errors.append(f"{relative} must contain <main id='main'>.")
        elif parser.main_attrs.get("tabindex") != "-1":
            errors.append(f"{relative} main skip-link target must use tabindex='-1'.")

    return report(errors)


def report(errors: list[str]) -> int:
    if errors:
        print("Application identity validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Application identity validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())