#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "website"
DIST = SOURCE / "dist"
IDENTITY = ROOT / "assets" / "identity" / "official" / "facet"
REFERENCE = ROOT / "reference"

if DIST.exists():
    shutil.rmtree(DIST)
(DIST / "assets").mkdir(parents=True)
(DIST / "reference").mkdir(parents=True)

for name in ("index.html", "404.html", "_headers"):
    shutil.copy2(SOURCE / name, DIST / name)

for name in ("site.css", "identity.css", "site.js", "v1.3-site.css"):
    shutil.copy2(SOURCE / name, DIST / "assets" / name)

# The Design Center publishes generic GoreeCloud/Glaze foundations plus a
# repository-local V1.3 consumer presentation layer. The canonical GLAZE UI
# V1.3 source remains GoreeCloud/goreecloud-glaze-ui and is identified by an
# exact revision in the HTML/acceptance record; this build must not pretend
# that a local website stylesheet is the canonical Stable entrypoint.
for name in (
    "glaze.css",
    "glaze.controls.css",
    "glaze.expressive.css",
    "glaze.formfactors.css",
    "glaze.accessibility.css",
    "glaze.color.css",
    "glaze.motion.css",
    "glaze.materials.css",
    "glaze.layout.css",
    "glaze.states.css",
):
    shutil.copy2(ROOT / "css" / name, DIST / "assets" / name)

shutil.copy2(IDENTITY / "glaze-ui-mark.svg", DIST / "assets" / "glaze-ui-mark.svg")
shutil.copy2(REFERENCE / "v1-system-shell.html", DIST / "reference" / "v1-system-shell.html")

print(
    f"Built {DIST.relative_to(ROOT)} as a GLAZE UI V1.3 / 1.3.0 consumer surface; "
    "rendered/native, accessibility, performance, rollback, and production acceptance remain independent gates"
)
