#!/usr/bin/env python3
"""Validate the public GoreeCloud Suite website and origin-local identity assets."""

from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import re
import sys

from glaze_ui_2 import GLAZE_PROMOTION_REVISION, apply_glaze_ui_2

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
STYLES = ROOT / "styles.css"
GLAZE = ROOT / "glaze-ui-2.1.0.css"

EXPECTED_ASSET_BLOBS = {
    "assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "assets/suite/ai.svg": "1cbe04748f50cb843eef0cbb7233e2769efa275a",
    "assets/suite/app-store.svg": "05c66a2a4c8edcc194183bb8ffb10ca90d8eaeef",
    "assets/suite/backup.svg": "6e8f2bc02beb4679ed99f2db787e7dc6b4a0f28f",
    "assets/suite/bookmarks.svg": "2e9947924708df10844a3a81f47585c4da6b931a",
    "assets/suite/browser.svg": "2a81cc68cb8c1831dfd7bec6c3d0b14e2f421f1f",
    "assets/suite/calendar.svg": "369c42a204c6b130f49f37f91ec0569256a2c19e",
    "assets/suite/changelogs.svg": "958878ecde32cadd3e646c606534638e4f5e01fb",
    "assets/suite/code.svg": "579f0416bd2839bf40e87de7751e319d80bd0bf9",
    "assets/suite/contacts.svg": "22e818436ebef790333fcf56efa79d5bdfff5c88",
    "assets/suite/dns.svg": "99c8e09f4e8e65bde57e671e4fd4beb1bd2fcb4a",
    "assets/suite/documents.svg": "58200e22b053fe17a2d80cc69e9908a3a2987a34",
    "assets/suite/drive.svg": "a931ebc4e657895128adb6391eb4665c99e74c4a",
    "assets/suite/feed.svg": "3464434f08f1c200621900ae86a00d04e812a5fb",
    "assets/suite/file-manager.svg": "c723a84eb2ecb29ef8a0cef845eb1d2cff714cd0",
    "assets/suite/gallery.svg": "ff3085d705b567283dd566a3c02e667866458012",
    "assets/suite/gateway.svg": "f8a94f6a6ff5dece3f93bc15531ee5845fa3db61",
    "assets/suite/identity.svg": "dc8287e385f86767f0105c48a8f234d8440d7623",
    "assets/suite/index.svg": "797cfbd9ae490e37b5a90efe02905159158a8e88",
    "assets/suite/keyboard.svg": "9dea51ca5853dc0faf41d94fbc12ee810480c472",
    "assets/suite/launcher.svg": "d6768114e689058f1c911beca4050f33c96bd7c2",
    "assets/suite/location.svg": "ceb93b6d814c80ece0929022eb5edcdfbc346e2d",
    "assets/suite/mail.svg": "6fcc489ccfc6348514755a9a052dc413ee17ccde",
    "assets/suite/manager.svg": "024d82d5b5911e426216dfbd6a19d95cd6d71fc3",
    "assets/suite/maps.svg": "07b6e52e04c95e1ec9f703a9d323cf799481351c",
    "assets/suite/memos.svg": "eb9396c3a1891f6afb96849a29110c6f35e65f19",
    "assets/suite/messenger.svg": "01102af91a43e100c66877489b94929165ec0430",
    "assets/suite/monitor.svg": "f31c9abab93f1e9e45e34e0eef411705228d1a66",
    "assets/suite/music.svg": "74d7726676faf6447116153da53790e4c272e03c",
    "assets/suite/network.svg": "7457cd187d65887189150016b44c28af279635e5",
    "assets/suite/notes.svg": "9618b85e29f89990320cc3a101f0f3bf6fffc89f",
    "assets/suite/notify.svg": "1ce1239cd2319a0f96232b1562ec1f6e68d43815",
    "assets/suite/photos.svg": "7cce0f2f1b1fad209577a4e0294f0b767fd06b14",
    "assets/suite/search.svg": "fc441c75d6cc2bd0d88a80d77b60994b34475670",
    "assets/suite/sync.svg": "91e40049d146881df6befe32d836e260e2bd908c",
    "assets/suite/tasks.svg": "180e162c81b34a0b1dffd20031b36cbb874e2f61",
    "assets/suite/terminal.svg": "fd28f49fc0dd67e2f3e31480942d555914e8fc5b",
    "assets/suite/vault.svg": "c34edae0c57a6bac002fb0f940de7ae26cf1450e",
    "assets/suite/video.svg": "0fbffa1c5210b5da3934c4615b40d59303c0844c",
}

APPROVED_NEW_PRODUCT_IMAGES = {
    "GoreeCloud App Store": "assets/suite/app-store.svg",
    "GoreeCloud File Manager": "assets/suite/file-manager.svg",
    "GoreeCloud Maps": "assets/suite/maps.svg",
    "GoreeCloud Index": "assets/suite/index.svg",
}


