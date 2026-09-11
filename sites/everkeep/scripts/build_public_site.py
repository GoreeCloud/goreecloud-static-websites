#!/usr/bin/env python3
"""Build the isolated Continuity Center artifact from exact reviewed source."""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "website"
DIST = ROOT / "dist"
ICON = ROOT / "assets" / "everkeep.svg"
LOCK = json.loads((SOURCE / "glaze.lock.json").read_text(encoding="utf-8"))
EXPECTED_VERSION = "1.3.0"
EXPECTED_COMMIT = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
EXPECTED_ENTRYPOINT = "glaze-v1.3.0.css"
EXPECTED_ENTRYPOINT_BLOB = "4c3ad293ba9196e2e5a32700b530ec67fd01cef6"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)

if LOCK.get("version") != EXPECTED_VERSION or LOCK.get("lifecycle") != "Stable":
    raise SystemExit("Continuity Center Glaze lock must target 1.3.0 Stable")
if LOCK.get("stable_commit") != EXPECTED_COMMIT:
    raise SystemExit("unexpected Continuity Center Glaze V1.3 source revision")
if LOCK.get("entrypoint") != EXPECTED_ENTRYPOINT or LOCK.get("entrypoint_blob") != EXPECTED_ENTRYPOINT_BLOB:
    raise SystemExit("unexpected Continuity Center Glaze V1.3 entrypoint contract")
if LOCK.get("consumer_state") != "source-migrated-rendered-acceptance-pending":
    raise SystemExit("Continuity Center consumer state must remain fail-closed")


def git_blob_sha(data: bytes) -> str:
    prefix = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


def require_file(path: Path) -> Path:
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"missing or unsafe Continuity Center source: {path.relative_to(ROOT)}")
    return path


def read_glaze(name: str) -> bytes:
    if Path(name).name != name or not name.endswith(".css"):
        raise SystemExit(f"unsafe Glaze dependency: {name}")
    source_root = os.environ.get("GLAZE_UI_SOURCE")
    try:
        if source_root:
            data = require_file(Path(source_root) / "css" / name).read_bytes()
        else:
            url = f"https://raw.githubusercontent.com/{LOCK['repository']}/{LOCK['stable_commit']}/css/{name}"
            request = urllib.request.Request(url, headers={"User-Agent": "GoreeCloud-Continuity-Center-builder/1"})
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read()
    except urllib.error.URLError as exc:
        raise SystemExit(f"failed to fetch pinned Glaze dependency {name}: {exc}") from exc
    if name == EXPECTED_ENTRYPOINT and git_blob_sha(data) != EXPECTED_ENTRYPOINT_BLOB:
        raise SystemExit("Continuity Center Glaze V1.3 entrypoint integrity mismatch")
    return data


def collect_glaze(name: str, collected: dict[str, bytes]) -> None:
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
        collect_glaze(dependency, collected)
    collected[name] = data


if DIST.exists():
    if DIST.is_symlink():
        raise SystemExit("Continuity Center dist must not be a symlink")
    shutil.rmtree(DIST)
(DIST / "assets").mkdir(parents=True)

for name in ("index.html", "404.html", "_headers", "robots.txt", "sitemap.xml"):
    shutil.copy2(require_file(SOURCE / name), DIST / name)
for name in ("style.css", "site-polish.css", "v1.3-site.css"):
    shutil.copy2(require_file(SOURCE / name), DIST / "assets" / name)
shutil.copy2(require_file(ICON), DIST / "assets" / "everkeep.svg")

glaze: dict[str, bytes] = {}
collect_glaze(EXPECTED_ENTRYPOINT, glaze)
for name, data in sorted(glaze.items()):
    (DIST / "assets" / name).write_bytes(data)

print(
    f"Built Continuity Center with canonical Everkeep identity and GLAZE UI {EXPECTED_VERSION} Stable "
    f"pinned to {EXPECTED_COMMIT}; rendered, recovery-effect, deployment, and production acceptance remain separate"
)
