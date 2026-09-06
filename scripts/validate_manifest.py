#!/usr/bin/env python3
"""Fail-closed validation for the GoreeCloud static-website migration registry."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "sites" / "manifest.json"
ALLOWED_STATES = {
    "inventory-confirmed",
    "source-copied",
    "validated-in-central-repo",
    "deployment-cutover-pending",
    "production-verified",
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
    "retirement_condition",
}


def fail(message: str) -> None:
    raise SystemExit(f"manifest validation failed: {message}")


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        fail("schema_version must be 1.0")
    if data.get("repository") != "GoreeCloud/goreecloud-static-websites":
        fail("repository authority is incorrect")
    if set(data.get("states", [])) != ALLOWED_STATES:
        fail("declared migration-state vocabulary drifted")

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
        if not target.startswith("sites/") or target == "sites/manifest.json":
            fail(f"{site_id} has invalid central target path")
        if repo == "GoreeCloud/goreecloud-static-websites":
            fail(f"{site_id} legacy repository cannot be the central repository")
        if not repo.startswith("GoreeCloud/"):
            fail(f"{site_id} legacy repository is outside GoreeCloud")
        if len(source_tree) != 40 or any(ch not in "0123456789abcdef" for ch in source_tree):
            fail(f"{site_id} source_tree_sha must be a 40-character lowercase Git SHA")
        if not entry["retirement_condition"].strip():
            fail(f"{site_id} retirement condition is empty")

        parsed = urlparse(f"https://{domain}")
        if parsed.scheme != "https" or parsed.hostname != domain or "/" in domain:
            fail(f"{site_id} has invalid canonical domain")

        site_dir = ROOT / target
        if state != "inventory-confirmed" and not site_dir.is_dir():
            fail(f"{site_id} state {state} requires central source directory {target}")

    required_ids = {
        "main", "projects", "roadmap", "blog", "archive", "suite", "design",
        "privacy", "security", "everkeep", "identity", "manager", "mesh",
    }
    if not required_ids.issubset(ids):
        fail(f"known migration inventory missing: {sorted(required_ids - ids)}")

    print(f"Static website migration manifest valid: {len(sites)} sites")


if __name__ == "__main__":
    main()
