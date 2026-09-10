#!/usr/bin/env python3
"""Validate the GoreeCloud Suite source or built artifact against current portfolio authority."""

from __future__ import annotations

from hashlib import sha1
from html.parser import HTMLParser
from pathlib import Path
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
LOCK = json.loads((ROOT / "glaze.lock.json").read_text(encoding="utf-8"))
EXPECTED_VERSION = "1.3.0"
EXPECTED_COMMIT = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
EXPECTED_ENTRYPOINT = "glaze-v1.3.0.css"
EXPECTED_ENTRYPOINT_BLOB = "4c3ad293ba9196e2e5a32700b530ec67fd01cef6"
EXPECTED_CONSUMER_STATE = "source-migrated-rendered-acceptance-pending"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)

parser = argparse.ArgumentParser()
parser.add_argument("--dist", action="store_true")
args = parser.parse_args()
BASE = DIST if args.dist else ROOT

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

CURRENT_PRODUCTS = (
    "GoreeCloud Notes", "GoreeCloud Memos", "GoreeCloud Tasks", "GoreeCloud Calendar", "GoreeCloud Contacts", "GoreeCloud Documents",
    "GoreeCloud Drive", "GoreeCloud File Manager", "GoreeCloud Sync", "GoreeCloud Photos", "GoreeCloud Gallery", "GoreeCloud Music", "GoreeCloud Video", "GoreeCloud Bookmarks", "GoreeCloud Reader",
    "GoreeCloud Mail", "GoreeCloud Messenger", "GoreeCloud Search", "GoreeCloud Browser", "GoreeCloud Feed", "GoreeCloud Location", "GoreeCloud Maps", "GoreeCloud Social",
    "GoreeCloud Keyboard", "GoreeCloud Launcher", "GoreeCloud Terminal",
    "GoreeCloud Manager", "GoreeCloud App Store", "GoreeCloud Identity", "GoreeVault", "GoreeCloud Backup", "GoreeCloud Network", "GoreeCloud DNS", "GoreeCloud Gateway", "GoreeCloud Notify", "GoreeCloud Monitor", "GoreeCloud Changelogs",
    "GoreeCloud AI", "GoreeCloud Index", "GoreeCloud Code",
    "GoreeCloud Health", "GoreeCloud Home", "GoreeCloud Home Security",
    "GoreeCloud Router OS", "GoreeCloud Website",
)
CURRENT_CAPABILITIES = ("GoreeCloud Quill", "GoreeCloud Waypoint", "GoreeCloud Resonance")
NEUTRAL_ARTWORK_PRODUCTS = (
    "GoreeCloud Reader", "GoreeCloud Social", "GoreeCloud Health", "GoreeCloud Home", "GoreeCloud Home Security", "GoreeCloud Router OS",
)
INTEGRAL_SYSTEM_MARKERS = (
    "GoreeCloud Manager", "GoreeCloud Identity", "Glaze UI · Design Center", "Wardveil Security · Security Center",
    "Privacy Shield · Privacy Center", "Everkeep · Continuity Center", "GoreeCloud Mesh",
)


def blob_id(raw: bytes) -> str:
    return sha1(f"blob {len(raw)}\0".encode("ascii") + raw, usedforsecurity=False).hexdigest()


class HtmlAudit(HTMLParser):
    def __init__(self, errors: list[str]):
        super().__init__()
        self.errors = errors

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "style" in values:
            self.errors.append("inline style attributes are forbidden")
        if tag == "script" and not values.get("src"):
            self.errors.append("inline scripts are forbidden")
        if tag in ("script", "link"):
            value = values.get("src") or values.get("href") or ""
            rel = values.get("rel", "")
            if value.startswith(("http://", "https://", "//")) and not (tag == "link" and "canonical" in rel.split()):
                self.errors.append(f"remote runtime dependency is forbidden: {value}")
        if tag == "a" and values.get("href", "").startswith("http://"):
            self.errors.append(f"external navigation must use HTTPS: {values['href']}")


def imported_closure(errors: list[str]) -> set[str]:
    assets = DIST / "assets"
    seen: set[str] = set()

    def visit(name: str) -> None:
        if name in seen:
            return
        if Path(name).name != name or not name.endswith(".css"):
            errors.append(f"unsafe Glaze dependency: {name}")
            return
        path = assets / name
        if not path.is_file() or path.is_symlink():
            errors.append(f"missing built Glaze dependency: {name}")
            return
        seen.add(name)
        text = path.read_text(encoding="utf-8")
        for statement in re.findall(r"@import[^;]+;", text, flags=re.IGNORECASE):
            if "http://" in statement.lower() or "https://" in statement.lower() or "//" in statement:
                errors.append(f"remote Glaze import is forbidden: {statement}")
                continue
            match = IMPORT_RE.search(statement)
            if not match:
                errors.append(f"unsupported Glaze import syntax: {statement}")
                continue
            visit(match.group(1))

    visit(EXPECTED_ENTRYPOINT)
    return seen


