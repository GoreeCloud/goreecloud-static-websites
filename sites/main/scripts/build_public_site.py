#!/usr/bin/env python3
"""Build the exact allowlisted Cloudflare Pages artifact for www.goreecloud.com.

The canonical repository contains migration provenance and historical source that is
not part of the public website. Only the files listed here plus the generated pinned
GLAZE UI V1.1 bundle can enter dist/.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from glaze_v1 import FILES as GLAZE_FILES, install_glaze  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

PUBLIC_ROOT_FILES = (
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
)
PUBLIC_ASSET_FILES = ("assets/goreecloud-logo.svg",)
PUBLIC_STYLE_FILES = ("css/site-v1.1.css",)
PUBLIC_SCRIPT_FILES = ("js/main.js", "js/theme-init.js")
PUBLIC_FILES = (*PUBLIC_ROOT_FILES, *PUBLIC_ASSET_FILES, *PUBLIC_STYLE_FILES, *PUBLIC_SCRIPT_FILES)
GENERATED_GLAZE_FILES = tuple(f"assets/glaze-v1/{name}" for name in GLAZE_FILES)


def fail(message: str) -> int:
    print(f"Public-site build failed: {message}")
    return 1


def main() -> int:
    try:
        if len(PUBLIC_FILES) != len(set(PUBLIC_FILES)):
            return fail("public file allowlist contains duplicates")
        for relative in PUBLIC_FILES:
            source = ROOT / relative
            if not source.is_file() or source.is_symlink():
                return fail(f"invalid allowlisted public source: {relative}")

        if DIST.exists():
            if DIST.is_symlink():
                return fail("dist must not be a symlink")
            shutil.rmtree(DIST)
        DIST.mkdir()

        for relative in PUBLIC_FILES:
            source = ROOT / relative
            destination = DIST / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        install_glaze(DIST / "assets" / "glaze-v1")
    except (OSError, ValueError) as exc:
        return fail(str(exc))

    files = [path for path in DIST.rglob("*") if path.is_file()]
    print(f"Built isolated Main artifact: {len(files)} files -> dist/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
