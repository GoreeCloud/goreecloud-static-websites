#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "website"
DIST = SOURCE / "dist"
ICON = ROOT / "branding" / "wardveil-security-icon.svg"
GLAZE_ASSET = "v1.3-site.css"

if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir(parents=True)
(DIST / "assets").mkdir(parents=True)

for name in ("index.html", "404.html", "_headers", GLAZE_ASSET):
    shutil.copy2(SOURCE / name, DIST / name)
for name in ("site.css", "site.js"):
    shutil.copy2(SOURCE / name, DIST / "assets" / name)
shutil.copy2(ICON, DIST / "assets" / "wardveil-security-icon.svg")
print(
    f"Built {DIST.relative_to(ROOT)} with canonical Wardveil identity "
    "and GLAZE UI V1.3 / 1.3.0 source-migrated consumer surface; "
    "rendered and production acceptance remain separate"
)
