#!/usr/bin/env python3
"""Validate retained Mesh Center source or exact GLAZE UI V1.4 publication artifact."""
from pathlib import Path
from html.parser import HTMLParser
import argparse
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "website"
DIST = ROOT / "dist"
parser = argparse.ArgumentParser()
parser.add_argument("--dist", action="store_true")
args = parser.parse_args()
BASE = DIST if args.dist else SOURCE
errors: list[str] = []

SOURCE_VERSION = "1.3.0"
SOURCE_COMMIT = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
PUBLICATION_VERSION = "1.4.0"
PUBLICATION_COMMIT = "84cb3db4884042f0fa25ed6d475a127fb110f596"
PUBLICATION_ENTRYPOINT = "glaze-v1.4.0.css"
PUBLICATION_ENTRYPOINT_BLOB = "d48a9bc317090d152799769271de0fb4325494c4"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data, usedforsecurity=False).hexdigest()


class PublicHtmlAudit(HTMLParser):
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "style" in values:
            errors.append("inline style attributes are forbidden by the public-site CSP")
        if tag == "script" and not values.get("src"):
            errors.append("inline scripts are forbidden by the public-site CSP")
        src = values.get("src", "")
        if src.startswith(("http://", "https://", "//")):
            errors.append(f"remote runtime source is forbidden: {src}")
        if tag == "link":
            href = values.get("href", "")
            rel = values.get("rel", "")
            if href.startswith(("http://", "https://", "//")) and "canonical" not in rel.split():
                errors.append(f"remote runtime link is forbidden: {href}")
        if tag == "a" and values.get("href", "").startswith("http://"):
            errors.append(f"external navigation must use HTTPS: {values.get('href')}")


def imported_stylesheet_closure(entrypoint: str) -> set[str]:
    seen: set[str] = set()
    def visit(name: str) -> None:
        if name in seen:
            return
        check(Path(name).name == name and name.endswith(".css"), f"unsafe built Glaze dependency: {name}")
        path = DIST / "assets" / name
        check(path.is_file() and not path.is_symlink(), f"missing built Glaze dependency: {name}")
        if not path.is_file() or path.is_symlink():
            return
        seen.add(name)
        for statement in re.findall(r"@import[^;]+;", path.read_text(encoding="utf-8"), flags=re.IGNORECASE):
            check("http://" not in statement.lower() and "https://" not in statement.lower() and "//" not in statement, f"remote built Glaze import: {statement}")
            match = IMPORT_RE.search(statement)
            check(match is not None, f"unsupported built Glaze import: {statement}")
            if match:
                visit(match.group(1))
    visit(entrypoint)
    return seen


lock = json.loads((SOURCE / "glaze.lock.json").read_text(encoding="utf-8"))
for key, expected in {
    "version": PUBLICATION_VERSION,
    "lifecycle": "Stable",
    "repository": "GoreeCloud/goreecloud-glaze-ui",
    "stable_commit": PUBLICATION_COMMIT,
    "entrypoint": PUBLICATION_ENTRYPOINT,
    "entrypoint_blob": PUBLICATION_ENTRYPOINT_BLOB,
    "consumer_state": "build-migrated-rendered-acceptance-pending",
}.items():
    check(lock.get(key) == expected, f"Mesh current publication lock mismatch for {key}: {lock.get(key)!r}")

html = (BASE / "index.html").read_text(encoding="utf-8")
nf = (BASE / "404.html").read_text(encoding="utf-8")
css = (BASE / "assets" / "site.css" if args.dist else SOURCE / "site.css").read_text(encoding="utf-8")
v13_css = (BASE / "assets" / "v1.3-site.css" if args.dist else SOURCE / "v1.3-site.css").read_text(encoding="utf-8")
js = (BASE / "assets" / "site.js" if args.dist else SOURCE / "site.js").read_text(encoding="utf-8")
for page in (BASE / "index.html", BASE / "404.html"):
    PublicHtmlAudit().feed(page.read_text(encoding="utf-8"))

if args.dist:
    required = (
        'data-glaze-version="1.4.0"',
        'name="goreecloud-glaze-ui" content="1.4.0"',
        f'name="goreecloud-glaze-source-revision" content="{PUBLICATION_COMMIT}"',
        'name="goreecloud-glaze-consumer-state" content="build-migrated-rendered-acceptance-pending"',
        '/assets/glaze-v1.4.0.css',
        'data-glaze-ui="1.4.0"',
    )
