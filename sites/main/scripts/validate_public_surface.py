#!/usr/bin/env python3
"""Validate Main's complete source-native public HTML surface."""

from __future__ import annotations

from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree
import sys

from normalize_homepage import normalize_homepage
from render_repository_portfolio import load_manifest, render_public_file

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = tuple(ROOT / name for name in ("index.html", "privacy.html", "repositories.html", "security.html", "404.html"))
INDEXABLE = {
    "index.html": "https://www.goreecloud.com/",
    "privacy.html": "https://www.goreecloud.com/privacy.html",
    "repositories.html": "https://www.goreecloud.com/repositories.html",
    "security.html": "https://www.goreecloud.com/security.html",
}
SOCIAL_IMAGE = "https://www.goreecloud.com/assets/social-preview.png"


class Audit(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: Counter[str] = Counter()
        self.refs: list[tuple[str, str]] = []
        self.canonical: str | None = None
        self.robots: str = ""
        self.manifest: str = ""
        self.icons: list[tuple[str, str]] = []
        self.meta_name: dict[str, str] = {}
        self.meta_prop: dict[str, str] = {}
        self.inline_scripts = 0
        self.inline_styles = 0

    def handle_starttag(self, tag, attrs_list):
        attrs = {k: v or "" for k, v in attrs_list}
        if attrs.get("id"):
            self.ids[attrs["id"]] += 1
        if tag == "link":
            rel = set(attrs.get("rel", "").split())
            if "canonical" in rel:
                self.canonical = attrs.get("href")
            if "manifest" in rel:
                self.manifest = attrs.get("href", "")
            if "icon" in rel or "apple-touch-icon" in rel:
                self.icons.append((attrs.get("rel", ""), attrs.get("href", "")))
        if tag == "meta":
            if attrs.get("name"):
                self.meta_name[attrs["name"].lower()] = attrs.get("content", "")
            if attrs.get("property"):
                self.meta_prop[attrs["property"].lower()] = attrs.get("content", "")
            if attrs.get("name", "").lower() == "robots":
                self.robots = attrs.get("content", "")
        if tag == "script" and not attrs.get("src"):
            self.inline_scripts += 1
        if tag == "style":
            self.inline_styles += 1
        for key in ("href", "src"):
            value = attrs.get(key)
            if value:
                self.refs.append((tag, value))


def rendered(page: Path, manifest: dict) -> str:
    relative = str(page.relative_to(ROOT))
    text = render_public_file(relative, page.read_text(encoding="utf-8"), manifest)
    if relative == "index.html":
        text = normalize_homepage(text)
    return text


def local_target(source: Path, value: str) -> Path:
    parsed = urlparse(value)
    raw = unquote(parsed.path)
    if raw in {"", "/"}:
        return ROOT / "index.html"
    relative = raw.lstrip("/") if raw.startswith("/") else str(source.parent.relative_to(ROOT) / raw)
    target = (ROOT / relative).resolve()
    target.relative_to(ROOT.resolve())
    if raw.endswith("/"):
        target = target / "index.html"
    return target


def main() -> int:
    errors: list[str] = []
    try:
        manifest = load_manifest(ROOT)
    except (OSError, ValueError) as exc:
        print(f"Public surface validation failed: {exc}")
        return 1

    parsed: dict[Path, Audit] = {}
    for page in PUBLIC_PAGES:
        if not page.is_file():
            errors.append(f"missing public page: {page.name}")
            continue
        try:
            text = rendered(page, manifest)
        except (OSError, ValueError) as exc:
            errors.append(f"cannot render {page.name}: {exc}")
            continue
        audit = Audit(); audit.feed(text); parsed[page.resolve()] = audit
        for identifier, count in audit.ids.items():
            if count > 1:
                errors.append(f"duplicate id in {page.name}: {identifier}")
        if audit.inline_scripts or audit.inline_styles:
            errors.append(f"{page.name} contains inline script/style blocked by self-only CSP")
        if audit.manifest.lstrip("/") != "site.webmanifest":
            errors.append(f"{page.name} must link local site.webmanifest")
        if not any(href.lstrip("/") == "assets/goreecloud-logo.svg" for _, href in audit.icons):
            errors.append(f"{page.name} missing canonical GoreeCloud SVG identity")

        expected = INDEXABLE.get(page.name)
        if expected:
            if audit.canonical != expected:
                errors.append(f"{page.name} canonical mismatch: {audit.canonical!r}")
            if "noindex" in audit.robots.lower():
                errors.append(f"indexable page is noindex: {page.name}")
        else:
            if "noindex" not in audit.robots.lower():
                errors.append("404.html must remain noindex")
            if audit.canonical:
                errors.append("404.html must not publish a canonical URL")

        if page.name in {"index.html", "repositories.html"}:
            for key, expected_value in (("og:type", "website"), ("og:site_name", "GoreeCloud"), ("og:url", expected), ("og:image", SOCIAL_IMAGE)):
                if audit.meta_prop.get(key) != expected_value:
                    errors.append(f"{page.name} {key} metadata mismatch")
            for key, expected_value in (("twitter:card", "summary_large_image"), ("twitter:image", SOCIAL_IMAGE)):
                if audit.meta_name.get(key) != expected_value:
                    errors.append(f"{page.name} {key} metadata mismatch")

    for page_path, audit in parsed.items():
        page = Path(page_path)
        for tag, value in audit.refs:
            parsed_ref = urlparse(value)
            if parsed_ref.scheme or parsed_ref.netloc or value.startswith("//"):
                continue
            if value.startswith("#"):
                fragment = unquote(value[1:])
                if fragment and fragment not in audit.ids:
                    errors.append(f"{page.name} links to missing fragment #{fragment}")
                continue
            try:
                target = local_target(page, value)
            except ValueError:
                errors.append(f"{page.name} local reference escapes site root: {value}")
                continue
            if not target.exists():
                errors.append(f"{page.name} references missing local resource: {value}")
                continue
            if parsed_ref.fragment and target.suffix == ".html":
                target_audit = parsed.get(target.resolve())
                if target_audit is not None and unquote(parsed_ref.fragment) not in target_audit.ids:
                    errors.append(f"{page.name} links to missing fragment in {target.name}: {value}")

    sitemap = ROOT / "sitemap.xml"
    if not sitemap.is_file():
        errors.append("sitemap.xml is missing")
    else:
        try:
            xml = ElementTree.fromstring(sitemap.read_text(encoding="utf-8"))
            ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
            locations = []
            for node in xml.findall(f"{ns}url"):
                loc = node.find(f"{ns}loc"); lastmod = node.find(f"{ns}lastmod")
                if loc is None or not (loc.text or "").strip():
                    errors.append("sitemap contains empty URL")
                    continue
                locations.append((loc.text or "").strip())
                if lastmod is None:
                    errors.append(f"sitemap entry lacks lastmod: {locations[-1]}")
                else:
                    try:
                        if date.fromisoformat((lastmod.text or "").strip()) > date.today():
                            errors.append(f"sitemap future lastmod: {locations[-1]}")
                    except ValueError:
                        errors.append(f"sitemap invalid lastmod: {locations[-1]}")
            if set(locations) != set(INDEXABLE.values()):
                errors.append("sitemap URLs must exactly match the four indexable Main pages")
        except ElementTree.ParseError as exc:
            errors.append(f"invalid sitemap XML: {exc}")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8") if (ROOT / "robots.txt").is_file() else ""
    if "Sitemap: https://www.goreecloud.com/sitemap.xml" not in robots:
        errors.append("robots.txt canonical sitemap line missing")

    if errors:
        print("Public surface validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Source-native Main public surface validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
