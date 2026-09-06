#!/usr/bin/env python3
"""Enforce conservative performance budgets for the exact public website artifact."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import sys

from build_public_site import PUBLIC_FILES, ROOT

KIB = 1024
HTML_FILE_BUDGET = 64 * KIB
HTML_TOTAL_BUDGET = 96 * KIB
# Glaze UI 1.5 Stable is intentionally vendored as one same-origin bundle so
# public pages do not depend on a cross-origin design-system runtime. The
# reviewed bundle is ~49 KiB; keep a narrow ceiling above it rather than
# weakening the per-file check entirely.
CSS_FILE_BUDGET = 56 * KIB
# The homepage retains its existing local presentation layers alongside the
# vendored Stable bundle. 128 KiB keeps the aggregate CSS budget explicit while
# accommodating the reviewed 1.5 adoption without removing those local layers.
CSS_TOTAL_BUDGET = 128 * KIB
JS_FILE_BUDGET = 16 * KIB
JS_TOTAL_BUDGET = 24 * KIB
SVG_FILE_BUDGET = 24 * KIB
SVG_TOTAL_BUDGET = 128 * KIB
RASTER_FILE_BUDGET = 256 * KIB
RASTER_TOTAL_BUDGET = 256 * KIB
PUBLIC_ARTIFACT_BUDGET = 512 * KIB
MAX_STYLESHEETS_BY_PAGE = {
    "index.html": 12,
    "repositories.html": 5,
    "privacy.html": 4,
    "security.html": 4,
    "404.html": 5,
}
MAX_SCRIPTS_BY_PAGE = {
    "index.html": 2,
    "repositories.html": 2,
    "privacy.html": 1,
    "security.html": 1,
    "404.html": 1,
}

PUBLIC_HTML = tuple(
    ROOT / relative
    for relative in PUBLIC_FILES
    if relative in {"index.html", "repositories.html", "privacy.html", "security.html", "404.html"}
)


class PerformanceHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.images_without_dimensions: list[str] = []
        self.stylesheet_count = 0
        self.script_count = 0

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {name: value or "" for name, value in attrs_list}
        if tag == "img":
            if not attrs.get("width") or not attrs.get("height"):
                self.images_without_dimensions.append(attrs.get("src", "(missing src)"))
        elif tag == "link" and "stylesheet" in attrs.get("rel", "").split():
            self.stylesheet_count += 1
        elif tag == "script" and attrs.get("src"):
            self.script_count += 1


def public_files(errors: list[str]) -> list[Path]:
    paths: list[Path] = []
    for relative in PUBLIC_FILES:
        path = ROOT / relative
        if not path.exists() or not path.is_file() or path.is_symlink():
            errors.append(f"Performance budget cannot measure invalid allowlisted source: {relative}")
            continue
        paths.append(path)
    return paths


def enforce_individual(errors: list[str], files: list[Path], budget: int, label: str) -> None:
    for path in files:
        size = path.stat().st_size
        if size > budget:
            errors.append(
                f"{label} exceeds {budget // KIB} KiB budget: {path.relative_to(ROOT)} is {size / KIB:.1f} KiB."
            )


def enforce_total(errors: list[str], files: list[Path], budget: int, label: str) -> None:
    size = sum(path.stat().st_size for path in files)
    if size > budget:
        errors.append(f"{label} exceeds {budget // KIB} KiB total budget: {size / KIB:.1f} KiB.")


def main() -> int:
    errors: list[str] = []
    deployable = public_files(errors)

    if len(deployable) != len(PUBLIC_FILES):
        errors.append("Performance measurement must cover every explicitly allowlisted public file.")

    html_files = [path for path in deployable if path.suffix.lower() == ".html"]
    css_files = [path for path in deployable if path.suffix.lower() == ".css"]
    js_files = [path for path in deployable if path.suffix.lower() == ".js"]
    svg_files = [path for path in deployable if path.suffix.lower() == ".svg"]
    raster_files = [path for path in deployable if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}]

    enforce_individual(errors, html_files, HTML_FILE_BUDGET, "HTML file")
    enforce_total(errors, html_files, HTML_TOTAL_BUDGET, "HTML")
    enforce_individual(errors, css_files, CSS_FILE_BUDGET, "CSS file")
    enforce_total(errors, css_files, CSS_TOTAL_BUDGET, "CSS")
    enforce_individual(errors, js_files, JS_FILE_BUDGET, "JavaScript file")
    enforce_total(errors, js_files, JS_TOTAL_BUDGET, "JavaScript")
    enforce_individual(errors, svg_files, SVG_FILE_BUDGET, "SVG file")
    enforce_total(errors, svg_files, SVG_TOTAL_BUDGET, "SVG")
    enforce_individual(errors, raster_files, RASTER_FILE_BUDGET, "Raster image")
    enforce_total(errors, raster_files, RASTER_TOTAL_BUDGET, "Raster images")

    total_size = sum(path.stat().st_size for path in deployable)
    if total_size > PUBLIC_ARTIFACT_BUDGET:
        errors.append(
            f"Public static artifact exceeds {PUBLIC_ARTIFACT_BUDGET // KIB} KiB source budget: "
            f"{total_size / KIB:.1f} KiB."
        )

    for path in PUBLIC_HTML:
        if not path.exists():
            errors.append(f"Human-facing public page is missing from performance validation: {path.relative_to(ROOT)}")
            continue
        parser = PerformanceHTMLParser()
        parser.feed(path.read_text(encoding="utf-8"))
        for src in parser.images_without_dimensions:
            errors.append(
                f"Image must declare width and height to reserve layout space in {path.relative_to(ROOT)}: {src}"
            )

        stylesheet_limit = MAX_STYLESHEETS_BY_PAGE[path.name]
        script_limit = MAX_SCRIPTS_BY_PAGE[path.name]
        if parser.stylesheet_count > stylesheet_limit:
            errors.append(
                f"{path.name} stylesheet request count exceeds {stylesheet_limit}: "
                f"found {parser.stylesheet_count}."
            )
        if parser.script_count > script_limit:
            errors.append(
                f"{path.name} script request count exceeds {script_limit}: found {parser.script_count}."
            )

    if errors:
        print("Performance budget validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"Performance budget validation passed: {len(deployable)} explicitly allowlisted public files, "
        f"{total_size / KIB:.1f} KiB."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
