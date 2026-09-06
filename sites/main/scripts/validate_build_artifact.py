#!/usr/bin/env python3
"""Validate that Main dist/ contains only reviewed source plus the pinned V1.1 bundle."""
from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from glaze_v1 import FILES as GLAZE_FILES, validate_bundle  # noqa: E402
from build_public_site import DIST, GENERATED_GLAZE_FILES, PUBLIC_FILES, ROOT  # noqa: E402

FORBIDDEN_TOP_LEVEL = {".git", ".github", "README.md", "SECURITY.md", "scripts", "docs"}
PAGES = ("index.html", "repositories.html", "privacy.html", "security.html", "404.html")


def main() -> int:
    errors: list[str] = []
    if not DIST.is_dir() or DIST.is_symlink():
        errors.append("dist/ is missing or invalid; run scripts/build_public_site.py first")
    if errors:
        for error in errors:
            print(f"Build artifact validation failed: {error}")
        return 1

    for path in DIST.rglob("*"):
        if path.is_symlink():
            errors.append(f"artifact must not contain symlinks: {path.relative_to(DIST)}")

    expected = {Path(p) for p in (*PUBLIC_FILES, *GENERATED_GLAZE_FILES)}
    actual = {path.relative_to(DIST) for path in DIST.rglob("*") if path.is_file()}
    for path in sorted(expected - actual):
        errors.append(f"expected public file missing from dist/: {path}")
    for path in sorted(actual - expected):
        errors.append(f"unexpected file present in dist/: {path}")

    for relative in map(Path, PUBLIC_FILES):
        source = ROOT / relative
        built = DIST / relative
        if built.is_file() and source.read_bytes() != built.read_bytes():
            errors.append(f"built reviewed file differs from source: {relative}")

    bundle: dict[str, str] = {}
    for name in GLAZE_FILES:
        path = DIST / "assets" / "glaze-v1" / name
        if path.is_file():
            bundle[name] = path.read_text(encoding="utf-8")
    if len(bundle) == len(GLAZE_FILES):
        try:
            validate_bundle(bundle)
        except ValueError as exc:
            errors.append(str(exc))

    top = {path.parts[0] for path in actual if path.parts}
    for forbidden in sorted(FORBIDDEN_TOP_LEVEL & top):
        errors.append(f"repository-only content leaked into artifact: {forbidden}")

    for page in PAGES:
        path = DIST / page
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in (
            'data-glaze-version="1.1"',
            'name="goreecloud-glaze-ui" content="1.1.0"',
            'data-glaze-ui="1.1.0"',
            '/assets/glaze-v1/glaze-v1.1.0.css',
        ):
            if marker not in text:
                errors.append(f"built {page} missing V1.1 marker: {marker}")
        for forbidden in ('data-glaze-ui="2.', 'glaze-ui-2.', 'glaze-2.'):
            if forbidden in text:
                errors.append(f"built {page} still activates pre-reset GLAZE source: {forbidden}")

    if errors:
        print("Build artifact validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Build artifact validation passed: {len(actual)} files, pinned GLAZE UI V1.1 active.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
