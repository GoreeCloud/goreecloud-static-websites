#!/usr/bin/env python3
"""Regression coverage for the manifest-rendered public GoreeCloud repository directory."""

from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from render_repository_portfolio import render_repository_directory

PAGE = ROOT / "repositories.html"
MANIFEST = ROOT / "docs" / "repository-portfolio.json"
PORTFOLIO = json.loads(MANIFEST.read_text(encoding="utf-8"))
EXPECTED_REPOSITORIES = {repository["name"] for group in PORTFOLIO["groups"] for repository in group["repositories"]}
PRIVATE_REPOSITORIES = {repository["name"] for group in PORTFOLIO["groups"] for repository in group["repositories"] if repository["visibility"] == "private"}
EXPECTED_COUNTS = PORTFOLIO["counts"]


class DirectoryParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.stylesheets: set[str] = set()
        self.scripts: set[str] = set()
        self.canonical = ""
        self.has_viewport = False
        self.has_color_scheme = False
        self.has_skip_link = False
        self.has_main = False
        self.main_tabindex = ""
        self.repository_names: list[str] = []
        self.public_badges = 0
        self.private_badges = 0
        self.public_links: set[str] = set()
        self._h4_depth = 0
        self._h4_text: list[str] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        classes = set(attrs.get("class", "").split())
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "link" and "stylesheet" in attrs.get("rel", "").split():
            self.stylesheets.add(attrs.get("href", ""))
        if tag == "link" and "canonical" in attrs.get("rel", "").split():
            self.canonical = attrs.get("href", "")
        if tag == "script" and attrs.get("src"):
            self.scripts.add(attrs["src"])
        if tag == "meta" and attrs.get("name") == "viewport":
            self.has_viewport = True
        if tag == "meta" and attrs.get("name") == "color-scheme":
            self.has_color_scheme = True
        if tag == "a" and "skip-link" in classes and attrs.get("href") == "#main":
            self.has_skip_link = True
        if tag == "main" and attrs.get("id") == "main":
            self.has_main = True
            self.main_tabindex = attrs.get("tabindex", "")
        if tag == "span" and "repo-visibility" in classes:
            self.public_badges += int("public" in classes)
            self.private_badges += int("private" in classes)
        if tag == "a" and attrs.get("href", "").startswith("https://github.com/GoreeCloud/"):
            self.public_links.add(attrs["href"].rstrip("/").split("/")[-1])
        if tag == "h4":
            self._h4_depth = 1
            self._h4_text = []
        elif self._h4_depth:
            self._h4_depth += 1

    def handle_data(self, data: str) -> None:
        if self._h4_depth:
            self._h4_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self._h4_depth:
            return
        self._h4_depth -= 1
        if tag == "h4" and self._h4_depth == 0:
            self.repository_names.append("".join(self._h4_text).strip())
            self._h4_text = []


class RepositoryDirectoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        rendered = render_repository_directory(PAGE.read_text(encoding="utf-8"), PORTFOLIO)
        cls.parser = DirectoryParser()
        cls.parser.feed(rendered)

    def test_directory_has_canonical_public_identity(self) -> None:
        self.assertEqual(self.parser.canonical, "https://www.goreecloud.com/repositories.html")
        self.assertTrue(self.parser.has_viewport)
        self.assertTrue(self.parser.has_color_scheme)

    def test_directory_uses_shared_glaze_and_local_runtime(self) -> None:
        for stylesheet in ("css/style.css", "css/glaze.css", "css/glaze-polish.css", "css/repositories.css"):
            self.assertIn(stylesheet, self.parser.stylesheets)
        self.assertIn("js/theme-init.js", self.parser.scripts)
        self.assertIn("js/main.js", self.parser.scripts)

    def test_directory_preserves_accessible_page_shell(self) -> None:
        self.assertTrue(self.parser.has_skip_link)
        self.assertTrue(self.parser.has_main)
        self.assertEqual(self.parser.main_tabindex, "-1")
        self.assertIn("main", self.parser.ids)

    def test_directory_matches_manifest_repository_inventory(self) -> None:
        self.assertEqual(set(self.parser.repository_names), EXPECTED_REPOSITORIES)
        self.assertEqual(len(self.parser.repository_names), EXPECTED_COUNTS["total"])
        self.assertEqual(self.parser.public_badges, EXPECTED_COUNTS["public"])
        self.assertEqual(self.parser.private_badges, EXPECTED_COUNTS["private"])

    def test_private_repositories_do_not_publish_source_links(self) -> None:
        self.assertTrue(PRIVATE_REPOSITORIES.isdisjoint(self.parser.public_links))
        self.assertEqual(self.parser.public_links.intersection(EXPECTED_REPOSITORIES), EXPECTED_REPOSITORIES - PRIVATE_REPOSITORIES)


if __name__ == "__main__":
    unittest.main()
