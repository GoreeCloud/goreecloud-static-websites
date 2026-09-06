#!/usr/bin/env python3
"""Validate Identity Center truth, canonical identity, and namespace boundaries."""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parent
for name in ("index.html", "404.html", "style.css", "app.js", "build.py", "_headers", "robots.txt", "sitemap.xml", "assets/identity.svg"):
    if not (ROOT / name).is_file():
        raise SystemExit(f"missing Identity Center source: {name}")

html = (ROOT / "index.html").read_text(encoding="utf-8")
error_html = (ROOT / "404.html").read_text(encoding="utf-8")
script = (ROOT / "app.js").read_text(encoding="utf-8")
headers = (ROOT / "_headers").read_text(encoding="utf-8")
robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")

for marker in (
    "GoreeCloud Integral Platform System",
    "id.goreecloud.com",
    "production GoreeCloud Identity is not yet accepted",
    "Other Integral Platform Systems stay independent",
    "GoreeCloud Manager",
    "Wardveil Security",
    "Privacy Shield",
    "Everkeep",
    "Glaze UI",
    "GoreeCloud Mesh",
    "GLAZE UI V1.1 / 1.1.0 consumer acceptance",
    "authentik-derived transitional runtime",
):
    if marker not in html:
        raise SystemExit(f"missing Identity Center truth marker: {marker}")

for page_name, page in (("index", html), ("404", error_html)):
    for marker in (
        'data-glaze-version="1.1"',
        'name="goreecloud-glaze-ui" content="1.1.0"',
        'data-glaze-ui="1.1.0"',
        '/assets/glaze-v1/glaze-v1.1.0.css',
        'glaze-canvas',
        '/assets/identity.svg',
    ):
        if marker not in page:
            raise SystemExit(f"{page_name} missing Identity/V1.1 marker: {marker}")

for stale in (
    "identity.goreecloud.com",
    'name="goreecloud-glaze-ui" content="2.1.0"',
    'data-glaze-ui="2.1.0"',
    "glaze-ui-2.1.0.css",
    "Glaze UI 2.1.0 Stable consumer acceptance",
):
    if stale in html or stale in robots or stale in sitemap:
        raise SystemExit(f"superseded Identity Center state remains active: {stale}")

if "https://id.goreecloud.com/" not in sitemap or "https://id.goreecloud.com/sitemap.xml" not in robots:
    raise SystemExit("Identity Center crawl metadata is not bound to id.goreecloud.com")

if "dataset.glzAppearance" not in script or "data-glz-appearance" not in script:
    raise SystemExit("Identity Center JavaScript is missing the V1.1 appearance contract")
if "dataset.theme" in script:
    raise SystemExit("Identity Center JavaScript still mutates the pre-reset theme attribute")

icon = ROOT / "assets/identity.svg"
raw = icon.read_bytes()
actual_blob = hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()
if actual_blob != "dc8287e385f86767f0105c48a8f234d8440d7623":
    raise SystemExit(f"Identity Center icon drifted from centralized canonical copy: {actual_blob}")

for marker in ("Content-Security-Policy:", "X-Content-Type-Options: nosniff", "frame-ancestors"):
    if marker not in headers:
        raise SystemExit(f"missing Identity Center security header: {marker}")
for forbidden in ("docs.goauthentik.io", "google-analytics", "googletagmanager", "segment.com", "fonts.googleapis.com"):
    if forbidden in html.lower():
        raise SystemExit(f"forbidden/upstream Identity Center dependency: {forbidden}")

print("Identity Center V1.1 source, approved id.goreecloud.com namespace, canonical identity, and evidence boundaries validated")