else:
    required = (
        'data-glaze-version="1.3.0"',
        'name="goreecloud-glaze-ui" content="1.3.0"',
        f'name="goreecloud-glaze-source-revision" content="{SOURCE_COMMIT}"',
        'name="goreecloud-glaze-consumer-state" content="source-migrated-rendered-acceptance-pending"',
        '/assets/glaze-v1.3.0.css',
    )
for page_name, page_text in (("index", html), ("404", nf)):
    for marker in required:
        check(marker in page_text, f"{page_name}: missing Mesh {'V1.4 publication' if args.dist else 'V1.3 template'} marker: {marker}")
    for stale in ('data-glaze-version="2.2.0"','name="goreecloud-glaze-ui" content="2.2.0"','/assets/glaze-2.2.0.css','Glaze UI 2.2 Stable'):
        check(stale not in page_text, f"{page_name}: superseded Glaze marker remains: {stale}")

for marker in (
    "--mesh-v13-control:48px", "--mesh-v13-control-coarse:56px", "pointer:coarse",
    "prefers-reduced-motion:reduce", "prefers-reduced-transparency:reduce", "prefers-contrast:more",
    "forced-colors:active", "focus-visible", "@media print",
):
    check(marker in v13_css, f"missing inherited Mesh V1.3 adaptation marker: {marker}")
check("prefers-reduced-motion:reduce" in css, "base reduced-motion fallback missing")
check("forced-colors:active" in css, "base forced-colors fallback missing")
check("prefers-contrast:more" in css, "base increased-contrast fallback missing")
check("data-reduce-transparency" in css, "base reduced-transparency fallback missing")
check("localStorage" in js and all(choice in js for choice in ("system", "light", "dark")), "appearance modes missing")
check("fonts.googleapis" not in html + css + v13_css, "remote fonts are forbidden")
check("googletagmanager" not in html.lower() and "segment.com" not in html.lower(), "analytics/tracker runtime is forbidden")
headers = (BASE / "_headers").read_text(encoding="utf-8")
for marker in ("Content-Security-Policy:", "connect-src 'none'", "Strict-Transport-Security: max-age=31536000", "Referrer-Policy: no-referrer"):
    check(marker in headers, f"Mesh security-header contract missing: {marker}")

mark = SOURCE / "assets" / "goreecloud-mesh-mark.svg"
check(mark.exists() and not mark.is_symlink(), "Mesh mark missing or unsafe")
if mark.exists():
    check(blob_sha(mark) == "5362a52bd9fb38379f083a4d894934ed1acf9b67", "Mesh mark diverged from canonical branding asset")
for marker in (
    "authority_transfer = false", 'rel="canonical" href="https://mesh.goreecloud.com/"',
    "Production acceptance stays explicit", "Mesh itself remains in Development", "Mesh Center remains planned",
    "8da8e52593dad045ed2356182b7ba755b789b79f",
):
    check(marker in html, f"Mesh public truth boundary missing: {marker}")

if args.dist:
    entrypoint = DIST / "assets" / PUBLICATION_ENTRYPOINT
    check(entrypoint.is_file() and not entrypoint.is_symlink(), "built GLAZE UI V1.4 entrypoint missing")
    if entrypoint.is_file():
        check(blob_sha(entrypoint) == PUBLICATION_ENTRYPOINT_BLOB, "built GLAZE UI V1.4 entrypoint integrity mismatch")
        imported_stylesheet_closure(PUBLICATION_ENTRYPOINT)
    check(css.startswith('@import url("./v1.3-site.css");'), "built Mesh CSS does not activate inherited V1.3 adaptation")
    check('data-glaze-consumer-adaptation="1.3-inherited"' in html, "built Mesh page does not identify inherited adaptation")
    built_mark = DIST / "assets" / mark.name
    check(built_mark.exists(), f"missing built product mark: {mark.name}")
    if built_mark.exists():
        check(blob_sha(built_mark) == blob_sha(mark), f"built product mark integrity mismatch: {mark.name}")

if errors:
    print("Mesh public website validation failed:", file=sys.stderr)
    for error in errors:
        print(f" - {error}", file=sys.stderr)
    raise SystemExit(1)
print(f"Mesh public website validation passed ({'V1.4 artifact' if args.dist else 'retained V1.3 source template'}); runtime and production acceptance remain separate")
