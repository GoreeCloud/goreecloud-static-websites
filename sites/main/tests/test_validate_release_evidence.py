#!/usr/bin/env python3
"""Exercise candidate release-evidence structural and privacy validation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
import tempfile
import unittest
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_public_site import PUBLIC_FILES  # noqa: E402
from create_release_evidence import render_record  # noqa: E402
from validate_release_evidence import (  # noqa: E402
    REQUIRED_ACCEPTED_CHECKBOXES,
    validate_record,
    validate_records,
)

TEMPLATE = ROOT / "docs" / "release-evidence-template.md"
CENTRAL = ZoneInfo("America/Chicago")
SAMPLE_SHA = "0123456789abcdef0123456789abcdef01234567"
SAMPLE_DATE = "2026-08-15"


class ReleaseEvidenceValidationTests(unittest.TestCase):
    """Keep historical release evidence candidate-bound, fail-closed, and public-safe."""

    def setUp(self) -> None:
        self.template = TEMPLATE.read_text(encoding="utf-8")
        self.created_at = datetime(2026, 8, 15, 2, 7, tzinfo=CENTRAL)

    def write_record(self, directory: Path, text: str, name: str | None = None) -> Path:
        path = directory / (name or f"{SAMPLE_DATE}-{SAMPLE_SHA[:12]}-release-evidence.md")
        path.write_text(text, encoding="utf-8")
        return path

    def working_record(self) -> str:
        return render_record(self.template, SAMPLE_SHA, self.created_at)

    def test_valid_working_record_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = self.write_record(Path(temp), self.working_record())
            self.assertEqual(validate_record(path), [])

    def test_absent_evidence_directory_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            errors, count = validate_records(Path(temp) / "not-created-yet")
            self.assertEqual(errors, [])
            self.assertEqual(count, 0)

    def test_filename_and_candidate_identity_must_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = self.write_record(
                Path(temp),
                self.working_record(),
                name=f"{SAMPLE_DATE}-aaaaaaaaaaaa-release-evidence.md",
            )
            errors = validate_record(path)
            self.assertTrue(any("short SHA does not match" in error for error in errors))

    def test_private_network_address_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            text = self.working_record().replace("Evidence/notes:\n", "Evidence/notes: 192.168.1.25\n", 1)
            path = self.write_record(Path(temp), text)
            errors = validate_record(path)
            self.assertTrue(any("Private-range IP address" in error for error in errors))

    def test_multiple_final_dispositions_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            text = self.working_record()
            text = text.replace("- [ ] ACCEPTED", "- [x] ACCEPTED", 1)
            text = text.replace("- [ ] BLOCKED", "- [x] BLOCKED", 1)
            path = self.write_record(Path(temp), text)
            errors = validate_record(path)
            self.assertTrue(any("more than one final candidate disposition" in error for error in errors))

    def test_accepted_record_cannot_skip_required_gates(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            text = self.working_record()
            text = text.replace("- Record state: **Working — not accepted**", "- Record state: **Accepted**", 1)
            text = text.replace("- [ ] ACCEPTED", "- [x] ACCEPTED", 1)
            path = self.write_record(Path(temp), text)
            errors = validate_record(path)
            self.assertTrue(any("missing required acceptance checkbox" in error for error in errors))

    def test_structurally_complete_accepted_record_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            text = self.working_record()
            text = text.replace("- Record state: **Working — not accepted**", "- Record state: **Accepted**", 1)
            text = text.replace("- [ ] ACCEPTED", "- [x] ACCEPTED", 1)
            for label in REQUIRED_ACCEPTED_CHECKBOXES:
                text = text.replace(f"- [ ] {label}", f"- [x] {label}", 1)
            text = text.replace("- Merge authorization:\n", "- Merge authorization: Approved for merge\n", 1)
            text = text.replace("- Authorizing person/role:\n", "- Authorizing person/role: GoreeCloud owner\n", 1)
            text = text.replace(
                "- Authorization date/time:\n",
                "- Authorization date/time: August 15, 2026 at 2:07 AM CDT\n",
                1,
            )
            path = self.write_record(Path(temp), text)
            self.assertEqual(validate_record(path), [])

    def test_post_release_success_requires_result_and_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            text = self.working_record().replace(
                "- [ ] Production verification passed without a material discrepancy.",
                "- [x] Production verification passed without a material discrepancy.",
                1,
            )
            path = self.write_record(Path(temp), text)
            errors = validate_record(path)
            self.assertTrue(any("production verifier result" in error for error in errors))
            self.assertTrue(any("production verification timestamp" in error for error in errors))

    def test_nested_evidence_directories_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            evidence_dir = Path(temp) / "release-evidence"
            (evidence_dir / "nested").mkdir(parents=True)
            errors, count = validate_records(evidence_dir)
            self.assertEqual(count, 0)
            self.assertTrue(any("Nested directories are not allowed" in error for error in errors))

    def test_release_evidence_tooling_is_not_public_artifact_content(self) -> None:
        self.assertNotIn("scripts/validate_release_evidence.py", PUBLIC_FILES)
        self.assertNotIn("scripts/create_release_evidence.py", PUBLIC_FILES)
        self.assertFalse(any(path.startswith("docs/release-evidence/") for path in PUBLIC_FILES))


if __name__ == "__main__":
    unittest.main()
