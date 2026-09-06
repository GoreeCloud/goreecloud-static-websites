#!/usr/bin/env python3
"""Keep publication/licensing inventory synchronized with deployable and retained artwork."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_public_site import (  # noqa: E402
    PUBLIC_ASSET_FILES,
    PUBLIC_FILES,
    RETIRED_SOURCE_ONLY_ASSET_FILES,
)

INVENTORY = ROOT / "docs" / "public-asset-inventory.md"
BLOB_ID_RE = re.compile(r"[0-9a-f]{40,64}")


def inventory_section(text: str, heading: str, next_heading: str | None = None) -> str:
    start_marker = f"## {heading}"
    if start_marker not in text:
        raise AssertionError(f"Missing inventory section: {heading}")
    section = text.split(start_marker, 1)[1]
    if next_heading:
        end_marker = f"## {next_heading}"
        if end_marker not in section:
            raise AssertionError(f"Missing inventory section boundary: {next_heading}")
        section = section.split(end_marker, 1)[0]
    return section


def inventory_rows(text: str) -> dict[str, str]:
    """Return asset paths mapped to their reviewed Git blob IDs for one table/section."""
    rows: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or "`assets/" not in line:
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4:
            continue

        path_cell = cells[0]
        blob_cell = cells[-1]
        if not (path_cell.startswith("`assets/") and path_cell.endswith("`")):
            continue
        if not (blob_cell.startswith("`") and blob_cell.endswith("`")):
            continue

        path = path_cell[1:-1]
        blob_id = blob_cell[1:-1]
        if BLOB_ID_RE.fullmatch(blob_id):
            if path in rows:
                raise AssertionError(f"Duplicate asset row in inventory section: {path}")
            rows[path] = blob_id
    return rows


def git_blob_id(path: Path) -> str:
    """Compute the repository-format Git blob ID for the checked-out file bytes."""
    result = subprocess.run(
        ("git", "hash-object", str(path)),
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "unknown git hash-object failure"
        raise AssertionError(f"Could not compute Git blob ID for {path.relative_to(ROOT)}: {message}")

    blob_id = result.stdout.strip()
    if not BLOB_ID_RE.fullmatch(blob_id):
        raise AssertionError(f"Unexpected Git blob ID for {path.relative_to(ROOT)}: {blob_id!r}")
    return blob_id


def normalize_markdown_text(text: str) -> str:
    """Normalize lightweight Markdown emphasis before semantic wording checks."""
    return re.sub(r"[*_]", "", text).lower()


class PublicAssetInventoryTests(unittest.TestCase):
    """Prevent current or retained artwork from bypassing publication/provenance review."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = INVENTORY.read_text(encoding="utf-8")
        cls.deployable_section = inventory_section(
            cls.text,
            "Deployable artwork",
            "Retained source-only historical/provenance artwork",
        )
        cls.retained_section = inventory_section(
            cls.text,
            "Retained source-only historical/provenance artwork",
        )

    def test_inventory_exists_but_is_not_deployed(self) -> None:
        self.assertTrue(INVENTORY.is_file())
        self.assertNotIn("docs/public-asset-inventory.md", PUBLIC_FILES)

    def test_inventory_matches_exact_public_asset_allowlist(self) -> None:
        documented = set(inventory_rows(self.deployable_section))
        expected = set(PUBLIC_ASSET_FILES)

        self.assertEqual(
            documented,
            expected,
            "Deployable inventory section must exactly match PUBLIC_ASSET_FILES; review licensing/provenance whenever deployment artwork changes.",
        )

        for path in PUBLIC_ASSET_FILES:
            self.assertEqual(
                self.deployable_section.count(f"`{path}`"),
                1,
                f"Deployable asset must appear exactly once in the deployable inventory table: {path}",
            )
            self.assertNotIn(
                f"`{path}`",
                self.retained_section,
                f"Deployable asset must not also be classified as source-only history: {path}",
            )

    def test_retained_inventory_matches_exact_source_only_set(self) -> None:
        documented = set(inventory_rows(self.retained_section))
        expected = set(RETIRED_SOURCE_ONLY_ASSET_FILES)
        self.assertEqual(
            documented,
            expected,
            "Source-only inventory section must exactly match RETIRED_SOURCE_ONLY_ASSET_FILES.",
        )
        self.assertTrue(expected.isdisjoint(set(PUBLIC_ASSET_FILES)))
        for path in RETIRED_SOURCE_ONLY_ASSET_FILES:
            self.assertEqual(self.retained_section.count(f"`{path}`"), 1)
            self.assertNotIn(path, PUBLIC_FILES)

    def test_reviewed_blob_ids_match_current_asset_bytes(self) -> None:
        deployable = inventory_rows(self.deployable_section)
        retained = inventory_rows(self.retained_section)

        for relative_path in PUBLIC_ASSET_FILES:
            actual = git_blob_id(ROOT / relative_path)
            self.assertEqual(
                deployable[relative_path],
                actual,
                (
                    f"Deployable asset bytes changed without updating the rights/provenance inventory: {relative_path}. "
                    "Review the new artwork and update its recorded Git blob ID in the same change."
                ),
            )

        for relative_path in RETIRED_SOURCE_ONLY_ASSET_FILES:
            actual = git_blob_id(ROOT / relative_path)
            self.assertEqual(
                retained[relative_path],
                actual,
                (
                    f"Retained source-only asset bytes changed without updating provenance: {relative_path}. "
                    "Historical retention does not bypass byte/provenance review."
                ),
            )

    def test_inventory_preserves_publication_boundary_language(self) -> None:
        text = normalize_markdown_text(self.text)
        required = (
            "not a license grant",
            "official artwork is required when it exists",
            "identity artwork must be source-traceable before deployment",
            "does not automatically license goreecloud branding or third-party marks",
            "final human reachable-history/contextual-disclosure review",
            "issue #5 remains open",
            "not part of the current public build allowlist",
            "must not be published by the current goreecloud website artifact",
        )
        for marker in required:
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
