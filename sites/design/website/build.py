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

for name in ("site.css", "identity.css", "site.js"):
    shutil.copy2(SOURCE / name, DIST / "assets" / name)

# Publish only the generic foundations used by the public reference surface and the
# official V1.1 entrypoint/layers and inherited V1 structural layers. Former product-release and candidate assets are not
# part of the current public artifact.
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
    "glaze-v1.1.0.css",
    "glaze-v1.1.css",
    "glaze-v1.1-appearance.css",
    "glaze-v1.0.0.css",
    "glaze-v1.foundation.css",
    "glaze-v1.components.css",
    "glaze-v1.components.adaptive.css",
    "glaze-v1.components.runtime.css",
    "glaze-v1.structure.css",
    "glaze-v1.overlay.css",
    "glaze-v1.advanced.css",
    "glaze-v1.visual-refinement.css",
    "glaze-v1.optical-reachability.css",
):
    shutil.copy2(ROOT / "css" / name, DIST / "assets" / name)

shutil.copy2(IDENTITY / "glaze-ui-mark.svg", DIST / "assets" / "glaze-ui-mark.svg")
shutil.copy2(REFERENCE / "v1-system-shell.html", DIST / "reference" / "v1-system-shell.html")

print(
    f"Built {DIST.relative_to(ROOT)} from the official GLAZE UI V1.1 Stable source "
    "with an isolated current V1.1 public publication boundary"
)
