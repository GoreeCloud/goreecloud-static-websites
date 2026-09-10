#!/usr/bin/env python3
"""Build the explicit public artifact for suite.goreecloud.com."""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
LOCK = json.loads((ROOT / "glaze.lock.json").read_text(encoding="utf-8"))
EXPECTED_VERSION = "1.3.0"
EXPECTED_COMMIT = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
EXPECTED_ENTRYPOINT = "glaze-v1.3.0.css"
EXPECTED_ENTRYPOINT_BLOB = "4c3ad293ba9196e2e5a32700b530ec67fd01cef6"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)

SUITE_ICON_FILES = (
    "assets/suite/backup.svg",
    "assets/suite/bookmarks.svg",
    "assets/suite/browser.svg",
    "assets/suite/calendar.svg",
    "assets/suite/changelogs.svg",
    "assets/suite/contacts.svg",
    "assets/suite/dns.svg",
    "assets/suite/feed.svg",
    "assets/suite/gallery.svg",
    "assets/suite/identity.svg",
    "assets/suite/keyboard.svg",
    "assets/suite/launcher.svg",
    "assets/suite/location.svg",
    "assets/suite/manager.svg",
    "assets/suite/memos.svg",
    "assets/suite/monitor.svg",
    "assets/suite/music.svg",
    "assets/suite/network.svg",
    "assets/suite/notes.svg",
    "assets/suite/notify.svg",
    "assets/suite/photos.svg",
    "assets/suite/search.svg",
    "assets/suite/sync.svg",
    "assets/suite/tasks.svg",
    "assets/suite/vault.svg",
    "assets/suite/video.svg",
)

PUBLIC_FILES = (
    "index.html",
    "styles.css",
    "glaze-v1.3-consumer.css",
    "_headers",
    "robots.txt",
    "sitemap.xml",
    "site.webmanifest",
    "assets/goreecloud-logo.svg",
    *SUITE_ICON_FILES,
)


def git_blob_sha(data: bytes) -> str:
    prefix = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


def require_file(path: Path) -> Path:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"invalid public source: {path.relative_to(ROOT)}")
    return path


def read_glaze(name: str) -> bytes:
    if Path(name).name != name or not name.endswith(".css"):
        raise ValueError(f"unsafe Glaze stylesheet dependency: {name}")
    source_root = os.environ.get("GLAZE_UI_SOURCE")
    if source_root:
        data = require_file(Path(source_root) / "css" / name).read_bytes()
    else:
        url = f"https://raw.githubusercontent.com/{LOCK['repository']}/{LOCK['stable_commit']}/css/{name}"
        request = urllib.request.Request(url, headers={"User-Agent": "GoreeCloud-public-site-builder/1"})
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read()
    if name == EXPECTED_ENTRYPOINT and git_blob_sha(data) != EXPECTED_ENTRYPOINT_BLOB:
        raise ValueError("Glaze V1.3 Stable entrypoint integrity mismatch")
    return data


def collect_glaze(name: str, collected: dict[str, bytes]) -> None:
    if name in collected:
        return
    data = read_glaze(name)
    text = data.decode("utf-8")
    for statement in re.findall(r"@import[^;]+;", text, flags=re.IGNORECASE):
        if "http://" in statement.lower() or "https://" in statement.lower() or "//" in statement:
            raise ValueError(f"remote Glaze import is forbidden: {statement}")
        match = IMPORT_RE.search(statement)
        if not match:
            raise ValueError(f"unsupported Glaze import syntax: {statement}")
        dependency = match.group(1)
        if Path(dependency).name != dependency or not dependency.endswith(".css"):
            raise ValueError(f"unsafe Glaze import dependency: {dependency}")
        collect_glaze(dependency, collected)
    collected[name] = data


def main() -> int:
    try:
        if LOCK.get("version") != EXPECTED_VERSION or LOCK.get("lifecycle") != "Stable":
            raise ValueError("Suite Glaze lock must target 1.3.0 Stable")
        if LOCK.get("stable_commit") != EXPECTED_COMMIT:
            raise ValueError("Suite Glaze lock has unexpected Stable source revision")
        if LOCK.get("entrypoint") != EXPECTED_ENTRYPOINT or LOCK.get("entrypoint_blob") != EXPECTED_ENTRYPOINT_BLOB:
            raise ValueError("Suite Glaze lock has unexpected Stable entrypoint contract")
        if LOCK.get("consumer_state") != "source-migrated-rendered-acceptance-pending":
            raise ValueError("Suite Glaze consumer state must remain fail-closed")
        if len(PUBLIC_FILES) != len(set(PUBLIC_FILES)):
            raise ValueError("public allowlist contains duplicate paths")
        if DIST.exists():
            if DIST.is_symlink():
                raise ValueError("dist must not be a symlink")
            shutil.rmtree(DIST)
        DIST.mkdir()
        for relative in PUBLIC_FILES:
            source = require_file(ROOT / relative)
            target = DIST / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

        glaze: dict[str, bytes] = {}
        collect_glaze(EXPECTED_ENTRYPOINT, glaze)
        assets = DIST / "assets"
        assets.mkdir(exist_ok=True)
        for name, data in sorted(glaze.items()):
            (assets / name).write_bytes(data)
    except (OSError, ValueError, UnicodeDecodeError, urllib.error.URLError) as exc:
        print(f"Suite website build failed: {exc}")
        return 1

    files = [path for path in DIST.rglob("*") if path.is_file()]
    print(
        f"Built Suite V1.3 source-migrated artifact: {len(files)} files, "
        f"{sum(path.stat().st_size for path in files)} bytes; rendered/production acceptance remains separate"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
