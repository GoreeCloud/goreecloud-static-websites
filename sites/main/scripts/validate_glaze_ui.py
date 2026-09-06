#!/usr/bin/env python3
"""Validate Main's source-side GLAZE UI V1.1 consumer contract."""
from __future__ import annotations

from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from glaze_v1 import GLAZE_SOURCE_REVISION, GLAZE_VERSION  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "repositories.html", "privacy.html", "security.html", "404.html")
errors: list[str] = []


def has_class_token(text: str, token: str) -> bool:
    return any(token in match.group(1).split() for match in re.finditer(r'class\s*=\s*["\']([^"\']*)["\']', text, re.I))


for name in PAGES:
    path = ROOT / name
    if not path.is_file():
        errors.append(f"missing public page: {name}")
        continue
    text = path.read_text(encoding="utf-8")
    for marker in (
        'data-glaze-version="1.1"',
        f'name="goreecloud-glaze-ui" content="{GLAZE_VERSION}"',
        f'data-glaze-ui="{GLAZE_VERSION}"',
        '/assets/glaze-v1/glaze-v1.1.0.css',
        '/css/site-v1.1.css',
    ):
        if marker not in text:
            errors.append(f"{name} missing V1.1 marker: {marker}")
    if not has_class_token(text, "glaze-canvas"):
        errors.append(f"{name} missing glaze-canvas class token")
    for forbidden in ('data-glaze-ui="2.', 'name="goreecloud-glaze-ui" content="2.', 'glaze-ui-2.', 'glaze-2.'):
        if forbidden in text:
            errors.append(f"{name} still activates pre-reset GLAZE source: {forbidden}")
    if "raw.githubusercontent.com" in text:
        errors.append(f"{name} must not load remote GLAZE resources")

css_path = ROOT / "css" / "site-v1.1.css"
css = css_path.read_text(encoding="utf-8") if css_path.is_file() else ""
for marker in (
    "GLAZE UI V1.1 / 1.1.0",
    "min-height: 48px",
    "@media (max-width: 980px)",
    "@media (max-width: 700px)",
    "prefers-reduced-motion: reduce",
    "prefers-reduced-transparency: reduce",
    "forced-colors: active",
):
    if marker not in css:
        errors.append(f"Main V1.1 consumer stylesheet missing marker: {marker}")

readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").is_file() else ""
for marker in ("GLAZE UI V1.1", GLAZE_SOURCE_REVISION, "production acceptance"):
    if marker not in readme:
        errors.append(f"Main README missing V1.1 governance marker: {marker}")

if errors:
    print("Main GLAZE UI V1.1 source validation failed:")
    for error in errors:
        print(f"  - {error}")
    raise SystemExit(1)
print(f"Main source targets GLAZE UI V1.1/{GLAZE_VERSION} at immutable revision {GLAZE_SOURCE_REVISION}; deployment and conformance acceptance remain separate.")
