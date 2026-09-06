#!/usr/bin/env python3
"""Validate Roadmap truth, identity, and source-specific public contract."""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parent
for name in ("index.html", "404.html", "site.css", "site.js", "build.py", "_headers", "assets/goreecloud-logo.svg"):
    if not (ROOT / name).is_file():
        raise SystemExit(f"missing roadmap site file: {name}")

html = (ROOT / "index.html").read_text(encoding="utf-8")
error_html = (ROOT / "404.html").read_text(encoding="utf-8")
script = (ROOT / "site.js").read_text(encoding="utf-8")
headers = (ROOT / "_headers").read_text(encoding="utf-8")

for needle in (
    "Public Development Roadmap",
    "September 6, 2026",
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
    "GoreeCloud Manager",
    "GoreeCloud File Manager",
    "GoreeCloud Maps",
    "GoreeCloud App Store",
    "Seven Integral Platform Systems",
    "GLAZE UI V1.1 / 1.1.0",
    "GoreeCloud/goreecloud-static-websites",
    "Controlled GLAZE UI V1.1 website adoption",
    "Central Cloudflare source cutover",
    "id.goreecloud.com",
    "Missing canonical product artwork",
    "Evidence over labels",
    "Authority stays explicit",
):
    if needle not in html:
        raise SystemExit(f"required roadmap content missing: {needle}")

for page_name, page in (("index", html), ("404", error_html)):
    for needle in (
        'data-glaze-version="1.1"',
        'name="goreecloud-glaze-ui" content="1.1.0"',
        'data-glaze-ui="1.1.0"',
        '/assets/glaze-v1/glaze-v1.1.0.css',
        'glaze-canvas',
    ):
        if needle not in page:
            raise SystemExit(f"{page_name} missing GLAZE UI V1.1 marker: {needle}")
    if '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">' not in page:
        raise SystemExit(f"{page_name} missing canonical GoreeCloud favicon")

for needle in (
    '<img src="/assets/goreecloud-logo.svg" width="32" height="32" alt="">',
    '<span class="brand-name">GoreeCloud <span>Roadmap</span></span>',
):
    if needle not in html:
        raise SystemExit(f"roadmap visible canonical identity missing: {needle}")

logo = ROOT / "assets/goreecloud-logo.svg"
raw = logo.read_bytes()
actual_blob = hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()
if actual_blob != "082936062de7839148db89ea3ab4e86ff71341b0":
    raise SystemExit(f"roadmap GoreeCloud logo drifted from canonical branding asset: {actual_blob}")

for stale in (
    'name="goreecloud-glaze-ui" content="2.1.0"',
    'data-glaze-ui="2.1.0"',
    'href="/glaze-ui-2.1.0.css"',
    "Ten independently deployed public destinations",
    "Six substantive platform systems",
    "Identity Center is the eleventh official first-party surface",
    "Glaze UI 2.1.0 is the current Stable production design target",
    "official websites consume Glaze UI 2.1 Stable directly",
    "identity.goreecloud.com",
    "the five substantive platform systems",
    "Gitea is the selected permanent authoritative source-control",
    "Complete Gitea independence",
):
    if stale in html:
        raise SystemExit(f"superseded roadmap direction remains public: {stale}")

if "dataset.glzAppearance" not in script or "data-glz-appearance" not in script:
    raise SystemExit("Roadmap JavaScript is missing the V1.1 appearance contract")
if "dataset.theme" in script:
    raise SystemExit("Roadmap JavaScript still mutates the pre-reset theme attribute")

for needle in ("Content-Security-Policy:", "frame-ancestors 'none'", "Permissions-Policy:", "X-Content-Type-Options: nosniff"):
    if needle not in headers:
        raise SystemExit(f"required security header missing: {needle}")
for prohibited in ("google-analytics", "googletagmanager", "fonts.googleapis.com", "segment.com"):
    if prohibited in html.lower():
        raise SystemExit(f"prohibited runtime dependency: {prohibited}")

print("GoreeCloud Roadmap current V1.1 target, seven-system platform model, canonical identity, and public truth validation passed")
