#!/usr/bin/env python3
"""Validate the complete deployable public HTML surface as one linked static site.

The source repository contains deterministic HTML composition anchors. This validator
uses the same reviewed render boundary as the public build before crawling links,
assets, fragments, metadata, sitemap entries, and crawler policy. That keeps source
validation aligned with the bytes that can actually enter the deployment artifact.
"""

from __future__ import annotations

from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree
import sys

from glaze_ui_2 import apply_glaze_ui_2
from normalize_homepage import normalize_homepage
from render_repository_portfolio import load_manifest, render_public_file

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = (
    ROOT / "index.html",
    ROOT / "privacy.html",
    ROOT / "repositories.html",
    ROOT / "security.html",
    ROOT / "404.html",
)
INDEXABLE_PAGES = {
    ROOT / "index.html": "https://www.goreecloud.com/",
    ROOT / "privacy.html": "https://www.goreecloud.com/privacy.html",
    ROOT / "repositories.html": "https://www.goreecloud.com/repositories.html",
    ROOT / "security.html": "https://www.goreecloud.com/security.html",
}
SITEMAP = ROOT / "sitemap.xml"
ROBOTS = ROOT / "robots.txt"
CANONICAL_SITEMAP_URL = "https://www.goreecloud.com/sitemap.xml"
SOCIAL_IMAGE_URL = "https://www.goreecloud.com/assets/social-preview.png"
SITEMAP_NAMESPACE = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class PublicPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: Counter[str] = Counter()
        self.references: list[tuple[str, str, str]] = []
        self.canonical: str | None = None
        self.robots: str | None = None
        self.meta_names: dict[str, str] = {}
        self.meta_properties: dict[str, str] = {}
        self.manifest_href: str | None = None
        self.icon_links: list[tuple[set[str], str, str]] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        if attrs.get("id"):
            self.ids[attrs["id"]] += 1

        if tag == "link":
            rels = set(attrs.get("rel", "").lower().split())
            if "canonical" in rels:
                self.canonical = attrs.get("href")
            if "manifest" in rels:
                self.manifest_href = attrs.get("href")
            if rels.intersection({"icon", "apple-touch-icon"}):
                self.icon_links.append((rels, attrs.get("href", ""), attrs.get("type", "")))
        if tag == "meta":
            name = attrs.get("name", "").lower()
            prop = attrs.get("property", "").lower()
            if name:
                self.meta_names[name] = attrs.get("content", "")
            if prop:
                self.meta_properties[prop] = attrs.get("content", "")
            if name == "robots":
                self.robots = attrs.get("content")

        for attr_name in ("href", "src"):
            value = attrs.get(attr_name)
            if value:
                self.references.append((tag, attr_name, value))


def report(errors: list[str]) -> int:
    if errors:
        print("Public surface validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Rendered public surface validation passed.")
    return 0


def render_page(page: Path, manifest: dict) -> str:
    relative = str(page.relative_to(ROOT))
    rendered = render_public_file(relative, page.read_text(encoding="utf-8"), manifest)
    if relative == "index.html":
        rendered = normalize_homepage(rendered)
    return apply_glaze_ui_2(rendered)


def target_for_local_reference(source: Path, path_text: str) -> Path:
    decoded = unquote(path_text)
    if decoded in {"", "/"}:
        return ROOT / "index.html"

    if decoded.startswith("/"):
        relative = decoded.lstrip("/")
    else:
        relative = str((source.parent.relative_to(ROOT) / decoded))

    candidate = (ROOT / relative).resolve()
    candidate.relative_to(ROOT.resolve())

    if decoded.endswith("/"):
        candidate = candidate / "index.html"
    return candidate


def parse_pages(errors: list[str]) -> dict[Path, PublicPageParser]:
    parsed_pages: dict[Path, PublicPageParser] = {}
    try:
        manifest = load_manifest(ROOT)
    except (OSError, ValueError) as exc:
        errors.append(f"Cannot load reviewed repository manifest for public-surface rendering: {exc}")
        return parsed_pages

    for page in PUBLIC_PAGES:
        if not page.exists():
            errors.append(f"Required public page is missing: {page.relative_to(ROOT)}")
            continue
        try:
            html = render_page(page, manifest)
        except (OSError, ValueError, KeyError) as exc:
            errors.append(f"Could not render {page.relative_to(ROOT)} for public-surface validation: {exc}")
            continue

        parser = PublicPageParser()
        parser.feed(html)
        parsed_pages[page.resolve()] = parser

        for identifier, count in sorted(parser.ids.items()):
            if count > 1:
                errors.append(f"Duplicate id in rendered {page.relative_to(ROOT)}: {identifier}")
    return parsed_pages


