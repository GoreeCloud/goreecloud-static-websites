#!/usr/bin/env python3
"""Build the isolated Privacy Center artifact with pinned GLAZE UI V1.1."""
from pathlib import Path
import shutil
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from glaze_v1 import install_glaze  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "website"
DIST = SOURCE / "dist"
ICON = ROOT / "branding" / "privacy-shield" / "privacy-shield-icon.svg"

if DIST.exists():
    if DIST.is_symlink():
        raise SystemExit("Privacy Center dist must not be a symlink")
    shutil.rmtree(DIST)
(DIST / "assets").mkdir(parents=True)

for name in ("index.html", "404.html", "_headers"):
    source = SOURCE / name
    if not source.is_file() or source.is_symlink():
        raise SystemExit(f"invalid Privacy Center source: {name}")
    shutil.copy2(source, DIST / name)
for name in ("site.css", "site-polish.css", "site.js"):
    source = SOURCE / name
    if not source.is_file() or source.is_symlink():
        raise SystemExit(f"invalid Privacy Center asset: {name}")
    shutil.copy2(source, DIST / "assets" / name)
if not ICON.is_file() or ICON.is_symlink():
    raise SystemExit("invalid canonical Privacy Shield identity asset")
shutil.copy2(ICON, DIST / "assets" / "privacy-shield-icon.svg")
install_glaze(DIST / "assets" / "glaze-v1")
print(f"Built {DIST.relative_to(REPO_ROOT)} with canonical Privacy Shield identity and pinned GLAZE UI V1.1")
