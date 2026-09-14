#!/usr/bin/env python3
"""Build the canonical GoreeCloud Design Center V1.4 publication artifact."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "website"
DIST = SOURCE / "dist"
IDENTITY = ROOT / "assets" / "identity" / "official" / "facet"
REFERENCE = ROOT / "reference"
VERSION = "1.4.0"
REVISION = "84cb3db4884042f0fa25ed6d475a127fb110f596"
ENTRY = "glaze-v1.4.0.css"
ENTRY_BLOB = "d48a9bc317090d152799769271de0fb4325494c4"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data, usedforsecurity=False).hexdigest()


def load_lock() -> dict:
    lock_path = SOURCE / "glaze.lock.json"
    if not lock_path.is_file() or lock_path.is_symlink():
        raise SystemExit("Design Center GLAZE UI lock is missing or unsafe")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    expected = {
        "version": VERSION, "lifecycle": "Stable", "repository": "GoreeCloud/goreecloud-glaze-ui",
        "stable_commit": REVISION, "entrypoint": ENTRY, "entrypoint_blob": ENTRY_BLOB,
        "consumer_state": "build-migrated-rendered-acceptance-pending",
    }
    for key, value in expected.items():
        if lock.get(key) != value:
            raise SystemExit(f"invalid Design Center GLAZE UI lock {key}: {lock.get(key)!r}")
    return lock


def read_glaze(name: str, lock: dict) -> bytes:
    if Path(name).name != name or not name.endswith(".css"):
        raise SystemExit(f"unsafe GLAZE UI dependency: {name}")
    source_root = os.environ.get("GLAZE_UI_SOURCE")
    try:
        if source_root:
            path = Path(source_root) / "css" / name
            if not path.is_file() or path.is_symlink():
                raise SystemExit(f"missing or unsafe pinned GLAZE UI source: {name}")
            data = path.read_bytes()
        else:
            url = f"https://raw.githubusercontent.com/{lock['repository']}/{lock['stable_commit']}/css/{name}"
            request = urllib.request.Request(url, headers={"User-Agent": "GoreeCloud-design-center-builder/1.4"})
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read()
    except urllib.error.URLError as exc:
        raise SystemExit(f"failed to fetch pinned GLAZE UI dependency {name}: {exc}") from exc
    if name == ENTRY and git_blob_sha(data) != ENTRY_BLOB:
        raise SystemExit("GLAZE UI V1.4 entrypoint integrity mismatch")
    return data


def main() -> None:
    lock = load_lock()
    if DIST.exists():
        if DIST.is_symlink():
            raise SystemExit("Design Center dist must not be a symlink")
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    (DIST / "reference").mkdir(parents=True)

    for name in ("index.html", "404.html", "_headers"):
        source = SOURCE / name
        if not source.is_file() or source.is_symlink():
            raise SystemExit(f"missing or unsafe Design Center source: {name}")
        shutil.copy2(source, DIST / name)

    for name in ("site.css", "identity.css", "site.js", "v1.3-site.css"):
        source = SOURCE / name
        if not source.is_file() or source.is_symlink():
            raise SystemExit(f"missing or unsafe Design Center source: {name}")
        shutil.copy2(source, DIST / "assets" / name)

    mark = IDENTITY / "glaze-ui-mark.svg"
    if not mark.is_file() or mark.is_symlink():
        raise SystemExit("canonical Design Center Facet identity is missing or unsafe")
    shutil.copy2(mark, DIST / "assets" / "glaze-ui-mark.svg")
    reference = REFERENCE / "v1-system-shell.html"
    if not reference.is_file() or reference.is_symlink():
        raise SystemExit("Design Center reference shell is missing or unsafe")
    shutil.copy2(reference, DIST / "reference" / "v1-system-shell.html")

    collected: dict[str, bytes] = {}
    def collect(name: str) -> None:
        if name in collected:
            return
        data = read_glaze(name, lock)
        text = data.decode("utf-8")
        for statement in re.findall(r"@import[^;]+;", text, flags=re.IGNORECASE):
            lowered = statement.lower()
            if "http://" in lowered or "https://" in lowered or "//" in statement:
                raise SystemExit(f"remote GLAZE UI import is forbidden: {statement}")
            match = IMPORT_RE.search(statement)
            if not match:
                raise SystemExit(f"unsupported GLAZE UI import syntax: {statement}")
            dependency = match.group(1)
            if Path(dependency).name != dependency or not dependency.endswith(".css"):
                raise SystemExit(f"unsafe GLAZE UI dependency: {dependency}")
            collect(dependency)
        collected[name] = data
    collect(ENTRY)
    for name, data in sorted(collected.items()):
        (DIST / "assets" / name).write_bytes(data)

    print(
        f"Built {DIST.relative_to(ROOT)} as GLAZE UI {VERSION} Stable pinned to {REVISION}; "
        "rendered, accessibility, performance, rollback, Cloudflare cutover, and production acceptance remain independent gates"
    )


if __name__ == "__main__":
    main()
