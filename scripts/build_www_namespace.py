#!/usr/bin/env python3
"""Build all GoreeCloud informational websites into the governed www path namespace.

This is the canonical unified-publication builder. It preserves independent site-source
provenance and application-subdomain boundaries while mounting the informational sites
beneath https://www.goreecloud.com/<website-slug>. The final mounted artifact is normalized
to the current GLAZE UI Stable publication contract without rewriting historical source.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "sites" / "url-namespace.json"
OUTPUT = ROOT / "dist"
TEXT_SUFFIXES = {".html", ".css", ".js", ".mjs", ".json", ".xml", ".txt", ".webmanifest", ".svg"}
EXPECTED_NAMESPACE_STATE = "provider-cutover-verified"
GLAZE_VERSION = "1.4.1"
GLAZE_RELEASE_REVISION = "4fab9da0fad2e5c974e0e66ec88632c61745751c"
GLAZE_ENTRYPOINT = "glaze-v1.4.1.css"
GLAZE_ENTRYPOINT_BLOB = "4373cc859da9a329bcfb4cc56062ec639ad2ff93"
GLAZE_REPOSITORY = "GoreeCloud/goreecloud-glaze-ui"
IMPORT_RE = re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)', re.IGNORECASE)


def fail(message: str) -> None:
    raise RuntimeError(message)


def git_blob_sha(data: bytes) -> str:
    prefix = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


def load_registry() -> dict:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if data.get("canonical_origin") != "https://www.goreecloud.com":
        fail("unexpected canonical origin")
    if data.get("state") != EXPECTED_NAMESPACE_STATE:
        fail(f"URL namespace registry must be {EXPECTED_NAMESPACE_STATE} after verified cutover")
    return data


def run(command: list[str]) -> None:
    print("+ " + " ".join(command))
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode:
        fail(f"build command failed ({completed.returncode}): {' '.join(command)}")


def copy_checked(source: Path, destination: Path) -> None:
    if source.is_symlink():
        fail(f"symlink is not allowed in public artifact: {source.relative_to(ROOT)}")
    if source.is_dir():
        destination.mkdir(parents=True, exist_ok=True)
        for child in sorted(source.iterdir(), key=lambda item: item.name):
            copy_checked(child, destination / child.name)
    elif source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    else:
        fail(f"missing publication source: {source.relative_to(ROOT)}")


def static_artifact(entry: dict, staging: Path) -> Path:
    source = ROOT / entry["source_path"]
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    for relative in entry["static_allowlist"]:
        copy_checked(source / relative, staging / relative)
    return staging


def rewrite_legacy_origins(text: str, entries: list[dict], origin: str) -> str:
    for entry in entries:
        host = entry.get("current_public_host")
        if not host or host == "www.goreecloud.com":
            continue
        base = origin + entry["canonical_path"]
        text = text.replace(f"https://{host}", base)
        text = text.replace(f"http://{host}", base)
    return text


def prefix_root_relative_strings(text: str, path_prefix: str) -> str:
    if path_prefix == "/":
        return text
    escaped = re.escape(path_prefix.lstrip("/"))

    quoted = re.compile(rf"(?P<quote>['\"])/(?!/|{escaped}(?:/|['\"]))")
    text = quoted.sub(lambda match: f"{match.group('quote')}{path_prefix}/", text)

    css_url = re.compile(rf"url\(\s*/(?!/|{escaped}(?:/|\)))", re.IGNORECASE)
    text = css_url.sub(f"url({path_prefix}/", text)
    return text


def rewrite_artifact(root: Path, entry: dict, entries: list[dict], origin: str) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or path.name == "_headers":
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"robots.txt", "sitemap.xml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            fail(f"text publication file is not UTF-8: {path}")
        text = rewrite_legacy_origins(text, entries, origin)
        text = prefix_root_relative_strings(text, entry["canonical_path"])
        path.write_text(text, encoding="utf-8")


def read_glaze_css(name: str) -> bytes:
    if Path(name).name != name or not name.endswith(".css"):
        fail(f"unsafe GLAZE UI dependency: {name}")
    source_root = os.environ.get("GLAZE_UI_SOURCE")
    try:
        if source_root:
            path = Path(source_root) / "css" / name
            if not path.is_file() or path.is_symlink():
                fail(f"missing or unsafe pinned GLAZE UI source: {name}")
            data = path.read_bytes()
        else:
            url = f"https://raw.githubusercontent.com/{GLAZE_REPOSITORY}/{GLAZE_RELEASE_REVISION}/css/{name}"
            request = urllib.request.Request(url, headers={"User-Agent": "GoreeCloud-unified-www-builder/1.4.1"})
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read()
    except urllib.error.URLError as exc:
        fail(f"failed to fetch pinned GLAZE UI dependency {name}: {exc}")
    if name == GLAZE_ENTRYPOINT and git_blob_sha(data) != GLAZE_ENTRYPOINT_BLOB:
        fail("GLAZE UI V1.4.1 entrypoint integrity mismatch")
    return data


def collect_glaze_css() -> dict[str, bytes]:
    collected: dict[str, bytes] = {}

    def collect(name: str) -> None:
        if name in collected:
            return
        data = read_glaze_css(name)
        text = data.decode("utf-8")
        for statement in re.findall(r"@import[^;]+;", text, flags=re.IGNORECASE):
            lowered = statement.lower()
            if "http://" in lowered or "https://" in lowered or "//" in statement:
                fail(f"remote GLAZE UI import is forbidden: {statement}")
            match = IMPORT_RE.search(statement)
            if not match:
                fail(f"unsupported GLAZE UI import syntax: {statement}")
            dependency = match.group(1)
            if Path(dependency).name != dependency or not dependency.endswith(".css"):
                fail(f"unsafe GLAZE UI import dependency: {dependency}")
            collect(dependency)
        collected[name] = data

    collect(GLAZE_ENTRYPOINT)
    return collected


def replace_named_meta(text: str, name: str, content: str) -> str:
    pattern = re.compile(rf'<meta\b(?=[^>]*\bname=["\']{re.escape(name)}["\'])[^>]*>', re.IGNORECASE)
    tag = f'<meta name="{name}" content="{content}">'
    if pattern.search(text):
        return pattern.sub(tag, text, count=1)
    if "</head>" not in text.lower():
        return text
    return re.sub(r"</head>", f"  {tag}\n</head>", text, count=1, flags=re.IGNORECASE)


def normalize_current_glaze_claims(text: str) -> str:
    replacements = (
        ("GLAZE UI V1.3 source target", "GLAZE UI V1.4.1 source target"),
        ("GLAZE UI V1.4 source target", "GLAZE UI V1.4.1 source target"),
        ("Current Official Stable · 1.3.0", "Current Official Stable · 1.4.1"),
        ("Current Official Stable · 1.4.0", "Current Official Stable · 1.4.1"),
        ("1.3.0 current Official Stable", "1.4.1 current Official Stable"),
        ("1.4.0 current Official Stable", "1.4.1 current Official Stable"),
        ("GLAZE UI 1.3.0 is the current Official Stable", "GLAZE UI 1.4.1 is the current Official Stable"),
        ("GLAZE UI 1.4.0 is the current Official Stable", "GLAZE UI 1.4.1 is the current Official Stable"),
        ("GLAZE UI V1.3 / 1.3.0", "GLAZE UI V1.4 / 1.4.1"),
        ("GLAZE UI V1.4 / 1.4.0", "GLAZE UI V1.4 / 1.4.1"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def normalize_html(text: str, entry: dict, origin: str, root_index: bool) -> str:
    if "</head>" not in text.lower():
        return text

    prefix = entry["canonical_path"]
    asset_href = "/assets/" + GLAZE_ENTRYPOINT if prefix == "/" else f"{prefix}/assets/{GLAZE_ENTRYPOINT}"

    text = replace_named_meta(text, "goreecloud-glaze-ui", GLAZE_VERSION)
    text = replace_named_meta(text, "goreecloud-glaze-source-revision", GLAZE_RELEASE_REVISION)
    text = re.sub(r'data-glaze-version=["\'][^"\']+["\']', f'data-glaze-version="{GLAZE_VERSION}"', text, flags=re.IGNORECASE)
    text = normalize_current_glaze_claims(text)

    stable_link_pattern = re.compile(
        r'<link\b(?=[^>]*\brel=["\']stylesheet["\'])(?=[^>]*\bhref=["\'][^"\']*glaze-v1\.(?:3\.0|4\.0|4\.1)\.css(?:\?[^"\']*)?["\'])[^>]*>',
        re.IGNORECASE,
    )
    stable_link = f'<link rel="stylesheet" href="{asset_href}" data-glaze-ui="{GLAZE_VERSION}">'
    if stable_link_pattern.search(text):
        text = stable_link_pattern.sub("", text)
        first_stylesheet = re.search(r'<link\b(?=[^>]*\brel=["\']stylesheet["\'])[^>]*>', text, flags=re.IGNORECASE)
        if first_stylesheet:
            text = text[: first_stylesheet.start()] + stable_link + "\n  " + text[first_stylesheet.start() :]
        else:
            text = re.sub(r"</head>", f"  {stable_link}\n</head>", text, count=1, flags=re.IGNORECASE)
    elif asset_href not in text:
        first_stylesheet = re.search(r'<link\b(?=[^>]*\brel=["\']stylesheet["\'])[^>]*>', text, flags=re.IGNORECASE)
        if first_stylesheet:
            text = text[: first_stylesheet.start()] + stable_link + "\n  " + text[first_stylesheet.start() :]
        else:
            text = re.sub(r"</head>", f"  {stable_link}\n</head>", text, count=1, flags=re.IGNORECASE)

    if root_index:
        canonical_url = origin + "/" if prefix == "/" else origin + prefix + "/"
        canonical_pattern = re.compile(r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*>', re.IGNORECASE)
        canonical_tag = f'<link rel="canonical" href="{canonical_url}">'
        if canonical_pattern.search(text):
            text = canonical_pattern.sub(canonical_tag, text, count=1)
        else:
            text = re.sub(r"</head>", f"  {canonical_tag}\n</head>", text, count=1, flags=re.IGNORECASE)

        og_pattern = re.compile(r'<meta\b(?=[^>]*\bproperty=["\']og:url["\'])[^>]*>', re.IGNORECASE)
        if og_pattern.search(text):
            text = og_pattern.sub(f'<meta property="og:url" content="{canonical_url}">', text, count=1)

    return text


def normalize_publication(root: Path, entry: dict, origin: str, glaze_css: dict[str, bytes]) -> None:
    assets = root / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for name, data in sorted(glaze_css.items()):
        (assets / name).write_bytes(data)

    for page in root.rglob("*.html"):
        if not page.is_file() or page.is_symlink():
            fail(f"unsafe HTML publication file: {page}")
        text = page.read_text(encoding="utf-8")
        text = normalize_html(text, entry, origin, root_index=(page.parent == root and page.name == "index.html"))
        page.write_text(text, encoding="utf-8")


def prefixed_header_block(raw: str, prefix: str, site_id: str) -> str:
    if prefix == "/":
        return raw.rstrip() + "\n"
    output = [f"# {site_id} mounted at {prefix}"]
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or line[:1].isspace():
            output.append(line)
            continue
        if stripped.startswith("http://") or stripped.startswith("https://"):
            fail(f"absolute _headers selector is unsupported for {site_id}: {stripped}")
        if not stripped.startswith("/"):
            fail(f"unexpected _headers selector for {site_id}: {stripped}")
        if stripped == "/":
            selector = prefix + "/"
        elif stripped == "/*":
            selector = prefix + "/*"
        else:
            selector = prefix + stripped
        output.append(selector)
    return "\n".join(output).rstrip() + "\n"


def verify_publication(root: Path, entry: dict, entries: list[dict], origin: str) -> None:
    prefix = entry["canonical_path"]
    index = root / "index.html"
    if not index.is_file():
        fail(f"{entry['id']} mounted artifact has no index.html")

    index_text = index.read_text(encoding="utf-8")
    canonical_url = origin + "/" if prefix == "/" else origin + prefix + "/"
    required_markers = (
        f'<link rel="canonical" href="{canonical_url}">',
        f'<meta name="goreecloud-glaze-ui" content="{GLAZE_VERSION}">',
        f'<meta name="goreecloud-glaze-source-revision" content="{GLAZE_RELEASE_REVISION}">',
        GLAZE_ENTRYPOINT,
    )
    for marker in required_markers:
        if marker not in index_text:
            fail(f"{entry['id']} mounted index is missing required current-publication marker: {marker}")

    stale_current_markers = (
        "GLAZE UI V1.3 source target",
        "GLAZE UI V1.4 source target",
        "Current Official Stable · 1.3.0",
        "Current Official Stable · 1.4.0",
        "1.3.0 current Official Stable",
        "1.4.0 current Official Stable",
        "GLAZE UI 1.3.0 is the current Official Stable",
        "GLAZE UI 1.4.0 is the current Official Stable",
    )
    for marker in stale_current_markers:
        if marker in index_text:
            fail(f"{entry['id']} mounted index still exposes stale current-state wording: {marker}")

    legacy_hosts = [item.get("current_public_host") for item in entries if item.get("current_public_host") not in {None, "www.goreecloud.com"}]
    escaped = re.escape(prefix.lstrip("/"))
    bad_root_ref = None if prefix == "/" else re.compile(rf"['\"]/(?!/|{escaped}(?:/|['\"]))")
    problems: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.name == "_headers":
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"robots.txt", "sitemap.xml"}:
            continue
        text = path.read_text(encoding="utf-8")
        for host in legacy_hosts:
            if f"https://{host}" in text or f"http://{host}" in text:
                problems.append(f"{path.relative_to(root)} still references legacy host {host}")
        if bad_root_ref is not None and bad_root_ref.search(text):
            problems.append(f"{path.relative_to(root)} still contains an unrebased root-relative string")
    if problems:
        fail(f"{entry['id']} namespace verification failed: " + "; ".join(problems[:12]))


def main() -> int:
    registry = load_registry()
    entries = registry["sites"]
    origin = registry["canonical_origin"]

    run([sys.executable, "scripts/validate_url_namespace.py"])
    glaze_css = collect_glaze_css()

    if OUTPUT.exists():
        if OUTPUT.is_symlink():
            fail("dist must not be a symlink")
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()

    header_blocks: list[str] = []
    sitemap_urls: list[str] = []
    staging_root = ROOT / ".namespace-staging"
    if staging_root.exists():
        shutil.rmtree(staging_root)
    staging_root.mkdir()

    try:
        for entry in entries:
            site_id = entry["id"]
            command = entry.get("build_command")
            artifact_path = entry.get("artifact_path")
            if command:
                run(command)
                artifact = ROOT / artifact_path
                if not artifact.is_dir() or artifact.is_symlink():
                    fail(f"{site_id} builder did not produce safe artifact {artifact_path}")
            else:
                artifact = static_artifact(entry, staging_root / site_id)

            prefix = entry["canonical_path"]
            destination = OUTPUT if prefix == "/" else OUTPUT / prefix.lstrip("/")
            if prefix == "/":
                for child in sorted(artifact.iterdir(), key=lambda item: item.name):
                    copy_checked(child, destination / child.name)
            else:
                copy_checked(artifact, destination)

            rewrite_artifact(destination, entry, entries, origin)
            normalize_publication(destination, entry, origin, glaze_css)
            verify_publication(destination, entry, entries, origin)

            headers = artifact / "_headers"
            if headers.is_file():
                header_blocks.append(prefixed_header_block(headers.read_text(encoding="utf-8"), prefix, site_id))
            sitemap = destination / "sitemap.xml"
            if sitemap.is_file() and prefix != "/":
                sitemap_urls.append(f"{origin}{prefix}/sitemap.xml")

        if header_blocks:
            (OUTPUT / "_headers").write_text("\n".join(header_blocks).rstrip() + "\n", encoding="utf-8")

        robots = OUTPUT / "robots.txt"
        if robots.is_file() and sitemap_urls:
            text = robots.read_text(encoding="utf-8").rstrip() + "\n"
            for url in sorted(set(sitemap_urls)):
                marker = f"Sitemap: {url}"
                if marker not in text:
                    text += marker + "\n"
            robots.write_text(text, encoding="utf-8")

        file_count = sum(1 for path in OUTPUT.rglob("*") if path.is_file())
        total_bytes = sum(path.stat().st_size for path in OUTPUT.rglob("*") if path.is_file())
        print(
            f"Built unified GoreeCloud www namespace: {len(entries)} sites, {file_count} files, {total_bytes} bytes -> dist/; "
            f"GLAZE UI {GLAZE_VERSION} Stable publication layer pinned to {GLAZE_RELEASE_REVISION}"
        )
        print(
            "Per-site rendered/mobile/accessibility acceptance, exact deployed-revision verification, nested legacy-path compatibility, "
            "old Pages/reference cleanup, and legacy-source retirement remain separate evidence gates."
        )
        return 0
    finally:
        if staging_root.exists():
            shutil.rmtree(staging_root)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"www namespace build failed: {exc}")
