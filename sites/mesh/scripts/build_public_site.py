#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "website"
DIST = ROOT / "dist"
LOCK = json.loads((SOURCE / "glaze.lock.json").read_text(encoding="utf-8"))
PUBLIC_FILES = ("index.html", "404.html", "_headers", "robots.txt")
LOCAL_ASSETS = ("site.css", "v1.3-site.css", "site.js")
EXPECTED_VERSION = "1.3.0"
EXPECTED_COMMIT = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
EXPECTED_ENTRYPOINT = "glaze-v1.3.0.css"
EXPECTED_ENTRYPOINT_BLOB = "4c3ad293ba9196e2e5a32700b530ec67fd01cef6"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)

if LOCK.get("version") != EXPECTED_VERSION or LOCK.get("lifecycle") != "Stable":
    raise SystemExit("Glaze consumer lock must target 1.3.0 Stable")
if LOCK.get("stable_commit") != EXPECTED_COMMIT:
    raise SystemExit("unexpected Glaze V1.3 Stable source revision")
if LOCK.get("entrypoint") != EXPECTED_ENTRYPOINT or LOCK.get("entrypoint_blob") != EXPECTED_ENTRYPOINT_BLOB:
    raise SystemExit("unexpected Glaze V1.3 Stable entrypoint contract")
if LOCK.get("consumer_state") != "source-migrated-rendered-acceptance-pending":
    raise SystemExit("Mesh consumer state must remain fail-closed before rendered acceptance")


def git_blob_sha(data: bytes) -> str:
    prefix = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


def require_file(path: Path) -> Path:
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"missing or unsafe public source: {path.relative_to(ROOT)}")
    return path


def read_glaze(name: str) -> bytes:
    if Path(name).name != name or not name.endswith(".css"):
        raise SystemExit(f"unsafe Glaze stylesheet dependency: {name}")
    source_root = os.environ.get("GLAZE_UI_SOURCE")
    if source_root:
        data = require_file(Path(source_root) / "css" / name).read_bytes()
    else:
        url = f"https://raw.githubusercontent.com/{LOCK['repository']}/{LOCK['stable_commit']}/css/{name}"
        request = urllib.request.Request(url, headers={"User-Agent": "GoreeCloud-public-site-builder/1"})
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read()
    if name == EXPECTED_ENTRYPOINT:
        actual_sha = git_blob_sha(data)
        if actual_sha != EXPECTED_ENTRYPOINT_BLOB:
            raise SystemExit(f"Glaze V1.3 entrypoint integrity mismatch: {actual_sha} != {EXPECTED_ENTRYPOINT_BLOB}")
    return data


def collect_glaze(name: str, collected: dict[str, bytes]) -> None:
    if name in collected:
        return
    data = read_glaze(name)
    text = data.decode("utf-8")
    for statement in re.findall(r"@import[^;]+;", text, flags=re.IGNORECASE):
        if "http://" in statement.lower() or "https://" in statement.lower() or "//" in statement:
            raise SystemExit(f"remote Glaze import is forbidden in pinned consumer bundle: {statement}")
        match = IMPORT_RE.search(statement)
        if not match:
            raise SystemExit(f"unsupported Glaze import syntax in pinned consumer bundle: {statement}")
        dependency = match.group(1)
        if Path(dependency).name != dependency or not dependency.endswith(".css"):
            raise SystemExit(f"unsafe Glaze import dependency: {dependency}")
        collect_glaze(dependency, collected)
    collected[name] = data


if DIST.exists():
    shutil.rmtree(DIST)
(DIST / "assets").mkdir(parents=True)

for name in PUBLIC_FILES:
    shutil.copy2(require_file(SOURCE / name), DIST / name)
if (SOURCE / "sitemap.xml").exists():
    shutil.copy2(require_file(SOURCE / "sitemap.xml"), DIST / "sitemap.xml")
for name in LOCAL_ASSETS:
    source_path = require_file(SOURCE / name)
    destination = DIST / "assets" / name
    if name == "site.css":
        destination.write_bytes(b'@import url("./v1.3-site.css");\n' + source_path.read_bytes())
    else:
        shutil.copy2(source_path, destination)
for asset in sorted((SOURCE / "assets").iterdir()):
    if asset.is_symlink() or not asset.is_file():
        raise SystemExit(f"unsafe public asset: {asset.relative_to(ROOT)}")
    shutil.copy2(asset, DIST / "assets" / asset.name)

stylesheets: dict[str, bytes] = {}
collect_glaze(EXPECTED_ENTRYPOINT, stylesheets)
for name, data in sorted(stylesheets.items()):
    (DIST / "assets" / name).write_bytes(data)

print(
    f"Built Mesh public site with GLAZE UI {LOCK['version']} {LOCK['lifecycle']} "
    f"pinned to {LOCK['stable_commit']}; rendered and production acceptance remain separate"
)
