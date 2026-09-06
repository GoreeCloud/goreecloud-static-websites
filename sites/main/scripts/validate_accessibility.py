#!/usr/bin/env python3
"""Validate structural accessibility across GoreeCloud's human-facing pages.

This validator intentionally uses only the Python standard library. It catches
high-value accessibility regressions that can be verified statically without
pretending to replace assistive-technology or real-browser testing.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_HTML = (
    ROOT / "index.html",
    ROOT / "repositories.html",
    ROOT / "privacy.html",
    ROOT / "security.html",
    ROOT / "404.html",
)
FOCUS_STYLES = (
    ROOT / "css" / "style.css",
    ROOT / "css" / "glaze-polish.css",
)
HEADING_RE = re.compile(r"h([1-6])")


@dataclass
class InteractiveElement:
    tag: str
    line: int
    attrs: dict[str, str]
    text_parts: list[str] = field(default_factory=list)

    def accessible_name(self) -> str:
        explicit = self.attrs.get("aria-label", "").strip()
        if explicit:
            return explicit
        if self.attrs.get("aria-labelledby", "").strip():
            return "aria-labelledby"
        return " ".join(part.strip() for part in self.text_parts if part.strip()).strip()


class AccessibilityParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang: str | None = None
        self.ids: Counter[str] = Counter()
        self.headings: list[tuple[int, int]] = []
        self.mains: list[tuple[int, dict[str, str]]] = []
        self.navs: list[tuple[int, dict[str, str]]] = []
        self.skip_links: list[tuple[int, str]] = []
        self.images_missing_alt: list[tuple[int, str]] = []
        self.aria_references: list[tuple[int, str, list[str]]] = []
        self.positive_tabindex: list[tuple[int, str, str]] = []
        self.autofocus: list[tuple[int, str]] = []
        self.target_blank_errors: list[tuple[int, str]] = []
        self.invalid_links: list[tuple[int, str]] = []
        self.interactive_stack: list[InteractiveElement] = []
        self.interactive_elements: list[InteractiveElement] = []
        self.open_tag_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        line, _ = self.getpos()
        attrs = {name.lower(): value or "" for name, value in attrs_list}
        tag = tag.lower()
        self.open_tag_stack.append(tag)

        if tag == "html":
            self.html_lang = attrs.get("lang")
        if attrs.get("id"):
            self.ids[attrs["id"]] += 1
        if tag == "main":
            self.mains.append((line, attrs))
        if tag == "nav":
            self.navs.append((line, attrs))

        heading = HEADING_RE.fullmatch(tag)
        if heading:
            self.headings.append((int(heading.group(1)), line))

        classes = set(attrs.get("class", "").split())
        if tag == "a" and "skip-link" in classes:
            self.skip_links.append((line, attrs.get("href", "")))

        if tag == "img":
            if "alt" not in attrs:
                self.images_missing_alt.append((line, attrs.get("src", "(missing src)")))
            elif attrs["alt"].strip():
                for interactive in self.interactive_stack:
                    interactive.text_parts.append(attrs["alt"])

        for reference_attr in ("aria-controls", "aria-labelledby"):
            raw = attrs.get(reference_attr, "").strip()
            if raw:
                self.aria_references.append((line, reference_attr, raw.split()))

        if "tabindex" in attrs:
            raw = attrs["tabindex"].strip()
            try:
                value = int(raw)
            except ValueError:
                self.positive_tabindex.append((line, tag, raw))
            else:
                if value > 0:
                    self.positive_tabindex.append((line, tag, raw))

        if "autofocus" in attrs:
            self.autofocus.append((line, tag))

        if tag == "a":
            href = attrs.get("href", "").strip()
            if not href or href.lower().startswith(("javascript:", "data:")):
                self.invalid_links.append((line, href or "(empty href)"))
            if attrs.get("target") == "_blank":
                rel = set(attrs.get("rel", "").lower().split())
                if not {"noopener", "noreferrer"}.issubset(rel):
                    self.target_blank_errors.append((line, href or "(empty href)"))

        if tag in {"a", "button"}:
            interactive = InteractiveElement(tag=tag, line=line, attrs=attrs)
            self.interactive_stack.append(interactive)
            self.interactive_elements.append(interactive)

        if tag == "button" and not attrs.get("type", "").strip():
            self.invalid_links.append((line, "button missing explicit type"))

    def handle_startendtag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs_list)
        self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        if not data.strip():
            return
        for interactive in self.interactive_stack:
            interactive.text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"a", "button"}:
            for index in range(len(self.interactive_stack) - 1, -1, -1):
                if self.interactive_stack[index].tag == tag:
                    del self.interactive_stack[index]
                    break
        for index in range(len(self.open_tag_stack) - 1, -1, -1):
            if self.open_tag_stack[index] == tag:
                del self.open_tag_stack[index:]
                break


def validate_page(path: Path) -> list[str]:
    errors: list[str] = []
    parser = AccessibilityParser()
    parser.feed(path.read_text(encoding="utf-8"))
    name = path.name

    if parser.html_lang != "en":
        errors.append(f"{name}: <html> must declare lang=\"en\".")

    duplicate_ids = sorted(identifier for identifier, count in parser.ids.items() if count > 1)
    for identifier in duplicate_ids:
        errors.append(f"{name}: duplicate id #{identifier}.")

    if len(parser.mains) != 1:
        errors.append(f"{name}: expected exactly one <main>, found {len(parser.mains)}.")
    else:
        line, attrs = parser.mains[0]
        if attrs.get("id") != "main":
            errors.append(f"{name}:{line}: <main> must retain id=\"main\" for the skip link.")
        if attrs.get("tabindex") != "-1":
            errors.append(f"{name}:{line}: <main> must retain tabindex=\"-1\" for programmatic focus.")

    if not parser.skip_links:
        errors.append(f"{name}: a visible-on-focus skip link is required.")
    else:
        first_line, first_href = parser.skip_links[0]
        if first_href != "#main":
            errors.append(f"{name}:{first_line}: primary skip link must target #main.")

    if not parser.headings:
        errors.append(f"{name}: at least one heading is required.")
    else:
        if parser.headings[0][0] != 1:
            errors.append(f"{name}:{parser.headings[0][1]}: the first heading must be h1.")
        h1_count = sum(1 for level, _ in parser.headings if level == 1)
        if h1_count != 1:
            errors.append(f"{name}: expected exactly one h1, found {h1_count}.")
        previous_level = parser.headings[0][0]
        for level, line in parser.headings[1:]:
            if level > previous_level + 1:
                errors.append(f"{name}:{line}: heading level jumps from h{previous_level} to h{level}.")
            previous_level = level

    for line, attrs in parser.navs:
        if not attrs.get("aria-label", "").strip() and not attrs.get("aria-labelledby", "").strip():
            errors.append(f"{name}:{line}: every <nav> landmark must have an accessible label.")

    for line, source in parser.images_missing_alt:
        errors.append(f"{name}:{line}: image must include alt text, even when decorative: {source}")

    for line, attr, identifiers in parser.aria_references:
        for identifier in identifiers:
            if identifier not in parser.ids:
                errors.append(f"{name}:{line}: {attr} references missing id #{identifier}.")

    for line, tag, value in parser.positive_tabindex:
        errors.append(f"{name}:{line}: <{tag}> must not use positive/invalid tabindex {value!r}.")

    for line, tag in parser.autofocus:
        errors.append(f"{name}:{line}: <{tag}> must not use autofocus.")

    for line, href in parser.target_blank_errors:
        errors.append(f"{name}:{line}: target=\"_blank\" must include rel=\"noopener noreferrer\": {href}")

    for line, detail in parser.invalid_links:
        if detail == "button missing explicit type":
            errors.append(f"{name}:{line}: every <button> must declare an explicit type.")
        else:
            errors.append(f"{name}:{line}: link has an unsafe or empty destination: {detail}")

    for interactive in parser.interactive_elements:
        if not interactive.accessible_name():
            errors.append(f"{name}:{interactive.line}: <{interactive.tag}> requires an accessible name.")

    return errors


def validate_focus_styles() -> list[str]:
    errors: list[str] = []
    css = "\n".join(path.read_text(encoding="utf-8") for path in FOCUS_STYLES if path.exists())
    if ":focus-visible" not in css:
        errors.append("CSS must retain explicit :focus-visible styling for keyboard users.")
    if ".skip-link:focus" not in css and ".skip-link:focus-visible" not in css:
        errors.append("CSS must retain a visible focused state for the skip link.")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in PUBLIC_HTML:
        if not path.exists():
            errors.append(f"Required human-facing page is missing: {path.relative_to(ROOT)}")
            continue
        errors.extend(validate_page(path))
    errors.extend(validate_focus_styles())

    if errors:
        print("Accessibility validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Accessibility validation passed across {len(PUBLIC_HTML)} human-facing HTML pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
