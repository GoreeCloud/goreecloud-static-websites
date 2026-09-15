#!/usr/bin/env python3
"""Build all GoreeCloud informational websites into the governed www path namespace.

This is a publication builder, not a production-acceptance declaration. It preserves
application subdomain boundaries and rebases each independent static artifact beneath
https://www.goreecloud.com/<website-slug>.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "sites" / "url-namespace.json"
OUTPUT = ROOT / "dist"
TEXT_SUFFIXES = {".html", ".css", ".js", ".mjs", ".json", ".xml", ".txt", ".webmanifest", ".svg"}


def fail(message: str) -> None:
    raise RuntimeError(message)


def load_registry() -> dict:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if data.get("canonical_origin") != "https://www.goreecloud.com":
        fail("unexpected canonical origin")
    if data.get("state") != "migration-preparation":
        fail("URL namespace registry must remain migration-preparation until verified cutover")
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

    # Quoted root-relative values cover HTML attributes, JSON, web manifests,
    # and ordinary JavaScript string literals without touching protocol-relative URLs.
    quoted = re.compile(rf"(?P<quote>['\"])/(?!/|{escaped}(?:/|['\"]))")
    text = quoted.sub(lambda match: f"{match.group('quote')}{path_prefix}/", text)

    # Unquoted CSS url(/asset) references are legal and need the same path rebasing.
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


def verify_satellite(root: Path, entry: dict, entries: list[dict]) -> None:
    prefix = entry["canonical_path"]
    index = root / "index.html"
    if not index.is_file():
        fail(f"{entry['id']} mounted artifact has no index.html")

    legacy_hosts = [item.get("current_public_host") for item in entries if item.get("current_public_host") not in {None, "www.goreecloud.com"}]
    escaped = re.escape(prefix.lstrip("/"))
    bad_root_ref = re.compile(rf"['\"]/(?!/|{escaped}(?:/|['\"]))")
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
        if bad_root_ref.search(text):
            problems.append(f"{path.relative_to(root)} still contains an unrebased root-relative string")
    if problems:
        fail(f"{entry['id']} namespace verification failed: " + "; ".join(problems[:12]))


def main() -> int:
    registry = load_registry()
    entries = registry["sites"]
    origin = registry["canonical_origin"]

    # Validate the registry before any artifact construction.
    run([sys.executable, "scripts/validate_url_namespace.py"])

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
                verify_satellite(destination, entry, entries)

            headers = artifact / "_headers"
            if headers.is_file():
                header_blocks.append(prefixed_header_block(headers.read_text(encoding="utf-8"), prefix, site_id))
            sitemap = destination / "sitemap.xml"
            if sitemap.is_file() and prefix != "/":
                sitemap_urls.append(f"{origin}{prefix}/sitemap.xml")

        # _headers is global at the Pages project root. Merge each site's rules under
        # its mounted path so satellite security headers are not silently discarded.
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
        print(f"Built unified GoreeCloud www namespace: {len(entries)} sites, {file_count} files, {total_bytes} bytes -> dist/")
        print("Production acceptance remains separate and requires exact deployed-revision, routing, DNS/TLS, redirect, rendered, accessibility, and current-Glaze verification.")
        return 0
    finally:
        if staging_root.exists():
            shutil.rmtree(staging_root)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"www namespace build failed: {exc}")
