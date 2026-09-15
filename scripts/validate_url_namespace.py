#!/usr/bin/env python3
"""Fail-closed validation for the GoreeCloud public website URL namespace."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "sites" / "url-namespace.json"
MANIFEST = ROOT / "sites" / "manifest.json"
EXPECTED_STATE = "provider-cutover-verified"
EXPECTED_PENDING_CUTOVERS = {"firefox"}
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
    "firefox": "/firefox-extensions",
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
    if registry.get("state") != EXPECTED_STATE:
        fail(f"registry baseline state must remain {EXPECTED_STATE}")

    pending_cutovers = registry.get("pending_cutovers", [])
    if not isinstance(pending_cutovers, list) or set(pending_cutovers) != EXPECTED_PENDING_CUTOVERS:
        fail(f"pending cutover inventory must be exactly {sorted(EXPECTED_PENDING_CUTOVERS)} until Firefox provider cutover is verified")

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
    reserved_hosts: set[str] = set()
    redirect_count = 0
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
            if current_host in seen_hosts or current_host in reserved_hosts:
                fail(f"duplicate or reserved current_public_host: {current_host}")
            seen_hosts.add(current_host)

        if entry.get("legacy_redirect"):
            redirect_count += 1

        reserved_app_host = entry.get("reserved_application_host")
        if reserved_app_host is not None:
            if not isinstance(reserved_app_host, str) or not valid_host(reserved_app_host):
                fail(f"{site_id} has invalid reserved_application_host")
            if reserved_app_host == current_host:
                fail(f"{site_id} current_public_host cannot be its reserved web-application host")
            if reserved_app_host in seen_hosts or reserved_app_host in reserved_hosts:
                fail(f"duplicate or conflicting reserved_application_host: {reserved_app_host}")
            reserved_hosts.add(reserved_app_host)

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

    if redirect_count != 14:
        fail(f"legacy informational compatibility inventory must contain 14 hosts after adding Firefox, found {redirect_count}")

    main_site = next(entry for entry in sites if entry["id"] == "main")
    if main_site.get("current_public_host") != "www.goreecloud.com" or main_site.get("legacy_redirect"):
        fail("Main must remain the canonical www origin and must not be a legacy redirect source")

    design = next(entry for entry in sites if entry["id"] == "design")
    if design.get("build_command") != ["python", "sites/design/website/build_v14.py"]:
        fail("Design Center unified publication must use its V1.4+ builder rather than the obsolete V1.3 builder")

    manager = next(entry for entry in sites if entry["id"] == "manager")
    if manager.get("current_public_host") != "manage.goreecloud.com":
        fail("Manager informational publication legacy host must be manage.goreecloud.com")
    if not manager.get("legacy_redirect"):
        fail("manage.goreecloud.com must be marked for compatibility redirect to /manager")
    if manager.get("reserved_application_host") != "manager.goreecloud.com":
        fail("manager.goreecloud.com must remain reserved as the Manager web-application boundary")

    firefox = next(entry for entry in sites if entry["id"] == "firefox")
    if firefox.get("current_public_host") != "firefox.goreecloud.com":
        fail("Firefox Extensions legacy informational host must remain firefox.goreecloud.com until redirect retirement")
    if not firefox.get("legacy_redirect"):
        fail("firefox.goreecloud.com must be marked for compatibility redirect to /firefox-extensions")
    if firefox.get("cutover_state") != "migration-preparation":
        fail("Firefox Extensions must remain explicitly migration-preparation until the provider cutover is verified")

    print(
        f"URL namespace registry valid: {len(sites)} informational websites -> https://www.goreecloud.com paths; "
        f"baseline_state={EXPECTED_STATE}; pending_cutovers={sorted(EXPECTED_PENDING_CUTOVERS)}; "
        f"legacy compatibility hosts={redirect_count}"
    )


if __name__ == "__main__":
    main()
