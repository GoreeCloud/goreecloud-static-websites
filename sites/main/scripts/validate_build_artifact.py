#!/usr/bin/env python3
"""Validate that Main dist/ is exactly the reviewed source plus pinned V1.3 CSS."""

from __future__ import annotations

from pathlib import Path
import sys

from build_public_site import DIST, GENERATED_HTML, PUBLIC_FILES, ROOT
from glaze_v1_3 import GLAZE_CONSUMER_STATE, GLAZE_ENTRYPOINT, GLAZE_PROMOTION_REVISION, GLAZE_VERSION, collect_glaze_css
from normalize_homepage import normalize_homepage
from render_repository_portfolio import load_manifest, render_public_file

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
                rendered = source.read_text(encoding="utf-8")
                if str(path) in GENERATED_HTML:
                    rendered = render_public_file(str(path), rendered, manifest)
                    if str(path) == "index.html":
                        rendered = normalize_homepage(rendered)
                expected_bytes = rendered.encode("utf-8")
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
        Path("css/glaze-polish.css"), Path("css") / GLAZE_ENTRYPOINT, Path("js/theme-init.js"), Path("js/main.js"),
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
            f'glaze-v1.3.0.css" data-glaze-ui="{GLAZE_VERSION}"',
        ):
            if marker not in text:
                errors.append(f"Built {page} missing V1.3 marker: {marker}")
        for stale in ("glaze-ui-2.1.0.css", "glaze-2.2.0.css", 'data-glaze-ui="2.1.0"', 'data-glaze-ui="2.2.0"'):
            if stale in text:
                errors.append(f"Built {page} still activates superseded Glaze: {stale}")

    if errors:
        print("Build artifact validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    total_bytes = sum((DIST / path).stat().st_size for path in actual)
    print(f"Build artifact validation passed: {len(actual)} files, {total_bytes} bytes, exact GLAZE UI V1.3 closure active.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
