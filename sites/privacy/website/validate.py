#!/usr/bin/env python3
"""Validate Privacy Center V1.1 source, authority boundaries, and built artifact."""
from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from glaze_v1 import FILES, GLAZE_SOURCE_REVISION, validate_bundle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "website"
DIST = SITE / "dist"
ICON = ROOT / "branding" / "privacy-shield" / "privacy-shield-icon.svg"
errors: list[str] = []

for name in ("index.html", "404.html", "_headers", "site.css", "site-polish.css", "site.js"):
    if not (SITE / name).is_file():
        errors.append(f"missing Privacy Center source: {name}")
if not ICON.is_file():
    errors.append("missing canonical Privacy Shield icon")

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
        '<link rel="icon" href="/assets/privacy-shield-icon.svg" type="image/svg+xml">',
    ):
        if marker not in text:
            errors.append(f"{page_name} missing V1.1/identity marker: {marker}")
    for forbidden in ('data-glaze-ui="2.', 'content="2.1.0"', 'glaze-ui-2.', 'data-glaze-appearance=', 'data-theme='):
        if forbidden in text:
            errors.append(f"{page_name} still activates pre-reset source: {forbidden}")

index = (SITE / "index.html").read_text(encoding="utf-8") if (SITE / "index.html").is_file() else ""
for marker in (
    "GoreeCloud Manager", "Privacy Shield", "Wardveil Security", "Everkeep",
    "Glaze UI", "GoreeCloud Mesh", "GoreeCloud Identity",
    "GLAZE UI V1.1", "Consumer acceptance · Evidence required",
):
    if marker not in index:
        errors.append(f"Privacy Center current authority marker missing: {marker}")
for stale in ("Glaze UI 2.1", "Glaze UI 2.2", "Presented through Glaze UI 2.1 Stable"):
    if stale in index:
        errors.append(f"Privacy Center stale current-design claim remains: {stale}")

js = (SITE / "site.js").read_text(encoding="utf-8") if (SITE / "site.js").is_file() else ""
for marker in ("dataset.glzAppearance", "localStorage.removeItem", "IntersectionObserver"):
    if marker not in js:
        errors.append(f"Privacy Center V1.1 interaction marker missing: {marker}")
for forbidden in ("dataset.glazeAppearance", "dataset.theme", "deep-dark", "createElement("):
    if forbidden in js:
        errors.append(f"Privacy Center pre-reset/dynamic truth behavior remains: {forbidden}")

css = (SITE / "site.css").read_text(encoding="utf-8") if (SITE / "site.css").is_file() else ""
for marker in (
    "data-glz-appearance=dark", "min-width:320px", "min-height:48px",
    "prefers-reduced-motion:reduce", "prefers-reduced-transparency:reduce", "forced-colors:active",
):
    if marker not in css:
        errors.append(f"Privacy Center V1.1 responsive/accessibility marker missing: {marker}")

headers = (SITE / "_headers").read_text(encoding="utf-8") if (SITE / "_headers").is_file() else ""
for marker in ("Content-Security-Policy:", "frame-ancestors 'none'", "X-Content-Type-Options: nosniff", "Permissions-Policy:"):
    if marker not in headers:
        errors.append(f"Privacy Center security header missing: {marker}")

if DIST.is_dir():
    expected = {
        "index.html", "404.html", "_headers", "assets/site.css", "assets/site-polish.css",
        "assets/site.js", "assets/privacy-shield-icon.svg",
        *(f"assets/glaze-v1/{name}" for name in FILES),
    }
    actual = {str(path.relative_to(DIST)).replace("\\", "/") for path in DIST.rglob("*") if path.is_file()}
    if actual != expected:
        errors.append(f"Privacy Center artifact allowlist mismatch: actual={sorted(actual)}")
    icon_out = DIST / "assets" / "privacy-shield-icon.svg"
    if icon_out.is_file() and ICON.is_file() and icon_out.read_bytes() != ICON.read_bytes():
        errors.append("Privacy Center built icon differs from canonical source")
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
    errors.append("Privacy Center dist/ is missing; build before validation")

if errors:
    print("Privacy Center V1.1 validation failed:")
    for error in errors:
        print(f"  - {error}")
    raise SystemExit(1)
print(f"Privacy Center source/build validated against GLAZE UI V1.1 revision {GLAZE_SOURCE_REVISION}; production acceptance remains separate.")
