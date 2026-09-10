#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import argparse
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PUBLIC_MANAGER_ORIGIN = "https://manage.goreecloud.com/"
PRIVATE_MANAGER_HOST = "manager.goreecloud.com"
EXPECTED_VERSION = "1.3.0"
EXPECTED_COMMIT = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
EXPECTED_ENTRYPOINT = "glaze-v1.3.0.css"
EXPECTED_ENTRYPOINT_BLOB = "4c3ad293ba9196e2e5a32700b530ec67fd01cef6"
EXPECTED_MANAGER_MARK_BLOB = "024d82d5b5911e426216dfbd6a19d95cd6d71fc3"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)
parser = argparse.ArgumentParser()
parser.add_argument("--dist", action="store_true")
args = parser.parse_args()
BASE = DIST if args.dist else ROOT
errors: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    prefix = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


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
            if "stylesheet" in rel.split() and ".candidate.css" in href:
                errors.append(f"direct Candidate stylesheet imports are forbidden: {href}")
        if tag == "a":
            href = values.get("href", "")
            if href.startswith("http://"):
                errors.append(f"external navigation must use HTTPS: {href}")


lock = json.loads((ROOT / "glaze.lock.json").read_text(encoding="utf-8"))
check(lock.get("version") == EXPECTED_VERSION, "Glaze version must be 1.3.0")
check(lock.get("lifecycle") == "Stable", "Glaze lifecycle must be Stable")
check(lock.get("stable_commit") == EXPECTED_COMMIT, "Glaze Stable commit must be exact")
check(lock.get("entrypoint") == EXPECTED_ENTRYPOINT, "Glaze Stable entrypoint must be exact")
check(lock.get("entrypoint_blob") == EXPECTED_ENTRYPOINT_BLOB, "Glaze Stable entrypoint blob must be exact")
check(lock.get("consumer_state") == "source-migrated-rendered-acceptance-pending", "Manager consumer state must remain fail-closed")

html = (BASE / "index.html").read_text(encoding="utf-8")
nf = (BASE / "404.html").read_text(encoding="utf-8")
css = (BASE / "assets" / "site.css" if args.dist else ROOT / "site.css").read_text(encoding="utf-8")
v13 = (BASE / "assets" / "v1.3-site.css" if args.dist else ROOT / "v1.3-site.css").read_text(encoding="utf-8")
js = (BASE / "assets" / "site.js" if args.dist else ROOT / "site.js").read_text(encoding="utf-8")
for page in (html, nf):
    PublicHtmlAudit().feed(page)
    for marker in (
        'data-glaze-version="1.3.0"',
        'name="goreecloud-glaze-ui" content="1.3.0"',
        f'name="goreecloud-glaze-source-revision" content="{EXPECTED_COMMIT}"',
        'name="goreecloud-glaze-consumer-state" content="source-migrated-rendered-acceptance-pending"',
        '/assets/glaze-v1.3.0.css',
        '/assets/v1.3-site.css',
    ):
        check(marker in page, f"missing Manager V1.3 page marker: {marker}")
    for stale in (
        'data-glaze-version="2.2.0"', 'content="2.2.0"', 'glaze-2.2.0.css',
        'glaze-ui-2.1.0.css', 'data-glaze-ui="2.1.0"', 'GLAZE UI 2.2 Stable',
    ):
        check(stale not in page, f"superseded active Manager Glaze target remains: {stale}")

for marker in (
    "--manager-v13-control:48px", "--manager-v13-control-assisted:56px",
    "focus-visible", "pointer:coarse", "prefers-reduced-motion:reduce",
    "prefers-reduced-transparency:reduce", "prefers-contrast:more",
    "forced-colors:active", "@media print",
):
    check(marker in v13, f"missing Manager V1.3 adaptation: {marker}")
