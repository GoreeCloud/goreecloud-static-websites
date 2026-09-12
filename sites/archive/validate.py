#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
README = ROOT / "README.md"

for path in (HTML, README):
    if not path.is_file():
        raise SystemExit(f"missing Archive contract file: {path.name}")

html = HTML.read_text(encoding="utf-8")
readme = README.read_text(encoding="utf-8")

current_match = re.search(r'<section id="current"\b.*?</section>', html, flags=re.DOTALL)
if not current_match:
    raise SystemExit("Archive current-boundary section is missing")
current = current_match.group(0)

timeline_match = re.search(r'<section id="timeline"\b.*?</section>', html, flags=re.DOTALL)
if not timeline_match:
    raise SystemExit("Archive historical timeline is missing")
timeline = timeline_match.group(0)

for marker in (
    "Current boundary · September 12, 2026",
    "GLAZE UI V1.3 / 1.3.0",
    "14 registered packages",
    "Labs is integrated as the fourteenth authoritative-main package",
    "Cloudflare source cutover",
    "exact deployed-revision verification",
    "canonical-domain browser acceptance",
    "production acceptance",
    "indexing release",
    "GoreeCloud Manager, Privacy Shield, Wardveil Security, Everkeep, GLAZE UI, GoreeCloud Mesh, and GoreeCloud Identity",
):
    if marker not in current:
        raise SystemExit(f"Archive current boundary missing current authority marker: {marker}")

for stale in (
    "13 registered packages",
    "Labs remains separate candidate scope",
    "Labs remains separate candidate",
):
    if stale in current:
        raise SystemExit(f"Archive current boundary still publishes superseded state: {stale}")

# Preserve the earlier 13-package state only as explicit historical evidence.
for historical in (
    "September 2026 · Static-site consolidation",
    "The live authoritative scope contains 13 registered packages.",
    "legacy source copies are transitional until cutover and exact deployment verification are complete",
):
    if historical not in timeline:
        raise SystemExit(f"Archive historical website-migration evidence is missing: {historical}")

for marker in (
    "14 authoritative website packages",
    "Historical Archive entries may preserve earlier package counts",
    "Labs is integrated as the fourteenth authoritative-main package",
):
    if marker not in readme:
        raise SystemExit(f"Archive README missing authority-boundary marker: {marker}")

print(
    "GoreeCloud Archive current-truth validation passed: current boundary uses the 14-package authority, "
    "Labs deployment/indexing remain independently gated, and the earlier 13-package state remains preserved only as history."
)
