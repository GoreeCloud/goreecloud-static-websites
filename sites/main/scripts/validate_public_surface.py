#!/usr/bin/env python3
"""Validate Main's complete static HTML surface, local references, sitemap, and robots policy."""
from __future__ import annotations

from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
PAGES = tuple(ROOT / name for name in ("index.html", "repositories.html", "privacy.html", "security.html", "404.html"))
INDEXABLE = {
    "index.html": "https://www.goreecloud.com/",
    "repositories.html": "https://www.goreecloud.com/repositories.html",
    "privacy.html": "https://www.goreecloud.com/privacy.html",
    "security.html": "https://www.goreecloud.com/security.html",
}
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: Counter[str] = Counter()
        self.refs: list[str] = []
        self.canonical: str | None = None
        self.robots: str | None = None
        self.manifest: str | None = None
        self.icons: list[str] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        if attrs.get("id"):
            self.ids[attrs["id"]] += 1
        if tag == "link":
            rels = set(attrs.get("rel", "").split())
            if "canonical" in rels:
                self.canonical = attrs.get("href")
            if "manifest" in rels:
                self.manifest = attrs.get("href")
            if "icon" in rels:
                self.icons.append(attrs.get("href", ""))
        if tag == "meta" and attrs.get("name", "").lower() == "robots":
            self.robots = attrs.get("content")
        for key in ("href", "src"):
            if attrs.get(key):
                self.refs.append(attrs[key])


def local_target(source: Path, value: str) -> Path | None:
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc or value.startswith("//") or value.startswith("#"):
        return None
    path = unquote(parsed.path)
    if path in {"", "/"}:
        return ROOT / "index.html"
    relative = path.lstrip("/") if path.startswith("/") else str(source.parent.relative_to(ROOT) / path)
    candidate = (ROOT / relative).resolve()
    candidate.relative_to(ROOT.resolve())
    if path.endswith("/"):
        candidate = candidate / "index.html"
    return candidate


def main() -> int:
    errors: list[str] = []
    parsed: dict[Path, Parser] = {}
    for page in PAGES:
        if not page.is_file():
            errors.append(f"missing public page: {page.name}")
            continue
        parser = Parser()
        parser.feed(page.read_text(encoding="utf-8"))
        parsed[page.resolve()] = parser
        for identifier, count in parser.ids.items():
            if count > 1:
                errors.append(f"duplicate id in {page.name}: {identifier}")
        if (parser.manifest or "").lstrip("/") != "site.webmanifest":
            errors.append(f"{page.name} must link local site.webmanifest")
        if "assets/goreecloud-logo.svg" not in {icon.lstrip("/") for icon in parser.icons}:
            errors.append(f"{page.name} missing canonical GoreeCloud favicon")

    for name, canonical in INDEXABLE.items():
        parser = parsed.get((ROOT / name).resolve())
        if parser and parser.canonical != canonical:
            errors.append(f"{name} canonical mismatch: {parser.canonical!r}")
        if parser and parser.robots and "noindex" in parser.robots.lower():
            errors.append(f"indexable page is noindex: {name}")
    error_parser = parsed.get((ROOT / "404.html").resolve())
    if error_parser and (not error_parser.robots or "noindex" not in error_parser.robots.lower()):
        errors.append("404.html must remain noindex")

    for page, parser in parsed.items():
        for value in parser.refs:
            try:
                target = local_target(page, value)
            except ValueError:
                errors.append(f"{page.name} reference escapes site root: {value}")
                continue
            if target is None:
                continue
            rel = target.relative_to(ROOT)
            if str(rel).startswith("assets/glaze-v1/"):
                continue
            if not target.exists():
                errors.append(f"{page.name} references missing local resource: {value}")
                continue
            fragment = urlparse(value).fragment
            if fragment and target.suffix == ".html":
                target_parser = parsed.get(target.resolve())
                if target_parser and unquote(fragment) not in target_parser.ids:
                    errors.append(f"{page.name} links missing fragment #{fragment} in {rel}")

    sitemap = ROOT / "sitemap.xml"
    if not sitemap.is_file():
        errors.append("sitemap.xml is missing")
    else:
        try:
            root = ElementTree.fromstring(sitemap.read_text(encoding="utf-8"))
            locations: list[str] = []
            for node in root.findall(f"{NS}url"):
                loc = node.find(f"{NS}loc")
                lastmod = node.find(f"{NS}lastmod")
                if loc is None or not (loc.text or "").strip():
                    errors.append("sitemap entry missing loc")
                    continue
                locations.append((loc.text or "").strip())
                if lastmod is None:
                    errors.append(f"sitemap entry missing lastmod: {locations[-1]}")
                else:
                    try:
                        parsed_date = date.fromisoformat((lastmod.text or "").strip())
                        if parsed_date > date.today():
                            errors.append(f"sitemap lastmod is in the future: {locations[-1]}")
                    except ValueError:
                        errors.append(f"invalid sitemap lastmod: {locations[-1]}")
            if set(locations) != set(INDEXABLE.values()):
                errors.append("sitemap URLs do not exactly match the four indexable Main pages")
        except ElementTree.ParseError as exc:
            errors.append(f"sitemap.xml is invalid XML: {exc}")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8") if (ROOT / "robots.txt").is_file() else ""
    for marker in ("User-agent: *", "Allow: /", "Sitemap: https://www.goreecloud.com/sitemap.xml"):
        if marker not in robots:
            errors.append(f"robots.txt missing marker: {marker}")
    if "Disallow:" in robots:
        errors.append("Main robots.txt must not block the public site")

    if errors:
        print("Main public surface validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Main linked public surface, indexing, sitemap, robots, and canonical metadata validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
