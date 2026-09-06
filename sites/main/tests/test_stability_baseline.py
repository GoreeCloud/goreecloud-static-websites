#!/usr/bin/env python3
"""Regression coverage for GoreeCloud website stable-version metadata."""

from __future__ import annotations

from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_public_site import PUBLIC_FILES  # noqa: E402
from glaze_ui_2 import GLAZE_PROMOTION_REVISION, GLAZE_VERSION  # noqa: E402

VERSION_PATH = ROOT / "VERSION"
BASELINE_PATH = ROOT / "docs" / "stability-baseline.md"
GLAZE_CONFORMANCE_PATH = ROOT / "docs" / "glaze-ui-conformance.md"
GLAZE_ADOPTION_PATH = ROOT / "docs" / "glaze-ui-2.1-public-sites.md"
README_PATH = ROOT / "README.md"
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class StabilityBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.version = VERSION_PATH.read_text(encoding="utf-8").strip()
        cls.baseline = BASELINE_PATH.read_text(encoding="utf-8")
        cls.glaze_conformance = GLAZE_CONFORMANCE_PATH.read_text(encoding="utf-8")
        cls.glaze_adoption = GLAZE_ADOPTION_PATH.read_text(encoding="utf-8")
        cls.readme = README_PATH.read_text(encoding="utf-8")

    def test_version_is_current_strict_semver(self) -> None:
        self.assertRegex(self.version, SEMVER_RE)
        self.assertEqual(self.version, "5.24.0")

    def test_baseline_names_canonical_version(self) -> None:
        self.assertIn(f"**{self.version}**", self.baseline)
        self.assertIn("`VERSION` is the canonical machine-readable version source", self.baseline)

    def test_readme_tracks_current_release_and_design_state(self) -> None:
        self.assertIn(f"Current accepted website package: **v{self.version}**", self.readme)
        self.assertIn("`VERSION` is the canonical machine-readable version source", self.readme)
        self.assertIn("Version metadata is repository-only release metadata", self.readme)
        self.assertIn("does not establish deployment or production acceptance by itself", self.readme)
        self.assertIn("Glaze UI 2.1.0 Stable", self.readme)
        self.assertIn("57 repositories — 40 public, 17 private", self.readme)
        self.assertIn("10 destinations on Glaze UI 2.1.0 Stable", self.readme)
        self.assertIn("Identity Center", self.readme)
        self.assertIn("GoreeCloud/goreecloud-branding-assets", self.readme)
        self.assertIn("Content is solid. Interaction is glazed.", self.readme)
        self.assertIn("56px Touch Assistance floor", self.readme)

    def test_stability_requires_exact_preview_and_production_verification(self) -> None:
        self.assertIn("exact branch-preview deployment verification", self.baseline)
        self.assertIn("exact production deployment verification", self.baseline)
        self.assertIn("A merge alone is not a stable release", self.baseline)

    def test_stability_records_current_portfolio_and_platform_systems(self) -> None:
        for marker in (
            "57 repositories: 40 public, 17 private, across 13 functional groups",
            "10 production-accepted destinations on Glaze UI 2.1.0 Stable",
            "GoreeCloud Identity",
            "Identity Center",
            "publication and exact production acceptance remain pending",
            "Glaze UI 2.1.0 Stable",
            "Glaze UI 2.0.0 Stable",
            "Facet",
            "goreecloud-index",
        ):
            self.assertIn(marker, self.baseline)

    def test_stability_rejects_obsolete_current_state(self) -> None:
        for stale in (
            "30 repository / 23 public / 7 private",
            "56 repositories: 40 public, 16 private",
            "Glaze UI 1.1.0 using the exact canonical source revision",
            "Glaze UI 2.1 remains Candidate",
            "active modernization candidate moves the official GoreeCloud public-web ecosystem",
            "goreecloud-logo` repository artwork source",
        ):
            self.assertNotIn(stale, self.baseline)

    def test_stability_preserves_governance_boundaries(self) -> None:
        for marker in (
            "repository visibility change",
            "DNS change",
            "creative-rights/publication decision",
            "final human reachable-history/contextual-disclosure review",
        ):
            self.assertIn(marker, self.baseline)

    def test_version_metadata_is_repository_only(self) -> None:
        self.assertNotIn("VERSION", PUBLIC_FILES)
        self.assertNotIn("docs/stability-baseline.md", PUBLIC_FILES)
        self.assertNotIn("docs/glaze-ui-conformance.md", PUBLIC_FILES)
        self.assertNotIn("docs/glaze-ui-2.1-public-sites.md", PUBLIC_FILES)

    def test_scope_preserves_static_privacy_and_current_glaze_boundaries(self) -> None:
        for marker in (
            "Glaze UI 2.1.0 Stable",
            "Canvas → Surface → Soft Glaze → Glaze → Deep Glaze → Live Glaze",
            "Content is solid. Interaction is glazed.",
            "48px minimum general interaction targets",
            "56px Touch Assistance floor",
            "reduced-motion and reduced-transparency",
            "privacy-preserving static browser surfaces",
            "isolated Cloudflare Pages publication artifact",
        ):
            self.assertIn(marker, self.baseline)

    def test_glaze_conformance_records_current_target(self) -> None:
        for marker in (
            f"Target Glaze UI version: **{GLAZE_VERSION}**",
            GLAZE_PROMOTION_REVISION,
            "GoreeCloud/goreecloud-glaze-ui",
            "Glaze UI 2.1.0 Stable web contract prepared",
            "same-origin Glaze UI 2.1.0 web layer",
            "Content is solid. Interaction is glazed.",
            "48px general interaction floor",
            "56px Touch Assistance floor",
            "Reduced Motion removes nonessential transformation and travel.",
            "Reduced Transparency resolves optical material to solid hierarchy.",
            "No production Glaze UI exception is recorded",
        ):
            self.assertIn(marker, self.glaze_conformance)

    def test_21_adoption_record_preserves_acceptance_boundary(self) -> None:
        for marker in (
            "Stable source target: **2.1.0**",
            GLAZE_PROMOTION_REVISION,
            "Content is solid. Interaction is glazed.",
            "56px Touch Assistance floor",
            "Accepted production web portfolio: **10 independently deployed destinations on Glaze UI 2.1.0 Stable**",
            "Identity Center is source-merged on Glaze UI 2.1.0 Stable",
            "Later source commits, content changes, or consumer updates must earn their own exact-revision acceptance",
            "Glaze UI 2.0.0 remains the immediately preceding historical Stable baseline",
        ):
            self.assertIn(marker, self.glaze_adoption)


if __name__ == "__main__":
    unittest.main()
