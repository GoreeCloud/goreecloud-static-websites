#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for name in ("index.html", "404.html", "site.css", "site.js", "v1.3-site.css", "glaze.lock.json", "_headers"):
    if not (ROOT / name).is_file():
        raise SystemExit(f"missing roadmap site file: {name}")

html = (ROOT / "index.html").read_text(encoding="utf-8")
headers = (ROOT / "_headers").read_text(encoding="utf-8")

for needle in (
    "Public Development Roadmap · September 12, 2026",
    "dates are not promises",
    "private infrastructure or security-sensitive work is omitted",
    "GLAZE UI V1.3 / 1.3.0 is the current official Stable consumer target",
    "14 registered website packages",
    "GoreeCloud/goreecloud-static-websites",
    "Seven systems, seven authority boundaries",
    "GoreeCloud Manager, Privacy Shield, Wardveil Security, Everkeep, GLAZE UI, GoreeCloud Mesh, and GoreeCloud Identity",
    "45 verified GoreeCloud products across nine functional product groups",
    "GoreeCloud Health, Reader, Router OS, Social, Home, and Home Security",
    "Portfolio membership does not establish Stable or production acceptance for any product",
    "nine current Suite product groups",
    "developer and intelligence",
    "home, health, and personal systems",
    "infrastructure and edge products",
    "Privacy Shield durable authorization",
    "Wardveil shared security plane",
    "Everkeep recovery assurance",
    "Manager visibility-first operations",
    "Labs is the fourteenth authoritative-main static-site package",
    "Labs production deployment remains separately gated",
    "Evidence over labels",
):
    if needle not in html:
        raise SystemExit(f"required current roadmap content missing: {needle}")

for stale in (
    "August 31, 2026",
    "September 10, 2026",
    "57 repositories",
    "40 public and 17 private",
    "Six substantive platform systems",
    "Glaze UI 2.1.0",
    "Glaze UI 2.1",
    "Glaze UI 2.0.0",
    "Facet is the current official",
    "Ten independently deployed public destinations",
    "Identity Center is the eleventh",
    "identity.goreecloud.com",
    "27 Suite applications across seven functional groups",
    "27 Suite applications",
    "across seven functional groups",
    "13 registered website packages",
    "Labs remains separate candidate scope",
    "manifest currently contains 13 packages",
):
    if stale in html:
        raise SystemExit(f"superseded current-state roadmap claim remains public: {stale}")

for needle in ("Content-Security-Policy:", "frame-ancestors 'none'", "Permissions-Policy:", "X-Content-Type-Options: nosniff"):
    if needle not in headers:
        raise SystemExit(f"required security header missing: {needle}")
for prohibited in ("google-analytics", "googletagmanager", "fonts.googleapis.com", "segment.com"):
    if prohibited in html.lower():
        raise SystemExit(f"prohibited runtime dependency: {prohibited}")

if html.count('id="now"') != 1 or html.count('id="next"') != 1 or html.count('id="later"') != 1 or html.count('id="principles"') != 1:
    raise SystemExit("roadmap section structure is incomplete or duplicated")
if html.count('<div class="principle-grid">') != 1:
    raise SystemExit("roadmap principle-grid structure is missing or duplicated")

print("GoreeCloud Roadmap current V1.3, seven-system, 45-product, nine-group, and 14-package public direction validated")