check("min-height:48px" in css or "--manager-v13-control:48px" in v13, "48px interaction floor missing")
check("localStorage" in js and all(choice in js for choice in ("system", "light", "dark")), "appearance modes missing")
check("fonts.googleapis" not in html + css + v13, "remote fonts are forbidden")
check("googletagmanager" not in html.lower(), "analytics/tracker runtime is forbidden")
check("segment.com" not in html.lower(), "analytics/tracker runtime is forbidden")

headers = (BASE / "_headers").read_text(encoding="utf-8")
check("Content-Security-Policy:" in headers, "Content Security Policy missing")
check("connect-src 'none'" in headers, "public website must not make browser network API connections")
check("Referrer-Policy: no-referrer" in headers, "strict referrer policy missing")

source_mark = ROOT / "assets" / "manager-mark.svg"
check(source_mark.is_file() and not source_mark.is_symlink(), "Manager mark missing or unsafe")
if source_mark.is_file():
    check(blob_sha(source_mark) == EXPECTED_MANAGER_MARK_BLOB, "Manager mark diverged from canonical branding asset")
check("noindex,nofollow,noarchive" in html, "Manager must remain noindex before public deployment acceptance")
check(f'rel="canonical" href="{PUBLIC_MANAGER_ORIGIN}"' in html, "Manager public canonical must use manage.goreecloud.com")
check("manage.goreecloud.com" in html, "Manager public hostname identity is missing")
check(PRIVATE_MANAGER_HOST not in html, "private Manager application hostname must not be advertised by public site")
check("Disallow: /" in (BASE / "robots.txt").read_text(encoding="utf-8"), "Manager robots must block indexing before public deployment acceptance")
check("Conceptual · no live data" in html, "Manager conceptual graphic must be labeled non-live")
for marker in (
    "NetBird, Healthchecks, Uptime Kuma, Beszel, Kopia, and GoreeCloud Tasks",
    "No direct Docker socket", "Production remains separately unapproved",
    "Current GLAZE UI V1.3 source reconciliation under review",
):
    check(marker in html, f"current Manager authority/status marker missing: {marker}")

if args.dist:
    entry = DIST / "assets" / EXPECTED_ENTRYPOINT
    check(entry.is_file() and not entry.is_symlink(), "built Glaze V1.3 entrypoint missing")
    if entry.is_file():
        check(blob_sha(entry) == EXPECTED_ENTRYPOINT_BLOB, "built Glaze V1.3 entrypoint integrity mismatch")
    built_mark = DIST / "assets" / "manager-mark.svg"
    check(built_mark.is_file(), "built Manager mark missing")
    if built_mark.is_file():
        check(blob_sha(built_mark) == EXPECTED_MANAGER_MARK_BLOB, "built Manager mark integrity mismatch")
    seen: set[str] = set()
    def visit(name: str) -> None:
        if name in seen:
            return
        path = DIST / "assets" / name
        check(path.is_file() and not path.is_symlink(), f"missing built Glaze dependency: {name}")
        if not path.is_file():
            return
        seen.add(name)
        for statement in re.findall(r"@import[^;]+;", path.read_text(encoding="utf-8"), flags=re.IGNORECASE):
            check("http://" not in statement.lower() and "https://" not in statement.lower() and "//" not in statement, f"remote built Glaze import: {statement}")
            match = IMPORT_RE.search(statement)
            check(match is not None, f"unsupported built Glaze import: {statement}")
            if match:
                visit(match.group(1))
    visit(EXPECTED_ENTRYPOINT)
    check("glaze-v1.2.0.css" in seen, "V1.3 inherited Stable dependency closure is incomplete")
    check(not any("glaze-2.2" in path.name for path in (DIST / "assets").iterdir()), "obsolete Glaze 2.2 asset remains in built artifact")

if errors:
    print("Manager public website validation failed:", file=sys.stderr)
    for error in errors:
        print(f" - {error}", file=sys.stderr)
    raise SystemExit(1)
print(f"Manager public website GLAZE UI V1.3 validation passed ({'dist' if args.dist else 'source'}); private-runtime and production acceptance remain separate")
