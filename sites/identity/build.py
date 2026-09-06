#!/usr/bin/env python3
"""Build Identity Center as an isolated GLAZE UI V1.1 Pages artifact."""
from __future__ import annotations

from pathlib import Path
import shutil
import sys

SITE = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from glaze_v1 import install_glaze  # noqa: E402

DIST = SITE / "dist"
PUBLIC = ("index.html", "404.html", "_headers", "style.css", "app.js", "robots.txt", "sitemap.xml")
ASSETS = ("assets/identity.svg",)


def main() -> int:
    if DIST.exists():
        if DIST.is_symlink():
            raise SystemExit("Identity Center build refused: dist must not be a symlink")
        shutil.rmtree(DIST)
    DIST.mkdir()

    for relative in (*PUBLIC, *ASSETS):
        source = SITE / relative
        if not source.is_file() or source.is_symlink():
            raise SystemExit(f"Identity Center build refused: required source is not a regular file: {relative}")
        destination = DIST / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    install_glaze(DIST / "assets" / "glaze-v1")
    print("Built isolated Identity Center artifact with pinned GLAZE UI V1.1 source and bounded Stable workaround")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
