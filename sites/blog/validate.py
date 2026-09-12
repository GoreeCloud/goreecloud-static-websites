#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
HEADERS = ROOT / "_headers"

for path in (HTML, HEADERS):
    if not path.is_file():
        raise SystemExit(f"missing Blog contract file: {path.name}")

html = HTML.read_text(encoding="utf-8")
headers = HEADERS.read_text(encoding="utf-8")

required = (
    "GLAZE UI V1.3 / 1.3.0 Stable",
    "seven integral platform systems",
    "GoreeCloud Manager, Privacy Shield, Wardveil Security, Everkeep, GLAZE UI, GoreeCloud Mesh, and GoreeCloud Identity",
    "45 verified GoreeCloud products across nine functional product groups",
    "productivity and organization",
    "storage, media, and library",
    "communication and discovery",
    "devices and interface",
    "platform and operations",
    "developer and intelligence",
    "home, health, and personal systems",
    "infrastructure and edge products",
    "public experience",
    "GoreeCloud Health, Reader, Router OS, Social, Home, and Home Security",
    "without turning portfolio membership into a Stable or production claim",
    "14 registered static website packages",
    "GoreeCloud/goreecloud-static-websites",
    "Labs is integrated as the fourteenth authoritative-main package",
    "production acceptance, and indexing release remain separate gates",
)
for needle in required:
    if needle not in html:
        raise SystemExit(f"required current Blog content missing: {needle}")

stale_current_claims = (
    "27 applications across seven functional groups",
    "27 Suite applications across seven functional groups",
    "38 applications across",
    "38 Suite applications",
    "Glaze UI 2.1",
    "GLAZE UI 2.1",
    "identity.goreecloud.com",
    "13 registered static website packages",
    "Labs remains separate candidate scope",
)
for stale in stale_current_claims:
    if stale in html:
        raise SystemExit(f"superseded current-state Blog claim remains public: {stale}")

for needle in (
    "Content-Security-Policy:",
    "frame-ancestors 'none'",
    "Permissions-Policy:",
    "X-Content-Type-Options: nosniff",
):
    if needle not in headers:
        raise SystemExit(f"required Blog security header missing: {needle}")

for prohibited in ("google-analytics", "googletagmanager", "segment.com"):
    if prohibited in html.lower():
        raise SystemExit(f"prohibited Blog runtime dependency: {prohibited}")

print("GoreeCloud Blog current V1.3, seven-system, 45-product, nine-group, and 14-package public direction validated")
