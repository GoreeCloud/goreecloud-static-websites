#!/usr/bin/env python3
from pathlib import Path
import sys

from glaze_ui_2 import GLAZE_PROMOTION_REVISION, GLAZE_VERSION

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT.parent
BUNDLE = ROOT / "css/glaze-ui-2.1.0.css"
ROOT_PAGES = [ROOT / n for n in ("index.html", "repositories.html", "privacy.html", "security.html", "404.html")]
CHILD_PAGES = [
    SITES / "projects/index.html", SITES / "projects/404.html",
    SITES / "roadmap/index.html", SITES / "roadmap/404.html",
    SITES / "blog/index.html", SITES / "blog/404.html",
    SITES / "archive/index.html", SITES / "archive/404.html",
]
CHILD_BUNDLES = [
    SITES / "projects/assets/glaze-ui-2.1.0.css",
    SITES / "roadmap/glaze-ui-2.1.0.css",
    SITES / "blog/glaze-ui-2.1.0.css",
    SITES / "archive/glaze-ui-2.1.0.css",
]
CONFORMANCE = ROOT / "docs/glaze-ui-conformance.md"
errors = []


def display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path.relative_to(SITES.parent))


bundle_markers = [
    "Glaze UI 2.1.0 Stable integration",
    GLAZE_PROMOTION_REVISION,
    "Content is solid. Interaction is glazed.",
    "--glaze-touch-min:48px",
    "--glaze-touch-assisted:56px",
    "data-glaze-density=comfortable",
    "data-glaze-density=compact",
    "data-glaze-performance=reduced",
    "data-glaze-large-text=true",
    "prefers-reduced-motion",
    "prefers-reduced-transparency",
    "forced-colors:active",
]
for bundle in [BUNDLE, *CHILD_BUNDLES]:
    if not bundle.is_file():
        errors.append(f"Glaze UI 2.1 bundle is missing: {display(bundle)}")
        continue
    css = bundle.read_text(encoding="utf-8")
    for marker in bundle_markers:
        if marker not in css:
            errors.append(f"{display(bundle)} missing 2.1 marker: {marker}")


def validate_page(page: Path) -> None:
    if not page.is_file():
        errors.append(f"Glaze UI page is missing: {display(page)}")
        return
    text = page.read_text(encoding="utf-8")
    for marker in [
        f'name="goreecloud-glaze-ui" content="{GLAZE_VERSION}"',
        f'data-glaze-ui="{GLAZE_VERSION}"',
        'glaze-canvas',
        'name="viewport"',
    ]:
        if marker not in text:
            errors.append(f"{display(page)} missing source-native 2.1 marker: {marker}")
    for stale in (
        'data-glaze-ui="1.5.0"',
        'data-glaze-ui="2.0.0"',
        'goreecloud-glaze-ui" content="1.5.0"',
        'goreecloud-glaze-ui" content="2.0.0"',
    ):
        if stale in text:
            errors.append(f"{display(page)} still activates a superseded Glaze UI bundle: {stale}")
    if "raw.githubusercontent.com" in text:
        errors.append(f"{display(page)} must not load remote Glaze UI at runtime")


for page in [*ROOT_PAGES, *CHILD_PAGES]:
    validate_page(page)

text = CONFORMANCE.read_text(encoding="utf-8") if CONFORMANCE.is_file() else ""
for marker in [
    "Target Glaze UI version: **2.1.0**",
    "GoreeCloud/goreecloud-glaze-ui",
    GLAZE_PROMOTION_REVISION,
    "same-origin",
    "Content is solid. Interaction is glazed.",
    "48px general interaction floor",
    "56px Touch Assistance floor",
    "Rendered/production acceptance",
    "No production Glaze UI exception",
]:
    if marker not in text:
        errors.append(f"Conformance marker missing: {marker}")

if errors:
    print("Glaze UI 2.1 validation failed:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
print("Glaze UI 2.1.0 Stable source validation passed across every Main, Projects, Roadmap, Blog, and Archive HTML surface in the canonical central hierarchy.")
