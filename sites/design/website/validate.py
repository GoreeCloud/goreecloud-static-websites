#!/usr/bin/env python3
from pathlib import Path
import hashlib
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "website"
DIST = SITE / "dist"
IDENTITY = ROOT / "assets" / "identity" / "official" / "facet"
GLAZE_VERSION = "1.3.0"
GLAZE_REVISION = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
CANONICAL_SHA256 = "82d3bdc331a96593873ca4d327e3b46d561d1ca96e653cef71e0c5e42fa1a31c"

for name in (
    "index.html", "404.html", "site.css", "identity.css", "site.js",
    "v1.3-site.css", "_headers", "build.py"
):
    if not (SITE / name).is_file():
        raise SystemExit(f"missing Design Center source: {name}")

mark = IDENTITY / "glaze-ui-mark.svg"
if not mark.is_file() or hashlib.sha256(mark.read_bytes()).hexdigest() != CANONICAL_SHA256:
    raise SystemExit("synchronized Facet source missing or changed")

subprocess.run([sys.executable, str(SITE / "build.py")], cwd=ROOT, check=True)

required = (
    "index.html", "404.html", "_headers", "reference/v1-system-shell.html",
    "assets/site.css", "assets/identity.css", "assets/site.js",
    "assets/v1.3-site.css", "assets/glaze-ui-mark.svg", "assets/glaze.css",
    "assets/glaze.controls.css", "assets/glaze.expressive.css",
    "assets/glaze.formfactors.css", "assets/glaze.accessibility.css",
    "assets/glaze.color.css", "assets/glaze.motion.css", "assets/glaze.materials.css",
    "assets/glaze.layout.css", "assets/glaze.states.css",
)
for name in required:
    if not (DIST / name).is_file():
        raise SystemExit(f"missing Design Center build artifact: {name}")

if (DIST / "assets" / "glaze-ui-mark.svg").read_bytes() != mark.read_bytes():
    raise SystemExit("public Design Center identity asset drifted from Facet source")

html = (DIST / "index.html").read_text(encoding="utf-8")
not_found = (DIST / "404.html").read_text(encoding="utf-8")
headers = (DIST / "_headers").read_text(encoding="utf-8")
js = (DIST / "assets" / "site.js").read_text(encoding="utf-8")
v13 = (DIST / "assets" / "v1.3-site.css").read_text(encoding="utf-8")

for surface_name, surface in (("index", html), ("404", not_found)):
    for marker in (
        f'name="goreecloud-glaze-ui" content="{GLAZE_VERSION}"',
        f'name="goreecloud-glaze-source-revision" content="{GLAZE_REVISION}"',
        'data-glaze-version="1.3.0"',
        'data-glaze-ui="1.3.0"',
    ):
        if marker not in surface:
            raise SystemExit(f"{surface_name} missing V1.3 source anchor: {marker}")

for text in (
    "GLAZE UI V1.3 — Adaptive Resonance",
    "Current Official Stable · 1.3.0",
    "Neutral glass remains the material foundation",
    "Adaptive Expression",
    "Human Ergonomics",
    "Living Material 2.0",
    "Accessibility outranks expression.",
    "Design Center rendered acceptance pending",
    "source-migrated-rendered-acceptance-pending",
    GLAZE_REVISION,
):
    if text not in html:
        raise SystemExit(f"required V1.3 Design Center content missing: {text}")

for stale in (
    "Current Stable · GLAZE UI V1.1",
    "GLAZE UI V1.1 is GoreeCloud's current Stable",
    "Glaze UI 2.1",
    "glaze-ui-2.1.0.css",
    "data-glaze-ui=\"2.1.0\"",
):
    if stale in html + not_found:
        raise SystemExit(f"stale active Glaze publication marker remains: {stale}")

for marker in (
    "--v13-touch:48px",
    "--v13-touch-assisted:56px",
    "prefers-reduced-motion:reduce",
    "prefers-reduced-transparency:reduce",
    "prefers-contrast:more",
    "forced-colors:active",
    "pointer:coarse",
    "focus-visible",
    "grid-template-columns",
    "backdrop-filter",
):
    if marker not in v13:
        raise SystemExit(f"V1.3 consumer presentation marker missing: {marker}")

for surface_name, surface in (("index", html), ("404", not_found)):
    for asset in re.findall(r'(?:src|href)=["\'](/assets/[^"\']+)', surface):
        if not (DIST / asset.removeprefix("/")).is_file():
            raise SystemExit(f"{surface_name} references missing public asset: {asset}")

for remote in re.findall(r'(?:src|href)=["\'](https?://[^"\']+)', html + not_found):
    if not remote.startswith("https://github.com/GoreeCloud/goreecloud-glaze-ui"):
        raise SystemExit(f"unexpected remote Design Center link/resource: {remote}")

for directive in (
    "Content-Security-Policy:", "frame-ancestors 'none'", "Permissions-Policy:",
    "X-Content-Type-Options: nosniff",
):
    if directive not in headers:
        raise SystemExit(f"required security header missing: {directive}")

if "localStorage" not in js or "data-theme-choice" not in html:
    raise SystemExit("local appearance preference contract missing")

# The pending consumer-state marker above is the positive acceptance-state guard.
# Reject only unambiguously affirmative completion claims; do not reject truthful
# negative disclosures such as “not production visually accepted.”
for forbidden in (
    "Design Center V1.3 conformance passed",
    "production acceptance complete",
    'name="goreecloud-glaze-consumer-state" content="accepted"',
):
    if forbidden in html:
        raise SystemExit(f"unsupported Design Center acceptance claim: {forbidden}")

print(
    "GLAZE UI V1.3 Design Center source validation passed: exact Stable source anchor, "
    "current public release identity, accessibility/responsive consumer layer, current canonical Facet identity, "
    "and explicit rendered/production acceptance boundary"
)
