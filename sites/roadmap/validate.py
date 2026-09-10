#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for name in ("index.html", "404.html", "site.css", "site.js", "v1.3-site.css", "glaze.lock.json", "_headers"):
    if not (ROOT / name).is_file():
        raise SystemExit(f"missing roadmap site file: {name}")

html = (ROOT / "index.html").read_text(encoding="utf-8")
headers = (ROOT / "_headers").read_text(encoding="utf-8")

for needle in (
    "Public Development Roadmap · September 10, 2026",
    "dates are not promises",
    "private infrastructure or security-sensitive work is omitted",
    "GLAZE UI V1.3 / 1.3.0 is the current official Stable consumer target",
    "13 registered website packages",
    "GoreeCloud/goreecloud-static-websites",
    "Seven systems, seven authority boundaries",
    "GoreeCloud Manager, Privacy Shield, Wardveil Security, Everkeep, GLAZE UI, GoreeCloud Mesh, and GoreeCloud Identity",
    "27 Suite applications across seven functional groups",
    "Privacy Shield durable authorization",
    "Wardveil shared security plane",
    "Everkeep recovery assurance",
    "Manager visibility-first operations",
    "Labs remains separate candidate scope",
    "Evidence over labels",
):
    if needle not in html:
        raise SystemExit(f"required current roadmap content missing: {needle}")

for stale in (
    "August 31, 2026",
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
):
    if stale in html:
        raise SystemExit(f"superseded current-state roadmap claim remains public: {stale}")

for needle in ("Content-Security-Policy:", "frame-ancestors 'none'", "Permissions-Policy:", "X-Content-Type-Options: nosniff"):
    if needle not in headers:
        raise SystemExit(f"required security header missing: {needle}")
for prohibited in ("google-analytics", "googletagmanager", "fonts.googleapis.com", "segment.com"):
    if prohibited in html.lower():
        raise SystemExit(f"prohibited runtime dependency: {prohibited}")

print("GoreeCloud Roadmap current V1.3, seven-system, 27-application, and 13-package public direction validated")
