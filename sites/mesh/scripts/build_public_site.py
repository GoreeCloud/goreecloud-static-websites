#!/usr/bin/env python3
"""Build Mesh Center as an exact GLAZE UI V1.4 publication artifact."""
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
EXPECTED_VERSION = "1.4.0"
EXPECTED_COMMIT = "84cb3db4884042f0fa25ed6d475a127fb110f596"
EXPECTED_ENTRYPOINT = "glaze-v1.4.0.css"
EXPECTED_ENTRYPOINT_BLOB = "d48a9bc317090d152799769271de0fb4325494c4"
LEGACY_COMMIT = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)

for key, expected in {
    "version": EXPECTED_VERSION,
    "lifecycle": "Stable",
    "repository": "GoreeCloud/goreecloud-glaze-ui",
    "stable_commit": EXPECTED_COMMIT,
    "entrypoint": EXPECTED_ENTRYPOINT,
    "entrypoint_blob": EXPECTED_ENTRYPOINT_BLOB,
    "consumer_state": "build-migrated-rendered-acceptance-pending",
}.items():
    if LOCK.get(key) != expected:
        raise SystemExit(f"unexpected Mesh GLAZE UI V1.4 lock value for {key}: {LOCK.get(key)!r}")


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data, usedforsecurity=False).hexdigest()


def require_file(path: Path) -> Path:
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"missing or unsafe public source: {path.relative_to(ROOT)}")
    return path


def render(text: str) -> str:
    replacements = (
        ('data-glaze-version="1.3.0"', 'data-glaze-version="1.4.0"'),
        ('name="goreecloud-glaze-ui" content="1.3.0"', 'name="goreecloud-glaze-ui" content="1.4.0"'),
        (f'name="goreecloud-glaze-source-revision" content="{LEGACY_COMMIT}"', f'name="goreecloud-glaze-source-revision" content="{EXPECTED_COMMIT}"'),
        ('name="goreecloud-glaze-consumer-state" content="source-migrated-rendered-acceptance-pending"', 'name="goreecloud-glaze-consumer-state" content="build-migrated-rendered-acceptance-pending"'),
        ('GLAZE UI V1.3', 'GLAZE UI V1.4'),
        ('Glaze UI V1.3', 'Glaze UI V1.4'),
        (LEGACY_COMMIT, EXPECTED_COMMIT),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    text = text.replace('/assets/glaze-v1.3.0.css', '/assets/glaze-v1.4.0.css')
    text = text.replace('<link rel="stylesheet" href="/assets/v1.3-site.css">', '<link rel="stylesheet" href="/assets/v1.3-site.css" data-glaze-consumer-adaptation="1.3-inherited">')
    text = text.replace('<link rel="stylesheet" href="/assets/glaze-v1.4.0.css">', '<link rel="stylesheet" href="/assets/glaze-v1.4.0.css" data-glaze-ui="1.4.0">')
    return text


def read_glaze(name: str) -> bytes:
    if Path(name).name != name or not name.endswith(".css"):
        raise SystemExit(f"unsafe Glaze stylesheet dependency: {name}")
    source_root = os.environ.get("GLAZE_UI_SOURCE")
    if source_root:
        path = Path(source_root) / "css" / name
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"missing or unsafe pinned Glaze source: {name}")
        data = path.read_bytes()
    else:
        url = f"https://raw.githubusercontent.com/{LOCK['repository']}/{LOCK['stable_commit']}/css/{name}"
        request = urllib.request.Request(url, headers={"User-Agent": "GoreeCloud-mesh-public-site-builder/1.4"})
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read()
    if name == EXPECTED_ENTRYPOINT and git_blob_sha(data) != EXPECTED_ENTRYPOINT_BLOB:
        raise SystemExit("Mesh GLAZE UI V1.4 entrypoint integrity mismatch")
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
        collect_glaze(match.group(1), collected)
    collected[name] = data


if DIST.exists():
    if DIST.is_symlink():
        raise SystemExit("Mesh dist must not be a symlink")
    shutil.rmtree(DIST)
(DIST / "assets").mkdir(parents=True)

for name in PUBLIC_FILES:
    source = require_file(SOURCE / name)
    target = DIST / name
    shutil.copy2(source, target)
    if name.endswith(".html"):
        target.write_text(render(target.read_text(encoding="utf-8")), encoding="utf-8")
if (SOURCE / "sitemap.xml").exists():
    shutil.copy2(require_file(SOURCE / "sitemap.xml"), DIST / "sitemap.xml")
for name in LOCAL_ASSETS:
    source_path = require_file(SOURCE / name)
    destination = DIST / "assets" / name
    if source_path.suffix in {".css", ".js"}:
        data = render(source_path.read_text(encoding="utf-8"))
        if name == "site.css":
            data = '@import url("./v1.3-site.css");\n' + data
        destination.write_text(data, encoding="utf-8")
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

print(f"Built Mesh Center with GLAZE UI {EXPECTED_VERSION} Stable pinned to {EXPECTED_COMMIT}; runtime and production acceptance remain separate")
