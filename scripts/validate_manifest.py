#!/usr/bin/env python3
"""Fail-closed validation for the GoreeCloud static-website migration registry."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "sites" / "manifest.json"
CENTRAL_REPOSITORY = "GoreeCloud/goreecloud-static-websites"
ALLOWED_STATES = {
    "inventory-confirmed",
    "source-copied",
    "validated-in-central-repo",
    "deployment-cutover-pending",
    "production-verified",
    "legacy-source-retired",
}
ALLOWED_DEPLOYMENT_STATES = {
    "legacy-source",
    "cutover-in-progress",
    "central-source-production-verified",
    "legacy-source-retired",
}
REQUIRED_FIELDS = {
    "id",
    "canonical_domain",
    "target_path",
    "legacy_repository",
    "legacy_path",
    "source_tree_sha",
    "migration_state",
    "deployment_state",
    "target_deployment",
    "retirement_condition",
}
REQUIRED_TARGET_DEPLOYMENT_FIELDS = {
    "provider",
    "repository",
    "production_branch",
    "root_directory",
    "build_command",
    "output_directory",
}


def fail(message: str) -> None:
    raise SystemExit(f"manifest validation failed: {message}")


def valid_relative_path(value: str, *, allow_dot: bool = False) -> bool:
    if allow_dot and value == ".":
        return True
    if not value or value.startswith("/") or value.endswith("/"):
        return False
    parts = value.split("/")
    return all(part not in {"", ".", ".."} for part in parts)


def validate_target_deployment(site_id: str, target: str, deployment: object) -> None:
    if not isinstance(deployment, dict):
        fail(f"{site_id} target_deployment must be an object")

    missing = REQUIRED_TARGET_DEPLOYMENT_FIELDS - deployment.keys()
    if missing:
        fail(f"{site_id} target_deployment missing fields: {sorted(missing)}")

    extra = deployment.keys() - REQUIRED_TARGET_DEPLOYMENT_FIELDS
    if extra:
        fail(f"{site_id} target_deployment has unknown fields: {sorted(extra)}")

    if deployment["provider"] != "cloudflare-pages":
        fail(f"{site_id} target provider must be cloudflare-pages")
    if deployment["repository"] != CENTRAL_REPOSITORY:
        fail(f"{site_id} target repository must be the central repository")
    if deployment["production_branch"] != "main":
        fail(f"{site_id} target production branch must be main")
    if deployment["root_directory"] != target:
        fail(f"{site_id} Pages root must equal its central target path")

    build_command = deployment["build_command"]
    if build_command is not None:
        if not isinstance(build_command, str) or not build_command.strip():
            fail(f"{site_id} build_command must be null or a non-empty string")
        if "\n" in build_command or "\r" in build_command:
            fail(f"{site_id} build_command must be a single command line")

    output = deployment["output_directory"]
    if not isinstance(output, str) or not valid_relative_path(output, allow_dot=True):
        fail(f"{site_id} has invalid Pages output_directory: {output!r}")
    if build_command is None and output != ".":
        fail(f"{site_id} direct-static target must publish the selected root itself")


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.1":
        fail("schema_version must be 1.1")
    if data.get("repository") != CENTRAL_REPOSITORY:
        fail("repository authority is incorrect")
    if set(data.get("states", [])) != ALLOWED_STATES:
        fail("declared migration-state vocabulary drifted")
    if set(data.get("deployment_states", [])) != ALLOWED_DEPLOYMENT_STATES:
        fail("declared deployment-state vocabulary drifted")

    sites = data.get("sites")
    if not isinstance(sites, list) or not sites:
        fail("sites must be a non-empty list")

    ids: set[str] = set()
    domains: set[str] = set()
    targets: set[str] = set()

    for entry in sites:
        if not isinstance(entry, dict):
            fail("every site entry must be an object")
        missing = REQUIRED_FIELDS - entry.keys()
        if missing:
            fail(f"{entry.get('id', '<unknown>')} missing fields: {sorted(missing)}")

        site_id = entry["id"]
        domain = entry["canonical_domain"].lower()
        target = entry["target_path"]
        state = entry["migration_state"]
        deployment_state = entry["deployment_state"]
        repo = entry["legacy_repository"]
        source_tree = entry["source_tree_sha"]

        if site_id in ids:
            fail(f"duplicate site id: {site_id}")
        if domain in domains:
            fail(f"duplicate canonical domain: {domain}")
        if target in targets:
            fail(f"duplicate target path: {target}")
        ids.add(site_id)
        domains.add(domain)
        targets.add(target)

        if state not in ALLOWED_STATES:
            fail(f"{site_id} has invalid migration state: {state}")
        if deployment_state not in ALLOWED_DEPLOYMENT_STATES:
            fail(f"{site_id} has invalid deployment state: {deployment_state}")
        if not target.startswith("sites/") or target == "sites/manifest.json":
            fail(f"{site_id} has invalid central target path")
        if not valid_relative_path(target):
            fail(f"{site_id} central target path is not a safe relative path")
        if repo == CENTRAL_REPOSITORY:
            fail(f"{site_id} legacy repository cannot be the central repository")
        if not repo.startswith("GoreeCloud/"):
            fail(f"{site_id} legacy repository is outside GoreeCloud")
        if len(source_tree) != 40 or any(ch not in "0123456789abcdef" for ch in source_tree):
            fail(f"{site_id} source_tree_sha must be a 40-character lowercase Git SHA")
        if not entry["retirement_condition"].strip():
            fail(f"{site_id} retirement condition is empty")

        validate_target_deployment(site_id, target, entry["target_deployment"])

        parsed = urlparse(f"https://{domain}")
        if parsed.scheme != "https" or parsed.hostname != domain or "/" in domain:
            fail(f"{site_id} has invalid canonical domain")

        site_dir = ROOT / target
        if state != "inventory-confirmed" and not site_dir.is_dir():
            fail(f"{site_id} state {state} requires central source directory {target}")

        if deployment_state != "legacy-source" and state == "inventory-confirmed":
            fail(f"{site_id} cannot advance deployment before central source is copied")
        if deployment_state == "legacy-source-retired" and state != "legacy-source-retired":
            fail(f"{site_id} deployment retirement requires migration_state legacy-source-retired")

    required_ids = {
        "main", "projects", "roadmap", "blog", "archive", "suite", "design",
        "privacy", "security", "everkeep", "identity", "manager", "mesh",
    }
    if not required_ids.issubset(ids):
        fail(f"known migration inventory missing: {sorted(required_ids - ids)}")

    print(
        f"Static website migration manifest valid: {len(sites)} sites, "
        "Cloudflare Pages target contracts locked"
    )


if __name__ == "__main__":
    main()
