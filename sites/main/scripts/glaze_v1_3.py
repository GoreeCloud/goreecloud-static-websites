#!/usr/bin/env python3
"""Exact GLAZE UI V1.3 source contract for the GoreeCloud Main website."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request

GLAZE_VERSION = "1.3.0"
GLAZE_LIFECYCLE = "Stable"
GLAZE_PROMOTION_REVISION = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
GLAZE_ENTRYPOINT = "glaze-v1.3.0.css"
GLAZE_ENTRYPOINT_BLOB = "4c3ad293ba9196e2e5a32700b530ec67fd01cef6"
GLAZE_CONSUMER_STATE = "source-migrated-rendered-acceptance-pending"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)


def git_blob_sha(data: bytes) -> str:
    prefix = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


def load_lock(root: Path) -> dict:
    lock_path = root / "glaze.lock.json"
    if not lock_path.is_file() or lock_path.is_symlink():
        raise ValueError("Main GLAZE UI consumer lock is missing or unsafe")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    expected = {
        "version": GLAZE_VERSION,
        "lifecycle": GLAZE_LIFECYCLE,
        "repository": "GoreeCloud/goreecloud-glaze-ui",
        "stable_commit": GLAZE_PROMOTION_REVISION,
        "entrypoint": GLAZE_ENTRYPOINT,
        "entrypoint_blob": GLAZE_ENTRYPOINT_BLOB,
        "consumer_state": GLAZE_CONSUMER_STATE,
    }
    for key, value in expected.items():
        if lock.get(key) != value:
            raise ValueError(f"unexpected Main GLAZE UI lock value for {key}: {lock.get(key)!r}")
    return lock


def collect_glaze_css(root: Path) -> dict[str, bytes]:
    """Collect the exact same-origin CSS dependency closure rooted at V1.3 Stable."""
    lock = load_lock(root)
    source_root = os.environ.get("GLAZE_UI_SOURCE")
    collected: dict[str, bytes] = {}

    def read(name: str) -> bytes:
        if Path(name).name != name or not name.endswith(".css"):
            raise ValueError(f"unsafe GLAZE UI dependency: {name}")
        try:
            if source_root:
                path = Path(source_root) / "css" / name
                if not path.is_file() or path.is_symlink():
                    raise ValueError(f"missing or unsafe pinned GLAZE UI source: {name}")
                data = path.read_bytes()
            else:
                url = f"https://raw.githubusercontent.com/{lock['repository']}/{lock['stable_commit']}/css/{name}"
                request = urllib.request.Request(url, headers={"User-Agent": "GoreeCloud-main-site-builder/1"})
                with urllib.request.urlopen(request, timeout=20) as response:
                    data = response.read()
        except urllib.error.URLError as exc:
            raise ValueError(f"failed to fetch pinned GLAZE UI dependency {name}: {exc}") from exc
        if name == GLAZE_ENTRYPOINT and git_blob_sha(data) != GLAZE_ENTRYPOINT_BLOB:
            raise ValueError("GLAZE UI V1.3 entrypoint integrity mismatch")
        return data

    def collect(name: str) -> None:
        if name in collected:
            return
        data = read(name)
        text = data.decode("utf-8")
        for statement in re.findall(r"@import[^;]+;", text, flags=re.IGNORECASE):
            lowered = statement.lower()
            if "http://" in lowered or "https://" in lowered or "//" in statement:
                raise ValueError(f"remote GLAZE UI import is forbidden: {statement}")
            match = IMPORT_RE.search(statement)
            if not match:
                raise ValueError(f"unsupported GLAZE UI import syntax: {statement}")
            dependency = match.group(1)
            if Path(dependency).name != dependency or not dependency.endswith(".css"):
                raise ValueError(f"unsafe GLAZE UI import dependency: {dependency}")
            collect(dependency)
        collected[name] = data

    collect(GLAZE_ENTRYPOINT)
    return collected
