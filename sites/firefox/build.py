#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
FILES = ["index.html", "404.html", "site.css", "site.js", "_headers", "robots.txt", "sitemap.xml"]

if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir()
for name in FILES:
    shutil.copy2(ROOT / name, DIST / name)
shutil.copytree(ROOT / "assets", DIST / "assets")
print(f"Built {DIST}")