def validate_references(errors: list[str], parsed_pages: dict[Path, PublicPageParser]) -> None:
    for page, parser in parsed_pages.items():
        display_page = page.relative_to(ROOT)
        for tag, attr_name, raw_value in parser.references:
            value = raw_value.strip()
            if not value:
                continue

            if value.startswith("#"):
                fragment = unquote(value[1:])
                if fragment and fragment not in parser.ids:
                    errors.append(
                        f"Rendered {display_page} {tag}[{attr_name}] references missing fragment #{fragment}."
                    )
                continue

            parsed = urlparse(value)
            if parsed.scheme or parsed.netloc or value.startswith("//"):
                continue

            try:
                target = target_for_local_reference(page, parsed.path)
            except ValueError:
                errors.append(
                    f"Rendered {display_page} {tag}[{attr_name}] escapes repository root: {value}"
                )
                continue

            if not target.exists():
                errors.append(
                    f"Rendered {display_page} {tag}[{attr_name}] references missing local resource: {value}"
                )
                continue

            if parsed.fragment:
                target_parser = parsed_pages.get(target.resolve())
                if target_parser is None and target.suffix.lower() == ".html":
                    errors.append(
                        f"Rendered {display_page} links to HTML outside the declared public surface: {value}"
                    )
                    continue
                fragment = unquote(parsed.fragment)
                if target_parser is not None and fragment not in target_parser.ids:
                    errors.append(
                        f"Rendered {display_page} links to missing fragment #{fragment} in {target.relative_to(ROOT)}."
                    )


def validate_indexing(errors: list[str], parsed_pages: dict[Path, PublicPageParser]) -> None:
    for page, expected_canonical in INDEXABLE_PAGES.items():
        parser = parsed_pages.get(page.resolve())
        if parser is None:
            continue
        if parser.canonical != expected_canonical:
            errors.append(
                f"{page.relative_to(ROOT)} canonical must be {expected_canonical!r}, found {parser.canonical!r}."
            )
        if parser.robots and "noindex" in parser.robots.lower():
            errors.append(f"Indexable public page is marked noindex: {page.relative_to(ROOT)}")

    error_parser = parsed_pages.get((ROOT / "404.html").resolve())
    if error_parser is not None:
        if not error_parser.robots or "noindex" not in error_parser.robots.lower():
            errors.append("404.html must remain noindex.")
        if error_parser.canonical:
            errors.append("404.html must not publish a canonical URL for a missing resource.")


def validate_page_metadata(errors: list[str], parsed_pages: dict[Path, PublicPageParser]) -> None:
    for page in PUBLIC_PAGES:
        parser = parsed_pages.get(page.resolve())
        if parser is None:
            continue
        display = page.relative_to(ROOT)
        manifest_href = (parser.manifest_href or "").lstrip("/")
        if manifest_href != "site.webmanifest":
            errors.append(f"{display} must link to the local site.webmanifest.")
        normalized_icons = {
            (frozenset(rels), href.lstrip("/"), content_type)
            for rels, href, content_type in parser.icon_links
        }
        if not any(
            "icon" in rels
            and href == "assets/goreecloud-logo.svg"
            and content_type == "image/svg+xml"
            for rels, href, content_type in normalized_icons
        ):
            errors.append(f"{display} must publish the canonical GoreeCloud SVG favicon.")
        if not any(
            "apple-touch-icon" in rels and href == "assets/goreecloud-logo.svg"
            for rels, href, _ in normalized_icons
        ):
            errors.append(f"{display} must publish the canonical GoreeCloud SVG Apple-touch identity.")

    for page, canonical in INDEXABLE_PAGES.items():
        if page.name not in {"index.html", "repositories.html"}:
            continue
        parser = parsed_pages.get(page.resolve())
        if parser is None:
            continue
        display = page.relative_to(ROOT)
        expected_properties = {
            "og:type": "website",
            "og:site_name": "GoreeCloud",
            "og:url": canonical,
            "og:image": SOCIAL_IMAGE_URL,
        }
        for key, expected in expected_properties.items():
            if parser.meta_properties.get(key) != expected:
                errors.append(f"{display} metadata {key} must be {expected!r}.")
        for key in ("og:title", "og:description", "og:image:alt"):
            if not parser.meta_properties.get(key, "").strip():
                errors.append(f"{display} must publish non-empty {key} metadata.")
        expected_names = {
            "twitter:card": "summary_large_image",
            "twitter:image": SOCIAL_IMAGE_URL,
        }
        for key, expected in expected_names.items():
            if parser.meta_names.get(key) != expected:
                errors.append(f"{display} metadata {key} must be {expected!r}.")
        for key in ("twitter:title", "twitter:description", "twitter:image:alt"):
            if not parser.meta_names.get(key, "").strip():
                errors.append(f"{display} must publish non-empty {key} metadata.")


