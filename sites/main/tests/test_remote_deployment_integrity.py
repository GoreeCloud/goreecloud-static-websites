#!/usr/bin/env python3
"""Regression tests for GoreeCloud remote deployment trust and candidate identity."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import URLError
from urllib.request import Request

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_public_site as public_build  # noqa: E402
import verify_remote_deployment as verifier  # noqa: E402


class RemoteDeploymentIntegrityTests(unittest.TestCase):
    """Keep remote verification bound to the reviewed public artifact and host allowlist."""

    @staticmethod
    def response(*, body: bytes, path: str = "/privacy.html", status: int = 200):
        return verifier.Response(
            status=status,
            final_url=f"https://www.goreecloud.com{path}",
            headers={},
            body=body,
        )

    def test_remote_integrity_set_tracks_public_allowlist_except_headers_control(self) -> None:
        self.assertEqual(verifier.NON_FETCHABLE_PUBLIC_FILES, frozenset({"_headers"}))
        self.assertEqual(
            set(verifier.REMOTE_INTEGRITY_FILES),
            set(public_build.PUBLIC_FILES) - {"_headers"},
        )
        self.assertNotIn("_headers", verifier.REMOTE_INTEGRITY_FILES)

    def test_public_source_path_maps_to_expected_remote_path(self) -> None:
        self.assertEqual(verifier.remote_path_for_public_file("index.html"), "/")
        self.assertEqual(
            verifier.remote_path_for_public_file(".well-known/security.txt"),
            "/.well-known/security.txt",
        )
        self.assertEqual(
            verifier.remote_path_for_public_file("css/glaze.css"),
            "/css/glaze.css",
        )
        with self.assertRaises(ValueError):
            verifier.remote_path_for_public_file("../private.txt")
        with self.assertRaises(ValueError):
            verifier.remote_path_for_public_file("/absolute.txt")

    def test_candidate_bytes_include_final_glaze_ui_21_transform(self) -> None:
        candidate = verifier.candidate_bytes("index.html").decode("utf-8")
        self.assertIn('name="goreecloud-glaze-ui" content="2.1.0"', candidate)
        self.assertIn('data-glaze-ui="2.1.0"', candidate)
        self.assertIn(
            "Ten independently deployed public destinations are production-accepted on Glaze UI 2.1.0 Stable",
            candidate,
        )
        self.assertIn("Identity Center is the eleventh official first-party surface", candidate)
        self.assertIn("The GoreeCloud Design Center for Glaze UI 2.1.0 Stable", candidate)
        self.assertNotIn('data-glaze-ui="1.5.0"', candidate)
        self.assertNotIn('data-glaze-ui="2.0.0"', candidate)
        self.assertNotIn("Glaze UI 2.1 remains Candidate", candidate)
        self.assertNotIn(
            "The public portfolio uses Glaze UI 2.0.0 Stable as its production design target.",
            candidate,
        )

    def test_exact_candidate_bytes_pass_remote_integrity(self) -> None:
        relative = "privacy.html"
        # Compare against the exact reviewed build candidate, not the raw source
        # template. Glaze UI 2.1 normalization is intentionally applied at the
        # public render boundary before Cloudflare receives this page.
        expected = verifier.candidate_bytes(relative)
        errors: list[str] = []

        with (
            patch.object(verifier, "REMOTE_INTEGRITY_FILES", (relative,)),
            patch.object(
                verifier,
                "fetch",
                return_value=self.response(body=expected),
            ),
        ):
            verifier.verify_candidate_content_integrity(
                verifier.TARGETS["production"],
                errors,
            )

        self.assertEqual(errors, [])

    def test_candidate_byte_mismatch_fails_without_echoing_content(self) -> None:
        relative = "privacy.html"
        errors: list[str] = []
        deployed_body = b"unexpected deployed content"

        with (
            patch.object(verifier, "REMOTE_INTEGRITY_FILES", (relative,)),
            patch.object(
                verifier,
                "fetch",
                return_value=self.response(body=deployed_body),
            ),
        ):
            verifier.verify_candidate_content_integrity(
                verifier.TARGETS["production"],
                errors,
            )

        self.assertEqual(len(errors), 1)
        self.assertIn("Candidate content mismatch for /privacy.html", errors[0])
        self.assertIn("SHA-256", errors[0])
        self.assertNotIn(deployed_body.decode("utf-8"), errors[0])

    def test_redirect_handler_rejects_unreviewed_host_before_following(self) -> None:
        request = Request("https://www.goreecloud.com/")
        handler = verifier.AllowlistedRedirectHandler()

        with self.assertRaises(URLError) as context:
            handler.redirect_request(
                request,
                None,
                302,
                "Found",
                {},
                "https://example.com/untrusted",
            )

        self.assertIn("Redirect target rejected", str(context.exception.reason))
        self.assertIn("outside the GoreeCloud verifier allowlist", str(context.exception.reason))

    def test_redirect_handler_allows_reviewed_goreecloud_destination(self) -> None:
        request = Request("https://goreecloud.com/")
        handler = verifier.AllowlistedRedirectHandler()

        redirected = handler.redirect_request(
            request,
            None,
            301,
            "Moved Permanently",
            {},
            "https://www.goreecloud.com/",
        )

        self.assertIsNotNone(redirected)
        self.assertEqual(redirected.full_url, "https://www.goreecloud.com/")


if __name__ == "__main__":
    unittest.main()
