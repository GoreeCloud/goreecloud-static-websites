#!/usr/bin/env python3
"""Offline regression tests for the fixed-target GoreeCloud deployment verifier.

These tests deliberately replace network access with synthetic responses. They protect the
security, indexing, candidate-integrity, error-page, repository-isolation, and RFC 9116 decisions
that the live verifier enforces after a Cloudflare Pages deployment without making CI depend on
the network.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import verify_remote_deployment as verifier  # noqa: E402


class RemoteVerifierTests(unittest.TestCase):
    """Exercise verifier behavior without performing external requests."""

    @staticmethod
    def response(
        *,
        status: int = 200,
        final_url: str = "https://www.goreecloud.com/",
        headers: dict[str, str] | None = None,
        body: bytes = b"",
    ) -> verifier.Response:
        return verifier.Response(
            status=status,
            final_url=final_url,
            headers=headers or {},
            body=body,
        )

    @staticmethod
    def security_txt(expires: datetime) -> bytes:
        timestamp = expires.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        return (
            f"Contact: {verifier.EXPECTED_SECURITY_CONTACT}\n"
            f"Expires: {timestamp}\n"
            "Preferred-Languages: en\n"
            f"Canonical: {verifier.EXPECTED_SECURITY_CANONICAL}\n"
            f"Policy: {verifier.EXPECTED_SECURITY_POLICY}\n"
        ).encode("utf-8")

    def test_fixed_url_accepts_only_reviewed_https_hosts(self) -> None:
        for url in verifier.TARGETS.values():
            verifier.validate_fixed_url(url)

        invalid = (
            "http://www.goreecloud.com/",
            "https://example.com/",
            "https://user:password@www.goreecloud.com/",
            "https://www.goreecloud.com/?debug=1",
            "https://www.goreecloud.com/#fragment",
        )
        for url in invalid:
            with self.subTest(url=url), self.assertRaises(ValueError):
                verifier.validate_fixed_url(url)

    def test_build_url_requires_origin_rooted_paths(self) -> None:
        self.assertEqual(
            verifier.build_url(verifier.TARGETS["production"], "/privacy.html"),
            "https://www.goreecloud.com/privacy.html",
        )
        with self.assertRaises(ValueError):
            verifier.build_url(verifier.TARGETS["production"], "privacy.html")

    def test_content_type_matching_handles_expected_web_variants(self) -> None:
        cases = (
            ("text/html; charset=utf-8", "text/html", True),
            ("application/manifest+json", "json", True),
            ("application/ld+json", "json", True),
            ("application/xml", "xml", True),
            ("application/rss+xml", "xml", True),
            ("text/javascript; charset=utf-8", "javascript", True),
            ("application/octet-stream", "image/png", False),
        )
        for actual, expected, result in cases:
            with self.subTest(actual=actual, expected=expected):
                self.assertEqual(verifier.content_type_matches(actual, expected), result)

    def test_security_txt_parser_is_case_insensitive_and_preserves_repeats(self) -> None:
        fields = verifier.parse_security_txt(
            "# comment\nContact: mailto:first@example.com\nCONTACT: mailto:second@example.com\nPolicy: https://example.com/policy\n"
        )
        self.assertEqual(
            fields["contact"],
            ["mailto:first@example.com", "mailto:second@example.com"],
        )
        self.assertEqual(fields["policy"], ["https://example.com/policy"])

    def test_rfc3339_parser_requires_timezone_and_normalizes_utc(self) -> None:
        parsed = verifier.parse_rfc3339("2027-01-02T03:04:05Z")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.utcoffset(), timedelta(0))
        self.assertIsNone(verifier.parse_rfc3339("2027-01-02T03:04:05"))
        self.assertIsNone(verifier.parse_rfc3339("not-a-date"))

    def test_fresh_security_txt_passes(self) -> None:
        response = self.response(
            final_url="https://www.goreecloud.com/.well-known/security.txt",
            headers={"cache-control": "public, max-age=3600"},
            body=self.security_txt(datetime.now(timezone.utc) + timedelta(days=45)),
        )
        errors: list[str] = []
        with patch.object(verifier, "fetch", return_value=response):
            verifier.verify_security_txt(verifier.TARGETS["production"], errors)
        self.assertEqual(errors, [])

    def test_security_txt_inside_renewal_window_fails(self) -> None:
        response = self.response(
            final_url="https://www.goreecloud.com/.well-known/security.txt",
            headers={"cache-control": "max-age=3600"},
            body=self.security_txt(datetime.now(timezone.utc) + timedelta(days=20)),
        )
        errors: list[str] = []
        with patch.object(verifier, "fetch", return_value=response):
            verifier.verify_security_txt(verifier.TARGETS["production"], errors)
        self.assertTrue(any("expires within 30 days" in error for error in errors))

    def test_security_txt_rejects_missing_contract_fields_and_cache_policy(self) -> None:
        body = b"Expires: 2027-01-02T03:04:05Z\n"
        response = self.response(
            final_url="https://www.goreecloud.com/.well-known/security.txt",
            headers={},
            body=body,
        )
        errors: list[str] = []
        with patch.object(verifier, "fetch", return_value=response):
            verifier.verify_security_txt(verifier.TARGETS["production"], errors)
        joined = "\n".join(errors)
        self.assertIn("one-hour Cache-Control", joined)
        self.assertIn("expected primary security contact", joined)
        self.assertIn("expected canonical URL", joined)
        self.assertIn("expected security policy URL", joined)

    def test_branch_preview_requires_noindex_header(self) -> None:
        errors: list[str] = []
        response = self.response(headers={"x-robots-tag": "noindex, nofollow"})
        with patch.object(verifier, "fetch", return_value=response):
            verifier.verify_indexing_header(
                "branch-preview", verifier.TARGETS["branch-preview"], errors
            )
        self.assertEqual(errors, [])

        errors = []
        with patch.object(verifier, "fetch", return_value=self.response(headers={})):
            verifier.verify_indexing_header(
                "branch-preview", verifier.TARGETS["branch-preview"], errors
            )
        self.assertTrue(any("missing the expected X-Robots-Tag" in error for error in errors))

    def test_production_rejects_noindex_header(self) -> None:
        errors: list[str] = []
        response = self.response(headers={"x-robots-tag": "noindex"})
        with patch.object(verifier, "fetch", return_value=response):
            verifier.verify_indexing_header("production", verifier.TARGETS["production"], errors)
        self.assertTrue(any("unexpectedly publishes X-Robots-Tag" in error for error in errors))

    def test_public_surface_rejects_redirect_outside_allowlist(self) -> None:
        errors: list[str] = []
        check = {"/": (200, "expected-marker", "text/html")}
        response = self.response(
            final_url="https://example.com/",
            headers={"content-type": "text/html; charset=utf-8"},
            body=b"expected-marker",
        )
        with (
            patch.object(verifier, "PUBLIC_CHECKS", check),
            patch.object(verifier, "fetch", return_value=response),
        ):
            verifier.verify_public_surface(verifier.TARGETS["production"], errors)
        self.assertTrue(any("redirected outside" in error for error in errors))

    def test_nested_404_requires_goreecloud_error_markers(self) -> None:
        valid = self.response(
            status=404,
            body="Page Not Found — GoreeCloud\nThis page isn’t here.\nnoindex,follow".encode("utf-8"),
        )
        errors: list[str] = []
        with patch.object(verifier, "fetch", return_value=valid):
            verifier.verify_not_found_behavior(verifier.TARGETS["production"], errors)
        self.assertEqual(errors, [])

        errors = []
        with patch.object(verifier, "fetch", return_value=self.response(status=404, body=b"generic 404")):
            verifier.verify_not_found_behavior(verifier.TARGETS["production"], errors)
        self.assertEqual(len(errors), 3)

    def test_repository_only_path_must_remain_404(self) -> None:
        errors: list[str] = []
        with (
            patch.object(verifier, "REPOSITORY_ONLY_PATHS", ("/README.md",)),
            patch.object(verifier, "fetch", return_value=self.response(status=200)),
        ):
            verifier.verify_repository_isolation(verifier.TARGETS["production"], errors)
        self.assertTrue(any("Repository-only path /README.md returned HTTP 200" in error for error in errors))

    def test_production_apex_must_finish_on_www(self) -> None:
        errors: list[str] = []
        with patch.object(
            verifier,
            "fetch",
            return_value=self.response(final_url="https://www.goreecloud.com/"),
        ):
            verifier.verify_production_redirect(errors)
        self.assertEqual(errors, [])

        errors = []
        with patch.object(
            verifier,
            "fetch",
            return_value=self.response(final_url="https://goreecloud.com/"),
        ):
            verifier.verify_production_redirect(errors)
        self.assertTrue(any("did not resolve to the canonical www host" in error for error in errors))

    def test_integrity_set_matches_public_allowlist_except_cloudflare_headers(self) -> None:
        expected = tuple(
            relative
            for relative in verifier.PUBLIC_FILES
            if relative not in verifier.NON_FETCHABLE_PUBLIC_FILES
        )
        self.assertEqual(verifier.NON_FETCHABLE_PUBLIC_FILES, frozenset({"_headers"}))
        self.assertEqual(verifier.REMOTE_INTEGRITY_FILES, expected)
        self.assertNotIn("_headers", verifier.REMOTE_INTEGRITY_FILES)

    def test_remote_integrity_path_mapping_is_origin_rooted_and_safe(self) -> None:
        self.assertEqual(verifier.remote_path_for_public_file("index.html"), "/")
        self.assertEqual(verifier.remote_path_for_public_file("robots.txt"), "/robots.txt")
        self.assertEqual(
            verifier.remote_path_for_public_file("assets/goreecloud-icon.png"),
            "/assets/goreecloud-icon.png",
        )
        for invalid in ("/absolute.html", "../escape.txt", "assets/../escape.txt", ""):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                verifier.remote_path_for_public_file(invalid)

    def test_candidate_content_integrity_accepts_exact_bytes(self) -> None:
        relative = "robots.txt"
        expected = (verifier.ROOT / relative).read_bytes()
        response = self.response(
            final_url="https://www.goreecloud.com/robots.txt",
            body=expected,
        )
        errors: list[str] = []
        with (
            patch.object(verifier, "REMOTE_INTEGRITY_FILES", (relative,)),
            patch.object(verifier, "fetch", return_value=response),
        ):
            verifier.verify_candidate_content_integrity(verifier.TARGETS["production"], errors)
        self.assertEqual(errors, [])

    def test_candidate_content_integrity_rejects_byte_mismatch(self) -> None:
        relative = "robots.txt"
        response = self.response(
            final_url="https://www.goreecloud.com/robots.txt",
            body=b"not-the-reviewed-candidate",
        )
        errors: list[str] = []
        with (
            patch.object(verifier, "REMOTE_INTEGRITY_FILES", (relative,)),
            patch.object(verifier, "fetch", return_value=response),
        ):
            verifier.verify_candidate_content_integrity(verifier.TARGETS["production"], errors)
        self.assertTrue(any("Candidate content mismatch for /robots.txt" in error for error in errors))
        self.assertTrue(any("expected SHA-256" in error for error in errors))
        self.assertTrue(any("deployed SHA-256" in error for error in errors))

    def test_candidate_content_integrity_rejects_non_200_resource(self) -> None:
        relative = "robots.txt"
        response = self.response(
            status=404,
            final_url="https://www.goreecloud.com/robots.txt",
            body=b"missing",
        )
        errors: list[str] = []
        with (
            patch.object(verifier, "REMOTE_INTEGRITY_FILES", (relative,)),
            patch.object(verifier, "fetch", return_value=response),
        ):
            verifier.verify_candidate_content_integrity(verifier.TARGETS["production"], errors)
        self.assertTrue(any("returned HTTP 404; expected 200" in error for error in errors))

    def test_static_configuration_contract_passes_without_network(self) -> None:
        self.assertEqual(verifier.check_configuration(), 0)


if __name__ == "__main__":
    unittest.main()
