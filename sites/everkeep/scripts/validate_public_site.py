#!/usr/bin/env python3
"""Validate Continuity Center V1.1 source, authority boundary, and isolated artifact."""
from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from glaze_v1 import FILES, GLAZE_SOURCE_REVISION, validate_bundle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "website"
DIST = SITE / "dist"
ICON = ROOT / "assets" / "everkeep.svg"
errors: list[str] = []

for name in ("index.html", "404.html", "style.css", "site-polish.css", "_headers", "robots.txt", "sitemap.xml"):
    if not (SITE / name).is_file():
        errors.append(f"missing Continuity Center source: {name}")
if not ICON.is_file():
    errors.append("missing canonical Everkeep identity asset")

for page_name in ("index.html", "404.html"):
    path = SITE / page_name
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8")
    for marker in (
        'data-glaze-version="1.1"',
        'name="goreecloud-glaze-ui" content="1.1.0"',
        'data-glaze-ui="1.1.0"',
        '/assets/glaze-v1/glaze-v1.1.0.css',
        'glaze-canvas',
    ):
        if marker not in text:
            errors.append(f"{page_name} missing V1.1 source marker: {marker}")
    for forbidden in ('data-glaze-ui="2.', 'content="2.1.0"', 'glaze-ui-2.', 'glaze-2.'):
        if forbidden in text:
            errors.append(f"{page_name} still activates pre-reset GLAZE source: {forbidden}")

index = (SITE / "index.html").read_text(encoding="utf-8") if (SITE / "index.html").is_file() else ""
for marker in (
    '<link rel="icon" href="assets/everkeep.svg" type="image/svg+xml">',
    '<img src="assets/everkeep.svg" alt="" width="38" height="38">',
    "GoreeCloud Manager", "Privacy Shield", "Wardveil Security", "Everkeep",
    "Glaze UI", "GoreeCloud Mesh", "GoreeCloud Identity",
    "simulation-only", "Production recovery effects", "GLAZE UI V1.1 / 1.1.0",
):
    if marker not in index:
        errors.append(f"Continuity Center authority/truth marker missing: {marker}")
for stale in ("Glaze UI 2.1", "Glaze UI 2.2", "Presented through Glaze UI 2.1 Stable"):
    if stale in index:
        errors.append(f"Continuity Center stale current-design claim remains: {stale}")

error_html = (SITE / "404.html").read_text(encoding="utf-8") if (SITE / "404.html").is_file() else ""
if '<link rel="icon" href="/assets/everkeep.svg" type="image/svg+xml">' not in error_html:
    errors.append("Continuity Center 404 missing canonical Everkeep favicon")
if 'name="robots" content="noindex,follow"' not in error_html:
    errors.append("Continuity Center 404 must remain noindex")

headers = (SITE / "_headers").read_text(encoding="utf-8") if (SITE / "_headers").is_file() else ""
for marker in ("Content-Security-Policy:", "frame-ancestors 'none'", "X-Content-Type-Options: nosniff", "Permissions-Policy:", "Strict-Transport-Security:"):
    if marker not in headers:
        errors.append(f"Continuity Center security header missing: {marker}")

robots = (SITE / "robots.txt").read_text(encoding="utf-8") if (SITE / "robots.txt").is_file() else ""
sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8") if (SITE / "sitemap.xml").is_file() else ""
if "https://everkeep.goreecloud.com/sitemap.xml" not in robots:
    errors.append("Continuity Center robots.txt missing canonical sitemap URL")
if "https://everkeep.goreecloud.com/" not in sitemap:
    errors.append("Continuity Center sitemap missing canonical domain")

if DIST.is_dir():
    expected = {
        "index.html", "404.html", "style.css", "site-polish.css", "_headers", "robots.txt", "sitemap.xml",
        "assets/everkeep.svg", *(f"assets/glaze-v1/{name}" for name in FILES),
    }
    actual = {str(path.relative_to(DIST)).replace("\\", "/") for path in DIST.rglob("*") if path.is_file()}
    if actual != expected:
        errors.append(f"Continuity Center artifact allowlist mismatch: actual={sorted(actual)}")
    built_icon = DIST / "assets" / "everkeep.svg"
    if built_icon.is_file() and ICON.is_file() and built_icon.read_bytes() != ICON.read_bytes():
        errors.append("built Everkeep identity differs from canonical source")
    bundle: dict[str, str] = {}
    for name in FILES:
        path = DIST / "assets" / "glaze-v1" / name
        if path.is_file():
            bundle[name] = path.read_text(encoding="utf-8")
    if len(bundle) == len(FILES):
        try:
            validate_bundle(bundle)
        except ValueError as exc:
            errors.append(str(exc))
else:
    errors.append("Continuity Center website/dist is missing; build before validation")

if errors:
    print("Continuity Center V1.1 validation failed:")
    for error in errors:
        print(f"  - {error}")
    raise SystemExit(1)
print(f"Continuity Center source/build validated against GLAZE UI V1.1 revision {GLAZE_SOURCE_REVISION}; production recovery and consumer acceptance remain separate.")
