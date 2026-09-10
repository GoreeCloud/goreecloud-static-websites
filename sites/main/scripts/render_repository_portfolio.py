#!/usr/bin/env python3
"""Render reviewed GoreeCloud Main website source into public-safe HTML.

The Main site deliberately does not publish a numeric claim about the live GitHub
portfolio. Repository creation is continuous; the connected GitHub organization is
the live source of truth for counts. The checked-in repository manifest remains a
reviewed historical/source-role record, not a live-count authority.
"""

from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "repository-portfolio.json"

PLATFORM_SECTION = re.compile(
    r'\n    <section id="platform" class="section platform-section">.*?(?=\n    <section id="development")',
    re.DOTALL,
)
DEVELOPMENT_SECTION = re.compile(
    r'\n    <section id="development" class="section section-alt">.*?(?=\n    <section id="repositories")',
    re.DOTALL,
)
PLATFORM_NAVIGATION = re.compile(r'\s*<a href="(?:index\.html)?#platform">Platform</a>')
DEVELOPMENT_NAVIGATION = re.compile(r'\s*<a href="(?:index\.html)?#development">Projects</a>')


def load_manifest(root: Path = ROOT) -> dict:
    return json.loads((root / "docs" / "repository-portfolio.json").read_text(encoding="utf-8"))


def _remove_obsolete_navigation(source: str) -> str:
    source = PLATFORM_NAVIGATION.sub("", source)
    return DEVELOPMENT_NAVIGATION.sub("", source)


def render_homepage(source: str) -> str:
    rendered = source
    rendered, platform_count = PLATFORM_SECTION.subn("", rendered, count=1)
    if platform_count != 1:
        raise ValueError("homepage legacy infrastructure-foundation section could not be resolved")
    rendered, development_count = DEVELOPMENT_SECTION.subn("", rendered, count=1)
    if development_count != 1:
        raise ValueError("homepage duplicate development section could not be resolved")
    rendered = _remove_obsolete_navigation(rendered)
    rendered = rendered.replace('  <link rel="stylesheet" href="css/platform.css">\n', '')
    rendered = rendered.replace('  <link rel="stylesheet" href="css/development.css">\n', '')
    return rendered


def render_public_file(relative: str, source: str, manifest: dict) -> str:
    # ``manifest`` remains in the signature for deterministic build compatibility,
    # but is intentionally not used to create live-count claims.
    del manifest
    if relative == "index.html":
        return render_homepage(source)
    if relative.endswith(".html"):
        return _remove_obsolete_navigation(source)
    return source
