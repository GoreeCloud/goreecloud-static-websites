#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for name in ("index.html", "404.html", "site.css", "site.js", "glaze-ui-2.1.0.css", "_headers"):
    if not (ROOT / name).is_file():
        raise SystemExit(f"missing roadmap site file: {name}")

html = (ROOT / "index.html").read_text(encoding="utf-8")
error_html = (ROOT / "404.html").read_text(encoding="utf-8")
css = (ROOT / "glaze-ui-2.1.0.css").read_text(encoding="utf-8")
headers = (ROOT / "_headers").read_text(encoding="utf-8")

for needle in (
    "Public Development Roadmap",
    "August 31, 2026",
    "Active development",
    "Near-term priorities",
    "Long-term direction",
    "dates are not promises",
    "private infrastructure or security-sensitive work is omitted",
    "GoreeCloud Code",
    "Forgejo is an initial replaceable infrastructure foundation",
    "GoreeCloud AI",
    "GoreeCloud Documents",
    "GoreeCloud Messenger",
    "GoreeCloud Gateway",
    "GoreeCloud Quill",
    "GoreeCloud Mesh",
    "GoreeCloud Identity",
    "GoreeCloud File Manager",
    "GoreeCloud Maps",
    "GoreeCloud App Store",
    "Six substantive platform systems",
    "Glaze UI 2.1.0",
    "Content is solid. Interaction is glazed.",
    "56px Touch Assistance",
    "Facet is the current official Glaze UI identity",
    "Evidence over labels",
    "Ten independently deployed public destinations",
    "Identity Center is the eleventh official first-party surface",
    "Identity Center publication acceptance",
):
    if needle not in html:
        raise SystemExit(f"required roadmap content missing: {needle}")

for page_name, page in (("index", html), ("404", error_html)):
    for needle in ('name="goreecloud-glaze-ui" content="2.1.0"', 'data-glaze-ui="2.1.0"', 'glaze-canvas'):
        if needle not in page:
            raise SystemExit(f"{page_name} missing Glaze UI 2.1 marker: {needle}")
    if 'data-glaze-ui="1.5.0"' in page or 'data-glaze-ui="2.0.0"' in page:
        raise SystemExit(f"{page_name} still activates a superseded Glaze UI bundle")

for needle in (
    "Glaze UI 2.1.0 Stable integration",
    "c49113eb8b93c267613fdf1bbca1f814495acad7",
    "Content is solid. Interaction is glazed.",
    "--glaze-touch-assisted:56px",
    "data-glaze-density=compact",
    "data-glaze-performance=reduced",
    "data-glaze-large-text=true",
    "prefers-reduced-motion",
    "prefers-reduced-transparency",
    "forced-colors:active",
):
    if needle not in css:
        raise SystemExit(f"Glaze UI 2.1 web-layer marker missing: {needle}")

for stale in (
    "Glaze UI 2.1 remains Candidate",
    "53-repository source inventory",
    "the five substantive platform systems",
    "Gitea is the selected permanent authoritative source-control",
    "Complete Gitea independence",
    "Glaze UI 1.4 is the current Stable production target",
    "Glaze UI 1.5.0 is the current Stable production target",
    "Glaze UI 2.0.0 is the current Stable production target",
    "Glaze UI Fold identity",
    "approved Fold mark remains the canonical Glaze UI visual identity",
):
    if stale in html:
        raise SystemExit(f"superseded roadmap direction remains public: {stale}")

for needle in ("Content-Security-Policy:", "frame-ancestors 'none'", "Permissions-Policy:", "X-Content-Type-Options: nosniff"):
    if needle not in headers:
        raise SystemExit(f"required security header missing: {needle}")
for prohibited in ("google-analytics", "googletagmanager", "fonts.googleapis.com", "segment.com"):
    if prohibited in html.lower():
        raise SystemExit(f"prohibited runtime dependency: {prohibited}")

print("GoreeCloud roadmap current portfolio, six-system model, Facet identity, and Glaze UI 2.1 public-site validation passed")
