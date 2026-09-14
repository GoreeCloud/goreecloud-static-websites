#!/usr/bin/env python3
"""Build the Manager public website as an exact GLAZE UI V1.4 publication artifact."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
LOCK = json.loads((ROOT / "glaze.lock.json").read_text(encoding="utf-8"))
PUBLIC_FILES = ("index.html", "404.html", "_headers", "robots.txt")
LOCAL_ASSETS = ("site.css", "v1.3-site.css", "site.js", "assets/manager-mark.svg")
EXPECTED_VERSION = "1.4.0"
EXPECTED_COMMIT = "84cb3db4884042f0fa25ed6d475a127fb110f596"
EXPECTED_ENTRYPOINT = "glaze-v1.4.0.css"
EXPECTED_ENTRYPOINT_BLOB = "d48a9bc317090d152799769271de0fb4325494c4"
LEGACY_VERSION = "1.3.0"
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
        raise SystemExit(f"unexpected Manager GLAZE UI V1.4 lock value for {key}: {LOCK.get(key)!r}")


def git_blob_sha(data: bytes) -> str:
    prefix = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


def require_file(path: Path) -> Path:
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"missing or unsafe public source: {path.relative_to(ROOT)}")
    return path


def render(text: str) -> str:
    replacements = (
        (f'data-glaze-version="{LEGACY_VERSION}"', f'data-glaze-version="{EXPECTED_VERSION}"'),
        (f'name="goreecloud-glaze-ui" content="{LEGACY_VERSION}"', f'name="goreecloud-glaze-ui" content="{EXPECTED_VERSION}"'),
        (f'name="goreecloud-glaze-source-revision" content="{LEGACY_COMMIT}"', f'name="goreecloud-glaze-source-revision" content="{EXPECTED_COMMIT}"'),
        ('name="goreecloud-glaze-consumer-state" content="source-migrated-rendered-acceptance-pending"', 'name="goreecloud-glaze-consumer-state" content="build-migrated-rendered-acceptance-pending"'),
        ("GLAZE UI V1.3 source target", "GLAZE UI V1.4 publication target"),
        ("GLAZE UI V1.3 source reconciliation", "GLAZE UI V1.4 publication reconciliation"),
        ("GLAZE UI V1.3 acceptance", "GLAZE UI V1.4 acceptance"),
        ("GLAZE UI V1.3", "GLAZE UI V1.4"),
        ("official Stable 1.3.0 source revision", "official Stable 1.4.0 source revision"),
        (LEGACY_COMMIT, EXPECTED_COMMIT),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    old_link = '<link rel="stylesheet" href="/assets/glaze-v1.3.0.css">'
    new_link = '<link rel="stylesheet" href="/assets/glaze-v1.4.0.css" data-glaze-ui="1.4.0">'
    text = text.replace(old_link, new_link)
    inherited = '<link rel="stylesheet" href="/assets/v1.3-site.css">'
    text = text.replace(inherited, '<link rel="stylesheet" href="/assets/v1.3-site.css" data-glaze-consumer-adaptation="1.3-inherited">')
    return text


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
            url = f"https://raw.githubusercontent.com/{LOCK['repository']}/{LOCK['stable_commit']}/css/{name}"
            request = urllib.request.Request(url, headers={"User-Agent": "GoreeCloud-Manager-public-site-builder/1.4"})
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read()
    except urllib.error.URLError as exc:
        raise SystemExit(f"failed to fetch pinned Glaze dependency {name}: {exc}") from exc
    if name == EXPECTED_ENTRYPOINT and git_blob_sha(data) != EXPECTED_ENTRYPOINT_BLOB:
        raise SystemExit("Manager GLAZE UI V1.4 entrypoint integrity mismatch")
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
        raise SystemExit("Manager public-site dist must not be a symlink")
    shutil.rmtree(DIST)
(DIST / "assets").mkdir(parents=True)

for name in PUBLIC_FILES:
    source = require_file(ROOT / name)
    target = DIST / name
    shutil.copy2(source, target)
    if name.endswith(".html"):
        target.write_text(render(target.read_text(encoding="utf-8")), encoding="utf-8")
if (ROOT / "sitemap.xml").exists():
    shutil.copy2(require_file(ROOT / "sitemap.xml"), DIST / "sitemap.xml")
for relative in LOCAL_ASSETS:
    source = require_file(ROOT / relative)
    target = DIST / "assets" / source.name
    if source.suffix in {".css", ".js"}:
        target.write_text(render(source.read_text(encoding="utf-8")), encoding="utf-8")
    else:
        shutil.copy2(source, target)

glaze: dict[str, bytes] = {}
collect_glaze(EXPECTED_ENTRYPOINT, glaze)
for name, data in sorted(glaze.items()):
    (DIST / "assets" / name).write_bytes(data)

print(
    f"Built Manager public site with GLAZE UI {EXPECTED_VERSION} Stable pinned to {EXPECTED_COMMIT}; "
    "private-runtime, platform-integration, Cloudflare, and production acceptance remain separate"
)
