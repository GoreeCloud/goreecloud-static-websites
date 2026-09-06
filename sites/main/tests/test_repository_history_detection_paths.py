#!/usr/bin/env python3
"""Protect the exact-path allowlist used only for detector-literal history scanning."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validate_repository_history import DETECTION_SOURCE_PATHS  # noqa: E402

EXPECTED_DETECTION_SOURCE_PATHS = {
    "scripts/validate_repository_history.py",
    "scripts/validate_repository_guidance.py",
    "scripts/validate_release_evidence.py",
    "scripts/validate_site.py",
    "scripts/validate_resilience.py",
    "scripts/validate_privacy_policy.py",
    "scripts/validate_security_policy.py",
    "tests/test_validate_release_evidence.py",
}


class RepositoryHistoryDetectionPathTests(unittest.TestCase):
    """Keep literal-detector exemptions narrow, explicit, and reviewable."""

    def test_detection_source_allowlist_is_exact(self) -> None:
        self.assertEqual(DETECTION_SOURCE_PATHS, EXPECTED_DETECTION_SOURCE_PATHS)

    def test_detection_source_allowlist_has_no_globs_or_directory_exemptions(self) -> None:
        for path in DETECTION_SOURCE_PATHS:
            self.assertNotIn("*", path)
            self.assertNotIn("?", path)
            self.assertFalse(path.endswith("/"))
            self.assertTrue(path.startswith(("scripts/", "tests/")))
            self.assertNotIn("docs/", path)
            self.assertNotIn("assets/", path)


if __name__ == "__main__":
    unittest.main()
