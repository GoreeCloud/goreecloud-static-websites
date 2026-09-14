#!/usr/bin/env python3
"""Build GoreeCloud Design Center as an exact GLAZE UI V1.4 publication artifact."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import urllib.error
import urllib.request

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
DIST = SITE / "dist"
IDENTITY = ROOT / "assets" / "identity" / "official" / "facet"
REFERENCE = ROOT / "reference"
VERSION = "1.4.0"
REVISION = "84cb3db4884042f0fa25ed6d475a127fb110f596"
ENTRY = "glaze-v1.4.0.css"
ENTRY_BLOB = "d48a9bc317090d152799769271de0fb4325494c4"
LEGACY_REVISION = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data, usedforsecurity=False).hexdigest()


def render(text: str) -> str:
    replacements = (
        ('data-glaze-version="1.3.0"', 'data-glaze-version="1.4.0"'),
        ('name="goreecloud-glaze-ui" content="1.3.0"', 'name="goreecloud-glaze-ui" content="1.4.0"'),
        (f'name="goreecloud-glaze-source-revision" content="{LEGACY_REVISION}"', f'name="goreecloud-glaze-source-revision" content="{REVISION}"'),
        ('name="goreecloud-glaze-consumer-state" content="source-migrated-rendered-acceptance-pending"', 'name="goreecloud-glaze-consumer-state" content="build-migrated-rendered-acceptance-pending"'),
        ('data-glaze-ui="1.3.0"', 'data-glaze-consumer-adaptation="1.3-inherited"'),
        ('GLAZE UI V1.3 — Adaptive Resonance', 'GLAZE UI V1.4 — Optical Intelligence'),
        ('GLAZE UI V1.3', 'GLAZE UI V1.4'),
        ('Current Official Stable · 1.3.0', 'Current Official Stable · 1.4.0'),
        ('V1.3.0 is consumer-eligible', 'V1.4.0 is consumer-eligible'),
        ('Explore V1.3', 'Explore V1.4'),
        ('Adaptive Resonance.', 'Optical Intelligence.'),
        ('css/glaze-v1.3.0.css', 'css/glaze-v1.4.0.css'),
        ('js/glaze-v1.3.0.mjs', 'js/glaze-v1.4.0.mjs'),
        (LEGACY_REVISION, REVISION),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    shared = '<link rel="stylesheet" href="/assets/glaze-v1.4.0.css" data-glaze-ui="1.4.0">'
    inherited = '<link rel="stylesheet" href="/assets/v1.3-site.css" data-glaze-consumer-adaptation="1.3-inherited">'
    if shared not in text and inherited in text:
        text = text.replace(inherited, shared + "\n  " + inherited, 1)
    return text


def read_glaze_css(name: str, lock: dict) -> bytes:
    if Path(name).name != name or not name.endswith(".css"):
        raise SystemExit(f"unsafe GLAZE UI dependency: {name}")
    source_root = os.environ.get("GLAZE_UI_SOURCE")
    if source_root:
        path = Path(source_root) / "css" / name
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"missing or unsafe pinned GLAZE UI source: {name}")
        data = path.read_bytes()
    else:
        url = f"https://raw.githubusercontent.com/{lock['repository']}/{lock['stable_commit']}/css/{name}"
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "GoreeCloud-design-builder/1.4"})
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read()
        except urllib.error.URLError as exc:
            raise SystemExit(f"failed to fetch pinned GLAZE UI dependency {name}: {exc}") from exc
    if name == ENTRY and blob_sha(data) != ENTRY_BLOB:
        raise SystemExit("GLAZE UI V1.4 entrypoint integrity mismatch")
    return data


def main() -> None:
    lock = json.loads((SITE / "glaze.lock.json").read_text(encoding="utf-8"))
    expected = {
        "version": VERSION,
        "lifecycle": "Stable",
        "repository": "GoreeCloud/goreecloud-glaze-ui",
        "stable_commit": REVISION,
        "entrypoint": ENTRY,
        "entrypoint_blob": ENTRY_BLOB,
        "consumer_state": "build-migrated-rendered-acceptance-pending",
    }
    for key, value in expected.items():
        if lock.get(key) != value:
            raise SystemExit(f"invalid Design Center GLAZE UI lock {key}: {lock.get(key)!r}")

    if DIST.exists():
        if DIST.is_symlink():
            raise SystemExit("Design Center dist must not be a symlink")
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    (DIST / "reference").mkdir(parents=True)

    for name in ("index.html", "404.html", "_headers"):
        source = SITE / name
        if not source.is_file() or source.is_symlink():
            raise SystemExit(f"missing or unsafe Design Center source: {name}")
        shutil.copy2(source, DIST / name)
    for page in ("index.html", "404.html"):
        path = DIST / page
        path.write_text(render(path.read_text(encoding="utf-8")), encoding="utf-8")

    for name in ("site.css", "identity.css", "site.js", "v1.3-site.css"):
        source = SITE / name
        target = DIST / "assets" / name
        if source.suffix in {".css", ".js"}:
            target.write_text(render(source.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copy2(source, target)

    for name in (
        "glaze.css", "glaze.controls.css", "glaze.expressive.css", "glaze.formfactors.css",
        "glaze.accessibility.css", "glaze.color.css", "glaze.motion.css", "glaze.materials.css",
        "glaze.layout.css", "glaze.states.css",
    ):
        shutil.copy2(ROOT / "css" / name, DIST / "assets" / name)

    shutil.copy2(IDENTITY / "glaze-ui-mark.svg", DIST / "assets" / "glaze-ui-mark.svg")
    shutil.copy2(REFERENCE / "v1-system-shell.html", DIST / "reference" / "v1-system-shell.html")

    collected: dict[str, bytes] = {}
    def collect(name: str) -> None:
        if name in collected:
            return
        data = read_glaze_css(name, lock)
        text = data.decode("utf-8")
        for statement in re.findall(r"@import[^;]+;", text, flags=re.IGNORECASE):
            lowered = statement.lower()
            if "http://" in lowered or "https://" in lowered or "//" in statement:
                raise SystemExit(f"remote GLAZE UI import is forbidden: {statement}")
            match = IMPORT_RE.search(statement)
            if not match:
                raise SystemExit(f"unsupported GLAZE UI import syntax: {statement}")
            collect(match.group(1))
        collected[name] = data

    collect(ENTRY)
    for name, data in sorted(collected.items()):
        (DIST / "assets" / name).write_bytes(data)

    print(f"Built Design Center with GLAZE UI {VERSION} Stable pinned to {REVISION}; production acceptance remains separate")


if __name__ == "__main__":
    main()
