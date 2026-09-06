#!/usr/bin/env python3
"""Build the Main GoreeCloud website as an isolated GLAZE UI V1.1 Pages artifact."""
from __future__ import annotations

from pathlib import Path
import shutil
import sys

SITE = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from glaze_v1 import install_glaze  # noqa: E402

DIST = SITE / "dist"
PUBLIC = (
    "404.html",
    "_headers",
    "googlea0a636fd5dafd9e0.html",
    "index.html",
    "privacy.html",
    "repositories.html",
    "robots.txt",
    "security.html",
    "site.webmanifest",
    "sitemap.xml",
    ".well-known/security.txt",
    "assets/goreecloud-logo.svg",
    "css/site-v1.1.css",
    "js/main.js",
    "js/theme-init.js",
)


def main() -> int:
    if len(PUBLIC) != len(set(PUBLIC)):
        raise SystemExit("Main build refused: public allowlist contains duplicates")

    if DIST.exists():
        if DIST.is_symlink():
            raise SystemExit("Main build refused: dist must not be a symlink")
        shutil.rmtree(DIST)
    DIST.mkdir()

    for relative in PUBLIC:
        source = SITE / relative
        if not source.is_file() or source.is_symlink():
            raise SystemExit(f"Main build refused: required source is not a regular file: {relative}")
        destination = DIST / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    install_glaze(DIST / "assets" / "glaze-v1")
    files = sum(1 for path in DIST.rglob("*") if path.is_file())
    print(f"Built isolated Main V1.1 artifact: {files} files -> {DIST.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
