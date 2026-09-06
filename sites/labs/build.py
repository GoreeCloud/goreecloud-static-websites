#!/usr/bin/env python3
"""Build the isolated Cloudflare Pages artifact for the GoreeCloud six-product center."""
from __future__ import annotations
from pathlib import Path
import shutil
import sys

SITE = Path(__file__).resolve().parent
DIST = SITE / "dist"
sys.path.insert(0, str(SITE / "scripts"))
from glaze_v1 import FILES as GLAZE_FILES, install_glaze  # noqa: E402

SITE_FILES = ("index.html", "404.html", "labs.css", "_headers", "robots.txt")
SHARED_FILES = ("css/site-v1.1.css", "js/main.js", "js/theme-init.js", "assets/goreecloud-logo.svg")


def main() -> int:
    try:
        for name in SITE_FILES:
            path = SITE / name
            if not path.is_file() or path.is_symlink():
                raise ValueError(f"invalid site source: {name}")
        for name in SHARED_FILES:
            path = SITE / name
            if not path.is_file() or path.is_symlink():
                raise ValueError(f"invalid shared source: {name}")
        if DIST.exists():
            if DIST.is_symlink():
                raise ValueError("dist must not be a symlink")
            shutil.rmtree(DIST)
        DIST.mkdir()
        for name in SITE_FILES:
            destination = DIST / ("css/labs.css" if name == "labs.css" else name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SITE / name, destination)
        for name in SHARED_FILES:
            destination = DIST / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SITE / name, destination)
        install_glaze(DIST / "css" / "glaze-v1")
    except (OSError, ValueError) as exc:
        print(f"Labs build failed: {exc}")
        return 1
    print(f"Built Labs product-center artifact: {sum(1 for p in DIST.rglob('*') if p.is_file())} files -> {DIST}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
