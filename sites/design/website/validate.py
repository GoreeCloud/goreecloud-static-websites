#!/usr/bin/env python3
"""Validate the canonical Design Center GLAZE UI V1.4 source/build contract."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "website"
DIST = SITE / "dist"
IDENTITY = ROOT / "assets" / "identity" / "official" / "facet"
GLAZE_VERSION = "1.4.0"
GLAZE_REVISION = "84cb3db4884042f0fa25ed6d475a127fb110f596"
GLAZE_ENTRY = "glaze-v1.4.0.css"
GLAZE_ENTRY_BLOB = "d48a9bc317090d152799769271de0fb4325494c4"
CANONICAL_FACET_SHA256 = "82d3bdc331a96593873ca4d327e3b46d561d1ca96e653cef71e0c5e42fa1a31c"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)

for name in (
    "index.html", "404.html", "site.css", "identity.css", "site.js",
    "v1.3-site.css", "_headers", "build.py", "README.md", "glaze.lock.json"
):
    path = SITE / name
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"missing or unsafe Design Center source: {name}")

lock = json.loads((SITE / "glaze.lock.json").read_text(encoding="utf-8"))
for key, expected in {
    "version": GLAZE_VERSION,
    "lifecycle": "Stable",
    "repository": "GoreeCloud/goreecloud-glaze-ui",
    "stable_commit": GLAZE_REVISION,
    "entrypoint": GLAZE_ENTRY,
    "entrypoint_blob": GLAZE_ENTRY_BLOB,
    "consumer_state": "build-migrated-rendered-acceptance-pending",
}.items():
    if lock.get(key) != expected:
        raise SystemExit(f"invalid Design Center GLAZE UI V1.4 lock {key}: {lock.get(key)!r}")

readme = (SITE / "README.md").read_text(encoding="utf-8")
for marker in (
    "GLAZE UI V1.4", "1.4.0", "GoreeCloud/goreecloud-static-websites",
    "design.goreecloud.com", "goreecloud-design.pages.dev", GLAZE_REVISION,
    "python3 build.py", "dist", "legacy"
):
    if marker not in readme:
        raise SystemExit(f"Design Center README missing current publication guidance: {marker}")

mark = IDENTITY / "glaze-ui-mark.svg"
if not mark.is_file() or mark.is_symlink() or hashlib.sha256(mark.read_bytes()).hexdigest() != CANONICAL_FACET_SHA256:
    raise SystemExit("synchronized Facet source missing or changed")

source_html = (SITE / "index.html").read_text(encoding="utf-8")
source_404 = (SITE / "404.html").read_text(encoding="utf-8")
for surface_name, surface in (("index", source_html), ("404", source_404)):
    for marker in (
        'data-glaze-version="1.4.0"',
        'name="goreecloud-glaze-ui" content="1.4.0"',
        f'name="goreecloud-glaze-source-revision" content="{GLAZE_REVISION}"',
        'name="goreecloud-glaze-consumer-state" content="build-migrated-rendered-acceptance-pending"',
        'data-glaze-ui="1.4.0"',
        '/assets/glaze-v1.4.0.css',
        'data-glaze-consumer-adaptation="1.3-inherited"',
    ):
        if marker not in surface:
            raise SystemExit(f"{surface_name} missing V1.4 source marker: {marker}")
    for stale in (
        'name="goreecloud-glaze-ui" content="1.3.0"',
        'data-glaze-ui="1.3.0"',
        "GLAZE UI V1.3 — Adaptive Resonance",
        "Current Official Stable · 1.3.0",
    ):
        if stale in surface:
            raise SystemExit(f"{surface_name} retains stale active V1.3 publication marker: {stale}")

for text in (
    "GLAZE UI V1.4 — Optical Intelligence",
    "Current Official Stable · 1.4.0",
    "Optical Intelligence.",
    "Content-Aware Frost",
    "Semantic Blur Protection",
    "Environmental Fit",
    "Accessibility outranks expression.",
    "Design Center rendered acceptance pending",
    "build-migrated-rendered-acceptance-pending",
    GLAZE_REVISION,
):
    if text not in source_html:
        raise SystemExit(f"required V1.4 Design Center content missing: {text}")

subprocess.run([sys.executable, str(SITE / "build.py")], cwd=ROOT, check=True)

required = (
    "index.html", "404.html", "_headers", "reference/v1-system-shell.html",
    "assets/site.css", "assets/identity.css", "assets/site.js",
    "assets/v1.3-site.css", "assets/glaze-ui-mark.svg", f"assets/{GLAZE_ENTRY}",
)
for name in required:
    path = DIST / name
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"missing or unsafe Design Center build artifact: {name}")

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
        'data-glaze-version="1.4.0"',
        'data-glaze-ui="1.4.0"',
        'name="goreecloud-glaze-consumer-state" content="build-migrated-rendered-acceptance-pending"',
    ):
        if marker not in surface:
            raise SystemExit(f"{surface_name} missing built V1.4 source anchor: {marker}")

for marker in (
    "--v13-touch:48px", "--v13-touch-assisted:56px",
    "prefers-reduced-motion:reduce", "prefers-reduced-transparency:reduce",
    "prefers-contrast:more", "forced-colors:active", "pointer:coarse",
    "focus-visible", "grid-template-columns", "backdrop-filter",
):
    if marker not in v13:
        raise SystemExit(f"inherited Design Center consumer adaptation marker missing: {marker}")

for surface_name, surface in (("index", html), ("404", not_found)):
    for asset in re.findall(r'(?:src|href)=["\'](/assets/[^"\']+)', surface):
        if not (DIST / asset.removeprefix("/")).is_file():
            raise SystemExit(f"{surface_name} references missing public asset: {asset}")

for remote in re.findall(r'(?:src|href)=["\'](https?://[^"\']+)', html + not_found):
    if not remote.startswith("https://github.com/GoreeCloud/goreecloud-glaze-ui"):
        raise SystemExit(f"unexpected remote Design Center link/resource: {remote}")

for directive in (
    "Content-Security-Policy:", "frame-ancestors 'none'", "Permissions-Policy:",
    "X-Content-Type-Options: nosniff", "Strict-Transport-Security: max-age=31536000",
):
    if directive not in headers:
        raise SystemExit(f"required security header missing: {directive}")

if "localStorage" not in js or "data-theme-choice" not in html:
    raise SystemExit("local appearance preference contract missing")

for forbidden in (
    "Design Center V1.4 conformance passed", "production acceptance complete",
    'name="goreecloud-glaze-consumer-state" content="accepted"',
):
    if forbidden in html:
        raise SystemExit(f"unsupported Design Center acceptance claim: {forbidden}")

entry = DIST / "assets" / GLAZE_ENTRY
data = entry.read_bytes()
actual_blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data, usedforsecurity=False).hexdigest()
if actual_blob != GLAZE_ENTRY_BLOB:
    raise SystemExit(f"Design Center V1.4 entrypoint integrity mismatch: {actual_blob}")

seen: set[str] = set()
def visit(name: str) -> None:
    if name in seen:
        return
    path = DIST / "assets" / name
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"missing built GLAZE UI dependency: {name}")
    seen.add(name)
    for statement in re.findall(r"@import[^;]+;", path.read_text(encoding="utf-8"), flags=re.IGNORECASE):
        lowered = statement.lower()
        if "http://" in lowered or "https://" in lowered or "//" in statement:
            raise SystemExit(f"remote built GLAZE UI import is forbidden: {statement}")
        match = IMPORT_RE.search(statement)
        if not match:
            raise SystemExit(f"unsupported built GLAZE UI import syntax: {statement}")
        visit(match.group(1))
visit(GLAZE_ENTRY)
if "glaze-v1.3.0.css" not in seen:
    raise SystemExit("Design Center V1.4 inherited Stable dependency closure is incomplete")

print(
    "GLAZE UI V1.4 Design Center validation passed: exact Stable source/entrypoint, current Optical Intelligence publication identity, inherited responsive/accessibility adaptation, canonical Facet identity, security baseline, and fail-closed production boundary"
)
