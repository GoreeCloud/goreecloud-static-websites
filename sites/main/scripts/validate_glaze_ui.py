#!/usr/bin/env python3
from pathlib import Path
import sys

from glaze_v1_4 import (
    GLAZE_CONSUMER_STATE,
    GLAZE_ENTRYPOINT,
    GLAZE_ENTRYPOINT_BLOB,
    GLAZE_PROMOTION_REVISION,
    GLAZE_VERSION,
    git_blob_sha,
    load_lock,
    render_v1_4_html,
)

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / name for name in ("index.html", "repositories.html", "privacy.html", "security.html", "404.html")]
ENTRYPOINT = ROOT / "css" / GLAZE_ENTRYPOINT
CONSUMER = ROOT / "css" / "glaze-v1.4-main.css"
POLISH = ROOT / "css" / "glaze-polish.css"
CONFORMANCE = ROOT / "docs" / "glaze-ui-conformance.md"
errors: list[str] = []

try:
    load_lock(ROOT)
except (OSError, ValueError) as exc:
    errors.append(str(exc))

if not ENTRYPOINT.is_file() or ENTRYPOINT.is_symlink():
    errors.append("exact GLAZE UI V1.4 Stable source entrypoint is missing or unsafe")
elif git_blob_sha(ENTRYPOINT.read_bytes()) != GLAZE_ENTRYPOINT_BLOB:
    errors.append("committed GLAZE UI V1.4 entrypoint is not byte-identical to canonical Stable source")

for page in PAGES:
    if not page.is_file():
        errors.append(f"missing Main public page: {page.name}")
        continue
    source = page.read_text(encoding="utf-8")
    try:
        text = render_v1_4_html(source)
    except ValueError as exc:
        errors.append(f"{page.name} cannot be projected to V1.4: {exc}")
        continue
    required = (
        f'data-glaze-version="{GLAZE_VERSION}"',
        f'name="goreecloud-glaze-ui" content="{GLAZE_VERSION}"',
        f'name="goreecloud-glaze-source-revision" content="{GLAZE_PROMOTION_REVISION}"',
        f'name="goreecloud-glaze-consumer-state" content="{GLAZE_CONSUMER_STATE}"',
        f'{GLAZE_ENTRYPOINT}" data-glaze-ui="{GLAZE_VERSION}"',
        "css/glaze-v1.4-main.css",
        'data-glaze-optical-v14="adaptive-optical"',
        "glaze-canvas",
        'name="viewport"',
    )
    for marker in required:
        if marker not in text:
            errors.append(f"{page.name} missing V1.4 runtime marker: {marker}")
    for stale in (
        'data-glaze-version="1.3.0"',
        'goreecloud-glaze-ui" content="1.3.0"',
        'glaze-v1.3.0.css" data-glaze-ui="1.3.0"',
        'data-glaze-ui="2.1.0"',
        'data-glaze-ui="2.2.0"',
        "glaze-ui-2.1.0.css",
        "glaze-2.2.0.css",
    ):
        if stale in text:
            errors.append(f"{page.name} projected artifact still activates superseded Glaze: {stale}")
    if "raw.githubusercontent.com" in text:
        errors.append(f"{page.name} must not load remote GLAZE UI at runtime")
    if "glaze-v1.4.0.mjs" in text or "glaze-v1.4-optical-engine.mjs" in text:
        errors.append(f"{page.name} must not load the optional V1.4 Optical Engine without a separate runtime review")

consumer = CONSUMER.read_text(encoding="utf-8") if CONSUMER.is_file() else ""
for marker in (
    "GLAZE UI V1.4 consumer refinement",
    "grid-template-areas: \"brand navigation actions\"",
    "#goreecloud-analytics-consent",
    "@media (max-width: 1040px)",
    "prefers-reduced-motion",
    "prefers-reduced-transparency",
    "forced-colors: active",
):
    if marker not in consumer:
        errors.append(f"Main V1.4 navigation/consumer adaptation missing: {marker}")

polish = POLISH.read_text(encoding="utf-8") if POLISH.is_file() else ""
for marker in (
    ":focus-visible",
    "@media (pointer:coarse)",
    "prefers-reduced-motion",
    "prefers-reduced-transparency",
    "prefers-contrast: more",
    "forced-colors: active",
    "@media print",
):
    if marker not in polish:
        errors.append(f"Inherited Main accessibility adaptation missing: {marker}")

conformance = CONFORMANCE.read_text(encoding="utf-8") if CONFORMANCE.is_file() else ""
for marker in (
    "Target GLAZE UI version: **V1.4 / 1.4.0 Stable**",
    GLAZE_PROMOTION_REVISION,
    GLAZE_ENTRYPOINT,
    "same-origin",
    "optional V1.4 JavaScript Optical Engine",
    "Rendered, accessibility, deployment, and production acceptance: **Separate gates**",
):
    if marker not in conformance:
        errors.append(f"V1.4 conformance record missing: {marker}")

if errors:
    print("GLAZE UI V1.4 consumer validation failed:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
print("GLAZE UI V1.4 consumer contract passed for all Main public runtime surfaces.")
