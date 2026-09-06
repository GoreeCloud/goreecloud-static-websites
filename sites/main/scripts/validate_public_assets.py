#!/usr/bin/env python3
from __future__ import annotations

from hashlib import sha1, sha256
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

from build_public_site import PUBLIC_ASSET_FILES, RETIRED_SOURCE_ONLY_ASSET_FILES, ROOT
from render_repository_portfolio import load_manifest, load_suite_manifest, render_public_file

MANIFEST = ROOT / "docs/visual-identity-sources.json"
INDEX = ROOT / "index.html"
GITHUB_REF = re.compile(r"^[0-9a-f]{40}$|^(?:main|master|dev)$")
DATE_REF = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def git_blob_id(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return sha1(header + raw).hexdigest()


def suite_records() -> dict[str, dict]:
    records: dict[str, dict] = {}
    for group in load_suite_manifest(ROOT)["groups"]:
        for app in group["applications"]:
            path = app["icon"]
            repository = app["source_repository"]
            source_ref = app["source_ref"]
            source_path = app["source_path"]
            records[path] = {
                "asset_path": path,
                "official_artwork_exists": True,
                "git_blob": app["icon_blob"],
                "source_authority": repository,
                "source_path": source_path,
                "source_ref": source_ref,
                "source_url": f"https://raw.githubusercontent.com/{repository}/{source_ref}/{source_path}",
            }
    return records


def main() -> int:
    errors: list[str] = []
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    legacy_records = {
        record["asset_path"]: record
        for record in data.get("assets", [])
        if record.get("asset_path")
    }
    suite = suite_records()
    collisions = sorted(set(legacy_records).intersection(suite))
    for path in collisions:
        errors.append(f"Suite artwork path collides with legacy identity record: {path}")

    all_records = {**legacy_records, **suite}
    expected = set(PUBLIC_ASSET_FILES) - {"assets/social-preview.png"}
    retired = set(RETIRED_SOURCE_ONLY_ASSET_FILES)

    overlap = sorted(expected.intersection(retired))
    for rel in overlap:
        errors.append(f"Source-only historical asset has re-entered the deployable artwork allowlist: {rel}")

    missing_provenance = sorted(expected.difference(all_records))
    for rel in missing_provenance:
        errors.append(f"Deployable identity asset lacks a reviewed provenance record: {rel}")

    missing_retired_provenance = sorted(retired.difference(all_records))
    for rel in missing_retired_provenance:
        errors.append(f"Retained source-only historical asset lacks its provenance record: {rel}")

    unclassified_records = sorted(set(all_records).difference(expected).difference(retired))
    for rel in unclassified_records:
        errors.append(
            f"Identity provenance record is neither deployable nor explicitly retained source-only history: {rel}"
        )

    deployed = {rel: all_records[rel] for rel in expected if rel in all_records}
    retained = {rel: all_records[rel] for rel in retired if rel in all_records}

    # Preserve byte/provenance integrity for both current deployment derivatives and
    # source-only historical records. Historical retention must not become a path
    # around provenance review, even though those assets are excluded from dist/.
    for rel, rec in {**deployed, **retained}.items():
        path = ROOT / rel
        if not path.is_file() or path.is_symlink():
            errors.append(f"Reviewed identity asset is not a regular file: {rel}")
            continue

        raw = path.read_bytes()
        if rec.get("git_blob"):
            if rec["git_blob"] != git_blob_id(raw):
                errors.append(f"Identity asset changed without reviewed Git-blob provenance: {rel}")
        else:
            actual = sha256(raw).hexdigest()
            if rec.get("sha256") != actual:
                errors.append(f"Identity asset changed without provenance review: {rel}")
            if rec.get("bytes") != path.stat().st_size:
                errors.append(f"Identity asset byte count drifted without provenance review: {rel}")

        if not rec.get("source_authority") or not rec.get("source_url"):
            errors.append(f"Identity asset lacks source authority: {rel}")
            continue

        parsed = urlparse(rec["source_url"])
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"Identity asset source URL must be an absolute HTTPS URL: {rel}")

        source_ref = str(rec.get("source_ref", ""))
        if parsed.netloc == "raw.githubusercontent.com" and not GITHUB_REF.fullmatch(source_ref):
            errors.append(f"GitHub-hosted identity asset must record a commit or named source branch: {rel}")
        elif parsed.netloc != "raw.githubusercontent.com" and not (
            GITHUB_REF.fullmatch(source_ref) or DATE_REF.fullmatch(source_ref)
        ):
            errors.append(f"Identity asset must record a commit, named branch, or dated review ref: {rel}")

    source_index = INDEX.read_text(encoding="utf-8")
    rendered_index = render_public_file("index.html", source_index, load_manifest(ROOT))
    combined_index = source_index + "\n" + rendered_index

    for stale in (
        'class="service-icon"',
        "platform-native-mark",
        "social-letter",
        "neutral Glaze UI letter marks instead of third-party logo artwork",
        "assets/goreecloud-icon.png",
        "assets/favicon.svg",
    ):
        if stale in rendered_index:
            errors.append(f"Obsolete placeholder/identity marker remains in deployable homepage: {stale}")

    for rel in expected:
        if rel != "assets/goreecloud-logo.svg" and rel not in combined_index:
            errors.append(f"Deployable identity asset is not represented by the reviewed homepage source/render: {rel}")

    for rel in retired:
        if rel in combined_index:
            errors.append(f"Source-only historical upstream asset appears in the current homepage source/render: {rel}")

    if rendered_index.count("assets/goreecloud-logo.svg") < 3:
        errors.append("Canonical GoreeCloud logo is not used across visible website identity surfaces.")

    for rec in data.get("assets", []):
        if rec.get("official_artwork_exists") is False and rec.get("fallback") != "text-only":
            errors.append(f"Non-art fallback must be text-only: {rec.get('id')}")

    if errors:
        print("Official visual-identity validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Official visual-identity validation passed across "
        f"{len(deployed)} deployable identity assets and {len(retained)} retained source-only provenance assets."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())