def blob_id(raw: bytes) -> str:
    return sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def main() -> int:
    errors: list[str] = []
    source_html = INDEX.read_text(encoding="utf-8")
    html = apply_glaze_ui_2(source_html)
    css = STYLES.read_text(encoding="utf-8")

    for required in (
        'name="goreecloud-glaze-ui" content="2.1.0"',
        'data-glaze-ui="2.1.0"',
        'class="site-header glaze-material-soft"',
        'class="glaze-navigation-capsule"',
        'Stable 2.1.0 design, interaction, accessibility, motion, material, density, and form-factor contract',
        'GoreeCloud Identity · Identity Center',
    ):
        if required not in source_html:
            errors.append(f"Suite canonical source is missing current Glaze UI/ecosystem marker: {required}")
    for stale in (
        'data-glaze-ui="1.5.0"',
        'data-glaze-ui="2.0.0"',
        'href="glaze-ui-1.5.0.css"',
        'href="glaze-ui-2.0.0.css"',
        'Stable 1.5.0 design',
        'Stable 2.0.0 design',
        'the five substantive platform systems',
    ):
        if stale in source_html:
            errors.append(f"Suite canonical source still contains superseded active state: {stale}")
    if source_html != html:
        errors.append("Suite build normalizer must not need to rewrite the current canonical source template")

    if not GLAZE.is_file():
        errors.append("vendored Glaze UI 2.1.0 bundle is missing")
    else:
        glaze_text = GLAZE.read_text(encoding="utf-8")
        for required in (
            "Glaze UI 2.1.0 Stable integration",
            GLAZE_PROMOTION_REVISION,
            "Content is solid. Interaction is glazed.",
            "prefers-reduced-motion",
            "prefers-reduced-transparency",
            "forced-colors",
            "--glaze-touch-assisted:56px",
            "data-glaze-density=comfortable",
            "data-glaze-density=compact",
            "data-glaze-performance=reduced",
            "data-glaze-large-text=true",
        ):
            if required not in glaze_text:
                errors.append(f"Glaze UI 2.1 bundle marker missing: {required}")

    for required in (
        'name="goreecloud-glaze-ui" content="2.1.0"',
        'data-glaze-ui="2.1.0"',
        'class="site-header glaze-material-soft"',
        'class="glaze-navigation-capsule"',
        'Stable 2.1.0 design, interaction, accessibility, motion, material, density, and form-factor contract',
    ):
        if required not in html:
            errors.append(f"Suite rendered page is missing Glaze UI 2.1 contract marker: {required}")
    if 'data-glaze-ui="1.5.0"' in html or 'data-glaze-ui="2.0.0"' in html:
        errors.append("Suite rendered page still activates a superseded Glaze UI bundle")

    if '<link rel="canonical" href="https://suite.goreecloud.com/">' not in html:
        errors.append("canonical Suite domain is missing")
    app_card_count = html.count('class="app-card"')
    if app_card_count != 38:
        errors.append(f"expected 38 Suite application cards; found {app_card_count}")
    capability_card_count = html.count('class="capability-card"')
    if capability_card_count != 5:
        errors.append(f"expected 5 umbrella capability cards; found {capability_card_count}")

    for label in (
        "Glaze UI · Design Center",
        "Privacy Shield · Privacy Center",
        "Wardveil Security · Security Center",
        "Everkeep · Continuity Center",
        "GoreeCloud Mesh · Mesh Center",
        "GoreeCloud Identity · Identity Center",
    ):
        if html.count(f"<strong>{label}</strong>") != 1:
            errors.append(f"platform-system and Center contract must appear exactly once in the principle band: {label}")

    for product, icon in APPROVED_NEW_PRODUCT_IMAGES.items():
        if html.count(f"<h4>{product}</h4>") != 1:
            errors.append(f"current Suite application card missing: {product}")
        if html.count(f'<img src="{icon}"') != 1:
            errors.append(f"approved Suite product identity is not rendered exactly once: {product} -> {icon}")

    if "app-mark-pending" in html or any(mark in html for mark in ('>FM</span>', '>MP</span>', '>AS</span>')):
        errors.append("approved Suite products must not regress to pending letter-mark placeholders")

    if "Open WebUI" in html or "AnythingLLM" in html:
        errors.append("retired GoreeCloud AI front ends must not appear")
    if "GoreeCloud Identity" not in html:
        errors.append("GoreeCloud Identity application/system presentation is missing")

    ids = re.findall(r'\bid="([^"]+)"', html)
    if len(ids) != len(set(ids)):
        errors.append("HTML contains duplicate id attributes")

    if "https://www.goreecloud.com/assets/suite/" in html:
        errors.append("Suite icon references must be origin-local, not loaded from goreecloud.com")

    allowed_images = set(EXPECTED_ASSET_BLOBS)
    for src in re.findall(r'<img[^>]+src="([^"]+)"', html):
        if src not in allowed_images:
            errors.append(f"unexpected or non-local image source: {src}")

    for relative, expected_blob in EXPECTED_ASSET_BLOBS.items():
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            errors.append(f"required local identity asset is missing or invalid: {relative}")
            continue
        actual_blob = blob_id(path.read_bytes())
        if actual_blob != expected_blob:
            errors.append(f"local identity asset is not byte-identical to the reviewed canonical copy: {relative}")

    if "@media (prefers-reduced-motion: reduce)" not in css:
        errors.append("base reduced-motion handling is missing")
    if "@media (prefers-reduced-transparency: reduce)" not in css:
        errors.append("base reduced-transparency handling is missing")
    if ":focus-visible" not in css:
        errors.append("base visible keyboard focus styling is missing")

    if errors:
        print("Suite website validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        "Suite website Glaze UI 2.1 validation passed: canonical source and rendered output agree across "
        "38 applications, 6 substantive platform systems, 5 umbrella capabilities, approved canonical "
        "product artwork, 2.1 material hierarchy, density, touch assistance, accessibility, and performance fallbacks."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