def validate_sitemap(errors: list[str]) -> None:
    if not SITEMAP.exists():
        errors.append("sitemap.xml is missing.")
        return

    try:
        root = ElementTree.fromstring(SITEMAP.read_text(encoding="utf-8"))
    except ElementTree.ParseError as exc:
        errors.append(f"sitemap.xml is not valid XML: {exc}")
        return

    if root.tag != f"{SITEMAP_NAMESPACE}urlset":
        errors.append("sitemap.xml must use the standard sitemaps.org urlset namespace.")
        return

    locations: list[str] = []
    today = date.today()
    for url_node in root.findall(f"{SITEMAP_NAMESPACE}url"):
        loc_nodes = url_node.findall(f"{SITEMAP_NAMESPACE}loc")
        lastmod_nodes = url_node.findall(f"{SITEMAP_NAMESPACE}lastmod")

        if len(loc_nodes) != 1:
            errors.append(f"Each sitemap URL entry must contain exactly one <loc>; found {len(loc_nodes)}.")
            continue
        location = (loc_nodes[0].text or "").strip()
        if not location:
            errors.append("sitemap.xml contains an empty <loc> value.")
            continue
        locations.append(location)

        if len(lastmod_nodes) != 1:
            errors.append(
                f"Sitemap entry {location} must contain exactly one <lastmod>; found {len(lastmod_nodes)}."
            )
            continue

        lastmod_text = (lastmod_nodes[0].text or "").strip()
        try:
            lastmod = date.fromisoformat(lastmod_text)
        except ValueError:
            errors.append(f"Sitemap entry {location} has invalid YYYY-MM-DD lastmod: {lastmod_text!r}.")
            continue
        if lastmod > today:
            errors.append(f"Sitemap entry {location} has a future lastmod date: {lastmod_text}.")

    expected = list(INDEXABLE_PAGES.values())

    duplicates = sorted(url for url, count in Counter(locations).items() if count > 1)
    for url in duplicates:
        errors.append(f"Duplicate sitemap URL: {url}")

    missing = sorted(set(expected).difference(locations))
    extra = sorted(set(locations).difference(expected))
    for url in missing:
        errors.append(f"Indexable public page is missing from sitemap.xml: {url}")
    for url in extra:
        errors.append(f"sitemap.xml contains an unexpected public URL: {url}")


def validate_robots(errors: list[str]) -> None:
    if not ROBOTS.exists():
        errors.append("robots.txt is missing.")
        return

    directives = [
        line.strip()
        for line in ROBOTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    lowered = [line.lower() for line in directives]

    if lowered.count("user-agent: *") != 1:
        errors.append("robots.txt must contain exactly one global 'User-agent: *' directive.")
    if lowered.count("allow: /") != 1:
        errors.append("robots.txt must explicitly allow the public site root exactly once.")
    if any(line.startswith("disallow:") for line in lowered):
        errors.append("robots.txt must not accidentally block the intentionally public website with Disallow directives.")

    sitemap_directives = [line for line in directives if line.lower().startswith("sitemap:")]
    expected = f"Sitemap: {CANONICAL_SITEMAP_URL}"
    if sitemap_directives != [expected]:
        errors.append(
            f"robots.txt must publish exactly the canonical sitemap directive {expected!r}; found {sitemap_directives!r}."
        )


def main() -> int:
    errors: list[str] = []
    parsed_pages = parse_pages(errors)
    validate_references(errors, parsed_pages)
    validate_indexing(errors, parsed_pages)
    validate_page_metadata(errors, parsed_pages)
    validate_sitemap(errors)
    validate_robots(errors)
    return report(errors)


if __name__ == "__main__":
    sys.exit(main())
