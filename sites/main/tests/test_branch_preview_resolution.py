#!/usr/bin/env python3
"""Regression coverage for Cloudflare Pages branch-preview target resolution."""

from __future__ import annotations

from pathlib import Path
import os
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import verify_remote_deployment as verifier  # noqa: E402


class BranchPreviewResolutionTests(unittest.TestCase):
    def test_current_pull_request_branch_resolves_to_cloudflare_preview(self) -> None:
        with patch.dict(os.environ, {"GITHUB_HEAD_REF": "agent/portfolio-current-state"}, clear=False):
            self.assertEqual(
                verifier.target_url("branch-preview"),
                "https://agent-portfolio-current-stat.goreecloud-website.pages.dev",
            )

    def test_branch_label_is_normalized_and_bounded(self) -> None:
        self.assertEqual(
            verifier.normalize_branch_preview_label("Feature/Glaze_UI--Polish"),
            "feature-glaze-ui-polish",
        )
        self.assertLessEqual(
            len(verifier.normalize_branch_preview_label("agent/" + "very-long-branch-name-" * 4)),
            28,
        )

    def test_empty_branch_label_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            verifier.normalize_branch_preview_label("///___")

    def test_preview_domain_is_allowed_but_unrelated_domain_is_rejected(self) -> None:
        verifier.validate_fixed_url(
            "https://agent-portfolio-current-stat.goreecloud-website.pages.dev/"
        )
        with self.assertRaises(ValueError):
            verifier.validate_fixed_url("https://goreecloud-website.pages.dev.evil.example/")

    def test_production_target_remains_fixed(self) -> None:
        with patch.dict(os.environ, {"GITHUB_HEAD_REF": "agent/anything"}, clear=False):
            self.assertEqual(verifier.target_url("production"), verifier.PRODUCTION_URL)

    def test_without_ci_context_reviewed_fallback_remains_available(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                verifier.branch_preview_url(),
                verifier.DEFAULT_BRANCH_PREVIEW_URL,
            )


if __name__ == "__main__":
    unittest.main()
