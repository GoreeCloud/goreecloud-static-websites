#!/usr/bin/env python3
"""Regression tests for the fail-closed release-evidence record generator."""

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

import create_release_evidence as generator  # noqa: E402
from build_public_site import PUBLIC_FILES  # noqa: E402

CENTRAL = ZoneInfo("America/Chicago")
TEST_SHA = "0123456789abcdef0123456789abcdef01234567"


class CreateReleaseEvidenceTests(unittest.TestCase):
    """Keep evidence creation deterministic, non-overwriting, and non-authorizing."""

    def test_generator_is_repository_only(self) -> None:
        self.assertNotIn("scripts/create_release_evidence.py", PUBLIC_FILES)
        self.assertNotIn("docs/release-evidence-template.md", PUBLIC_FILES)

    def test_commit_sha_requires_canonical_full_lowercase_form(self) -> None:
        self.assertEqual(generator.validate_commit_sha(TEST_SHA), TEST_SHA)
        for invalid in (
            "0123456",
            TEST_SHA.upper(),
            "g" * 40,
            TEST_SHA + "0",
            f" {TEST_SHA}",
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    generator.validate_commit_sha(invalid)

    def test_record_date_requires_real_iso_calendar_date(self) -> None:
        self.assertEqual(generator.validate_record_date("2026-08-15"), "2026-08-15")
        for invalid in ("08-15-2026", "2026-8-15", "2026-02-30", "2026/08/15"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    generator.validate_record_date(invalid)

    def test_central_timestamp_uses_12_hour_format(self) -> None:
        moment = datetime(2026, 8, 15, 1, 53, tzinfo=CENTRAL)
        self.assertEqual(
            generator.format_central_timestamp(moment),
            "August 15, 2026 at 1:53 AM CDT",
        )

    def test_rendered_record_is_candidate_bound_but_unchecked(self) -> None:
        template = generator.TEMPLATE.read_text(encoding="utf-8")
        moment = datetime(2026, 8, 15, 1, 53, tzinfo=CENTRAL)
        rendered = generator.render_record(template, TEST_SHA, moment)

        self.assertTrue(rendered.startswith("# GoreeCloud Website Release Evidence — 2026-08-15 — 0123456789ab"))
        self.assertIn(f"- Bound candidate commit: `{TEST_SHA}`", rendered)
        self.assertIn(f"- Exact candidate commit (40-character SHA): {TEST_SHA}", rendered)
        self.assertIn("Record state: **Working — not accepted**", rendered)
        self.assertIn("no validation, acceptance, or authorization is inferred", rendered.lower())
        self.assertNotIn("[x]", rendered.lower())

    def test_create_record_uses_safe_filename_and_preserves_template(self) -> None:
        moment = datetime(2026, 8, 15, 1, 53, tzinfo=CENTRAL)
        template_before = generator.TEMPLATE.read_bytes()

        with tempfile.TemporaryDirectory() as directory:
            destination = generator.create_record(
                TEST_SHA,
                record_date="2026-08-15",
                created_at=moment,
                output_dir=Path(directory),
                verify_commit=False,
            )
            self.assertEqual(destination.name, "2026-08-15-0123456789ab-release-evidence.md")
            self.assertTrue(destination.is_file())
            self.assertNotIn("[x]", destination.read_text(encoding="utf-8").lower())

        self.assertEqual(generator.TEMPLATE.read_bytes(), template_before)

    def test_create_record_refuses_overwrite(self) -> None:
        moment = datetime(2026, 8, 15, 1, 53, tzinfo=CENTRAL)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            first = generator.create_record(
                TEST_SHA,
                record_date="2026-08-15",
                created_at=moment,
                output_dir=output,
                verify_commit=False,
            )
            first_contents = first.read_bytes()

            with self.assertRaises(FileExistsError):
                generator.create_record(
                    TEST_SHA,
                    record_date="2026-08-15",
                    created_at=moment,
                    output_dir=output,
                    verify_commit=False,
                )

            self.assertEqual(first.read_bytes(), first_contents)

    def test_create_record_rejects_symlink_output_directory(self) -> None:
        moment = datetime(2026, 8, 15, 1, 53, tzinfo=CENTRAL)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            actual = root / "actual"
            actual.mkdir()
            linked = root / "linked"
            linked.symlink_to(actual, target_is_directory=True)

            with self.assertRaises(ValueError):
                generator.create_record(
                    TEST_SHA,
                    record_date="2026-08-15",
                    created_at=moment,
                    output_dir=linked,
                    verify_commit=False,
                )


if __name__ == "__main__":
    unittest.main()
