#!/usr/bin/env python3
"""Build a simple GoreeCloud static-site package from exact GLAZE UI V1.3 source."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import urllib.error
import urllib.request

EXPECTED_VERSION = "1.3.0"
EXPECTED_COMMIT = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
EXPECTED_ENTRYPOINT = "glaze-v1.3.0.css"
EXPECTED_ENTRYPOINT_BLOB = "4c3ad293ba9196e2e5a32700b530ec67fd01cef6"
ROOT_PUBLIC_FILES = ("index.html", "404.html", "_headers")
OPTIONAL_PUBLIC_FILES = ("robots.txt", "sitemap.xml")
LOCAL_RUNTIME_FILES = ("site.css", "style.css", "site.js", "v1.3-site.css")
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)


def blob_sha(data: bytes) -> str:
    prefix = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


def require_file(path: Path, root: Path) -> Path:
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"missing or unsafe public source: {path.relative_to(root)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("site")
    args = parser.parse_args()
    root = Path(args.site).resolve()
    dist = root / "dist"
    lock_path = require_file(root / "glaze.lock.json", root)
    lock = json.loads(lock_path.read_text(encoding="utf-8"))

    if lock.get("version") != EXPECTED_VERSION or lock.get("lifecycle") != "Stable":
        raise SystemExit("simple-site Glaze lock must target 1.3.0 Stable")
    if lock.get("stable_commit") != EXPECTED_COMMIT:
        raise SystemExit("unexpected GLAZE UI V1.3 source revision")
    if lock.get("entrypoint") != EXPECTED_ENTRYPOINT or lock.get("entrypoint_blob") != EXPECTED_ENTRYPOINT_BLOB:
        raise SystemExit("unexpected GLAZE UI V1.3 entrypoint contract")
    if lock.get("consumer_state") != "source-migrated-rendered-acceptance-pending":
        raise SystemExit("simple-site Glaze consumer state must remain fail-closed")

    def read_glaze(name: str) -> bytes:
        if Path(name).name != name or not name.endswith(".css"):
            raise SystemExit(f"unsafe Glaze dependency: {name}")
        source_root = os.environ.get("GLAZE_UI_SOURCE")
        try:
            if source_root:
                path = Path(source_root) / "css" / name
                if not path.is_file() or path.is_symlink():
                    raise SystemExit(f"missing or unsafe pinned Glaze source: {name}")
                data = path.read_bytes()
            else:
                url = f"https://raw.githubusercontent.com/{lock['repository']}/{lock['stable_commit']}/css/{name}"
                request = urllib.request.Request(url, headers={"User-Agent": "GoreeCloud-simple-static-site-builder/1"})
                with urllib.request.urlopen(request, timeout=20) as response:
                    data = response.read()
        except urllib.error.URLError as exc:
            raise SystemExit(f"failed to fetch pinned Glaze dependency {name}: {exc}") from exc
        if name == EXPECTED_ENTRYPOINT and blob_sha(data) != EXPECTED_ENTRYPOINT_BLOB:
            raise SystemExit("GLAZE UI V1.3 entrypoint integrity mismatch")
        return data

    collected: dict[str, bytes] = {}
    def collect(name: str) -> None:
        if name in collected:
            return
        data = read_glaze(name)
        text = data.decode("utf-8")
        for statement in re.findall(r"@import[^;]+;", text, flags=re.IGNORECASE):
            if "http://" in statement.lower() or "https://" in statement.lower() or "//" in statement:
                raise SystemExit(f"remote Glaze import is forbidden: {statement}")
            match = IMPORT_RE.search(statement)
            if not match:
                raise SystemExit(f"unsupported Glaze import syntax: {statement}")
            dependency = match.group(1)
            if Path(dependency).name != dependency or not dependency.endswith(".css"):
                raise SystemExit(f"unsafe Glaze import dependency: {dependency}")
            collect(dependency)
        collected[name] = data

    if dist.exists():
        if dist.is_symlink():
            raise SystemExit("dist must not be a symlink")
        shutil.rmtree(dist)
    (dist / "assets").mkdir(parents=True)

    for name in ROOT_PUBLIC_FILES:
        shutil.copy2(require_file(root / name, root), dist / name)
    for name in OPTIONAL_PUBLIC_FILES:
        path = root / name
        if path.exists():
            shutil.copy2(require_file(path, root), dist / name)
    for name in LOCAL_RUNTIME_FILES:
        path = root / name
        if path.exists():
            shutil.copy2(require_file(path, root), dist / "assets" / name)
    assets = root / "assets"
    if assets.exists():
        if assets.is_symlink() or not assets.is_dir():
            raise SystemExit("assets must be a real directory")
        for source in assets.rglob("*"):
            if source.is_symlink():
                raise SystemExit(f"unsafe public asset: {source.relative_to(root)}")
            if source.is_file():
                target = dist / "assets" / source.relative_to(assets)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

    collect(EXPECTED_ENTRYPOINT)
    for name, data in sorted(collected.items()):
        (dist / "assets" / name).write_bytes(data)

    print(
        f"Built {root.name} with GLAZE UI {EXPECTED_VERSION} Stable pinned to {EXPECTED_COMMIT}; "
        "rendered, deployment, and production acceptance remain separate"
    )


if __name__ == "__main__":
    main()
