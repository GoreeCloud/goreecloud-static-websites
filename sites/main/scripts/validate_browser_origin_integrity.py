#!/usr/bin/env python3
"""Enforce GoreeCloud's first-party, stateless browser-resource boundary.

The public website intentionally avoids third-party browser dependencies and runtime
network clients. External navigation links are allowed, but resources the browser
loads as part of rendering must stay local to the current origin so previews and
production behave the same way without leaking visitor requests to third parties.
"""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import sys

from build_public_site import PUBLIC_FILES, ROOT

HTML_FILES = tuple(ROOT / name for name in PUBLIC_FILES if name.endswith(".html"))
CSS_FILES = tuple(ROOT / name for name in PUBLIC_FILES if name.startswith("css/") and name.endswith(".css"))
JS_FILES = tuple(ROOT / name for name in PUBLIC_FILES if name.startswith("js/") and name.endswith(".js"))
MANIFEST = ROOT / "site.webmanifest"

RESOURCE_LINK_RELS = {
    "apple-touch-icon",
    "icon",
    "manifest",
    "modulepreload",
    "preload",
    "stylesheet",
}
NETWORK_JS_MARKERS = (
    "fetch(",
    "XMLHttpRequest",
    "WebSocket",
    "EventSource",
    "navigator.sendBeacon",
    "navigator.serviceWorker",
    "new Worker(",
    "new SharedWorker(",
    "importScripts(",
)
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
CSS_IMPORT_RE = re.compile(r"@import\s+(?:url\(\s*)?(['\"]?)([^'\"\s;)]+)\1", re.IGNORECASE)


def is_local_resource(value: str, *, allow_data: bool = True) -> bool:
    value = value.strip()
    if not value or value.startswith("#"):
        return True
    if allow_data and value.lower().startswith("data:"):
        return True
    if value.startswith("//"):
        return False
    parsed = urlparse(value)
    return not parsed.scheme and not parsed.netloc


def srcset_candidates(value: str) -> list[str]:
    candidates: list[str] = []
    for candidate in value.split(","):
        token = candidate.strip().split()[0] if candidate.strip() else ""
        if token:
            candidates.append(token)
    return candidates


class ResourceParser(HTMLParser):
    def __init__(self, source: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.source = source
        self.errors: list[str] = []

    def reject_external(self, tag: str, attr: str, value: str) -> None:
        if not is_local_resource(value):
            self.errors.append(
                f"{self.source.relative_to(ROOT)} browser resource must be local: <{tag}> {attr}={value!r}"
            )

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {name.lower(): value or "" for name, value in attrs_list}
        tag = tag.lower()

        if tag == "script" and attrs.get("src"):
            self.reject_external(tag, "src", attrs["src"])
        elif tag == "img":
            if attrs.get("src"):
                self.reject_external(tag, "src", attrs["src"])
            for candidate in srcset_candidates(attrs.get("srcset", "")):
                self.reject_external(tag, "srcset", candidate)
        elif tag == "source":
            if attrs.get("src"):
                self.reject_external(tag, "src", attrs["src"])
            for candidate in srcset_candidates(attrs.get("srcset", "")):
                self.reject_external(tag, "srcset", candidate)
        elif tag in {"audio", "video", "track", "iframe", "embed"} and attrs.get("src"):
            self.reject_external(tag, "src", attrs["src"])
        elif tag == "video" and attrs.get("poster"):
            self.reject_external(tag, "poster", attrs["poster"])
        elif tag == "object" and attrs.get("data"):
            self.reject_external(tag, "data", attrs["data"])
        elif tag == "input" and attrs.get("type", "").lower() == "image" and attrs.get("src"):
            self.reject_external(tag, "src", attrs["src"])
        elif tag == "link":
            rels = set(attrs.get("rel", "").lower().split())
            if rels.intersection(RESOURCE_LINK_RELS) and attrs.get("href"):
                self.reject_external(tag, "href", attrs["href"])

        if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
            self.errors.append(f"{self.source.relative_to(ROOT)} must not use meta refresh redirects.")


def validate_html(errors: list[str]) -> None:
    for path in HTML_FILES:
        parser = ResourceParser(path)
        parser.feed(path.read_text(encoding="utf-8"))
        errors.extend(parser.errors)


def validate_css(errors: list[str]) -> None:
    for path in CSS_FILES:
        text = path.read_text(encoding="utf-8", errors="replace")
        for _, value in CSS_URL_RE.findall(text):
            if not is_local_resource(value):
                errors.append(f"{path.relative_to(ROOT)} CSS url() must be local or data: {value}")
        for _, value in CSS_IMPORT_RE.findall(text):
            if not is_local_resource(value, allow_data=False):
                errors.append(f"{path.relative_to(ROOT)} CSS @import must be local: {value}")


def validate_js(errors: list[str]) -> None:
    for path in JS_FILES:
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in NETWORK_JS_MARKERS:
            if marker in text:
                errors.append(
                    f"{path.relative_to(ROOT)} contains runtime network/browser-service capability forbidden by the static privacy boundary: {marker}"
                )
        if "document.cookie" in text:
            errors.append(f"{path.relative_to(ROOT)} must not read or write document.cookie.")


def validate_manifest(errors: list[str]) -> None:
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"site.webmanifest is not valid readable JSON: {exc}")
        return

    for field in ("id", "start_url", "scope"):
        value = manifest.get(field)
        if not isinstance(value, str) or not is_local_resource(value, allow_data=False):
            errors.append(f"site.webmanifest {field} must remain origin-local, found {value!r}.")

    icons = manifest.get("icons", [])
    if not isinstance(icons, list) or not icons:
        errors.append("site.webmanifest must contain local application icons.")
    else:
        for index, icon in enumerate(icons):
            src = icon.get("src") if isinstance(icon, dict) else None
            if not isinstance(src, str) or not is_local_resource(src):
                errors.append(f"site.webmanifest icon {index} must be local, found {src!r}.")


def main() -> int:
    errors: list[str] = []

    required_allowlisted_runtime = {
        "assets/goreecloud-logo.svg",
        "css/glaze.css",
        "css/glaze-polish.css",
        "js/theme-init.js",
        "js/main.js",
        "site.webmanifest",
    }
    missing = sorted(required_allowlisted_runtime.difference(PUBLIC_FILES))
    for path in missing:
        errors.append(f"Browser-origin validator requires public runtime file to remain explicitly allowlisted: {path}")

    validate_html(errors)
    validate_css(errors)
    validate_js(errors)
    validate_manifest(errors)

    if errors:
        print("Browser origin integrity validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Browser origin integrity validation passed: explicitly allowlisted render resources remain local and browser code remains stateless.")
    return 0


if __name__ == "__main__":
    sys.exit(main())