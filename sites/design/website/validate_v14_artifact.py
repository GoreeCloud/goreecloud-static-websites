#!/usr/bin/env python3
"""Validate the exact built GoreeCloud Design Center GLAZE UI V1.4 artifact."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

SITE = Path(__file__).resolve().parent
DIST = SITE / "dist"
VERSION = "1.4.0"
REVISION = "84cb3db4884042f0fa25ed6d475a127fb110f596"
ENTRY = "glaze-v1.4.0.css"
ENTRY_BLOB = "d48a9bc317090d152799769271de0fb4325494c4"


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data, usedforsecurity=False).hexdigest()


for name in (
    "index.html", "404.html", "_headers", "assets/site.css", "assets/identity.css", "assets/site.js",
    "assets/v1.3-site.css", "assets/glaze-ui-mark.svg", f"assets/{ENTRY}", "reference/v1-system-shell.html",
):
    path = DIST / name
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"missing or unsafe Design Center V1.4 artifact file: {name}")

entry = DIST / "assets" / ENTRY
if blob_sha(entry) != ENTRY_BLOB:
    raise SystemExit("Design Center V1.4 entrypoint Git blob mismatch")

index = (DIST / "index.html").read_text(encoding="utf-8")
not_found = (DIST / "404.html").read_text(encoding="utf-8")
headers = (DIST / "_headers").read_text(encoding="utf-8")
for page_name, page in (("index.html", index), ("404.html", not_found)):
    for marker in (
        'data-glaze-version="1.4.0"',
        'name="goreecloud-glaze-ui" content="1.4.0"',
        f'name="goreecloud-glaze-source-revision" content="{REVISION}"',
        'name="goreecloud-glaze-consumer-state" content="build-migrated-rendered-acceptance-pending"',
        '/assets/glaze-v1.4.0.css',
        'data-glaze-ui="1.4.0"',
        'data-glaze-consumer-adaptation="1.3-inherited"',
    ):
        if marker not in page:
            raise SystemExit(f"{page_name} missing Design Center V1.4 publication marker: {marker}")
    for stale in (
        'name="goreecloud-glaze-ui" content="1.3.0"',
        'data-glaze-version="1.3.0"',
        'data-glaze-ui="1.3.0"',
        "GLAZE UI V1.3 — Adaptive Resonance",
        "Current Official Stable · 1.3.0",
    ):
        if stale in page:
            raise SystemExit(f"{page_name} still exposes superseded active Design Center publication state: {stale}")

for marker in (
    "GLAZE UI V1.4 — Optical Intelligence",
    "Current Official Stable · 1.4.0",
    "Optical Intelligence.",
    "V1.4.0 is consumer-eligible",
):
    if marker not in index:
        raise SystemExit(f"Design Center V1.4 public identity missing: {marker}")

for directive in (
    "Content-Security-Policy:", "frame-ancestors 'none'", "Permissions-Policy:",
    "X-Content-Type-Options: nosniff", "Strict-Transport-Security: max-age=31536000",
):
    if directive not in headers:
        raise SystemExit(f"required Design Center security header missing: {directive}")

for surface_name, surface in (("index", index), ("404", not_found)):
    for asset in re.findall(r'(?:src|href)=["\'](/assets/[^"\']+)', surface):
        if not (DIST / asset.removeprefix("/")).is_file():
            raise SystemExit(f"{surface_name} references missing Design Center artifact asset: {asset}")

print("Design Center exact GLAZE UI V1.4 artifact validation passed")
