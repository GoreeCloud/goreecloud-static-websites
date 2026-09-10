#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import re

EXPECTED_VERSION = "1.3.0"
EXPECTED_COMMIT = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
EXPECTED_ENTRYPOINT = "glaze-v1.3.0.css"
EXPECTED_ENTRYPOINT_BLOB = "4c3ad293ba9196e2e5a32700b530ec67fd01cef6"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)

parser = argparse.ArgumentParser(description="Validate a simple GoreeCloud static site package")
parser.add_argument("site")
parser.add_argument("--dist", action="store_true")
args = parser.parse_args()
source = Path(args.site)
root = source / "dist" if args.dist else source

for name in ("index.html", "404.html", "_headers"):
    if not (root / name).is_file():
        raise SystemExit(f"missing required static-site file: {root / name}")
lock = json.loads((source / "glaze.lock.json").read_text(encoding="utf-8"))
for key, expected in {
    "version": EXPECTED_VERSION,
    "lifecycle": "Stable",
    "stable_commit": EXPECTED_COMMIT,
    "entrypoint": EXPECTED_ENTRYPOINT,
    "entrypoint_blob": EXPECTED_ENTRYPOINT_BLOB,
    "consumer_state": "source-migrated-rendered-acceptance-pending",
}.items():
    if lock.get(key) != expected:
        raise SystemExit(f"invalid GLAZE UI V1.3 lock field {key}: {lock.get(key)!r}")

index = (root / "index.html").read_text(encoding="utf-8")
error = (root / "404.html").read_text(encoding="utf-8")
headers = (root / "_headers").read_text(encoding="utf-8")
for page_name, page in (("index.html", index), ("404.html", error)):
    for marker in (
        'data-glaze-version="1.3.0"',
        'name="goreecloud-glaze-ui" content="1.3.0"',
        f'name="goreecloud-glaze-source-revision" content="{EXPECTED_COMMIT}"',
        'name="goreecloud-glaze-consumer-state" content="source-migrated-rendered-acceptance-pending"',
        '/assets/glaze-v1.3.0.css',
        '/assets/v1.3-site.css',
        'glaze-canvas',
    ):
        if marker not in page:
            raise SystemExit(f"{page_name} is missing GLAZE UI V1.3 marker: {marker}")
    for stale in (
        'glaze-ui-2.1.0.css', 'data-glaze-ui="2.1.0"', 'content="2.1.0"',
        'glaze-2.2.0.css', 'data-glaze-version="2.2.0"', 'content="2.2.0"',
    ):
        if stale in page:
            raise SystemExit(f"{page_name} activates superseded Glaze source: {stale}")

for required_header in ("Content-Security-Policy:", "X-Content-Type-Options: nosniff", "frame-ancestors 'none'", "Permissions-Policy:"):
    if required_header not in headers:
        raise SystemExit(f"required security header missing: {required_header}")
for prohibited in ("google-analytics", "googletagmanager", "fonts.googleapis.com", "segment.com"):
    if prohibited in (index + error).lower():
        raise SystemExit(f"prohibited runtime dependency: {prohibited}")

v13 = root / "assets" / "v1.3-site.css" if args.dist else source / "v1.3-site.css"
if not v13.is_file():
    raise SystemExit("V1.3 consumer adaptation is missing")
v13_text = v13.read_text(encoding="utf-8")
for marker in (
    "48px", "56px", "focus-visible", "pointer:coarse", "prefers-reduced-motion:reduce",
    "prefers-reduced-transparency:reduce", "prefers-contrast:more", "forced-colors:active", "@media print",
):
    if marker not in v13_text:
        raise SystemExit(f"V1.3 consumer adaptation marker missing: {marker}")

if args.dist:
    def blob_sha(path: Path) -> str:
        data = path.read_bytes()
        return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data, usedforsecurity=False).hexdigest()
    entry = root / "assets" / EXPECTED_ENTRYPOINT
    if not entry.is_file() or entry.is_symlink():
        raise SystemExit("built V1.3 Stable entrypoint is missing or unsafe")
    if blob_sha(entry) != EXPECTED_ENTRYPOINT_BLOB:
        raise SystemExit("built V1.3 Stable entrypoint integrity mismatch")
    seen: set[str] = set()
    def visit(name: str) -> None:
        if name in seen:
            return
        path = root / "assets" / name
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"missing built Glaze dependency: {name}")
        seen.add(name)
        for statement in re.findall(r"@import[^;]+;", path.read_text(encoding="utf-8"), flags=re.IGNORECASE):
            if "http://" in statement.lower() or "https://" in statement.lower() or "//" in statement:
                raise SystemExit(f"remote built Glaze import is forbidden: {statement}")
            match = IMPORT_RE.search(statement)
            if not match:
                raise SystemExit(f"unsupported built Glaze import syntax: {statement}")
            visit(match.group(1))
    visit(EXPECTED_ENTRYPOINT)
    if "glaze-v1.2.0.css" not in seen:
        raise SystemExit("V1.3 inherited Stable dependency closure is incomplete")
    if any("glaze-ui-2.1.0.css" in path.name or "glaze-2.2" in path.name for path in (root / "assets").iterdir()):
        raise SystemExit("superseded active Glaze asset remains in built artifact")

print(f"validated GLAZE UI V1.3 simple static site: {root}")
