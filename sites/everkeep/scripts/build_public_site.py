#!/usr/bin/env python3
"""Build the isolated Continuity Center artifact with pinned GLAZE UI V1.1."""
from pathlib import Path
import shutil
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from glaze_v1 import install_glaze  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "website"
DIST = SOURCE / "dist"
FILES = {
    SOURCE / "index.html": DIST / "index.html",
    SOURCE / "404.html": DIST / "404.html",
    SOURCE / "style.css": DIST / "style.css",
    SOURCE / "site-polish.css": DIST / "site-polish.css",
    SOURCE / "_headers": DIST / "_headers",
    SOURCE / "robots.txt": DIST / "robots.txt",
    SOURCE / "sitemap.xml": DIST / "sitemap.xml",
    ROOT / "assets" / "everkeep.svg": DIST / "assets" / "everkeep.svg",
}

if DIST.exists():
    if DIST.is_symlink():
        raise SystemExit("Continuity Center dist must not be a symlink")
    shutil.rmtree(DIST)
for src, dst in FILES.items():
    if not src.is_file() or src.is_symlink():
        raise SystemExit(f"invalid public source: {src.relative_to(ROOT)}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
install_glaze(DIST / "assets" / "glaze-v1")
print(f"Built Continuity Center V1.1 artifact: {len(FILES)} reviewed files plus pinned GLAZE bundle -> {DIST.relative_to(REPO_ROOT)}")
