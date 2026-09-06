#!/usr/bin/env python3
"""Validate a controlled GLAZE UI V1.1 static-site source and built artifact."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from glaze_v1 import FILES, GLAZE_SOURCE_REVISION, GLAZE_VERSION, validate_bundle  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("site", help="site package path relative to repository root")
args = parser.parse_args()
site = ROOT / args.site
dist = site / "dist"

errors: list[str] = []
for name in ("index.html", "404.html", "_headers"):
    if not (site / name).is_file():
        errors.append(f"missing required site source: {name}")

for page_name in ("index.html", "404.html"):
    path = site / page_name
    if not path.is_file():
        continue
    page = path.read_text(encoding="utf-8")
    for marker in (
        'data-glaze-version="1.1"',
        f'name="goreecloud-glaze-ui" content="{GLAZE_VERSION}"',
        f'data-glaze-ui="{GLAZE_VERSION}"',
        '/assets/glaze-v1/glaze-v1.1.0.css',
        'class="glaze-canvas"',
    ):
        if marker not in page:
            errors.append(f"{page_name} missing V1.1 source marker: {marker}")
    for forbidden in (
        'data-glaze-ui="2.',
        'name="goreecloud-glaze-ui" content="2.',
        'glaze-ui-2.',
        'glaze-2.',
    ):
        if forbidden in page:
            errors.append(f"{page_name} still activates pre-reset GLAZE source: {forbidden}")

headers = (site / "_headers").read_text(encoding="utf-8") if (site / "_headers").is_file() else ""
for marker in ("Content-Security-Policy:", "X-Content-Type-Options: nosniff", "frame-ancestors 'none'", "Permissions-Policy:"):
    if marker not in headers:
        errors.append(f"required security header missing: {marker}")

if not dist.is_dir():
    errors.append("built artifact directory is missing: dist/")
else:
    for name in ("index.html", "404.html", "_headers"):
        if not (dist / name).is_file():
            errors.append(f"built artifact missing required file: {name}")
    bundle_dir = dist / "assets" / "glaze-v1"
    bundle: dict[str, str] = {}
    for name in FILES:
        path = bundle_dir / name
        if not path.is_file() or path.is_symlink():
            errors.append(f"built artifact missing pinned GLAZE file: assets/glaze-v1/{name}")
            continue
        bundle[name] = path.read_text(encoding="utf-8")
    if len(bundle) == len(FILES):
        try:
            validate_bundle(bundle)
        except ValueError as exc:
            errors.append(str(exc))
    for path in dist.rglob("*"):
        if path.is_file() and ("glaze-ui-2." in path.name or path.name.startswith("glaze-2.")):
            errors.append(f"pre-reset GLAZE asset leaked into artifact: {path.relative_to(dist)}")

if errors:
    print(f"GLAZE UI V1.1 static-site validation failed for {args.site}:")
    for error in errors:
        print(f"  - {error}")
    raise SystemExit(1)

print(
    f"Validated {args.site} as a controlled GLAZE UI V1.1/{GLAZE_VERSION} consumer "
    f"using immutable source revision {GLAZE_SOURCE_REVISION}; production acceptance remains separate."
)
