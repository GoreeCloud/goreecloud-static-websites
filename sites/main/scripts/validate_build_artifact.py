#!/usr/bin/env python3
"""Validate that dist/ contains exactly the intentional public website surface."""

from __future__ import annotations

from pathlib import Path
import sys

from build_public_site import DIST, GENERATED_HTML, PUBLIC_FILES, ROOT
from glaze_ui_2 import apply_glaze_ui_2
from normalize_homepage import normalize_homepage
from render_repository_portfolio import load_manifest, render_public_file

FORBIDDEN_NAMES = {".git", ".github", ".gitignore", "README.md", "SECURITY.md", "scripts"}


def source_file_set() -> set[Path]:
    return {Path(relative) for relative in PUBLIC_FILES}


def artifact_file_set() -> set[Path]:
    return {path.relative_to(DIST) for path in DIST.rglob("*") if path.is_file()}


def expected_bytes(path: Path, manifest: dict) -> bytes:
    source = ROOT / path
    if path.suffix == ".html":
        rendered = source.read_text(encoding="utf-8")
        if str(path) in GENERATED_HTML:
            rendered = render_public_file(str(path), rendered, manifest)
            if str(path) == "index.html":
                rendered = normalize_homepage(rendered)
        return apply_glaze_ui_2(rendered).encode("utf-8")
    return source.read_bytes()


def main() -> int:
    errors: list[str] = []
    if not DIST.exists() or not DIST.is_dir():
        errors.append("dist/ is missing; run scripts/build_public_site.py first.")
    elif DIST.is_symlink():
        errors.append("dist/ must not be a symlink.")
    if errors:
        for error in errors:
            print(f"Build artifact validation failed: {error}")
        return 1

    for path in DIST.rglob("*"):
        if path.is_symlink():
            errors.append(f"Build artifact must not contain symlinks: {path.relative_to(DIST)}")

    expected = source_file_set()
    actual = artifact_file_set()
    manifest = load_manifest(ROOT)

    for path in sorted(expected - actual):
        errors.append(f"Expected public file is missing from dist/: {path}")
    for path in sorted(actual - expected):
        errors.append(f"Unexpected file is present in dist/: {path}")

    for path in sorted(expected & actual):
        source = ROOT / path
        built = DIST / path
        if not source.is_file() or source.is_symlink():
            errors.append(f"Allowlisted source is invalid: {path}")
            continue
        if expected_bytes(path, manifest) != built.read_bytes():
            errors.append(f"Built file differs from its reviewed/generated source contract: {path}")

    top_level_names = {path.parts[0] for path in actual if path.parts}
    for forbidden in sorted(FORBIDDEN_NAMES & top_level_names):
        errors.append(f"Repository-only content leaked into the deploy artifact: {forbidden}")

    required_runtime_files = {
        Path("index.html"), Path("repositories.html"), Path("404.html"), Path("privacy.html"),
        Path("security.html"), Path("_headers"), Path("robots.txt"), Path("sitemap.xml"),
        Path("site.webmanifest"), Path(".well-known/security.txt"), Path("css/glaze.css"),
        Path("css/glaze-polish.css"), Path("css/glaze-ui-2.1.0.css"), Path("js/theme-init.js"),
    }
    for path in sorted(required_runtime_files - actual):
        errors.append(f"Required runtime file is missing from dist/: {path}")

    for page in ("index.html","repositories.html","404.html","privacy.html","security.html"):
        text=(DIST/page).read_text(encoding="utf-8")
        for marker in ('name="goreecloud-glaze-ui" content="2.1.0"','data-glaze-ui="2.1.0"'):
            if marker not in text: errors.append(f"Built {page} missing Glaze UI 2.1 marker: {marker}")
        for stale in ('data-glaze-ui="1.5.0"','data-glaze-ui="2.0.0"'):
            if stale in text: errors.append(f"Built {page} still activates a superseded Glaze UI bundle")

    if errors:
        print("Build artifact validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    total_bytes = sum((DIST / path).stat().st_size for path in actual)
    print(f"Build artifact validation passed: {len(actual)} explicitly allowlisted files, {total_bytes} bytes, Glaze UI 2.1 active.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
