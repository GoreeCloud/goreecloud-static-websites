#!/usr/bin/env python3
"""Validate that Main dist/ is exactly the reviewed source plus pinned V1.4 CSS."""

from __future__ import annotations

from pathlib import Path
import sys

from build_public_site import DIST, PUBLIC_FILES, ROOT, render_public_html
from glaze_v1_4 import GLAZE_CONSUMER_STATE, GLAZE_ENTRYPOINT, GLAZE_PROMOTION_REVISION, GLAZE_VERSION, collect_glaze_css
from render_repository_portfolio import load_manifest

FORBIDDEN_NAMES = {".git", ".github", ".gitignore", "README.md", "SECURITY.md", "scripts", "docs"}


def main() -> int:
    errors: list[str] = []
    if not DIST.exists() or not DIST.is_dir() or DIST.is_symlink():
        print("Build artifact validation failed: dist/ is missing or unsafe; run build_public_site.py first.")
        return 1

    try:
        glaze_css = collect_glaze_css(ROOT)
        manifest = load_manifest(ROOT)
    except (OSError, ValueError) as exc:
        print(f"Build artifact validation failed: {exc}")
        return 1

    source_expected = {Path(relative) for relative in PUBLIC_FILES}
    glaze_expected = {Path("css") / name for name in glaze_css}
    expected = source_expected | glaze_expected
    actual = {path.relative_to(DIST) for path in DIST.rglob("*") if path.is_file()}

    for path in DIST.rglob("*"):
        if path.is_symlink():
            errors.append(f"Build artifact must not contain symlinks: {path.relative_to(DIST)}")
    for path in sorted(expected - actual):
        errors.append(f"Expected public file is missing from dist/: {path}")
    for path in sorted(actual - expected):
        errors.append(f"Unexpected file is present in dist/: {path}")

    for path in sorted(expected & actual):
        built = DIST / path
        if path.parts[:1] == ("css",) and path.name in glaze_css:
            expected_bytes = glaze_css[path.name]
        else:
            source = ROOT / path
            if not source.is_file() or source.is_symlink():
                errors.append(f"Allowlisted source is invalid: {path}")
                continue
            if path.suffix == ".html":
                expected_bytes = render_public_html(str(path), source.read_text(encoding="utf-8"), manifest).encode("utf-8")
            else:
                expected_bytes = source.read_bytes()
        if expected_bytes != built.read_bytes():
            errors.append(f"Built file differs from reviewed/pinned contract: {path}")

    for forbidden in sorted(FORBIDDEN_NAMES & {path.parts[0] for path in actual if path.parts}):
        errors.append(f"Repository-only content leaked into deploy artifact: {forbidden}")

    required = {
        Path("index.html"), Path("repositories.html"), Path("404.html"), Path("privacy.html"),
        Path("security.html"), Path("_headers"), Path("robots.txt"), Path("sitemap.xml"),
        Path("site.webmanifest"), Path(".well-known/security.txt"), Path("css/glaze.css"),
        Path("css/glaze-polish.css"), Path("css/glaze-v1.4-main.css"), Path("css") / GLAZE_ENTRYPOINT,
        Path("js/theme-init.js"), Path("js/main.js"), Path("js/telemetry.js"),
    }
    for path in sorted(required - actual):
        errors.append(f"Required runtime file is missing from dist/: {path}")

    for page in ("index.html", "repositories.html", "404.html", "privacy.html", "security.html"):
        path = DIST / page
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in (
            f'data-glaze-version="{GLAZE_VERSION}"',
            f'name="goreecloud-glaze-ui" content="{GLAZE_VERSION}"',
            f'name="goreecloud-glaze-source-revision" content="{GLAZE_PROMOTION_REVISION}"',
            f'name="goreecloud-glaze-consumer-state" content="{GLAZE_CONSUMER_STATE}"',
            f'{GLAZE_ENTRYPOINT}" data-glaze-ui="{GLAZE_VERSION}"',
            'css/glaze-v1.4-main.css',
            'data-glaze-optical-v14="adaptive-optical"',
        ):
            if marker not in text:
                errors.append(f"Built {page} missing V1.4 marker: {marker}")
        for stale in (
            'data-glaze-version="1.3.0"',
            'goreecloud-glaze-ui" content="1.3.0"',
            'glaze-v1.3.0.css" data-glaze-ui="1.3.0"',
            "glaze-ui-2.1.0.css",
            "glaze-2.2.0.css",
            'data-glaze-ui="2.1.0"',
            'data-glaze-ui="2.2.0"',
        ):
            if stale in text:
                errors.append(f"Built {page} still activates superseded Glaze: {stale}")

    if errors:
        print("Build artifact validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    total_bytes = sum((DIST / path).stat().st_size for path in actual)
    print(f"Build artifact validation passed: {len(actual)} files, {total_bytes} bytes, exact GLAZE UI V1.4 closure active.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
