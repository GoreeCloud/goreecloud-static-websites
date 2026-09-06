#!/usr/bin/env python3
"""Protect the repository-only GoreeCloud website release-evidence record template."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_public_site import PUBLIC_FILES  # noqa: E402

TEMPLATE = ROOT / "docs" / "release-evidence-template.md"


class ReleaseEvidenceTemplateTests(unittest.TestCase):
    """Keep release evidence separate, fail-closed, and outside the public artifact."""

    def setUp(self) -> None:
        self.text = TEMPLATE.read_text(encoding="utf-8")
        self.lower = self.text.lower()

    def test_template_exists_but_is_not_deployed(self) -> None:
        self.assertTrue(TEMPLATE.is_file())
        self.assertNotIn("docs/release-evidence-template.md", PUBLIC_FILES)

    def test_template_preserves_exact_candidate_and_evidence_boundaries(self) -> None:
        required = (
            "one exact GoreeCloud website release candidate",
            "exact 40-character Git commit SHA",
            "Evidence from one candidate must not be silently reused",
            "Central Time (`America/Chicago`)",
            "12-hour time format",
            "must remain outside the website `dist/` artifact",
            "does not itself authorize a merge",
            "Historical evidence must remain distinguishable from current state",
        )
        for marker in required:
            self.assertIn(marker.lower(), self.lower)

    def test_template_covers_all_release_gate_domains(self) -> None:
        required_sections = (
            "## 1. Candidate identity",
            "## 2. Automated validation evidence",
            "## 3. Glaze UI visual and interaction acceptance",
            "## 4. Accessibility acceptance",
            "## 5. Progressive enhancement, resilience, privacy, and origin boundary",
            "## 6. Source publication and creative-rights gate — issue #5",
            "## 7. Cloudflare isolated-artifact gate — issue #6",
            "## 8. Exceptions and accepted limitations",
            "## 9. Release authorization",
            "## 10. Post-release production verification",
        )
        for section in required_sections:
            self.assertIn(section, self.text)

    def test_template_starts_fail_closed(self) -> None:
        self.assertNotIn("[x]", self.lower)
        self.assertIn("- [ ] ACCEPTED", self.text)
        self.assertIn("- [ ] BLOCKED", self.text)
        self.assertIn("- [ ] REJECTED", self.text)
        self.assertIn("- [ ] SUPERSEDED", self.text)
        self.assertIn("Select exactly one final candidate disposition", self.text)

    def test_template_prohibits_sensitive_evidence_material(self) -> None:
        required = (
            "Do not place credentials",
            "private keys",
            "private IP addresses",
            "private hostnames",
            "Do not paste raw logs",
            "appropriate protected system",
        )
        for marker in required:
            self.assertIn(marker.lower(), self.lower)

    def test_template_keeps_integrity_evidence_scoped(self) -> None:
        self.assertIn("checksum", self.lower)
        self.assertIn("git blob id", self.lower)
        self.assertIn("is evidence for the specific property it validates", self.lower)
        self.assertIn("not proof of unrelated security", self.lower)


if __name__ == "__main__":
    unittest.main()
