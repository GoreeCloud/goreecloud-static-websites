#!/usr/bin/env python3
"""Fail-closed validation for the GoreeCloud public website URL namespace."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "sites" / "url-namespace.json"
MANIFEST = ROOT / "sites" / "manifest.json"
EXPECTED_PATHS = {
    "main": "/",
    "projects": "/projects",
    "roadmap": "/roadmap",
    "blog": "/blog",
    "archive": "/archive",
    "suite": "/suite",
    "design": "/glaze-ui",
    "privacy": "/privacy-shield",
    "security": "/wardveil",
    "everkeep": "/everkeep",
    "identity": "/identity",
    "manager": "/manager",
    "mesh": "/mesh",
    "labs": "/labs",
}


def fail(message: str) -> None:
    raise SystemExit(f"URL namespace validation failed: {message}")


def valid_host(host: str) -> bool:
    parsed = urlparse(f"https://{host}")
    return parsed.scheme == "https" and parsed.hostname == host and "/" not in host


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    if registry.get("schema_version") != "1.0":
        fail("schema_version must be 1.0")
    if registry.get("repository") != "GoreeCloud/goreecloud-static-websites":
        fail("repository authority is incorrect")
    if registry.get("canonical_origin") != "https://www.goreecloud.com":
        fail("canonical origin must be https://www.goreecloud.com")
    if registry.get("state") != "migration-preparation":
        fail("registry must remain migration-preparation until production cutover is verified")

    sites = registry.get("sites")
    if not isinstance(sites, list):
        fail("sites must be a list")

    manifest_ids = {entry["id"] for entry in manifest.get("sites", [])}
    registry_ids = {entry.get("id") for entry in sites}
    if registry_ids != manifest_ids:
        fail(f"registry IDs must exactly match manifest IDs: registry={sorted(registry_ids)} manifest={sorted(manifest_ids)}")
    if registry_ids != set(EXPECTED_PATHS):
        fail("registry IDs drifted from the governed public-site inventory")

    seen_paths: set[str] = set()
    seen_hosts: set[str] = set()
    for entry in sites:
        site_id = entry["id"]
        canonical_path = entry.get("canonical_path")
        if canonical_path != EXPECTED_PATHS[site_id]:
            fail(f"{site_id} canonical path must be {EXPECTED_PATHS[site_id]}")
        if canonical_path in seen_paths:
            fail(f"duplicate canonical path: {canonical_path}")
        seen_paths.add(canonical_path)
        if canonical_path != "/" and (not canonical_path.startswith("/") or canonical_path.endswith("/")):
            fail(f"{site_id} canonical path must be a normalized path prefix")

        source_path = entry.get("source_path")
        if not isinstance(source_path, str) or not source_path.startswith("sites/"):
            fail(f"{site_id} has invalid source_path")
        source = ROOT / source_path
        if not source.is_dir() or source.is_symlink():
            fail(f"{site_id} source_path is missing or unsafe: {source_path}")

        current_host = entry.get("current_public_host")
        if current_host is not None:
            if not isinstance(current_host, str) or not valid_host(current_host):
                fail(f"{site_id} has invalid current_public_host")
            if current_host in seen_hosts:
                fail(f"duplicate current_public_host: {current_host}")
            seen_hosts.add(current_host)

        reserved_app_host = entry.get("reserved_application_host")
        if reserved_app_host is not None and (not isinstance(reserved_app_host, str) or not valid_host(reserved_app_host)):
            fail(f"{site_id} has invalid reserved_application_host")
        if reserved_app_host is not None and entry.get("legacy_redirect"):
            fail(f"{site_id} cannot redirect a hostname reserved for a web application")

        command = entry.get("build_command")
        artifact = entry.get("artifact_path")
        allowlist = entry.get("static_allowlist")
        if command is None:
            if not isinstance(allowlist, list) or not allowlist:
                fail(f"{site_id} requires either build_command or static_allowlist")
            if artifact is not None:
                fail(f"{site_id} static publication must not declare artifact_path")
        else:
            if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
                fail(f"{site_id} has invalid build_command")
            if not isinstance(artifact, str) or not artifact.startswith("sites/"):
                fail(f"{site_id} has invalid artifact_path")

    manager = next(entry for entry in sites if entry["id"] == "manager")
    if manager.get("current_public_host") is not None:
        fail("Manager informational publication must not claim manager.goreecloud.com as its current public host")
    if manager.get("reserved_application_host") != "manager.goreecloud.com":
        fail("manager.goreecloud.com must remain reserved as the Manager web-application boundary")

    print(f"URL namespace registry valid: {len(sites)} informational websites -> https://www.goreecloud.com paths")


if __name__ == "__main__":
    main()
