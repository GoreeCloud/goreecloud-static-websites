#!/usr/bin/env python3
from pathlib import Path
import sys

from glaze_v1_3 import (
    GLAZE_CONSUMER_STATE,
    GLAZE_ENTRYPOINT,
    GLAZE_ENTRYPOINT_BLOB,
    GLAZE_PROMOTION_REVISION,
    GLAZE_VERSION,
    git_blob_sha,
    load_lock,
)

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / name for name in ("index.html", "repositories.html", "privacy.html", "security.html", "404.html")]
ENTRYPOINT = ROOT / "css" / GLAZE_ENTRYPOINT
POLISH = ROOT / "css" / "glaze-polish.css"
CONFORMANCE = ROOT / "docs" / "glaze-ui-conformance.md"
errors: list[str] = []

try:
    load_lock(ROOT)
except (OSError, ValueError) as exc:
    errors.append(str(exc))

if not ENTRYPOINT.is_file() or ENTRYPOINT.is_symlink():
    errors.append("exact GLAZE UI V1.3 source entrypoint is missing or unsafe")
elif git_blob_sha(ENTRYPOINT.read_bytes()) != GLAZE_ENTRYPOINT_BLOB:
    errors.append("committed GLAZE UI V1.3 entrypoint is not byte-identical to canonical source")

for page in PAGES:
    if not page.is_file():
        errors.append(f"missing Main public page: {page.name}")
        continue
    text = page.read_text(encoding="utf-8")
    required = (
        f'data-glaze-version="{GLAZE_VERSION}"',
        f'name="goreecloud-glaze-ui" content="{GLAZE_VERSION}"',
        f'name="goreecloud-glaze-source-revision" content="{GLAZE_PROMOTION_REVISION}"',
        f'name="goreecloud-glaze-consumer-state" content="{GLAZE_CONSUMER_STATE}"',
        f'glaze-v1.3.0.css" data-glaze-ui="{GLAZE_VERSION}"',
        "glaze-canvas",
        'name="viewport"',
    )
    for marker in required:
        if marker not in text:
            errors.append(f"{page.name} missing V1.3 source marker: {marker}")
    for stale in (
        'data-glaze-ui="2.1.0"',
        'data-glaze-ui="2.2.0"',
        'goreecloud-glaze-ui" content="2.1.0"',
        'goreecloud-glaze-ui" content="2.2.0"',
        "glaze-ui-2.1.0.css",
        "glaze-2.2.0.css",
    ):
        if stale in text:
            errors.append(f"{page.name} still activates a superseded Glaze contract: {stale}")
    if "raw.githubusercontent.com" in text:
        errors.append(f"{page.name} must not load remote GLAZE UI at runtime")

polish = POLISH.read_text(encoding="utf-8") if POLISH.is_file() else ""
for marker in (
    "GLAZE UI V1.3 / 1.3.0 consumer layer",
    GLAZE_PROMOTION_REVISION,
    "--goreecloud-v13-touch:48px",
    "--goreecloud-v13-touch-assisted:56px",
    ":focus-visible",
    "@media (pointer:coarse)",
    "prefers-reduced-motion",
    "prefers-reduced-transparency",
    "prefers-contrast: more",
    "forced-colors: active",
    "@media print",
):
    if marker not in polish:
        errors.append(f"Main V1.3 consumer adaptation missing: {marker}")

conformance = CONFORMANCE.read_text(encoding="utf-8") if CONFORMANCE.is_file() else ""
for marker in (
    "Target GLAZE UI version: **V1.3 / 1.3.0 Stable**",
    GLAZE_PROMOTION_REVISION,
    GLAZE_ENTRYPOINT,
    "same-origin",
    "48px",
    "56px",
    "Rendered, accessibility, deployment, and production acceptance: **Separate gates**",
):
    if marker not in conformance:
        errors.append(f"V1.3 conformance record missing: {marker}")

if errors:
    print("GLAZE UI V1.3 source validation failed:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
print("GLAZE UI V1.3 source contract passed for all Main public HTML surfaces.")
