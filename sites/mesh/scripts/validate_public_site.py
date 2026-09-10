#!/usr/bin/env python3
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
PRODUCT = ROOT.name.lower()
parser = argparse.ArgumentParser()
parser.add_argument("--dist", action="store_true")
args = parser.parse_args()
BASE = DIST if args.dist else SOURCE
errors = []

EXPECTED_VERSION = "1.3.0"
EXPECTED_COMMIT = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
EXPECTED_ENTRYPOINT = "glaze-v1.3.0.css"
EXPECTED_ENTRYPOINT_BLOB = "4c3ad293ba9196e2e5a32700b530ec67fd01cef6"
EXPECTED_CONSUMER_STATE = "source-migrated-rendered-acceptance-pending"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)


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
                errors.append(f"direct Candidate stylesheet import is forbidden: {href}")
        if tag == "a":
            href = values.get("href", "")
            if href.startswith("http://"):
                errors.append(f"external navigation must use HTTPS: {href}")


def imported_stylesheet_closure(entrypoint: str) -> set[str]:
    assets = DIST / "assets"
    seen: set[str] = set()

    def visit(name: str) -> None:
        if name in seen:
            return
        check(Path(name).name == name and name.endswith(".css"), f"unsafe built Glaze stylesheet dependency: {name}")
        if Path(name).name != name or not name.endswith(".css"):
            return
        path = assets / name
        check(path.is_file() and not path.is_symlink(), f"missing built Glaze stylesheet dependency: {name}")
        if not path.is_file() or path.is_symlink():
            return
        seen.add(name)
        text = path.read_text(encoding="utf-8")
        for statement in re.findall(r"@import[^;]+;", text, flags=re.IGNORECASE):
            check("http://" not in statement.lower() and "https://" not in statement.lower() and "//" not in statement,
                  f"remote Glaze import is forbidden in built closure: {statement}")
            match = IMPORT_RE.search(statement)
            check(match is not None, f"unsupported Glaze import syntax in built closure: {statement}")
            if match is None:
                continue
            dependency = match.group(1)
            visit(dependency)

    visit(entrypoint)
    return seen


lock = json.loads((SOURCE / "glaze.lock.json").read_text(encoding="utf-8"))
check(lock.get("version") == EXPECTED_VERSION, "Glaze version must be 1.3.0")
check(lock.get("lifecycle") == "Stable", "Glaze lifecycle must be Stable")
check(lock.get("stable_commit") == EXPECTED_COMMIT, "Glaze V1.3 Stable source revision must be pinned")
check(lock.get("entrypoint") == EXPECTED_ENTRYPOINT, "Glaze V1.3 Stable entrypoint must be pinned")
check(lock.get("entrypoint_blob") == EXPECTED_ENTRYPOINT_BLOB, "Glaze V1.3 Stable entrypoint blob must be pinned")
check(lock.get("consumer_state") == EXPECTED_CONSUMER_STATE, "Mesh consumer state must remain fail-closed before rendered acceptance")

html = (BASE / "index.html").read_text(encoding="utf-8")
nf = (BASE / "404.html").read_text(encoding="utf-8")
css = (BASE / "assets" / "site.css" if args.dist else SOURCE / "site.css").read_text(encoding="utf-8")
v13_css = (BASE / "assets" / "v1.3-site.css" if args.dist else SOURCE / "v1.3-site.css").read_text(encoding="utf-8")
js = (BASE / "assets" / "site.js" if args.dist else SOURCE / "site.js").read_text(encoding="utf-8")
for page in (BASE / "index.html", BASE / "404.html"):
    PublicHtmlAudit().feed(page.read_text(encoding="utf-8"))

for page_name, page_text in (("index", html), ("404", nf)):
    for marker in (
        'data-glaze-version="1.3.0"',
        'name="goreecloud-glaze-ui" content="1.3.0"',
        f'name="goreecloud-glaze-source-revision" content="{EXPECTED_COMMIT}"',
        f'name="goreecloud-glaze-consumer-state" content="{EXPECTED_CONSUMER_STATE}"',
        '/assets/glaze-v1.3.0.css',
    ):
        check(marker in page_text, f"{page_name}: missing GLAZE UI V1.3 marker: {marker}")
    for stale in (
        'data-glaze-version="2.2.0"',
        'name="goreecloud-glaze-ui" content="2.2.0"',
        '/assets/glaze-2.2.0.css',
        'Glaze UI 2.2 Stable',
        '6731098b28dd0393faa878c70d989a221d714a20',
    ):
        check(stale not in page_text, f"{page_name}: superseded active Glaze 2.2 marker remains: {stale}")