def main() -> int:
    errors: list[str] = []
    html = (BASE / "index.html").read_text(encoding="utf-8")
    css = (BASE / "styles.css").read_text(encoding="utf-8")
    v13_css = (BASE / "glaze-v1.3-consumer.css").read_text(encoding="utf-8")
    HtmlAudit(errors).feed(html)

    for key, expected in (
        ("version", EXPECTED_VERSION),
        ("lifecycle", "Stable"),
        ("stable_commit", EXPECTED_COMMIT),
        ("entrypoint", EXPECTED_ENTRYPOINT),
        ("entrypoint_blob", EXPECTED_ENTRYPOINT_BLOB),
        ("consumer_state", EXPECTED_CONSUMER_STATE),
    ):
        if LOCK.get(key) != expected:
            errors.append(f"Suite Glaze lock mismatch for {key}: {LOCK.get(key)!r} != {expected!r}")

    for marker in (
        'data-glaze-version="1.3.0"',
        'name="goreecloud-glaze-ui" content="1.3.0"',
        f'name="goreecloud-glaze-source-revision" content="{EXPECTED_COMMIT}"',
        f'name="goreecloud-glaze-consumer-state" content="{EXPECTED_CONSUMER_STATE}"',
        'href="assets/glaze-v1.3.0.css" data-glaze-ui="1.3.0"',
        'href="glaze-v1.3-consumer.css"',
        '<link rel="canonical" href="https://suite.goreecloud.com/">',
        'GLAZE UI V1.3 source target.',
        '45</strong><span>verified Suite products',
        '9</strong><span>functional product groups',
        '3</strong><span>application-centered capability identities',
        'Products without an approved canonical asset use an intentionally neutral marker',
    ):
        if marker not in html:
            errors.append(f"Suite V1.3/current-portfolio marker missing: {marker}")

    for stale in (
        'goreecloud-glaze-ui" content="2.1.0"', 'data-glaze-ui="2.1.0"', 'glaze-ui-2.1.0.css',
        '27</strong><span>current Suite applications', '7</strong><span>functional groups',
        '38</strong><span>current applications', '5</strong><span>approved umbrella',
    ):
        if stale in html:
            errors.append(f"superseded Suite directory or Glaze marker remains active: {stale}")

    app_card_count = html.count('class="app-card"')
    group_count = html.count('class="product-group"')
    capability_count = html.count('class="capability-card"')
    neutral_count = html.count('class="neutral-product-mark"')
    if app_card_count != 45:
        errors.append(f"expected 45 reconciled Suite product cards; found {app_card_count}")
    if group_count != 9:
        errors.append(f"expected 9 reconciled Suite functional product groups; found {group_count}")
    if capability_count != 3:
        errors.append(f"expected 3 current application-centered capability identities; found {capability_count}")
    if neutral_count != len(NEUTRAL_ARTWORK_PRODUCTS):
        errors.append(f"expected {len(NEUTRAL_ARTWORK_PRODUCTS)} neutral product marks; found {neutral_count}")

    for product in CURRENT_PRODUCTS:
        if html.count(f"<h4>{product}</h4>") != 1:
            errors.append(f"reconciled Suite product must appear exactly once: {product}")
    for capability in CURRENT_CAPABILITIES:
        if html.count(f"<h3>{capability}</h3>") != 1:
            errors.append(f"current Suite capability identity must appear exactly once: {capability}")
    for marker in INTEGRAL_SYSTEM_MARKERS:
        if marker not in html:
            errors.append(f"Integral Platform System marker missing: {marker}")

    for marker in (
        "--suite-v13-control:48px", "--suite-v13-control-assisted:56px", "pointer:coarse", "focus-visible",
        "prefers-reduced-motion:reduce", "prefers-reduced-transparency:reduce", "prefers-contrast:more",
        "forced-colors:active", "@media print",
    ):
        if marker not in v13_css:
            errors.append(f"Suite V1.3 adaptation marker missing: {marker}")
    for marker in ("@media (prefers-reduced-motion: reduce)", "@media (prefers-reduced-transparency: reduce)", ":focus-visible", ".neutral-product-mark"):
        if marker not in css:
            errors.append(f"Suite base accessibility/identity fallback missing: {marker}")

    ids = re.findall(r'\bid="([^"]+)"', html)
    if len(ids) != len(set(ids)):
        errors.append("HTML contains duplicate id attributes")
    if "https://www.goreecloud.com/assets/suite/" in html:
        errors.append("Suite identity assets must remain origin-local")
    allowed_images = set(EXPECTED_ASSET_BLOBS)
    for src in re.findall(r'<img[^>]+src="([^"]+)"', html):
        if src not in allowed_images:
            errors.append(f"unexpected or non-reviewed image source: {src}")

    for relative, expected_blob in EXPECTED_ASSET_BLOBS.items():
        source_path = ROOT / relative
        if not source_path.is_file() or source_path.is_symlink():
            errors.append(f"required reviewed identity asset missing: {relative}")
            continue
        if blob_id(source_path.read_bytes()) != expected_blob:
            errors.append(f"reviewed identity asset drifted: {relative}")
        if args.dist:
            built_path = DIST / relative
            if not built_path.is_file() or built_path.is_symlink():
                errors.append(f"built reviewed identity asset missing: {relative}")
            elif blob_id(built_path.read_bytes()) != expected_blob:
                errors.append(f"built reviewed identity asset drifted: {relative}")

    if args.dist:
        entrypoint = DIST / "assets" / EXPECTED_ENTRYPOINT
        if not entrypoint.is_file():
            errors.append("built GLAZE UI V1.3 Stable entrypoint missing")
        elif blob_id(entrypoint.read_bytes()) != EXPECTED_ENTRYPOINT_BLOB:
            errors.append("built GLAZE UI V1.3 Stable entrypoint integrity mismatch")
        closure = imported_closure(errors)
        if "glaze-v1.2.0.css" not in closure:
            errors.append("canonical V1.3 inherited rendering foundation is incomplete")

    if errors:
        print("Suite website validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"Suite website V1.3 validation passed ({'dist' if args.dist else 'source'}): 45 reconciled products, "
        "9 functional product groups, 3 application-centered capability identities, 38 reviewed product assets plus "
        "6 neutral artwork fallbacks, exact Glaze source pin, and accessibility/adaptive fallbacks. "
        "Rendered/production acceptance remains separate."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