for marker in (
    "--mesh-v13-control:48px",
    "--mesh-v13-control-coarse:56px",
    "pointer:coarse",
    "prefers-reduced-motion:reduce",
    "prefers-reduced-transparency:reduce",
    "prefers-contrast:more",
    "forced-colors:active",
    "focus-visible",
    "@media print",
):
    check(marker in v13_css, f"missing Mesh V1.3 accessibility/adaptation marker: {marker}")
check("prefers-reduced-motion:reduce" in css, "base reduced-motion fallback missing")
check("forced-colors:active" in css, "base forced-colors fallback missing")
check("prefers-contrast:more" in css, "base increased-contrast fallback missing")
check("data-reduce-transparency" in css, "base reduced-transparency fallback missing")
check("localStorage" in js and all(choice in js for choice in ("system", "light", "dark")), "appearance modes missing")
check("fonts.googleapis" not in html + css + v13_css, "remote fonts are forbidden")
check("googletagmanager" not in html.lower(), "analytics/tracker runtime is forbidden")
check("segment.com" not in html.lower(), "analytics/tracker runtime is forbidden")
headers = (BASE / "_headers").read_text(encoding="utf-8")
check("Content-Security-Policy:" in headers, "Content Security Policy missing")
check("connect-src 'none'" in headers, "public website must not make browser network API connections")
check("Strict-Transport-Security: max-age=31536000" in headers, "HSTS policy missing")
check("Referrer-Policy: no-referrer" in headers, "strict referrer policy missing")

if "mesh" in PRODUCT:
    mark = SOURCE / "assets" / "goreecloud-mesh-mark.svg"
    check(mark.exists(), "Mesh mark missing")
    if mark.exists():
        check(blob_sha(mark) == "5362a52bd9fb38379f083a4d894934ed1acf9b67", "Mesh mark diverged from canonical branding asset")
    check("authority_transfer = false" in html, "Mesh authority-transfer invariant missing")
    check('rel="canonical" href="https://mesh.goreecloud.com/"' in html, "Mesh intended canonical URL missing")
    check("Production acceptance stays explicit" in html, "Mesh production truth boundary missing")
    check("Mesh itself remains in Development" in html, "Mesh Development lifecycle boundary missing")
    check("Mesh Center remains planned" in html, "Mesh Center incomplete-state disclosure missing")
    check("8da8e52593dad045ed2356182b7ba755b789b79f" in html, "Mesh website truth baseline is stale or missing")
else:
    mark = SOURCE / "assets" / "manager-mark.svg"
    check(mark.exists(), "Manager mark missing")
    if mark.exists():
        check(blob_sha(mark) == "81d5d6659bf22ee61a1be46fce816031b835f967", "Manager mark diverged from approved product blob")
    check("noindex,nofollow,noarchive" in html, "Manager must remain noindex before public hostname approval")
    check("manager.goreecloud.com" not in html, "private Manager application hostname must not be advertised by public site")
    check("Disallow: /" in (BASE / "robots.txt").read_text(encoding="utf-8"), "Manager robots must block indexing before public hostname approval")
    check("Conceptual · no live data" in html, "Manager conceptual graphic must be labeled non-live")

if args.dist:
    entrypoint = DIST / "assets" / EXPECTED_ENTRYPOINT
    check(entrypoint.is_file(), "built GLAZE UI V1.3 Stable entrypoint missing")
    if entrypoint.is_file():
        check(blob_sha(entrypoint) == EXPECTED_ENTRYPOINT_BLOB, "built GLAZE UI V1.3 entrypoint integrity mismatch")
        closure = imported_stylesheet_closure(EXPECTED_ENTRYPOINT)
        check("glaze-v1.2.0.css" in closure, "canonical V1.3 inherited rendering foundation is incomplete")
    check(css.startswith('@import url("./v1.3-site.css");'), "built Mesh CSS does not activate the V1.3 consumer adaptation")
    built_mark = DIST / "assets" / mark.name
    check(built_mark.exists(), f"missing built product mark: {mark.name}")
    if built_mark.exists():
        check(blob_sha(built_mark) == blob_sha(mark), f"built product mark integrity mismatch: {mark.name}")
    check((DIST / "_headers").exists(), "built security headers missing")

if errors:
    print("Public website validation failed:", file=sys.stderr)
    for error in errors:
        print(f" - {error}", file=sys.stderr)
    raise SystemExit(1)
print(f"Public website GLAZE UI V1.3 validation passed ({'dist' if args.dist else 'source'}); rendered/production acceptance remains separate")
